#!/usr/bin/env python3
"""Measure a song file so mixing/mastering decisions rest on facts, not guesses.

Reports: format (codec, sample rate, bit depth, channels, duration), integrated
loudness (LUFS), loudness range, max short-term loudness, true peak, sample peak,
clipping, peak-to-loudness ratio, DC offset, left/right balance, stereo
correlation and mono-fold loss, leading/trailing silence, abrupt endings,
high-frequency bandwidth (a hint of lossy encoding), and tonal balance by band.

Usage:
  python analyze_audio.py SONG [SONG ...]
  python analyze_audio.py SONG --reference REF_SONG   # loudness/RMS/peak/stereo/spectral deltas vs a reference
                                                      # (a reference song, or the original to verify a master)
  python analyze_audio.py SONG --json report.json      # also save machine-readable results

Needs ffmpeg and ffprobe on PATH, and numpy. Nothing else.
Numbers describe the file; they are not a listening test. Treat the "notes"
as prompts for attention, not verdicts.
"""
import argparse
import json
import math
import re
import subprocess
import sys

import numpy as np

CHUNK = 16384          # frames per analysis block (~0.37 s at 44.1 kHz)
FFT_N = 8192
SILENCE_DB = -60.0
BANDS = [("sub", 20, 60), ("bass", 60, 250), ("low-mid", 250, 500),
         ("mid", 500, 2000), ("upper-mid", 2000, 6000),
         ("high", 6000, 12000), ("air", 12000, 20000)]
LOSSY = {"mp3", "aac", "vorbis", "opus", "wmav2", "wmav1", "ac3", "eac3", "mp2"}


def db(x, floor=-200.0):
    return 20 * math.log10(x) if x > 0 else floor


def pdb(x, floor=-200.0):
    return 10 * math.log10(x) if x > 0 else floor


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
         "-show_streams", "-select_streams", "a:0", path],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"ffprobe could not read {path}: {out.stderr.strip()}")
    info = json.loads(out.stdout)
    if not info.get("streams"):
        raise SystemExit(f"No audio stream found in {path}")
    s, f = info["streams"][0], info.get("format", {})
    bits = s.get("bits_per_raw_sample") or s.get("bits_per_sample") or None
    try:
        bits = int(bits) or None
    except (TypeError, ValueError):
        bits = None
    dur = s.get("duration") or f.get("duration")
    return {
        "codec": s.get("codec_name"),
        "sample_rate": int(s.get("sample_rate", 0)),
        "channels": int(s.get("channels", 0)),
        "channel_layout": s.get("channel_layout"),
        "sample_fmt": s.get("sample_fmt"),
        "bit_depth": bits,
        "bit_rate_kbps": round(int(f["bit_rate"]) / 1000) if f.get("bit_rate") else None,
        "duration_s": round(float(dur), 3) if dur else None,
        "lossy": s.get("codec_name") in LOSSY,
    }


FRAME_RE = re.compile(r"t:\s*([\d.]+).*?M:\s*(-?[\d.]+|-inf)\s+S:\s*(-?[\d.]+|-inf)")


def loudness(path, channels):
    af = "ebur128=peak=true+sample:framelog=info"
    if channels == 1:
        af += ":dualmono=true"
    run = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "a:0",
                          "-af", af, "-f", "null", "-"], capture_output=True, text=True)
    err = run.stderr
    if "Summary:" not in err:
        raise SystemExit(f"Loudness measurement failed for {path}:\n{err[-800:]}")
    summ = err[err.rindex("Summary:"):]

    def grab(label):
        m = re.search(label + r"\s*(-?[\d.]+|-inf)", summ)
        if not m:
            return None
        return None if m.group(1) == "-inf" else float(m.group(1))

    tp = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)", summ)
    sp = re.search(r"Sample peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)", summ)
    s_max, m_max = None, None
    for line in err.splitlines():
        m = FRAME_RE.search(line)
        if not m or m.group(3) == "-inf":
            continue
        t, mom, st = float(m.group(1)), m.group(2), float(m.group(3))
        if t >= 3.0 and st > -100:
            s_max = st if s_max is None else max(s_max, st)
        if mom != "-inf" and float(mom) > -100:
            m_max = float(mom) if m_max is None else max(m_max, float(mom))
    return {
        "integrated_lufs": grab(r"I:"),
        "loudness_range_lu": grab(r"LRA:"),
        "max_short_term_lufs": s_max,
        "max_momentary_lufs": m_max,
        "true_peak_dbtp": None if not tp or tp.group(1) == "-inf" else float(tp.group(1)),
        "sample_peak_dbfs": None if not sp or sp.group(1) == "-inf" else float(sp.group(1)),
    }


def _runs(mask, carry):
    """Count runs of True with length >= 3; return (count, carry_into_next_chunk)."""
    count = 0
    if not mask.any():
        if carry >= 3:
            count += 1
        return count, 0
    edges = np.diff(np.concatenate(([0], mask.astype(np.int8), [0])))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    lengths = ends - starts
    if carry:
        if starts[0] == 0:
            lengths[0] += carry
        elif carry >= 3:
            count += 1
    new_carry = 0
    if ends[-1] == len(mask):
        new_carry = int(lengths[-1])
        lengths = lengths[:-1]
    count += int((lengths >= 3).sum())
    return count, new_carry


def sample_stats(path, info):
    sr = info["sample_rate"]
    ch_in = info["channels"]
    ch = 1 if ch_in == 1 else 2  # analyze surround as a stereo fold-down
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-map", "a:0", "-f", "f32le", "-ac", str(ch), "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    n = 0
    peak = np.zeros(ch)
    over = np.zeros(ch, dtype=np.int64)
    at_fs = np.zeros(ch, dtype=np.int64)
    clip_runs = np.zeros(ch, dtype=np.int64)
    carry = [0] * ch
    sumsq = np.zeros(ch)
    sums = np.zeros(ch)
    s_lr = s_mid = s_side = 0.0
    win_corr = []
    first_loud = last_loud = None
    thr = 10 ** (SILENCE_DB / 20)
    spec = np.zeros(FFT_N // 2 + 1)
    spec_frames = 0
    window = np.hanning(FFT_N)
    tail = np.zeros((0, ch), dtype=np.float32)
    need = int(0.1 * sr)
    pending = b""
    bpf = 4 * ch

    while True:
        buf = proc.stdout.read(CHUNK * bpf)
        if not buf:
            break
        buf = pending + buf
        usable = len(buf) - (len(buf) % bpf)
        pending = buf[usable:]
        x = np.frombuffer(buf[:usable], dtype="<f4").reshape(-1, ch).astype(np.float64)
        if not len(x):
            continue
        a = np.abs(x)
        peak = np.maximum(peak, a.max(axis=0))
        over += (a > 1.0).sum(axis=0)
        fs_mask = a >= 0.999
        at_fs += fs_mask.sum(axis=0)
        for c in range(ch):
            k, carry[c] = _runs(fs_mask[:, c], carry[c])
            clip_runs[c] += k
        sumsq += (x ** 2).sum(axis=0)
        sums += x.sum(axis=0)
        loud = np.flatnonzero(a.max(axis=1) > thr)
        if len(loud):
            if first_loud is None:
                first_loud = n + int(loud[0])
            last_loud = n + int(loud[-1])
        if ch == 2:
            L, R = x[:, 0], x[:, 1]
            s_lr += float((L * R).sum())
            mid = (L + R) / 2
            s_mid += float((mid ** 2).sum())
            s_side += float((((L - R) / 2) ** 2).sum())
            rl, rr = math.sqrt((L ** 2).mean()), math.sqrt((R ** 2).mean())
            if db(rl) > -50 and db(rr) > -50:
                Lc, Rc = L - L.mean(), R - R.mean()
                den = math.sqrt((Lc ** 2).sum() * (Rc ** 2).sum())
                if den > 0:
                    win_corr.append(float((Lc * Rc).sum() / den))
        else:
            mid = x[:, 0]
        for off in range(0, len(mid) - FFT_N + 1, FFT_N):
            seg = mid[off:off + FFT_N]
            if np.abs(seg).max() > thr:
                spec += np.abs(np.fft.rfft(seg * window)) ** 2
                spec_frames += 1
        tail = np.concatenate((tail, x.astype(np.float32)))[-need:]
        n += len(x)

    for c in range(ch):
        if carry[c] >= 3:
            clip_runs[c] += 1
    err = proc.stderr.read().decode(errors="replace").strip()
    proc.wait()
    if n == 0:
        raise SystemExit(f"Could not decode audio from {path}: {err}")

    rms = np.sqrt(sumsq / n)
    res = {
        "decoded_frames": n,
        "decode_errors": err[:300] if err else None,
        "sample_peak_dbfs_per_channel": [round(db(p), 2) for p in peak],
        "samples_above_full_scale": int(over.sum()),
        "samples_at_or_near_full_scale": int(at_fs.sum()),
        "clip_runs_3plus_samples": int(clip_runs.sum()),
        "rms_dbfs_per_channel": [round(db(r), 2) for r in rms],
        "crest_factor_db": round(db(peak.max()) - db(rms.max()), 2),
        "dc_offset_per_channel": [round(float(s / n), 5) for s in sums],
        "leading_silence_s": round((first_loud or 0) / sr, 3) if first_loud is not None else None,
        "trailing_silence_s": round((n - 1 - last_loud) / sr, 3) if last_loud is not None else None,
        "last_100ms_rms_dbfs": round(db(math.sqrt(float((tail.astype(np.float64) ** 2).mean()))), 1) if len(tail) else None,
    }
    if ch == 2:
        den = math.sqrt(sumsq[0] * sumsq[1])
        res["stereo_correlation"] = round(s_lr / den, 3) if den > 0 else None
        wc = np.array(win_corr) if win_corr else np.array([1.0])
        res["min_window_correlation"] = round(float(wc.min()), 3)
        res["pct_windows_negative_correlation"] = round(100 * float((wc < 0).mean()), 1)
        res["lr_balance_db"] = round(db(rms[0]) - db(rms[1]), 2)
        res["mono_fold_change_db"] = round(pdb(s_mid / n) - pdb(float(sumsq.mean()) / n), 2)
        res["side_to_mid_db"] = round(pdb(s_side) - pdb(s_mid), 2)

    if spec_frames:
        freqs = np.fft.rfftfreq(FFT_N, 1 / sr)
        total = spec[(freqs >= 20) & (freqs <= min(20000, sr / 2))].sum()
        bands = {}
        for name, lo, hi in BANDS:
            if lo >= sr / 2:
                continue
            sel = (freqs >= lo) & (freqs < min(hi, sr / 2))
            bands[name] = round(pdb(spec[sel].sum() / total), 1) if total > 0 else None
        res["band_share_db"] = bands
        sdb = 10 * np.log10(np.convolve(spec, np.ones(25) / 25, mode="same") + 1e-30)
        ref = sdb[(freqs >= 1000) & (freqs <= 4000)].mean()
        floor = np.percentile(sdb[freqs >= 1000], 5)  # noise floor estimate
        above = np.flatnonzero((sdb > max(ref - 70, floor + 15)) & (freqs < sr / 2 - 200))
        res["content_up_to_khz"] = round(float(freqs[above[-1]]) / 1000, 1) if len(above) else None
    return res


def notes_for(r):
    f, l, s = r["format"], r["loudness"], r["samples"]
    out = []
    if f["lossy"]:
        out.append(f"Lossy source ({f['codec']}{', ~%d kbps' % f['bit_rate_kbps'] if f['bit_rate_kbps'] else ''}): "
                   "work in WAV to avoid further loss, but conversion cannot restore what encoding removed.")
    if f["sample_rate"] and f["sample_rate"] < 44100:
        out.append(f"Low sample rate ({f['sample_rate']} Hz): high frequencies are limited by the source.")
    if s.get("content_up_to_khz") and s["content_up_to_khz"] < 17 and f["sample_rate"] >= 44100:
        out.append(f"Very little content above ~{s['content_up_to_khz']} kHz: typical of lossy encoding or AI generation. "
                   "A gentle high shelf can add sparkle, but it cannot recreate missing detail.")
    if s["samples_above_full_scale"] or s["clip_runs_3plus_samples"]:
        out.append(f"Clipping signs: {s['clip_runs_3plus_samples']} runs of 3+ samples at full scale, "
                   f"{s['samples_above_full_scale']} decoded samples above 0 dBFS. Listen for crackle in loud parts.")
    tp, I = l["true_peak_dbtp"], l["integrated_lufs"]
    if tp is not None and tp > -1.0:
        out.append(f"True peak {tp:+.1f} dBTP is above -1 dBTP: MP3/AAC encoding of this file may distort.")
    if tp is not None and I is not None:
        plr = tp - I
        if plr < 8:
            out.append(f"Peak-to-loudness ratio {plr:.1f} dB: already heavily limited. Avoid stacking another aggressive limiter.")
        elif plr > 16 and I < -18:
            out.append(f"Peak-to-loudness ratio {plr:.1f} dB with {I:.1f} LUFS: quite dynamic and quiet; there is room for gentle mastering.")
    if l["loudness_range_lu"] is not None and l["loudness_range_lu"] < 3:
        out.append(f"Loudness range {l['loudness_range_lu']:.1f} LU: very little contrast between sections.")
    if "stereo_correlation" in s:
        if s["stereo_correlation"] is not None and s["stereo_correlation"] < 0.2:
            out.append(f"Low stereo correlation ({s['stereo_correlation']}): check for phase problems and mono playback.")
        if s["pct_windows_negative_correlation"] > 5:
            out.append(f"{s['pct_windows_negative_correlation']}% of moments have negative correlation: parts may vanish in mono.")
        if s["mono_fold_change_db"] < -3.5:
            out.append(f"Summing to mono loses {-s['mono_fold_change_db']:.1f} dB: wide or out-of-phase content. Check phone speakers.")
        if abs(s["lr_balance_db"]) > 1.5:
            side = "left" if s["lr_balance_db"] > 0 else "right"
            out.append(f"Leans {side} by {abs(s['lr_balance_db']):.1f} dB (overall level). Check whether that is intentional.")
    if any(abs(d) > 0.002 for d in s["dc_offset_per_channel"]):
        out.append("DC offset present: a high-pass around 20-30 Hz removes it and frees headroom.")
    if s["leading_silence_s"] is not None and s["leading_silence_s"] > 1.0:
        out.append(f"{s['leading_silence_s']:.1f} s of silence at the start.")
    if s["trailing_silence_s"] is not None and s["trailing_silence_s"] > 3.0:
        out.append(f"{s['trailing_silence_s']:.1f} s of silence at the end.")
    if (s["last_100ms_rms_dbfs"] is not None and s["last_100ms_rms_dbfs"] > -40
            and (s["trailing_silence_s"] or 0) < 0.05):
        out.append(f"The file ends while still loud ({s['last_100ms_rms_dbfs']} dBFS in the last 0.1 s): "
                   "the ending or a reverb tail may be cut off. A short fade may help.")
    if s.get("decode_errors"):
        out.append(f"Decoder reported problems: {s['decode_errors'][:120]}")
    return out


def analyze(path):
    fmt = probe(path)
    r = {"file": path, "format": fmt, "loudness": loudness(path, fmt["channels"]),
         "samples": sample_stats(path, fmt)}
    l = r["loudness"]
    if l["true_peak_dbtp"] is not None and l["integrated_lufs"] is not None:
        l["peak_to_loudness_ratio_db"] = round(l["true_peak_dbtp"] - l["integrated_lufs"], 1)
    r["notes"] = notes_for(r)
    return r


def fmt_num(v, unit="", sign=False):
    if v is None:
        return "n/a"
    return (f"{v:+.1f}" if sign else f"{v:.1f}") + unit


def print_report(r):
    f, l, s = r["format"], r["loudness"], r["samples"]
    print(f"\n=== {r['file']}")
    bits = f"{f['bit_depth']}-bit" if f["bit_depth"] else f["sample_fmt"]
    br = f", {f['bit_rate_kbps']} kbps" if f["bit_rate_kbps"] else ""
    print(f"Format      {f['codec']}, {f['sample_rate']} Hz, {bits}, {f['channels']} ch "
          f"({f['channel_layout'] or 'unknown layout'}), {f['duration_s']} s{br}")
    print(f"Loudness    {fmt_num(l['integrated_lufs'], ' LUFS integrated')} | "
          f"loudest 3 s: {fmt_num(l['max_short_term_lufs'], ' LUFS')} | "
          f"range: {fmt_num(l['loudness_range_lu'], ' LU')}")
    print(f"Peaks       true peak {fmt_num(l['true_peak_dbtp'], ' dBTP', True)} | "
          f"sample peak {fmt_num(l['sample_peak_dbfs'], ' dBFS', True)} | "
          f"peak-to-loudness {fmt_num(l.get('peak_to_loudness_ratio_db'), ' dB')} | "
          f"crest {fmt_num(s['crest_factor_db'], ' dB')}")
    print(f"Clipping    {s['clip_runs_3plus_samples']} runs of 3+ full-scale samples, "
          f"{s['samples_above_full_scale']} samples above 0 dBFS")
    if "stereo_correlation" in s:
        print(f"Stereo      correlation {s['stereo_correlation']} (min moment {s['min_window_correlation']}, "
              f"{s['pct_windows_negative_correlation']}% negative) | mono fold {fmt_num(s['mono_fold_change_db'], ' dB', True)} | "
              f"L-R balance {fmt_num(s['lr_balance_db'], ' dB', True)} | side vs mid {fmt_num(s['side_to_mid_db'], ' dB', True)}")
    print(f"Edges       start silence {s['leading_silence_s']} s | end silence {s['trailing_silence_s']} s | "
          f"last 0.1 s at {s['last_100ms_rms_dbfs']} dBFS | DC {s['dc_offset_per_channel']}")
    if s.get("band_share_db"):
        bands = "  ".join(f"{k} {v:.1f}" for k, v in s["band_share_db"].items() if v is not None)
        print(f"Tone (dB share of total energy)  {bands}")
        print(f"Bandwidth   content reaches ~{s['content_up_to_khz']} kHz")
    if r["notes"]:
        print("Notes")
        for n in r["notes"]:
            print(f"  - {n}")
    else:
        print("Notes       nothing unusual detected by measurement")


def print_delta(song, ref):
    print(f"\n=== Compared with reference: {ref['file']}")
    ls, lr = song["loudness"], ref["loudness"]
    for key, label in [("integrated_lufs", "Integrated LUFS"), ("loudness_range_lu", "Loudness range LU"),
                       ("true_peak_dbtp", "True peak dBTP"), ("peak_to_loudness_ratio_db", "Peak-to-loudness dB")]:
        a, b = ls.get(key), lr.get(key)
        if a is not None and b is not None:
            print(f"  {label:<22} song {a:>6.1f}   ref {b:>6.1f}   diff {a - b:+.1f}")
    ss, sref = song["samples"], ref["samples"]
    for key, label in [("rms_dbfs_per_channel", "RMS dBFS (loudest ch)"), ("sample_peak_dbfs_per_channel", "Sample peak dBFS")]:
        a, b = max(ss[key]), max(sref[key])
        print(f"  {label:<22} song {a:>6.1f}   ref {b:>6.1f}   diff {a - b:+.1f}")
    for key, label in [("stereo_correlation", "Stereo correlation"), ("mono_fold_change_db", "Mono fold dB")]:
        if ss.get(key) is not None and sref.get(key) is not None:
            print(f"  {label:<22} song {ss[key]:>6.2f}   ref {sref[key]:>6.2f}   diff {ss[key] - sref[key]:+.2f}")
    bs, br = song["samples"].get("band_share_db", {}), ref["samples"].get("band_share_db", {})
    if bs and br:
        print("  Tonal balance (song minus reference, dB). Positive = song has relatively more energy there:")
        print("   " + "  ".join(f"{k} {bs[k] - br[k]:+.1f}" for k in bs if k in br and bs[k] is not None and br[k] is not None))
        print("  Differences under ~1.5 dB are usually minor; genre and arrangement explain many differences.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--reference", help="a reference song to compare loudness and tonal balance against")
    ap.add_argument("--json", help="save all results to this JSON file")
    a = ap.parse_args()
    results = [analyze(p) for p in a.files]
    for r in results:
        print_report(r)
    ref = None
    if a.reference:
        ref = analyze(a.reference)
        print_report(ref)
        for r in results:
            print_delta(r, ref)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"results": results, "reference": ref}, fh, indent=2)
        print(f"\nSaved JSON to {a.json}")


if __name__ == "__main__":
    main()

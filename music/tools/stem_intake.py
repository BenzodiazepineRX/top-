#!/usr/bin/env python3
"""Stem intake check. Run this BEFORE any mixing or mastering.

It answers the questions that, when skipped, cost whole mix versions:
  * Are the files healthy (clipping, panning, bandwidth, silence, noise)?
  * Do the stems add up to the mixdown, or is something missing?
  * Where is the beat grid (tempo phase), if a BPM is known?
It also writes a short solo preview of every stem (same passage for all) and
a question sheet, so the ARTIST can say by ear what is on each stem.
Measurements cannot tell a "beat" from a "beat with the main vocal in it".

Usage:
  python3 stem_intake.py --stems s1.flac s2.flac [--mix dry_mix.flac]
                         [--reference original_master.flac] [--bpm 135]
                         --out intake/

Needs: numpy, scipy, soundfile. Optional: pyloudnorm (LUFS), ffmpeg (MP3 previews).
Sources are only read, never modified.
"""
import argparse
import json
import os
import shutil
import subprocess

import numpy as np
import soundfile as sf
from scipy.signal import butter, find_peaks, sosfiltfilt, welch

BLOCK_S = 0.05          # activity block length
PREVIEW_S = 15.0        # solo preview length
BANDS = [("sub", 20, 60), ("bass", 60, 250), ("low-mid", 250, 500), ("mid", 500, 2000),
         ("upper-mid", 2000, 6000), ("high", 6000, 12000), ("air", 12000, 20000)]


def db(x):
    return 20.0 * np.log10(max(float(x), 1e-12))


def block_levels(x, sr):
    """Level per 50 ms block in dBFS (power average over channels, so panning does not hide audio)."""
    n = int(BLOCK_S * sr)
    k = len(x) // n
    p = np.mean(x[:k * n] ** 2, axis=1).reshape(k, n).mean(axis=1)
    return 10.0 * np.log10(p + 1e-12)


def flat_runs(ch, level=0.99995, min_len=3):          # 0.99995 = the top code of 16-bit audio and up
    """Count runs of >= min_len consecutive samples at full scale (flat-topped, i.e. clipped)."""
    hot = np.abs(ch) >= level
    if not hot.any():
        return 0, 0
    d = np.diff(np.r_[0, hot.astype(np.int8), 0])
    lengths = np.where(d == -1)[0] - np.where(d == 1)[0]
    return int(hot.sum()), int((lengths >= min_len).sum())


def stereo_relation(x):
    """Describe how the two channels relate: dual mono, a panned copy, or true stereo."""
    L, R = x[:, 0], x[:, 1]
    rl, rr = np.sqrt(np.mean(L ** 2)), np.sqrt(np.mean(R ** 2))
    out = {"balance_L_minus_R_dB": round(db(rl) - db(rr), 2)}
    if rl < 1e-6 or rr < 1e-6:
        out["kind"] = "one channel silent"
        return out
    out["correlation"] = round(float(np.corrcoef(L, R)[0, 1]), 4)
    loud, quiet = (L, R) if rl >= rr else (R, L)
    ok = (np.abs(loud) < 0.9) & (np.abs(loud) > 1e-4)          # ignore clipped and silent samples
    g = float(np.dot(quiet[ok], loud[ok]) / np.dot(loud[ok], loud[ok]))
    resid = db(np.std(quiet[ok] - g * loud[ok])) - db(np.std(quiet[ok]))
    out.update(quiet_over_loud_gain=round(g, 5), quiet_over_loud_dB=round(db(abs(g)), 2),
               scaled_copy_residual_dB=round(resid, 1))
    if resid < -40:
        out["kind"] = "dual mono" if abs(db(abs(g))) < 0.2 else "panned copy (one channel is a quieter copy of the other)"
    else:
        out["kind"] = "true stereo"
    return out


def spectrum_summary(x, sr):
    f, p = welch(x, sr, nperseg=8192, axis=0)                # one spectrum per channel
    p = p.mean(axis=1)                                       # averaged as power, so panning does not matter
    total = p[(f >= 20) & (f <= 20000)].sum() + 1e-30
    shares = {name: round(10 * np.log10(p[(f >= lo) & (f < hi)].sum() / total + 1e-30), 1) for name, lo, hi in BANDS}
    # Bandwidth: the highest frequency still clearly above the noise floor, judged against the 1-4 kHz level
    # (judging against the loudest bin would let a strong sub-bass hide a missing top end).
    sdb = 10 * np.log10(np.convolve(p, np.ones(9) / 9, "same") + 1e-30)
    mid_level = sdb[(f >= 1000) & (f <= 4000)].mean()
    noise_floor = np.percentile(sdb[f >= 1000], 5)
    above = np.where((sdb > max(mid_level - 70, noise_floor + 15)) & (f < sr / 2 - 200))[0]
    return shares, (round(float(f[above[-1]]) / 1000, 1) if len(above) else None)


def analyse_stem(path):
    x, sr = sf.read(path, always_2d=True)
    info = sf.info(path)
    lev = block_levels(x, sr)
    thr = max(np.percentile(lev, 95) - 30.0, -60.0)
    active = lev > thr
    idx = np.where(active)[0]
    res = {"file": os.path.basename(path), "sample_rate": sr, "channels": x.shape[1], "frames": len(x),
           "seconds": round(len(x) / sr, 3), "format": info.subtype}
    res["channels_detail"] = []
    for c in range(x.shape[1]):
        n_fs, n_runs = flat_runs(x[:, c])
        res["channels_detail"].append({"peak_dBFS": round(db(np.abs(x[:, c]).max()), 2),
                                       "full_scale_samples": n_fs, "flat_runs_3plus": n_runs})
    if x.shape[1] == 2:
        res["stereo"] = stereo_relation(x)
    if len(idx):
        span = lev[idx[0]:idx[-1] + 1]
        res.update(first_sound_s=round(idx[0] * BLOCK_S, 2), last_sound_s=round((idx[-1] + 1) * BLOCK_S, 2),
                   active_pct=round(100.0 * active.mean(), 1),
                   loud_p90_dBFS=round(float(np.percentile(span, 90)), 1),
                   quiet_p10_dBFS=round(float(np.percentile(span, 10)), 1))
        res["loud_to_quiet_span_dB"] = round(res["loud_p90_dBFS"] - res["quiet_p10_dBFS"], 1)
    try:
        import pyloudnorm
        res["integrated_LUFS"] = round(float(pyloudnorm.Meter(sr).integrated_loudness(x)), 1)
    except Exception:
        res["integrated_LUFS"] = None
    res["band_shares_dB"], res["bandwidth_kHz"] = spectrum_summary(x, sr)
    return res, x, sr, active


def fit_mix(stems, mix):
    """Least-squares gains so that sum(g_i * stem_i) matches the mixdown; the residual says what is unexplained."""
    n = min(len(mix), *[len(s) for s in stems])
    A = np.stack([s[:n].ravel() for s in stems], axis=1)
    y = mix[:n].ravel()
    gains, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = db(np.std(y - A @ gains)) - db(np.std(y))
    return [float(g) for g in gains], float(resid)


def grid_offset(x, sr, bpm, t0, t1):
    """Where the 16th-note grid sits: the position (ms after t=0, within one 16th) where sharp hits pile up.

    Uses the attacks of hats, snares and kick clicks (2-10 kHz). Do NOT use the kick's low end for this:
    its body swells 20-30 ms after the click, and off-beat 808 notes drag an averaged phase far from the
    grid. On the first project that put every bar line about 95 ms late.
    Returns (offset_ms, share of hits within 10 ms of it).
    """
    hop = max(1, int(0.0005 * sr))
    y = sosfiltfilt(butter(4, [2000, min(10000, sr / 2 * 0.9)], "band", fs=sr, output="sos"), x.mean(axis=1))
    k = len(y) // hop
    env = np.sqrt(np.mean(y[:k * hop].reshape(k, hop) ** 2, axis=1))
    flux = np.clip(np.diff(env, prepend=env[0]), 0, None)
    t = np.arange(k) * hop / sr
    m = (t >= t0) & (t < t1)
    if flux[m].max() <= 0:
        return None, 0.0
    peaks, props = find_peaks(flux[m], height=np.percentile(flux[m], 99.5), distance=int(0.05 * sr / hop))
    if len(peaks) < 8:
        return None, 0.0
    period_ms = 15000.0 / bpm                                 # one 16th note
    pos = (t[m][peaks] * 1000.0) % period_ms
    w = props["peak_heights"]
    hist, edges = np.histogram(pos, bins=int(period_ms / 2), range=(0, period_ms), weights=w)
    centre = edges[int(np.argmax(hist))] + 1.0
    d = (pos - centre + period_ms / 2) % period_ms - period_ms / 2          # distance to the peak, wrapped
    near = np.abs(d) <= 10
    offset = (centre + np.sum(d[near] * w[near]) / np.sum(w[near])) % period_ms
    return round(float(offset), 1), round(float(w[near].sum() / w.sum()), 2)


def common_preview_window(actives, levels):
    """Pick one passage where as many stems as possible are sounding, so the artist compares like with like."""
    w = int(PREVIEW_S / BLOCK_S)
    n = min(len(a) for a in actives)
    if n <= w:
        return 0.0
    kernel = np.ones(w) / w
    frac = np.stack([np.convolve(a[:n].astype(float), kernel, "valid") for a in actives])
    loud = np.stack([np.convolve(l[:n], kernel, "valid") for l in levels]).mean(axis=0)
    score = frac.min(axis=0) * 100 + frac.mean(axis=0) * 10 + (loud - loud.min()) / (np.ptp(loud) + 1e-9)
    return float(np.argmax(score) * BLOCK_S)


def write_preview(x, sr, start_s, path_no_ext):
    seg = x[int(start_s * sr):int((start_s + PREVIEW_S) * sr)].copy()
    peak = np.abs(seg).max()
    if peak > 0:
        seg *= 10 ** (-3 / 20) / peak                         # same peak for every preview; pan is kept
    fade = int(0.02 * sr)
    seg[:fade] *= np.linspace(0, 1, fade)[:, None]
    seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
    wav = path_no_ext + ".wav"
    sf.write(wav, seg.astype(np.float32), sr, subtype="PCM_16")
    if shutil.which("ffmpeg"):
        mp3 = path_no_ext + ".mp3"
        done = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "192k", mp3])
        if done.returncode == 0:
            os.remove(wav)
            return mp3
    return wav


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stems", nargs="+", required=True)
    ap.add_argument("--mix", help="mixdown made with all effects bypassed (optional)")
    ap.add_argument("--reference", help="the artist's own current master, for comparison only (optional)")
    ap.add_argument("--bpm", type=float, help="project tempo, if known")
    ap.add_argument("--preview-at", type=float, help="start second for the solo previews (default: chosen automatically)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    results, audio, actives, levels, warnings = [], [], [], [], []
    for p in a.stems:
        r, x, sr, act = analyse_stem(p)
        results.append(r); audio.append(x); actives.append(act); levels.append(block_levels(x, sr))
    sr0 = results[0]["sample_rate"]
    if len({r["sample_rate"] for r in results}) > 1:
        warnings.append("Stems have different sample rates: resample before mixing.")
    if len({r["frames"] for r in results}) > 1:
        warnings.append("Stems have different lengths: confirm they all start at project time zero.")
    for r in results:
        for c, ch in enumerate(r["channels_detail"]):
            if ch["flat_runs_3plus"] > 0:
                warnings.append(f"{r['file']} ch{c + 1}: {ch['flat_runs_3plus']} flat-topped runs at full scale (clipping is in the file).")
        st = r.get("stereo", {})
        if st.get("kind", "").startswith("panned copy"):
            quiet_first = st["balance_L_minus_R_dB"] < 0
            q = r["channels_detail"][0 if quiet_first else 1]; l = r["channels_detail"][1 if quiet_first else 0]
            note = f"{r['file']}: {st['kind']}, {abs(st['quiet_over_loud_dB']):.1f} dB apart. Panning may be the artist's choice: keep it unless asked."
            if l["full_scale_samples"] and not q["full_scale_samples"]:
                note += " The quieter channel has no full-scale samples, so it can patch the clipped moments of the louder one."
            warnings.append(note)
        if r["bandwidth_kHz"] and r["bandwidth_kHz"] < 17:
            warnings.append(f"{r['file']}: little content above ~{r['bandwidth_kHz']} kHz (lossy or resampled origin). Boosting highs adds grit, not detail.")

    report = {"stems": results, "warnings": warnings}

    if a.mix:
        mix, msr = sf.read(a.mix, always_2d=True)
        if msr == sr0 and all(x.shape[1] == mix.shape[1] for x in audio):
            gains, resid = fit_mix(audio, mix)
            verdict = ("the provided stems account for the mixdown" if resid < -20 else
                       "mostly explained: some processing or material differs" if resid < -10 else
                       "NOT explained: stems are missing, or the mixdown was processed")
            report["mix_fit"] = {"gains": [round(g, 3) for g in gains], "gains_dB": [round(db(abs(g)), 2) for g in gains],
                                 "residual_dB": round(resid, 1), "verdict": verdict}
        else:
            warnings.append("Mixdown has a different sample rate or channel count: mix fit skipped.")

    if a.reference:
        ref, rsr = sf.read(a.reference, always_2d=True)
        shares, bw = spectrum_summary(ref, rsr)
        report["reference"] = {"file": os.path.basename(a.reference), "band_shares_dB": shares, "bandwidth_kHz": bw}
        try:
            import pyloudnorm
            report["reference"]["integrated_LUFS"] = round(float(pyloudnorm.Meter(rsr).integrated_loudness(ref)), 1)
        except Exception:
            pass

    if a.bpm:
        low_energy = [np.mean(sosfiltfilt(butter(4, [40, 120], "band", fs=sr0, output="sos"), x.mean(axis=1)) ** 2) for x in audio]
        i = int(np.argmax(low_energy))
        r = results[i]
        t_a, t_b = r.get("first_sound_s", 0), r.get("last_sound_s", r["seconds"])
        thirds = np.linspace(t_a, t_b, 4)
        offsets = [grid_offset(audio[i], sr0, a.bpm, thirds[k], thirds[k + 1]) for k in range(3)]
        report["beat_grid"] = {"bpm": a.bpm, "measured_on": r["file"], "beat_ms": round(60000 / a.bpm, 3),
                               "bar_ms_4_4": round(240000 / a.bpm, 3), "sixteenth_ms": round(15000 / a.bpm, 3),
                               "grid_offset_ms_early_mid_late": [o[0] for o in offsets],
                               "share_of_hits_on_grid": [o[1] for o in offsets],
                               "note": "Sharp hits (hats, snares, kick clicks) fall this many ms after each 16th-note line counted from t = 0. "
                                       "It does not say which line is beat 1 of bar 1: find that from the arrangement (drops, pattern) "
                                       "and check that real hits sit within a few ms of your bar lines early, in the middle and late."}

    start = a.preview_at if a.preview_at is not None else common_preview_window(actives, levels)
    previews = []
    for n, (r, x) in enumerate(zip(results, audio), 1):
        name = os.path.splitext(r["file"])[0]
        previews.append(os.path.basename(write_preview(x, r["sample_rate"], start, os.path.join(a.out, f"Preview_{n}_{name}"))))
    report["previews"] = {"start_s": round(start, 2), "length_s": PREVIEW_S, "files": previews}

    with open(os.path.join(a.out, "intake.json"), "w") as f:
        json.dump(report, f, indent=1)

    lines = ["# Stem intake report", "",
             "**Roles are NOT verified by this report.** Do not process anything until the artist has listened to the",
             "previews and said what is on each stem.", "", "## Stems", "",
             "| # | File | Length | Loudness | Peaks L/R (dBFS) | Full-scale samples | Stereo | Sound from-to (s) | Loud-quiet span | Reaches |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(results, 1):
        ch = r["channels_detail"]
        lines.append("| {} | {} | {:.1f} s | {} LUFS | {} | {} | {} | {}-{} | {} dB | {} kHz |".format(
            n, r["file"], r["seconds"], r["integrated_LUFS"], " / ".join(str(c["peak_dBFS"]) for c in ch),
            " / ".join(str(c["full_scale_samples"]) for c in ch), r.get("stereo", {}).get("kind", "mono"),
            r.get("first_sound_s", "-"), r.get("last_sound_s", "-"), r.get("loud_to_quiet_span_dB", "-"), r["bandwidth_kHz"]))
    if "mix_fit" in report:
        m = report["mix_fit"]
        lines += ["", "## Do the stems add up to the mixdown?", "",
                  "Fader gains that best rebuild the mixdown: " + ", ".join(f"stem {i + 1}: {g} dB" for i, g in enumerate(m["gains_dB"])) + ".",
                  f"Unexplained remainder: {m['residual_dB']} dB. Verdict: **{m['verdict']}**.",
                  "These gains are the artist's own dry balance: start from them, not from a genre default."]
    if "reference" in report:
        ref = report["reference"]
        lines += ["", "## The artist's current master (reference only)", "",
                  f"{ref['file']}: {ref.get('integrated_LUFS', '?')} LUFS, content to ~{ref['bandwidth_kHz']} kHz. "
                  "Its tone and balance are what the artist is used to: stay close unless asked to change them."]
    if "beat_grid" in report:
        g = report["beat_grid"]
        lines += ["", "## Beat grid", "",
                  f"{g['bpm']} BPM: beat {g['beat_ms']} ms, bar {g['bar_ms_4_4']} ms, 16th {g['sixteenth_ms']} ms. Measured on {g['measured_on']}: "
                  f"hits sit {g['grid_offset_ms_early_mid_late']} ms after each 16th line (early / middle / late), "
                  f"share of hits on that grid {g['share_of_hits_on_grid']}.", g["note"]]
    lines += ["", "## Warnings", ""] + ([f"- {w}" for w in warnings] or ["- none"])
    lines += ["", "## Previews for the artist", "",
              f"Same {PREVIEW_S:.0f} seconds of every stem, starting at {start:.1f} s: " + ", ".join(previews) + "."]
    with open(os.path.join(a.out, "intake_report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    q = ["# Questions for the artist (ask before mixing)", "",
         "Play each preview, then answer in a few words.", ""]
    for n, p in enumerate(previews, 1):
        q.append(f"{n}. **{p}**: what do you hear? (beat only / beat + main vocal / main vocal / adlibs or backing / something else)")
    k = len(previews)
    q += [f"{k + 1}. Is anything missing that should be its own track (main vocal, adlibs, hook, beat)?",
          f"{k + 2}. Which effects in your current version do you want to KEEP the feel of (echo, reverb, autotune, panning)?",
          f"{k + 3}. What bothers you most in your current version? (one or two things)",
          f"{k + 4}. Name one released song whose sound you want to be close to (optional)."]
    with open(os.path.join(a.out, "ASK_THE_ARTIST.md"), "w") as f:
        f.write("\n".join(q) + "\n")

    print("\n".join(lines))


if __name__ == "__main__":
    main()

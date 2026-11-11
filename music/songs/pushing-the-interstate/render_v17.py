#!/usr/bin/env python3
"""v17 from the v16 stems. Only the adlib delay, the phone vocal level, the phone
delay and the stutters change. Everything else is the v16 mix.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v16", os.path.join(HERE, "render_v16.py"))
v16 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v16)

SR = v16.SR
BPM = v16.BPM
WORK = v16.WORK
Q = int(round(60000.0 / BPM * SR / 1000.0))  # 20512 samples, 465.12 ms
E = Q // 2  # 10256 samples, 232.56 ms
LEAD_FADER = v16.LEAD_FADER
ADLIB_FADER = v16.ADLIB_FADER
OUTRO_BUS = v16.OUTRO_BUS
# Measured against the beat, the phone vocal is 8 dB hotter than the verse vocal.
# A 4 dB cut would still leave it about 4 dB hot, so the trim is 8 dB.
PHONE_DB = -8.0
ADLIB_BUMP = 3.0


def mono(x):
    return x[:, 0] if x.ndim == 2 else x


def active_db(x, t0, t1, thr=-30.0):
    m = mono(x)
    i0, i1 = int(t0 * SR), min(len(m), int(t1 * SR))
    seg = m[i0:i1]
    hop = int(0.02 * SR)
    n = len(seg) // hop
    if n < 2:
        return -120.0
    rms = np.sqrt((seg[: n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(np.maximum(rms, 1e-12))
    keep = db[db > thr]
    if not len(keep):
        keep = db
    return float(10 * np.log10(np.mean(10 ** (keep / 10))))


def grid_sample(t_samples, step):
    return int(round(t_samples / step) * step)


def off_ms(t, division):
    step = (60.0 / BPM) / (division / 4.0)
    nearest = round(t / step) * step
    return (t - nearest) * 1000.0


def place(buf, audio, start, fade_in=0.008, fade_out=0.025):
    audio = np.asarray(audio, dtype=np.float64).copy()
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    if len(audio) > fi + fo + 8:
        audio[:fi] *= np.linspace(0, 1, fi)
        audio[-fo:] *= np.linspace(1, 0, fo)
    i0 = int(start)
    if i0 < 0:
        audio = audio[-i0:]
        i0 = 0
    i1 = min(len(buf), i0 + len(audio))
    if i1 <= i0:
        return
    buf[i0:i1] += audio[: i1 - i0]


def first_word_len(x, onset):
    """Onset to the end of the first word. Early consonant dips are ignored."""
    m = mono(x)
    i = int(onset * SR)
    hop = int(0.005 * SR)
    frame = m[i:i + int(0.55 * SR)]
    n = len(frame) // hop
    if n < 8:
        return 0.28
    rms = np.sqrt((frame[: n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(np.maximum(rms, 1e-9))
    peak = np.max(db[:12]) if len(db) >= 12 else db.max()
    # Don't call a consonant gap the end of the word. Look only after 0.18 s.
    start_k = int(0.18 / 0.005)
    for k in range(start_k, len(db) - 3):
        if db[k] < -32 and db[k:k + 3].mean() < peak - 8:
            return max(0.20, k * 0.005)
    return min(0.42, n * 0.005)


def build_stutters(phone, placed):
    """Most of the first word, at least an eighth note when the word is that long, on the grid."""
    out = np.zeros_like(phone)
    rows = []
    info = []
    for p in placed:
        on, off = v16.speech_bounds(phone, p["i0"], p["i1"])
        info.append((p, on, off))
    for idx, (p, on, off) in enumerate(info):
        prev_end = info[idx - 1][2] if idx else on - 5.0
        word = first_word_len(phone, on)
        eighth = E / SR
        # Almost the whole first word, and never shorter than an eighth note.
        chop = max(eighth, min(0.88 * word, 0.42))
        step = Q if chop > eighth + 0.02 else E
        gap = on - prev_end
        onset_i = int(round(on * SR))
        chop_n = int(round(chop * SR))
        # Last chop ends as the real word begins, and its start is on the grid.
        target = onset_i - chop_n
        g = grid_sample(target, step)
        if g + chop_n > onset_i - int(0.004 * SR):
            g -= step
        starts = []
        s = g
        while s >= int((prev_end + 0.012) * SR) and len(starts) < 3:
            starts.append(s)
            s -= step
        starts = list(reversed(starts))
        if not starts:
            # The gap is shorter than one chop. One grid chop that ends at the word,
            # even if it borrows the tail of the previous line, is the only way to
            # keep a full eighth on the beat. Prefer the grid line that overlaps least.
            s = grid_sample(target, step)
            if s + chop_n > onset_i:
                s -= step
            starts = [s]
        print(f"stutter {p['block']}{p['name']}: word {word * 1000:.0f} ms, chop {chop * 1000:.0f} ms, "
              f"gap {gap * 1000:.0f} ms, step {step / SR * 1000:.1f} ms, repeats {len(starts)}", flush=True)
        src = int(round(on * SR))
        seg_src = phone[src:src + chop_n]
        for k, start in enumerate(starts):
            gdb = -4.0 + 3.0 * k / max(len(starts) - 1, 1)
            seg = seg_src * 10 ** (gdb / 20)
            place(out, seg, start, fade_in=0.006, fade_out=0.02)
            t = start / SR
            rows.append({
                "line": f"block {p['block']} line {p['name']}", "k": k + 1, "of": len(starts),
                "start": t, "chop_ms": chop_n / SR * 1000, "word": on, "gap_ms": gap * 1000,
                "off_8": off_ms(t, 8), "off_4": off_ms(t, 4), "gain_db": gdb,
            })
    return out, rows


def shifted_send(source, windows, note_samples, grid_step):
    """Land the first tap on the grid. Later taps stay there because the delay is exact."""
    buf = np.zeros(len(source) + note_samples * 4)
    notes = []
    for lo, hi in windows:
        i0, i1 = int(round(lo * SR)), int(round(hi * SR))
        natural = i0 + note_samples
        g = grid_sample(natural, grid_step)
        delta_ms = (g - natural) / SR * 1000.0
        place(buf, source[i0:i1], i0 + (g - natural), fade_out=0.10)
        notes.append({"source": lo, "end": hi, "tap": g / SR, "nudge_ms": delta_ms,
                      "off_8": off_ms(g / SR, 8), "off_4": off_ms(g / SR, 4)})
        print(f"  word {lo:.3f}-{hi:.3f} tap {natural / SR:.3f} -> {g / SR:.3f}  nudge {delta_ms:+.1f} ms "
              f"8th {notes[-1]['off_8']:+.2f} quarter {notes[-1]['off_4']:+.2f}", flush=True)
    return buf, notes


def soften_cuts(x):
    """Fade the delay send into a steep drop so the echo doesn't stop dead."""
    y = np.asarray(x, dtype=np.float64).copy()
    hop = int(0.01 * SR)
    n = len(y) // hop
    rms = np.sqrt((y[: n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(np.maximum(rms, 1e-9))
    fade_n = int(0.10 * SR)
    covered = np.zeros(len(y), dtype=bool)
    for i in range(2, n):
        if db[i - 2] > -26 and db[i - 2] - db[i] > 9:
            end = i * hop
            start = max(0, end - fade_n)
            if covered[start:end].any():
                continue
            y[start:end] *= np.linspace(1, 0, end - start)
            covered[start:end] = True
    return y


def main():
    lead, _ = v16.read_audio(f"{WORK}/lead.wav")
    ad, _ = v16.read_audio(f"{WORK}/ad.wav")
    beat, _ = v16.read_audio(f"{WORK}/beat_f.wav")
    phone, _ = v16.read_audio(f"{WORK}/phone.wav")
    lead_m, ad_m, phone_m = mono(lead), mono(ad), mono(phone)
    lg, bg = 10 ** (LEAD_FADER / 20), 10 ** (OUTRO_BUS / 20)

    def rel(vocal, t0, t1, vocal_gain):
        v = active_db(vocal * vocal_gain, t0, t1)
        b = active_db(beat, t0, t1, thr=-24)
        return v, b, v - b

    print("Phone vocal versus the verse, before the trim:", flush=True)
    lv, lb, ld = rel(lead_m, 20, 55, lg)
    print(f"  verse lead {lv:.1f} dB, beat {lb:.1f}, lead-minus-beat {ld:+.1f} dB")
    pv, pb, pd = rel(phone_m, 135.1, 149.5, bg)
    print(f"  phone     {pv:.1f} dB, beat {pb:.1f}, phone-minus-beat {pd:+.1f} dB")
    print(f"  phone sits {pd - ld:+.1f} dB hotter than the verse vocal against the beat", flush=True)

    # Adlib delay keeps the dotted eighth. The send fades into hard phrase endings
    # (the 2:14.7 echo was a copy of a cut at 2:14.3). Repeats are +3 dB, then a short plate.
    softened = soften_cuts(ad_m)
    v16.write_audio(f"{WORK}/ad_send17.wav", softened)
    v16.dsp("delay", f"{WORK}/ad_send17.wav", f"{WORK}/ad_delay17.wav", "--bpm", "129", "--note", "1/8d",
            "--feedback", "0.35", "--hp", "300", "--lp", "6000", "--return-db", "-6.79",
            "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4", "--duck-attack", "5", "--duck-release", "80")
    v16.dsp("reverb", f"{WORK}/ad_delay17.wav", f"{WORK}/ad_plate17.wav",
            "--type", "plate", "--decay", "1.2", "--predelay", "29.07",
            "--hp", "400", "--lp", "5000", "--return-db", "-8",
            "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "3")

    words = json.load(open(f"{WORK}/words_fixed.json"))
    # A copy longer than one beat makes the repeats overlap. Keep the end of the word.
    trimmed = []
    for a, b in words["words"]:
        if b - a > 0.42:
            print(f"  trim {a:.3f}-{b:.3f} ({(b - a) * 1000:.0f} ms) to {b - 0.42:.3f}-{b:.3f}", flush=True)
            a = b - 0.42
        trimmed.append((a, b))
    print("Lead echoes, feedback 0.5, first tap still about 12 dB under, landed on the eighth grid:", flush=True)
    send, lead_notes = shifted_send(lead_m, trimmed, Q, E)
    v16.write_audio(f"{WORK}/lead_send17.wav", send)
    v16.dsp("delay", f"{WORK}/lead_send17.wav", f"{WORK}/lead_echo17.wav", "--bpm", "129", "--note", "1/4",
            "--feedback", "0.5", "--hp", "450", "--lp", "5000", "--return-db", "-6.82",
            "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4", "--duck-attack", "5", "--duck-release", "80")
    print("Verse throw:", flush=True)
    half = int(round(120000.0 / BPM * SR / 1000.0))  # 41023 samples, the delay tool's half note
    tsend, throw_notes = shifted_send(lead_m, words["throw"], half, E)
    v16.write_audio(f"{WORK}/throw_send17.wav", tsend)
    v16.dsp("delay", f"{WORK}/throw_send17.wav", f"{WORK}/v1_throw17.wav", "--bpm", "129", "--note", "1/2",
            "--feedback", "0.35", "--hp", "350", "--lp", "4500", "--return-db", "-8.08",
            "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4", "--duck-attack", "5", "--duck-release", "80")
    v16.dsp("reverb", f"{WORK}/v1_throw17.wav", f"{WORK}/v1_throw_hall17.wav", "--type", "hall",
            "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-10",
            "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4")

    phone17 = phone_m * 10 ** (PHONE_DB / 20)
    BAR = 4 * 60.0 / BPM
    placed = []
    for bi, bars in enumerate((56, 60, 64)):
        shift = int(round(bars * BAR * SR))
        for name, lo, hi in (("A", 30.80, 34.62), ("B", 34.70, 38.25)):
            i0 = int(round(lo * SR)) + shift
            i1 = int(round(hi * SR)) + shift
            placed.append({"block": bi + 1, "name": name, "i0": i0, "i1": i1})
    stutters, stutter_rows = build_stutters(phone17, placed)
    v16.write_audio(f"{WORK}/stutters17.wav", stutters)
    hiss = v16.add_hiss(phone17 + stutters)
    bus = phone17 + stutters + hiss
    v16.write_audio(f"{WORK}/phone_bus17.wav", bus)
    v16.dsp("reverb", f"{WORK}/phone_bus17.wav", f"{WORK}/hall_all17.wav", "--type", "hall",
            "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-14",
            "--duck-by", f"{WORK}/phone_bus17.wav", "--duck-depth", "3")
    for block, decay, ret, name in ((2, "1.86047", "-9", "hall_b2_17"), (3, "2.7907", "-7", "hall_b3_17")):
        mask = np.zeros_like(bus)
        for p in placed:
            if p["block"] == block:
                mask[p["i0"]:p["i1"]] = bus[p["i0"]:p["i1"]]
        v16.write_audio(f"{WORK}/{name}_send.wav", mask)
        v16.dsp("reverb", f"{WORK}/{name}_send.wav", f"{WORK}/{name}.wav", "--type", "hall",
                "--decay", decay, "--predelay", "29.07", "--return-db", ret)

    print("Phone delay, +3 semitones, one beat, on the quarter grid:", flush=True)
    pitched = v16.pitch_up(phone17, 3)
    send = np.zeros(len(pitched) + Q * 6)
    phone_notes = []
    for p in placed:
        on, off = v16.speech_bounds(phone17, p["i0"], p["i1"])
        i0, i1 = int(round(on * SR)), int(round(off * SR))
        # Exactly one beat after the line. The lines sit where v4 put them, so the
        # echo inherits that placement. Snapping it onto a downbeat would make the
        # lag no longer one beat.
        place(send, pitched[i0:i1], i0)
        g = i0 + Q
        phone_notes.append({"line": f"block {p['block']} {p['name']}", "source": on, "tap": g / SR,
                            "nudge_ms": (g - natural) / SR * 1000, "off_4": off_ms(g / SR, 4)})
        print(f"  {phone_notes[-1]['line']} onset {on:.3f} tap {g / SR:.3f} nudge {phone_notes[-1]['nudge_ms']:+.1f} ms",
              flush=True)
    v16.write_audio(f"{WORK}/phone_send17.wav", send)
    v16.dsp("delay", f"{WORK}/phone_send17.wav", f"{WORK}/phone_delay17_raw.wav", "--bpm", "129", "--note", "1/4",
            "--feedback", "0.35", "--hp", "400", "--lp", "3500", "--return-db", "0")
    raw, _ = v16.read_audio(f"{WORK}/phone_delay17_raw.wav")
    deltas = []
    for nte in phone_notes:
        i = int(nte["source"] * SR)
        j = int(nte["tap"] * SR)
        n = int(0.2 * SR)
        dry = np.sqrt(np.mean(phone17[i:i + n] ** 2))
        echo = np.sqrt(np.mean(mono(raw)[j:j + n] ** 2))
        if dry > 1e-6:
            deltas.append(20 * np.log10(echo / dry))
    med = float(np.median(deltas)) if deltas else 0.0
    ret = -12.0 - med
    print(f"phone delay at 0 dB is {med:+.1f} dB vs the line; return {ret:+.1f} dB so the first tap is -12 dB", flush=True)
    v16.dsp("delay", f"{WORK}/phone_send17.wav", f"{WORK}/phone_delay17.wav", "--bpm", "129", "--note", "1/4",
            "--feedback", "0.35", "--hp", "400", "--lp", "3500", "--return-db", f"{ret:.2f}",
            "--duck-by", f"{WORK}/phone_bus17.wav", "--duck-depth", "2", "--duck-attack", "5", "--duck-release", "80")

    v16.dsp("mix", f"{WORK}/outro_17.wav",
            "--track", f"{WORK}/phone_bus17.wav:0",
            "--track", f"{WORK}/phone_delay17.wav:0",
            "--track", f"{WORK}/hall_all17.wav:0",
            "--track", f"{WORK}/hall_b2_17.wav:0",
            "--track", f"{WORK}/hall_b3_17.wav:0")
    x, _ = v16.read_audio(f"{WORK}/outro_17.wav")
    v16.write_audio(f"{WORK}/outro_17.wav", x * 10 ** (OUTRO_BUS / 20))

    print("Phone vocal after -4 dB (same bus gain as v16):", flush=True)
    pv2, pb2, pd2 = rel(phone17, 135.1, 149.5, bg)
    print(f"  phone {pv2:.1f} dB, beat {pb2:.1f}, phone-minus-beat {pd2:+.1f} dB", flush=True)
    print(f"  was {pd:+.1f} dB over the beat, now {pd2:+.1f}; verse vocal is {ld:+.1f}", flush=True)

    v16.dsp("mix", f"{WORK}/mix17.wav",
            "--track", f"{WORK}/beat_f.wav:0",
            "--track", f"{WORK}/lead.wav:{LEAD_FADER}",
            "--track", f"{WORK}/ad.wav:{ADLIB_FADER}",
            "--track", f"{WORK}/plate.wav:{LEAD_FADER}",
            "--track", f"{WORK}/ad_delay17.wav:{ADLIB_FADER}",
            "--track", f"{WORK}/ad_plate17.wav:{ADLIB_FADER}",
            "--track", f"{WORK}/lead_echo17.wav:{LEAD_FADER}",
            "--track", f"{WORK}/v1_throw17.wav:{LEAD_FADER}",
            "--track", f"{WORK}/v1_throw_hall17.wav:{LEAD_FADER}",
            "--track", f"{WORK}/fx_16.wav:0",
            "--track", f"{WORK}/outro_17.wav:0")
    v16.dsp("ms-bus", f"{WORK}/mix17.wav", f"{WORK}/bus17.wav", "--side-hp", "90", "--mid-shelf", "9500:2.0")
    bus, _ = v16.read_audio(f"{WORK}/bus17.wav")
    bus = v16.fade_db(bus, 157.4, 159.15, 0, -30)
    end = int(160.6 * SR)
    y = bus[:end].copy()
    fade = int(1.2 * SR)
    y[-fade:] *= np.linspace(1, 0, fade)[:, None]
    v16.write_audio(f"{WORK}/bus17_t.wav", y)
    settings = json.load(open(f"{WORK}/master4.wav.settings.json"))
    gain, limit = settings["gain_into_limiter_db"], settings["limiter"]["limit_db"]
    v16.ffmpeg_af(f"{WORK}/bus17_t.wav", f"{WORK}/master17.wav",
                  f"volume={gain:.3f}dB,aresample={SR * 4}:resampler=soxr,"
                  f"alimiter=limit={limit:.3f}dB:attack=5:release=60:level=disabled:latency=true,"
                  f"aresample={SR}:resampler=soxr")

    song = os.path.join(os.path.dirname(HERE), "..", "..") if False else os.path.dirname(HERE)
    # HERE is the song directory
    v16.sh([sys.executable, os.path.join(os.path.dirname(HERE), "..", "tools", "export_master.py")
            if False else os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools", "export_master.py"),
            f"{WORK}/master17.wav", "--name", "Pushing_the_Interstate_master_v17",
            "--outdir", HERE, "--rate", "44100"])
    v16.dsp("mix", f"{WORK}/fxbus17.wav",
            "--track", f"{WORK}/lead_echo17.wav:{LEAD_FADER}",
            "--track", f"{WORK}/v1_throw17.wav:{LEAD_FADER}",
            "--track", f"{WORK}/ad_delay17.wav:{ADLIB_FADER}",
            "--track", f"{WORK}/ad_plate17.wav:{ADLIB_FADER}",
            "--track", f"{WORK}/phone_delay17.wav:{OUTRO_BUS}",
            "--track", f"{WORK}/stutters17.wav:{OUTRO_BUS}")
    v16.sh([sys.executable, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools", "export_master.py"),
            f"{WORK}/fxbus17.wav", "--name", "Pushing_the_Interstate_v17_effects_bus",
            "--outdir", HERE, "--rate", "44100", "--mp3", "none"])
    v16.sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", "128", "-i",
            os.path.join(HERE, "Pushing_the_Interstate_master_v17_24bit.wav"),
            "-b:a", "320k", os.path.join(HERE, "Outro_preview_v17.mp3")])

    # Confirm the phone delay really sits about 12 dB under, and list grid offsets.
    final, _ = v16.read_audio(f"{WORK}/phone_delay17.wav")
    ratios = []
    for nte in phone_notes:
        i = int(nte["source"] * SR)
        j = int(nte["tap"] * SR)
        n = int(0.18 * SR)
        dry = np.sqrt(np.mean(phone17[i:i + n] ** 2))
        echo = np.sqrt(np.mean(mono(final)[j:j + n] ** 2))
        if dry > 1e-6 and echo > 1e-8:
            ratios.append(20 * np.log10(echo / dry))
    print(f"heard phone first-tap vs the line: {float(np.median(ratios)):+.1f} dB", flush=True)
    print("Grid check (flag if the absolute offset is over 5 ms):", flush=True)
    flags = []
    for nte in lead_notes + throw_notes:
        flag = abs(nte["off_8"]) > 5
        flags.append(flag)
        print(f"  lead/throw {nte['source']:.3f} 8th {nte['off_8']:+.2f} ms  quarter {nte['off_4']:+.2f} ms"
              + ("  FLAG" if flag else ""))
    for nte in phone_notes:
        print(f"  phone {nte['line']} quarter offset {nte['off_4']:+.2f} ms")
    for s in stutter_rows:
        worst = min(abs(s["off_8"]), abs(s["off_4"]))
        mark = "FLAG" if worst > 5 else "ok"
        print(f"  stutter {s['line']} {s['k']}/{s['of']} at {s['start']:.3f} "
              f"8th {s['off_8']:+.2f}  quarter {s['off_4']:+.2f}  {mark}")
    json.dump({"phone_before_db": pd, "phone_after_db": pd2, "verse_db": ld,
               "lead_notes": lead_notes, "throw_notes": throw_notes, "phone_notes": phone_notes,
               "stutters": stutter_rows, "phone_ratio_db": float(np.median(ratios)) if ratios else None,
               "adlib_bump_db": ADLIB_BUMP, "phone_trim_db": PHONE_DB},
              open(f"{WORK}/v17_report.json", "w"), indent=2)
    print("V17_DONE", flush=True)


if __name__ == "__main__":
    main()

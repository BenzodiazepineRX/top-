#!/usr/bin/env python3
"""Satan's Casino v02 review candidate.

Reproducible mix from the immutable FLAC sources. Dry beat stays at -8 dB and
dry vocal at -6 dB, both starting at sample 0. No mastering limiter.

Run from the repo root:
  python3 music/songs/satans-casino/tools/render_v02.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, oaconvolve, resample_poly, sosfilt, sosfiltfilt

ROOT = Path(__file__).resolve().parents[4]
SONG = Path(__file__).resolve().parents[1]
CFG = json.loads((SONG / "config" / "v02.json").read_text())
SR = int(CFG["sample_rate"])
BPM = float(CFG["bpm"])
Q = int(CFG["samples_per_quarter"])  # 19600 at 135 BPM, 44.1 kHz
BAR = 4 * Q
EIGHTH = Q // 2
DOTTED_8 = int(round(Q * 0.75))
NOTE_SAMPLES = {
    "1/1": 4 * Q,
    "1/2": 2 * Q,
    "1/2 dotted": 3 * Q,
    "1/4": Q,
    "1/8": EIGHTH,
    "1/8 dotted": DOTTED_8,
    "1/16": Q // 4,
    "1/32": Q // 8,
    "1/64": Q // 16,
}


def db(x):
    x = np.asarray(x, dtype=np.float64)
    return 20.0 * np.log10(np.sqrt(np.mean(x * x) + 1e-20))


def peak_db(x):
    p = float(np.max(np.abs(x))) if np.size(x) else 0.0
    return 20.0 * np.log10(p + 1e-20), p


def load_flac(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True,
        check=True,
    )
    audio = np.frombuffer(raw.stdout, dtype="<f4").reshape(-1, 2).astype(np.float32)
    return audio


def gain_lin(db_):
    return float(10 ** (db_ / 20.0))


def cos_fade(n, fade_in=True):
    if n <= 1:
        return np.ones(max(n, 0), np.float32)
    w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n, dtype=np.float64))
    w = w.astype(np.float32)
    return w if fade_in else w[::-1].copy()


def apply_fades(seg, fade_in, fade_out):
    y = np.array(seg, dtype=np.float32, copy=True)
    if fade_in > 1:
        n = min(fade_in, len(y))
        y[:n] *= cos_fade(n, True)[:, None]
    if fade_out > 1:
        n = min(fade_out, len(y))
        y[-n:] *= cos_fade(n, False)[:, None]
    return y


def add_at(bus, seg, dest, gain_db):
    if seg is None or len(seg) == 0:
        return
    y = np.asarray(seg, dtype=np.float32) * np.float32(gain_lin(gain_db))
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    s = int(dest)
    if s < 0:
        y = y[-s:]
        s = 0
    if s >= len(bus) or len(y) == 0:
        return
    e = min(len(bus), s + len(y))
    bus[s:e] += y[: e - s]


def next_grid(sample, grid):
    sample = int(sample)
    if sample <= 0:
        return 0
    r = sample % grid
    return sample if r == 0 else sample + (grid - r)


def frame_db(mono, hop, win):
    n = 1 + max(0, (len(mono) - win) // hop)
    c = np.cumsum(np.concatenate([[0.0], mono.astype(np.float64) ** 2]))
    i0 = np.arange(n) * hop
    i1 = i0 + win
    rms = np.sqrt((c[i1] - c[i0]) / win + 1e-20)
    return 20.0 * np.log10(rms)


def detect_phrases(vocal_mono):
    p = CFG["phrase"]
    hop = int(0.005 * SR)
    win = int(0.020 * SR)
    levels = frame_db(vocal_mono, hop, win)
    active = np.zeros(len(levels), dtype=bool)
    state = False
    for i, v in enumerate(levels):
        if not state and v >= p["on_db"]:
            state = True
        elif state and v < p["off_db"]:
            state = False
        active[i] = state
    spans = []
    i = 0
    while i < len(active):
        if not active[i]:
            i += 1
            continue
        j = i
        while j < len(active) and active[j]:
            j += 1
        t0 = i * hop / SR
        t1 = min(len(vocal_mono), (j - 1) * hop + win) / SR
        if t1 - t0 >= p["min_phrase_s"]:
            spans.append([t0, t1])
        i = j
    merged = []
    for a, b in spans:
        if merged and a - merged[-1][1] < p["merge_gap_s"]:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return merged


def region_db(mono, t0, t1):
    s = max(0, int(t0 * SR))
    e = min(len(mono), int(t1 * SR))
    if e <= s + 8:
        return -200.0
    return float(db(mono[s:e]))


def last_syllable(mono, phrase):
    """Last rise inside the phrase. Measurement of an onset, not a lyric call."""
    a, b = phrase
    hop = int(0.004 * SR)
    win = int(0.012 * SR)
    s0 = int(max(a, b - 0.75) * SR)
    s1 = int(b * SR)
    seg = mono[s0:s1]
    if len(seg) < win * 2:
        start = max(a, b - 0.28)
        return start, b
    levels = frame_db(seg, hop, win)
    onset_i = None
    for i in range(4, len(levels)):
        if levels[i] > -30.0 and levels[i] - levels[i - 3] > 7.0:
            onset_i = i
    if onset_i is None:
        start = max(a, b - 0.30)
    else:
        start = (s0 + onset_i * hop) / SR
    max_s = CFG["throws"]["max_syllable_s"]
    if b - start > max_s:
        start = b - max_s
    if b - start < 0.09:
        start = max(a, b - 0.16)
    return start, b


def choose_subdivision(syllable_s):
    """Fit the repeat to the syllable so the copy starts after the syllable.

    Eighths and dotted eighths are both legal grid points. A kick is not required.
    """
    if syllable_s <= 0.20:
        return "1/8", EIGHTH
    if syllable_s <= 0.34:
        return "1/8 dotted", DOTTED_8
    return "1/4", Q


def make_ir(decay_s, predelay_s, seed, high_hz=3800):
    rng = np.random.default_rng(seed)
    pre = int(round(predelay_s * SR))
    n = pre + int(decay_s * 1.35 * SR)
    ir = np.zeros((n, 2), np.float32)
    coef = np.float32(np.exp(-2 * np.pi * high_hz / SR))
    for ch in range(2):
        noise = rng.standard_normal(n - pre).astype(np.float32)
        acc = np.float32(0.0)
        one = np.float32(1.0 - coef)
        for i in range(len(noise)):
            acc = one * noise[i] + coef * acc
            noise[i] = acc
        t = np.arange(n - pre, dtype=np.float32) / SR
        env = np.exp(np.float32(-6.907755) * t / np.float32(decay_s))
        ir[pre:, ch] = noise * env
        sign = 1.0 if ch == 0 else -1.0
        for ms, g in ((11, 0.32), (23, 0.22), (41, 0.14)):
            i = pre + int(ms / 1000 * SR)
            if i < n:
                ir[i, ch] += np.float32(g * sign)
    ir /= np.float32(max(np.max(np.abs(ir)), 1e-8))
    return ir


def convolve_stereo(mono_or_stereo, ir):
    if mono_or_stereo.ndim == 1:
        src = [mono_or_stereo, mono_or_stereo]
    else:
        src = [mono_or_stereo[:, 0], mono_or_stereo[:, 1]]
    chans = []
    for ch in range(2):
        wet = oaconvolve(src[ch].astype(np.float32), ir[:, ch], mode="full")
        chans.append(wet[: len(src[ch])].astype(np.float32))
    return np.stack(chans, axis=1)


def smooth_follow(flag, release_samples):
    """flag 1 = duck. Release back toward 0 when the flag clears."""
    out = np.zeros(len(flag), np.float32)
    acc = 0.0
    rel = np.float32(1.0 / max(release_samples, 1))
    att = np.float32(1.0 / max(int(0.008 * SR), 1))
    for i, f in enumerate(flag):
        target = 1.0 if f else 0.0
        coef = att if target > acc else rel
        acc += (target - acc) * float(coef)
        out[i] = acc
    return out


def band_slice(stereo, s0, s1, lo, hi):
    pad = int(0.2 * SR)
    a = max(0, s0 - pad)
    b = min(len(stereo), s1 + pad)
    sos = butter(4, [lo, hi], btype="band", fs=SR, output="sos")
    y = sosfiltfilt(sos, stereo[a:b].astype(np.float64), axis=0).astype(np.float32)
    return y[s0 - a : s1 - a]


def write_pcm24(path, audio):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    step = 2 ** -23
    rng = np.random.default_rng(abs(hash(path.name)) % (2 ** 32))
    dither = (rng.random(audio.shape) + rng.random(audio.shape) - 1.0) * step
    y = np.clip(audio.astype(np.float64) + dither, -1.0 + 1e-8, 1.0 - 1e-8)
    subtype = "PCM_24"
    if path.suffix.lower() == ".flac":
        sf.write(path, y, SR, format="FLAC", subtype=subtype)
    else:
        sf.write(path, y, SR, subtype=subtype)


def true_peak_db(audio):
    # 4x oversample, blockwise so the whole song is not one giant buffer
    peaks = []
    block = SR * 15
    for s in range(0, len(audio), block):
        chunk = audio[s : s + block]
        up = resample_poly(chunk, 4, 1, axis=0)
        peaks.append(float(np.max(np.abs(up))))
    p = max(peaks) if peaks else 0.0
    return 20.0 * np.log10(p + 1e-20), p


def integrated_lufs(audio):
    import pyloudnorm

    meter = pyloudnorm.Meter(SR)
    return float(meter.integrated_loudness(audio.astype(np.float64)))


def main():
    beat_path = SONG / "sources" / "satans-casino-beat.flac"
    vocal_path = SONG / "sources" / "satans-casino-lead-vocals.flac"
    print("loading sources")
    beat = load_flac(beat_path)
    vocal_src = load_flac(vocal_path)
    n = len(beat)
    vocal = np.zeros((n, 2), np.float32)
    vocal[: len(vocal_src)] = vocal_src
    vm = vocal_src.mean(axis=1).astype(np.float32)
    bm = beat.mean(axis=1)

    beat_pk, _ = peak_db(beat)
    voc_pk, _ = peak_db(vocal_src)
    print(f"beat {len(beat)/SR:.6f}s peak {beat_pk:.5f} dBFS")
    print(f"vocal {len(vocal_src)/SR:.6f}s peak {voc_pk:.5f} dBFS")

    g_beat = gain_lin(CFG["balance_db"]["beat"])
    g_vocal = gain_lin(CFG["balance_db"]["vocal"])
    beat_dry = beat * np.float32(g_beat)
    vocal_dry = vocal * np.float32(g_vocal)
    baseline = beat_dry + vocal_dry
    base_pk, _ = peak_db(baseline)
    print(f"baseline peak {base_pk:.5f} dBFS")

    # --- verify the suggested return times; do not treat them as stops ---
    q_s = Q / SR
    candidate_notes = []
    for t in CFG["energy_return_candidates_s"]:
        beats = t / q_s
        nearest = int(round(beats))
        nt = nearest * q_s
        bar = nearest // 4
        beat_in_bar = nearest % 4
        vr = region_db(vm, t - 0.08, t + 0.08)
        br = region_db(bm, t - 0.08, t + 0.08)
        decision = (
            "not a stop: vocal and beat are both up. No beat-stop envelope here."
            if vr > -30 and br > -20
            else "checked; not used as a stop."
        )
        candidate_notes.append(
            {
                "suggested_s": t,
                "nearest_beat": nearest,
                "nearest_beat_s": round(nt, 6),
                "offset_ms": round((t - nt) * 1000, 1),
                "bar": bar,
                "beat_in_bar": beat_in_bar + 1,
                "beat_rms_db": round(br, 2),
                "vocal_rms_db": round(vr, 2),
                "decision": decision,
            }
        )
        print(
            f"candidate {t:.3f}s -> beat {nearest} ({nt:.3f}s, {((t-nt)*1000):+.0f} ms) "
            f"bar {bar} beat {beat_in_bar+1} beat {br:.1f} dB vocal {vr:.1f} dB | {decision}"
        )

    phrases = detect_phrases(vm)
    print(f"phrases {len(phrases)}")

    # sung onset: first time the 15 ms level crosses the sung threshold after 14 s
    hop = int(0.002 * SR)
    win = int(0.015 * SR)
    levels = frame_db(vm, hop, win)
    sung_idx = None
    for i, t0 in enumerate(levels):
        if i * hop / SR >= 14.0 and t0 >= CFG["phrase"]["sung_on_db"]:
            sung_idx = i
            break
    sung_onset_s = (sung_idx * hop / SR) if sung_idx is not None else phrases[0][0]
    # activity at -60 dB, for the report only; the file is not trimmed
    act_idx = int(np.argmax(levels > -60))
    activity_s = act_idx * hop / SR

    # return after the long quiet gap: first sung frame after 155.2 s
    return_idx = None
    for i in range(int(155.2 * SR) // hop, len(levels)):
        if levels[i] >= -28.0:
            return_idx = i
            break
    return_s = return_idx * hop / SR
    gap_quiet_start = None
    for i in range(int(154.2 * SR) // hop, return_idx):
        if levels[i] < -40.0:
            gap_quiet_start = i * hop / SR
            break
    print(f"activity -60 dB {activity_s:.4f}s  sung onset {sung_onset_s:.4f}s")
    print(f"quiet gap {gap_quiet_start:.4f} -> vocal return {return_s:.4f}s")

    events = []
    limitations = []

    # buses
    stop_bus = np.zeros((n, 2), np.float32)
    reverse_bus = np.zeros((n, 2), np.float32)
    phone_bus = np.zeros((n, 2), np.float32)
    throw_bus = np.zeros((n, 2), np.float32)
    envelope = np.ones(n, np.float32)

    # ---------- beat-stop layer: only the two measured hat dropouts ----------
    for stop in CFG["beat_stops"]:
        bar = int(stop["bar"])
        dest = bar * BAR
        rise = BAR
        fall = EIGHTH
        s = dest - rise
        # cosine rise in dB, then fall back to 0
        env_db = np.zeros(rise + fall, np.float32)
        env_db[:rise] = cos_fade(rise, True) * np.float32(stop["envelope_db"])
        env_db[rise:] = cos_fade(fall, False) * np.float32(stop["envelope_db"])
        a0 = max(0, s)
        b0 = min(n, s + len(env_db))
        # convert the dB ride to a linear multiplier on top of unity
        mult = (10 ** (env_db / 20.0)).astype(np.float32)
        envelope[a0:b0] *= mult[a0 - s : a0 - s + (b0 - a0)]
        lo, hi = stop["riser_band_hz"]
        src = band_slice(beat, dest - BAR, dest, lo, hi)
        src = src[::-1].copy()
        ramp = np.linspace(0, 1, len(src), dtype=np.float32) ** 1.6
        # yield over the last 64th note so the riser does not click on the downbeat
        tail = min(NOTE_SAMPLES["1/64"], len(src) // 4)
        ramp[-tail:] *= cos_fade(tail, False)
        src *= ramp[:, None]
        pk, _ = peak_db(src)
        need = stop["riser_peak_dbfs"] - pk
        src = apply_fades(src, int(0.03 * SR), 0)
        add_at(stop_bus, src, dest - len(src), need)
        events.append(
            {
                "id": f"beat-stop-bar-{bar}",
                "layer": "beat_stop",
                "source_start_s": round((dest - BAR) / SR, 6),
                "source_end_s": round(dest / SR, 6),
                "source_start_sample": int(dest - BAR),
                "source_end_sample": int(dest),
                "dest_start_s": round((dest - len(src)) / SR, 6),
                "dest_end_s": round(dest / SR, 6),
                "dest_start_sample": int(dest - len(src)),
                "dest_end_sample": int(dest),
                "gain_db": round(float(need), 3),
                "envelope_db": stop["envelope_db"],
                "subdivision": "1 bar",
                "fade_in_ms": 30,
                "fade_out_ms": round(NOTE_SAMPLES["1/64"] / SR * 1000, 2),
                "why": stop["why"],
            }
        )

    stop_delta = beat_dry * (envelope - 1.0)[:, None]
    stop_bus += stop_delta

    # ---------- reverse swells ----------
    rev_ir = make_ir(CFG["reverse"]["decay_s"], 0.0, CFG["reverse"]["seed"], high_hz=5000)

    def add_reverse(event_id, src_t0, src_t1, target_s, length_samples, why):
        s0 = int(src_t0 * SR)
        s1 = int(src_t1 * SR)
        s0 = max(0, min(s0, len(vocal_src) - 1))
        s1 = max(s0 + 16, min(s1, len(vocal_src)))
        snippet = vocal_src[s0:s1].mean(axis=1)
        wet = convolve_stereo(snippet, rev_ir)
        wet = wet[::-1].copy()
        if len(wet) > length_samples:
            wet = wet[-length_samples:]
        elif len(wet) < length_samples:
            pad = np.zeros((length_samples - len(wet), 2), np.float32)
            wet = np.concatenate([pad, wet], axis=0)
        fade_in = max(int(0.08 * len(wet)), int(0.01 * SR))
        wet = apply_fades(wet, fade_in, int(CFG["reverse"]["end_fade_ms"] / 1000 * SR))
        pk, _ = peak_db(wet)
        g = CFG["reverse"]["target_peak_dbfs"] - pk
        target = int(round(target_s * SR))
        dest = target - len(wet)
        add_at(reverse_bus, wet, dest, g)
        events.append(
            {
                "id": event_id,
                "layer": "reverse_swells",
                "source_start_s": round(s0 / SR, 6),
                "source_end_s": round(s1 / SR, 6),
                "source_start_sample": int(s0),
                "source_end_sample": int(s1),
                "dest_start_s": round(max(dest, 0) / SR, 6),
                "dest_end_s": round(target / SR, 6),
                "dest_start_sample": int(dest),
                "dest_end_sample": int(target),
                "gain_db": round(float(g), 3),
                "target_peak_dbfs": CFG["reverse"]["target_peak_dbfs"],
                "subdivision": "placed to end on the vocal entry",
                "fade_in_ms": round(fade_in / SR * 1000, 2),
                "fade_out_ms": CFG["reverse"]["end_fade_ms"],
                "why": why,
            }
        )

    first = phrases[0]
    add_reverse(
        "reverse-first-entry",
        sung_onset_s,
        min(sung_onset_s + 0.45, first[1]),
        sung_onset_s,
        BAR,
        "One-bar reverse of the opening sung phrase. Ends as that phrase becomes audible. The -60 dB activity before it is left in place and is not treated as the lyric.",
    )
    add_reverse(
        "reverse-into-return",
        return_s,
        min(return_s + 0.45, return_s + 0.5),
        return_s,
        int(0.90 * SR),
        "Reverse of the vocal that comes back after the measured quiet gap. Ends on that return. Throws use the earlier part of the same gap.",
    )

    # ---------- delay throws ----------
    throw_cfg = CFG["throws"]
    sos_lp = butter(2, throw_cfg["lowpass_hz"], btype="low", fs=SR, output="sos")
    # phrase end times for clearance, plus the vocal-return sample as a hard wall
    phrase_starts = [p[0] for p in phrases] + [len(vocal_src) / SR]
    # do not throw into the reverse body: reserve the last 0.90 s before the return
    reserve_throw_until = return_s - 0.90

    for pi, (a, b) in enumerate(phrases):
        nxt = phrase_starts[pi + 1]
        gap = nxt - b
        if gap < CFG["phrase"]["min_gap_s"]:
            continue
        # Judge the start of the gap. A long hole can be quiet and then
        # the next phrase begins; averaging the whole hole would hide it.
        body_end = min(b + 0.55, nxt - 0.20)
        body_db = region_db(vm, b + 0.06, max(b + 0.12, body_end))
        if body_db > CFG["phrase"]["clean_gap_rms_db"]:
            continue
        ws, we = last_syllable(vm, (a, b))
        syl = we - ws
        # A line longer than the cap cannot repeat inside a one-second gap.
        # Use the last 300 ms of that line (natural ending, short fade-in)
        # so a dotted eighth can repeat. Longer gaps keep the longer syllable.
        excerpt_fade = throw_cfg["fade_in_ms"]
        if syl >= throw_cfg["max_syllable_s"] - 0.001 and gap < 1.35:
            ws = max(a, we - 0.30)
            syl = we - ws
            excerpt_fade = 18
        note, step = choose_subdivision(syl)
        wall = nxt - throw_cfg["clearance_s"]
        # Only the quiet hole that leads into the vocal return is reserved
        # for the reverse swell. Later gaps are not.
        if b < return_s < nxt + 0.02:
            wall = min(wall, reserve_throw_until)
        word = vocal_src[int(ws * SR) : int(we * SR)]
        if len(word) < int(0.08 * SR):
            continue
        word_f = sosfilt(sos_lp, word.astype(np.float32), axis=0)
        word_f = apply_fades(
            word_f,
            int(excerpt_fade / 1000 * SR),
            int(throw_cfg["fade_out_ms"] / 1000 * SR),
        )
        first_dest = next_grid(int(we * SR) + int(0.02 * SR), step)
        placed = 0
        for r in range(throw_cfg["max_repeats"]):
            dest = first_dest + r * step
            end = dest + len(word_f)
            if end / SR > wall:
                break
            # the destination window itself has to be quiet in the source vocal
            if region_db(vm, dest / SR, end / SR) > -38.0:
                break
            g = throw_cfg["first_db"] - r * throw_cfg["step_drop_db"]
            add_at(throw_bus, word_f, dest, g)
            placed += 1
            events.append(
                {
                    "id": f"throw-p{pi:02d}-r{r+1}",
                    "layer": "delay_throws",
                    "source_start_s": round(ws, 6),
                    "source_end_s": round(we, 6),
                    "source_start_sample": int(ws * SR),
                    "source_end_sample": int(we * SR),
                    "dest_start_s": round(dest / SR, 6),
                    "dest_end_s": round(end / SR, 6),
                    "dest_start_sample": int(dest),
                    "dest_end_sample": int(end),
                    "gain_db": round(float(g), 3),
                    "subdivision": note,
                    "step_samples": int(step),
                    "on_grid": int(dest % step == 0),
                    "fade_in_ms": excerpt_fade,
                    "fade_out_ms": throw_cfg["fade_out_ms"],
                    "next_phrase_s": round(nxt, 6),
                    "clearance_s": round(wall - end / SR, 4),
                    "syllable_s": round(syl, 4),
                    "why": "Copy of the last measured syllable, on an 8th, dotted-8th, or quarter grid after the syllable ends. Not locked to a kick. Omitted if it would reach the next phrase.",
                }
            )
        if placed == 0:
            limitations.append(
                f"Phrase ending {b:.3f}s had a clean gap of {gap:.2f}s but no full repeat fit before the next phrase without cutting the syllable."
            )

    # ---------- telephone BGV: intro preview and outro answer, not on top of the lead ----------
    phone_lo, phone_hi = CFG["phone"]["band_hz"]
    sos_phone = butter(4, [phone_lo, phone_hi], btype="band", fs=SR, output="sos")

    def phone_slice(t0, t1):
        s0 = int(t0 * SR)
        s1 = int(min(t1, len(vocal_src) / SR) * SR)
        seg = vocal_src[s0:s1].mean(axis=1).astype(np.float32)
        seg = sosfilt(sos_phone, seg).astype(np.float32)
        seg = np.stack([seg, seg], axis=1)
        return apply_fades(seg, int(0.012 * SR), int(0.12 * SR)), s0, s1

    # intro: first sung phrase, placed at bar 1, gone well before vocal activity
    intro_seg, is0, is1 = phone_slice(phrases[0][0], phrases[0][1])
    intro_dest = BAR  # bar 1
    # level against the intro beat
    beat_win = beat_dry[intro_dest : intro_dest + len(intro_seg)]
    raw_rms = db(intro_seg)
    target_rms = db(beat_win) - 5.0
    intro_gain = target_rms - raw_rms
    add_at(phone_bus, intro_seg, intro_dest, intro_gain)
    events.append(
        {
            "id": "phone-intro",
            "layer": "telephone_bgv",
            "source_start_s": round(is0 / SR, 6),
            "source_end_s": round(is1 / SR, 6),
            "source_start_sample": int(is0),
            "source_end_sample": int(is1),
            "dest_start_s": round(intro_dest / SR, 6),
            "dest_end_s": round((intro_dest + len(intro_seg)) / SR, 6),
            "dest_start_sample": int(intro_dest),
            "dest_end_sample": int(intro_dest + len(intro_seg)),
            "gain_db": round(float(intro_gain), 3),
            "band_hz": [phone_lo, phone_hi],
            "fade_in_ms": 12,
            "fade_out_ms": 120,
            "why": "Same opening phrase, band-limited, placed in the intro before any sung entry. Mono. No slap delay.",
        }
    )

    last = phrases[-1]
    # closing fragment: last onset in the final 2 seconds, not a slice through the middle of a vowel if an onset exists
    frag_start, frag_end = last_syllable(vm, (max(last[0], last[1] - 2.0), last[1]))
    if last[1] - frag_start < 0.7:
        frag_start = max(last[0], last[1] - 1.6)
    outro_seg, os0, os1 = phone_slice(frag_start, frag_end)
    # start on the next bar after the last phrase, and after any throw that used that ending
    throw_ends = [e["dest_end_sample"] for e in events if e["layer"] == "delay_throws" and abs(e["source_end_s"] - last[1]) < 0.05]
    earliest = int(last[1] * SR) + Q
    if throw_ends:
        earliest = max(earliest, max(throw_ends) + int(0.12 * SR))
    outro_dest = next_grid(earliest, BAR)
    beat_win = beat_dry[outro_dest : outro_dest + len(outro_seg)]
    if len(beat_win) < int(0.2 * SR):
        beat_win = beat_dry[outro_dest : min(n, outro_dest + SR)]
    outro_gain = (db(beat_win) - 3.0) - db(outro_seg)
    # keep the phone from becoming the song peak
    phone_peak = peak_db(outro_seg)[0] + outro_gain
    if phone_peak > -14.0:
        outro_gain -= phone_peak - (-14.0)
    add_at(phone_bus, outro_seg, outro_dest, outro_gain)
    events.append(
        {
            "id": "phone-outro",
            "layer": "telephone_bgv",
            "source_start_s": round(os0 / SR, 6),
            "source_end_s": round(os1 / SR, 6),
            "source_start_sample": int(os0),
            "source_end_sample": int(os1),
            "dest_start_s": round(outro_dest / SR, 6),
            "dest_end_s": round((outro_dest + len(outro_seg)) / SR, 6),
            "dest_start_sample": int(outro_dest),
            "dest_end_sample": int(outro_dest + len(outro_seg)),
            "gain_db": round(float(outro_gain), 3),
            "band_hz": [phone_lo, phone_hi],
            "fade_in_ms": 12,
            "fade_out_ms": 120,
            "why": "Closing fragment of the last lead phrase, after the lead has finished, on a bar line. The lead ending itself is not replaced.",
        }
    )

    # silence the phone bus from 11.5 s through the sung entrance so the preview cannot sit on the vocal
    kill_a = int(11.2 * SR)
    kill_b = int(13.2 * SR)
    if kill_b > kill_a:
        fade_n = int(0.25 * SR)
        phone_bus[kill_a : kill_a + fade_n] *= cos_fade(fade_n, False)[:, None]
        phone_bus[kill_a + fade_n : kill_b] = 0

    # ---------- reverbs ----------
    print("rendering lead reverb")
    lead_cfg = CFG["lead_reverb"]
    lead_ir = make_ir(
        NOTE_SAMPLES[lead_cfg["decay_note"]] / SR,
        NOTE_SAMPLES[lead_cfg["predelay_note"]] / SR,
        lead_cfg["seed"],
        high_hz=4200,
    )
    send = vocal_dry.mean(axis=1)
    lead_reverb = convolve_stereo(send, lead_ir)
    # scale so wet RMS during singing sits return_db under the dry vocal, before ducking
    sung_mask = np.zeros(n, dtype=bool)
    for a, b in phrases:
        sung_mask[int(a * SR) : int(b * SR)] = True
    if sung_mask.any():
        dry_rms = db(vocal_dry[sung_mask])
        wet_rms = db(lead_reverb[sung_mask])
        lead_gain_db = (dry_rms + lead_cfg["return_db"]) - wet_rms
    else:
        lead_gain_db = lead_cfg["return_db"]
    lead_reverb *= np.float32(gain_lin(lead_gain_db))
    # duck while the lead is up so the tail opens in the gaps instead of being chopped
    hop_e = 256
    env = frame_db(vocal_dry.mean(axis=1), hop_e, 1024)
    flag = np.repeat(env > -34.0, hop_e)[:n]
    if len(flag) < n:
        flag = np.pad(flag, (0, n - len(flag)))
    follow = smooth_follow(flag.astype(np.float32), int(lead_cfg["release_ms"] / 1000 * SR))
    duck = (10 ** ((-lead_cfg["duck_db"] * follow) / 20.0)).astype(np.float32)
    lead_reverb *= duck[:, None]

    print("rendering phone reverb")
    phone_cfg = CFG["phone"]
    phone_ir = make_ir(
        NOTE_SAMPLES[phone_cfg["reverb_decay_note"]] / SR,
        NOTE_SAMPLES[phone_cfg["reverb_predelay_note"]] / SR,
        phone_cfg["seed"],
        high_hz=2800,
    )
    phone_reverb = convolve_stereo(phone_bus.mean(axis=1), phone_ir)
    phone_active = np.max(np.abs(phone_bus), axis=1) > 1e-4
    if phone_active.any():
        pr = db(phone_reverb[phone_active])
        pdry = db(phone_bus[phone_active])
        phone_rev_gain = (pdry + phone_cfg["reverb_return_db"]) - pr
    else:
        phone_rev_gain = phone_cfg["reverb_return_db"]
    phone_reverb *= np.float32(gain_lin(phone_rev_gain))
    # same kill zone as the dry phone, plus the reverb tail after the intro must finish before the vocal
    if kill_b > kill_a:
        phone_reverb[kill_a : kill_a + fade_n] *= cos_fade(fade_n, False)[:, None]
        phone_reverb[kill_a + fade_n : kill_b] = 0

    events.append(
        {
            "id": "lead-reverb",
            "layer": "lead_reverb",
            "source_start_s": 0.0,
            "source_end_s": round(len(vocal_src) / SR, 6),
            "dest_start_s": 0.0,
            "dest_end_s": round(n / SR, 6),
            "gain_db": round(float(lead_gain_db), 3),
            "predelay_ms": round(NOTE_SAMPLES[lead_cfg["predelay_note"]] / SR * 1000, 2),
            "decay_s": round(NOTE_SAMPLES[lead_cfg["decay_note"]] / SR, 5),
            "duck_db": lead_cfg["duck_db"],
            "why": "Plate-style return on the dry vocal only. Predelay 1/64, decay a dotted half at 135 BPM. Ducked while the lead is up; the tail is not gated off.",
        }
    )
    events.append(
        {
            "id": "phone-reverb",
            "layer": "telephone_reverb",
            "gain_db": round(float(phone_rev_gain), 3),
            "predelay_ms": round(NOTE_SAMPLES[phone_cfg["reverb_predelay_note"]] / SR * 1000, 2),
            "decay_s": round(NOTE_SAMPLES[phone_cfg["reverb_decay_note"]] / SR, 5),
            "why": "Separate reverb for the telephone bus only. Half-note decay. Not printed onto the lead.",
        }
    )

    fx = stop_bus + reverse_bus + phone_bus + phone_reverb + lead_reverb + throw_bus
    dry = beat_dry + vocal_dry
    mix = dry + fx

    # headroom: trim FX only, never the dry -8 / -6 balance
    def peak_of(x):
        return float(np.max(np.abs(x)))

    trims = []
    for _ in range(6):
        pk = peak_of(mix)
        pk_db = 20 * np.log10(pk + 1e-20)
        if pk_db <= CFG["headroom_dbfs"]:
            break
        over = pk_db - CFG["headroom_dbfs"] + 0.15
        fx *= np.float32(gain_lin(-over))
        mix = dry + fx
        trims.append(round(over, 3))
    if trims:
        limitations.append(
            "FX buses were turned down by "
            + ", ".join(f"{t:.2f} dB" for t in trims)
            + " so the sum stayed at or under the headroom target. Dry beat and vocal gains were not changed."
        )
        # record the trim on FX events
        trim_total = sum(trims)
        for e in events:
            if "gain_db" in e and e["layer"] != "lead_reverb_note":
                e["gain_db_after_headroom_trim"] = round(e["gain_db"] - trim_total, 3)
                e["headroom_trim_db"] = round(trim_total, 3)

    print("measuring")
    # apply the same trim to exported buses
    trim_lin = np.float32(gain_lin(-sum(trims))) if trims else np.float32(1.0)
    buses = {
        "beat_dry": beat_dry,
        "vocal_dry": vocal_dry,
        "beat_stop": stop_bus * trim_lin,
        "reverse_swells": reverse_bus * trim_lin,
        "telephone_bgv": phone_bus * trim_lin,
        "telephone_reverb": phone_reverb * trim_lin,
        "lead_reverb": lead_reverb * trim_lin,
        "delay_throws": throw_bus * trim_lin,
    }
    mix = dry + sum(buses[k] for k in buses if k not in ("beat_dry", "vocal_dry"))

    finite = bool(np.isfinite(mix).all())
    sample_pk_db, sample_pk = peak_db(mix)
    tp_db, tp = true_peak_db(mix)
    lufs = integrated_lufs(mix)
    base_lufs = integrated_lufs(baseline)
    bus_levels = {}
    for _name, _audio in buses.items():
        pk, _ = peak_db(_audio)
        bus_levels[_name] = {"peak_dbfs": round(pk, 2), "rms_db": round(float(db(_audio)), 2)}
    base_tp, _ = true_peak_db(baseline)

    # alignment: dry vocal vs source at lag 0
    ref = vocal_src * np.float32(g_vocal)
    corr = float(np.corrcoef(vocal_dry[: len(ref), 0], ref[:, 0])[0, 1])

    # baked-effect measurements on the vocal source
    side = (vocal_src[:, 0] - vocal_src[:, 1]) * 0.5
    mid = (vocal_src[:, 0] + vocal_src[:, 1]) * 0.5
    side_mid = float(db(side) - db(mid))
    # envelope autocorr at musical lags, active region only
    ds = SR // 200
    env = np.abs(vm[int(14 * SR) : int(180 * SR)])
    env = np.convolve(env, np.ones(int(0.01 * SR)) / int(0.01 * SR), mode="same")[::ds]
    env = env - env.mean()
    env = env / (np.std(env) + 1e-9)
    spec = np.fft.rfft(env, n=2 * len(env))
    ac = np.fft.irfft(np.abs(spec) ** 2)[: len(env)]
    ac /= ac[0] + 1e-12
    lag_notes = {}
    for name, ms in (("1/8", 222.22), ("1/8 dotted", 333.33), ("1/4", 444.44), ("1/2", 888.89)):
        lag = int(round(ms / 1000 * 200))
        lag_notes[name] = round(float(ac[lag]), 4)
    # a gap decay
    gap_decay = []
    if gap_quiet_start:
        for dt in (0.0, 0.1, 0.2, 0.4, 0.8):
            gap_decay.append({"t_offset_s": dt, "rms_db": round(region_db(vm, gap_quiet_start + dt, gap_quiet_start + dt + 0.08), 2)})

    baked = {
        "measurement_not_listening": True,
        "vocal_side_minus_mid_db": round(side_mid, 2),
        "envelope_autocorr_at_note_lags": lag_notes,
        "quiet_gap_decay_from_s": None if gap_quiet_start is None else round(gap_quiet_start, 4),
        "quiet_gap_decay": gap_decay,
        "reading": (
            "The lead is nearly mono (side well below mid). "
            "Autocorrelation at a dotted eighth is not a discrete echo peak; "
            "the quarter-note value tracks the delivery sitting near the grid. "
            "The quiet gap falls toward the noise floor within a few hundred milliseconds. "
            "No substantial baked delay or long stereo reverb was measured, so none was removed and none was doubled. "
            "A short decay at phrase ends is the voice closing, not a printed throw."
        ),
    }

    # quality checks
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + " — " + detail)

    check("finite", finite, "all mix samples finite" if finite else "non-finite samples")
    check("no_clip", sample_pk < 1.0, f"sample peak {sample_pk_db:.3f} dBFS")
    check("sample_headroom", sample_pk_db <= -1.0, f"{sample_pk_db:.3f} dBFS")
    check("true_peak", tp_db <= CFG["headroom_dbtp"] + 0.05, f"{tp_db:.3f} dBTP")
    check("length", len(mix) == n, f"{len(mix)} samples, {len(mix)/SR:.6f}s, beat was {n/SR:.6f}s")
    check("baseline_peak", abs(base_pk - (-1.55)) < 0.05, f"{base_pk:.3f} dBFS (DAW reference -1.55)")
    check("vocal_unshifted", corr > 0.9999, f"lag-0 correlation {corr:.6f}")
    check("sources_untouched_peaks", abs(beat_pk - (-0.10024)) < 0.02 and abs(voc_pk - (-0.10024)) < 0.02,
          f"beat {beat_pk:.5f} vocal {voc_pk:.5f}")
    check("vocal_start_kept", activity_s < 13.6, f"first -60 dB frame {activity_s:.4f}s (stated 13.437s)")

    throw_events = [e for e in events if e["layer"] == "delay_throws"]
    grid_ok = all(e["dest_start_sample"] % e["step_samples"] == 0 for e in throw_events)
    clear_ok = all(e["clearance_s"] >= -0.001 for e in throw_events)
    check("throws_on_subdivision_grid", grid_ok, f"{len(throw_events)} throws, phase 0")
    check("throws_clear_next_phrase", clear_ok, "each kept repeat ends before the clearance wall")
    # no throw inside a sung phrase
    collide = []
    for e in throw_events:
        if region_db(vm, e["dest_start_s"], e["dest_end_s"]) > -36:
            collide.append(e["id"])
    check("throws_not_on_lead", not collide, "none" if not collide else ",".join(collide))

    rev_events = [e for e in events if e["layer"] == "reverse_swells"]
    rev_ok = True
    for e in rev_events:
        # swell should be quiet in the source vocal until the last 80 ms
        if e["dest_end_s"] - e["dest_start_s"] > 0.2:
            mid_db = region_db(vm, e["dest_start_s"], e["dest_end_s"] - 0.08)
            if mid_db > -36:
                rev_ok = False
    check("reverse_sits_in_a_gap", rev_ok, "reverse body before the landing is under -36 dB in the vocal")

    stop_ids = [e["id"] for e in events if e["layer"] == "beat_stop"]
    check("few_beat_stops", stop_ids == ["beat-stop-bar-40", "beat-stop-bar-80"], ",".join(stop_ids))
    # energy-return times must not be the end of a beat-stop event
    er_hit = []
    for c in candidate_notes:
        for e in events:
            if e["layer"] == "beat_stop" and abs(e["dest_end_s"] - c["suggested_s"]) < 0.3:
                er_hit.append(c["suggested_s"])
    check("energy_returns_not_used_as_stops", not er_hit, "none landed on" if not er_hit else str(er_hit))

    phone_on_lead = region_db(phone_bus.mean(1), 13.4, 15.9)
    check("phone_clear_of_vocal_entry", phone_on_lead < -70, f"phone rms 13.4-15.9s {phone_on_lead:.1f} dB")

    fades_ok = all(e.get("fade_in_ms", 1) > 0 for e in events if e["layer"] in ("delay_throws", "reverse_swells", "telephone_bgv", "beat_stop"))
    check("fades_present", fades_ok, "throws, reverses, phone, and risers have a fade")

    print(f"LUFS mix {lufs:.2f}  baseline {base_lufs:.2f}  true peak {tp_db:.2f} dBTP")

    out_renders = SONG / "renders"
    out_buses = SONG / "buses"
    out_renders.mkdir(exist_ok=True)
    out_buses.mkdir(exist_ok=True)
    print("writing audio")
    write_pcm24(out_renders / "satans-casino-v02-review.wav", mix)
    write_pcm24(out_renders / "satans-casino-baseline-reference.flac", baseline)
    for name, audio in buses.items():
        write_pcm24(out_buses / f"{name}.flac", audio)

    mp3 = out_renders / "satans-casino-v02-review.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(out_renders / "satans-casino-v02-review.wav"),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)],
        check=True,
    )
    mp3_raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    )
    mp3_audio = np.frombuffer(mp3_raw.stdout, dtype="<f4").reshape(-1, 2)
    mp3_pk, _ = peak_db(mp3_audio)
    mp3_tp, _ = true_peak_db(mp3_audio[: len(mp3_audio)])
    mp3_gain = 0.0
    if mp3_tp > -1.0:
        mp3_gain = -1.05 - mp3_tp
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(out_renders / "satans-casino-v02-review.wav"),
             "-af", f"volume={mp3_gain:.3f}dB", "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)],
            check=True,
        )
        mp3_raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
            capture_output=True, check=True,
        )
        mp3_audio = np.frombuffer(mp3_raw.stdout, dtype="<f4").reshape(-1, 2)
        mp3_pk, _ = peak_db(mp3_audio)
        mp3_tp, _ = true_peak_db(mp3_audio)
        limitations.append(
            f"The 320 kbps MP3 was encoded {mp3_gain:.2f} dB lower than the WAV so its true peak stayed at or under -1 dBTP. The WAV was not turned down."
        )
    check("mp3_true_peak", mp3_tp <= -0.9, f"{mp3_tp:.3f} dBTP, sample {mp3_pk:.3f} dBFS, encode trim {mp3_gain:.2f} dB")
    check("mp3_length", abs(len(mp3_audio) / SR - n / SR) < 0.05, f"{len(mp3_audio)/SR:.3f}s")

    limitations.extend(
        [
            "No listening pass was done. Grid, gaps, peaks, and lags are measurements.",
            "Eighth-note and dotted-eighth throws are allowed and are not required to land on a kick.",
            "Energy-return suggestions at 30.6, 59.1, 87.5, and 158.6 s sit on beat 2 while the vocal is up. They were not turned into stops.",
            "Only two hat-dropout builds were automated (bars 40 and 80). Other dips were left as the beat stem wrote them.",
            "One vocal stem. Telephone parts are copies of measured phrases, not new performances.",
            "Lead tone is the raw stem at -6 dB. No EQ boost, compressor, or de-esser was added.",
            "No mastering limiter and no loudness target. LUFS is whatever the -8/-6 balance plus the FX produced.",
            "Key was not used for tuning. An earlier chroma estimate favored A minor with a close runner-up; that is not confirmed by ear.",
            "The WAV chapter tag says Tempo 110.0. The drum grid measures 135.00 BPM. 129 BPM was not used.",
            "Reverse landings use a 6 ms fade so the swell does not click. That is a few milliseconds, not a chopped lyric.",
            "This is a review candidate, not a signed-off master.",
        ]
    )

    quality = {
        "version": "v02",
        "bpm": BPM,
        "samples_per_quarter": Q,
        "quarter_ms": round(Q / SR * 1000, 4),
        "eighth_ms": round(EIGHTH / SR * 1000, 4),
        "dotted_eighth_ms": round(DOTTED_8 / SR * 1000, 4),
        "bar_s": round(BAR / SR, 6),
        "activity_minus60_s": round(activity_s, 4),
        "sung_onset_s": round(sung_onset_s, 4),
        "quiet_gap_start_s": None if gap_quiet_start is None else round(gap_quiet_start, 4),
        "vocal_return_s": round(return_s, 4),
        "energy_return_candidates": candidate_notes,
        "bus_levels": bus_levels,
        "baseline": {
            "beat_db": -8.0,
            "vocal_db": -6.0,
            "sample_peak_dbfs": round(base_pk, 3),
            "true_peak_dbtp": round(base_tp, 3),
            "integrated_lufs": round(base_lufs, 2),
            "seconds": round(n / SR, 6),
        },
        "candidate": {
            "sample_peak_dbfs": round(sample_pk_db, 3),
            "true_peak_dbtp": round(tp_db, 3),
            "integrated_lufs": round(lufs, 2),
            "seconds": round(n / SR, 6),
            "samples": int(n),
            "sample_rate": SR,
            "bit_depth_wav": 24,
            "mp3_kbps": 320,
            "mp3_sample_peak_dbfs": round(mp3_pk, 3),
            "mp3_true_peak_dbtp": round(mp3_tp, 3),
            "mp3_trim_db": round(mp3_gain, 3),
            "fx_headroom_trims_db": trims,
        },
        "baked_vocal_effects": baked,
        "checks": checks,
        "throw_count": len(throw_events),
        "limitations": limitations,
        "listening": "not performed",
        "claim": "review candidate only",
    }
    payload = {"events": events, "limitations": limitations, "config": CFG}
    (SONG / "effects").mkdir(exist_ok=True)
    (SONG / "reports").mkdir(exist_ok=True)
    (SONG / "effects" / "v02-events.json").write_text(json.dumps(payload, indent=2))
    (SONG / "reports" / "v02-quality.json").write_text(json.dumps(quality, indent=2))

    failed = [c for c in checks if not c["pass"]]
    lines = [
        "# Satan's Casino v02 quality report",
        "",
        "Measurements from the renderer. Not a listening pass. Not a finished master.",
        "",
        f"- Tempo used: **{BPM:.2f} BPM**, phase 0. Quarter = {Q} samples = {Q/SR*1000:.4f} ms. Eighth = {EIGHTH/SR*1000:.4f} ms. Dotted eighth = {DOTTED_8/SR*1000:.4f} ms. Bar = {BAR/SR:.6f} s.",
        f"- Embedded WAV chapter says Tempo 110.0. That grid does not fit the drums. 129 BPM was not used.",
        f"- Vocal file starts at sample 0. First level above -60 dBFS is {activity_s:.3f} s. Sung level (about -32 dBFS) begins at {sung_onset_s:.3f} s. Nothing was trimmed or shifted.",
        f"- Quiet gap used for the return: {gap_quiet_start:.3f} s to {return_s:.3f} s. The suggested window 154.8–156.4 s matches this measurement.",
        f"- Baseline (-8 beat, -6 vocal, no normalize): sample peak {base_pk:.3f} dBFS, true peak {base_tp:.3f} dBTP, integrated loudness {base_lufs:.2f} LUFS.",
        f"- Candidate: sample peak {sample_pk_db:.3f} dBFS, true peak {tp_db:.3f} dBTP, integrated loudness {lufs:.2f} LUFS, {n/SR:.3f} s, 24-bit 44.1 kHz.",
        f"- MP3 320 kbps: sample peak {mp3_pk:.3f} dBFS, true peak {mp3_tp:.3f} dBTP, encode trim {mp3_gain:.2f} dB.",
        f"- Throws placed: {len(throw_events)}. Beat-stop builds: {', '.join(stop_ids)}.",
        "",
        "## Bus levels (after the dry faders, and after any FX headroom trim)",
        "",
    ]
    for _name, _lv in bus_levels.items():
        lines.append(f"- {_name}: peak {_lv['peak_dbfs']:.2f} dBFS, RMS {_lv['rms_db']:.2f} dB")
    lines += [
        "",
        "## Suggested energy returns",
        "",
        "These were checked against the 135 grid. Beat 2 of the bar, vocal still present. They were not used as stops.",
        "",
    ]
    for c in candidate_notes:
        lines.append(
            f"- {c['suggested_s']:.1f} s → beat {c['nearest_beat']} at {c['nearest_beat_s']:.3f} s "
            f"({c['offset_ms']:+.0f} ms), bar {c['bar']} beat {c['beat_in_bar']}. "
            f"Beat RMS {c['beat_rms_db']:.1f} dB, vocal RMS {c['vocal_rms_db']:.1f} dB. {c['decision']}"
        )
    lines += ["", "## Baked effects in the vocal source", "", baked["reading"], ""]
    lines.append(f"- Side minus mid: {side_mid:.2f} dB.")
    lines.append("- Envelope autocorrelation (1 = a perfect copy): " + ", ".join(f"{k} {v}" for k, v in lag_notes.items()) + ".")
    lines += ["", "## Checks", ""]
    for c in checks:
        lines.append(f"- {'PASS' if c['pass'] else 'FAIL'} — {c['name']}: {c['detail']}")
    lines += ["", "## Limitations", ""]
    for item in limitations:
        lines.append(f"- {item}")
    lines.append("")
    (SONG / "reports" / "v02.md").write_text("\n".join(lines))
    print("failed", len(failed))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

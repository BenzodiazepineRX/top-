#!/usr/bin/env python3
"""Groove-locked echo: every repeat lands on the beat's real drum hits.

A tempo-synced delay repeats a word exactly N beats after it was sung. That is only "on the beat" if the word
was exactly on the beat and the beat is perfectly even. Rappers sit ahead of or behind the drums on purpose, and
many beats swing, so a fixed delay leaves echoes 20-40 ms off the drums. Inside a line nobody hears it; alone in a
gap, the ear does (measured on Pushing the Interstate: echoes up to 36 ms off; half the adlib echoes over 20 ms).

This tool echoes chosen events (a word, a line ending, an adlib phrase). For each event it finds the attack of
the sound, then places repeat k on the drum hit nearest to (attack + k x note) within --snap-ms, so the echo
rides the groove. Without a drum hit in range it falls back to the exact tempo position. Each repeat passes the
loop filter again (darker), alternates left/right with --pingpong, and drops by --feedback.

Usage:
  python3 music/tools/groove_delay.py lead.wav lead_echo.wav --drums beat.wav --bpm 129 --note 1/4 \\
      --events "34.10-34.43,37.86-38.17" --duck-by lead.wav
  python3 music/tools/groove_delay.py adlibs.wav adlib_echo.wav --drums beat.wav --bpm 129 --note 1/8d \\
      --auto-phrases --duck-by lead.wav

Prints, for every repeat, where a fixed delay would have put it and how far it was moved onto the drums.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.signal import butter, find_peaks, sosfilt, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsp_tools as dt  # noqa: E402

NOTES = {"1/1": 4, "1/2": 2, "1/2d": 3, "1/4": 1, "1/4d": 1.5, "1/4t": 2 / 3, "1/8": 0.5, "1/8d": 0.75,
         "1/8t": 1 / 3, "1/16": 0.25, "1/16d": 0.375}


def drum_hits(path):
    """Onset times (s) of kick (<150 Hz), snare/clap (1-5 kHz) and hats (>7 kHz), 1 ms resolution."""
    x, sr = dt.read(path)
    m = dt.mono(x)
    hits = []
    for btype, band, pct, dist in (("low", 150, 97, 150), ("band", [1000, 5000], 98, 120), ("high", 7000, 97, 80)):
        y = sosfiltfilt(butter(4, band, btype, fs=sr, output="sos"), m)
        n = max(1, sr // 1000)
        k = len(y) // n
        e = np.sqrt((y[:k * n] ** 2).reshape(k, n).mean(axis=1))
        fl = np.diff(np.log(e + 1e-5), prepend=0)
        fl[fl < 0] = 0
        pk, _ = find_peaks(fl, height=np.percentile(fl, pct), distance=dist)
        hits.append(pk * n / sr)
    return np.sort(np.concatenate(hits)), sr


def attack(x, sr, t_guess, before=0.03, after=0.10):
    """The word's attack: the sharpest rise in the 300-4000 Hz envelope (log spectral flux, 1 ms) nearest to
    t_guess, searched from t_guess-before to t_guess+after.

    A "first time it gets loud" threshold fails in dense rap, where the previous syllable's tail runs into the
    next word (it moved attacks by up to 46 ms in testing); the flux peak marks the consonant or vowel onset."""
    a, b = max(0, int((t_guess - 0.15) * sr)), min(len(x), int((t_guess + 0.25) * sr))
    seg = dt.mono(x[a:b])
    if len(seg) < 256:
        return t_guess
    y = sosfiltfilt(butter(4, [300, 4000], "band", fs=sr, output="sos"), seg)
    n = max(1, sr // 1000)
    k = len(y) // n
    e = np.sqrt((y[:k * n] ** 2).reshape(k, n).mean(axis=1))
    fl = np.diff(np.log(e + 1e-5), prepend=0)
    fl = np.convolve(np.clip(fl, 0, None), np.ones(5) / 5, "same")
    t = a / sr + np.arange(k) * n / sr
    win = (t >= t_guess - before) & (t <= t_guess + after)
    if not win.any() or fl[win].max() <= 0:
        return t_guess
    pk, _ = find_peaks(fl, height=0.25 * fl[win].max())
    pk = [p for p in pk if win[p]]
    if not pk:
        return float(t[win][np.argmax(fl[win])])
    return float(t[min(pk, key=lambda p: abs(t[p] - t_guess) + (0 if t[p] >= t_guess - 0.01 else 0.02))])


def auto_phrases(x, sr, gap=0.15, t_min=None, t_max=None):
    """Phrases separated by at least `gap` s of quiet (30 dB under the loudest 10 ms block)."""
    m = dt.power_mono(x)
    w = int(0.01 * sr)
    k = len(m) // w
    lv = 20 * np.log10(np.sqrt((m[:k * w] ** 2).reshape(k, w).mean(axis=1)) + 1e-12)
    on = lv > lv.max() - 30
    g = int(gap / 0.01)
    out, i = [], 0
    while i < k:
        if on[i]:
            j = i
            while j < k and (on[j] or on[j:j + g].any()):
                j += 1
            s, e = i * 0.01, min(j, k) * 0.01
            if (t_min is None or s >= t_min) and (t_max is None or e <= t_max):
                out.append((s, e))
            i = j
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--drums", required=True, help="the beat (or drum stem) whose hits the echoes lock to")
    ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--note", default="1/4", choices=sorted(NOTES))
    ap.add_argument("--events", help="comma-separated start-end seconds to echo (whole words or phrases)")
    ap.add_argument("--auto-phrases", action="store_true", help="echo every phrase found in the input")
    ap.add_argument("--range", help="limit --auto-phrases to start-end seconds")
    ap.add_argument("--feedback", type=float, default=0.35)
    ap.add_argument("--taps", type=int, default=6)
    ap.add_argument("--snap-ms", type=float, default=60.0, help="largest move onto a drum hit")
    ap.add_argument("--hp", type=float, default=450.0)
    ap.add_argument("--lp", type=float, default=5000.0)
    ap.add_argument("--return-db", type=float, default=-6.0)
    ap.add_argument("--pingpong", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--duck-by", help="lead vocal: the echo dips lightly while it sings")
    ap.add_argument("--duck-depth", type=float, default=3.0)
    ap.add_argument("--duck-attack", type=float, default=5.0)
    ap.add_argument("--duck-release", type=float, default=120.0)
    a = ap.parse_args()

    x, sr = dt.read(a.input)
    if x.ndim == 1:
        x = x[:, None]
    hits, dsr = drum_hits(a.drums)
    if dsr != sr:
        sys.exit("Input and drums must share a sample rate")
    note_s = 60.0 / a.bpm * NOTES[a.note]
    if a.events:
        events = [tuple(float(v) for v in p.split("-")) for p in a.events.split(",")]
    elif a.auto_phrases:
        lo, hi = (None, None)
        if a.range:
            lo, hi = (float(v) for v in a.range.split("-"))
        events = auto_phrases(x, sr, t_min=lo, t_max=hi)
    else:
        sys.exit("give --events or --auto-phrases")

    sos = butter(2, [a.hp, min(a.lp, sr / 2 * 0.95)], btype="bandpass", fs=sr, output="sos")
    tail = int(note_s * (a.taps + 1) * sr)
    out = np.zeros((len(x) + tail, 2))
    pre, post, fade = 0.015, 0.03, int(0.004 * sr)
    moves = []
    log = []
    for s, e in events:
        t0 = attack(x, sr, s)
        a0, b0 = int((t0 - pre) * sr), int((e + post) * sr)
        seg = dt.mono(x[max(0, a0):b0]).copy()
        if len(seg) < 2 * fade:
            continue
        seg[:fade] *= np.linspace(0, 1, fade)
        seg[-fade:] *= np.linspace(1, 0, fade)
        lead_in = t0 - max(0, a0) / sr
        cur = seg
        ev = {"event": [round(s, 3), round(e, 3)], "attack": round(t0, 4), "repeats": []}
        log.append(ev)
        for k in range(1, a.taps + 1):
            cur = sosfilt(sos, cur)  # each repeat darker and thinner, like a loop filter
            target = t0 + k * note_s
            j = int(np.argmin(np.abs(hits - target))) if len(hits) else None
            land = hits[j] if j is not None and abs(hits[j] - target) <= a.snap_ms / 1000 else target
            moves.append((land - target) * 1000)
            ev["repeats"].append({"fixed": round(target, 4), "lands": round(float(land), 4)})
            p = int(round((land - lead_in) * sr))
            if p < 0 or p >= len(out):
                continue
            q = min(len(out), p + len(cur))
            g = a.feedback ** (k - 1)
            if a.pingpong:
                out[p:q, (k - 1) % 2] += cur[:q - p] * g
            else:
                out[p:q] += (cur[:q - p] * g * np.sqrt(0.5))[:, None]
    if a.duck_by:
        key, ksr = dt.read(a.duck_by)
        if ksr != sr:
            sys.exit("Duck key and input must share a sample rate")
        gk, thr, pct = dt.duck_gain(key, sr, len(out), a.duck_depth, None, a.duck_attack, a.duck_release)
        out *= gk[:, None]
    out *= 10 ** (a.return_db / 20)
    dt.write(a.output, out, sr)
    with open(a.output + ".json", "w") as fh:
        json.dump({"bpm": a.bpm, "note": a.note, "events": log}, fh, indent=1)
    mv = np.array(moves) if moves else np.zeros(1)
    print(f"Groove-locked {a.note} echo at {a.bpm:g} BPM ({note_s * 1000:.2f} ms nominal): {len(events)} events, "
          f"{a.taps} repeats each, feedback {a.feedback:g}, {'ping-pong' if a.pingpong else 'centered'}, "
          f"loop filter {a.hp:g}-{a.lp:g} Hz, return {a.return_db:+g} dB"
          + (f", ducked -{a.duck_depth:g} dB by {a.duck_by}" if a.duck_by else ""))
    print(f"Moved onto the drums: median {np.median(np.abs(mv)):.0f} ms, largest {np.max(np.abs(mv)):.0f} ms; "
          f"{int(np.sum(np.abs(mv) > 20))} of {len(mv)} repeats would have been more than 20 ms off with a fixed delay.")


if __name__ == "__main__":
    main()

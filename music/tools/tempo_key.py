#!/usr/bin/env python3
"""Detect a song's tempo (BPM), key and tuning, and print exact tempo-synced delay times.

Tempo: spectral-flux onset envelope -> autocorrelation -> comb scoring over
16 beats on a 0.05 BPM grid, so the estimate is precise, not just the nearest
whole frame. Half/double-time readings are always listed as alternatives,
because a detector can't know whether the artist counts 70 or 140.

Key: tuning-corrected chroma (pitch-class energy) correlated against the
Krumhansl-Kessler major and minor key profiles. The runner-up is listed; the
relative major/minor (for example E minor vs G major) is the most common
confusion.

Delay times (ms): quarter = 60000/BPM, dotted eighth = 45000/BPM,
half = 120000/BPM, plus whole, eighth, sixteenth, dotted and triplet values,
and short notes useful as reverb pre-delay.

Usage:
  python tempo_key.py SONG                    # detect tempo, key, tuning + delay table
  python tempo_key.py SONG --json facts.json  # also save results
  python tempo_key.py --bpm 92                # delay table only, for a known BPM
  python tempo_key.py SONG --bpm 92           # key detection + table for a known BPM

Needs ffmpeg, numpy and scipy. Detection is an estimate: if the user or the
project file states the BPM or key, that wins.
"""
import argparse
import json
import math
import subprocess
import sys

import numpy as np
from scipy.signal import stft

SR = 22050
NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
# Krumhansl-Kessler probe-tone profiles
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def load_mono(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "a:0", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True)
    if raw.returncode != 0 or not raw.stdout:
        sys.exit(f"Could not decode {path}: {raw.stderr.decode(errors='replace')[:300]}")
    return np.frombuffer(raw.stdout, dtype="<f4").astype(np.float64)


def onset_envelope(x, hop=256, n_fft=2048):
    _, _, Z = stft(x, fs=SR, nperseg=n_fft, noverlap=n_fft - hop, boundary=None, padded=False)
    mag = np.abs(Z)
    freqs = np.fft.rfftfreq(n_fft, 1 / SR)
    edges = np.geomspace(30, 10000, 41)  # 40 log-spaced bands
    bands = np.stack([mag[(freqs >= lo) & (freqs < hi)].sum(axis=0) for lo, hi in zip(edges[:-1], edges[1:])])
    logb = np.log1p(100 * bands / (bands.max() + 1e-12))
    flux = np.maximum(0, np.diff(logb, axis=1)).sum(axis=0)
    fps = SR / hop
    w = int(fps * 0.5)
    local = np.convolve(flux, np.ones(w) / w, mode="same")
    env = np.maximum(0, flux - local)
    return env / (env.std() + 1e-12), fps


def detect_tempo(x):
    env, fps = onset_envelope(x)
    n = len(env)
    if n < fps * 8:
        return None
    f = np.fft.rfft(env - env.mean(), 2 * n)
    ac = np.fft.irfft(np.abs(f) ** 2)[:n]
    ac /= ac[0] + 1e-12
    bpms = np.arange(50.0, 210.0, 0.05)
    beats = 16
    scores = np.zeros_like(bpms)
    for i, b in enumerate(bpms):
        period = 60.0 * fps / b
        lags = period * np.arange(1, beats + 1)
        lags = lags[lags < n - 1]
        scores[i] = np.interp(lags, np.arange(n), ac).mean()
    # mild preference for 80-160 BPM (log-normal prior around 115), only to rank octave candidates
    prior = np.exp(-0.5 * (np.log2(bpms / 115.0) / 1.0) ** 2)
    ranked = scores * (0.6 + 0.4 * prior)
    order = np.argsort(ranked)[::-1]
    picks = []
    for idx in order:
        b = bpms[idx]
        if all(abs(b - p) / p > 0.03 for p, _ in picks):
            picks.append((b, ranked[idx]))
        if len(picks) == 4:
            break
    best = picks[0][0]
    # contrast: how much the best stands out from the median of the grid
    contrast = (ranked.max() - np.median(ranked)) / (np.std(ranked) + 1e-12)
    conf = "high" if contrast > 4 else "medium" if contrast > 2.5 else "low"
    alts = sorted({round(best / 2, 1), round(best * 2, 1)} | {round(p, 1) for p, _ in picks[1:]})
    alts = [a for a in alts if 40 <= a <= 260 and abs(a - best) / best > 0.03]
    return {"bpm": round(float(best), 2), "bpm_rounded": int(round(best)), "confidence": conf,
            "alternatives": alts[:4]}


def detect_key(x):
    n_fft, hop = 8192, 2048
    freqs, _, Z = stft(x, fs=SR, nperseg=n_fft, noverlap=n_fft - hop, boundary=None, padded=False)
    mag = np.abs(Z)
    sel = (freqs >= 55) & (freqs <= 2000)
    f, m = freqs[sel], mag[sel]
    spec = m.mean(axis=1)
    # tuning: magnitude-weighted circular mean of strong peaks' deviation from equal temperament
    pk = np.flatnonzero((spec[1:-1] > spec[:-2]) & (spec[1:-1] > spec[2:]) &
                        (spec[1:-1] > np.percentile(spec, 90))) + 1
    tuning_cents = 0.0
    if len(pk):
        semis = 12 * np.log2(f[pk] / 440.0)
        dev = semis - np.round(semis)
        ang = 2 * np.pi * dev
        tuning_cents = float(np.angle((spec[pk] * np.exp(1j * ang)).sum()) / (2 * np.pi) * 100)
    ref = 440.0 * 2 ** (tuning_cents / 1200)
    pc = (np.round(12 * np.log2(f / ref)).astype(int) + 9) % 12
    chroma = np.zeros(12)
    for k in range(12):
        chroma[k] = m[pc == k].sum()  # linear magnitude: tested more reliable than log or sqrt weighting
    chroma /= chroma.sum() + 1e-12
    results = []
    for tonic in range(12):
        for mode, prof in (("major", MAJOR), ("minor", MINOR)):
            r = np.corrcoef(chroma, np.roll(prof, tonic))[0, 1]
            results.append((r, f"{NOTE_NAMES[tonic]} {mode}"))
    results.sort(reverse=True)
    best, second = results[0], results[1]
    gap = best[0] - second[0]
    conf = "high" if best[0] > 0.75 and gap > 0.08 else "medium" if best[0] > 0.6 and gap > 0.03 else "low"
    tonic, mode = best[1].split()
    t_idx = NOTE_NAMES.index(tonic)
    relative = (f"{NOTE_NAMES[(t_idx + 9) % 12]} minor" if mode == "major"
                else f"{NOTE_NAMES[(t_idx + 3) % 12]} major")
    return {"key": best[1], "score": round(float(best[0]), 3), "confidence": conf, "relative": relative,
            "runner_up": second[1], "runner_up_score": round(float(second[0]), 3),
            "tuning_a4_hz": round(ref, 1), "tuning_cents": round(tuning_cents, 1),
            "chroma": {NOTE_NAMES[i]: round(float(chroma[i]), 3) for i in range(12)}}


def delay_table(bpm):
    q = 60000.0 / bpm
    rows = [("1/1 whole", 4 * q, "240000/BPM"), ("1/2 half", 2 * q, "120000/BPM"),
            ("1/2 dotted", 3 * q, "180000/BPM"), ("1/4 quarter", q, "60000/BPM"),
            ("1/4 dotted", 1.5 * q, "90000/BPM"), ("1/4 triplet", 2 * q / 3, "40000/BPM"),
            ("1/8 eighth", q / 2, "30000/BPM"), ("1/8 dotted", 0.75 * q, "45000/BPM"),
            ("1/8 triplet", q / 3, "20000/BPM"), ("1/16 sixteenth", q / 4, "15000/BPM"),
            ("1/16 dotted", 3 * q / 8, "22500/BPM"), ("1/32", q / 8, "7500/BPM"),
            ("1/64", q / 16, "3750/BPM"), ("1/128", q / 32, "1875/BPM")]
    return [{"note": n, "ms": round(ms, 2), "formula": fm} for n, ms, fm in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("song", nargs="?")
    ap.add_argument("--bpm", type=float, help="known BPM (skips tempo detection)")
    ap.add_argument("--json", help="save results to this JSON file")
    a = ap.parse_args()
    if not a.song and not a.bpm:
        ap.error("give a song file, --bpm, or both")

    out = {}
    if a.song:
        x = load_mono(a.song)
        out["file"] = a.song
        out["duration_s"] = round(len(x) / SR, 2)
        if not a.bpm:
            t = detect_tempo(x)
            if t is None:
                sys.exit("Song is too short for tempo detection (needs about 8 s). Pass --bpm.")
            out["tempo"] = t
            print(f"Tempo    {t['bpm']:.2f} BPM (likely {t['bpm_rounded']}), confidence {t['confidence']}"
                  f"; also possible: {', '.join(str(v) for v in t['alternatives'])}")
        k = detect_key(x)
        out["key"] = k
        print(f"Key      {k['key']} (score {k['score']}, confidence {k['confidence']})"
              f"; runner-up {k['runner_up']} ({k['runner_up_score']})")
        if k["runner_up"] == k["relative"]:
            print(f"         {k['key']} and {k['relative']} use the same notes; the chord the song "
                  "resolves to decides which one it is.")
        print(f"Tuning   A4 = {k['tuning_a4_hz']} Hz ({k['tuning_cents']:+.1f} cents from 440)")

    bpm = a.bpm or out["tempo"]["bpm_rounded"]
    if not a.bpm and a.song:
        note = "rounded detected tempo" if abs(out["tempo"]["bpm"] - bpm) < 0.3 else "nearest whole BPM; check it"
        print(f"\nDelay times at {bpm} BPM ({note}):")
    else:
        print(f"\nDelay times at {bpm:g} BPM:")
    table = delay_table(bpm)
    out["delay_bpm"] = bpm
    out["delay_ms"] = table
    for r in table:
        print(f"  {r['note']:<15} {r['ms']:>9.2f} ms   ({r['formula']})")
    q = 60000.0 / bpm
    # pre-delay is always a note value: the one inside 25-40 ms, or else the one closest to that range
    cands = [("1/32", q / 8), ("1/64", q / 16), ("1/128", q / 32), ("1/256", q / 64)]
    inside = [(n, ms) for n, ms in cands if 25 <= ms <= 40]
    pick = inside[0] if inside else min(cands, key=lambda c: min(abs(c[1] - 25), abs(c[1] - 40)))
    where = "in the 25-40 ms range" if inside else "closest to the 25-40 ms range"
    print(f"Tempo-synced reverb pre-delay ({where}): {pick[0]} = {pick[1]:.2f} ms")
    out["predelay"] = {"note": pick[0], "ms": round(pick[1], 2)}
    decays = [("1/2", q * 2), ("1/2 dotted", q * 3), ("1 bar", q * 4)]
    print("Tempo-synced reverb decay (RT60) choices: "
          + ", ".join(f"{n} = {ms / 1000:.3f} s" for n, ms in decays)
          + " (plate usually 1.2-2.0 s, hall 1.8-2.8 s: pick the note value in that range)")
    out["decay_s"] = {n: round(ms / 1000, 5) for n, ms in decays}

    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=2)
        print(f"Saved {a.json}")


if __name__ == "__main__":
    main()

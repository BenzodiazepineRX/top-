#!/usr/bin/env python3
"""Vocal rider: even out a supporting vocal (adlibs, backing) and keep it under the main track.

It works like an engineer riding a fader, in three steps:
  1. Phrase leveling: each phrase is moved toward the median phrase level (at most +3 / -6 dB).
     Breaths and blips (more than 12 dB under the median) are never turned up.
  2. Word control: a word that jumps more than 3 dB above the phrase target is pulled 60% of the way back.
  3. Ceiling: the vocal is kept at least --margin-db under the main track's typical level
     (2-second average), with 150 ms look-ahead so the gain moves before the loud word.

Levels are measured on the mono sum (so a panned vocal is measured correctly), with an approximate
K-weighting, in 400 ms windows every 10 ms. Effect returns (echo, reverb) are not part of the measurement.

Usage:
  python3 vocal_rider.py VOCAL.wav MAIN.wav OUT.wav --gain-db 4.6 --margin-db 6

The main track may be a composite (beat + lead vocal). Then the ceiling is relative to that whole track,
not to an isolated lead vocal. Say so when reporting it.
"""
import argparse
import json

import numpy as np
import soundfile as sf
from scipy.ndimage import binary_closing, binary_opening, maximum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfilt

HOP_S, WIN_S = 0.01, 0.4


def k_weight(x, sr):
    """Approximate K-weighting: high-pass at 60 Hz plus about +4 dB above 1.5 kHz."""
    y = sosfilt(butter(2, 60, "hp", fs=sr, output="sos"), x)
    return y + 0.585 * sosfilt(butter(1, 1500, "hp", fs=sr, output="sos"), y)


def short_term_level(x, sr):
    hop, win = int(HOP_S * sr), int(WIN_S * sr)
    c = np.concatenate([[0.0], np.cumsum(k_weight(x, sr) ** 2)])
    idx = np.arange((len(x) - win) // hop) * hop
    return 10 * np.log10((c[idx + win] - c[idx]) / win + 1e-12)


def find_phrases(level, threshold):
    on = binary_opening(binary_closing(level > threshold, np.ones(15)), np.ones(12))   # join gaps <150 ms, drop blips <120 ms
    d = np.diff(np.r_[0, on.astype(int), 0])
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def smooth(g, attack_frames, release_frames):
    """One-pole smoothing of a gain curve (in dB), faster when turning down than when turning back up."""
    out = np.copy(g)
    for i in range(1, len(g)):
        a = 1 / attack_frames if g[i] < out[i - 1] else 1 / release_frames
        out[i] = out[i - 1] + a * (g[i] - out[i - 1])
    return out


def mean_db(level):
    return 10 * np.log10(np.mean(10 ** (level / 10)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vocal"); ap.add_argument("main"); ap.add_argument("out")
    ap.add_argument("--gain-db", type=float, default=0.0, help="static gain applied to the vocal before riding")
    ap.add_argument("--margin-db", type=float, default=6.0, help="keep the vocal at least this far under the main track")
    a = ap.parse_args()

    v, sr = sf.read(a.vocal, always_2d=True)
    m, msr = sf.read(a.main, always_2d=True)
    if sr != msr:
        raise SystemExit("vocal and main track have different sample rates")
    hop, win = int(HOP_S * sr), int(WIN_S * sr)

    lv = short_term_level(v.mean(axis=1) * 10 ** (a.gain_db / 20), sr)
    lm_fast = short_term_level(m.mean(axis=1)[:len(v)], sr)
    lm = 10 * np.log10(uniform_filter1d(10 ** (lm_fast / 10), 200) + 1e-12)       # main's typical level over 2 s

    phrases = find_phrases(lv, np.max(lv) - 35)
    phrase_level = [mean_db(lv[s:e]) for s, e in phrases]
    target = float(np.median(phrase_level))

    g = np.zeros_like(lv)
    for (s, e), p in zip(phrases, phrase_level):
        if p < target - 12:
            continue                                                               # breath or blip: leave alone
        g[s:e] = np.clip(target - p, -6, 3)                                        # 1) phrase leveling
        over = (lv[s:e] + g[s:e]) - (target + 3)
        g[s:e] -= 0.6 * np.clip(over, 0, None)                                     # 2) word control
    g = smooth(g, 3, 15)
    for _ in range(3):                                                             # 3) ceiling under the main track
        over = np.clip((lv + g) - lm + a.margin_db, 0, None)
        g = g - smooth(maximum_filter1d(over, 31), 2, 25)

    centres = np.arange(len(g)) * hop + win // 2
    gain = np.interp(np.arange(len(v)), centres, g)
    y = v * 10 ** ((a.gain_db + gain) / 20)[:, None]
    sf.write(a.out, y.astype(np.float32), sr, subtype="FLOAT")

    la = short_term_level(y.mean(axis=1), sr)
    active = np.zeros(len(lv), bool)
    for s, e in phrases:
        active[s:e] = True
    real = [(s, e) for (s, e), p in zip(phrases, phrase_level) if p >= target - 12]
    before = [mean_db(lv[s:e]) for s, e in real]
    after = [mean_db(la[s:e]) for s, e in real]
    spread = lambda x: round(float(np.percentile(x, 95) - np.percentile(x, 5)), 1)
    stats = lambda d: {"median": round(float(np.median(d)), 1), "p95": round(float(np.percentile(d, 95)), 1), "max": round(float(d.max()), 1)}
    report = {
        "phrases": len(phrases),
        "phrase_level_spread_dB": {"before": spread(before), "after": spread(after)},
        "vocal_minus_main_2s_average_dB": {"before": stats((lv - lm)[active]), "after": stats((la - lm)[active])},
        "vocal_minus_main_instant_dB_max": {"before": round(float((lv - lm_fast)[active].max()), 1),
                                            "after": round(float((la - lm_fast)[active].max()), 1)},
        "measurement": "mono sum, approx. K-weighting, 400 ms windows / 10 ms hop; effect returns not included",
    }
    print(json.dumps(report, indent=1))
    with open(a.out + ".rider.json", "w") as f:
        json.dump(report, f, indent=1)


if __name__ == "__main__":
    main()

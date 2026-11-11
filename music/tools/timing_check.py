#!/usr/bin/env python3
"""Timing check: is a supporting vocal consistently early or late against the main track?

Run it before adding any time-based effect (echo throws, reverse reverb). A vocal recorded while
monitoring through a phone or wireless headphones is often late by a constant 20-40 ms.

Method: syllable onsets (300-3000 Hz, 1 ms resolution) of each vocal phrase are slid against the main
track by up to +/- --max-ms. Only phrases with a clear best match are counted. The main track may be a
composite (beat + lead vocal), so the match is against everything in it, not an isolated lead.

The result is an ESTIMATE. A constant shift is a judgment call: render an A/B and let the artist choose.

Usage:
  python3 timing_check.py SUPPORT_VOCAL.wav MAIN.wav [--max-ms 80] [--json timing.json]
"""
import argparse
import json

import numpy as np
import soundfile as sf
from scipy.ndimage import binary_closing, binary_opening
from scipy.signal import butter, sosfiltfilt


def onset_flux(x, sr, hop):
    y = sosfiltfilt(butter(4, [300, 3000], "band", fs=sr, output="sos"), x)
    k = len(y) // hop
    env = np.sqrt(np.mean(y[:k * hop].reshape(k, hop) ** 2, axis=1))
    return np.clip(np.diff(env, prepend=env[0]), 0, None)


def find_phrases(x, sr, min_s=0.4):
    blk = int(0.01 * sr)
    k = len(x) // blk
    lev = 20 * np.log10(np.sqrt(np.mean(x[:k * blk].reshape(k, blk) ** 2, axis=1)) + 1e-12)
    on = lev > np.percentile(lev[lev > -80], 95) - 20
    on = binary_opening(binary_closing(on, np.ones(15)), np.ones(12))
    d = np.diff(np.r_[0, on.astype(int), 0])
    return [(s * 0.01, e * 0.01) for s, e in zip(np.where(d == 1)[0], np.where(d == -1)[0]) if (e - s) * 0.01 >= min_s]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vocal"); ap.add_argument("main")
    ap.add_argument("--max-ms", type=int, default=80)
    ap.add_argument("--json")
    a = ap.parse_args()

    v, sr = sf.read(a.vocal, always_2d=True)
    m, msr = sf.read(a.main, always_2d=True)
    if sr != msr:
        raise SystemExit("files have different sample rates")
    hop = int(0.001 * sr)                                    # 1 ms
    vm, mm = v.mean(axis=1), m.mean(axis=1)
    fv, fm = onset_flux(vm, sr, hop), onset_flux(mm, sr, hop)
    lags = np.arange(-a.max_ms, a.max_ms + 1)

    rows = []
    for start, end in find_phrases(vm, sr):
        i0, i1 = int(start * 1000), int(end * 1000)
        if i0 - a.max_ms < 0 or i1 + a.max_ms > len(fm):
            continue
        x = fv[i0:i1]
        norm = np.linalg.norm(x) * np.linalg.norm(fm[i0:i1]) + 1e-12
        c = np.array([np.dot(x, fm[i0 + l:i1 + l]) for l in lags]) / norm
        best = int(np.argmax(c))
        rows.append({"start_s": round(start, 2), "end_s": round(end, 2),
                     "vocal_late_ms": int(-lags[best]),      # main matches earlier => the vocal is late
                     "match": round(float(c[best]), 3),
                     "prominence": round(float((c[best] - np.median(c)) / (np.std(c) + 1e-12)), 1)})
    for r in rows:
        r["confident"] = bool(r["prominence"] >= 3.0 and r["match"] >= 0.3 and abs(r["vocal_late_ms"]) <= 60)

    sure = np.array([r["vocal_late_ms"] for r in rows if r["confident"]])
    summary = {"phrases": len(rows), "confident": int(len(sure))}
    if len(sure):
        med = float(np.median(sure))
        same_side = float(np.mean(np.sign(sure) == np.sign(med))) if med != 0 else 0.0
        summary.update(median_late_ms=round(med, 1), quartiles_ms=[float(np.percentile(sure, 25)), float(np.percentile(sure, 75))],
                       range_ms=[int(sure.min()), int(sure.max())], share_on_same_side=round(same_side, 2))
        if len(sure) >= 8 and same_side >= 0.8 and abs(med) >= 10:
            word = "LATE" if med > 0 else "EARLY"
            summary["verdict"] = (f"Consistent offset: the vocal is {word} by about {abs(med):.0f} ms. "
                                  "A constant shift is a candidate. Render an A/B and let the artist choose.")
        else:
            summary["verdict"] = "No consistent offset found. Do not shift the whole take."
    else:
        summary["verdict"] = "No phrase matched clearly. Timing cannot be judged this way."

    print(json.dumps(summary, indent=1))
    for r in rows:
        if r["confident"]:
            print("  {:7.2f}-{:7.2f} s  late {:+4d} ms  match {:.2f}  prominence {:.1f}".format(
                r["start_s"], r["end_s"], r["vocal_late_ms"], r["match"], r["prominence"]))
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"summary": summary, "phrases": rows}, f, indent=1)


if __name__ == "__main__":
    main()

"""Driftin' Away v2: even out the adlib responses (bars 51-88) so no answer jumps out over the others.

In v1 the 16 responses varied by 5.0 dB (K-weighted loudness, -18.8 to -13.8). Each response is moved toward the
median of all of them (at most +-4 dB), with the gain change made in the space between responses (60 ms ramps),
so no word is cut. The verse part (the double under the lead, before 79 s) is not touched.

in: a_7.wav (processed adlibs)   out: a_8.wav
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = sys.argv[:1] + ["v1"]
import build_mix as bm  # noqa: E402  (loudness helper and file loader)

D = bm.D
sr = 44100
RESP = [(80.21, 82.00), (83.63, 85.08), (86.82, 88.45), (90.13, 91.64), (93.23, 94.84), (96.43, 98.12),
        (99.66, 101.47), (102.86, 104.53), (104.87, 109.05), (111.50, 113.23), (114.71, 116.42), (118.07, 120.02),
        (121.28, 123.22), (124.72, 126.27), (130.90, 132.75), (135.93, 138.91)]

x, _ = bm.dt.read(D + "a_7.wav")
n = len(x)
lv = [bm.loud(x, a, b) for a, b in RESP]
target = float(np.median(lv))
gains_db = [float(np.clip(target - v, -4, 4)) for v in lv]
# gain curve: 0 dB before 79 s; each response holds its own gain; ramps sit in the gaps between responses
curve = np.zeros(n)
t = np.arange(n) / sr
ramp = 0.06
for k, ((a, b), g) in enumerate(zip(RESP, gains_db)):
    lo = a - 0.15 if k == 0 else (RESP[k - 1][1] + a) / 2
    hi = b + 0.25 if k == len(RESP) - 1 else (b + RESP[k + 1][0]) / 2
    curve[(t >= lo) & (t < hi)] = g
# smooth the steps (60 ms) so the change is never a jump; the steps sit mid-gap, at least 0.15 s from any word
k = int(ramp * sr)
curve = np.convolve(curve, np.ones(k) / k, mode="same")
y = x * (10 ** (curve / 20))[:, None]
bm.dt.write(D + "a_8.wav", y, sr)
after = [bm.loud(y, a, b) for a, b in RESP]
print(f"responses before: {' '.join(f'{v:.1f}' for v in lv)}  (spread {max(lv) - min(lv):.1f} dB)")
print(f"gains:            {' '.join(f'{g:+.1f}' for g in gains_db)}")
print(f"responses after:  {' '.join(f'{v:.1f}' for v in after)}  (spread {max(after) - min(after):.1f} dB)")
min_gap = min(RESP[k + 1][0] - RESP[k][1] for k in range(len(RESP) - 1))
print(f"smallest gap between responses {min_gap:.2f} s (the ramps sit in the middle of each gap)")
json.dump({"target_lufs": round(target, 2), "before": [round(v, 2) for v in lv], "gains_db": [round(g, 2) for g in gains_db],
           "after": [round(v, 2) for v in after]}, open(D + "level_adlibs.json", "w"), indent=1)

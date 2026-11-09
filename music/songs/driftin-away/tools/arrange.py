"""Driftin' Away: the bar grid, what the beat does bar by bar, and the vocal lines.

Grid: 150 BPM (self-match), beats at g0 + 0.4 n. g0 is refined from the drum hits that sit near the eighth grid.
Which beat is "1": the beat position (of 4) where the kick is strongest on average.
"""
import os
import json
import sys

import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402

D = os.path.join(os.environ.get("DRIFT_WORK", "."), "")  # folder with the stems and renders
sr = 44100
Q = 0.4
hits = np.load(D + "drum_hits.npy")

# ---- refine g0
g = 0.0405
for _ in range(3):
    e = ((hits - g + Q / 4) % (Q / 2)) - Q / 4
    near = e[np.abs(e) < 0.015]
    g += float(np.median(near))
print(f"grid: 150 BPM, eighth-grid offset g0 = {g * 1000:.2f} ms ({len(near)} of {len(hits)} hits within 15 ms, "
      f"median |error| of those {np.median(np.abs(near - np.median(near))) * 1000:.1f} ms)")

beat, _ = dt.read(D + "01_Beat.wav")
bm = beat.mean(axis=1)
bands = {"sub": butter(4, 100, "low", fs=sr, output="sos"),
         "mid": butter(4, [300, 3000], "band", fs=sr, output="sos"),
         "hat": butter(4, 6000, "high", fs=sr, output="sos")}
filt = {k: sosfiltfilt(v, bm) for k, v in bands.items()}

# kick position: low-band energy in the first 60 ms after each beat, averaged per position mod 4
nbeats = int((len(bm) / sr - g) / Q)
pos_e = np.zeros(4)
cnt = np.zeros(4)
for n in range(nbeats):
    i = int((g + n * Q) * sr)
    seg = filt["sub"][i:i + int(0.06 * sr)]
    pos_e[n % 4] += np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    cnt[n % 4] += 1
pos_db = 20 * np.log10(pos_e / cnt + 1e-12)
print("kick-band level right after each beat position (n mod 4):", " ".join(f"{d:6.1f}" for d in pos_db))
one = int(np.argmax(pos_db))
bar0 = g + one * Q
# snare check: mid band on positions
pos_m = np.zeros(4)
for n in range(nbeats):
    i = int((g + n * Q) * sr)
    seg = filt["mid"][i:i + int(0.06 * sr)]
    pos_m[n % 4] += np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
print("mid-band (snare/clap) level per position:              ", " ".join(f"{20 * np.log10(v / cnt[0] + 1e-12):6.1f}" for v in pos_m))
print(f"bar 1 downbeat taken at {bar0:.4f} s (position {one})")


def bb(t):
    """bar.beat (1-based) of a time"""
    k = (t - bar0) / Q
    bar = int(np.floor(k / 4)) + 1
    beat_ = k - (bar - 1) * 4 + 1
    return f"{bar}.{beat_:.2f}"


# ---- beat per bar
nbars = int((len(bm) / sr - bar0) / (4 * Q)) + 1
print()
print("beat, bar by bar (dB RMS of sub / mid / hats); '!' marks a bar 6+ dB down from the bar before in any band")
rows = []
prev = None
for b in range(-1, nbars):
    a = bar0 + b * 4 * Q
    i0, i1 = max(0, int(a * sr)), min(len(bm), int((a + 4 * Q) * sr))
    if i1 - i0 < sr * 0.2:
        continue
    lv = {k: 20 * np.log10(np.sqrt(np.mean(v[i0:i1] ** 2)) + 1e-9) for k, v in filt.items()}
    flag = ""
    if prev and any(lv[k] < prev[k] - 6 for k in lv):
        flag = "!"
    if prev and any(lv[k] > prev[k] + 6 for k in lv):
        flag += "^"
    rows.append((b + 1, a, lv, flag))
    prev = lv
for r in rows:
    b, a, lv, flag = r
    print(f"  bar {b:3d} {a:7.2f}s  sub {lv['sub']:6.1f} mid {lv['mid']:6.1f} hat {lv['hat']:6.1f} {flag}")

# beat-level detail around candidate drop points: per beat sub/mid/hat
print()
print("per-beat detail near the section changes")
for lo, hi in ((24.0, 28.5), (74.5, 79.5), (136.0, 141.0), (162.0, 167.0)):
    print(f"  {lo}-{hi} s")
    n0 = int(np.ceil((lo - g) / Q))
    while g + n0 * Q < hi:
        t = g + n0 * Q
        i0, i1 = int(t * sr), int((t + Q) * sr)
        lv = {k: 20 * np.log10(np.sqrt(np.mean(v[i0:i1] ** 2)) + 1e-9) for k, v in filt.items()}
        print(f"     {t:7.3f} s ({bb(t):>7s})  sub {lv['sub']:6.1f} mid {lv['mid']:6.1f} hat {lv['hat']:6.1f}")
        n0 += 1

# ---- vocal lines: segments separated by gaps >= 0.18 s
print()
lines = {}
for name in ("02_Lead", "03_Background", "04_Adlibs"):
    x, _ = dt.read(D + name + ".wav")
    m = x.mean(axis=1)
    hop = int(0.01 * sr)
    n = len(m) // hop
    r = np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(axis=1))
    db = 20 * np.log10(r + 1e-12)
    act_lvl = 20 * np.log10(np.sqrt(np.mean(r[db > -45] ** 2)))
    on = db > act_lvl - 24
    segs, s = [], None
    for i, a in enumerate(on):
        if a and s is None:
            s = i
        if not a and s is not None:
            segs.append([s * 0.01, i * 0.01])
            s = None
    if s is not None:
        segs.append([s * 0.01, n * 0.01])
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < 0.18:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    merged = [q for q in merged if q[1] - q[0] >= 0.08]
    lines[name] = merged
    print(f"{name}: {len(merged)} lines (gap >= 0.18 s; active level {act_lvl:.1f} dBFS, floor {act_lvl - 24:.1f})")
    for k, (a, b) in enumerate(merged):
        gap = merged[k + 1][0] - b if k + 1 < len(merged) else 99
        print(f"   {a:7.2f}-{b:7.2f}  ({bb(a):>7s} to {bb(b):>7s})  len {b - a:5.2f}  gap after {gap:5.2f}")

json.dump({"g0": g, "bar0": bar0, "lines": lines}, open(D + "arrange.json", "w"), indent=1)

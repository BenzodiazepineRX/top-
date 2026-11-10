"""Baccdoor checks, measured on the rendered files.   usage: verify_bacc.py <version>

1. retune: each stem's pitch moved by the planned cents, and its timing unchanged (envelope correlation)
2. echoes: every repeat found by correlating the word with the echo track; distance to the grid beat
3. layer order, every 2 bars: background under the mains by its target, background-of-background under the
   background (K-weighted). FAIL if a layer is louder than the one above it, or more than 1.5 dB over its target
4. gaps: stretches of 0.6 s+ with no vocal and no echo, from the first vocal to the last
5. phones: mono fold-down of the master (level change and the vocal band), stereo correlation
Exits 1 on any FAIL.
"""
import json
import os
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc_lib as L  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("BACC_WORK", ".")), "")
V = sys.argv[1] if len(sys.argv) > 1 else "v1"
sr = L.sr
b = json.load(open(D + f"build_{V}.json"))
fails = []

# ---- 2. echoes
bp = butter(4, [500, 4500], "bandpass", fs=sr, output="sos")
E, _ = L.dt.read(D + f"stem_{V}_echo.wav")
E = sosfiltfilt(bp, L.mono(E))
srcs = {"lead 1": L.dt.read(D + "m1_8.wav")[0], "lead 2": L.dt.read(D + "m2_8.wav")[0]}
offs = []
for r in b["echoes"]:
    a, e = r["word"]
    w = sosfiltfilt(bp, L.mono(srcs[r["src"]][int((a - 0.005) * sr):int((e + 0.02) * sr)]))
    for tk in r["echo_times"]:
        s0 = int((tk - 0.045) * sr)
        seg = E[s0:s0 + len(w) + int(0.08 * sr)]
        if len(seg) < len(w) + 10:
            continue
        c = fftconvolve(seg, w[::-1], mode="valid")
        k = int(np.argmax(c))
        tf = (s0 + k) / sr + 0.005
        offs.append((tf - L.beat_t(round((tf - L.G0) / L.Q))) * 1000)
offs = np.abs(offs)
print(f"2. echoes: {len(b['echoes'])} throws, {len(offs)} repeats; distance from the grid beat median {np.median(offs):.2f} ms, max {offs.max():.2f} ms")
if offs.max() > 2.0:
    fails.append("echo off the grid")

# ---- 3. layer order
Km = L.kweight(L.dt.read(D + f"stem_{V}_mains.wav")[0])
Kb = L.kweight(L.dt.read(D + f"stem_{V}_bg.wav")[0])
Kbb = L.kweight(L.dt.read(D + f"stem_{V}_bgbg.wav")[0])
bgr = {"A": -6.0, "drop 1": -5.0, "B": -5.0, "drop 2": -5.0, "C": -4.5}
pm, pb, pbb = (L.kblocks(k) for k in (Km, Kb, Kbb))
am, ab, abb = (L.active_blocks(p) for p in (pm, pb, pbb))
rows = []
bar = 1
while L.bar_t(bar + 2) < 175:
    a0, a1 = L.bar_t(bar), L.bar_t(bar + 2)
    sec = L.section_of((a0 + a1) / 2)
    d = L.layer_diff(pb, pm, ab, am, a0, a1)
    if d is not None:
        rows.append(("background vs mains", a0, d, bgr.get(sec, -5.0)))
    d = L.layer_diff(pbb, pb, abb, ab, a0, a1)
    if d is not None:
        rows.append(("bg-of-bg vs background", a0, d, -4.0))
    else:
        d = L.layer_diff(pbb, pm, abb, am, a0, a1)
        if d is not None:
            rows.append(("bg-of-bg vs mains", a0, d, -9.0))
    bar += 2
print("3. layer order, measured only where both layers sing (every 2 bars):")
for lab in ("background vs mains", "bg-of-bg vs background", "bg-of-bg vs mains"):
    rr = [r for r in rows if r[0] == lab]
    if not rr:
        continue
    over = [r for r in rr if r[2] > 0 or r[2] > r[3] + 1.5]
    print(f"   {lab}: {len(rr)} windows, diff median {np.median([r[2] for r in rr]):+.1f} dB (range {min(r[2] for r in rr):+.1f} to {max(r[2] for r in rr):+.1f}); "
          f"louder than the layer above or >1.5 dB over target: {len(over)}"
          + ("  " + ", ".join(f"{int(r[1] // 60)}:{r[1] % 60:04.1f} {r[2]:+.1f}" for r in over[:8]) if over else ""))
    if over:
        fails.append(lab)

# ---- 4. gaps
def act(x, rel=-35):
    m = L.mono(x)
    h = 882
    nn = len(m) // h
    r = 20 * np.log10(np.sqrt((m[:nn * h].reshape(nn, h) ** 2).mean(1)) + 1e-9)
    out = np.zeros(int(210 / 0.02), bool)
    lv = np.percentile(r[r > -80], 95) if (r > -80).any() else -200
    a = r > lv + rel
    out[:min(len(a), len(out))] = a[:len(out)]
    return out


V_ = np.any([act(L.dt.read(D + f)[0]) for f in (f"stem_{V}_mains.wav", f"stem_{V}_bg.wav", f"stem_{V}_bgbg.wav")], axis=0)
EE = act(L.dt.read(D + f"stem_{V}_echo.wav")[0], -45)
first, lastv = np.where(V_)[0][0], np.where(V_)[0][-1]
gaps, s = [], None
for i in range(first, lastv):
    if not V_[i] and s is None:
        s = i
    if V_[i] and s is not None:
        if (i - s) * 0.02 >= 0.6:
            gaps.append((s * 0.02, i * 0.02, EE[s:i].mean()))
        s = None
print(f"4. vocal gaps of 0.6 s+ between the first and last vocal: {len(gaps)}"
      + ("  " + ", ".join(f"{int(a // 60)}:{a % 60:04.1f} ({c - a:.1f} s, echo {e * 100:.0f}%)" for a, c, e in gaps) if gaps else ""))
print(f"   the vocals end at {int(lastv * 0.02 // 60)}:{lastv * 0.02 % 60:04.1f}")

# ---- 5. phones
mst, _ = L.dt.read(D + f"Baccdoor_master_{V}_24bit.wav")
mono_ = mst.mean(axis=1, keepdims=True).repeat(2, 1)
lst, lmo = L.loud(mst, 0, len(mst) / sr, False), L.loud(mono_, 0, len(mst) / sr, False)
vb = butter(4, [1000, 4000], "bandpass", fs=sr, output="sos")
st_v = 10 * np.log10(np.mean(sosfiltfilt(vb, mst, axis=0) ** 2))
mo_v = 10 * np.log10(np.mean(sosfiltfilt(vb, mono_, axis=0) ** 2))
corr = float(np.corrcoef(mst[:, 0], mst[:, 1])[0, 1])
print(f"5. phones (mono): loudness {lst:.1f} -> {lmo:.1f} LUFS ({lmo - lst:+.1f} dB), vocal band 1-4 kHz {mo_v - st_v:+.1f} dB, L/R correlation {corr:.2f}")
if lmo - lst < -1.5:
    fails.append("mono loss")

print("RESULT:", "FAIL " + "; ".join(fails) if fails else "all checks pass")
sys.exit(1 if fails else 0)

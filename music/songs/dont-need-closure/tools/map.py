"""Don't Need Closure: tempo (self-match, exact envelope rate), the drum grid, the beat bar by bar, every vocal stem's lines,
and whether the vocal stems line up with this beat file (beat bleed in the vocal stems, and syllable timing on the
grid). Every index/time conversion uses the real hop (samples / sr), the lesson from Driftin' Away."""
import json
import os
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402
import groove_delay as gd  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("CLOSURE_WORK", ".")), "")
sr = 44100
beat, _ = dt.read(D + "01_Beat.wav")
bm = beat.mean(axis=1)

# ---- tempo by self-match
step = 22
rate = sr / step


def flux(sig):
    e = np.abs(sig)
    k = int(0.005 * sr)
    e = np.convolve(e, np.ones(k) / k, mode="same")[::step]
    return np.maximum(np.diff(np.log(e + 1e-6), prepend=0), 0)


low = flux(sosfiltfilt(butter(2, 150, "low", fs=sr, output="sos"), bm))
mid = flux(sosfiltfilt(butter(2, [150, 2500], "band", fs=sr, output="sos"), bm))
hi = flux(sosfiltfilt(butter(2, 5000, "high", fs=sr, output="sos"), bm))
on = low + mid + hi
print("tempo self-match (onset pattern vs itself N bars later, 4/4):")
best_all = []
for bars in (4, 8, 16, 24):
    best = None
    for bpm in np.arange(124.0, 128.0, 0.002):
        L = int(round(bars * 240 / bpm * rate))
        if L > len(on) - rate * 10:
            continue
        a, b = on[:-L], on[L:]
        c = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        if best is None or c > best[0]:
            best = (c, bpm)
    if best:
        best_all.append(best[1])
        print(f"   {bars:2d} bars: {best[1]:.3f} BPM (similarity {best[0]:.3f})")
BPM = float(np.median(best_all))
Q = 60 / BPM
t = np.arange(len(on)) / rate
for lab, e in (("kick", low), ("snare/body", mid), ("hats", hi)):
    w = e * (e > np.percentile(e, 99))
    out = []
    for P, pl in ((Q, "1/4"), (Q / 2, "1/8"), (Q / 4, "1/16"), (Q / 3, "1/8t")):
        z = np.sum(w * np.exp(2j * np.pi * t / P)) / np.sum(w)
        out.append(f"{pl} R {abs(z):.2f} phase {((np.angle(z) % (2 * np.pi)) / (2 * np.pi) * P) * 1000:6.1f} ms")
    print(f"   {lab:10s} " + " | ".join(out))

hits, _ = gd.drum_hits(D + "01_Beat.wav")
np.save(D + "drum_hits.npy", hits)
g = 0.0
z = np.mean(np.exp(2j * np.pi * hits / (Q / 2)))
g = (np.angle(z) % (2 * np.pi)) / (2 * np.pi) * (Q / 2)
for _ in range(3):
    e = ((hits - g + Q / 4) % (Q / 2)) - Q / 4
    near = e[np.abs(e) < 0.015]
    g += float(np.median(near))
print(f"BPM {BPM:.3f}; eighth-grid offset from drum hits g0 = {g * 1000:.2f} ms ({len(near)} of {len(hits)} hits within 15 ms)")

# downbeat: the beat position (mod 4) with the strongest kick
lowsig = sosfiltfilt(butter(4, 100, "low", fs=sr, output="sos"), bm)
midsig = sosfiltfilt(butter(4, [300, 3000], "band", fs=sr, output="sos"), bm)
hisig = sosfiltfilt(butter(4, 6000, "high", fs=sr, output="sos"), bm)
nb = int((len(bm) / sr - g) / Q)
pk = np.zeros(4)
ps = np.zeros(4)
for n in range(nb):
    i = int((g + n * Q) * sr)
    pk[n % 4] += np.sqrt(np.mean(lowsig[i:i + int(0.06 * sr)] ** 2))
    ps[n % 4] += np.sqrt(np.mean(midsig[i:i + int(0.06 * sr)] ** 2))
print("kick per beat position:", " ".join(f"{20 * np.log10(v / (nb / 4)):.1f}" for v in pk),
      "| snare per position:", " ".join(f"{20 * np.log10(v / (nb / 4)):.1f}" for v in ps))
one = int(np.argmax(pk))
bar0 = g + one * Q
BAR = 4 * Q
print(f"bar 1 at {bar0:.4f} s, bar = {BAR:.4f} s")

print("\nbeat bar by bar (sub / mid / hats dB; ! = 6 dB drop vs previous bar in a band, ^ = 6 dB rise):")
prev = None
for b in range(0, int((len(bm) / sr - bar0) / BAR) + 1):
    a = bar0 + b * BAR
    i0, i1 = int(a * sr), min(len(bm), int((a + BAR) * sr))
    if i1 - i0 < sr * 0.3:
        continue
    lv = {k: 20 * np.log10(np.sqrt(np.mean(v[i0:i1] ** 2)) + 1e-9) for k, v in (("sub", lowsig), ("mid", midsig), ("hat", hisig))}
    flag = ""
    if prev and any(lv[k] < prev[k] - 6 for k in lv):
        flag += "!"
    if prev and any(lv[k] > prev[k] + 6 for k in lv):
        flag += "^"
    print(f"  bar {b + 1:3d} {a:7.2f}s  sub {lv['sub']:6.1f} mid {lv['mid']:6.1f} hat {lv['hat']:6.1f} {flag}")
    prev = lv

# ---- vocal stems: lines (10 ms frames; exact 441-sample hop)
print()
lines = {}
for name in ("02_Lead1", "03_Lead2", "04_Adlib1", "05_Adlib2"):
    x, _ = dt.read(D + name + ".wav")
    m = x.mean(axis=1)
    hop = 441
    n = len(m) // hop
    r = np.sqrt((m[:n * hop].reshape(n, hop) ** 2).mean(axis=1))
    db = 20 * np.log10(r + 1e-12)
    act = db[db > db.max() - 50]
    lvl = 20 * np.log10(np.sqrt(np.mean(10 ** (act / 10))))
    onm = db > lvl - 22
    segs, s = [], None
    for i, a in enumerate(onm):
        if a and s is None:
            s = i
        if not a and s is not None:
            segs.append([s * hop / sr, i * hop / sr])
            s = None
    if s is not None:
        segs.append([s * hop / sr, n * hop / sr])
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < 0.25:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    merged = [q for q in merged if q[1] - q[0] >= 0.1]
    lines[name] = merged
    tot = sum(b - a for a, b in merged)

    def bb(tt):
        k = (tt - bar0) / Q
        bar = int(np.floor(k / 4)) + 1
        return f"{bar}.{k - (bar - 1) * 4 + 1:.2f}"

    print(f"{name}: {len(merged)} phrases (gap >= 0.25 s), {tot:.1f} s active, level {lvl:.1f} dBFS, peak frame {db.max():.1f}")
    print("   " + "  ".join(f"{a:.2f}-{b:.2f}({bb(a)})" for a, b in merged))

# ---- alignment check 1: beat bleed in each vocal stem (correlation of the vocal stem with the beat around lag 0)
print("\nbeat bleed check (normalized correlation of each vocal stem with the beat, 200-2000 Hz, lags +-2 s):")
bpf = butter(4, [200, 2000], "band", fs=sr, output="sos")
B = sosfiltfilt(bpf, bm)[::4]
for name in ("02_Lead1", "03_Lead2", "04_Adlib1", "05_Adlib2"):
    x, _ = dt.read(D + name + ".wav")
    v = sosfiltfilt(bpf, x.mean(axis=1))[::4]
    n = min(len(v), len(B))
    a0 = int(40 * sr / 4)
    a1 = min(n, a0 + int(60 * sr / 4))
    seg = v[a0:a1]
    W = int(2 * sr / 4)
    ref = B[a0 - W:a1 + W]
    c = fftconvolve(ref, seg[::-1], mode="valid")
    en = np.sqrt(np.convolve(ref ** 2, np.ones(len(seg)), mode="valid") * np.dot(seg, seg)) + 1e-12
    r = c / en
    k = int(np.argmax(np.abs(r)))
    print(f"   {name:9s} best |r| {abs(r[k]):.3f} at lag {(k - W) * 4 / sr * 1000:+.1f} ms (median |r| {np.median(np.abs(r)):.3f})")

json.dump({"bpm": BPM, "g0": g, "bar0": bar0, "lines": lines}, open(D + "map.json", "w"), indent=1)

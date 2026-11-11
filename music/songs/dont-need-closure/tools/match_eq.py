"""Tone match: move a vocal's long-term tone part of the way toward a reference vocal.
usage: match_eq.py src.wav ref.wav out.wav [--amount 0.7] [--max-cut 10] [--max-boost 4] [--src-t 40 100] [--ref-t 30 75]
       match_eq.py src.wav - out.wav --curve-in saved_curve.json    (re-apply a saved curve, no reference needed)

Both tones are measured over the louder half of the sung frames (silence excluded), as power per octave-wide band (centred every 1/3 octave) relative to each file's
own total from 120 Hz to 14 kHz, so only the SHAPE is compared, not the level. The difference (reference minus
source) is taken --amount of the way, clamped, smoothed over 1/3 octave, and applied as a linear-phase EQ (no phase
change, timing kept to the sample). Below 120 Hz and above 14 kHz the curve holds its edge value.
Baccdoor v3: the reference is the owner's own Driftin' Away lead as mixed (l_8.wav), which he did not call harsh.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.signal import fftconvolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closure_lib as L  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("ref")
ap.add_argument("out")
ap.add_argument("--amount", type=float, default=0.7)
ap.add_argument("--max-cut", type=float, default=10.0)
ap.add_argument("--max-boost", type=float, default=4.0)
ap.add_argument("--src-t", type=float, nargs=2, default=[40, 100])
ap.add_argument("--ref-t", type=float, nargs=2, default=[30, 75])
ap.add_argument("--curve-out", default=None)
ap.add_argument("--curve-in", default=None)
a = ap.parse_args()
sr = L.sr
N = 4096
f = np.fft.rfftfreq(N, 1 / sr)
win = np.hanning(N)


def ltas(path, t0, t1):
    x, _ = L.dt.read(path)
    m = L.mono(x)[int(t0 * sr):int(t1 * sr)]
    S = np.array([np.abs(np.fft.rfft(m[i:i + N] * win)) ** 2 for i in range(0, len(m) - N, 1024)])
    e = S.sum(1)
    act = e > e.max() * 1e-4        # frames within 40 dB of the loudest: silence between lines does not count, so a
    return S[e > np.percentile(e[act], 50)].mean(0)   # track that rests half the time is measured like a continuous one


def third_oct(S):
    """power in octave-wide bands centred every 1/3 octave, relative to the 120 Hz-14 kHz total (dB)"""
    fc = 1000 * 2 ** (np.arange(-23, 12) / 3)          # 5 Hz .. 16 kHz
    fc = fc[(fc >= 100) & (fc <= 16000)]
    tot = S[(f >= 120) & (f < 14000)].sum()
    # each band is one octave wide (centres every 1/3 octave): a monotone voice has deep gaps between its harmonics
    # (B2: 123, 247, 370 Hz), and narrower bands would try to fill those gaps
    v = np.array([S[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].sum() / tot for c in fc])
    return fc, 10 * np.log10(v + 1e-20)


if a.curve_in:
    cv = json.load(open(a.curve_in))
    fc = np.array([float(k) for k in cv["curve_db"]])
    d = np.array(list(cv["curve_db"].values()), float)
    a.amount, a.max_cut, a.max_boost, a.ref = cv["amount"], cv["max_cut"], cv["max_boost"], cv["ref"]
else:
    fc, s_db = third_oct(ltas(a.src, *a.src_t))
    _, r_db = third_oct(ltas(a.ref, *a.ref_t))
    d = np.clip(a.amount * (r_db - s_db), -a.max_cut, a.max_boost)
    inside = (fc >= 120) & (fc <= 14000)
    d[fc < 120] = d[inside][0]
    d[fc > 14000] = d[inside][-1]
    d = np.convolve(np.pad(d, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")   # 1/3-octave smoothing
# linear-phase FIR from the curve (interpolated on log frequency)
NF = 8192
ff = np.fft.rfftfreq(NF, 1 / sr)
g_db = np.interp(np.log10(np.maximum(ff, 1)), np.log10(fc), d)
h = np.fft.irfft(10 ** (g_db / 20), NF)
h = np.roll(h, NF // 2) * np.blackman(NF)
x, _ = L.dt.read(a.src)
y = np.stack([fftconvolve(x[:, c], h, mode="full")[NF // 2:NF // 2 + len(x)] for c in range(x.shape[1])], 1)
L.dt.write(a.out, y.astype(np.float32), sr)
curve = {f"{c:.1f}": round(float(v), 3) for c, v in zip(fc, d)}
if a.curve_out:
    json.dump({"amount": a.amount, "max_cut": a.max_cut, "max_boost": a.max_boost, "ref": os.path.basename(a.ref),
               "curve_db": curve}, open(a.curve_out, "w"), indent=1)
print("Tone match ({:.0f}% toward {}): ".format(a.amount * 100, os.path.basename(a.ref))
      + ", ".join(f"{c:.0f} Hz {v:+.1f}" for c, v in zip(fc, d) if c in fc[::3]))

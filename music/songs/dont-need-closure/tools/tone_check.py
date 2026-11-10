"""Don't Need Closure: how each vocal layer sits over the beat, band by band (while it sings, verse 1), and each
layer's own tone and grit. usage: tone_check.py <version>"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closure_lib as L  # noqa: E402

V = sys.argv[1] if len(sys.argv) > 1 else "v1"
D = os.path.join(os.path.abspath(os.environ.get("CLOSURE_WORK", ".")), "")
sr = L.sr
N = 4096
f = np.fft.rfftfreq(N, 1 / sr)
win = np.hanning(N)
T0, T1 = L.bar_t(18), L.bar_t(42)


def spec(x):
    m = L.mono(x)[int(T0 * sr):int(T1 * sr)]
    return np.array([np.abs(np.fft.rfft(m[i:i + N] * win)) ** 2 for i in range(0, len(m) - N, 2048)])


def bandp(S, c):
    return S[:, (f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum(1)


fc = [250, 400, 630, 1000, 1587, 2000, 2520, 3175, 4000, 5040, 6350, 8000]
edges = [100, 200, 400, 800, 1600, 2500, 3500, 5000, 7000, 10000, 14000]
Sb = spec(L.dt.read(D + f"stem_{V}_beat.wav")[0])
print("1/3-octave band (Hz)     " + " ".join(f"{c:6d}" for c in fc))
S = {}
for nm in ("leads", "adlibs"):
    S[nm] = spec(L.dt.read(D + f"stem_{V}_{nm}.wav")[0])
    e = S[nm].sum(1)
    act = e > e.max() * 1e-4
    s = e > np.percentile(e[act], 50)
    S[nm + "_s"] = s
    print(f"{nm:7s} over the beat (dB) " + " ".join(f"{10 * np.log10(bandp(S[nm], c)[s].mean() / bandp(Sb, c)[s].mean()):6.1f}" for c in fc))
print("\ntone (dB of own total)   " + "".join(f"{a:6d}" for a in edges[:-1]) + "   grit(3-8k)")
for nm in ("leads", "adlibs"):
    Sx = S[nm][S[nm + "_s"]]
    tot = Sx.mean(0)[(f > 100) & (f < 14000)].sum()
    fl = Sx[:, (f >= 3000) & (f < 8000)]
    grit = float(np.mean(np.exp(np.mean(np.log(fl + 1e-20), 1)) / np.mean(fl, 1)))
    print(f"{nm:25s}" + "".join(f"{10 * np.log10(Sx.mean(0)[(f >= a) & (f < b)].sum() / tot):6.1f}" for a, b in zip(edges[:-1], edges[1:])) + f"   {grit:.3f}")

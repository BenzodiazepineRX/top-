"""Grain reducer for sung, autotuned vocals.   usage: degrain.py in.wav out.wav [--depth 8] [--lo 1500] [--hi 12500]

The scratchy sound in these takes is noise-like energy BETWEEN the harmonics of the sung note (measured with hnr.py:
the lead stems carry it, the chain does not add it). In voiced frames only, this lowers the energy between the
harmonics by up to --depth dB from --lo to --hi Hz, and leaves alone:
  - the harmonics themselves (the note, the words),
  - every frame without a steady pitch (consonants, S and T sounds, breaths, slides),
  - everything below --lo (the body of the voice).
Where the pitch moves inside a frame, the kept zone around each harmonic widens with frequency, and where it would
cover more than 70% of the gap between harmonics the frame is left untouched, so nothing gets chopped.
The output is the MID (mono) of the input, written as two identical channels.
"""
import argparse
import os
import sys

import numpy as np
from scipy.signal import istft, stft

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc_lib as L  # noqa: E402

from scipy.signal import butter, sosfiltfilt  # noqa: E402

BP = butter(4, [70, 1500], "bandpass", fs=L.sr, output="sos")


def f0_track(m, thr=0.35):
    """YIN pitch every 10 ms (40 ms frames). The threshold is looser than pitch_layers.py's 0.15 because these takes
    are grainy: the comb fit below decides whether a frame really has a clear note."""
    m = sosfiltfilt(BP, m)
    fl, hop, sr_ = 1764, 441, L.sr
    out = np.full((len(m) - fl) // hop, np.nan)
    lo, hi = int(sr_ / 800), int(sr_ / 70)
    for k in range(len(out)):
        w = m[k * hop:k * hop + fl]
        if np.sqrt(np.mean(w ** 2)) < 10 ** (-55 / 20):
            continue
        w = w - w.mean()
        ac = np.correlate(w, w, mode="full")[fl - 1:fl - 1 + hi + 2]
        e = np.cumsum(w[::-1] ** 2)[::-1]
        dif = e[0] + e[:hi + 2] - 2 * ac
        cm = np.concatenate(([1], dif[1:] * np.arange(1, len(dif)) / (np.cumsum(dif[1:]) + 1e-12)))
        cand = np.where(cm[lo:hi] < thr)[0]
        if len(cand) == 0:
            continue
        t = lo + cand[0]
        while t + 1 < hi and cm[t + 1] < cm[t]:
            t += 1
        a_, b_, c_ = cm[t - 1], cm[t], cm[min(t + 1, len(cm) - 1)]
        out[k] = sr_ / (t + (a_ - c_) / (2 * (a_ - 2 * b_ + c_) + 1e-12))
    return out

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("output")
ap.add_argument("--depth", type=float, default=8.0)
ap.add_argument("--lo", type=float, default=1500.0)
ap.add_argument("--hi", type=float, default=12500.0)
a = ap.parse_args()

sr = L.sr
x, s = L.dt.read(a.input)
assert s == sr
m = L.mono(x).astype(np.float64)
f0 = f0_track(m)
tc = (np.arange(len(f0)) * 441 + 882) / sr

N, H = 4096, 512
fr, tt, Z = stft(m, sr, window="hann", nperseg=N, noverlap=N - H)
df = fr[1]
G = np.zeros(Z.shape, np.float32)            # gain in dB
wf = np.clip((fr - a.lo) / 1000.0, 0, 1) * (fr <= a.hi)
used = 0
voiced = 0
for j, t0 in enumerate(tt):
    sel = (tc >= t0 - N / 2 / sr) & (tc <= t0 + N / 2 / sr)
    ff = f0[sel]
    if len(ff) < 5 or np.isnan(ff).mean() > 0.2:
        continue
    ff = ff[~np.isnan(ff)]
    voiced += 1
    fm = float(np.median(ff))
    spread = float(np.log(np.percentile(ff, 90) / np.percentile(ff, 10)))   # pitch movement inside the frame
    if spread > 0.06:
        continue
    mag = np.log(np.abs(Z[:, j]) + 1e-12)
    # refine the pitch to the harmonics actually in the frame (1-5 kHz comb fit, +-1.2%)
    cand = fm * (1 + np.linspace(-0.012, 0.012, 49))
    ks = np.arange(1, int(5000 / fm) + 1)
    sc = np.interp((cand[:, None] * ks[None, :]).ravel(), fr, mag).reshape(len(cand), len(ks)).sum(1)
    f1 = float(cand[int(np.argmax(sc))])
    # a clear note: harmonics stand at least 6 dB over the midpoints between them (1-4 kHz)
    kh = np.arange(max(1, int(1000 / f1)), int(4000 / f1) + 1)
    if (np.interp(kh * f1, fr, mag).mean() - np.interp((kh + 0.5) * f1, fr, mag).mean()) * 20 / np.log(10) < 6.0:
        continue
    # distance of every bin to its nearest harmonic, in Hz
    kk = np.round(fr / f1)
    dist = np.abs(fr - kk * f1)
    hw = 22.0 + fr * spread / 2                            # kept zone: window main lobe + pitch movement
    gap = f1 / 2
    ok = hw < 0.7 * gap                                     # comb only where the harmonics are clearly resolved
    rw = np.maximum(gap - hw, 1.0)
    u = np.clip((dist - hw) / rw, 0, 1)
    g = -a.depth * (0.5 - 0.5 * np.cos(np.pi * u)) * wf * ok
    G[:, j] = g
    used += 1

# smooth the gains over time (1-2-1), so the comb fades in and out with the notes
Gs = G.copy()
Gs[:, 1:-1] = 0.25 * G[:, :-2] + 0.5 * G[:, 1:-1] + 0.25 * G[:, 2:]
_, y = istft(Z * (10 ** (Gs / 20)), sr, window="hann", nperseg=N, noverlap=N - H)
y = y[:len(m)]
if len(y) < len(m):
    y = np.pad(y, (0, len(m) - len(y)))
band = (fr >= 2000) & (fr < 8000)
e0 = (np.abs(Z[band]) ** 2).sum()
e1 = (np.abs(Z[band] * 10 ** (Gs[band] / 20)) ** 2).sum()
L.dt.write(a.output, np.stack([y, y], 1).astype(np.float32), sr)
print(f"Grain reducer: {used} of {voiced} voiced frames combed ({used / max(voiced, 1) * 100:.0f}%), depth {a.depth} dB "
      f"between harmonics {a.lo:.0f}-{a.hi:.0f} Hz; 2-8 kHz energy {10 * np.log10(e1 / e0):+.1f} dB overall")

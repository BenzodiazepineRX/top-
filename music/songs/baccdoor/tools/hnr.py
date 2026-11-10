"""How clean is the voice at each step? Harmonics-to-noise ratio: on sustained sung frames (pitch known from the raw
take), the energy ON the harmonics (k * f0, +-35 cents) against the energy BETWEEN them, in 1-6 kHz.
Grain, phasiness or distortion that a step adds lands between the harmonics and lowers the ratio.
Also the waveform distortion a compressor adds on low notes: energy between harmonics below 1 kHz."""
import os
import sys

import numpy as np

sys.argv = ["x"]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pitch_layers.py")).read().split("for nm in (")[0]
ns = {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "pitch_layers.py")}
exec(compile(src, "pl", "exec"), ns)
dt, f0_track = ns["dt"], ns["f0_track"]
sr = 44100
N = 4096
f = np.fft.rfftfreq(N, 1 / sr)
win = np.hanning(N)


def frames_and_f0(path_raw, t0, t1):
    x, _ = dt.read(path_raw)
    seg = x[int(t0 * sr):int(t1 * sr)]
    f0, conf = f0_track(seg)
    return f0


def hnr(path, f0, t0, t1, lo=1000, hi=6000):
    x, _ = dt.read(path)
    m = x.mean(axis=1)[int(t0 * sr):int(t1 * sr)]
    on_e, off_e, on_l, off_l = 0.0, 0.0, 0.0, 0.0
    used = 0
    for k in range(0, len(f0)):
        c = k * 441 + 882  # f0 frame k is centred at k*10 ms + 20 ms
        if np.isnan(f0[k]) or k == 0 or k + 1 >= len(f0) or np.isnan(f0[k - 1]) or np.isnan(f0[k + 1]):
            continue
        if abs(1200 * np.log2(f0[k + 1] / f0[k - 1])) > 30:    # sustained only
            continue
        s = c - N // 2
        if s < 0 or s + N > len(m):
            continue
        S = np.abs(np.fft.rfft(m[s:s + N] * win)) ** 2
        h = np.arange(1, int(hi / f0[k]) + 1) * f0[k]
        cents = 1200 * np.log2(np.maximum(f, 1) / f0[k])
        near = np.zeros_like(f, bool)
        for hk in h:
            near |= np.abs(f - hk) < hk * (2 ** (35 / 1200) - 1) + 5.4
        band = (f >= lo) & (f < hi)
        on_e += S[band & near].sum()
        off_e += S[band & ~near].sum()
        bl = (f >= 120) & (f < 1000)
        on_l += S[bl & near].sum()
        off_l += S[bl & ~near].sum()
        used += 1
    return 10 * np.log10(on_e / off_e), 10 * np.log10(on_l / off_l), used


# run inside the work folder (the chain files of v2 and v3)
for raw, chain in (("02_Main1.wav", ["02_Main1_rt.wav", "m1_2.wav", "m1_9.wav", "m1_mid.wav", "m1_10.wav"]),
                   ("03_Main2.wav", ["03_Main2_rt.wav", "m2_2.wav", "m2_9.wav", "m2_mid.wav", "m2_10.wav"])):
    t0, t1 = 40.0, 100.0
    f0 = frames_and_f0(raw, t0, t1)
    print(f"{raw}: harmonics-to-noise 1-6 kHz | below 1 kHz (dB; higher = cleaner)")
    for p in [raw] + chain:
        a, b, u = hnr(p, f0, t0, t1)
        print(f"   {p:18s} {a:6.2f} | {b:6.2f}   ({u} sustained frames)")

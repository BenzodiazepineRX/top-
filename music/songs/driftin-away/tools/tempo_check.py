"""Re-run the self-match with the true envelope rate (44100/22 = 2004.5 Hz, the first run assumed 2000),
then find the main-beat (quarter-note) grid from the strongest low and mid hits."""
import os
import sys
import numpy as np
from scipy.signal import butter, sosfiltfilt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt
D = os.path.join(os.path.abspath(os.environ.get("DRIFT_WORK", ".")), "")  # work folder, absolute
sr = 44100
beat, _ = dt.read(D + "01_Beat.wav")
bm = beat.mean(axis=1)
step = 22
rate = sr / step
def flux(sig):
    e = np.abs(sig); k = int(0.005 * sr)
    e = np.convolve(e, np.ones(k) / k, mode="same")[::step]
    return np.maximum(np.diff(np.log(e + 1e-6), prepend=0), 0)
low = flux(sosfiltfilt(butter(2, 150, "low", fs=sr, output="sos"), bm))
mid = flux(sosfiltfilt(butter(2, [150, 2500], "band", fs=sr, output="sos"), bm))
high = flux(sosfiltfilt(butter(2, 5000, "high", fs=sr, output="sos"), bm))
on = low + mid + high
print("self-match with the true envelope rate:")
for bars in (8, 16, 32, 48):
    best = None
    for bpm in np.arange(149.0, 151.0, 0.002):
        L = int(round(bars * 240 / bpm * rate))
        a, b = on[:-L], on[L:]
        c = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        if best is None or c > best[0]:
            best = (c, bpm)
    L = int(round(bars * 240 / 150 * rate)); a, b = on[:-L], on[L:]
    c150 = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    print(f"   {bars:2d} bars: best {best[1]:.3f} BPM (similarity {best[0]:.3f}); at 150.000: {c150:.3f}")
# main-beat grid: phase of the onset strength at the quarter note, per band
Q = 0.4
t = np.arange(len(on)) / rate
for lab, e in (("kick (<150 Hz)", low), ("snare/body (150-2500 Hz)", mid), ("hats (>5 kHz)", high)):
    w = e * (e > np.percentile(e, 99))
    for P, pl in ((Q, "1/4"), (Q / 2, "1/8"), (Q / 3, "1/8 triplet"), (Q / 4, "1/16")):
        z = np.sum(w * np.exp(2j * np.pi * t / P)) / np.sum(w)
        print(f"   {lab:25s} {pl:11s} R {abs(z):.2f}  phase {((np.angle(z) % (2*np.pi)) / (2*np.pi) * P) * 1000:6.1f} ms")

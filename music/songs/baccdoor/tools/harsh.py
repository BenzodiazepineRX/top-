"""Where does the harshness come from? For each step of the lead chains (and the same stage of Driftin' Away's
lead, which the owner did not call harsh): over sung frames only, the energy of
  harsh 2-5 kHz and fizz 5-12 kHz relative to the body 200-1500 Hz (dB),
  grit: spectral flatness 3-8 kHz (0 = clean harmonics, 1 = noise-like),
  added distortion: energy between the harmonics vs on them, 1-5 kHz (dB)."""
import sys
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__))); import bacc_lib as L
sr = 44100
N = 4096
f = np.fft.rfftfreq(N, 1 / sr)
def bands(path, t0=40, t1=100):
    x, _ = L.dt.read(path); m = L.mono(x)[int(t0 * sr):int(t1 * sr)]
    hop = 2048; win = np.hanning(N)
    rows = []
    for i in range(0, len(m) - N, hop):
        w = m[i:i + N] * win
        if np.sqrt(np.mean(w ** 2)) < 10 ** (-45 / 20) * np.sqrt(np.mean(m ** 2)) * 10 ** (25 / 20) * 0 + 1e-4: pass
        S = np.abs(np.fft.rfft(w)) ** 2
        rows.append(S)
    S = np.array(rows)
    e = S.sum(1); keep = e > np.percentile(e, 50)           # the louder half of frames = singing
    S = S[keep]
    def band(a, b): return S[:, (f >= a) & (f < b)].sum(1)
    body, harsh, fizz = band(200, 1500), band(2000, 5000), band(5000, 12000)
    sel = (f >= 3000) & (f < 8000)
    flat = np.exp(np.mean(np.log(S[:, sel] + 1e-20), 1)) / (np.mean(S[:, sel], 1) + 1e-20)
    return (10 * np.log10(harsh.mean() / body.mean()), 10 * np.log10(fizz.mean() / body.mean()), float(np.median(flat)))
print(f"{'file':34s} harsh  fizz   grit")
for p in ("02_Main1.wav", "02_Main1_rt.wav", "m1_2.wav", "m1_4.wav", "m1_5.wav", "m1_6.wav", "m1_7.wav", "m1_8.wav",
          "03_Main2.wav", "03_Main2_rt.wav", "m2_7.wav", "m2_8.wav", "stem_v1_mains.wav"):
    h, z, g = bands(p)
    print(f"{p:34s} {h:+5.1f} {z:+5.1f}  {g:.3f}")
print("Driftin' Away lead for comparison (owner did not call it harsh):")
for p in ("../drift/02_Lead.wav", "../drift/l_8.wav"):
    h, z, g = bands(p, 30, 75)
    print(f"{p:34s} {h:+5.1f} {z:+5.1f}  {g:.3f}")

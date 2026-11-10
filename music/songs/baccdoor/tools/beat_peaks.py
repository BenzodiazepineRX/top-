"""Beat spike control for Baccdoor (v1). The master limiter dipped up to 5.9 dB on the beat's snare/kick hits; the
peaks sat in 120 Hz-2 kHz (the 808 below 120 Hz was 6-10 dB lower). Zero-phase split into low (<120 Hz), mid
(120 Hz-2 kHz) and high (rest), which add back exactly to the original; a 5 ms lookahead peak limiter on the mid band
only (ceiling = that band's loudness + 12 dB, 60 ms release). The 808 and the top are untouched. Writes beat_pk.wav."""
import os
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc_lib as L
D = os.path.join(os.path.abspath(os.environ.get("BACC_WORK", ".")), "")
sr = L.sr
x, _ = L.dt.read(D + "01_Beat.wav")
low = L.sosfiltfilt(L.butter(2, 120, "low", fs=sr, output="sos"), x, axis=0)
rest = x - low
mid = L.sosfiltfilt(L.butter(2, 2000, "low", fs=sr, output="sos"), rest, axis=0)
high = rest - mid
lm = L.loud(mid, 30.3, 183.8, False)
mid2, st = L.peak_catch(mid, lm + 12.0)
y = low + mid2 + high
L.dt.write(D + "beat_pk.wav", y, sr)
def rms(z): return 10 * np.log10(np.mean(z ** 2) + 1e-20)
s0, s1 = int(30.3 * sr), int(183.8 * sr)
st.update({"band": "120-2000 Hz", "band_loudness_lufs": round(lm, 2),
           "reconstruction_error_db": round(20 * np.log10(np.abs(low + mid + high - x).max() + 1e-15), 1),
           "beat_peak_db": [round(20 * np.log10(np.abs(x).max()), 2), round(20 * np.log10(np.abs(y).max()), 2)],
           "beat_loudness_lufs": [round(L.loud(x, 30.3, 183.8, False), 2), round(L.loud(y, 30.3, 183.8, False), 2)],
           "low_band_change_db": round(rms(L.sosfiltfilt(L.butter(4, 120, "low", fs=sr, output="sos"), y[s0:s1], axis=0)) - rms(L.sosfiltfilt(L.butter(4, 120, "low", fs=sr, output="sos"), x[s0:s1], axis=0)), 2),
           "mid_band_change_db": round(rms(mid2[s0:s1]) - rms(mid[s0:s1]), 2)})
json.dump(st, open(D + "beat_peaks.json", "w"), indent=1)
print(json.dumps(st))

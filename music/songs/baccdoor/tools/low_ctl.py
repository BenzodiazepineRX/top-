"""808 peak control for the Baccdoor beat: zero-phase split at 120 Hz (low = zero-phase low-pass, rest = x - low,
so low + rest is exactly the original), peak compressor on the low part only (4:1 above -14 dBFS, 5 ms attack,
100 ms release), no makeup. Writes beat_lc.wav and prints what changed."""
import os
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc_lib as L
D = os.path.join(os.path.abspath(os.environ.get("BACC_WORK", ".")), "")
sr = L.sr
x, _ = L.dt.read(D + "01_Beat.wav")
lo = L.sosfiltfilt(L.butter(2, 120, "low", fs=sr, output="sos"), x, axis=0)
rest = x - lo
blk = int(0.001 * sr)
a = np.abs(lo).max(1)
nb = len(a) // blk
lv = 20 * np.log10(a[:nb * blk].reshape(nb, blk).max(1) + 1e-12)
THR, RATIO, KNEE, MAKEUP = -14.0, 4.0, 4.0, 2.0
over = lv - THR
gr = np.where(over <= -KNEE / 2, 0.0, np.where(over >= KNEE / 2, over * (1 - 1 / RATIO), (1 - 1 / RATIO) * (over + KNEE / 2) ** 2 / (2 * KNEE)))
grs = L.dt.ar_smooth(gr, 0.001, 5.0, 100.0)          # gain reduction rises fast (attack 5 ms), falls slow (100 ms)
curve = np.interp(np.arange(len(a)), (np.arange(nb) + 0.5) * blk, grs)
y = lo * (10 ** ((MAKEUP - curve) / 20))[:, None] + rest
L.dt.write(D + "beat_lc.wav", y, sr)
def pk(z): return 20 * np.log10(np.abs(z).max() + 1e-12)
def rms(z): return 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-12)
lo2 = lo * (10 ** ((MAKEUP - curve) / 20))[:, None]
st = {"makeup_db": MAKEUP, "threshold_dbfs": THR, "ratio": RATIO, "attack_ms": 5, "release_ms": 100, "split_hz": 120,
      "beat_peak_db": [round(pk(x), 2), round(pk(y), 2)], "low_peak_db": [round(pk(lo), 2), round(pk(lo2), 2)],
      "low_rms_db": [round(rms(lo), 2), round(rms(lo2), 2)], "rest_unchanged": bool(np.allclose(y - lo2, rest)),
      "max_gr_db": round(float(curve.max()), 1), "pct_time_over_1db": round(float((curve > 1).mean() * 100), 1),
      "reconstruction_error_db": round(pk(lo + rest - x), 1)}
json.dump(st, open(D + "low_ctl.json", "w"), indent=1)
print(json.dumps(st))

"""Retune check: pitch moved by the planned cents and the new tuning centre sits on the beat's (-6.7 c from 440)."""
import os
import json, sys
import numpy as np
sys.argv = ["x"]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pitch_layers.py")).read().split("for nm in (")[0]
ns = {}; exec(compile(src, "pitch_layers_funcs", "exec"), ns)
dt, f0_track = ns["dt"], ns["f0_track"]; sr = 44100
plan = json.load(open("retune.json"))
for name, p in plan.items():
    a, _ = dt.read(name + ".wav"); b, _ = dt.read(name + "_rt.wav")
    s0 = int(40 * sr); s1 = int(100 * sr)
    fa, _ = f0_track(a[s0:s1]); fb, _ = f0_track(b[s0:s1])
    v = ~np.isnan(fa) & ~np.isnan(fb)
    d = 1200 * np.log2(fb[v] / fa[v])
    nb = 12 * np.log2(fb[v] / 440) + 69; cd = (nb - np.round(nb)) * 100
    centre = np.angle(np.mean(np.exp(2j * np.pi * cd / 100))) / (2 * np.pi) * 100
    print(f"{name}: moved {np.median(d):+.2f} cents (plan {p['cents']:+.1f}); tuning centre now {centre:+.1f} c from 440 (beat -6.7); timing re-align residual {p['after_realign_samples']} samples")

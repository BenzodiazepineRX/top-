"""Line the vocal files up with the beat: remove the slow slide measured by drift_map.py. Each voice is read a few ms ahead or behind
(y(t) = x(t + offset(t))), a smooth tape-speed change of at most about 0.4% (about 7 cents, below hearing). Word timings move with it."""
import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly
SR=44100; m=json.load(open("align/drift_map.json")); T=np.array(m["times"]); O=np.array(m["offset_ms"])/1000
off=lambda t: np.interp(t, T, O)                                         # held at the end values outside the mapped span
for name in ("Lead 1","Lead 2","Background lead","Background lead 2"):
    x,sr=sf.read(f"src/{name}.wav",always_2d=True); assert sr==SR; n=len(x); t=np.arange(n)/SR
    src=(t+off(t))*SR*4; y=np.zeros_like(x)
    for c in range(x.shape[1]):
        xu=resample_poly(x[:,c],4,1); y[:,c]=np.interp(src, np.arange(len(xu)), xu, left=0, right=0)
    sf.write(f"src_aligned/{name}.wav", y, SR, subtype="PCM_24")
    sp=np.gradient(off(t[::441]))/0.01
    print(f"{name}: moved {1000*off(0):+.0f} ms at the start .. {1000*off(t[-1]):+.0f} ms at the end; largest speed change {100*np.abs(sp).max():.2f}%")
for k in ("L1","L2","B1","B2"):
    w=json.load(open(f"words/{k}.json"))
    for x in w: x["s"]=round(x["s"]-float(off(x["s"])),3); x["e"]=round(x["e"]-float(off(x["e"])),3)
    json.dump(w, open(f"words_aligned/{k}.json","w"))

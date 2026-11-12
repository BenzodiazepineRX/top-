"""How abruptly does each vocal file cut to / restart from the digital silence the recording app leaves between lines?
(Cuts quieter than -45 dBFS cannot click.)   usage: python3 silence_edges.py   (run from a folder holding src/)"""
import numpy as np, soundfile as sf
SR=44100
for name in ("Lead 1","Lead 2","Background lead","Background lead 2"):
    x,_=sf.read(f"src/{name}.wav",always_2d=True); x=x.mean(1); z=(x==0); d=np.diff(np.r_[0,z.astype(int),0]); s=np.where(d==1)[0]; e=np.where(d==-1)[0]
    bd=[(a,b) for a,b in zip(s,e) if b-a>=int(0.02*SR)]
    ends=[20*np.log10(np.abs(x[a-int(0.004*SR):a]).max()+1e-9) for a,b in bd if a>int(0.01*SR)]
    print(f"{name}: {len(bd)} stretches of digital silence; level of the last 4 ms before a cut: median {np.median(ends):.0f}, loudest {max(ends):.0f} dBFS; louder than -45: {sum(v>-45 for v in ends)}")

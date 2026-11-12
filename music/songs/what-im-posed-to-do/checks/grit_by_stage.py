import sys; sys.path.insert(0,"diag"); sys.path.insert(0,".")
import numpy as np, soundfile as sf
from harsh_ours import bands, ld
from v3lib import praat_pitch
SR=44100; N=4096; f=np.fft.rfftfreq(N,1/SR); win=np.hanning(N)
def voiced_grit(x,t0=45,t1=130):
    """grit and fizz on frames where the voice has a steady pitch (selection does not depend on loudness)"""
    seg=x[int(t0*SR):int(t1*SR)]; ts,f0=praat_pitch(seg,SR,0.01); rows=[]
    for i in range(0,len(seg)-N,2048):
        c=(i+N/2)/SR; k=int(c/0.01)
        if k<3 or k+3>=len(f0): continue
        w=f0[k-3:k+4]
        if np.isnan(w).any(): continue
        if np.log(np.nanmax(w)/np.nanmin(w))>0.05: continue          # steady pitch only
        S=np.abs(np.fft.rfft(seg[i:i+N]*win))**2; rows.append(S)
    S=np.array(rows); e=S.sum(1); S=S[e>np.percentile(e,20)]
    b=lambda a,c: S[:,(f>=a)&(f<c)].sum(1); sel=(f>=3000)&(f<8000)
    flat=np.exp(np.mean(np.log(S[:,sel]+1e-20),1))/(np.mean(S[:,sel],1)+1e-20)
    return 10*np.log10(b(5000,12000).mean()/b(200,1500).mean()), float(np.median(flat)), len(S)
W="work_v3"   # the folder holding the stage files {k}_1.wav .. {k}_6.wav
for k,name in (("L1","Lead 1"),("L2","Lead 2")):
    print(f"--- {k}   (louder-half frames: harsh fizz grit)   |  (steady-pitch frames: fizz grit n)")
    stages=[("raw",f"src/{name}.wav"),("tuned v3 (0.6)",f"{W}/{k}_nat_0.6.wav"),("1 gain",f"{W}/{k}_1.wav"),("2 high-pass",f"{W}/{k}_2.wav"),("3 dyn EQ 3k",f"{W}/{k}_3.wav"),
            ("4 EQ+2:1 comp",f"{W}/{k}_4.wav"),("5 de-esser",f"{W}/{k}_5.wav"),("6 leveler",f"{W}/{k}_6.wav")]
    for lab,p in stages:
        x=ld(p); h,z,g=bands(x); vz,vg,n=voiced_grit(x)
        print(f"  {lab:16s} {h:+5.1f} {z:+5.1f} {g:.3f}   |  {vz:+5.1f} {vg:.3f} {n}")

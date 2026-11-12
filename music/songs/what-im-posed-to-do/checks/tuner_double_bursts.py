import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, find_peaks
SR=44100
def env(x):
    h=sosfiltfilt(butter(4,[2000,8000],"band",fs=SR,output="sos"),x); e=np.abs(h); 
    k=int(0.001*SR); return np.convolve(e,np.ones(k)/k,"same")[::k]   # 1 ms steps
def doubles(x):
    e=env(x); d=np.clip(np.diff(e,prepend=e[0]),0,None); th=np.percentile(d[d>0],99)
    pk,_=find_peaks(d,height=th,distance=2); out=[]
    for i in range(len(pk)-1):
        gap=pk[i+1]-pk[i]
        if 4<=gap<=16 and d[pk[i+1]]>0.5*d[pk[i]]: out.append((pk[i]/1000, gap))
    return len(pk), out
for k,name in (("L1","Lead 1"),("L2","Lead 2")):
    raw=sf.read(f"src/{name}.wav",always_2d=True)[0].mean(1)
    for tag,fn in (("v2 tuned",f"work_v2/{k}_tuned_0.6.wav"),("v3 tuned",f"work_v3b/{k}_nat_0.6.wav")):
        y=sf.read(fn,always_2d=True)[0].mean(1)[:len(raw)]
        a,b=int(40*SR),int(175*SR)
        n0,d0=doubles(raw[a:b]); n1,d1=doubles(y[a:b])
        # clicks: sharpest 2nd difference relative to local level
        dd=lambda z: np.abs(np.diff(z[a:b],2))
        print(f"{k} {tag}: strong HF onsets raw {n0} -> {n1}; close pairs (4-16 ms apart) raw {len(d0)} -> {len(d1)}; sharpest 2nd-difference raw {dd(raw).max():.4f} -> {dd(y).max():.4f}")
        new=[x for x in d1 if not any(abs(x[0]-r[0])<0.02 for r in d0)]
        if new: print("     new close pairs at (s):", [round(x[0]+40,2) for x in new][:12])

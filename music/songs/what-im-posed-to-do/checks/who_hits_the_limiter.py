import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100; W="work_v2"; Q=60/135; BAR=4*Q; G0=0.004; bar=lambda n:G0+(n-1)*BAR
rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
beat=rd("beat.wav"); lead=rd("lead.wav"); mix=rd("mix_trim.wav"); n=len(mix)
i,j=int(bar(38)*SR),int(bar(50)*SR)
def lp(x,f): return sosfiltfilt(butter(4,f,"low",fs=SR,output="sos"),x,axis=0)
bm=beat[i:j]; lo=lp(bm,150); mid=lp(bm,600)-lo; hi=bm-lo-mid
pk=lambda x: 20*np.log10(np.abs(x).max()+1e-9); rms=lambda x: 10*np.log10(np.mean(x**2)+1e-15)
print("beat bars 38-49: peak %.1f dBFS, RMS %.1f | below 150 Hz: peak %.1f RMS %.1f | 150-600: peak %.1f RMS %.1f | above 600: peak %.1f RMS %.1f"%(pk(bm),rms(bm),pk(lo),rms(lo),pk(mid),rms(mid),pk(hi),rms(hi)))
# at the mix's top peaks, who is contributing?
m=mix[i:j]; a=np.abs(m).max(1); idx=np.argsort(a)[::-1]; chosen=[]
for q in idx:
    if all(abs(q-c)>SR*0.05 for c in chosen): chosen.append(q)
    if len(chosen)==40: break
L=lead[i:j]; con={"beat<150":[], "beat150-600":[], "beat>600":[], "lead":[]}
for q in chosen:
    ch=int(np.argmax(np.abs(m[q]))); s=np.sign(m[q,ch])
    con["beat<150"].append(s*lo[q,ch]); con["beat150-600"].append(s*mid[q,ch]); con["beat>600"].append(s*hi[q,ch]); con["lead"].append(s*L[q,ch])
tot=np.abs(m[chosen]).max(1).mean()
print("top 40 mix peaks in bars 38-49 (mean %.2f = %.1f dBFS): share from "%(tot,20*np.log10(tot))+", ".join(f"{k} {100*np.mean(v)/tot:.0f}%" for k,v in con.items()))
# distribution of the mix's peaks over 5 ms blocks relative to RMS
b=int(0.005*SR); k=len(m)//b; p=np.abs(m[:k*b]).max(1).reshape(k,b).max(1); r=np.sqrt(np.mean(m**2))
for th in (6,8,10,12,14): print("   5 ms blocks whose peak is more than %d dB over the section RMS: %.1f%%"%(th,100*np.mean(20*np.log10(p/r)>th)))
# lead alone: which band its top peaks sit in
for kk in ("L1","L2"):
    x=rd(f"{kk}_6.wav").mean(1); act=np.abs(x)>1e-3; r=np.sqrt(np.mean(x[act]**2)); a=np.abs(x)
    lo_=lp(x,200); 
    idx=np.argsort(a)[::-1][:2000]; print(f"{kk}: RMS {20*np.log10(r):.1f} dBFS, peak {20*np.log10(a.max()):.1f}; share of top-2000-sample peaks coming from below 200 Hz: {100*np.mean(np.abs(lo_[idx])/a[idx]):.0f}%; samples more than 12 dB over RMS: {100*np.mean(a[act]>r*4):.2f}% of singing, more than 15 dB: {100*np.mean(a[act]>r*5.6):.3f}%")

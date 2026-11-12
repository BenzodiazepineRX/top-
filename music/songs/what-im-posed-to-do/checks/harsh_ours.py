# Baccdoor's harsh.py measure (4096-sample frames, louder half = singing): harsh 2-5 kHz and fizz 5-12 kHz relative to the
# body 200-1500 Hz (dB); grit = median spectral flatness 3-8 kHz (0 = clean harmonics, 1 = noise-like).
import numpy as np, soundfile as sf, sys
SR=44100; N=4096; f=np.fft.rfftfreq(N,1/SR); win=np.hanning(N)
def bands(x,t0=45,t1=130):
    m=x[int(t0*SR):int(t1*SR)]; S=np.array([np.abs(np.fft.rfft(m[i:i+N]*win))**2 for i in range(0,len(m)-N,2048)])
    e=S.sum(1); S=S[e>np.percentile(e,50)]
    b=lambda a,c: S[:,(f>=a)&(f<c)].sum(1)
    body,harsh,fizz=b(200,1500),b(2000,5000),b(5000,12000); sel=(f>=3000)&(f<8000)
    flat=np.exp(np.mean(np.log(S[:,sel]+1e-20),1))/(np.mean(S[:,sel],1)+1e-20)
    return 10*np.log10(harsh.mean()/body.mean()),10*np.log10(fizz.mean()/body.mean()),float(np.median(flat))
def ld(p): return sf.read(p,always_2d=True)[0].mean(1)
if __name__=="__main__":
    print(f"{'file':44s} harsh   fizz   grit")
    for k,name in (("L1","Lead 1"),("L2","Lead 2")):
        for lab,p in ((f"{k} raw",f"src/{name}.wav"),(f"{k} v2 after chain",f"work_v2/{k}_6.wav"),(f"{k} v3 after chain",f"work_v3b/{k}_6.wav")):
            h,z,g=bands(ld(p)); print(f"{lab:44s} {h:+5.1f}  {z:+5.1f}  {g:.3f}")
    print("anchors from Baccdoor notes (same measure): Driftin' Away lead grit 0.032; Baccdoor v3 leads fizz -34.4 grit 0.013 (Nearly PERFECT);")
    print("   Baccdoor v2 leads harsh -13.0 fizz -29.9 grit 0.048 (still harsh/scratchy); v1 harsh -10.6 fizz -19.5 grit 0.065 (very scratchy)")

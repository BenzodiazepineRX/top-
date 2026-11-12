# usage: limtest.py MIX.wav gain_dB release_ms  -> how the limiter moves a quiet 3 kHz test tone (i.e. the vocal range)
import numpy as np, soundfile as sf, sys, subprocess, os
from scipy.signal import butter, sosfiltfilt, hilbert, welch
SR=44100; Q=60/135; BAR=4*Q; G0=0.004; bar=lambda n:G0+(n-1)*BAR
mixp,gain,rel=sys.argv[1],float(sys.argv[2]),sys.argv[3]; tag=f"diag/lt_{os.getpid()}"
mix,_=sf.read(mixp,always_2d=True); n=len(mix); t=np.arange(n)/SR; probe=10**(-46/20)*np.sin(2*np.pi*3000*t)
sf.write(tag+"_p.wav",(mix+probe[:,None]).astype(np.float32),SR,subtype="FLOAT")
fg=f"volume={gain:.3f}dB,aresample=176400:resampler=soxr,alimiter=limit=-1.200dB:attack=5.0:release={rel}:level=disabled:latency=true,aresample=44100:resampler=soxr"
for src,dst in ((mixp,tag+"_a.wav"),(tag+"_p.wav",tag+"_b.wav")): subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-af",fg,"-c:a","pcm_f32le",dst],check=True)
a,_=sf.read(tag+"_a.wav",always_2d=True); b,_=sf.read(tag+"_b.wav",always_2d=True); m=min(len(a),len(b))
d=sosfiltfilt(butter(4,[2000,4000],"band",fs=SR,output="sos"),(b[:m]-a[:m]).mean(1)); g=20*np.log10(np.abs(hilbert(d))/(10**(-46/20)*10**(gain/20))+1e-9)
import pyloudnorm; L=pyloudnorm.Meter(SR).integrated_loudness(a)
out=[]
for name,x,y in [("38-49",38,50),("114-129",114,130),("50-65 soft",50,66)]:
    i,j=int(bar(x)*SR),int(bar(y)*SR); s=g[i:j]; lin=10**(s/20); f,p=welch(lin-lin.mean(),SR,nperseg=1<<15)
    bd=lambda lo,hi: 100*np.sqrt(np.trapezoid(p[(f>=lo)&(f<hi)],f[(f>=lo)&(f<hi)]))/lin.mean()
    dx=np.abs(s[220:]-s[:-220]); jolts=np.sum(np.diff((dx>2).astype(int))==1)/((j-i)/SR); j1=np.sum(np.diff((dx>1).astype(int))==1)/((j-i)/SR)
    out.append(f"bars {name}: p90 {-np.percentile(s,10):.1f} p99 {-np.percentile(s,1):.1f} deepest {-s.min():.1f} dB; jolts>2dB/5ms {jolts:.1f}/s, >1dB {j1:.1f}/s; wobble 2-20Hz {bd(2,20):.1f}% 20-300Hz {bd(20,300):.2f}%")
print(f"gain {gain:+.1f} dB, release {rel} ms -> {L:.1f} LUFS | "+" | ".join(out))
for e in ("_p.wav","_a.wav","_b.wav"): os.remove(tag+e)

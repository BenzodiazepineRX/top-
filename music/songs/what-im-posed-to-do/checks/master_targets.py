import sys; sys.path.insert(0,".")
import numpy as np, soundfile as sf, pyloudnorm, json
from v3lib import hold_limiter
SR=44100; Q=60/135; BAR=4*Q; G0=0.004; bar=lambda n:G0+(n-1)*BAR; M=pyloudnorm.Meter(SR)
for W in sys.argv[1:]:
    mix=sf.read(f"{W}/mix_trim.wav",always_2d=True)[0]; L0=M.integrated_loudness(mix); d=json.load(open(f"{W}/build_log.json")); print(f"{W}: pre-limiter mix {L0:.1f} LUFS; leads gain {d['levels']['lead_gain_dB']} dB")
    for tgt in (-14.0,-14.5,-15.0):
        g=tgt-L0+0.3
        for it in range(4):
            y,gd=hold_limiter(mix*10**(g/20),10**(-1.5/20),SR,look=0.008,hold=0.030,release_db_per_s=30.0); L=M.integrated_loudness(y)
            if abs(tgt-L)<0.03: break
            g+=tgt-L
        t=np.arange(len(gd))*0.001; out=[]
        for nm,a,c in [("38-49",38,50),("66-81",66,82),("114-129",114,130)]:
            s=gd[(t>=bar(a))&(t<bar(c))]; d5=np.abs(s[5:]-s[:-5]); out.append(f"{nm}: p90 {-np.percentile(s,10):.1f} p99 {-np.percentile(s,1):.1f} deep {-s.min():.1f} >1dB {100*np.mean(s<-1):.0f}% jolts {np.sum(np.diff((d5>2).astype(int))==1)/(len(s)/1000):.2f}/s")
        print(f"   {tgt:+.1f} LUFS (gain {g:+.1f}): "+" | ".join(out),flush=True)

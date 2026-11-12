import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
sys.path.insert(0,"diag")
SR=44100; H=SR//1000; W=sys.argv[1]; picks=[float(x) for x in sys.argv[2:]]
def env_db(x,win_ms):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos"); rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
beat=rd("beat.wav").mean(1); lead=rd("lead.wav").mean(1); bg=rd("bg.wav").mean(1); thr=rd("throws_raw.wav").mean(1); n=len(thr)
bb=sosfiltfilt(SOSB,beat[:n]); lb=sosfiltfilt(SOSB,lead[:n]+bg[:n]); eb=sosfiltfilt(SOSB,thr)
Eb,Lb,Bb,Mb=env_db(eb,20),env_db(lb,20),env_db(bb,20),env_db(bb+lb,20)
for c in json.load(open(f"{W}/throw_cues.json")):
    if not any(abs(c["line_end_s"]-p)<0.06 for p in picks): continue
    t0=c["first_echo_s"]; j=int(t0*1000); bar=(t0-0.004)/(4*60/135)
    print(f"\n{c['singer']} line end {c['line_end_s']}  words '{c['words']}'  echo starts {t0:.3f} s = bar {int(bar)+1} + {(bar-int(bar))*4:.2f} beats; copy {c['copy_len_s']} s, delay {c['delay_note']}")
    print("   t(ms)  echo  live-lead  beat   all-live | echo-minus-live")
    for k in range(-40,int(min(c['copy_len_s'],1.2)*1000)+100,60):
        print(f"  {k:6d} {Eb[j+k]:6.1f} {Lb[j+k]:8.1f} {Bb[j+k]:7.1f} {Mb[j+k]:8.1f} | {Eb[j+k]-Mb[j+k]:+6.1f}")

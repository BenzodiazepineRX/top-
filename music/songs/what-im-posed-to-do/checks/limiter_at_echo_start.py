"""Does the final limiter pull the mix down just as an echo starts, so that the echo seems to fade in?  Gain applied by the master stage (master/mix_trim in 400-3600 Hz, 5 ms RMS steps,
relative to the song's median gain) averaged over the first 100 ms of each echo's sound and over the next 300 ms."""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100
def env_db(x,win_ms):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos")
for W in sys.argv[1:]:
    mix=sf.read(f"{W}/mix_trim.wav",always_2d=True)[0].mean(1); mas=sf.read(f"{W}/master.wav",always_2d=True)[0].mean(1); n=min(len(mix),len(mas))
    g=env_db(sosfiltfilt(SOSB,mas[:n]),10)-env_db(sosfiltfilt(SOSB,mix[:n]),10); thr=np.load("/dev/null") if False else None
    ok=env_db(sosfiltfilt(SOSB,mix[:n]),10)>-60; base=np.median(g[ok]); red=g-base   # negative = limiter pulling down
    thrb=sosfiltfilt(SOSB,sf.read(f"{W}/throws_raw.wav",always_2d=True)[0].mean(1)); E=env_db(thrb,6); rows=[]
    for c in json.load(open(f"{W}/throw_cues.json")):
        L=c["copy_len_s"]; j0=int(round(c["first_echo_s"]*1000)); m=int(min(L,1.6)*1000); e=E[j0-10:j0+m+40]; epk=np.percentile(e[10:10+m],90); on=j0-10+10+int(np.argmax(e[10:]>epk-30))
        a=np.mean(red[on:on+100]); b=np.mean(red[on+100:on+400]); rows.append((a,b,a-b,c["line_end_s"],c["words"]))
    r=np.array([x[2] for x in rows]); a=np.array([x[0] for x in rows])
    print(f"{W}: limiter gain during the first 100 ms of an echo's sound: median {np.median(a):+.2f} dB (relative to the song's median); lower than during the next 300 ms by: median {np.median(-r):+.2f} dB, worst {(-r).max():+.1f} dB; echoes whose start is pulled down more than 1.5 dB more than their middle: {int(np.sum(-r>1.5))} of {len(rows)}")

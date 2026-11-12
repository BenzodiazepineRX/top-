"""Is the echo's start as strong as the original word's start?  For each cue, in 400-3600 Hz: the level of the first 100 ms after the first sound (30 dB under the loud part),
measured against the loud part, for the original words (voice_*.wav) and for the echo (first repeat). delta = echo - original (positive: the echo comes in more strongly than the word did)."""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100
def env_db(x,win_ms):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos"); W=sys.argv[1]; rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
thr=rd("throws_raw.wav").mean(1); n=len(thr); eb=sosfiltfilt(SOSB,thr); vb={k:sosfiltfilt(SOSB,rd(f"voice_{k}.wav").mean(1)[:n]) for k in ("L1","L2","B1","B2")}
def start(e,L):
    m=int(min(L,1.6)*1000); pk=np.percentile(e[10:10+m],90); on=10+int(np.argmax(e[10:]>pk-30)); return np.mean(e[on:on+100])-pk, np.mean(e[on:on+50])-pk
rows=[]
for c in json.load(open(f"{W}/throw_cues.json")):
    L=c["copy_len_s"]; a=int(c["words_from_s"]*SR); p=int(c["first_echo_s"]*SR); m=int(min(L,1.6)*SR)
    ed=env_db(vb[c["singer"]][a-int(0.01*SR):a+m+int(0.05*SR)],6); ee=env_db(eb[p-int(0.01*SR):p+m+int(0.05*SR)],6)
    d100,d50=start(ed,L); e100,e50=start(ee,L); rows.append((e100-d100,e50-d50,d100,e100,c["line_end_s"],c["singer"],c["words"]))
dl=np.array([r[0] for r in rows]); d5=np.array([r[1] for r in rows])
print(f"{W}: echo start (first 100 ms) minus the original word's start: median {np.median(dl):+.1f} dB; first 50 ms: median {np.median(d5):+.1f} dB; echo weaker than the original word at its start by more than 2 dB: {int(np.sum(dl<-2))} of {len(rows)}; stronger by more than 2 dB: {int(np.sum(dl>2))}")
print("   original word's own start vs its loud part: median %+.1f dB; echo's: median %+.1f dB"%(np.median([r[2] for r in rows]),np.median([r[3] for r in rows])))
bad=sorted(rows)[:6]; print("   weakest relative to the original:",[(round(r[0],1),r[4],r[6]) for r in bad])

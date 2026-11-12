"""For the echoes whose first 100 ms is far under their own plateau against the live mix: is it the echo's own soft start, or the live mix surging at that moment?"""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100
def env_db(x,win_ms):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos"); W=sys.argv[1]; rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
thr=rd("throws_raw.wav").mean(1); n=len(thr); E=env_db(sosfiltfilt(SOSB,thr),6); M=env_db(sosfiltfilt(SOSB,rd("beat.wav").mean(1)[:n]+rd("lead.wav").mean(1)[:n]+rd("bg.wav").mean(1)[:n]),20)
rows=[]
for c in json.load(open(f"{W}/throw_cues.json")):
    L=c["copy_len_s"]; j0=int(round(c["first_echo_s"]*1000)); m=int(min(L,1.6)*1000); e=E[j0-10:j0+m+40]; mk=M[j0-10:j0+m+40]; epk=np.percentile(e[10:10+m],90)
    on=10+int(np.argmax(e[10:]>epk-30)); snr=e-mk; loud=e>epk-12; loud[:10]=False; pl=np.median(snr[loud])
    s100=np.mean(snr[on:on+100]); own=np.mean(e[on:on+100])-epk; mask_surge=np.mean(mk[on:on+100])-np.median(mk[loud])
    rows.append((pl-s100,own,mask_surge,pl,c["line_end_s"],c["singer"],c["words"],c["lift_max_dB"]))
rows.sort(reverse=True); print("deficit = first-100-ms SNR is this far under the plateau SNR; own = echo's first 100 ms vs its own loud part; surge = how much louder the live mix is in that first 100 ms than during the echo's loud part")
print("deficit  own   surge  plateauSNR  time   who  words (lift max)")
for r in rows[:16]: print(f"  {r[0]:5.1f} {r[1]:+5.1f} {r[2]:+5.1f}   {r[3]:+5.1f}   {r[4]:7.2f} {r[5]} {r[6]} ({r[7]})")
d=np.array([r[0] for r in rows]); own=np.array([r[1] for r in rows]); sg=np.array([r[2] for r in rows])
print("all echoes: deficit>4 dB:",int(np.sum(d>4)),"| of those, own start more than 4 dB under its loud part:",int(np.sum((d>4)&(own<-4))),"| live mix surging by more than 3 dB:",int(np.sum((d>4)&(sg>3))),"| both:",int(np.sum((d>4)&(own<-4)&(sg>3))))

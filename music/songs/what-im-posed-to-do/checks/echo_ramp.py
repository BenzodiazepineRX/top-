"""How long does an echo take to reach its own normal presence over the live mix? (v3 vs v4, same measure)
SNR(t) = echo level - live-mix level in 400-3600 Hz, 1 ms steps. plateau = median SNR where the echo is within 12 dB of its loud part.
ramp = ms from the echo's first sound (30 dB under its loud part) until SNR is within 3 dB of the plateau.
dip100 = how far under the plateau the SNR is on average during the first 100 ms from that first sound."""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100; H=SR//1000
def env_db(x,win_ms):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos")
def run(W):
    rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
    beat=rd("beat.wav").mean(1); lead=rd("lead.wav").mean(1); bg=rd("bg.wav").mean(1); thr=rd("throws_raw.wav").mean(1); n=len(thr)
    live=sosfiltfilt(SOSB,beat[:n]+lead[:n]+bg[:n]); eb=sosfiltfilt(SOSB,thr); E=env_db(eb,6); M=env_db(live,20)
    out=[]
    for c in json.load(open(f"{W}/throw_cues.json")):
        L=c["copy_len_s"]; t0=c["first_echo_s"]; j0=int(t0*1000); m=int(min(L,1.6)*1000)
        e=E[j0-10:j0+m+40]; mk=M[j0-10:j0+m+40]; epk=np.percentile(e[10:10+m],90)
        on=int(np.argmax(e[10:]>epk-30)); snr=e-mk; loud=e>epk-12; loud[:10]=False
        pl=np.median(snr[loud]); idx=np.where((e>epk-20)&(snr>=pl-3))[0]; idx=idx[idx>=10+on]; ramp=int(idx[0]-(10+on)) if len(idx) else -1
        s100=np.mean(snr[10+on:10+on+100]); out.append((c["singer"],c["line_end_s"],ramp,pl-s100,pl,c["words"]))
    return out
if __name__=="__main__":
    for W in sys.argv[1:]:
        o=run(W); r=np.array([x[2] for x in o],float); d=np.array([x[3] for x in o],float); pl=np.array([x[4] for x in o],float)
        print(f"{W}: {len(o)} echoes | ramp to normal presence: median {np.median(r):.0f} ms, p90 {np.percentile(r,90):.0f} ms, over 60 ms: {int(np.sum(r>60))}, over 120 ms: {int(np.sum(r>120))} | first 100 ms under the plateau by: median {np.median(d):.1f} dB, p90 {np.percentile(d,90):.1f} dB, over 4 dB: {int(np.sum(d>4))} | plateau SNR vs live mix: median {np.median(pl):+.1f} dB, below -9: {int(np.sum(pl<-9))}")
        if len(sys.argv)==2 or W==sys.argv[-1]:
            bad=[(x[1],x[5],x[2],round(x[4],1)) for x in o if x[4]<-9 or x[2]>60]; print("   still slow or weak:",bad)

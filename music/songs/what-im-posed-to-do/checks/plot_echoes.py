import sys, json, numpy as np, soundfile as sf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt
SR=44100; H=SR//1000
def env_db(x,win_ms):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos")
picks=[46.23,51.1,54.66,58.26,69.47,76.48,83.48,115.17,156.81,165.86,225.71,229.52]; Ws=["work_v4"]
fig,axs=plt.subplots(6,2,figsize=(13,13.5),sharey=False)
for ci,W in enumerate(Ws):
    rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
    thr=rd("throws_raw.wav").mean(1); beat=rd("beat.wav").mean(1); lead=rd("lead.wav").mean(1); bg=rd("bg.wav").mean(1); n=len(thr)
    eb=sosfiltfilt(SOSB,thr); live=sosfiltfilt(SOSB,beat[:n]+lead[:n]+bg[:n]); lead_b=sosfiltfilt(SOSB,lead[:n]+bg[:n])
    # the dry words: lead.wav at the copy position (the other rapper may be in it, shown as the grey 'live' line separately)
    for ri,p in enumerate(picks):
        ax=axs[ri%6,ri//6]; c=min(json.load(open(f"{W}/throw_cues.json")),key=lambda c:abs(c["line_end_s"]-p))
        a=c["words_from_s"]; L=c["copy_len_s"]; t0=c["first_echo_s"]; m=int(min(L,1.6)*1000)+250
        j_dry=int(a*1000)-50; j_e=int(t0*1000)-50
        Ed=env_db(lead_b,8); Ee=env_db(eb,8); Em=env_db(live,20)
        t=np.arange(m)-50
        ax.plot(t,Em[j_e:j_e+m],color="0.7",lw=1.6,label="everything else playing at the echo (400-3600 Hz)")
        ax.plot(t,Ed[j_dry:j_dry+m],color="tab:blue",lw=1.2,label="the original words' time (lead+bg)")
        ax.plot(t,Ee[j_e:j_e+m],color="tab:orange",lw=1.8,label="the echo (first repeat)")
        ax.set_ylim(-70,-10); ax.set_xlim(-50,m-50); ax.grid(alpha=.3)
        ax.set_title(f"{W}: {c['singer']} '{c['words']}' ({c.get('delay_note','half')} delay, copy {L:.2f} s)",fontsize=8)
        if ri==0 and ci==0: ax.legend(fontsize=6,loc="lower right")
        if ri%6==5: ax.set_xlabel("ms from the start of the copy / echo")
        ax.set_ylabel("dB",fontsize=7)
plt.tight_layout(); plt.savefig("diag/echo_shapes_v4.png",dpi=80)
print("saved")

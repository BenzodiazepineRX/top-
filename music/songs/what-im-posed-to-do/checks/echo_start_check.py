"""Echo start check, using each voice as it enters the mix (voice_L1/L2/B1/B2.wav) so the other rapper is not in the 'dry' measure.
For every cue (first repeat): where the copy starts against the first sound of its words, whether it starts after its own source has
ended, when it becomes audible over the live mix, and whether it ever exceeds its own words.  usage: echo_check_v4.py WORKDIR [verbose]"""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100; W=sys.argv[1]; VERB=len(sys.argv)>2; H=SR//1000
rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
SOSB=butter(4,[400,3600],"band",fs=SR,output="sos"); bp=lambda x: sosfiltfilt(SOSB,x)
def env_db(x,win_ms=4):
    k=max(2,int(win_ms*SR/1000)); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; return 10*np.log10(ma[np.round(np.arange(0,len(ma),SR/1000.0)).astype(int)]+1e-12)
beat=rd("beat.wav").mean(1); lead=rd("lead.wav").mean(1); bg=rd("bg.wav").mean(1); thr=rd("throws_raw.wav").mean(1); n=len(thr)
live=bp((beat[:n]+lead[:n]+bg[:n])); echo_b=bp(thr)
voices={k:rd(f"voice_{k}.wav").mean(1) for k in ("L1","L2","B1","B2")}; vb={k:bp(v[:n]) for k,v in voices.items()}; vw=voices
cues=json.load(open(f"{W}/throw_cues.json")); rows=[]
for c in cues:
    who=c["singer"]; a=c["words_from_s"]; L=c["copy_len_s"]; t0=c["first_echo_s"]; D=c["spacing_ms"]/1000
    ia,ib=int(a*SR),int((a+L)*SR)
    ed=env_db(vw[who][ia-int(0.03*SR):ib+int(0.1*SR)],4); off=30; seg=ed[off:off+int(L*1000)]; pk=np.percentile(seg,90)
    on30=int(np.argmax(seg>pk-30)) if np.any(seg>pk-30) else -1              # ms from copy start to its first sound
    already=bool(ed[off]>pk-30)                                              # sound already there at the very first sample = the attack was cut
    # the dry copy (band) and its echo: level of the loud parts
    dseg=vb[who][ia:ib]; dl=env_db(dseg,8); dloud=dl>np.percentile(dl,90)-12
    ip=int(t0*SR); eseg=echo_b[ip:ip+(ib-ia)]; el=env_db(eseg,8); eloud=el>np.percentile(el,90)-12
    up=lambda b,n: np.interp(np.arange(n),np.arange(len(b))*SR/1000.0,b.astype(float))>0.5
    d_rms=10*np.log10(np.mean(dseg[up(dloud,len(dseg))]**2)+1e-12); e_rms=10*np.log10(np.mean(eseg[up(eloud,len(eseg))]**2)+1e-12)
    # timing: envelope cross-correlation of copy and echo (expected lag 0)
    m=min(len(dl),len(el)); x1=dl[:m]-dl[:m].mean(); x2=el[:m]-el[:m].mean(); cc=np.correlate(x2,x1,"full"); lag=int(np.argmax(cc))-(m-1)
    # audibility over the live mix, from the echo's first sound
    eenv=env_db(echo_b[ip-int(0.02*SR):ip+int(min(L,1.4)*SR)+int(0.05*SR)],4); eo=20; epk=np.percentile(eenv[eo:eo+int(L*1000)],90)
    e_on=int(np.argmax(eenv[eo:]>epk-30)) if np.any(eenv[eo:]>epk-30) else 0
    menv=env_db(live[ip-int(0.02*SR):ip+int(min(L,1.4)*SR)+int(0.05*SR)],20); mm=min(len(eenv),len(menv)); snr=eenv[:mm]-menv[:mm]
    ok=np.convolve((snr>=-6).astype(float),np.ones(30)/30,"same")>=0.999; aud=np.where(ok[eo+e_on:])[0]; aud=int(aud[0]) if len(aud) else -1
    s100=float(np.mean(snr[eo+e_on:eo+e_on+100])); srest=float(np.mean(snr[eo+e_on+100:eo+int(L*1000)])) if L>0.3 else np.nan
    rows.append(dict(who=who,end=c["line_end_s"],L=L,D=D,words=c["words"],on30=on30,already=already,gap_ms=(t0-(a+L))*1000,loud_vs_dry=e_rms-d_rms,lag=lag,aud=aud,s100=s100,srest=srest,pre=c.get("pre_roll_ms",0)))
if VERB:
    print("who  end     len  delay | copy-start->first sound (ms) | echo starts after source ends by (ms) | echo loud part vs dry (dB) | env lag (ms) | audible after (ms) | SNR first100 / rest | words")
    for r in rows: print(f" {r['who']} {r['end']:7.2f} {r['L']:.2f} {r['D']:.3f} |  {r['on30']:4d}{' CUT' if r['already'] else '    '} | {r['gap_ms']:+7.0f} | {r['loud_vs_dry']:+5.1f} | {r['lag']:+3d} | {r['aud']:4d} | {r['s100']:+5.1f} / {r['srest']:+5.1f} | {r['words']}")
g=lambda k: np.array([r[k] for r in rows],float)
print(f"{len(rows)} echoes (first repeat of each).")
print(f"  attack cut at the copy's first sample (sound already there): {sum(r['already'] for r in rows)}")
print(f"  first sound comes at least 8 ms after the copy starts (inside the fade-in is the only risk): {int(np.sum(g('on30')>=8))} of {len(rows)}; median {np.median(g('on30')):.0f} ms, max {g('on30').max():.0f} ms; pre-rolled: {int(np.sum(g('pre')>0))}")
print(f"  echo starts after its own source has ended (gap >= -30 ms): {int(np.sum(g('gap_ms')>=-30))} of {len(rows)}; earliest {g('gap_ms').min():+.0f} ms, median {np.median(g('gap_ms')):+.0f} ms")
print(f"  echo's loud part against its dry words' loud part, 400-3600 Hz: median {np.median(g('loud_vs_dry')):+.1f} dB, loudest {g('loud_vs_dry').max():+.1f} dB (over its words if > 0): {int(np.sum(g('loud_vs_dry')>0.2))}")
print(f"  envelope lag of echo against copy (should be 0 +-2 ms): max |{np.abs(g('lag')).max():.0f}| ms; delays used {sorted(set(round(r['D'],3) for r in rows))}")
a=g('aud'); print(f"  audible over the live mix (within 6 dB for 30 ms) after the echo's first sound: median {np.median(a[a>=0]):.0f} ms; within 60 ms: {int(np.sum((a>=0)&(a<=60)))}; within 120 ms: {int(np.sum((a>=0)&(a<=120)))}; later than 120 ms or never: {int(np.sum((a<0)|(a>120)))}")
print(f"  SNR over the live mix: first 100 ms median {np.nanmedian(g('s100')):+.1f} dB, rest of the echo {np.nanmedian(g('srest')):+.1f} dB; first 100 ms worse than the rest by more than 4 dB: {int(np.sum((g('srest')-g('s100'))>4))}")

"""For a delay-mode build: is every echo repeat an exact number of beats after the words it copies? Checked two ways: from the cue list,
and from the audio (envelope cross-correlation of each repeat in throws_raw against the voice it was cut from).
usage: delay_check.py WORKDIR SRC_DIR
Limit: a copy of a held vowel has a nearly flat envelope, so its lag reads up to ~40 ms off (v8: 8 of 113, all held words);
confirm those from the cue list ((first_echo_s - words_from_s) / beat is a whole number, within the 0.01 s rounding)."""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
SR=44100; Q=60/135; G0=0.004
W, SRC = sys.argv[1], sys.argv[2]
sos=butter(4,[500,3000],"band",fs=SR,output="sos")
def env(x):
    y=sosfiltfilt(sos,x); k=int(0.005*SR); return np.sqrt(np.convolve(y**2,np.ones(k)/k,"same"))[::SR//1000]   # ~1 ms steps (44 samples)
V={k:sf.read(f"{W}/{k}_nat_0.45_ck.wav",always_2d=True)[0].mean(1) for k in ("L1","L2","B1","B2")}
th=sf.read(f"{W}/throws_raw.wav",always_2d=True)[0].mean(1)
cues=json.load(open(f"{W}/throw_cues.json")); lags=[]; bad=[]
BAR=4*Q; bar=lambda n: G0+(n-1)*BAR
MOVES=[(83,89,58),(98,114,48),(114,130,80)]                             # the build's copied sections (to bars, shift in bars)
def source_time(a):
    for b0,b1,sh in MOVES:
        if bar(b0)-0.7 <= a < bar(b1): return a-sh*BAR
    return a
for c in cues:
    a=c["words_from_s"]; L=c["copy_len_s"]; a_src=source_time(a)
    for r in range(c["repeats"]):
        t=c["first_echo_s"]+r*c["spacing_ms"]/1000
        planned=(t-a)/Q
        src=V[c["singer"]][int(a_src*SR):int((a_src+L)*SR)]; seg=th[int((t-0.06)*SR):int((t+L+0.06)*SR)]
        if len(seg)<len(src)+10: continue
        es, eg = env(src), env(seg); best=None
        for l in range(0, len(eg)-len(es)):
            v=np.dot(es, eg[l:l+len(es)])
            if best is None or v>best[0]: best=(v,l)
        meas_t = t-0.06 + best[1]*(SR//1000)/SR; beats=(meas_t-a)/Q
        lags.append(beats-np.round(beats))
        if abs(beats-np.round(beats))*Q*1000>15: bad.append((round(t,2),r,c["words"],round(beats,3)))
lags=np.array(lags)*Q*1000
print(f"{W}: {len(lags)} repeats; each one's distance from a whole number of beats after its words: median {np.median(np.abs(lags)):.1f} ms, worst {np.abs(lags).max():.1f} ms; over 15 ms: {len(bad)}")
for b in bad[:8]: print("   ", b)

"""Map how the vocal files slide against the beat: syllable starts of all voices, their 8th-note grid position in 8-bar windows
(stepping 1 bar), unwrapped and smoothed. Writes align/drift_map.json: times (s) and offset_ms (vocal late = +)."""
import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, find_peaks, savgol_filter
SR=44100; Q=60/135; G0=0.004; E8=Q/2; BAR=4*Q
sos=butter(4,[300,3000],"band",fs=SR,output="sos")
def onsets(path):
    x=sf.read(path,always_2d=True)[0].mean(1)
    y=sosfiltfilt(sos,x); k=int(0.010*SR); hop=int(0.005*SR)
    e=np.sqrt(np.convolve(y**2,np.ones(k)/k,"same"))[::hop]; db=20*np.log10(e+1e-9)
    d=np.diff(db,prepend=db[0]); d=np.convolve(d,np.ones(3)/3,"same"); loud=db>np.percentile(db[db>-80],60)-12
    pk,_=find_peaks(d,height=3.0,distance=int(0.09/0.005)); pk=[p for p in pk if p+6<len(db) and loud[min(p+6,len(db)-1)]]
    return np.array(pk)*0.005
ON={n:onsets(f"src/{n}.wav") for n in ("Lead 1","Lead 2","Background lead","Background lead 2")}
allon=np.sort(np.concatenate(list(ON.values())))
def centre(s): z=np.mean(np.exp(2j*np.pi*(s-G0)/E8)); return np.angle(z)/(2*np.pi)*E8*1000, abs(z)
if __name__=="__main__":
    ts=[]; offs=[]; vs=[]
    for c in np.arange(allon.min()+4*BAR, allon.max()-2*BAR, BAR):
        s=allon[(allon>=c-4*BAR)&(allon<c+4*BAR)]
        if len(s)<15: continue
        o,v=centre(s); ts.append(c); offs.append(o); vs.append(v)
    offs=np.unwrap(np.array(offs)/(E8*1000)*2*np.pi)*(E8*1000)/(2*np.pi)
    offs-= E8*1000*np.round(np.median(offs)/(E8*1000))                     # the smallest overall shift
    sm=savgol_filter(offs, min(len(offs)//2*2-1, 21), 2)
    for t,o,s_,v in zip(ts,offs,sm,vs):
        if int(round((t-G0)/BAR))%4==0: print(f"{int(t//60)}:{t%60:04.1f}  vocal grid offset {o:+6.0f} ms (smoothed {s_:+6.0f})  clustering {v:.2f}")
    json.dump(dict(times=[float(t) for t in ts], offset_ms=[float(x) for x in sm], raw_ms=[float(x) for x in offs]), open("align/drift_map.json","w"))
    # validation: clustering of every syllable on the BEAT's 8th grid, before and after removing the smoothed offset
    corr=np.interp(allon, ts, sm)/1000
    for lab,s in (("as recorded",allon),("drift removed",allon-corr)):
        _,v=centre(s); print(f"whole song, all voices, on the beat's 8th grid: clustering {v:.2f}  ({lab})")
    for n,s in ON.items():
        _,v0=centre(s); _,v1=centre(s-np.interp(s,ts,sm)/1000); print(f"  {n:18} {len(s):4d} syllables: {v0:.2f} -> {v1:.2f}")

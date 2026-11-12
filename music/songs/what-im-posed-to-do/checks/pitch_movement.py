import numpy as np, soundfile as sf, parselmouth, json
from parselmouth.praat import call
from scipy.signal import butter, sosfiltfilt
SR=44100; W="work_v2"
def load(f):
    x,_=sf.read(f,always_2d=True); return x.mean(1)
def pitch(x):
    p=parselmouth.Sound(x,SR).to_pitch_ac(time_step=0.01,pitch_floor=70,pitch_ceiling=500)
    f=p.selected_array['frequency']; f[f==0]=np.nan; return p.xs(),f
for k,name in (("L1","Lead 1"),("L2","Lead 2")):
    raw=load(f"src/{name}.wav"); tun=load(f"{W}/{k}_tuned_0.6.wav")[:len(raw)]
    a,b=int(60*SR),int(130*SR)       # 70 s of singing
    t,fr=pitch(raw[a:b]); _,ft=pitch(tun[a:b])
    both=~np.isnan(fr)&~np.isnan(ft)
    cr=1200*np.log2(fr); ct=1200*np.log2(ft)
    # frame-to-frame movement inside voiced runs
    def move(c):
        d=np.abs(np.diff(c)); d=d[~np.isnan(d)]; return np.median(d), np.mean(d<3)*100, np.mean(d<1)*100
    mr=move(cr); mt=move(ct)
    print(f"{k}: voiced raw {np.mean(~np.isnan(fr))*100:.0f}%  tuned {np.mean(~np.isnan(ft))*100:.0f}%")
    print(f"   pitch movement per 10 ms: raw median {mr[0]:.1f} cents, frames moving <3c {mr[1]:.0f}%, <1c {mr[2]:.0f}% | tuned median {mt[0]:.1f}, <3c {mt[1]:.0f}%, <1c {mt[2]:.0f}%")
    sh=ct[both]-cr[both]; print(f"   shift applied (tuned-raw): median |{np.median(np.abs(sh)):.0f}| cents, p90 {np.percentile(np.abs(sh),90):.0f}, >50c {np.mean(np.abs(sh)>50)*100:.0f}%, >100c {np.mean(np.abs(sh)>100)*100:.0f}%")
    # longest dead-flat stretches in tuned (|d|<2c)
    d=np.abs(np.diff(ct)); flat=(d<2); runs=[];n=0
    for v in flat:
        if v: n+=1
        else:
            if n: runs.append(n); n=0
    d0=np.abs(np.diff(cr)); flat0=(d0<2); runs0=[];n=0
    for v in flat0:
        if v: n+=1
        else:
            if n: runs0.append(n); n=0
    print(f"   dead-flat stretches >=80 ms: raw {sum(r>=8 for r in runs0)}, tuned {sum(r>=8 for r in runs)}; >=150 ms: raw {sum(r>=15 for r in runs0)}, tuned {sum(r>=15 for r in runs)}; longest tuned {max(runs)*10} ms")
    # pitch spread inside voiced runs (how much melody/inflection is left)
    def runspread(c):
        out=[];cur=[]
        for v in c:
            if np.isnan(v):
                if len(cur)>=12: out.append(np.std(cur))
                cur=[]
            else: cur.append(v)
        return np.median(out), len(out)
    print(f"   inflection inside each voiced run (std, cents): raw {runspread(cr)[0]:.0f}, tuned {runspread(ct)[0]:.0f}  ({runspread(cr)[1]} runs)")
    # identity resynthesis: how much does PSOLA change the voice when the pitch is NOT changed?
    seg=raw[a:a+20*SR]; snd=parselmouth.Sound(seg,SR); man=call(snd,"To Manipulation",0.01,70,500); y=call(man,"Get resynthesis (overlap-add)").values[0]
    n=min(len(y),len(seg)); r=y[:n]-seg[:n]; act=np.abs(seg[:n])>10**(-45/20)
    print(f"   PSOLA with pitch untouched: residual {10*np.log10(np.mean(r[act]**2)/np.mean(seg[:n][act]**2)):.1f} dB relative to the voice")

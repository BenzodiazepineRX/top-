import numpy as np, soundfile as sf, json, sys
from scipy.signal import butter, sosfiltfilt
SR=44100; W=sys.argv[1]; Q=60/135; BAR=4*Q; G0=0.004
rd=lambda f: sf.read(f"{W}/{f}",always_2d=True)[0]
bp=lambda x: sosfiltfilt(butter(4,[400,3600],"band",fs=SR,output="sos"),x)
db=lambda x: 10*np.log10(np.mean(x**2)+1e-15)
thr=rd("throws.wav").mean(1); n=len(thr)
rest=(rd("beat.wav")[:n]+rd("lead.wav")[:n]+rd("bgbus.wav")[:n]+rd("lead_verb.wav")[:n]+rd("bg_verb.wav")[:n]).mean(1)
lead=rd("lead.wav").mean(1)[:n]+rd("bg.wav").mean(1)[:n]
tb=bp(thr); rb=bp(rest); lb=bp(lead)
cues=json.load(open(f"{W}/throw_cues.json")); rows=[]
for c in cues:
    L=int(c["copy_len_s"]*SR); i=int(c["words_from_s"]*SR); p=int(round(c["first_echo_s"]*SR))
    # audibility: echo vs everything else, in the telephone band, in 50 ms steps; count the steps where the echo is within 6 dB of the rest
    st=int(0.05*SR); snr=[db(tb[q:q+st])-db(rb[q:q+st]) for q in range(p,p+L-st+1,st)]
    wl=[db(lead[q:q+st]) for q in range(i,i+L-st+1,st)]; wl=np.array(wl); loud=np.mean(wl>wl.max()-10)
    rows.append((c["singer"],c["line_end_s"],c["copy_len_s"],c["repeats"],np.median(snr),np.mean(np.array(snr)>-6)*100,db(tb[p:p+L])-db(lb[i:i+L]),loud*100,c.get("cut_dip_dB",0)))
r=np.array([x[4] for x in rows]); a=np.array([x[5] for x in rows])
print(f"{len(rows)} echoes. First repeat against everything else playing (400-3600 Hz): median {np.median(r):.1f} dB; under -10 dB (hard to hear): {np.sum(r<-10)}; -10 to -6: {np.sum((r>=-10)&(r<-6))}; above -6 (clear): {np.sum(r>=-6)}")
print("copy length: under 0.45 s (about one syllable): %d; 0.45-0.7 s: %d; over 0.7 s: %d"%(sum(x[2]<0.45 for x in rows),sum(0.45<=x[2]<0.7 for x in rows),sum(x[2]>=0.7 for x in rows)))
print("copies whose start is not at a real break (dip under 10 dB): %d"%sum(x[8]<10 for x in rows))
print("singer end   len reps  echo-vs-rest  %clear  vs-own-words  %of copy that is loud")
for x in rows: print(f"  {x[0]} {x[1]:7.2f} {x[2]:.2f}  {x[3]}   {x[4]:6.1f}      {x[5]:3.0f}    {x[6]:6.1f}      {x[7]:3.0f}")

"""Where does each echo's first sound land against the song's pulse? This beat is half-time: kick on beat 1, clap only on beat 3, so the
felt pulse is beats 1 and 3 (every half note). usage: pulse_check.py WORKDIR [WORKDIR ...]
Known false alarm: the window opens 50 ms before each echo (to catch a pre-roll), so the tail of an earlier echo can be read as this one's
start. In v6 the one "off the grid" echo ('turn around and', 2:37.3) starts at beat 3.01; the sound at 2.83 is the echo before it."""
import sys, json, numpy as np, soundfile as sf
SR=44100; Q=60/135; G0=0.004
def env(x,w=4):
    k=int(w*SR/1000); c=np.cumsum(np.r_[0.0,np.asarray(x,np.float64)**2]); ma=(c[k:]-c[:-k])/k
    ma=np.r_[np.full(k//2,ma[0]),ma,np.full(k-k//2-1,ma[-1])]; idx=np.minimum(np.round(np.arange(0,len(ma),SR/1000.0)).astype(int),len(ma)-1); return 10*np.log10(ma[idx]+1e-12)
for W in sys.argv[1:]:
    th=sf.read(f"{W}/throws_raw.wav",always_2d=True)[0].mean(1); rows=[]
    for c in json.load(open(f"{W}/throw_cues.json")):
        for r in range(c["repeats"]):
            t=c["first_echo_s"]+r*c["spacing_ms"]/1000; e=env(th[int((t-0.05)*SR):int((t+min(c["copy_len_s"],0.7))*SR)])
            if len(e)<60: continue
            pk=np.percentile(e,95); on=t-0.05+int(np.argmax(e>pk-20))/1000; beat=((on-G0)/Q)%4; nb=int(np.round(beat))%4; dist=min(beat%1,1-beat%1)*Q*1000
            rows.append((r,nb,dist))
    f=[x for x in rows if x[0]==0]; a=[x for x in rows]
    p13=lambda L: sum(1 for x in L if x[1] in (0,2) and x[2]<40); p24=lambda L: sum(1 for x in L if x[1] in (1,3) and x[2]<40)
    print(f"{W}: first repeats on the pulse (beat 1/3, within 40 ms): {p13(f)} of {len(f)}; between pulses (beat 2/4): {p24(f)}; off the grid: {len(f)-p13(f)-p24(f)} | all repeats on the pulse: {p13(a)} of {len(a)}")

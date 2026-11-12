"""Does an echo push the final limiter down?  Final-limiter gain with everything, against the same limiter on the mix without the echoes,
over the first 150 ms of every repeat."""
import sys; sys.path.insert(0,".")
import json, numpy as np, soundfile as sf
from v3lib import hold_limiter
SR=44100
for W in sys.argv[1:]:
    d=json.load(open(f"{W}/build_log.json")); g=10**(d["master"]["gain_into_limiter_dB"]/20)
    mt=sf.read(f"{W}/mix_trim.wav",always_2d=True)[0]; th=sf.read(f"{W}/throws.wav",always_2d=True)[0][:len(mt)]; tv=sf.read(f"{W}/throw_verb.wav",always_2d=True)[0][:len(mt)]
    _,ga=hold_limiter(mt*g,10**(-1.5/20),SR,look=0.008,hold=0.030,release_db_per_s=30.0); _,gr=hold_limiter((mt-th-tv)*g,10**(-1.5/20),SR,look=0.008,hold=0.030,release_db_per_s=30.0)
    H=SR//1000; rows=[]
    for c in json.load(open(f"{W}/throw_cues.json")):
        for r in range(c["repeats"]):
            t0=c["first_echo_s"]+r*c["spacing_ms"]/1000; a,b=int(t0*SR)//H,int((t0+0.15)*SR)//H
            extra=float(ga[a:b].min()-gr[a:b].min()); rows.append((-extra,t0,r,c["words"],-ga[a:b].min()))
    rows.sort(reverse=True); big=[x for x in rows if x[0]>1.0]
    print(f"{W}: echo repeats {len(rows)}; the echo adds more than 1 dB of limiting in its first 150 ms: {len(big)}; worst {rows[0][0]:.1f} dB at {int(rows[0][1]//60)}:{rows[0][1]%60:04.1f} '{rows[0][3]}'")
    for x in big[:6]: print(f"    {int(x[1]//60)}:{x[1]%60:04.1f} repeat {x[2]} echo adds {x[0]:.1f} dB (total {x[4]:.1f}) '{x[3]}'")

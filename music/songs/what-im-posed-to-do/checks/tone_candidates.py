import sys; sys.path.insert(0,"diag"); sys.path.insert(0,".")
import subprocess, numpy as np, soundfile as sf
from grit_lib import voiced_grit
SR=44100; N=4096; f=np.fft.rfftfreq(N,1/SR); win=np.hanning(N)
def ld(p): return sf.read(p,always_2d=True)[0].mean(1)
def metrics(x,t0=45,t1=130):
    m=x[int(t0*SR):int(t1*SR)]; S=np.array([np.abs(np.fft.rfft(m[i:i+N]*win))**2 for i in range(0,len(m)-N,2048)])
    e=S.sum(1); S=S[e>np.percentile(e,50)]; b=lambda a,c: S[:,(f>=a)&(f<c)].sum(1)
    body=b(200,1500).mean(); sel=(f>=3000)&(f<8000)
    flat=np.exp(np.mean(np.log(S[:,sel]+1e-20),1))/(np.mean(S[:,sel],1)+1e-20)
    db=lambda v: 10*np.log10(v/body)
    return dict(low=db(b(100,200).mean()),words=db(b(1600,3500).mean()),edge=db(b(3500,5000).mean()),harsh=db(b(2000,5000).mean()),fizz=db(b(5000,12000).mean()),grit=float(np.median(flat)))
def ff(src,dst,af): subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-af",af,"-c:a","pcm_f32le",dst],check=True)
def deess(src,dst,mx=6): subprocess.run(["python3","/home/user/top-/music/tools/dsp_tools.py","deess",src,dst,"--low","5500","--high","9000","--auto-pct","97","--max-cut",str(mx)],capture_output=True,check=True)
def main():
    CASES=[("raw (stage 2, high-passed)",None),
     ("v3 chain (bell -3 @2.8k, shelf -2.5 @9k, 2:1 comp)","equalizer=f=2800:t=q:w=1.0:g=-3,highshelf=f=9000:g=-2.5,acompressor=threshold=-20dB:ratio=2:attack=20:release=200:knee=6:detection=rms:makeup=1.3"),
     ("shelf -4 @5k","highshelf=f=5000:g=-4"),
     ("shelf -6 @5k","highshelf=f=5000:g=-6"),
     ("shelf -6 @4.5k","highshelf=f=4500:g=-6"),
     ("shelf -4 @4k","highshelf=f=4000:g=-4"),
     ("bell -3 @4.2k Q1 + shelf -5 @6k","equalizer=f=4200:t=q:w=1.0:g=-3,highshelf=f=6000:g=-5"),
     ("bell -4 @4.2k Q0.8 + shelf -6 @5.5k","equalizer=f=4200:t=q:w=0.8:g=-4,highshelf=f=5500:g=-6"),
     ("shelf -6 @4.5k + lowpass 9k","highshelf=f=4500:g=-6,lowpass=f=9000"),
    ]
    print("                                                         low100-200  words1.6-3.5  edge3.5-5  harsh2-5  fizz5-12  grit | steady-pitch fizz grit   (all vs body 200-1500 Hz)")
    for k in ("L1","L2"):
        print("---",k)
        for lab,af in CASES:
            p=f"work_v3/{k}_2.wav"
            if af: ff(p,"diag/st4/a.wav",af); p="diag/st4/a.wav"
            ds="diag/st4/b.wav"; deess(p,ds)
            m=metrics(ld(ds)); vz,vg,_=voiced_grit(ld(ds))
            print(f"  {lab:52s} {m['low']:+6.1f} {m['words']:+8.1f} {m['edge']:+9.1f} {m['harsh']:+8.1f} {m['fizz']:+8.1f} {m['grit']:.3f} | {vz:+5.1f} {vg:.3f}",flush=True)
    print("approved reference points: Driftin' Away lead grit 0.032 | Baccdoor v3 leads (Nearly PERFECT): fizz -34.4, grit 0.013 | Baccdoor v2 (still harsh): fizz -29.9 grit 0.048")
if __name__=="__main__": main()

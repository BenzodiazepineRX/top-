import json, sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
def load16(p):
    x,sr=sf.read(p,always_2d=True); return resample_poly(x.mean(1),160,441).astype(np.float32)
from faster_whisper import WhisperModel
m=WhisperModel("small.en",device="cpu",compute_type="int8",cpu_threads=4)
for k,name in (("L1","Lead 1"),("L2","Lead 2"),("B1","Background lead"),("B2","Background lead 2")):
    segs,info=m.transcribe(load16(f"src/{name}.wav"),word_timestamps=True,vad_filter=True,vad_parameters=dict(min_silence_duration_ms=400),beam_size=5,condition_on_previous_text=False)
    out=[]
    for s in segs:
        for w in (s.words or []): out.append(dict(w=w.word.strip(),s=round(w.start,3),e=round(w.end,3),p=round(w.probability,2)))
    json.dump(out,open(f"words/{k}.json","w"),indent=0); print(k,len(out),"words; low confidence (<0.5):",sum(x["p"]<0.5 for x in out),flush=True)

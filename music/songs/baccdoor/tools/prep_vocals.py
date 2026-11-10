"""Baccdoor: retune each vocal stem to the beat's tuning, then run the vocal chains.

Retune: the autotune is aimed at A4 = 440 (measured tuning centres +0.5 to +1.4 cents), the beat sits at
A4 = 438.3 Hz (-6.7 cents). Each stem is shifted by (beat - its own centre) with rubberband (formants preserved,
quality mode); rubberband moves the audio about 36 ms early, so each output is re-aligned to its input by
cross-correlation (checked to the sample).
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import fftconvolve  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc_lib as L  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("BACC_WORK", ".")), "")
T = f"python3 -I {os.path.dirname(L.dt.__file__)}/dsp_tools.py"
FF = "ffmpeg -nostdin -v error -y"
sr = L.sr
RETUNE = {"02_Main1": -8.1, "03_Main2": -7.7, "04_BG": -7.2, "05_BGBG1": -7.9}
out = {}


def sh(cmd, show=2):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=D)
    if r.returncode:
        sys.exit(f"FAILED {cmd}\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}")
    lines = (r.stdout + r.stderr).strip().splitlines()
    for ln in lines[-show:]:
        print("   ", ln[:220])
    return r.stdout + r.stderr


for name, cents in RETUNE.items():
    ratio = 2 ** (cents / 1200)
    sh(f"{FF} -i {name}.wav -af \"aformat=sample_fmts=fltp,rubberband=pitch={ratio:.8f}:formant=preserved:pitchq=quality:"
       f"transients=smooth:window=standard:channels=together\" -c:a pcm_f32le {name}_rt_raw.wav", 0)
    a, _ = L.dt.read(D + name + ".wav")
    b, _ = L.dt.read(D + name + "_rt_raw.wav")
    # alignment by the amplitude envelope (300-4000 Hz, 3 ms smoothing): waveform correlation locks onto the wrong
    # pitch cycle on autotuned notes (it reported -70 to +42 ms); the envelope is pitch-free. Coarse at 1 ms over the
    # whole file, then exact to the sample within +-2 ms
    bpe = L.butter(2, [300, 4000], "band", fs=sr, output="sos")
    kk = int(0.003 * sr)

    def envf(z):
        return np.convolve(np.abs(L.sosfiltfilt(bpe, L.mono(z))), np.ones(kk) / kk, mode="same")

    ea, eb = envf(a), envf(b)
    ca, cb = ea[::44] - ea[::44].mean(), eb[::44] - eb[::44].mean()
    k0 = (int(np.argmax(fftconvolve(cb, ca[::-1], mode="full"))) - (len(ca) - 1)) * 44
    best = max(range(k0 - 88, k0 + 89), key=lambda q: float(np.dot(ea[10 * sr:-10 * sr], np.roll(eb, -q)[10 * sr:-10 * sr])))
    k = best
    b = np.roll(b, -k, axis=0)
    if k > 0:
        b[-k:] = 0
    elif k < 0:
        b[:-k] = 0
    k2 = max(range(-44, 45), key=lambda q: float(np.dot(ea[10 * sr:-10 * sr], np.roll(envf(b), -q)[10 * sr:-10 * sr])))
    L.dt.write(D + name + "_rt.wav", b, sr)
    out[name] = {"cents": cents, "rubberband_offset_samples": k, "after_realign_samples": k2}
    print(f"{name}: retuned {cents:+.1f} cents; rubberband moved it {k} samples ({k / sr * 1000:+.1f} ms), after re-align {k2}")

# ---- chains
print("\nmain vocals")
for src, tag in (("02_Main1_rt", "m1"), ("03_Main2_rt", "m2")):
    sh(f"{T} gain-stage {src}.wav {tag}_1.wav --target-rms -18 --against 01_Beat.wav", 2)
    sh(f"{T} hpf {tag}_1.wav {tag}_2.wav --freq 90 --order 3", 1)
    sh(f"{T} resonances {tag}_2.wav", 9)
print("background and its background")
for src, tag, hp in (("04_BG_rt", "bg", 150), ("05_BGBG1_rt", "bb", 180)):
    sh(f"{T} gain-stage {src}.wav {tag}_1.wav --target-rms -18 --against 01_Beat.wav", 1)
    sh(f"{T} hpf {tag}_1.wav {tag}_2.wav --freq {hp} --order 3", 1)
    sh(f"{T} resonances {tag}_2.wav", 6)
json.dump(out, open(D + "retune.json", "w"), indent=1)

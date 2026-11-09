"""Pushing the Interstate v14.

The v7 recipe (drum-locked line-end echoes, throw, adlib echoes, same reverb, same outro), with ONE change:
the printed effects stem's own echo copies are moved onto the drums' real hits (fx_v14.wav, from retime_stem.py).
No extra word echoes, no extra hall.

usage: build_v14.py <stem file> <tag> [folder]  (run from anywhere; folder holds the processed tracks, default .)
  stem fx_v4.wav  + tag null -> reproduces v7 exactly (null test against mix_v7.wav)
  stem fx_v14.wav + tag v14  -> the new version
"""
import os
import subprocess
import sys

import numpy as np

S = (sys.argv[3] if len(sys.argv) > 3 else ".").rstrip("/") + "/"
TT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")
os.chdir(S)
sys.path.insert(0, TT)
import dsp_tools as dt  # noqa: E402

STEM, TAG = sys.argv[1], sys.argv[2]
G = f"python3 -I {TT}/groove_delay.py"
T = f"python3 -I {TT}/dsp_tools.py"


def sh(cmd, tail=2):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {cmd[:160]}\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
    lines = (r.stdout + r.stderr).strip().splitlines()
    for ln in lines[-tail:]:
        print("   ", ln[:230])


# the nine line-end words, as in v7: (word start, word end + 30 ms)
ev = ("34.115-34.43,37.875-38.17,41.586-41.89,75.948-76.25,77.797-78.14,87.91-88.18,105.717-106.00,"
      "107.56-107.89,117.649-117.93")
print("line-end echoes (1/4, drum-locked, as v7):")
sh(f'{G} v8.wav {TAG}_accent.wav --drums 01_Beat.wav --bpm 129 --note 1/4 --events "{ev}" --feedback 0.32 --taps 7 '
   f'--hp 500 --lp 4800 --return-db 0 --duck-by v8.wav --duck-depth 3')

g = 3.9
outro = " ".join(f"--track {n}.wav:{g}" for n in ("o6_phone", "o6_hiss", "o6_stutters", "o6_delay", "o6_delay_verb",
                                                    "o6_throw", "o6_throw_verb", "o6_verb", "o6_verb_late"))
print("mix:")
sh(f"{T} mix mix_{TAG}.wav --track beat_v4.wav:0 --track v8.wav:-6.6 --track a5.wav:-10.0 --track {STEM}:0 "
   f"--track adlib_delay.wav:-10.0 --track vocal_verb.wav:-6.6 --track {TAG}_accent.wav:-6.6 "
   f"--track lead_throw.wav:-6.6 --track lead_throw_verb.wav:-6.6 {outro}", tail=1)
x, sr = dt.read(f"mix_{TAG}.wav")
m = np.abs(x).max(1)
on = np.where(m > 10 ** (-66 / 20))[0]
end = on[-1] + int(0.5 * sr)
x = x[:end]
f = int(2.0 * sr)
x[-f:] *= np.linspace(1, 0, f)[:, None] ** 2
dt.write(f"mix_{TAG}.wav", x, sr)
print(f"   trimmed to {end / sr:.2f} s")

if TAG == "null":
    ref, _ = dt.read("mix_v7.wav")
    n = min(len(ref), len(x))
    d = x[:n] - ref[:n]
    rms = lambda a: 20 * np.log10(np.sqrt((a ** 2).mean()) + 1e-12)  # noqa: E731
    print(f"null test vs mix_v7.wav: lengths {len(x)} / {len(ref)} samples; mix rms {rms(ref[:n]):.2f} dBFS, "
          f"difference rms {rms(d):.2f} dBFS, peak difference {20 * np.log10(np.abs(d).max() + 1e-12):.2f} dBFS")
    bad = np.where(np.abs(d).max(1) > 1e-4)[0]
    if len(bad):
        print(f"   {len(bad)} samples differ by more than -80 dBFS; from {bad[0] / sr:.2f} s to {bad[-1] / sr:.2f} s")
    sys.exit(0)

sh(f"{T} ms-bus mix_{TAG}.wav mix_{TAG}_ms.wav --side-hp 90 --mid-shelf 9500:2.0", tail=0)
print("master:")
sh(f'python3 -I {TT}/render_master.py mix_{TAG}_ms.wav master_{TAG}.wav --target-lufs -11.5 --ceiling -0.5 2>&1 | grep -E "Result|Limiter took|WARN"', tail=4)
sh(f"python3 -I {TT}/export_master.py master_{TAG}.wav --name Pushing_the_Interstate_master_{TAG} --rate 44100", tail=2)

"""Less of the reverb that is baked into a panned vocal track.   usage: dereverb.py in.wav out.wav [--knee 8] [--max-cut 14]

The adlib tracks of Don't Need Closure were exported with a long reverb on them: after a word stops, a tail holds
about 16 dB under the word for 0.7 s and more. Two steps, both leaving the words themselves alone:

1. Keep only the track's main direction. The dry voice is panned to one side (one fixed left/right ratio); the reverb
   is spread wide (different left and right). Projecting the stereo track onto the voice's own pan direction keeps the
   voice in full and drops the part of the reverb that is not on that direction; the result is put back at the same
   pan position, so the track stays where it was and nothing cancels in mono.
2. Turn the tails down (a downward expander that follows each phrase). The reference is the loudest level of the
   last 1.5 s. Sound more than --knee dB under it is turned down 1 dB for every dB further down, up to --max-cut dB.
   It opens 10 ms before a word starts (lookahead), so attacks are not clipped, and closes over 80 ms.
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closure_lib as L  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("output")
ap.add_argument("--knee", type=float, default=8.0)
ap.add_argument("--max-cut", type=float, default=14.0)
ap.add_argument("--memory", type=float, default=1.5)
a = ap.parse_args()
sr = L.sr
x, s = L.dt.read(a.input)
assert s == sr
x = x.astype(np.float64)

# 1. the pan direction (the principal axis of left/right over the sung parts)
e = (x ** 2).sum(1)
act = e > np.percentile(e[e > 0], 60)
w, v = np.linalg.eigh(np.cov(x[act].T))
d = v[:, 1] * np.sign(v[:, 1].sum())
m = x @ d
off = 10 * np.log10(w[0] / w.sum())

# 2. tails down
y, st = L.tails_down(m, a.knee, a.max_cut, a.memory)
out = np.stack([y * d[0], y * d[1]], 1)
L.dt.write(a.output, out.astype(np.float32), sr)
print(f"Less baked-in reverb: pan direction L {d[0]:.2f} / R {d[1]:.2f} kept ({off:.1f} dB of the energy was off that direction and is dropped); "
      f"tails more than {a.knee:.0f} dB under the phrase turned down up to {a.max_cut:.0f} dB: reducing {st['pct_reducing']:.0f}% of the time, "
      f"{st['db_on_loud_words']:.2f} dB on the loud words")

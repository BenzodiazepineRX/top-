"""How much reverb tail follows the words. The word endings are found once, in the RAW track: the level falls 12 dB
within 100 ms from a loud moment and no new word starts in the next half second (clean endings only). Then, in every
file given, at those same moments: the median level 150-500 ms after the ending against the level in the 100 ms
before it. Median over all endings. All files must share the raw track's timeline.
usage: tail_check.py raw.wav file.wav [file2.wav ...]"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closure_lib as L  # noqa: E402

H = 2205  # 50 ms


def env(path):
    x, _ = L.dt.read(path)
    m = np.sqrt((x ** 2).mean(1))
    n = len(m) // H
    return 20 * np.log10(np.sqrt((m[:n * H].reshape(n, H) ** 2).mean(1)) + 1e-9)


def endings(raw):
    e = env(raw)
    pk = np.percentile(e[e > -80], 95)
    out, i = [], 0
    while i < len(e) - 12:
        # a clean ending: nothing but tail for the next half second (no new word within 12 dB of this one)
        if e[i] > pk - 8 and e[i + 2] < e[i] - 12 and e[i + 3:i + 11].max() < e[i] - 12:
            out.append(i)
            i += 10
        i += 1
    return out


def tail(path, ends):
    e = env(path)
    v = [np.median(e[i + 3:i + 11]) - max(e[i - 1], e[i]) for i in ends if i + 11 < len(e)]
    return float(np.median(v))


if __name__ == "__main__":
    ends = endings(sys.argv[1])
    for p in sys.argv[1:]:
        print(f"{p:28s} tail {tail(p, ends):6.1f} dB under the word ({len(ends)} word endings from {sys.argv[1]})")

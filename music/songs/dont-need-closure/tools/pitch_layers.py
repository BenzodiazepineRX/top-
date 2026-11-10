"""Don't Need Closure: (1) how in tune the vocals already are, against E major at the beat's own tuning (A4 = 441.3 Hz);
(2) how the layers relate: is each background track a double of a main line (same words at the same time) or
an answer, and how loud is it against the line it backs. Exact hops (441 samples = 10 ms)."""
import os
import sys

import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("CLOSURE_WORK", ".")), "")
sr = 44100
A4 = 441.3
SCALE = {4, 6, 8, 9, 11, 1, 3}  # E major (C# minor) pitch classes
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
bp = butter(4, [70, 1500], "bandpass", fs=sr, output="sos")


def f0_track(x):
    m = sosfiltfilt(bp, x.mean(axis=1))
    fl, hop = 1764, 441  # 40 ms, 10 ms
    out = np.full((len(m) - fl) // hop, np.nan)
    conf = np.zeros_like(out)
    lo, hi = int(sr / 800), int(sr / 70)
    for k in range(len(out)):
        w = m[k * hop:k * hop + fl]
        if np.sqrt(np.mean(w ** 2)) < 10 ** (-55 / 20):
            continue
        w = w - w.mean()
        # YIN difference function (cumulative-mean normalized)
        ac = np.correlate(w, w, mode="full")[fl - 1:fl - 1 + hi + 2]
        e = np.cumsum(w[::-1] ** 2)[::-1]
        dif = e[0] + e[:hi + 2] - 2 * ac  # approx: sum (x_t - x_t+tau)^2
        cm = dif[1:] * np.arange(1, len(dif)) / (np.cumsum(dif[1:]) + 1e-12)
        cm = np.concatenate(([1], cm))
        cand = np.where(cm[lo:hi] < 0.15)[0]
        if len(cand) == 0:
            continue
        t = lo + cand[0]
        while t + 1 < hi and cm[t + 1] < cm[t]:
            t += 1
        # parabolic interpolation
        if 1 <= t < len(cm) - 1:
            a, b, c = cm[t - 1], cm[t], cm[t + 1]
            dd = (a - c) / (2 * (a - 2 * b + c) + 1e-12)
        else:
            dd = 0
        out[k] = sr / (t + dd)
        conf[k] = 1 - cm[t]
    return out, conf


def report(name):
    x, _ = dt.read(D + name + ".wav")
    f0, conf = f0_track(x)
    v = ~np.isnan(f0)
    note = 12 * np.log2(f0[v] / A4) + 69
    dev = (note - np.round(note)) * 100
    pc = np.round(note).astype(int) % 12
    # held notes: runs of 15+ frames (150 ms) staying within 60 cents
    held = np.zeros(len(f0), bool)
    i = 0
    nn = np.full(len(f0), np.nan)
    nn[v] = note
    while i < len(f0):
        if np.isnan(nn[i]):
            i += 1
            continue
        j = i
        while j + 1 < len(f0) and not np.isnan(nn[j + 1]) and abs(nn[j + 1] - nn[i]) < 0.6:
            j += 1
        if j - i + 1 >= 15:
            held[i:j + 1] = True
        i = j + 1
    hv = held[v]
    in_scale = np.isin(pc, list(SCALE))
    # the vocal's own tuning centre (where the autotune is aimed), relative to A4 = 440
    note440 = 12 * np.log2(f0[v][hv] / 440) + 69
    cdev = (note440 - np.round(note440)) * 100
    centre = np.angle(np.mean(np.exp(2j * np.pi * cdev / 100))) / (2 * np.pi) * 100
    hist = np.bincount(pc[hv], minlength=12)
    top = np.argsort(hist)[::-1][:6]
    print(f"{name}: voiced {v.mean() * 100:.0f}% of frames; held notes (>= 150 ms) {hv.mean() * 100:.0f}% of voiced time")
    print(f"   held notes vs E major at A4={A4}: |off| median {np.median(np.abs(dev[hv])):.1f} cents, "
          f"{np.mean(np.abs(dev[hv]) <= 15) * 100:.0f}% within 15 c, {np.mean(np.abs(dev[hv]) > 30) * 100:.0f}% more than 30 c off, "
          f"{np.mean(in_scale[hv]) * 100:.0f}% on scale notes")
    print(f"   the vocal's tuning centre: {centre:+.1f} cents from A4=440 (the beat sits at +5.0 c); "
          f"most-held notes: " + ", ".join(f"{NAMES[k]} {hist[k] / max(hist.sum(), 1) * 100:.0f}%" for k in top))
    return f0


for nm in ("02_Lead1", "03_Lead2", "04_Adlib1", "05_Adlib2"):
    report(nm)

# ---- layers: envelope correlation at lag 0 over the time both are active, and level difference there
print("\nlayer relations (where both are active): envelope correlation (1 = same words at the same time), level diff")
env_bp = butter(4, [300, 4000], "bandpass", fs=sr, output="sos")


def env(name):
    x, _ = dt.read(D + name + ".wav")
    m = sosfiltfilt(env_bp, x.mean(axis=1))
    n = len(m) // 441
    r = np.sqrt((m[:n * 441].reshape(n, 441) ** 2).mean(axis=1))
    out = np.zeros(int(190 / 0.01))
    out[:min(n, len(out))] = r[:len(out)]
    return out


E = {k: env(k) for k in ("02_Lead1", "03_Lead2", "04_Adlib1", "05_Adlib2")}
dbE = {k: 20 * np.log10(v + 1e-9) for k, v in E.items()}
act = {k: v > (np.percentile(v[v > 0], 90) * 10 ** (-25 / 20)) for k, v in E.items()}
for a, b in (("04_Adlib1", "02_Lead1"), ("04_Adlib1", "03_Lead2"), ("05_Adlib2", "02_Lead1"), ("05_Adlib2", "03_Lead2"), ("05_Adlib2", "04_Adlib1"), ("02_Lead1", "03_Lead2")):
    both = act[a] & act[b]
    if both.sum() < 100:
        print(f"   {a} vs {b}: overlap too short")
        continue
    c = np.corrcoef(dbE[a][both], dbE[b][both])[0, 1]
    # best lag within +-300 ms
    best = (c, 0)
    for lag in range(-30, 31, 2):
        bb = np.roll(both, lag) & both
        if bb.sum() < 100:
            continue
        cc = np.corrcoef(dbE[a][bb], np.roll(dbE[b], lag)[bb])[0, 1]
        if cc > best[0]:
            best = (cc, lag)
    lv = 10 * np.log10(np.mean(E[a][both] ** 2) / np.mean(E[b][both] ** 2))
    print(f"   {a:9s} vs {b:9s}: overlap {both.sum() / 100:5.1f} s, corr {c:.2f} (best {best[0]:.2f} at {best[1] * 10:+d} ms), level {lv:+.1f} dB")

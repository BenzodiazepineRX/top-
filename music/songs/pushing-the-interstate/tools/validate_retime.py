"""Usage: python3 -I validate_retime.py FOLDER (the folder retime_stem.py wrote into).

Independent check of fx_v14.wav against the printed stem, with the scan's own band (500-4500 Hz).

1. coverage      : the 69 clearly echoed lead words found by the first scan - what happened to each?
2. no ghosts     : correlation with the dry word at the OLD echo time, original stem vs the residual after the move,
                   against a control floor (same measure at lags where no copy exists)
3. on the drums  : where every echo copy in the FINAL stem sits against the nearest real drum hit
"""
import json
import os
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402
import groove_delay as gd  # noqa: E402

D = (sys.argv[1] if len(sys.argv) > 1 else ".").rstrip("/") + "/"
sr = 44100
QN = 60 / 129
orig, _ = dt.read(D + "fx_v4.wav")
fin, _ = dt.read(D + "fx_v14.wav")
res, _ = dt.read(D + "fx_v14_resid.wav")
lead, _ = dt.read(D + "02_Lead_Vocals.wav")
adl, _ = dt.read(D + "03_Adlibs.wav")
hits, _ = gd.drum_hits(D + "01_Beat.wav")
bp = butter(4, [500, 4500], "band", fs=sr, output="sos")
mono = lambda x: x.mean(axis=1) if x.ndim > 1 else x  # noqa: E731
bpf = lambda x: np.stack([sosfiltfilt(bp, x[:, c]) for c in range(2)], axis=1)  # noqa: E731
ref = {"lead": sosfiltfilt(bp, mono(lead)), "adlib": sosfiltfilt(bp, mono(adl))}
ob, fb, rb = bpf(orig), bpf(fin), bpf(res)
log = json.load(open(D + "retime_log.json"))


def ncc(w, seg):
    n = len(w)
    num = fftconvolve(seg, w[::-1], mode="valid")
    cs = np.concatenate([[0], np.cumsum(seg ** 2)])
    en = cs[n:] - cs[:-n]
    ww = float(np.dot(w, w)) + 1e-18
    r = num / (np.sqrt(np.maximum(en, 0) * ww) + 1e-18)
    r[en < 1e-5] = 0.0
    return np.clip(r, -1, 1)


def best(src, a, b, lag, arr, hw=int(0.004 * sr)):
    i0, n = int((a - 0.005) * sr), int((b - a + 0.02) * sr)
    w = ref[src][i0:i0 + n]
    s0, s1 = i0 + lag - hw, i0 + lag + hw + n
    if s0 < 0 or s1 > len(arr) or np.dot(w, w) < 1e-9:
        return None
    out = (0.0, lag)
    for c in range(2):
        r = ncc(w, arr[s0:s1, c])
        k = int(np.argmax(r))
        if r[k] > out[0]:
            out = (float(r[k]), lag - hw + k)
    return out


# ---- 1. coverage of the first scan's 69 words
scan = json.load(open(D + "stem_echo_words.json"))
moved1 = {round(r["word"][0], 2): r for r in log if r["src"] == "lead" and r["note"] == 1}
cov = [w for w in scan if round(w["start"], 2) in moved1 or any(abs(w["start"] - k) < 0.03 for k in moved1)]
unc = [w for w in scan if w not in cov]
print(f"1. the first scan's {len(scan)} clearly echoed lead words: {len(cov)} moved, {len(unc)} not moved")
for w in unc:
    a, lagms = w["start"], w["lag_ms"]
    echo_t = a + lagms / 1000
    off = (echo_t - hits[np.argmin(np.abs(hits - echo_t))]) * 1000
    why = "already within 1 ms of a drum hit" if abs(off) < 1.5 else ("no drum hit within 60 ms" if abs(off) > 60 else "below the detection threshold / odd lag")
    print(f"     {a:7.2f} s  lag {lagms:7.1f} ms  level {w['echo_vs_word_db']:6.1f} dB  {off:6.1f} ms from a drum hit  -> {why}")

# ---- 2. ghosts
rows = {k: [] for k in ("orig_old", "resid_old", "resid_ctl", "fin_new")}
seen = set()
for r in log:
    key = (r["src"], tuple(r["word"]), r["note"])
    if key in seen or abs(r["shift_ms"]) < 8:
        continue
    seen.add(key)
    a, b = r["word"]
    lag0 = int(round(r["lag_ms"] / 1000 * sr))
    new_lag = lag0 + int(round(r["shift_ms"] / 1000 * sr))
    o = best(r["src"], a, b, lag0, ob, hw=int(0.003 * sr))
    q = best(r["src"], a, b, lag0, rb, hw=int(0.003 * sr))
    n_ = best(r["src"], a, b, new_lag, fb, hw=int(0.004 * sr))
    ctl = [best(r["src"], a, b, lag0 + int(off * sr), rb, hw=int(0.003 * sr)) for off in (0.12, 0.14, 0.16, 0.18, 0.20)]
    ctl = [c[0] for c in ctl if c]
    if o and q and n_ and ctl:
        rows["orig_old"].append(o[0])
        rows["resid_old"].append(q[0])
        rows["resid_ctl"].append(float(np.median(ctl)))
        rows["fin_new"].append(n_[0])
print(f"2. {len(rows['orig_old'])} moved copies (shift >= 8 ms). Correlation with the dry word (0 = nothing, 1 = identical):")
for k, v in rows.items():
    print(f"     {k:10s} median {np.median(v):.2f}   10th/90th pct {np.percentile(v, 10):.2f} / {np.percentile(v, 90):.2f}")

# ---- 3. every echo copy in the final stem, against the drums (first echoes of lead and adlib words, all notes)
off_all, off_before = [], []
for r in log:
    a, b = r["word"]
    lag0 = int(round(r["lag_ms"] / 1000 * sr))
    new_lag = lag0 + int(round(r["shift_ms"] / 1000 * sr))
    nw = best(r["src"], a, b, new_lag, fb, hw=int(0.004 * sr))
    if nw is None:
        continue
    t_new = r["attack"] + nw[1] / sr
    t_old = r["attack"] + lag0 / sr
    off_all.append((t_new - hits[np.argmin(np.abs(hits - t_new))]) * 1000)
    off_before.append((t_old - hits[np.argmin(np.abs(hits - t_old))]) * 1000)
off_all, off_before = np.abs(off_all), np.abs(off_before)
print(f"3. {len(off_all)} moved copies, distance of the echo's attack to the nearest real drum hit:")
print(f"     before: median {np.median(off_before):.1f} ms, {int((off_before > 10).sum())} more than 10 ms off")
print(f"     after : median {np.median(off_all):.1f} ms, {int((off_all > 10).sum())} more than 10 ms off")

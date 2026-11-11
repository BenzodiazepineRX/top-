"""Keep the previous engineer's whole effects stem, but move its echo copies onto the drums' real hits.

Song-specific (Pushing the Interstate v14). Usage: python3 -I retime_stem.py FOLDER
FOLDER holds fx_v4.wav (the printed stem with the same -10 dB fade as the beat from 2:30.7), 02_Lead_Vocals.wav,
03_Adlibs.wav, 01_Beat.wav and word_events.txt (start-end seconds of each sung lead word, comma separated; in
this folder). Writes fx_v14.wav, fx_v14_resid.wav (subtraction only) and retime_log.json into FOLDER.
The four "odd chain" cases at the end are this song's loud throws that are not on a note multiple.

v1 found only about half of the echoes (it judged whole multi-word segments, and used a wide band that dilutes the
correlation). v2 judges every sung word on its own:

  detect  - normalized cross-correlation of the dry word with the stem exactly one note later (+-4 ms), in the
            500-4500 Hz band where the stem's echo copies live, against a threshold taken from control windows
            (the same measurement at lags where no copy can be)
  fit     - for each echoed word, a short least-squares filter from the dry word to the stem copy (per channel lag),
            so the copy keeps its own level, EQ and width
  move    - subtract that copy where it sits; add it back so the copy's attack lands on the nearest real drum hit
            (within 60 ms of one note after the word's attack). Copies already within 1 ms are left alone.
Everything else in the stem (reverb, reverse reverb, build-ups, other throws) is left as printed.
"""
import json
import os
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import butter, fftconvolve, find_peaks, sosfiltfilt

TT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")
sys.path.insert(0, TT)
import dsp_tools as dt  # noqa: E402
import groove_delay as gd  # noqa: E402

D = (sys.argv[1] if len(sys.argv) > 1 else ".").rstrip("/") + "/"
sr = 44100
QN = 60 / 129
SNAP = 0.060
HWD = int(0.004 * sr)  # detection: lag within +-4 ms of the exact note value
J = 48  # fit filter half-length (K = 97 taps, about 2.2 ms)

stem, _ = dt.read(D + "fx_v4.wav")
lead, _ = dt.read(D + "02_Lead_Vocals.wav")
adl, _ = dt.read(D + "03_Adlibs.wav")
hits, _ = gd.drum_hits(D + "01_Beat.wav")
fitbp = butter(4, [300, 6000], "band", fs=sr, output="sos")
detbp = butter(4, [500, 4500], "band", fs=sr, output="sos")
mono = lambda x: x.mean(axis=1) if x.ndim > 1 else x  # noqa: E731
bpf = lambda sos, x: np.stack([sosfiltfilt(sos, x[:, c]) for c in range(2)], axis=1)  # noqa: E731
SRC = {"lead": lead, "adlib": adl}
ref_fit = {k: sosfiltfilt(fitbp, mono(v)) for k, v in SRC.items()}
ref_det = {k: sosfiltfilt(detbp, mono(v)) for k, v in SRC.items()}
resid = stem.copy()
rfit = bpf(fitbp, stem)  # band-passed residual, kept in step with resid
added = np.zeros_like(stem)
log = []


def ncc(w, seg):
    n = len(w)
    num = fftconvolve(seg, w[::-1], mode="valid")
    cs = np.concatenate([[0], np.cumsum(seg ** 2)])
    en = cs[n:] - cs[:-n]
    ww = float(np.dot(w, w)) + 1e-18
    r = num / (np.sqrt(np.maximum(en, 0) * ww) + 1e-18)
    r[en < 1e-5] = 0.0
    return np.clip(r, -1, 1)


def det_at(ref, arr, i0, n, lag_c, hw=HWD):
    """best normalized correlation (and its lag, in samples) within +-hw of lag_c, both channels."""
    w = ref[i0:i0 + n]
    s0, s1 = i0 + lag_c - hw, i0 + lag_c + hw + n
    out = (0.0, lag_c)
    if s0 < 0 or s1 > len(arr) or np.dot(w, w) < 1e-9:
        return out
    for c in range(2):
        r = ncc(w, arr[s0:s1, c])
        k = int(np.argmax(r))
        if r[k] > out[0]:
            out = (float(r[k]), lag_c - hw + k)
    return out


def channel_lags(ref, arr, i0, n, lag, hw=int(0.003 * sr)):
    w = ref[i0:i0 + n]
    out = []
    for c in range(2):
        s0, s1 = i0 + lag - hw, i0 + lag + hw + n
        out.append(lag - hw + int(np.argmax(ncc(w, arr[s0:s1, c]))) if s0 >= 0 and s1 <= len(arr) else lag)
    return out


def fit(ref, i0, n, lags, lam=1e-3):
    K = 2 * J + 1
    X = sliding_window_view(ref[i0 - J:i0 + n + J], K)
    XtX, Xty = np.zeros((K, K)), np.zeros((K, 2))
    for s in range(0, n, 16384):
        Xc = np.ascontiguousarray(X[s:s + 16384])
        XtX += Xc.T @ Xc
        for c in range(2):
            Xty[:, c] += Xc.T @ rfit[i0 + lags[c] + s:i0 + lags[c] + s + len(Xc), c]
    H = np.linalg.solve(XtX + lam * np.trace(XtX) / K * np.eye(K), Xty)
    est = np.zeros((n, 2))
    for s in range(0, n, 16384):
        Xc = np.ascontiguousarray(X[s:s + 16384])
        est[s:s + len(Xc)] = Xc @ H
    ramp = int(0.003 * sr)
    est[:ramp] *= np.linspace(0, 1, ramp)[:, None]
    est[-ramp:] *= np.linspace(1, 0, ramp)[:, None]
    return est


def word_events(x, lo=30.8, hi=134.5):
    """Word onsets by log spectral flux, each running to the next onset (max 0.45 s)."""
    m = mono(x)
    y = sosfiltfilt(butter(4, [300, 4000], "band", fs=sr, output="sos"), m)
    n = 44
    k = len(y) // n
    e = np.sqrt((y[:k * n] ** 2).reshape(k, n).mean(1))
    fl = np.convolve(np.clip(np.diff(np.log(e + 1e-5), prepend=0), 0, None), np.ones(5) / 5, "same")
    lv = 20 * np.log10(e + 1e-9)
    pk, _ = find_peaks(fl, height=np.percentile(fl, 90), distance=90)
    t = [p * n / sr for p in pk if lo < p * n / sr < hi and lv[min(p + 20, k - 1)] > lv.max() - 35]
    return [(a, min(b, a + 0.45)) for a, b in zip(t, t[1:] + [t[-1] + 0.3]) if b - a > 0.06]


def windows(words):
    """(detection window, application window) in samples for each word; application windows never overlap."""
    out = []
    for k, (a, b) in enumerate(words):
        i0 = int((a - 0.005) * sr)
        n_det = int((b - a + 0.02) * sr)
        nxt = words[k + 1][0] - 0.005 + 0.003 if k + 1 < len(words) else b + 0.02  # 3 ms cross-fade into the next word
        n_app = int((min(b + 0.02, nxt) - (a - 0.005)) * sr)
        out.append((i0, n_det, max(n_app, 0)))
    return out



DMAX = {"lead": 0.040, "adlib": 0.015}  # largest jump in shift between neighbouring echoed words (s)
LAM = {"lead": 0.02, "adlib": 0.5}  # weight of a jump against a miss, per ms^2


def smooth_shifts(nats, dmax, lam, reach=60):
    """Shift for each echoed word (in a run) so its echo attack lands on a drum hit, with no jump between neighbours
    larger than dmax: dynamic programming over shifts in 1 ms steps; cost = miss^2 + small move penalty + lam*jump^2."""
    S = np.arange(-reach, reach + 1)
    cost = np.empty((len(nats), len(S)))
    for k, nat in enumerate(nats):
        miss = np.abs(hits[None, :] - (nat + S[:, None] / 1000)).min(axis=1) * 1000
        cost[k] = miss ** 2 + 0.02 * S ** 2
    jump = np.abs(S[:, None] - S[None, :]) / 1000
    pen = np.where(jump <= dmax, lam * (jump * 1000) ** 2, 1e9)
    tot = cost[0].copy()
    back = np.zeros((len(nats), len(S)), int)
    for k in range(1, len(nats)):
        m = tot[None, :] + pen  # rows: this shift, columns: previous shift
        back[k] = m.argmin(axis=1)
        tot = cost[k] + m.min(axis=1)
    idx = int(tot.argmin())
    out = [0] * len(nats)
    for k in range(len(nats) - 1, -1, -1):
        out[k] = S[idx] / 1000
        idx = back[k][idx]
    return out


def snap(nominal):
    j = int(np.argmin(np.abs(hits - nominal)))
    return hits[j] - nominal if abs(hits[j] - nominal) <= SNAP else None


lead_words = sorted(tuple(float(t) for t in p.split("-")) for p in open(D + "word_events.txt").read().split(","))
WORDS = {"lead": lead_words, "adlib": word_events(adl)}
NOTES = {"lead": (1, 2, 3, 4), "adlib": (2, 1, 3, 4)}
CONTROL_OFFSETS = (0.085, 0.135, 0.185, 0.235, 0.285, 0.335, 0.385, 0.435)  # none of them sits on a note multiple


def stage(src, note):
    words, wins = WORDS[src], windows(WORDS[src])
    ref_d, ref_f = ref_det[src], ref_fit[src]
    rdet = bpf(detbp, resid)
    Lc = int(round(note * QN * sr))
    ctrl = []
    for i0, n, _ in wins:
        if n < 2500:
            continue
        for off in CONTROL_OFFSETS:
            ctrl.append(det_at(ref_d, rdet, i0, n, Lc + int(off * sr))[0])
    thr = max(0.40, float(np.percentile(ctrl, 99)))
    cands = []
    for (a, b), (i0, n, n_app) in zip(words, wins):
        if n < 2500 or n_app < 2500:
            continue
        nc, lag = det_at(ref_d, rdet, i0, n, Lc)
        if nc < thr:
            continue
        t0 = gd.attack(SRC[src], sr, a)
        nominal = t0 + note * QN  # where the echo should fall: one note after the word's attack
        if np.abs(hits - nominal).min() > SNAP:
            continue  # no drum hit within 60 ms: leave this copy as printed
        cands.append({"a": a, "b": b, "i0": i0, "n_app": n_app, "t0": t0, "lag": lag, "nc": nc, "nat": t0 + lag / sr})
    # consecutive echoed words form a run; the shifts inside a run may not jump (jumps would overlap / gap the copy)
    runs, cur = [], []
    for cd in cands:
        if cur and cd["a"] - cur[-1]["b"] > 0.25:
            runs.append(cur)
            cur = []
        cur.append(cd)
    if cur:
        runs.append(cur)
    done = 0
    for run in runs:
        shifts = smooth_shifts([cd["nat"] for cd in run], DMAX[src], LAM[src])
        for cd, shift in zip(run, shifts):
            if abs(shift) < 0.001:
                continue
            i0, n_app, lag = cd["i0"], cd["n_app"], cd["lag"]
            lags = channel_lags(ref_f, rfit, i0, n_app, lag)
            est = fit(ref_f, i0, n_app, lags)
            level = 20 * np.log10(np.sqrt((est ** 2).mean() + 1e-18) / np.sqrt((ref_f[i0:i0 + n_app] ** 2).mean() + 1e-18))
            for c in range(2):
                pc = i0 + lags[c]
                resid[pc:pc + n_app, c] -= est[:, c]
                rfit[pc:pc + n_app, c] -= est[:, c]
                q = pc + int(round(shift * sr))
                added[q:q + n_app, c] += est[:, c]
            done += 1
            log.append({"src": src, "word": [round(cd["a"], 3), round(cd["b"], 3)], "attack": round(cd["t0"], 4), "note": note,
                        "ncc": round(cd["nc"], 2), "level_db": round(float(level), 1), "lag_ms": round(lag / sr * 1000, 2),
                        "shift_ms": round(shift * 1000, 1)})
    print(f"{src:5s} note {note}: threshold {thr:.2f} (control p99); {len(cands)} echoed words with a drum hit in reach, "
          f"{len(runs)} runs, {done} copies moved")


for src in ("lead", "adlib"):
    for note in NOTES[src]:
        stage(src, note)


def odd_chains(src, cases, thr=0.45):
    """A few loud throws in the stem are not on a note multiple (their first tap sits 25-45 ms past one) and repeat
    in a chain a quarter or half note apart. Each tap is moved to the nearest drum hit to where it naturally falls."""
    words = WORDS[src]
    wins = windows(words)
    ref_d, ref_f = ref_det[src], ref_fit[src]
    for t_word, lag0_ms in cases:
        k = int(np.argmin([abs(a - t_word) for a, _ in words]))
        (a, b), (i0, n, n_app) = words[k], wins[k]
        t0 = gd.attack(SRC[src], sr, a)
        for m in range(-2, 5):
            rdet = bpf(detbp, resid)
            lag_c = int(round((lag0_ms / 1000 + m * QN) * sr))
            if lag_c < int(0.1 * sr):
                continue
            nc, lag = det_at(ref_d, rdet, i0, n, lag_c, hw=int(0.006 * sr))
            if nc < thr:
                continue
            nat = t0 + lag / sr
            hit = hits[int(np.argmin(np.abs(hits - nat)))]
            shift = hit - nat
            if abs(shift) > SNAP or abs(shift) < 0.001:
                continue
            lags = channel_lags(ref_f, rfit, i0, n_app, lag)
            est = fit(ref_f, i0, n_app, lags)
            level = 20 * np.log10(np.sqrt((est ** 2).mean() + 1e-18) / np.sqrt((ref_f[i0:i0 + n_app] ** 2).mean() + 1e-18))
            for c in range(2):
                pc = i0 + lags[c]
                resid[pc:pc + n_app, c] -= est[:, c]
                rfit[pc:pc + n_app, c] -= est[:, c]
                q = pc + int(round(shift * sr))
                added[q:q + n_app, c] += est[:, c]
            log.append({"src": src, "word": [round(a, 3), round(b, 3)], "attack": round(t0, 4), "note": -1,
                        "ncc": round(nc, 2), "level_db": round(float(level), 1), "lag_ms": round(lag / sr * 1000, 2),
                        "shift_ms": round(shift * 1000, 1)})
            print(f"   odd chain, word {a:.2f} s, tap at {lag / sr * 1000:7.1f} ms: correlation {nc:.2f}, "
                  f"level {level:.1f} dB, moved {shift * 1000:+.1f} ms onto the drum hit")


print("loud throws that are not on a note multiple:")
odd_chains("lead", ((44.63, 1266.8), (60.33, 1885.3), (91.22, 974.4), (96.68, 1893.2)))

final = resid + added
dt.write(D + "fx_v14.wav", final, sr)
dt.write(D + "fx_v14_resid.wav", resid, sr)
json.dump(log, open(D + "retime_log.json", "w"), indent=1)

for src in ("lead", "adlib"):
    L = [r for r in log if r["src"] == src]
    sh = np.array([r["shift_ms"] for r in L]) if L else np.zeros(1)
    print(f"{src}: {len(L)} copies moved; level vs word median {np.median([r['level_db'] for r in L]):.1f} dB; "
          f"shift median {np.median(np.abs(sh)):.0f} ms, largest {np.abs(sh).max():.0f} ms")
for a, b in ((29.2, 30.75), (44.6, 47.1), (73.3, 74.4), (100.1, 101.75), (129.9, 131.45)):
    i, j = int(a * sr), int(b * sr)
    rms = lambda x: 20 * np.log10(np.sqrt((x[i:j] ** 2).mean()) + 1e-12)  # noqa: E731
    print(f"build-up {a:6.1f}-{b:6.1f} s: stem {rms(stem):6.2f} dB -> {rms(final):6.2f} dB")
print("whole stem rms:", round(20 * np.log10(np.sqrt((stem ** 2).mean())), 2), "->", round(20 * np.log10(np.sqrt((final ** 2).mean())), 2), "dBFS")

"""Shared helpers for Dont Need Closure (carried over from Baccdoor and Driftin' Away, with the lessons built in).

- Every envelope index/time conversion uses the real step (HOP / sr), never a rounded 2.5 ms.
- An echo is cut from the last clearly sung word of a phrase (within 6 dB of the phrase's loud level), one word
  long, and placed with its attack on a main beat of the grid measured from the drums.
- Loudness comparisons are K-weighted (ITU-R BS.1770), never plain RMS (an 808 dominates RMS but not the ear).
"""
import math
import os
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")
                if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
                else "/home/claude/top-/music/tools")
import dsp_tools as dt  # noqa: E402

sr = 44100
BPM = 126.0
Q = 60 / BPM            # 0.47619 s
BAR = 4 * Q             # 1.90476 s
G0 = 0.00263            # eighth-note grid offset measured from the drum hits
BAR0 = G0 + 2 * Q       # bar 1 (808 on beats 1-2, clap on beat 3; the drums enter on the downbeat of bar 10)


def beat_t(n):
    return G0 + n * Q


def bar_t(b, beat=1):
    return BAR0 + (b - 1) * BAR + (beat - 1) * Q


def next_beat(t, min_gap=0.10):
    return beat_t(math.ceil((t + min_gap - G0) / Q - 1e-9))


def bb(t):
    k = round((t - BAR0) / Q, 3)
    bar = int(k // 4) + 1
    return f"{bar}.{k - (bar - 1) * 4 + 1:.2f}"


SECTIONS = [("intro", 0.0, bar_t(10)), ("hook 1", bar_t(10), bar_t(18)), ("verse 1", bar_t(18), bar_t(42)),
            ("drop 1", bar_t(42), bar_t(50)), ("verse 2", bar_t(50), bar_t(66)), ("drop 2", bar_t(66), bar_t(74)),
            ("verse 3", bar_t(74), bar_t(90)), ("outro", bar_t(90), 1e9)]


def section_of(t):
    for name, a, b in SECTIONS:
        if a <= t < b:
            return name
    return "outro"


def mono(x):
    return x.mean(axis=1) if x.ndim > 1 else x


def fades(seg, fin, fout):
    seg = seg.copy()
    a, b = int(fin * sr), int(fout * sr)
    if a:
        seg[:a] *= np.linspace(0, 1, a)[:, None] if seg.ndim > 1 else np.linspace(0, 1, a)
    if b:
        seg[-b:] *= np.linspace(1, 0, b)[:, None] if seg.ndim > 1 else np.linspace(1, 0, b)
    return seg


# ---------------------------------------------------------------- word finding (exact step)
BAND = butter(4, [300, 5000], "bandpass", fs=sr, output="sos")
HOP = 110
STEP = HOP / sr


def envelope_db(x):
    b = sosfiltfilt(BAND, mono(x))
    n = len(b) // HOP
    r = np.sqrt((b[:n * HOP].reshape(n, HOP) ** 2).mean(axis=1))
    r = np.convolve(r, np.ones(4) / 4, mode="same")
    return 20 * np.log10(r + 1e-9)


def attacks_in(env, t0, t1, rise=6.0):
    i0, i1 = max(10, int(t0 / STEP)), min(len(env) - 1, int(t1 / STEP))
    out, last = [], -1
    for i in range(i0, i1):
        lo = env[i - 10:i].min()
        if env[i] - lo >= rise and env[i] > env[i - 1] and i - last > 24:
            j = i - 10 + int(np.argmin(env[i - 10:i]))
            k = j
            while k < i and env[k + 1] - env[j] < 1.5:
                k += 1
            out.append(k * STEP)
            last = i
    return out


def word_end(env, t_attack, t_max):
    i0, i1 = int(t_attack / STEP), int(t_max / STEP)
    pk = env[i0:i1].max()
    above = np.where(env[i0:i1] > pk - 30)[0]
    return (i0 + above[-1]) * STEP


def last_loud_word(env, start, end, within_db=6.0, max_len=0.44):
    """The last clearly sung word of a phrase, at most max_len long (an echo repeats every beat)."""
    lo = max(start, end - 1.6)
    loud = np.percentile(env[int(start / STEP):int(end / STEP)], 90)
    ats = attacks_in(env, lo, end)
    best = None
    for k, a in enumerate(ats):
        nxt = ats[k + 1] if k + 1 < len(ats) else end
        if nxt - a < 0.08:
            continue
        if env[int(a / STEP):int(nxt / STEP)].max() >= loud - within_db:
            best = (a, nxt)
    if best is None:
        a = max(start, end - max_len)
        return a, end
    a, nxt = best
    e = word_end(env, a, nxt + 0.03)
    if e - a > max_len + 0.02:
        starts = np.arange(a, e - max_len + 1e-9, 0.0125)
        vals = [10 * np.log10(np.mean(10 ** (env[int(x / STEP):int((x + max_len) / STEP)] / 10))) for x in starts]
        s0 = [x for x, v in zip(starts, vals) if v >= max(vals) - 3.0][-1]
        i0 = int(s0 / STEP)
        j = max(int(a / STEP), i0 - 24)
        s0 = (j + int(np.argmin(env[j:i0 + 1]))) * STEP
        a, e = s0, min(e, s0 + max_len + 0.03)
    return a, e


# ---------------------------------------------------------------- echoes on the beat
ECHO_BAND = butter(2, [250, 5500], "bandpass", fs=sr, output="sos")
DARK = butter(1, 4200, "lowpass", fs=sr, output="sos")


def render_echoes(src, events, n, label):
    """events: (attack, end, taps, first_db, step_db, spacing_in_beats). Each echo's attack starts on a main beat
    (the first beat at least 100 ms after the word ends), then every `spacing` beats, quieter and darker,
    alternating left/right. Zero-phase filters keep the attack in place."""
    out = np.zeros((n, 2))
    log = []
    pre = 0.005
    for att, end, taps, fd, sd, sp in events:
        i, j = int((att - pre) * sr), int((end + 0.04) * sr)
        seg = fades(mono(src[i:j]), 0.003, 0.04)
        y = sosfiltfilt(ECHO_BAND, seg)
        t1 = next_beat(end)
        times = []
        for k in range(taps):
            if k:
                y = sosfiltfilt(DARK, y)
            tk = t1 + k * Q * sp
            g = 10 ** ((fd + k * sd) / 20)
            s = int(round((tk - pre) * sr))
            e = min(n, s + len(y))
            if s >= n:
                break
            pan = (1.0, 0.45) if k % 2 == 0 else (0.45, 1.0)
            norm = 1 / math.sqrt((pan[0] ** 2 + pan[1] ** 2) / 2)
            out[s:e, 0] += y[:e - s] * g * pan[0] * norm
            out[s:e, 1] += y[:e - s] * g * pan[1] * norm
            times.append(round(tk, 4))
        log.append({"src": label, "word": [round(att, 4), round(end, 4)], "word_at": bb(att), "echo_times": times,
                    "first_echo_at": bb(times[0]) if times else None, "levels_db": [fd + k * sd for k in range(len(times))],
                    "spacing_beats": sp, "section": section_of(att)})
    return out, log


# ---------------------------------------------------------------- K-weighted loudness
KS = dt.rbj("highshelf", 1681.974, sr, 3.99984, 0.7071752)
_w0 = 2 * math.pi * 38.13547 / sr
_al = math.sin(_w0) / (2 * 0.5003270)
KH = (np.array([1, -2, 1]) * (1 + math.cos(_w0)) / 2 / (1 + _al),
      np.array([1 + _al, -2 * math.cos(_w0), 1 - _al]) / (1 + _al))


def kweight(x):
    if x.ndim == 1:
        x = x[:, None]
    return np.stack([lfilter(KH[0], KH[1], lfilter(KS[0], KS[1], x[:, c])) for c in range(x.shape[1])], 1)


def loud(x, t0, t1, gate_self=True, xk=None):
    """K-weighted loudness of x between t0 and t1 (400 ms blocks, 100 ms hop). gate_self: drop blocks more than
    10 dB under the part's own level there (so silence between words does not count)."""
    y = (xk if xk is not None else kweight(x))[int(t0 * sr):int(t1 * sr)]
    p = (y ** 2).sum(axis=1)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    if len(p) < blk:
        return -99.0
    c = np.concatenate(([0], np.cumsum(p)))
    st = np.arange(0, len(p) - blk + 1, hop)
    ms = (c[st + blk] - c[st]) / blk
    ms = ms[ms > 10 ** ((-70 + 0.691) / 10)]
    if gate_self and len(ms):
        rel = -0.691 + 10 * np.log10(ms.mean()) - 10
        ms = ms[-0.691 + 10 * np.log10(ms) > rel]
    return -0.691 + 10 * math.log10(ms.mean()) if len(ms) else -99.0


def reverb(x, kind, decay, predelay, ret_db, duck_key=None, duck_db=0.0, hp=150, lp=12000, seed=1):
    from scipy.signal import sosfilt
    send = sosfilt(butter(2, [hp, lp], "bandpass", fs=sr, output="sos"), mono(x))
    ir = dt.make_ir(sr, kind, decay, predelay, 1.0, seed=seed)
    out = np.stack([fftconvolve(send, ir[:, c])[:len(x)] for c in range(2)], 1)
    if duck_key is not None and duck_db:
        g, _, _ = dt.duck_gain(duck_key, sr, len(out), duck_db, None, 15, 400)
        out *= g[:, None]
    return out * 10 ** (ret_db / 20)


def peak_catch(x, ceiling_db, look_ms=5.0, release_ms=60.0):
    from scipy.ndimage import maximum_filter1d, minimum_filter1d
    thr = 10 ** (ceiling_db / 20)
    a = np.abs(x).max(1)
    k = int(look_ms / 1000 * sr)
    env = maximum_filter1d(a, size=2 * k + 1)
    g = np.minimum(1.0, thr / np.maximum(env, 1e-12))
    g = minimum_filter1d(g, size=2 * k + 1)
    g = np.convolve(g, np.ones(2 * k + 1) / (2 * k + 1), mode="same")
    blk = int(0.001 * sr)
    nb = len(g) // blk
    gb = g[:nb * blk].reshape(nb, blk).min(1)
    gs = dt.ar_smooth(gb, 0.001, release_ms, 0.5)
    curve = np.minimum(np.interp(np.arange(len(g)), (np.arange(nb) + 0.5) * blk, gs), g)
    act = a > thr * 10 ** (-30 / 20)
    gr = -20 * np.log10(np.maximum(curve, 1e-9))
    st = {"ceiling_dbfs": round(ceiling_db, 2), "max_gr_db": round(float(gr.max()), 1),
          "pct_active_over_1db": round(float((gr[act] > 1).mean() * 100), 1) if act.any() else 0.0,
          "avg_gr_active_db": round(float(gr[act].mean()), 2) if act.any() else 0.0}
    return x * curve[:, None], st


# ---------------------------------------------------------------- layer order (v1 fix: compare only where both sing)
def kblocks(xk):
    """K-weighted power of 400 ms blocks every 100 ms (block i starts at i * 0.1 s)."""
    p = (xk ** 2).sum(axis=1)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    c = np.concatenate(([0], np.cumsum(p)))
    st = np.arange(0, len(p) - blk + 1, hop)
    return (c[st + blk] - c[st]) / blk


def active_blocks(pw, below_db=20.0):
    lv = 10 * np.log10(pw + 1e-20)
    ref = np.percentile(lv[lv > -100], 95) if (lv > -100).any() else -200
    return lv > ref - below_db


def layer_diff(px, pr, ax, ar, a0, a1, min_blocks=8):
    """dB of x under/over the reference over the blocks of [a0, a1) where both are singing (None if < 0.8 s)."""
    i0, i1 = int(a0 / 0.1), int(a1 / 0.1)
    both = ax[i0:i1] & ar[i0:i1]
    if both.sum() < min_blocks:
        return None
    return 10 * np.log10(px[i0:i1][both].mean() / pr[i0:i1][both].mean())


def ride_layer(x, ref_k, target_fn, n, fallback_k=None, fallback_target=None, clamp_db=4.0):
    """Per 2-bar window, a gain that puts x target dB under the reference where both sing; windows without
    enough overlap take the nearest known gain; gains clamped to the median +- clamp_db; 0.3 s ramps."""
    px = kblocks(kweight(x))
    ax = active_blocks(px)
    pr = kblocks(ref_k)
    ar = active_blocks(pr)
    if fallback_k is not None:
        pf = kblocks(fallback_k)
        af = active_blocks(pf)
    wins = []
    b = 1
    while bar_t(b) < n / sr - 1:
        a0, a1 = bar_t(b), bar_t(b + 2)
        tgt = target_fn(section_of((a0 + a1) / 2))
        d = layer_diff(px, pr, ax, ar, a0, a1)
        if d is None and fallback_k is not None:
            d2 = layer_diff(px, pf, ax, af, a0, a1)
            if d2 is not None:
                d, tgt = d2, fallback_target
        wins.append([a0, a1, None if d is None else tgt - d])
        b += 2
    known = [w[2] for w in wins if w[2] is not None]
    med = float(np.median(known))
    for w in wins:
        if w[2] is not None:
            w[2] = float(np.clip(w[2], med - clamp_db, med + clamp_db))
    idx = [i for i, w in enumerate(wins) if w[2] is not None]
    for i, w in enumerate(wins):
        if w[2] is None:
            j = min(idx, key=lambda q: abs(q - i))
            w[2] = wins[j][2]
    curve = np.zeros(n)
    for a0, a1, gw in wins:
        curve[int(a0 * sr):min(n, int(a1 * sr))] = gw
    curve[:int(wins[0][0] * sr)] = wins[0][2]
    curve[int(wins[-1][1] * sr):] = wins[-1][2]
    k = int(0.3 * sr)
    curve = np.convolve(np.pad(curve, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
    return x * (10 ** (curve / 20))[:, None], [(round(a0, 3), round(gw, 2)) for a0, a1, gw in wins]


# ---------------------------------------------------------------- reverb tails down (a downward expander that follows each phrase)
def tails_down(x, knee=8.0, max_cut=10.0, memory=1.5):
    """The reference is the loudest level from `memory` s back to 50 ms ahead. Sound more than `knee` dB under it is
    turned down 1 dB for every dB further down, up to `max_cut` dB. It opens 10 ms before a word starts (lookahead),
    so attacks are not clipped, and closes over 80 ms. The same gain goes to both channels."""
    from scipy.ndimage import maximum_filter1d
    m = np.sqrt((x ** 2).sum(axis=1)) if x.ndim > 1 else np.abs(x)
    B = int(0.005 * sr)
    nb = len(m) // B
    lev = 20 * np.log10(np.sqrt((m[:nb * B].reshape(nb, B) ** 2).mean(1)) + 1e-9)
    if not (lev > -80).any():
        return x.copy(), {"pct_reducing": 0.0, "db_on_loud_words": 0.0}
    lev = maximum_filter1d(lev, size=5, origin=-2)                       # 10 ms lookahead
    mem = int(memory / 0.005)
    mem += mem % 2
    ref = maximum_filter1d(lev, size=mem + 11, origin=(mem - 10) // 2)   # loudest level from `memory` back to 50 ms ahead
    loud95 = np.percentile(lev[lev > -80], 95)
    ref = np.maximum(ref, loud95 - 30)                                   # a quiet phrase is not judged against silence
    gr = np.clip(ref - lev - knee, 0, max_cut)
    gr = dt.ar_smooth(gr, 0.005, 80.0, 3.0)                              # closes over 80 ms, opens in 3 ms
    g = 10 ** (-np.interp(np.arange(len(m)), (np.arange(nb) + 0.5) * B, gr) / 20)
    sung = lev > loud95 - 8
    st = {"knee_db": knee, "max_cut_db": max_cut, "pct_reducing": round(float(100 * (gr > 1).mean()), 1),
          "db_on_loud_words": round(float(gr[sung].mean()), 2)}
    return (x * g[:, None] if x.ndim > 1 else x * g), st

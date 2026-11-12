# Helpers for What I'm Posed To Do v3: a tuner that keeps the voice's own pitch movement, and a peak control that
# holds its gain across pitch periods so it cannot roughen the sound.
import numpy as np, parselmouth
from scipy.signal import medfilt, resample_poly
from scipy.ndimage import maximum_filter1d, uniform_filter1d

SCALE = np.array([2, 4, 5, 7, 9, 10, 0])                                  # D E F G A Bb C (D minor / F major)


def praat_pitch(x, sr, step=0.005):
    p = parselmouth.Sound(x, sr).to_pitch_ac(time_step=step, pitch_floor=70, pitch_ceiling=500)
    f = p.selected_array["frequency"].copy(); f[f == 0] = np.nan
    return p.xs(), f


def nearest_scale_cents(c):
    """c: pitch in cents (midi * 100, A4 = 6900). Returns the nearest D-minor note, in cents."""
    m = c / 100.0
    cand = np.floor(m)[:, None] + np.arange(-3, 4)[None, :]
    good = np.isin(np.mod(cand, 12), SCALE); d = np.where(good, np.abs(cand - m[:, None]), 99)
    return cand[np.arange(len(m)), np.argmin(d, 1)] * 100.0


def runs_of(mask):
    d = np.diff(np.r_[0, mask.astype(int), 0]); return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def correction_curve(ts, f, strength, a4=439.5, step=0.005, full_below=100.0, none_above=160.0):
    """Cents to add at each pitch frame. Only steady (held) pitch is corrected; glides and short blips are left alone."""
    c = 6900 + 1200 * np.log2(f / a4)
    corr = np.zeros(len(f)); info = dict(frames_voiced=int(np.sum(~np.isnan(f))), frames_corrected=0, steady_frames_left_alone_off_scale=0)
    dev_before = []; dev_after = []
    for a, b in runs_of(~np.isnan(f)):
        if b - a < 10: continue                                           # under 50 ms: leave it
        cc = c[a:b]
        k1 = min(15, (b - a) // 2 * 2 - 1); s = medfilt(np.pad(cc, k1, mode="edge"), k1)[k1:-k1] if k1 >= 3 else cc
        s = uniform_filter1d(s, 11, mode="nearest")                       # the slow centre of the note (about 75 + 55 ms)
        tgt = nearest_scale_cents(s)
        k2 = min(17, (b - a) // 2 * 2 - 1)
        if k2 >= 3: tgt = medfilt(np.pad(tgt, k2, mode="edge"), k2)[k2:-k2]     # a note must last about 80 ms to count
        d = s - tgt
        slope = np.abs(np.gradient(s)) / step                             # cents per second
        slope = uniform_filter1d(slope, 9, mode="nearest")
        w = np.clip((900.0 - slope) / 600.0, 0, 1)                        # steady: full correction; gliding fast: none
        w *= np.clip((none_above - np.abs(d)) / (none_above - full_below), 0, 1)   # far from any scale note (a note sung on purpose off the scale, a slip): none
        cr = -strength * d * w
        e = min(6, (b - a) // 3); ramp = np.ones(b - a); ramp[:e] = np.linspace(0, 1, e); ramp[-e:] = np.linspace(1, 0, e)
        cr = uniform_filter1d(cr, 9, mode="nearest") * ramp               # no steps, and nothing at the edges of the sound
        corr[a:b] = cr
        st = w > 0.7
        info["steady_frames_left_alone_off_scale"] += int(np.sum((np.clip((900.0 - slope) / 600.0, 0, 1) > 0.7) & (np.abs(d) >= none_above)))
        dev_before += list(np.abs(d[st])); dev_after += list(np.abs(d[st] + cr[st]))
        info["frames_corrected"] += int(np.sum(np.abs(cr) > 3))
    db_, da_ = np.array(dev_before), np.array(dev_after)
    if len(db_):
        info.update(held_frames=int(len(db_)), held_median_cents_before=round(float(np.median(db_)), 1), held_median_cents_after=round(float(np.median(da_)), 1),
                    held_within_15c_before=round(float(100 * np.mean(db_ < 15)), 0), held_within_15c_after=round(float(100 * np.mean(da_ < 15)), 0),
                    largest_shift_cents=round(float(np.abs(corr).max()), 0))
    return corr, info


def tune_natural(x, sr, strength=0.6, step=0.005, full_below=100.0, none_above=160.0):
    """Pitch correction by tiny speed changes on held notes, re-timed at the next quiet moment. No resynthesis."""
    ts, f = praat_pitch(x, sr, step)
    corr, info = correction_curve(ts, f, strength, step=step, full_below=full_below, none_above=none_above)
    n = len(x); idx = np.arange(n)
    cs = np.interp(idx / sr, ts, corr, left=0, right=0)
    r = 2.0 ** (cs / 1200.0) - 1.0
    blk = int(0.005 * sr); nb = n // blk
    en = np.sqrt(np.mean(x[:nb * blk].reshape(nb, blk) ** 2, 1)) + 1e-9
    delta = np.zeros(n); xf = []; carry = 0.0
    isl = runs_of(np.abs(cs) > 1e-6)
    drift = []
    for q, (a, b) in enumerate(isl):
        seg = np.cumsum(r[a:b]) + carry; delta[a:b] = seg; end = float(seg[-1]); drift.append(np.abs(seg).max())
        nxt = isl[q + 1][0] if q + 1 < len(isl) else n
        if nxt - b < int(0.03 * sr): delta[b:nxt] = end; carry = end; continue      # no room to re-time yet: carry the offset on
        lim = min(b + int(0.12 * sr), nxt - int(0.012 * sr))
        b0, b1 = b // blk, max(b // blk + 1, lim // blk)
        p = (b0 + int(np.argmin(en[b0:b1 + 1]))) * blk; p = int(np.clip(p, b, max(b, lim)))
        delta[b:p] = end; xf.append((p, end)); carry = 0.0
    xu = resample_poly(x, 4, 1); gu = np.arange(len(xu))
    y = np.interp((idx + delta) * 4.0, gu, xu)
    L = int(0.006 * sr)
    for p, end in xf:                                                    # glide back to the original timing at a quiet point
        m = min(L, n - p)
        if m <= 1: continue
        old = np.interp((idx[p:p + m] + end) * 4.0, gu, xu); g = np.linspace(0, 1, m)
        y[p:p + m] = old * (1 - g) + y[p:p + m] * g
    info.update(strength=strength, timing_offset_ms_max=round(float(1000 * max(drift) / sr), 1) if drift else 0.0,
                timing_offset_ms_median=round(float(1000 * np.median(drift) / sr), 2) if drift else 0.0, notes_touched=len(isl))
    return y, info


def hold_limiter(x, thr, sr, look=0.005, hold=0.015, release_db_per_s=40.0):
    """Peak control whose gain is held for `hold` after each peak, so it never follows single pitch periods or bass
    cycles. Returns (y, gain_dB at 1 ms steps)."""
    a = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    Lk, H = int(look * sr), int(hold * sr); size = Lk + H + 1
    env = maximum_filter1d(a, size=size, origin=(H - Lk) // 2, mode="constant")   # max over [n - hold, n + look]
    g = np.minimum(1.0, thr / np.maximum(env, 1e-12))
    ms = int(sr / 1000); nb = len(g) // ms
    gd = 20 * np.log10(g[:nb * ms].reshape(nb, ms).min(1))               # 1 ms steps, worst case in each
    step = release_db_per_s / 1000.0; out = np.empty(nb); cur = 0.0
    for i in range(nb):
        cur = min(gd[i], cur + step); out[i] = cur
    k = max(3, int(look * 1000) | 1)
    w = np.hanning(k + 2)[1:-1]; w /= w.sum()
    sm = np.minimum(np.convolve(np.pad(out, k // 2, mode="edge"), w, "valid"), 0.0)
    gs = np.interp(np.arange(len(a)), (np.arange(nb) + 0.5) * ms, sm)
    lin = 10 ** (gs / 20)
    return (x * lin[:, None] if x.ndim == 2 else x * lin), sm

#!/usr/bin/env python3
"""Professional mix for Old Motorola.

Stems are timeline-aligned 44.1 kHz stereo. The instrumental is a produced
128 BPM record, so every delay is an exact note value of that tempo.

  Lead vocals (Lead 1, Lead 2, Lead 3): one quiet eighth-note repeat.
    The line is said again just after, without a trailing wash.
  Adlibs: dry, a little under the lead, with one quiet dotted-eighth repeat.

Lead 3 is the Motorola section: narrowband, lightly overdriven, mono.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d, uniform_filter1d

SR = 44100
BPM = 128.0
HERE = Path(__file__).resolve().parent
# Stems live next to this file in ./stems, or in the scratch folder used to build the master.
STEMS = HERE / "stems" if (HERE / "stems").exists() else Path("/tmp/motorola/stems")
OUT = HERE / "out" if (HERE / "out").exists() else HERE

# Note lengths in samples. 128 BPM at 44.1 kHz is an exact quarter of
# 20671.875 samples; rounding leaves an error under 0.002 ms.
QUARTER = int(round(SR * 60.0 / BPM))
EIGHTH = int(round(SR * 60.0 / BPM / 2.0))
DOTTED_EIGHTH = int(round(SR * 60.0 / BPM * 0.75))

# How far in front of the beat each stem sits, measured in the 1.6–5 kHz
# presence band after tonal processing. This is the clarity range.
# Leads sit this far in front of the beat in the 1.6–5 kHz clarity band.
LEAD_PRESENCE_DB = 6.0
# Adlibs and the telephone lead are then set from the lead's own loudness.
ADLIB_UNDER_LEAD_DB = 10.0
PHONE_UNDER_LEAD_DB = 1.0

LEAD_SEND_DB = -12.5
ADLIB_SEND_DB = -14.0
LEAD_FEEDBACK = 0.12
ADLIB_FEEDBACK = 0.12
LEAD_DUCK_DB = 6.0
ADLIB_DUCK_DB = 3.5


def db(x: float) -> float:
    return 20.0 * math.log10(max(x, 1e-12))


def lin(db_val: float) -> float:
    return 10.0 ** (db_val / 20.0)


def load_wav(path: Path, n: int | None = None) -> np.ndarray:
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-f", "f32le", "-ac", "2", "-ar", str(SR), "pipe:1",
    ]
    raw = subprocess.check_output(cmd)
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float32)
    if n is None:
        return x
    if len(x) < n:
        x = np.pad(x, ((0, n - len(x)), (0, 0)))
    return np.ascontiguousarray(x[:n])


def biquad_sos(b: np.ndarray, a: np.ndarray) -> np.ndarray:
    return signal.tf2sos(b, a)


def design(kind: str, freq: float, q: float = 0.707, gain_db: float = 0.0) -> np.ndarray:
    w0 = 2.0 * math.pi * freq / SR
    cw, sw = math.cos(w0), math.sin(w0)
    alpha = sw / (2.0 * q)
    if kind == "hp":
        b = np.array([(1 + cw) / 2, -(1 + cw), (1 + cw) / 2])
        a = np.array([1 + alpha, -2 * cw, 1 - alpha])
    elif kind == "lp":
        b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2])
        a = np.array([1 + alpha, -2 * cw, 1 - alpha])
    elif kind == "peak":
        A = 10.0 ** (gain_db / 40.0)
        b = np.array([1 + alpha * A, -2 * cw, 1 - alpha * A])
        a = np.array([1 + alpha / A, -2 * cw, 1 - alpha / A])
    elif kind == "hs":
        A = 10.0 ** (gain_db / 40.0)
        sq = 2.0 * math.sqrt(A) * alpha
        b = np.array([
            A * ((A + 1) + (A - 1) * cw + sq),
            -2 * A * ((A - 1) + (A + 1) * cw),
            A * ((A + 1) + (A - 1) * cw - sq),
        ])
        a = np.array([
            (A + 1) - (A - 1) * cw + sq,
            2 * ((A - 1) - (A + 1) * cw),
            (A + 1) - (A - 1) * cw - sq,
        ])
    elif kind == "ls":
        A = 10.0 ** (gain_db / 40.0)
        sq = 2.0 * math.sqrt(A) * alpha
        b = np.array([
            A * ((A + 1) - (A - 1) * cw + sq),
            2 * A * ((A - 1) - (A + 1) * cw),
            A * ((A + 1) - (A - 1) * cw - sq),
        ])
        a = np.array([
            (A + 1) + (A - 1) * cw + sq,
            -2 * ((A - 1) + (A + 1) * cw),
            (A + 1) + (A - 1) * cw - sq,
        ])
    else:
        raise ValueError(kind)
    return biquad_sos(b, a)


def sos_chain(parts: list[np.ndarray]) -> np.ndarray:
    return np.vstack(parts)


def apply_sos(x: np.ndarray, sos: np.ndarray) -> np.ndarray:
    y = signal.sosfilt(sos, x, axis=0).astype(np.float32)
    return y


def mono(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=1).astype(np.float32)


def frame_rms(x: np.ndarray, win: int) -> np.ndarray:
    m = mono(x) if x.ndim == 2 else x
    power = uniform_filter1d(m.astype(np.float64) ** 2, size=win, mode="nearest")
    return np.sqrt(power + 1e-12).astype(np.float32)


def active_mask(x: np.ndarray, thresh_db: float = -42.0, win_ms: float = 30.0, dilate_ms: float = 80.0) -> np.ndarray:
    win = max(1, int(SR * win_ms / 1000.0))
    rms = frame_rms(x, win)
    mask = rms > lin(thresh_db)
    dil = max(1, int(SR * dilate_ms / 1000.0))
    # Dilate so word edges stay inside the measurement.
    mask = maximum_filter1d(mask.astype(np.uint8), size=dil, mode="nearest").astype(bool)
    return mask


def band_rms(x: np.ndarray, f1: float, f2: float, mask: np.ndarray | None = None) -> float:
    sos = signal.butter(4, [f1, f2], btype="band", fs=SR, output="sos")
    m = mono(x) if x.ndim == 2 else x
    y = signal.sosfilt(sos, m.astype(np.float64))
    if mask is not None:
        if not np.any(mask):
            return 0.0
        y = y[mask]
    return float(np.sqrt(np.mean(y * y) + 1e-20))


def k_weight(x: np.ndarray) -> np.ndarray:
    """BS.1770-style weighting, designed at this sample rate."""
    shelf = design("hs", 1500.0, q=0.71, gain_db=4.0)
    hp = design("hp", 38.0, q=0.5)
    y = apply_sos(x, sos_chain([shelf, hp, hp]))
    return y


def integrated_db(x: np.ndarray, mask: np.ndarray | None = None) -> float:
    y = k_weight(x)
    p = (y.astype(np.float64) ** 2).mean(axis=1)
    if mask is not None:
        if not np.any(mask):
            return -120.0
        p = p[mask]
    return float(10.0 * np.log10(np.mean(p) + 1e-20))


def narrow(x: np.ndarray, side_gain: float) -> np.ndarray:
    mid = (x[:, 0] + x[:, 1]) * 0.5
    side = (x[:, 0] - x[:, 1]) * 0.5 * side_gain
    out = np.empty_like(x)
    out[:, 0] = mid + side
    out[:, 1] = mid - side
    return out


def envelope_db(x: np.ndarray, attack_ms: float, release_ms: float, hop: int = 32) -> np.ndarray:
    m = np.abs(mono(x) if x.ndim == 2 else x).astype(np.float64)
    n = len(m) // hop
    if n < 2:
        return np.full(len(m), -120.0, dtype=np.float32)
    frames = m[: n * hop].reshape(n, hop).max(axis=1)
    att = math.exp(-hop / (SR * attack_ms / 1000.0))
    rel = math.exp(-hop / (SR * release_ms / 1000.0))
    env = np.empty(n, dtype=np.float64)
    e = frames[0]
    for i, v in enumerate(frames):
        c = att if v > e else rel
        e = c * e + (1.0 - c) * v
        env[i] = e
    full = np.repeat(env, hop)
    if len(full) < len(m):
        full = np.pad(full, (0, len(m) - len(full)), mode="edge")
    return (20.0 * np.log10(full[: len(m)] + 1e-12)).astype(np.float32)


def smooth_db_gain(gain_db_frames: np.ndarray, attack_ms: float, release_ms: float, hop: int) -> np.ndarray:
    att = math.exp(-hop / (SR * max(attack_ms, 0.1) / 1000.0))
    rel = math.exp(-hop / (SR * max(release_ms, 0.1) / 1000.0))
    out = np.empty_like(gain_db_frames)
    g = float(gain_db_frames[0])
    for i, target in enumerate(gain_db_frames):
        # Attack when reducing, release when recovering.
        c = att if target < g else rel
        g = c * g + (1.0 - c) * float(target)
        out[i] = g
    return out


def compressor(x: np.ndarray, thresh_db: float, ratio: float, attack_ms: float,
               release_ms: float, knee_db: float = 8.0) -> tuple[np.ndarray, float]:
    hop = 32
    level = envelope_db(x, attack_ms=1.0, release_ms=8.0, hop=hop)
    # Resample level to hops (envelope_db already upsampled; take hop centers).
    hops = level[::hop]
    over = hops - thresh_db
    gain = np.zeros_like(hops)
    half = knee_db / 2.0
    hard = over > half
    soft = (over > -half) & ~hard
    gain[hard] = -(1.0 - 1.0 / ratio) * over[hard]
    if np.any(soft):
        a = over[soft] + half
        gain[soft] = (1.0 / ratio - 1.0) * (a * a) / (2.0 * knee_db)
    smoothed = smooth_db_gain(gain, attack_ms, release_ms, hop)
    full = np.repeat(smoothed, hop)
    if len(full) < len(x):
        full = np.pad(full, (0, len(x) - len(full)), mode="edge")
    full = full[: len(x)]
    g = (10.0 ** (full / 20.0)).astype(np.float32)
    y = x * g[:, None]
    active = level > -45.0
    gr = float(-smoothed[active[::hop][: len(smoothed)]].mean()) if np.any(active) else 0.0
    return y.astype(np.float32), gr


def vocal_rider(x: np.ndarray, max_boost_db: float = 4.5, max_cut_db: float = 3.5) -> np.ndarray:
    win = int(0.18 * SR)
    rms = frame_rms(x, win)
    mask = active_mask(x, thresh_db=-40.0, win_ms=40.0, dilate_ms=40.0)
    if np.count_nonzero(mask) < SR // 5:
        return x
    target = float(np.percentile(rms[mask], 72))
    ratio = np.ones_like(rms)
    loud = rms > lin(-48.0)
    ratio[loud] = target / np.maximum(rms[loud], 1e-6)
    gain_db = np.clip(20.0 * np.log10(ratio + 1e-12), -max_cut_db, max_boost_db)
    # No boost on silence.
    gain_db[~mask] = 0.0
    # Smooth ~50 ms.
    gain_db = uniform_filter1d(gain_db, size=int(0.05 * SR), mode="nearest")
    g = (10.0 ** (gain_db / 20.0)).astype(np.float32)
    return (x * g[:, None]).astype(np.float32)


def deesser(x: np.ndarray, freq: float = 6500.0, q: float = 1.3,
            thresh_db: float = -22.0, ratio: float = 4.0) -> np.ndarray:
    band_sos = sos_chain([design("hp", freq * 0.7, q=0.7), design("lp", freq * 1.5, q=0.7)])
    band = apply_sos(x, band_sos)
    level = envelope_db(band, 2.0, 40.0, hop=16)
    hops = level[::16]
    over = hops - thresh_db
    gain = np.zeros_like(hops)
    hot = over > 0
    gain[hot] = -(1.0 - 1.0 / ratio) * over[hot]
    smoothed = smooth_db_gain(gain, 3.0, 50.0, 16)
    full = np.repeat(smoothed, 16)
    if len(full) < len(x):
        full = np.pad(full, (0, len(x) - len(full)), mode="edge")
    g = (10.0 ** (full[: len(x)] / 20.0)).astype(np.float32)
    # Reduce only the sibilant band, leave the rest of the vocal alone.
    return (x - band + band * g[:, None]).astype(np.float32)


def exciter(x: np.ndarray, amount: float = 0.9, drive: float = 2.6, hp_hz: float = 2200.0) -> np.ndarray:
    hp = apply_sos(x, sos_chain([design("hp", hp_hz, 0.707), design("hp", hp_hz, 0.707)]))
    # Unity small-signal gain, so this adds harmonics rather than more level.
    saturated = np.tanh(drive * hp) / drive
    harmonics = (saturated - hp).astype(np.float32)
    return (x + amount * harmonics).astype(np.float32)


def match_active_rms(processed: np.ndarray, reference: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if not np.any(mask):
        return processed
    a = float(np.sqrt(np.mean(mono(processed)[mask] ** 2) + 1e-12))
    b = float(np.sqrt(np.mean(mono(reference)[mask] ** 2) + 1e-12))
    if a < 1e-8:
        return processed
    return (processed * (b / a)).astype(np.float32)


def one_pole_coeffs(hp_hz: float, lp_hz: float) -> tuple[float, float]:
    hp_c = math.exp(-2.0 * math.pi * hp_hz / SR)
    lp_a = 1.0 - math.exp(-2.0 * math.pi * lp_hz / SR)
    return hp_c, lp_a


def comb_wet(x: np.ndarray, delay: int, feedback: float, hp_hz: float, lp_hz: float) -> np.ndarray:
    """Wet-only feedback delay. Output is the repeats, not the dry signal."""
    n = len(x)
    buf = np.zeros(delay, dtype=np.float64)
    out = np.empty(n, dtype=np.float64)
    hp_c, lp_a = one_pole_coeffs(hp_hz, lp_hz)
    idx = 0
    lp = 0.0
    hp = 0.0
    prev = 0.0
    fb = float(feedback)
    for i in range(n):
        delayed = buf[idx]
        lp += lp_a * (delayed - lp)
        hp = hp_c * (hp + lp - prev)
        prev = lp
        out[i] = hp
        v = float(x[i]) + fb * hp
        if v > 1.5:
            v = 1.5
        elif v < -1.5:
            v = -1.5
        if abs(v) < 1e-12:
            v = 0.0
        buf[idx] = v
        idx += 1
        if idx == delay:
            idx = 0
    return out.astype(np.float32)


def pingpong(x: np.ndarray, delay: int, feedback: float, hp_hz: float, lp_hz: float) -> np.ndarray:
    """Dotted echoes that alternate sides, with a little center so mono still has them."""
    n = len(x)
    buf_l = np.zeros(delay, dtype=np.float64)
    buf_r = np.zeros(delay, dtype=np.float64)
    out_l = np.empty(n, dtype=np.float64)
    out_r = np.empty(n, dtype=np.float64)
    hp_c, lp_a = one_pole_coeffs(hp_hz, lp_hz)
    i_l = i_r = 0
    lp_l = lp_r = hp_l = hp_r = prev_l = prev_r = 0.0
    fb = float(feedback)

    def filt(delayed: float, lp: float, hp: float, prev: float) -> tuple[float, float, float, float]:
        lp += lp_a * (delayed - lp)
        hp = hp_c * (hp + lp - prev)
        prev = lp
        return hp, lp, hp, prev

    for i in range(n):
        f_l, lp_l, hp_l, prev_l = filt(buf_l[i_l], lp_l, hp_l, prev_l)
        f_r, lp_r, hp_r, prev_r = filt(buf_r[i_r], lp_r, hp_r, prev_r)
        out_l[i] = f_l
        out_r[i] = f_r
        w_l = float(x[i]) + fb * f_r
        w_r = fb * f_l
        if abs(w_l) < 1e-12:
            w_l = 0.0
        if abs(w_r) < 1e-12:
            w_r = 0.0
        buf_l[i_l] = max(-1.5, min(1.5, w_l))
        buf_r[i_r] = max(-1.5, min(1.5, w_r))
        i_l += 1
        i_r += 1
        if i_l == delay:
            i_l = 0
        if i_r == delay:
            i_r = 0
    # Crossfeed keeps the echo audible in mono and stops it living only on one side.
    left = out_l + 0.42 * out_r
    right = out_r + 0.42 * out_l
    return np.stack([left, right], axis=1).astype(np.float32)


def duck_gain(source: np.ndarray, depth_db: float) -> np.ndarray:
    """1.0 when the source is silent, falling by depth_db when it is singing."""
    level = envelope_db(source, attack_ms=12.0, release_ms=140.0, hop=32)
    # Map a normal singing level (around the active 80th percentile) to full duck.
    audible = level > -50.0
    if not np.any(audible):
        return np.ones(len(source), dtype=np.float32)
    ref = float(np.percentile(level[audible], 75))
    # Presence 0 at ref-18 dB, 1 at ref.
    presence = np.clip((level - (ref - 18.0)) / 18.0, 0.0, 1.0)
    min_g = lin(-depth_db)
    gain = 1.0 + presence * (min_g - 1.0)
    return gain.astype(np.float32)


def safety_ceiling(x: np.ndarray, ceiling_db: float = -6.0) -> tuple[np.ndarray, float]:
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    ceiling = lin(ceiling_db)
    if peak <= ceiling:
        return x, 0.0
    # Smooth peak trim, not a hard clip.
    mag = np.max(np.abs(x), axis=1)
    env = maximum_filter1d(mag, size=int(0.008 * SR), mode="nearest")
    env = np.maximum(uniform_filter1d(env, size=int(0.004 * SR), mode="nearest"), 1e-8)
    g = np.minimum(1.0, ceiling / env).astype(np.float32)
    over = db(peak) - ceiling_db
    return (x * g[:, None]).astype(np.float32), over


def process_lead(x: np.ndarray) -> np.ndarray:
    raw = x
    mask = active_mask(x, -42.0)
    sos = sos_chain([
        design("hp", 85.0, 0.707),
        design("hp", 85.0, 0.707),
        design("peak", 260.0, 0.9, -2.4),
        design("peak", 950.0, 0.75, 3.6),
        design("peak", 1900.0, 0.85, 5.2),
        design("peak", 3400.0, 1.0, 5.6),
        design("hs", 8000.0, 0.71, 2.0),
    ])
    y = apply_sos(x, sos)
    y = narrow(y, 0.82)
    y = exciter(y, amount=1.05, drive=2.7, hp_hz=2300.0)
    y = deesser(y, freq=6200.0, thresh_db=-24.0, ratio=3.5)
    y = vocal_rider(y, max_boost_db=4.5, max_cut_db=3.2)
    y, gr = compressor(y, thresh_db=-18.0, ratio=2.6, attack_ms=14.0, release_ms=110.0, knee_db=8.0)
    y = match_active_rms(y, raw, mask)
    y = trim_tail(y, open_db=-42.0, release_ms=110.0)
    print(f"    lead compressor average GR {gr:.2f} dB")
    return y


def trim_tail(x: np.ndarray, open_db: float = -36.0, release_ms: float = 80.0) -> np.ndarray:
    """Close behind the word so a room tail does not hang into the next line."""
    level = envelope_db(x, attack_ms=2.0, release_ms=release_ms, hop=16)
    depth = np.clip((open_db - level) / 10.0, 0.0, 1.0)
    gain = (10.0 ** ((-24.0 * depth) / 20.0)).astype(np.float32)
    return (x * gain[:, None]).astype(np.float32)


def process_adlib(x: np.ndarray) -> np.ndarray:
    raw = x
    mask = active_mask(x, -44.0)
    sos = sos_chain([
        design("hp", 110.0, 0.707),
        design("hp", 110.0, 0.707),
        design("peak", 280.0, 0.9, -2.0),
        design("peak", 1100.0, 0.8, 3.2),
        design("peak", 2500.0, 0.9, 4.6),
        design("peak", 4200.0, 1.1, 3.4),
        design("hs", 9000.0, 0.71, 2.2),
    ])
    y = apply_sos(x, sos)
    y = exciter(y, amount=0.7, drive=2.3, hp_hz=2600.0)
    y = deesser(y, freq=6800.0, thresh_db=-26.0, ratio=3.0)
    y = vocal_rider(y, max_boost_db=5.0, max_cut_db=3.0)
    y, gr = compressor(y, thresh_db=-20.0, ratio=2.8, attack_ms=10.0, release_ms=90.0, knee_db=6.0)
    y = match_active_rms(y, raw, mask)
    y = trim_tail(y, open_db=-34.0, release_ms=70.0)
    print(f"    adlib compressor average GR {gr:.2f} dB")
    return y


def process_phone(x: np.ndarray) -> np.ndarray:
    """Old handset: mono, narrow, a little speaker grit, words still intelligible."""
    mid = mono(x)
    # Keep the channel that sums cleanly. These takes are not a hard opposite-phase pair.
    src = np.stack([mid, mid], axis=1).astype(np.float32)
    sos = sos_chain([
        design("hp", 420.0, 0.707),
        design("hp", 420.0, 0.707),
        design("lp", 3400.0, 0.707),
        design("lp", 3400.0, 0.707),
        design("peak", 1100.0, 1.3, 2.8),
        design("peak", 1800.0, 1.6, 2.2),
        design("peak", 2600.0, 2.0, -1.5),
    ])
    y = apply_sos(src, sos)
    drive = 1.7
    y = (np.tanh(drive * y) / drive).astype(np.float32)
    y, gr = compressor(y, thresh_db=-16.0, ratio=3.4, attack_ms=6.0, release_ms=70.0, knee_db=6.0)
    print(f"    phone compressor average GR {gr:.2f} dB")
    return y


def process_beat(x: np.ndarray) -> np.ndarray:
    sos = sos_chain([
        design("hp", 28.0, 0.707),
        design("ls", 90.0, 0.7, -0.7),
        design("peak", 350.0, 0.9, -0.8),
        design("hs", 10000.0, 0.71, 0.7),
    ])
    return apply_sos(x, sos)


def duck_beat(beat: np.ndarray, vocal: np.ndarray, depth_db: float = 2.3) -> np.ndarray:
    """Leave the sub alone and ease the mids when a vocal is in front of them."""
    low = apply_sos(beat, sos_chain([design("lp", 180.0, 0.707), design("lp", 180.0, 0.707)]))
    high = (beat - low).astype(np.float32)
    g = duck_gain(vocal, depth_db)
    # duck_gain goes to about -depth. Scale so the maximum move is depth_db.
    return (low + high * g[:, None]).astype(np.float32)


def presence_gain(stem: np.ndarray, beat: np.ndarray, stem_mask: np.ndarray,
                  beat_mask: np.ndarray, delta_db: float, label: str) -> float:
    both = stem_mask & beat_mask
    use = both if np.count_nonzero(both) > SR // 2 else stem_mask
    s = band_rms(stem, 1600.0, 5000.0, use)
    b = band_rms(beat, 1600.0, 5000.0, use if np.any(use & beat_mask) else beat_mask)
    if s < 1e-8 or b < 1e-8:
        print(f"    {label}: could not measure presence, gain 0 dB")
        return 1.0
    current = db(s) - db(b)
    need = delta_db - current
    need = float(np.clip(need, -6.0, 16.0))
    print(f"    {label}: presence vs beat {current:+.1f} dB, applying {need:+.1f} dB to reach {delta_db:+.1f}")
    return lin(need)


def limiter(x: np.ndarray, ceiling_db: float = -1.05, release_ms: float = 80.0) -> tuple[np.ndarray, float]:
    ceiling = lin(ceiling_db)
    mag = np.max(np.abs(x), axis=1).astype(np.float64)
    # 6 ms lookahead via a forward max.
    look = int(0.006 * SR)
    peak = np.maximum(mag, np.roll(maximum_filter1d(mag, size=look * 2 + 1, mode="nearest"), -look))
    hop = 32
    n = len(peak) // hop
    frames = peak[: n * hop].reshape(n, hop).max(axis=1)
    rel = math.exp(-hop / (SR * release_ms / 1000.0))
    env = np.empty(n, dtype=np.float64)
    e = 0.0
    for i, v in enumerate(frames):
        if v > e:
            e = v
        else:
            e = rel * e + (1.0 - rel) * v
        env[i] = e
    gain = np.ones(n, dtype=np.float64)
    hot = env > ceiling
    gain[hot] = ceiling / env[hot]
    full = np.repeat(gain, hop)
    if len(full) < len(x):
        full = np.pad(full, (0, len(x) - len(full)), mode="edge")
    g = full[: len(x)].astype(np.float32)
    gr = float(20.0 * np.log10(g.min() + 1e-12) * -1.0)
    return (x * g[:, None]).astype(np.float32), gr


def spectrum_profile(x: np.ndarray, mask: np.ndarray | None = None) -> list[tuple[str, float]]:
    bands = [
        (40, 80), (80, 160), (160, 300), (300, 600), (600, 1200),
        (1200, 2500), (2500, 5000), (5000, 8000), (8000, 12000),
    ]
    m = mono(x).astype(np.float64)
    if mask is not None and np.any(mask):
        # Gate by zeroing outside the mask so silence does not dominate.
        m = m.copy()
        m[~mask] = 0.0
    frame, hop = 4096, 2048
    window = np.hanning(frame)
    acc = None
    count = 0
    for i in range(0, len(m) - frame, hop):
        seg = m[i:i + frame]
        if np.max(np.abs(seg)) < lin(-50):
            continue
        mag = np.abs(np.fft.rfft(seg * window)) ** 2
        acc = mag if acc is None else acc + mag
        count += 1
    rows = []
    if acc is None or count == 0:
        return rows
    acc /= count
    freqs = np.fft.rfftfreq(frame, 1.0 / SR)
    vals = []
    for a, b in bands:
        sl = acc[(freqs >= a) & (freqs < b)]
        vals.append(10.0 * np.log10(sl.mean() + 1e-20))
    peak = max(vals)
    for (a, b), v in zip(bands, vals):
        rows.append((f"{a}-{b}", v - peak))
    return rows


def short_term_lufs(x: np.ndarray, win_s: float = 3.0, hop_s: float = 1.0) -> np.ndarray:
    y = k_weight(x).astype(np.float64)
    power = (y ** 2).mean(axis=1)
    win = int(win_s * SR)
    hop = int(hop_s * SR)
    vals = []
    for i in range(0, len(power) - win, hop):
        vals.append(10.0 * np.log10(power[i:i + win].mean() + 1e-20))
    return np.array(vals, dtype=np.float64)


def self_test() -> None:
    n = SR * 3
    burst = np.zeros(n, dtype=np.float32)
    t = np.arange(800) / SR
    burst[2000:2800] = (0.5 * np.sin(2 * math.pi * 1000 * t)).astype(np.float32)
    wet = comb_wet(burst, EIGHTH, 0.0, 20.0, 18000.0)
    loud = np.where(np.abs(wet) > 0.05)[0]
    err = int(loud[0] - (2000 + EIGHTH))
    print(f"delay self-test: eighth={EIGHTH} samples ({EIGHTH / SR * 1000:.2f} ms), "
          f"dotted={DOTTED_EIGHTH} ({DOTTED_EIGHTH / SR * 1000:.2f} ms), "
          f"repeat error {err} samples ({err / SR * 1000:.3f} ms)")
    if abs(err) > 2:
        raise SystemExit("delay timing self-test failed")


def render() -> None:
    self_test()
    beat_path = next(STEMS.glob("FREE_*.wav"))
    print("loading")
    beat_raw = load_wav(beat_path)
    n = len(beat_raw)
    lead1_raw = load_wav(STEMS / "LEAD 1.wav", n)
    lead2_raw = load_wav(STEMS / "LEAD 2.wav", n)
    lead3_raw = load_wav(STEMS / "LEAD 3 Telephone .wav", n)
    adlib_raw = load_wav(STEMS / "ADLIBS.wav", n)

    print("processing lead 1")
    lead1 = process_lead(lead1_raw)
    print("processing lead 2")
    lead2 = process_lead(lead2_raw)
    print("processing adlibs")
    adlib = process_adlib(adlib_raw)
    print("processing telephone lead")
    phone = process_phone(lead3_raw)
    print("processing beat")
    beat = process_beat(beat_raw)

    print("\nspectrum of lead 1, dB below its loudest band (active audio)")
    mask1 = active_mask(lead1_raw, -38.0)
    before = spectrum_profile(lead1_raw, mask1)
    after = spectrum_profile(lead1, mask1)
    for (name, b), (_, a) in zip(before, after):
        print(f"    {name:>12}  raw {b:7.1f}   processed {a:7.1f}")

    beat_full = active_mask(beat_raw, thresh_db=-20.0, win_ms=80.0, dilate_ms=100.0)
    m1 = active_mask(lead1_raw, -38.0)
    m2 = active_mask(lead2_raw, -38.0)
    ma = active_mask(adlib_raw, -40.0)
    m3 = active_mask(lead3_raw, -40.0)

    print("\nbalance")
    g1 = presence_gain(lead1, beat, m1, beat_full, LEAD_PRESENCE_DB, "lead 1")
    g2 = presence_gain(lead2, beat, m2, beat_full, LEAD_PRESENCE_DB, "lead 2")
    lead1 *= g1
    lead2 *= g2

    def active_lufs(stem: np.ndarray, mask: np.ndarray) -> float:
        return integrated_db(stem, mask)

    lead_ref = active_lufs(lead1, m1)
    ad_now = active_lufs(adlib, ma)
    ph_now = active_lufs(phone, m3)
    ad_need = float(np.clip((lead_ref - ADLIB_UNDER_LEAD_DB) - ad_now, -8.0, 12.0))
    ph_need = float(np.clip((lead_ref - PHONE_UNDER_LEAD_DB) - ph_now, -8.0, 14.0))
    adlib *= lin(ad_need)
    phone *= lin(ph_need)

    def even_out(stem: np.ndarray, mask: np.ndarray, label: str) -> np.ndarray:
        if np.count_nonzero(mask) < SR // 5:
            return stem
        level = envelope_db(stem, attack_ms=3.0, release_ms=20.0, hop=32)
        ref = float(np.percentile(level[mask], 78))
        y, gr = compressor(
            stem, thresh_db=ref - 5.0, ratio=2.4,
            attack_ms=8.0, release_ms=90.0, knee_db=6.0,
        )
        y = match_active_rms(y, stem, mask)
        print(f"    {label} leveler GR {gr:.2f} dB around {ref:.1f} dB")
        return y

    adlib = even_out(adlib, ma, "adlib")
    phone = even_out(phone, m3, "telephone")
    print(f"    lead 1 active {lead_ref:.1f} LUFS")
    print(f"    adlibs were {ad_now:.1f}, moved {ad_need:+.1f} dB to sit {ADLIB_UNDER_LEAD_DB:.1f} under the lead")
    print(f"    telephone was {ph_now:.1f}, moved {ph_need:+.1f} dB to sit {PHONE_UNDER_LEAD_DB:.1f} under the lead")

    # Only the tips. A deep ceiling here would dull the consonants.
    lead1, o1 = safety_ceiling(lead1, -3.0)
    lead2, o2 = safety_ceiling(lead2, -3.0)
    adlib, oa = safety_ceiling(adlib, -6.0)
    phone, o3 = safety_ceiling(phone, -3.0)
    print(f"    safety trim dB  lead1 {o1:.2f}  lead2 {o2:.2f}  adlib {oa:.2f}  phone {o3:.2f}")

    lead_bus = (lead1 + lead2 + phone).astype(np.float32)
    print("delays")
    # One thinner repeat, an eighth note later. The band is narrowed so it
    # does not bloom into a second vocal.
    lead_wet = comb_wet(mono(lead_bus), EIGHTH, LEAD_FEEDBACK, 500.0, 4800.0)
    lead_duck = duck_gain(lead_bus, LEAD_DUCK_DB)
    lead_delay = np.stack([lead_wet, lead_wet], axis=1) * lin(LEAD_SEND_DB) * lead_duck[:, None]

    # One timed repeat of the adlib. The band stays wide enough to keep the
    # voice in the echo, and the level stays well behind the dry adlib.
    ad_wet = pingpong(mono(adlib), DOTTED_EIGHTH, ADLIB_FEEDBACK, 450.0, 4500.0)
    ad_duck = duck_gain(lead_bus, 6.0)
    ad_self = duck_gain(adlib, 2.0)
    ad_echo = ad_wet * lin(ADLIB_SEND_DB) * ad_duck[:, None] * ad_self[:, None]

    def masked_rms_db(stem: np.ndarray, mask: np.ndarray) -> float:
        if not np.any(mask):
            return -120.0
        m = mono(stem)[mask]
        return db(float(np.sqrt(np.mean(m.astype(np.float64) ** 2) + 1e-20)))

    delay_mask = active_mask(lead_delay, thresh_db=-36.0, win_ms=40.0, dilate_ms=30.0)
    # Measure the echo where the adlib's repeat actually lands, one dotted eighth later.
    echo_at = np.zeros(len(ma), dtype=bool)
    echo_at[DOTTED_EIGHTH:] = ma[:-DOTTED_EIGHTH]
    print(f"    lead repeat vs dry lead: "
          f"{masked_rms_db(lead_delay, delay_mask) - masked_rms_db(lead_bus, m1 | m2):+.1f} dB")
    print(f"    adlib echo vs dry adlib: "
          f"{masked_rms_db(ad_echo, echo_at) - masked_rms_db(adlib, ma):+.1f} dB")

    print("vocal pocket on the beat")
    beat = duck_beat(beat, lead_bus, depth_db=1.6)

    mix = (beat + lead_bus + adlib + lead_delay + ad_echo).astype(np.float32)

    mix = apply_sos(mix, sos_chain([
        design("hp", 26.0, 0.707),
        design("peak", 280.0, 0.8, -0.5),
        design("hs", 11000.0, 0.71, 0.5),
    ]))

    # Glue raises density, then the peak is put back so the lift is in the
    # body of the mix rather than a hotter peak.
    peak0 = float(np.max(np.abs(mix)) + 1e-9)
    env = envelope_db(mix, attack_ms=5.0, release_ms=30.0, hop=32)
    glue_thresh = float(np.percentile(env, 88))
    mix, glue_gr = compressor(
        mix, thresh_db=glue_thresh - 5.0, ratio=1.7,
        attack_ms=22.0, release_ms=160.0, knee_db=6.0,
    )
    peak1 = float(np.max(np.abs(mix)) + 1e-9)
    mix *= np.float32(peak0 / peak1)
    print(f"    glue GR {glue_gr:.2f} dB, threshold {glue_thresh - 5.0:.1f} dB")

    # Streaming level, with the limiter only catching peaks. Chasing a louder
    # number than the crest factor allows would dull the vocal.
    st = short_term_lufs(mix)
    loud = float(np.percentile(st, 90))
    ceiling_db = -1.15
    max_limit_db = 2.6
    current_peak_db = db(float(np.max(np.abs(mix))))
    # After this much makeup, the tallest peak sits max_limit_db over the ceiling.
    peak_limited_makeup = (ceiling_db + max_limit_db) - current_peak_db
    loudness_makeup = -13.2 - loud
    make = float(np.clip(min(peak_limited_makeup, loudness_makeup), -12.0, 12.0))
    mix *= lin(make)
    print(f"    loud-section level {loud:.1f} LUFS, makeup {make:+.1f} dB "
          f"(peak allows {peak_limited_makeup:+.1f}, target wants {loudness_makeup:+.1f})")

    mix, lim_gr = limiter(mix, ceiling_db=ceiling_db, release_ms=90.0)
    print(f"    limiter max GR {lim_gr:.2f} dB")

    # Report
    print("\nsection levels (K-weighted short term, every 4s)")
    st4_win = 3.0 * SR
    power = (k_weight(mix).astype(np.float64) ** 2).mean(axis=1)
    csum = np.cumsum(np.concatenate([[0.0], power]))
    for t in range(0, int(n / SR) - 3, 4):
        a, b = int(t * SR), int((t + 3) * SR)
        lufs = 10.0 * math.log10((csum[b] - csum[a]) / (b - a) + 1e-20)
        bar = "#" * int(max(0, (lufs + 36) / 1.2))
        print(f"    {t:6.1f}s  {lufs:6.1f}  {bar}")

    peak = float(np.max(np.abs(mix)))
    corr = float(np.corrcoef(mix[:, 0], mix[:, 1])[0, 1])
    mid = (mix[:, 0] + mix[:, 1]) * 0.5
    side = (mix[:, 0] - mix[:, 1]) * 0.5
    mono_drop = db(float(np.sqrt(np.mean(mid ** 2)))) - db(float(np.sqrt(np.mean(mix[:, 0] ** 2))))
    print(f"\npeak {db(peak):.2f} dBFS   L/R corr {corr:.3f}   mono vs left {mono_drop:+.2f} dB")
    print(f"eighth-note lead delay {EIGHTH / SR * 1000:.2f} ms, feedback {LEAD_FEEDBACK}")
    print(f"dotted-eighth adlib echo {DOTTED_EIGHTH / SR * 1000:.2f} ms, feedback {ADLIB_FEEDBACK}")

    # Presence balance in the final mix during singing.
    vocal_only = (lead_bus + adlib).astype(np.float32)
    sing = m1 | m2
    if np.any(sing & beat_full):
        vb = band_rms(vocal_only, 1600, 5000, sing & beat_full)
        bb = band_rms(beat, 1600, 5000, sing & beat_full)
        print(f"final presence, vocals vs beat, while leads sing: {db(vb) - db(bb):+.1f} dB")

    OUT.mkdir(parents=True, exist_ok=True)
    wav_path = OUT / "Old Motorola.wav"
    mp3_path = OUT / "Old Motorola.mp3"
    print("writing", wav_path)
    pcm = mix.astype(np.float32).tobytes()
    meta = [
        "-metadata", "title=Old Motorola",
        "-metadata", "comment=Lead delay is an eighth note at 128 BPM. Adlib echoes are dotted eighths.",
    ]
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
        *meta,
        "-af", "aresample=dither_method=triangular",
        "-c:a", "pcm_s24le",
        str(wav_path),
    ]
    subprocess.run(cmd, input=pcm, check=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(wav_path),
        *meta, "-codec:a", "libmp3lame", "-b:a", "320k",
        str(mp3_path),
    ], check=True)

    print("\nloudness")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(wav_path),
        "-af", "ebur128=framelog=verbose", "-f", "null", "-",
    ], check=False)


if __name__ == "__main__":
    render()

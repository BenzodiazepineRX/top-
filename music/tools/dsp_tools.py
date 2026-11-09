#!/usr/bin/env python3
"""Exact, measurable DSP for vocal stems, effects returns, stem mixing and M/S bus work.

Every subcommand reads a file, writes a 32-bit float WAV at the same sample
rate, and prints what it measured and changed. Run `dsp_tools.py SUBCOMMAND -h`
for all options.

  gain-stage   IN OUT [--target-rms -18] [--against BEAT]  set working level by gated RMS; report vocal vs beat
  hpf          IN OUT --freq 90 [--order 3]                 Butterworth high-pass (order 3 = 18 dB/oct)
  resonances   IN [--fmin 150 --fmax 6000]                  find narrow resonant peaks; print EQ cut suggestions
  dyneq        IN OUT --freq 3500 --q 2                     split-band dynamic cut (harshness only when it flares)
  deess        IN OUT [--low 5500 --high 8500]              band-pass envelope de-esser
  comp2        IN OUT                                       two-stage serial compression: fast peak + smooth "opto-style"
  delay        IN OUT --bpm 92 --note 1/4 [--duck-by LEAD]  tempo-synced (ping-pong) delay return, ducked by the lead vocal
  reverb       IN OUT [--type plate|hall] [--predelay 30]   plate/hall reverb return with pre-delay
  saturate     IN OUT [--drive 6 --even 0.15 --mix 0.3]     oversampled odd/even harmonic saturation
  mix          OUT --track FILE:GAIN_DB [--track ...]       sum stems/returns, sample-aligned, to stereo
  ms-bus       IN OUT [--side-hp 90] [--mid-shelf 9500:2]   mono the sub-bass (side high-pass) + mid-only high shelf

Needs ffmpeg/ffprobe, numpy and scipy.
"""
import argparse
import json
import math
import subprocess
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter, resample_poly, sosfilt, sosfiltfilt, welch

# ---------------------------------------------------------------- file I/O


def read(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                        "stream=sample_rate,channels", "-of", "json", path], capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"Cannot read {path}: {p.stderr.strip()}")
    s = json.loads(p.stdout)["streams"][0]
    sr, ch = int(s["sample_rate"]), int(s["channels"])
    if ch > 2:
        ch = 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "a:0", "-ac", str(ch), "-f", "f32le", "-"],
                         capture_output=True)
    x = np.frombuffer(raw.stdout, dtype="<f4").astype(np.float64).reshape(-1, ch)
    return x, sr


def write(path, x, sr):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    proc = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(x.shape[1]),
                           "-i", "-", "-c:a", "pcm_f32le", path], input=x.astype("<f4").tobytes())
    if proc.returncode != 0:
        sys.exit(f"Could not write {path}")


def db(v, floor=-150.0):
    return 20 * np.log10(np.maximum(np.abs(v), 10 ** (floor / 20)))


def mono(x):
    return x.mean(axis=1) if x.ndim == 2 else x


# ---------------------------------------------------------------- level tools


def block_level(sig, sr, block_ms, mode="rms"):
    """Level per block in dBFS. Returns (levels_db, block_len_samples)."""
    n = max(1, int(sr * block_ms / 1000))
    m = len(sig) // n
    if m == 0:
        return np.array([-150.0]), n
    b = sig[: m * n].reshape(m, n)
    if mode == "peak":
        v = np.abs(b).max(axis=1)
    else:
        v = np.sqrt((b ** 2).mean(axis=1))
    return db(v), n


def gated_rms_db(x, sr, rel_gate=-30.0, abs_gate=-60.0):
    """RMS of the active parts only (50 ms blocks above both gates), in dBFS."""
    lev, _ = block_level(mono(x), sr, 50)
    loud = lev[lev > abs_gate]
    if not len(loud):
        return -150.0
    active = loud[loud > loud.max() + rel_gate]
    return float(10 * np.log10(np.mean(10 ** (active / 10))))


def ar_smooth(v, step_s, attack_ms, release_ms):
    """Asymmetric one-pole smoothing: 'attack' when the value rises, 'release' when it falls."""
    a_att = math.exp(-step_s / max(attack_ms / 1000, 1e-6))
    a_rel = math.exp(-step_s / max(release_ms / 1000, 1e-6))
    out = np.empty_like(v)
    s = float(v[0])
    for i, val in enumerate(v):
        c = a_att if val > s else a_rel
        s = c * s + (1 - c) * val
        out[i] = s
    return out


def to_samples(curve, block, n):
    """Expand a per-block curve to per-sample with linear interpolation."""
    centers = (np.arange(len(curve)) + 0.5) * block
    return np.interp(np.arange(n), centers, curve)


def loudness(path_or_none, x=None, sr=None):
    """Integrated LUFS and true peak via ffmpeg ebur128."""
    import os
    import tempfile
    tmp = None
    if path_or_none is None:
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        write(tmp, x, sr)
        path_or_none = tmp
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path_or_none, "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    if tmp:
        os.remove(tmp)
    s = r.stderr[r.stderr.rindex("Summary:"):] if "Summary:" in r.stderr else ""
    import re
    I = re.search(r"I:\s*(-?[\d.]+)", s)
    tp = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+)", s)
    return (float(I.group(1)) if I else None), (float(tp.group(1)) if tp else None)


# ---------------------------------------------------------------- RBJ biquads (exact cookbook formulas)


def rbj(kind, f0, sr, gain_db=0.0, q=0.7071):
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * f0 / sr
    cw, sw = math.cos(w0), math.sin(w0)
    alpha = sw / (2 * q)
    if kind == "bell":
        b = [1 + alpha * A, -2 * cw, 1 - alpha * A]
        a = [1 + alpha / A, -2 * cw, 1 - alpha / A]
    elif kind == "highshelf":
        sa = 2 * math.sqrt(A) * alpha
        b = [A * ((A + 1) + (A - 1) * cw + sa), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sa)]
        a = [(A + 1) - (A - 1) * cw + sa, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sa]
    elif kind == "lowshelf":
        sa = 2 * math.sqrt(A) * alpha
        b = [A * ((A + 1) - (A - 1) * cw + sa), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sa)]
        a = [(A + 1) + (A - 1) * cw + sa, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sa]
    else:
        raise ValueError(kind)
    b, a = np.array(b) / a[0], np.array(a) / a[0]
    return b, a


# ---------------------------------------------------------------- subcommands


def cmd_gain_stage(a):
    x, sr = read(a.input)
    before = gated_rms_db(x, sr)
    g = a.target_rms - before
    y = x * 10 ** (g / 20)
    peak = float(db(np.abs(y).max()))
    write(a.output, y, sr)
    print(f"Active RMS {before:.1f} dBFS -> {a.target_rms:.1f} dBFS (gain {g:+.2f} dB); peak now {peak:+.1f} dBFS")
    if peak > -1:
        print("Note: peaks are near or above 0 dBFS. Fine inside 32-bit float, but compress before any fixed-point stage.")
    if a.against:
        bx, bsr = read(a.against)
        b_rms = gated_rms_db(bx, bsr)
        vi, _ = loudness(a.output)
        bi, _ = loudness(a.against)
        print(f"Against {a.against}: beat active RMS {b_rms:.1f} dBFS, so vocal sits {a.target_rms - b_rms:+.1f} dB vs beat (RMS)")
        if vi is not None and bi is not None:
            print(f"Loudness: vocal {vi:.1f} LUFS, beat {bi:.1f} LUFS ({vi - bi:+.1f} LU). "
                  "Set the final balance in the mix step and confirm by ear.")


def cmd_hpf(a):
    x, sr = read(a.input)
    sos = butter(a.order, a.freq, btype="highpass", fs=sr, output="sos")
    y = sosfilt(sos, x, axis=0)
    write(a.output, y, sr)
    print(f"High-pass {a.freq:g} Hz, Butterworth order {a.order} ({6 * a.order} dB/oct), -3 dB at {a.freq:g} Hz")


NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def sung_notes(m, sr, cover=0.06):
    """Pitch histogram of a monophonic stem (autocorrelation f0 per 93 ms frame). Returns [(hz, name, pct)]."""
    N, hop = 4096, 2048
    lags = np.arange(int(sr / 1000), int(sr / 70))
    counts = {}
    voiced = 0
    for s in range(0, len(m) - N, hop):
        fr = m[s:s + N] - m[s:s + N].mean()
        if np.sqrt((fr ** 2).mean()) < 1e-3:
            continue
        ac = np.fft.irfft(np.abs(np.fft.rfft(fr, 2 * N)) ** 2)[:N]
        ac /= ac[0] + 1e-12
        seg = ac[lags]
        i = int(np.argmax(seg))
        if seg[i] < 0.6:
            continue
        midi = int(round(69 + 12 * math.log2(sr / lags[i] / 440)))
        counts[midi] = counts.get(midi, 0) + 1
        voiced += 1
    if not voiced:
        return []
    out = [(440 * 2 ** ((k - 69) / 12), f"{NOTE_NAMES[k % 12]}{k // 12 - 1}", 100 * c / voiced)
           for k, c in sorted(counts.items(), key=lambda kv: -kv[1]) if c / voiced >= cover]
    return out[:8]


def cmd_resonances(a):
    x, sr = read(a.input)
    m = mono(x)
    lev, n = block_level(m, sr, 50)
    gate = max(-60, lev.max() - 35)
    act = np.repeat(lev > gate, n)[: len(m)]
    sig = m[: len(act)][act]
    if len(sig) < sr:
        sys.exit("Not enough active audio to analyze.")
    f, p = welch(sig, fs=sr, nperseg=16384, noverlap=8192)
    pdb = 10 * np.log10(p + 1e-30)
    # baseline: 1/3-octave smoothing in log-frequency
    base = np.empty_like(pdb)
    for i, fi in enumerate(f):
        lo, hi = fi * 2 ** (-1 / 6), fi * 2 ** (1 / 6)
        sel = (f >= lo) & (f <= hi)
        base[i] = 10 * np.log10(np.mean(10 ** (pdb[sel] / 10))) if sel.any() else pdb[i]
    excess = pdb - base
    band = (f >= a.fmin) & (f <= a.fmax)
    idx = np.flatnonzero(band[1:-1] & (excess[1:-1] > excess[:-2]) & (excess[1:-1] >= excess[2:])) + 1
    cands = []
    for i in idx:
        if excess[i] < a.min_excess:
            continue
        half = excess[i] - 3
        lo = i
        while lo > 0 and excess[lo] > half:
            lo -= 1
        hi = i
        while hi < len(f) - 1 and excess[hi] > half:
            hi += 1
        bw = max(f[hi] - f[lo], f[1] - f[0])
        q = float(np.clip(f[i] / bw, 1.0, 12.0))
        cands.append((excess[i], f[i], q))
    cands.sort(reverse=True)
    # keep the strongest per 1/3 octave
    picked = []
    for e, fr, q in cands:
        if all(abs(math.log2(fr / p2)) > 1 / 3 for _, p2, _ in picked):
            picked.append((e, fr, q))
        if len(picked) == a.top:
            break
    tot = np.trapezoid(p, f) if hasattr(np, "trapezoid") else np.trapz(p, f)

    def share(lo, hi):
        s = (f >= lo) & (f < hi)
        v = np.trapezoid(p[s], f[s]) if hasattr(np, "trapezoid") else np.trapz(p[s], f[s])
        return 10 * math.log10(v / tot + 1e-30)
    print(f"Energy share (dB of total): boxy 200-350 Hz {share(200, 350):.1f} | harsh 2-5 kHz {share(2000, 5000):.1f}"
          f" | presence 2.5-4.5 kHz {share(2500, 4500):.1f} | sibilance 5.5-8.5 kHz {share(5500, 8500):.1f}")
    if not picked:
        print(f"No narrow resonances above {a.min_excess} dB found between {a.fmin:g} and {a.fmax:g} Hz.")
        return
    notes = sung_notes(m, sr)
    if notes:
        print("Most-sung notes: " + ", ".join(f"{nm} {hz:.0f} Hz ({pct:.0f}%)" for hz, nm, pct in notes))
    print("Peak candidates (above the 1/3-octave average). Cut about half the excess, then A/B:")
    for e, fr, q in picked:
        cut = -round(min(6.0, max(1.5, e / 2)), 1)
        q = min(q, 8.0)
        zone = " [boxy zone]" if 200 <= fr <= 350 else " [harsh zone]" if 2000 <= fr <= 5000 else ""
        match = ""
        for hz, nm, _ in notes:
            h = fr / hz
            if round(h) >= 1 and round(h) <= 8 and abs(h - round(h)) / round(h) < 0.015:
                match = f"  <- also harmonic {int(round(h))} of the sung note {nm}: may be melody, not a resonance"
                break
        print(f"  {fr:7.0f} Hz  +{e:4.1f} dB  Q~{q:3.1f}{zone}   ffmpeg: equalizer=f={fr:.0f}:t=q:w={q:.1f}:g={cut}{match}")
    print("Prefer `dyneq` over a static notch when unsure: it only cuts when that frequency flares.")
    print("Sustained notes also make peaks: confirm a candidate stays fixed across the song before cutting.")


def split_band_dynamic(x, sr, sos, thr_db, ratio, max_cut, attack, release, auto_pct, block_ms=1.0, mode="peak"):
    band_m = sosfilt(sos, mono(x))
    lev, n = block_level(band_m, sr, block_ms, mode)
    full, _ = block_level(mono(x), sr, block_ms, "rms")
    active = full > max(-60, full.max() - 45)
    thr = float(np.percentile(lev[active], auto_pct)) if thr_db is None else thr_db
    over = lev - thr
    gr = np.clip(over * (1 - 1 / ratio), 0, max_cut)
    gr = ar_smooth(gr, n / sr, attack, release)
    g = 10 ** (-to_samples(gr, n, len(x)) / 20)
    band = sosfilt(sos, x, axis=0)
    y = x - (1 - g)[:, None] * band
    act_gr = gr[active]
    stats = {"threshold_db": thr, "pct_time_reducing": 100 * float((act_gr > 0.5).mean()) if len(act_gr) else 0,
             "max_reduction_db": float(gr.max()), "mean_reduction_when_active_db": float(act_gr[act_gr > 0.5].mean()) if (act_gr > 0.5).any() else 0.0}
    return y, stats


def report_dyn(name, s):
    print(f"{name}: threshold {s['threshold_db']:.1f} dBFS (band level), reducing {s['pct_time_reducing']:.1f}% of active time, "
          f"average {s['mean_reduction_when_active_db']:.1f} dB, max {s['max_reduction_db']:.1f} dB")


def cmd_dyneq(a):
    x, sr = read(a.input)
    bw = a.freq / a.q
    lo, hi = a.freq * (math.sqrt(1 + 1 / (4 * a.q ** 2)) - 1 / (2 * a.q)), a.freq * (math.sqrt(1 + 1 / (4 * a.q ** 2)) + 1 / (2 * a.q))
    sos = butter(1, [lo, hi], btype="bandpass", fs=sr, output="sos")
    y, s = split_band_dynamic(x, sr, sos, a.threshold, a.ratio, a.max_cut, a.attack, a.release, a.auto_pct, mode="rms", block_ms=2.0)
    write(a.output, y, sr)
    print(f"Dynamic EQ at {a.freq:g} Hz (band {lo:.0f}-{hi:.0f} Hz, bandwidth {bw:.0f} Hz)")
    report_dyn("Dynamic EQ", s)


def cmd_deess(a):
    x, sr = read(a.input)
    sos = butter(2, [a.low, a.high], btype="bandpass", fs=sr, output="sos")
    y, s = split_band_dynamic(x, sr, sos, a.threshold, a.ratio, a.max_cut, a.attack, a.release, a.auto_pct, mode="peak", block_ms=1.0)
    write(a.output, y, sr)
    print(f"De-esser: band-pass detection {a.low:g}-{a.high:g} Hz, ratio {a.ratio:g}:1, max cut {a.max_cut:g} dB")
    report_dyn("De-esser", s)


def cmd_comp2(a):
    x, sr = read(a.input)
    chain = (f"acompressor=threshold={a.peak_threshold}dB:ratio={a.peak_ratio}:attack={a.peak_attack}:"
             f"release={a.peak_release}:knee=2:detection=peak,"
             f"acompressor=threshold={a.smooth_threshold}dB:ratio={a.smooth_ratio}:attack={a.smooth_attack}:"
             f"release={a.smooth_release}:knee=6:detection=rms")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", a.input, "-af", chain,
                        "-c:a", "pcm_f32le", a.output], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    y, _ = read(a.output)
    if a.makeup == "auto":  # restore the working level set by gain-stage
        mk = gated_rms_db(x, sr) - gated_rms_db(y, sr)
    else:
        mk = float(a.makeup)
    y = y * 10 ** (mk / 20)
    write(a.output, y, sr)
    lb, _ = block_level(mono(x), sr, 50)
    la, _ = block_level(mono(y), sr, 50)
    m = min(len(lb), len(la))
    act = lb[:m] > max(-60, lb.max() - 35)
    gr = (lb[:m] - la[:m])[act] + mk
    spread_b = np.percentile(lb[:m][act], 95) - np.percentile(lb[:m][act], 10)
    spread_a = np.percentile(la[:m][act], 95) - np.percentile(la[:m][act], 10)
    print("Two-stage compression: 1) fast peak tamer, 2) smooth slow-release leveler (an approximation of opto behavior)")
    print(f"Average gain reduction {np.mean(gr):.1f} dB (95th percentile {np.percentile(gr, 95):.1f} dB); "
          f"level spread (loud vs quiet phrases) {spread_b:.1f} -> {spread_a:.1f} dB; "
          f"peak {float(db(np.abs(x).max())):+.1f} -> {float(db(np.abs(y).max())):+.1f} dBFS")
    print(f"Makeup gain {mk:+.1f} dB (active RMS now {gated_rms_db(y, sr):.1f} dBFS). Chain: {chain}")


NOTE_FACTORS = {"1/1": 4, "1/2": 2, "1/2d": 3, "1/4": 1, "1/4d": 1.5, "1/4t": 2 / 3, "1/8": 0.5, "1/8d": 0.75,
                "1/8t": 1 / 3, "1/16": 0.25, "1/16d": 0.375}


def parse_ranges(s):
    out = []
    for part in s.split(","):
        lo, hi = part.split("-")
        out.append((float(lo), float(hi)))
    return out


def duck_gain(key, sr, n_out, depth, threshold, attack, release, knee=6.0):
    lev, n = block_level(mono(key), sr, 10)
    act = lev[lev > max(-60, lev.max() - 35)]
    thr = (10 * np.log10(np.mean(10 ** (act / 10))) - 15) if threshold is None else threshold
    t = np.clip((lev - thr) / knee + 0.5, 0, 1)
    gr = ar_smooth(depth * t, n / sr, attack, release)
    curve = to_samples(gr, n, min(n_out, len(key)))
    if n_out > len(curve):
        curve = np.concatenate((curve, np.zeros(n_out - len(curve))))
    return 10 ** (-curve / 20), thr, float((gr > depth / 2).mean() * 100)


def cmd_delay(a):
    x, sr = read(a.input)
    if a.note not in NOTE_FACTORS:
        sys.exit(f"--note must be one of {', '.join(NOTE_FACTORS)}")
    ms = 60000.0 / a.bpm * NOTE_FACTORS[a.note]
    D = int(round(ms * sr / 1000))
    taps = max(1, int(math.ceil(math.log(1e-3) / math.log(a.feedback)))) if 0 < a.feedback < 1 else 1
    taps = min(taps, a.max_taps)
    tail = D * taps
    send = mono(x)
    if a.throws:
        mask = np.zeros(len(send))
        fade = int(0.01 * sr)
        for lo, hi in parse_ranges(a.throws):
            i, j = int(lo * sr), min(len(send), int(hi * sr))
            seg = np.ones(j - i)
            if len(seg) > 2 * fade:
                seg[:fade] = np.linspace(0, 1, fade)
                seg[-fade:] = np.linspace(1, 0, fade)
            mask[i:j] = seg
        send = send * mask
    send = np.concatenate((send, np.zeros(tail)))
    sos = butter(2, [a.hp, min(a.lp, sr / 2 * 0.95)], btype="bandpass", fs=sr, output="sos")
    out = np.zeros((len(send), 2))
    tap = send
    for k in range(1, taps + 1):
        tap = sosfilt(sos, tap)  # each repeat passes the loop filter again, so repeats get darker and thinner
        tap = np.concatenate((np.zeros(D), tap[:-D])) * (1.0 if k == 1 else a.feedback)
        if a.pingpong:
            out[:, (k - 1) % 2] += tap
        else:
            out += tap[:, None] * math.sqrt(0.5)
    duck_info = ""
    if a.duck_by:
        key, ksr = read(a.duck_by)
        if ksr != sr:
            sys.exit("Lead vocal and delay source must share a sample rate")
        g, thr, pct = duck_gain(key, sr, len(out), a.duck_depth, a.duck_threshold, a.duck_attack, a.duck_release)
        out *= g[:, None]
        duck_info = (f"; ducked by {a.duck_by}: -{a.duck_depth:g} dB while the lead sings (threshold {thr:.1f} dBFS, "
                     f"attack {a.duck_attack:g} ms, release {a.duck_release:g} ms), fully ducked {pct:.0f}% of the time")
    out *= 10 ** (a.return_db / 20)
    write(a.output, out, sr)
    print(f"Delay {a.note} at {a.bpm:g} BPM = {ms:.2f} ms ({D} samples), feedback {a.feedback:g}, {taps} repeats to -60 dB, "
          f"{'ping-pong' if a.pingpong else 'centered'}, loop filter {a.hp:g}-{a.lp:g} Hz, return {a.return_db:+g} dB{duck_info}")
    print(f"Output is the wet return only ({len(out) / sr:.2f} s including the echo tail); blend it with `mix`.")


def make_ir(sr, kind, decay, predelay_ms, width, seed=1):
    rng = np.random.default_rng(seed)
    length = int(sr * decay * 1.3)
    t = np.arange(length) / sr
    edges = [0, 250, 1000, 4000, 8000, sr / 2 - 1]
    # high frequencies die away faster than lows: plate brighter, hall darker
    hf_ratio = 0.7 if kind == "plate" else 0.5
    rt = [decay * 1.1, decay, decay * 0.85, decay * hf_ratio, decay * hf_ratio * 0.7]
    ir = np.zeros((length, 2))
    for c in range(2):
        noise = rng.standard_normal(length)
        acc = np.zeros(length)
        for (lo, hi), r in zip(zip(edges[:-1], edges[1:]), rt):
            if lo == 0:
                sos = butter(4, hi, btype="lowpass", fs=sr, output="sos")
            else:
                sos = butter(4, [lo, hi], btype="bandpass", fs=sr, output="sos")
            acc += sosfilt(sos, noise) * np.exp(-6.9078 * t / r)  # -60 dB at t = RT60
        ir[:, c] = acc
    if kind == "hall":
        fade = np.minimum(1, t / 0.03)  # diffuse tail builds up over ~30 ms
        ir *= fade[:, None]
        ref = math.sqrt((ir[: int(sr * 0.1)] ** 2).mean())  # reflections scaled to the early tail level
        for d_ms, gdb, side in ((11, -4, 0), (17, -5, 1), (23, -6, 0), (31, -7, 1), (43, -9, 0), (57, -10, 1)):
            i = int(sr * d_ms / 1000)
            ir[i, side] += 10 ** (gdb / 20) * ref * 12
    mid, side = (ir[:, 0] + ir[:, 1]) / 2, (ir[:, 0] - ir[:, 1]) / 2 * width
    ir = np.stack((mid + side, mid - side), 1)
    ir /= math.sqrt((ir ** 2).sum() / 2)  # unit energy per channel: return level is set by return_db
    pre = int(sr * predelay_ms / 1000)
    return np.concatenate((np.zeros((pre, 2)), ir))


def cmd_reverb(a):
    x, sr = read(a.input)
    send = mono(x)
    sos = butter(2, [a.hp, min(a.lp, sr / 2 * 0.95)], btype="bandpass", fs=sr, output="sos")
    send = sosfilt(sos, send)
    ir = make_ir(sr, a.type, a.decay, a.predelay, a.width)
    out = np.stack([fftconvolve(send, ir[:, c]) for c in range(2)], 1)
    if a.duck_by:
        key, _ = read(a.duck_by)
        g, thr, pct = duck_gain(key, sr, len(out), a.duck_depth, None, 15, 400)
        out *= g[:, None]
    out *= 10 ** (a.return_db / 20)
    write(a.output, out, sr)
    corr = float(np.corrcoef(out[:, 0], out[:, 1])[0, 1])
    print(f"{a.type.title()} reverb: RT60 {a.decay:g} s (highs decay faster), pre-delay {a.predelay:g} ms, "
          f"send filter {a.hp:g}-{a.lp:g} Hz, width {a.width:g} (L/R correlation {corr:.2f}), return {a.return_db:+g} dB"
          + (f", ducked {a.duck_depth:g} dB under the lead" if a.duck_by else ""))
    print("Output is the wet return only; blend it with `mix`.")


def cmd_saturate(a):
    x, sr = read(a.input)
    os_f = 4
    up = resample_poly(x, os_f, 1, axis=0)
    g = 10 ** (a.drive / 20)
    b = a.even
    # asymmetric tanh: the bias b adds even harmonics, tanh itself adds odd ones; unity small-signal gain
    y = (np.tanh(g * up + b) - math.tanh(b)) / (g * (1 - math.tanh(b) ** 2))
    y = resample_poly(y, 1, os_f, axis=0)[: len(x)]
    y = sosfilt(butter(1, 10, btype="highpass", fs=sr, output="sos"), y, axis=0)  # remove DC from asymmetry
    out = (1 - a.mix) * x + a.mix * y
    write(a.output, out, sr)
    added = float(db(np.sqrt(((out - x) ** 2).mean()))) - float(db(np.sqrt((x ** 2).mean())))
    print(f"Saturation: drive {a.drive:g} dB, even-harmonic bias {a.even:g}, mix {a.mix:g}, 4x oversampled; "
          f"added harmonics/difference at {added:.1f} dB relative to the dry signal")


def cmd_mix(a):
    tracks = []
    sr0 = None
    for spec in a.track:
        path, _, gain = spec.rpartition(":")
        if not path:
            path, gain = spec, "0"
        x, sr = read(path)
        if sr0 is None:
            sr0 = sr
        elif sr != sr0:
            sys.exit(f"{path} is {sr} Hz but the first track is {sr0} Hz; resample first so samples line up")
        if x.shape[1] == 1:
            x = np.repeat(x, 2, axis=1)
        tracks.append((path, x * 10 ** (float(gain) / 20), float(gain)))
    n = max(len(t[1]) for t in tracks)
    out = np.zeros((n, 2))
    for path, x, g in tracks:
        out[: len(x)] += x
    write(a.output, out, sr0)
    I, tp = loudness(a.output)
    print(f"Mixed {len(tracks)} tracks at {sr0} Hz, {n / sr0:.2f} s: "
          + ", ".join(f"{p} {g:+g} dB" for p, _, g in tracks))
    print(f"Mix: {I} LUFS, true peak {tp:+.1f} dBTP, sample peak {float(db(np.abs(out).max())):+.1f} dBFS (float, no clipping)")


def cmd_ms_bus(a):
    x, sr = read(a.input)
    if x.shape[1] != 2:
        sys.exit("ms-bus needs a stereo file")
    M, S = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
    side_low_before = None
    if a.side_hp > 0:
        lp = butter(4, a.side_hp, btype="lowpass", fs=sr, output="sos")
        side_low_before = float(db(np.sqrt((sosfilt(lp, S) ** 2).mean())))
        # zero-phase: forward+backward 2nd-order = 24 dB/oct, no phase shift between mid and side
        S = sosfiltfilt(butter(2, a.side_hp, btype="highpass", fs=sr, output="sos"), S)
    if a.mid_shelf:
        f0, gdb = (float(v) for v in a.mid_shelf.split(":"))
        bb, aa = rbj("highshelf", f0, sr, gdb / 2, 0.7071)
        M = lfilter(bb, aa, lfilter(bb, aa, M)[::-1])[::-1]  # zero-phase, half gain each pass = full gain
    y = np.stack((M + S, M - S), 1)
    write(a.output, y, sr)
    lp = butter(4, a.side_hp or 90, btype="lowpass", fs=sr, output="sos")
    side_low_after = float(db(np.sqrt((sosfilt(lp, (y[:, 0] - y[:, 1]) / 2) ** 2).mean())))
    msg = []
    if a.side_hp > 0:
        msg.append(f"side high-pass {a.side_hp:g} Hz (24 dB/oct, zero-phase): side energy below {a.side_hp:g} Hz "
                   f"{side_low_before:.1f} -> {side_low_after:.1f} dBFS, so the sub-bass is mono")
    if a.mid_shelf:
        msg.append(f"mid-only high shelf {a.mid_shelf.replace(':', ' Hz, ')} dB (zero-phase)")
    print("M/S bus: " + ("; ".join(msg) if msg else "no processing requested (output equals input)"))


# ---------------------------------------------------------------- CLI


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("gain-stage")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--target-rms", type=float, default=-18.0, help="active RMS target in dBFS (-18 to -14 typical)")
    p.add_argument("--against", help="instrumental/beat file to compare against")
    p.set_defaults(func=cmd_gain_stage)

    p = sp.add_parser("hpf")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--freq", type=float, default=90.0); p.add_argument("--order", type=int, default=3)
    p.set_defaults(func=cmd_hpf)

    p = sp.add_parser("resonances")
    p.add_argument("input")
    p.add_argument("--fmin", type=float, default=150.0); p.add_argument("--fmax", type=float, default=6000.0)
    p.add_argument("--min-excess", type=float, default=3.0); p.add_argument("--top", type=int, default=6)
    p.set_defaults(func=cmd_resonances)

    for name, func, defaults in (("dyneq", cmd_dyneq, dict(ratio=3.0, max_cut=6.0, attack=5.0, release=80.0, auto_pct=85.0)),
                                 ("deess", cmd_deess, dict(ratio=4.0, max_cut=8.0, attack=0.5, release=60.0, auto_pct=95.0))):
        p = sp.add_parser(name)
        p.add_argument("input"); p.add_argument("output")
        if name == "dyneq":
            p.add_argument("--freq", type=float, default=3500.0); p.add_argument("--q", type=float, default=2.0)
        else:
            p.add_argument("--low", type=float, default=5500.0); p.add_argument("--high", type=float, default=8500.0)
        p.add_argument("--threshold", type=float, default=None, help="band level in dBFS; default: automatic")
        p.add_argument("--auto-pct", type=float, default=defaults["auto_pct"],
                       help="automatic threshold = this percentile of the band level while singing")
        p.add_argument("--ratio", type=float, default=defaults["ratio"])
        p.add_argument("--max-cut", type=float, default=defaults["max_cut"])
        p.add_argument("--attack", type=float, default=defaults["attack"])
        p.add_argument("--release", type=float, default=defaults["release"])
        p.set_defaults(func=func)

    p = sp.add_parser("comp2")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--peak-threshold", type=float, default=-10.0); p.add_argument("--peak-ratio", type=float, default=5.0)
    p.add_argument("--peak-attack", type=float, default=1.0); p.add_argument("--peak-release", type=float, default=50.0)
    p.add_argument("--smooth-threshold", type=float, default=-24.0); p.add_argument("--smooth-ratio", type=float, default=2.5)
    p.add_argument("--smooth-attack", type=float, default=15.0); p.add_argument("--smooth-release", type=float, default=350.0)
    p.add_argument("--makeup", default="auto", help="makeup gain in dB, or 'auto' to restore the input's active RMS")
    p.set_defaults(func=cmd_comp2)

    p = sp.add_parser("delay")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--bpm", type=float, required=True)
    p.add_argument("--note", default="1/4", help="1/4, 1/8d, 1/2, 1/8, 1/4d, 1/4t, 1/8t, 1/16, 1/16d, 1/2d, 1/1")
    p.add_argument("--feedback", type=float, default=0.35)
    p.add_argument("--max-taps", type=int, default=24)
    p.add_argument("--pingpong", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--hp", type=float, default=300.0); p.add_argument("--lp", type=float, default=6000.0)
    p.add_argument("--return-db", type=float, default=-8.0)
    p.add_argument("--throws", help="only send these time ranges, e.g. '31.2-32.0,58.5-59.1' (seconds)")
    p.add_argument("--duck-by", help="lead vocal file: the delay turns down while it sings")
    p.add_argument("--duck-depth", type=float, default=10.0)
    p.add_argument("--duck-threshold", type=float, default=None)
    p.add_argument("--duck-attack", type=float, default=10.0); p.add_argument("--duck-release", type=float, default=300.0)
    p.set_defaults(func=cmd_delay)

    p = sp.add_parser("reverb")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--type", choices=["plate", "hall"], default="plate")
    p.add_argument("--decay", type=float, default=1.6, help="RT60 in seconds")
    p.add_argument("--predelay", type=float, default=30.0, help="ms; 25-40 keeps the vocal upfront")
    p.add_argument("--hp", type=float, default=200.0); p.add_argument("--lp", type=float, default=8000.0)
    p.add_argument("--width", type=float, default=1.0)
    p.add_argument("--return-db", type=float, default=-14.0)
    p.add_argument("--duck-by"); p.add_argument("--duck-depth", type=float, default=4.0)
    p.set_defaults(func=cmd_reverb)

    p = sp.add_parser("saturate")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--drive", type=float, default=6.0, help="dB into the curve")
    p.add_argument("--even", type=float, default=0.15, help="asymmetry 0-0.5: more = more even harmonics")
    p.add_argument("--mix", type=float, default=0.3, help="0-1 parallel blend")
    p.set_defaults(func=cmd_saturate)

    p = sp.add_parser("mix")
    p.add_argument("output")
    p.add_argument("--track", action="append", required=True, help="FILE:GAIN_DB, repeat for each track")
    p.set_defaults(func=cmd_mix)

    p = sp.add_parser("ms-bus")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--side-hp", type=float, default=90.0, help="high-pass the side below this (Hz); 0 = off")
    p.add_argument("--mid-shelf", default="9500:2.0", help="FREQ:GAIN_DB high shelf on the mid only; '' = off")
    p.set_defaults(func=cmd_ms_bus)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()

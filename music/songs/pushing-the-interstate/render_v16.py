#!/usr/bin/env python3
"""Rebuild Pushing the Interstate v4, then v16.

Verses, the verse-1 throw, the adlib delay, the phone-call layout, the halls
and the fade are the v4 settings (effects/v4.json, commit 0e15d364). v16 keeps
that and, in the outro only, replaces the phone delay with a +3 semitone copy
and adds syllable stutters in the gaps that do not cover a lyric.

Work files go to /tmp/pti. Delivery WAVs are written by export_master.py.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SONG = os.path.join(ROOT, "music", "songs", "pushing-the-interstate")
STEMS = os.path.join(SONG, "stems")
TOOLS = os.path.join(ROOT, "music", "tools")
WORK = "/tmp/pti"
SR = 44100
BPM = 129.0
BAR = 4 * 60.0 / BPM
LEAD_FADER = -6.6
ADLIB_FADER = -10.0
OUTRO_BUS = 3.9

os.makedirs(WORK, exist_ok=True)
os.chdir(ROOT)


def sh(cmd, inp=None, binary=False):
    r = subprocess.run(cmd, input=inp, capture_output=True)
    if r.stdout and not binary:
        sys.stdout.write(r.stdout.decode("utf-8", errors="replace")[-5000:])
        sys.stdout.write("\n")
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace")[-2000:]
        sys.stderr.write(err + "\n")
        sys.exit(f"command failed: {' '.join(str(c) for c in cmd[:8])}")
    return r


def dsp(*args):
    print("dsp", " ".join(args), flush=True)
    r = sh([sys.executable, os.path.join(TOOLS, "dsp_tools.py"), *args])
    text = r.stdout.decode()
    print(text, flush=True)
    return text


def read_audio(path):
    probe = sh(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                 "stream=sample_rate,channels", "-of", "json", path])
    s = json.loads(probe.stdout)["streams"][0]
    sr, ch = int(s["sample_rate"]), int(s["channels"])
    raw = sh(["ffmpeg", "-v", "error", "-i", path, "-map", "a:0", "-ac", str(ch), "-f", "f32le", "-"], binary=True)
    x = np.frombuffer(raw.stdout, dtype="<f4").astype(np.float64).reshape(-1, ch)
    return x, sr


def write_audio(path, x, sr=SR):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    sh(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(x.shape[1]),
        "-i", "-", "-c:a", "pcm_f32le", path], inp=x.astype("<f4").tobytes())


def ffmpeg_af(src, dst, af):
    print("ffmpeg", af, flush=True)
    sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", src, "-af", af, "-c:a", "pcm_f32le", dst])


def env_db(x, hop_s=0.005):
    m = x.mean(axis=1) if x.ndim == 2 else x
    hop = int(hop_s * SR)
    n = len(m) // hop
    rms = np.sqrt((m[: n * hop].reshape(n, hop) ** 2).mean(1))
    return 20 * np.log10(np.maximum(rms, 1e-9)), hop_s


def silence_starts(db, hop_s, thr, min_dur):
    below = db < thr
    out = []
    i = 0
    while i < len(below):
        if below[i]:
            j = i
            while j < len(below) and below[j]:
                j += 1
            dur = (j - i) * hop_s
            if dur >= min_dur:
                out.append((i * hop_s, j * hop_s, dur))
            i = j
        else:
            i += 1
    return out


def build_chains():
    needed = [f"{WORK}/lead.wav", f"{WORK}/ad.wav", f"{WORK}/beat.wav", f"{WORK}/fx.wav"]
    if all(os.path.exists(p) and os.path.getsize(p) > 100000 for p in needed):
        print("vocal and beat chains already built, reusing them", flush=True)
        return
    lead = os.path.join(STEMS, "02_Lead_Vocals.mp3")
    ad = os.path.join(STEMS, "03_Adlibs.mp3")
    beat = os.path.join(STEMS, "01_Beat.mp3")
    fx = os.path.join(STEMS, "04_Vocal_FX_Reverb_Delays_Throws.mp3")
    w = WORK
    dsp("gain-stage", lead, f"{w}/lead_gs.wav", "--target-rms", "-18")
    dsp("hpf", f"{w}/lead_gs.wav", f"{w}/lead_hpf.wav", "--freq", "90", "--order", "3")
    ffmpeg_af(f"{w}/lead_hpf.wav", f"{w}/lead_eq.wav",
              "equalizer=f=229:t=q:w=6:g=-2.6,equalizer=f=320:t=q:w=1:g=-1.5")
    dsp("dyneq", f"{w}/lead_eq.wav", f"{w}/lead_dy1.wav", "--freq", "3529", "--q", "4", "--threshold", "-32")
    dsp("dyneq", f"{w}/lead_dy1.wav", f"{w}/lead_dy2.wav", "--freq", "4697", "--q", "4", "--threshold", "-33")
    ffmpeg_af(f"{w}/lead_dy2.wav", f"{w}/lead_pres.wav",
              "equalizer=f=3000:t=q:w=0.9:g=2,highshelf=f=10000:g=1.5")
    dsp("deess", f"{w}/lead_pres.wav", f"{w}/lead_de.wav", "--low", "5500", "--high", "8500", "--threshold", "-25")
    dsp("comp2", f"{w}/lead_de.wav", f"{w}/lead.wav", "--smooth-threshold", "-22")
    dsp("saturate", f"{w}/lead.wav", f"{w}/lead.wav", "--drive", "6", "--even", "0.15", "--mix", "0.25")

    dsp("gain-stage", ad, f"{w}/ad_gs.wav", "--target-rms", "-18")
    dsp("hpf", f"{w}/ad_gs.wav", f"{w}/ad_hpf.wav", "--freq", "180", "--order", "3")
    ffmpeg_af(f"{w}/ad_hpf.wav", f"{w}/ad_eq.wav",
              "equalizer=f=320:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1:g=1.5")
    dsp("deess", f"{w}/ad_eq.wav", f"{w}/ad_de.wav", "--low", "5500", "--high", "8500", "--threshold", "-29.5")
    dsp("comp2", f"{w}/ad_de.wav", f"{w}/ad.wav", "--smooth-threshold", "-22")

    ffmpeg_af(beat, f"{w}/beat_eq.wav",
              "equalizer=f=2500:t=q:w=1.5:g=-1,equalizer=f=250:t=q:w=1:g=-1")
    sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", f"{w}/beat_eq.wav", "-filter_complex",
        "[0:a]acrossover=split=120:order=4th:precision=double[lo][hi];"
        "[lo]acompressor=threshold=-20dB:ratio=5:attack=3:release=90:makeup=2[loc];"
        "[loc][hi]amix=inputs=2:duration=longest:normalize=0:dropout_transition=0[out]",
        "-map", "[out]", "-c:a", "pcm_f32le", f"{w}/beat.wav"])
    ffmpeg_af(fx, f"{w}/fx.wav", "anull")


def fade_db(x, t0, t1, db0, db1):
    """Linear dB ramp from t0 to t1. Hold db1 after t1."""
    y = x.copy()
    n = len(y)
    i0, i1 = int(t0 * SR), min(n, int(t1 * SR))
    if i1 <= i0:
        return y
    ramp = np.linspace(db0, db1, i1 - i0)
    y[i0:i1] *= (10 ** (ramp / 20))[:, None] if y.ndim == 2 else 10 ** (ramp / 20)
    if i1 < n:
        y[i1:] *= 10 ** (db1 / 20)
    return y


def last_words(mono, seeds, max_len=0.50):
    """The last word before each line break, from its start through its ending.

    A fixed 0.30 s slice was starting mid-word and, on five of the lines, cutting
    the word off. Syllables of the same word (a gap under 0.14 s) stay together.
    A legato phrase with no gap is limited to the last half-second so the echo
    is the end of the line and not the whole line.
    """
    db, hop = env_db(mono, 0.01)
    words = []
    print("Last words (whole word, not a fixed 0.30 s slice):", flush=True)
    for seed in seeds:
        i0 = max(0, int((seed - 1.6) / hop))
        i1 = min(len(db) - 1, int((seed + 0.9) / hop))
        seg = db[i0:i1]
        runs = []
        i = 0
        act = seg > -32
        while i < len(act):
            if act[i]:
                j = i
                while j < len(act) and act[j]:
                    j += 1
                if (j - i) * hop >= 0.05:
                    runs.append([i, j])
                i = j
            else:
                i += 1
        # The word that contains the logged line-ending, not a word from the next line.
        seed_i = int(seed / hop) - i0
        containing = [r for r in runs if r[0] <= seed_i <= r[1]]
        if containing:
            run = containing[-1]
        else:
            run = min(runs, key=lambda r: abs((i0 + r[1]) * hop - seed))
        # A short syllable after a tiny gap is still this word. A longer run is the next line.
        nxts = [r for r in runs if r[0] >= run[1]]
        if nxts:
            nxt = nxts[0]
            gap = (nxt[0] - run[1]) * hop
            if gap <= 0.08 and (nxt[1] - nxt[0]) * hop <= 0.25:
                run = [run[0], nxt[1]]
        if (run[1] - run[0]) * hop < 0.35:
            prevs = [r for r in runs if r[1] <= run[0]]
            if prevs and (run[0] - prevs[-1][1]) * hop <= 0.08:
                run = [prevs[-1][0], run[1]]
        end = (i0 + run[1]) * hop + 0.02
        start = (i0 + run[0]) * hop
        if end - start > max_len:
            start = end - max_len
        words.append((float(start), float(end)))
        print(f"  seed {seed:.1f}: word {start:.3f}-{end:.3f} ({(end - start) * 1000:.0f} ms)", flush=True)
    return words


def word_send(mono, words, fade_in=0.012, fade_out=0.040):
    """Copy each whole word. Short fades, no hard cut in the middle of the word."""
    y = np.zeros_like(mono)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    for lo, hi in words:
        i0, i1 = int(lo * SR), min(len(y), int(hi * SR))
        if i1 <= i0:
            continue
        seg = mono[i0:i1].copy()
        if len(seg) > fi + fo + 8:
            seg[:fi] *= np.linspace(0, 1, fi)
            seg[-fo:] *= np.linspace(1, 0, fo)
        y[i0:i1] = seg
    return y


def apply_gain_db(path, db):
    x, _ = read_audio(path)
    write_audio(path, x * 10 ** (db / 20))


def first_tap_delta_db(src, wet, words, lag_s, win=0.18):
    """How many dB the first echo sits under the dry word. Negative means quieter."""
    deltas = []
    lag = int(lag_s * SR)
    n = int(win * SR)
    for lo, hi in words:
        i0 = int(lo * SR)
        nuse = min(n, int((hi - lo) * SR), len(src) - i0, len(wet) - (i0 + lag))
        if nuse < int(0.06 * SR):
            continue
        dry = np.sqrt(np.mean(src[i0:i0 + nuse] ** 2))
        echo = np.sqrt(np.mean(wet[i0 + lag:i0 + lag + nuse] ** 2))
        if dry > 1e-6 and echo > 1e-8:
            deltas.append(20 * np.log10(echo / dry))
    return float(np.median(deltas)) if deltas else 0.0


def mute_regions(x, regions, gain_db=None):
    """Fade a printed-FX spot down. gain_db None means silence. Short fades, not a click."""
    y = x.copy()
    fade = int(0.012 * SR)
    for lo, hi in regions:
        i0, i1 = int(lo * SR), min(len(y), int(hi * SR))
        if i1 - i0 < 4:
            continue
        g = np.ones(i1 - i0)
        target = 0.0 if gain_db is None else 10 ** (gain_db / 20)
        n = min(fade, (i1 - i0) // 3)
        g[:n] = np.linspace(1, target, n)
        g[-n:] = np.linspace(target, 1, n)
        g[n:-n] = target
        y[i0:i1] *= g[:, None] if y.ndim == 2 else g
    return y


def throws_arg(windows):
    return ",".join(f"{a:.3f}-{b:.3f}" for a, b in windows)


def phone_dry(lead):
    """v4 phone lines: two cuts, three blocks, whole-bar shifts, 12 ms fades."""
    mono = lead.mean(axis=1)
    cuts = (("A", 30.80, 34.62), ("B", 34.70, 38.25))
    shifts = [int(round(bars * BAR * SR)) for bars in (56, 60, 64)]
    end = shifts[-1] + int(38.25 * SR) + int(8 * SR)
    out = np.zeros(end)
    placed = []
    fade = int(0.012 * SR)
    for bi, shift in enumerate(shifts):
        gain = 10 ** ([0.0, -1.5, -3.0][bi] / 20)
        for name, lo, hi in cuts:
            i0, i1 = int(round(lo * SR)), int(round(hi * SR))
            seg = mono[i0:i1].copy() * gain
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
            j0 = i0 + shift
            out[j0:j0 + len(seg)] += seg
            placed.append({"block": bi + 1, "name": name, "i0": j0, "i1": j0 + len(seg),
                           "t0": j0 / SR, "t1": (j0 + len(seg)) / SR})
    write_audio(f"{WORK}/phone_dry.wav", out)
    ffmpeg_af(f"{WORK}/phone_dry.wav", f"{WORK}/phone_band.wav",
              "highpass=f=420:poles=2,highpass=f=420:poles=2,lowpass=f=3200:poles=2,lowpass=f=3200:poles=2,"
              "equalizer=f=1800:t=q:w=1:g=4,"
              "aresample=8000:resampler=soxr,aresample=44100:resampler=soxr")
    got, _ = read_audio(f"{WORK}/phone_band.wav")
    if len(got) != len(out):
        print(f"phone resample length {len(got)} vs {len(out)}; fitting", flush=True)
        fixed = np.zeros(len(out))
        n = min(len(got), len(fixed))
        fixed[:n] = got[:n, 0] if got.ndim == 2 else got[:n]
        write_audio(f"{WORK}/phone_band.wav", fixed)
    dsp("saturate", f"{WORK}/phone_band.wav", f"{WORK}/phone_sat.wav", "--drive", "14", "--even", "0.15", "--mix", "0.7")
    ffmpeg_af(f"{WORK}/phone_sat.wav", f"{WORK}/phone.wav",
              "acompressor=threshold=-18dB:ratio=6:attack=8:release=80:makeup=2:knee=4")
    phone, _ = read_audio(f"{WORK}/phone.wav")
    phone = phone[:, 0]
    # Block 3 sits farther away: darker top.
    b3 = [p for p in placed if p["block"] == 3]
    a, b = b3[0]["i0"], b3[-1]["i1"]
    dark = phone.copy()
    write_audio(f"{WORK}/phone_tmp.wav", phone)
    ffmpeg_af(f"{WORK}/phone_tmp.wav", f"{WORK}/phone_dark.wav", "lowpass=f=2600:poles=2,lowpass=f=2600:poles=2")
    dark_a, _ = read_audio(f"{WORK}/phone_dark.wav")
    dark = np.zeros(len(phone))
    n = min(len(dark), len(dark_a))
    dark[:n] = dark_a[:n, 0]
    edge = int(0.01 * SR)
    w = np.zeros(len(phone))
    w[a:b] = 1
    if a > edge:
        w[a - edge:a] = np.linspace(0, 1, edge)
    if b + edge < len(w):
        w[b:b + edge] = np.linspace(1, 0, edge)
    phone = phone * (1 - w) + dark * w
    return phone, placed


def speech_bounds(x, i0, i1, thr=-36.0):
    seg = x[i0:i1]
    hop = int(0.005 * SR)
    n = len(seg) // hop
    if n < 2:
        return i0 / SR, i1 / SR
    rms = np.sqrt((seg[: n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(np.maximum(rms, 1e-9))
    on = np.flatnonzero(db > thr)
    if not len(on):
        return i0 / SR, i1 / SR
    return (i0 + on[0] * hop) / SR, (i0 + (on[-1] + 1) * hop) / SR


def syllable_len(x, onset_s):
    """Length of the first syllable: onset until the first real dip, capped at 0.28 s."""
    i = int(onset_s * SR)
    hop = int(0.005 * SR)
    frame = x[i:i + int(0.40 * SR)]
    n = len(frame) // hop
    rms = np.sqrt((frame[: n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(np.maximum(rms, 1e-9))
    peak = db[:8].max() if len(db) >= 8 else db.max()
    for k in range(4, len(db) - 2):
        if db[k] < peak - 8 and db[k:k + 2].mean() < peak - 6:
            return max(0.06, k * 0.005)
    return 0.12


def add_stutters(phone, placed):
    """Repeat the first half of each line's first syllable on 16th notes, in the free gap only."""
    step = (60.0 / BPM) / 4.0
    out = np.zeros_like(phone)
    rows = []
    # Previous lyric ends. The lead is still going until the outro; the first line has seconds of room.
    prev_end = 0.0
    info = []
    for p in placed:
        on, off = speech_bounds(phone, p["i0"], p["i1"])
        info.append((p, on, off))
    for idx, (p, on, off) in enumerate(info):
        if idx == 0:
            prev_end = on - 5.0
        syl = syllable_len(phone, on)
        half = syl * 0.5
        chop = float(np.clip(half, 0.075, 0.116))
        gap = on - prev_end
        chosen = 1
        for nrep in (4, 3, 2, 1):
            start0 = on - chop - (nrep - 1) * step
            if start0 >= prev_end + 0.012:
                chosen = nrep
                break
        print(f"stutter {p['block']}{p['name']}: syllable {syl * 1000:.0f} ms, chop {chop * 1000:.0f} ms, "
              f"gap {gap * 1000:.0f} ms, repeats {chosen}", flush=True)
        for k in range(chosen):
            start = on - chop - (chosen - 1 - k) * step
            # Rise toward the real word, and stay under it so the stutter never takes over.
            gdb = -6.0 + 4.5 * k / max(chosen - 1, 1)
            i0 = int(round(start * SR))
            n = int(round(chop * SR))
            src = int(round(on * SR))
            seg = phone[src:src + n].copy() * 10 ** (gdb / 20)
            fin = int(0.003 * SR)
            fout = int(0.010 * SR)
            if len(seg) > fin + fout:
                seg[:fin] *= np.linspace(0, 1, fin)
                seg[-fout:] *= np.linspace(1, 0, fout)
            if i0 < 0:
                seg = seg[-i0:]
                i0 = 0
            out[i0:i0 + len(seg)] += seg
            rows.append({"line": f"block {p['block']} line {p['name']}", "k": k + 1, "of": chosen,
                         "start": i0 / SR, "chop_ms": chop * 1000, "gain_db": gdb,
                         "word": on, "gap_ms": gap * 1000, "syl_ms": syl * 1000})
        prev_end = off
    return out, rows


def pitch_up(x, semitones=3):
    scale = 2 ** (semitones / 12.0)
    write_audio(f"{WORK}/pitch_in.wav", x)
    sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", f"{WORK}/pitch_in.wav",
        "-af", f"rubberband=pitch={scale:.8f}:transients=crisp", "-c:a", "pcm_f32le", f"{WORK}/pitch_out.wav"])
    y, _ = read_audio(f"{WORK}/pitch_out.wav")
    y = y[:, 0]
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    y = y[:len(x)]
    # Pitch-shifted audio does not match the dry waveform, so align the envelopes.
    # Positive lag means the pitched copy is late and has to move earlier.
    def envelope(z):
        w = int(0.008 * SR)
        return np.convolve(np.abs(z), np.ones(w) / w, mode="same")

    i0, i1 = int(134.5 * SR), int(142.5 * SR)
    ref = envelope(x[i0:i1])
    sig = envelope(y[i0:i1])
    ref = ref - ref.mean()
    sig = sig - sig.mean()
    nfft = 1 << int(math.ceil(math.log2(len(ref) + len(sig))))
    corr = np.fft.irfft(np.fft.rfft(ref, nfft) * np.conj(np.fft.rfft(sig, nfft)), nfft)
    k = int(np.argmax(corr))
    if k > nfft // 2:
        k -= nfft
    lag = -k
    print(f"rubberband lag {lag} samples ({lag / SR * 1000:.2f} ms), shifting to match", flush=True)
    if lag > 0:
        y = np.concatenate((y[lag:], np.zeros(lag)))
    elif lag < 0:
        y = np.concatenate((np.zeros(-lag), y[:lag]))
    sig2 = envelope(y[i0:i1])
    sig2 = sig2 - sig2.mean()
    corr2 = np.fft.irfft(np.fft.rfft(ref, nfft) * np.conj(np.fft.rfft(sig2, nfft)), nfft)
    k2 = int(np.argmax(corr2))
    if k2 > nfft // 2:
        k2 -= nfft
    print(f"pitched vocal residual lag {-k2} samples ({-k2 / SR * 1000:.2f} ms)", flush=True)
    return y


def add_hiss(phone, level_under_db=34.0):
    hop = int(0.02 * SR)
    n = len(phone) // hop
    rms = np.sqrt((phone[: n * hop].reshape(n, hop) ** 2).mean(1))
    active = rms > 10 ** (-40 / 20)
    if not active.any():
        return np.zeros_like(phone)
    call = np.sqrt(np.mean(rms[active] ** 2))
    rng = np.random.default_rng(4)
    noise = rng.standard_normal(len(phone))
    # Band-limit with a short FFT filter in the phone range, then set the level under the calls.
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(len(noise), 1 / SR)
    spec[(freqs < 300) | (freqs > 3400)] = 0
    noise = np.fft.irfft(spec, n=len(phone))
    noise *= call * 10 ** (-level_under_db / 20) / (np.sqrt(np.mean(noise ** 2)) + 1e-12)
    mask = np.repeat(active, hop)
    if len(mask) < len(phone):
        mask = np.pad(mask, (0, len(phone) - len(mask)))
    # 80 ms hang so the hiss doesn't chatter.
    hang = int(0.08 * SR)
    kernel = np.ones(hang)
    mask = np.convolve(mask.astype(np.float64), kernel, mode="same")
    mask = np.clip(mask, 0, 1)
    return noise * mask


def slice_send(x, windows):
    y = np.zeros_like(x)
    fade = int(0.01 * SR)
    for lo, hi in windows:
        i0, i1 = int(lo * SR), int(hi * SR)
        seg = x[i0:i1].copy()
        if len(seg) > 2 * fade:
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
        y[i0:i1] = seg
    return y


def grid_offset_ms(t, division):
    step = (60.0 / BPM) / (division / 4.0)
    nearest = round(t / step) * step
    return (t - nearest) * 1000.0, nearest


def xcorr_lag_ms(src, echo, sr, expect_s, search_s=0.04):
    """Lag of echo relative to src, searching around expect_s. src and echo are 1-D."""
    n = min(len(src), len(echo) - int((expect_s - search_s) * sr))
    if n < sr // 10:
        return expect_s * 1000
    a = src[:n] - src[:n].mean()
    center = int(expect_s * sr)
    half = int(search_s * sr)
    best, best_i = -1, center
    # Coarse scan in 1 ms steps is enough, then refine.
    step = int(0.001 * sr)
    for lag in range(center - half, center + half, step):
        if lag < 0 or lag + n > len(echo):
            continue
        b = echo[lag:lag + n]
        score = float(np.dot(a, b))
        if score > best:
            best, best_i = score, lag
    return best_i / sr * 1000.0


def phrases(x, min_gap=0.18, thr=-38.0):
    db, hop = env_db(x if x.ndim == 1 else x[:, 0], 0.01)
    active = db > thr
    rows = []
    i = 0
    while i < len(active):
        if active[i]:
            j = i
            while j < len(active) and active[j]:
                j += 1
            rows.append((i * hop, j * hop))
            i = j
        else:
            i += 1
    # Merge bursts separated by less than min_gap.
    merged = []
    for a, b in rows:
        if merged and a - merged[-1][1] < min_gap:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def measure(tag, src_t, echo_start, note_ms):
    off8, g8 = grid_offset_ms(echo_start, 8)
    off16, g16 = grid_offset_ms(echo_start, 16)
    return {"what": tag, "source_s": src_t, "first_tap_s": echo_start,
            "lag_ms": (echo_start - src_t) * 1000.0, "note_ms": note_ms,
            "off_8th_ms": off8, "grid_8th_s": g8, "off_16th_ms": off16, "grid_16th_s": g16}


def fmt_time(t):
    m = int(t // 60)
    return f"{m}:{t - 60 * m:06.3f}"


def main():
    build_chains()
    lead, _ = read_audio(f"{WORK}/lead.wav")
    ad, _ = read_audio(f"{WORK}/ad.wav")
    seeds = [34.1, 37.8, 41.6, 75.9, 77.8, 87.9, 105.7, 107.6, 117.6]
    words = last_words(lead[:, 0], seeds)
    # v4's own slices, kept only so the reference render can be compared.
    v4_slices = []
    db, hop = env_db(lead[:, 0], 0.01)
    breaths = silence_starts(db, hop, thr=-36.0, min_dur=0.08)
    for seed in seeds:
        cands = [b for b in breaths if seed - 0.1 <= b[0] <= seed + 0.7]
        end = min(cands, key=lambda b: abs(b[0] - (seed + 0.4)))[0] if cands else seed + 0.35
        v4_slices.append((end - 0.30, end))
    throw_word = last_words(lead[:, 0], [60.4], max_len=0.50)
    quarter = 60000.0 / BPM
    half = quarter * 2
    dotted = quarter * 0.75
    print(f"delay math: 1/4 {quarter:.2f} ms, 1/2 {half:.2f} ms, 1/8d {dotted:.2f} ms", flush=True)
    DUCK = ["--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4", "--duck-attack", "5", "--duck-release", "80"]

    write_audio(f"{WORK}/lead_send.wav", word_send(lead[:, 0], words))
    write_audio(f"{WORK}/lead_send4.wav", word_send(lead[:, 0], v4_slices, fade_out=0.010))
    write_audio(f"{WORK}/throw_word.wav", word_send(lead[:, 0], throw_word))
    # Level pass at 0 dB, no duck, so the return can be set to 12 dB under the dry word.
    dsp("delay", f"{WORK}/lead_send.wav", f"{WORK}/lead_echo_raw.wav", "--bpm", "129", "--note", "1/4",
        "--feedback", "0.35", "--hp", "450", "--lp", "5000", "--return-db", "0")
    raw, _ = read_audio(f"{WORK}/lead_echo_raw.wav")
    lead_delta = first_tap_delta_db(lead[:, 0], raw[:, 0], words, quarter / 1000)
    lead_return = -12.0 - lead_delta
    print(f"lead echo at 0 dB return is {lead_delta:+.1f} dB vs the word; return set to {lead_return:+.1f} dB", flush=True)
    dsp("delay", f"{WORK}/lead_send.wav", f"{WORK}/lead_echo.wav", "--bpm", "129", "--note", "1/4",
        "--feedback", "0.35", "--hp", "450", "--lp", "5000", "--return-db", f"{lead_return:.2f}", *DUCK)
    dsp("delay", f"{WORK}/lead_send4.wav", f"{WORK}/lead_echo4.wav", "--bpm", "129", "--note", "1/4",
        "--feedback", "0.35", "--hp", "450", "--lp", "5000", "--return-db", "3",
        "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "8", "--duck-attack", "10", "--duck-release", "300")
    dsp("delay", f"{WORK}/throw_word.wav", f"{WORK}/v1_throw_raw.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.35", "--hp", "350", "--lp", "4500", "--return-db", "0")
    raw, _ = read_audio(f"{WORK}/v1_throw_raw.wav")
    throw_delta = first_tap_delta_db(lead[:, 0], raw[:, 0], throw_word, half / 1000)
    throw_return = -12.0 - throw_delta
    print(f"verse throw at 0 dB return is {throw_delta:+.1f} dB; return set to {throw_return:+.1f} dB", flush=True)
    dsp("delay", f"{WORK}/throw_word.wav", f"{WORK}/v1_throw.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.35", "--hp", "350", "--lp", "4500", "--return-db", f"{throw_return:.2f}", *DUCK)
    dsp("delay", f"{WORK}/lead.wav", f"{WORK}/v1_throw4.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.5", "--hp", "350", "--lp", "4500", "--return-db", "6",
        "--throws", "60.250-60.650", "--duck-by", f"{WORK}/lead.wav",
        "--duck-depth", "10", "--duck-attack", "10", "--duck-release", "300")
    dsp("reverb", f"{WORK}/v1_throw.wav", f"{WORK}/v1_throw_hall.wav", "--type", "hall",
        "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-10",
        "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4")
    dsp("reverb", f"{WORK}/v1_throw4.wav", f"{WORK}/v1_throw_hall4.wav", "--type", "hall",
        "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-10",
        "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4")
    dsp("reverb", f"{WORK}/lead.wav", f"{WORK}/plate.wav", "--type", "plate",
        "--decay", "1.39535", "--predelay", "29.07", "--return-db", "-14",
        "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "4")
    # Adlib delay keeps v4's dotted eighth and 0.35 feedback. Level is pulled to the same -12 dB.
    dsp("delay", f"{WORK}/ad.wav", f"{WORK}/ad_delay_raw.wav", "--bpm", "129", "--note", "1/8d",
        "--feedback", "0.35", "--hp", "300", "--lp", "6000", "--return-db", "0")
    raw, _ = read_audio(f"{WORK}/ad_delay_raw.wav")
    ad_phrases = phrases(ad[:, 0], min_gap=0.20)
    ad_delta = first_tap_delta_db(ad[:, 0], raw[:, 0], [(a, b) for a, b in ad_phrases], dotted / 1000, win=0.12)
    ad_return = -12.0 - ad_delta
    print(f"adlib delay at 0 dB return is {ad_delta:+.1f} dB vs the adlib; return set to {ad_return:.1f} dB", flush=True)
    dsp("delay", f"{WORK}/ad.wav", f"{WORK}/ad_delay.wav", "--bpm", "129", "--note", "1/8d",
        "--feedback", "0.35", "--hp", "300", "--lp", "6000", "--return-db", f"{ad_return:.2f}", *DUCK)
    dsp("delay", f"{WORK}/ad.wav", f"{WORK}/ad_delay4.wav", "--bpm", "129", "--note", "1/8d",
        "--feedback", "0.35", "--hp", "300", "--lp", "6000", "--return-db", "-8",
        "--duck-by", f"{WORK}/lead.wav", "--duck-depth", "10", "--duck-attack", "10", "--duck-release", "300")

    phone, placed = phone_dry(lead)
    stutters, stutter_rows = add_stutters(phone, placed)
    write_audio(f"{WORK}/stutters.wav", stutters)
    hiss = add_hiss(phone + stutters)
    phone_bus = phone + stutters + hiss
    write_audio(f"{WORK}/phone_bus.wav", phone_bus)
    write_audio(f"{WORK}/phone_lines.wav", phone)

    pitched = pitch_up(phone, 3)
    # The last word of block 3 gets the half-note ring only, so a 1-beat copy and a
    # 2-beat copy of that word are not both in the song.
    final_word = (156.59, 157.29)
    pitched_q = pitched.copy()
    i0, i1 = int(final_word[0] * SR), int(final_word[1] * SR)
    fade = int(0.02 * SR)
    pitched_q[i0:i1] = 0
    if i0 > fade:
        pitched_q[i0 - fade:i0] *= np.linspace(1, 0, fade)
    write_audio(f"{WORK}/phone_pitched.wav", pitched_q)
    write_audio(f"{WORK}/phone_bus.wav", phone_bus)
    dsp("delay", f"{WORK}/phone_pitched.wav", f"{WORK}/phone_delay_raw.wav", "--bpm", "129", "--note", "1/4",
        "--feedback", "0.35", "--hp", "400", "--lp", "3500", "--return-db", "0")
    raw, _ = read_audio(f"{WORK}/phone_delay_raw.wav")
    phone_words = []
    for p in placed:
        if p["block"] == 3 and p["name"] == "B":
            continue
        on, off = speech_bounds(phone, p["i0"], p["i1"])
        phone_words.append((on, min(off, on + 0.45)))
    phone_delta = first_tap_delta_db(pitched, raw[:, 0], phone_words, quarter / 1000, win=0.16)
    phone_return = -12.0 - phone_delta
    print(f"phone delay at 0 dB return is {phone_delta:+.1f} dB; return set to {phone_return:+.1f} dB", flush=True)
    dsp("delay", f"{WORK}/phone_pitched.wav", f"{WORK}/phone_delay16.wav", "--bpm", "129", "--note", "1/4",
        "--feedback", "0.35", "--hp", "400", "--lp", "3500", "--return-db", f"{phone_return:.2f}",
        "--duck-by", f"{WORK}/phone_bus.wav", "--duck-depth", "4", "--duck-attack", "5", "--duck-release", "80")
    # v4 reference: unpitched, heavier duck, the original feedback.
    dsp("delay", f"{WORK}/phone_lines.wav", f"{WORK}/phone_delay4.wav", "--bpm", "129", "--note", "1/4",
        "--feedback", "0.42", "--hp", "400", "--lp", "3500", "--return-db", "-9",
        "--duck-by", f"{WORK}/phone_lines.wav", "--duck-depth", "10", "--duck-attack", "10", "--duck-release", "300")

    throw_w = [(149.15, 149.85), (156.59, 157.29)]
    write_audio(f"{WORK}/throw_send4.wav", slice_send(phone, throw_w))
    write_audio(f"{WORK}/throw_send16.wav", word_send(pitched, [final_word]))
    dsp("delay", f"{WORK}/throw_send4.wav", f"{WORK}/throw_b2_4.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.55", "--hp", "400", "--lp", "3500", "--return-db", "-5",
        "--throws", "149.150-149.850", "--duck-by", f"{WORK}/phone_lines.wav",
        "--duck-depth", "10", "--duck-attack", "10", "--duck-release", "300")
    dsp("delay", f"{WORK}/throw_send4.wav", f"{WORK}/throw_b3_4.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.66", "--hp", "400", "--lp", "3500", "--return-db", "3",
        "--throws", "156.590-157.290", "--duck-by", f"{WORK}/phone_lines.wav",
        "--duck-depth", "10", "--duck-attack", "10", "--duck-release", "300")
    dsp("delay", f"{WORK}/throw_send16.wav", f"{WORK}/throw_final_raw.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.35", "--hp", "400", "--lp", "3500", "--return-db", "0")
    raw, _ = read_audio(f"{WORK}/throw_final_raw.wav")
    final_delta = first_tap_delta_db(pitched, raw[:, 0], [final_word], half / 1000)
    final_return = -12.0 - final_delta
    print(f"final ring at 0 dB return is {final_delta:+.1f} dB; return set to {final_return:+.1f} dB", flush=True)
    dsp("delay", f"{WORK}/throw_send16.wav", f"{WORK}/throw_b3_16.wav", "--bpm", "129", "--note", "1/2",
        "--feedback", "0.35", "--hp", "400", "--lp", "3500", "--return-db", f"{final_return:.2f}",
        "--duck-by", f"{WORK}/phone_bus.wav", "--duck-depth", "4", "--duck-attack", "5", "--duck-release", "80")
    # No separate block-2 half-note throw in v16: the quarter-note delay already answers that line.
    write_audio(f"{WORK}/throw_b2_16.wav", np.zeros((SR, 2)))
    for tag in ("4",):
        dsp("reverb", f"{WORK}/throw_b2_{tag}.wav", f"{WORK}/throw_b2_hall_{tag}.wav", "--type", "hall",
            "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-10")
        dsp("reverb", f"{WORK}/throw_b3_{tag}.wav", f"{WORK}/throw_b3_hall_{tag}.wav", "--type", "hall",
            "--decay", "2.7907", "--predelay", "29.07", "--return-db", "-8")
    dsp("reverb", f"{WORK}/throw_b3_16.wav", f"{WORK}/throw_b3_hall_16.wav", "--type", "hall",
        "--decay", "2.7907", "--predelay", "29.07", "--return-db", "-12")
    write_audio(f"{WORK}/throw_b2_hall_16.wav", np.zeros((SR, 2)))

    # Halls on the calls. Block 2 and block 3 get an extra, longer one.
    dsp("reverb", f"{WORK}/phone_bus.wav", f"{WORK}/hall_all.wav", "--type", "hall",
        "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-14",
        "--duck-by", f"{WORK}/phone_bus.wav", "--duck-depth", "3")
    for block, decay, ret, name in ((2, "1.86047", "-9", "hall_b2"), (3, "2.7907", "-7", "hall_b3")):
        mask = np.zeros_like(phone_bus)
        for p in placed:
            if p["block"] == block:
                mask[p["i0"]:p["i1"]] = phone_bus[p["i0"]:p["i1"]]
        write_audio(f"{WORK}/{name}_send.wav", mask)
        dsp("reverb", f"{WORK}/{name}_send.wav", f"{WORK}/{name}.wav", "--type", "hall",
            "--decay", decay, "--predelay", "29.07", "--return-db", ret)

    beat, _ = read_audio(f"{WORK}/beat.wav")
    fx, _ = read_audio(f"{WORK}/fx.wav")
    # v4's fade to -10 dB, then the last second finishes to silence so the beat's
    # hard stop at 2:39 does not punch a hole after the echoes have faded.
    beat = fade_db(beat, 150.698, 157.4, 0, -10)
    beat = fade_db(beat, 157.4, 159.15, -10, -40)
    fx = fade_db(fx, 150.698, 157.4, 0, -10)
    fx = fade_db(fx, 157.4, 159.15, -10, -40)
    write_audio(f"{WORK}/beat_f.wav", beat)
    write_audio(f"{WORK}/fx_f.wav", fx)
    # Printed throws that land on the "and" instead of the beat. 58.2 starts on the
    # quarter (10 ms) so it stays. 134.95-135.30 is a 1-beat copy and a 2-beat copy
    # on top of each other; 6 dB down leaves one copy's level.
    offbeat = [(35.50, 35.90), (39.20, 39.60), (42.95, 43.55), (46.90, 47.45),
               (54.55, 54.90), (60.90, 61.45)]
    fx16 = mute_regions(fx, offbeat)
    fx16 = mute_regions(fx16, [(134.95, 135.35)], gain_db=-6.0)
    write_audio(f"{WORK}/fx_16.wav", fx16)

    def outro_bus(tag, phone_path, delay):
        tracks = [phone_path, delay, f"{WORK}/hall_all.wav", f"{WORK}/hall_b2.wav", f"{WORK}/hall_b3.wav",
                  f"{WORK}/throw_b2_{tag}.wav", f"{WORK}/throw_b3_{tag}.wav",
                  f"{WORK}/throw_b2_hall_{tag}.wav", f"{WORK}/throw_b3_hall_{tag}.wav"]
        args = ["mix", f"{WORK}/outro_{tag}.wav"]
        for t in tracks:
            args += ["--track", f"{t}:0"]
        dsp(*args)
        x, _ = read_audio(f"{WORK}/outro_{tag}.wav")
        write_audio(f"{WORK}/outro_{tag}.wav", x * 10 ** (OUTRO_BUS / 20))

    # v4 reference uses the dry phone lines (no stutters) plus the unpitched delay.
    write_audio(f"{WORK}/phone_bus4.wav", phone + add_hiss(phone))
    # Rebuild v4 halls? The shared halls include stutters. Make a v4-only call hall so the
    # verse-null stays honest and the v4 outro is the v4 outro.
    dsp("reverb", f"{WORK}/phone_bus4.wav", f"{WORK}/hall_all4.wav", "--type", "hall",
        "--decay", "1.86047", "--predelay", "29.07", "--return-db", "-14",
        "--duck-by", f"{WORK}/phone_bus4.wav", "--duck-depth", "3")
    for block, decay, ret, name in ((2, "1.86047", "-9", "hall_b2_4"), (3, "2.7907", "-7", "hall_b3_4")):
        mask = np.zeros_like(phone)
        bus4 = phone + add_hiss(phone)
        for p in placed:
            if p["block"] == block:
                mask[p["i0"]:p["i1"]] = bus4[p["i0"]:p["i1"]]
        write_audio(f"{WORK}/{name}_send.wav", mask)
        dsp("reverb", f"{WORK}/{name}_send.wav", f"{WORK}/{name}.wav", "--type", "hall",
            "--decay", decay, "--predelay", "29.07", "--return-db", ret)
    dsp("mix", f"{WORK}/outro_4.wav",
        "--track", f"{WORK}/phone_bus4.wav:0", "--track", f"{WORK}/phone_delay4.wav:0",
        "--track", f"{WORK}/hall_all4.wav:0", "--track", f"{WORK}/hall_b2_4.wav:0",
        "--track", f"{WORK}/hall_b3_4.wav:0", "--track", f"{WORK}/throw_b2_4.wav:0",
        "--track", f"{WORK}/throw_b3_4.wav:0", "--track", f"{WORK}/throw_b2_hall_4.wav:0",
        "--track", f"{WORK}/throw_b3_hall_4.wav:0")
    x, _ = read_audio(f"{WORK}/outro_4.wav")
    write_audio(f"{WORK}/outro_4.wav", x * 10 ** (OUTRO_BUS / 20))
    outro_bus("16", f"{WORK}/phone_bus.wav", f"{WORK}/phone_delay16.wav")

    bed = [
        "--track", f"{WORK}/beat_f.wav:0",
        "--track", f"{WORK}/lead.wav:{LEAD_FADER}",
        "--track", f"{WORK}/ad.wav:{ADLIB_FADER}",
        "--track", f"{WORK}/plate.wav:{LEAD_FADER}",
    ]
    dsp("mix", f"{WORK}/mix4.wav", *bed,
        "--track", f"{WORK}/ad_delay4.wav:{ADLIB_FADER}",
        "--track", f"{WORK}/lead_echo4.wav:{LEAD_FADER}",
        "--track", f"{WORK}/v1_throw4.wav:{LEAD_FADER}",
        "--track", f"{WORK}/v1_throw_hall4.wav:{LEAD_FADER}",
        "--track", f"{WORK}/fx_f.wav:0",
        "--track", f"{WORK}/outro_4.wav:0")
    dsp("mix", f"{WORK}/mix16.wav", *bed,
        "--track", f"{WORK}/ad_delay.wav:{ADLIB_FADER}",
        "--track", f"{WORK}/lead_echo.wav:{LEAD_FADER}",
        "--track", f"{WORK}/v1_throw.wav:{LEAD_FADER}",
        "--track", f"{WORK}/v1_throw_hall.wav:{LEAD_FADER}",
        "--track", f"{WORK}/fx_16.wav:0",
        "--track", f"{WORK}/outro_16.wav:0")
    dsp("ms-bus", f"{WORK}/mix4.wav", f"{WORK}/bus4.wav", "--side-hp", "90", "--mid-shelf", "9500:2.0")
    dsp("ms-bus", f"{WORK}/mix16.wav", f"{WORK}/bus16.wav", "--side-hp", "90", "--mid-shelf", "9500:2.0")

    def trim_tail(src, dst):
        x, _ = read_audio(src)
        m = np.sqrt((x ** 2).mean(axis=1))
        thr = 10 ** (-50 / 20)
        idx = np.flatnonzero(m > thr)
        last = int(idx[-1]) if len(idx) else len(m) - 1
        end = min(len(x), last + int(0.5 * SR))
        fade = int(2.0 * SR)
        y = x[:end].copy()
        if len(y) > fade:
            y[-fade:] *= np.linspace(1, 0, fade)[:, None]
        write_audio(dst, y)
        print(f"trimmed {src} to {end / SR:.2f}s", flush=True)

    trim_tail(f"{WORK}/bus4.wav", f"{WORK}/bus4_t.wav")
    trim_tail(f"{WORK}/bus16.wav", f"{WORK}/bus16_t.wav")

    sh([sys.executable, os.path.join(TOOLS, "render_master.py"), f"{WORK}/bus4_t.wav", f"{WORK}/master4.wav",
        "--target-lufs", "-11.5", "--ceiling", "-0.7"])
    settings = json.load(open(f"{WORK}/master4.wav.settings.json"))
    gain = settings["gain_into_limiter_db"]
    limit = settings["limiter"]["limit_db"]
    print(f"v4 limiter gain {gain} dB, limit {limit} dB", flush=True)
    ffmpeg_af(f"{WORK}/bus16_t.wav", f"{WORK}/master16.wav",
              f"volume={gain:.3f}dB,aresample={SR * 4}:resampler=soxr,"
              f"alimiter=limit={limit:.3f}dB:attack=5:release=60:level=disabled:latency=true,"
              f"aresample={SR}:resampler=soxr")
    # Record settings for the report.
    settings16 = dict(settings)
    settings16["input"] = f"{WORK}/bus16_t.wav"
    settings16["output"] = f"{WORK}/master16.wav"
    settings16["note"] = "same limiter gain and ceiling as the v4 render so the verses stay identical"
    json.dump(settings16, open(f"{WORK}/master16.wav.settings.json", "w"), indent=2)

    # Loudness of both float masters.
    for name in ("master4.wav", "master16.wav"):
        sh([sys.executable, os.path.join(TOOLS, "analyze_audio.py"), f"{WORK}/{name}"])

    # Difference by section, before dither.
    a, _ = read_audio(f"{WORK}/master4.wav")
    b, _ = read_audio(f"{WORK}/master16.wav")
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    diff = b - a
    sections = [("intro / verse", 0, 70), ("verse into the break", 70, 100),
                ("second verse", 100, 130), ("just before the phone", 130, 134.4),
                ("phone outro", 134.4, n / SR)]
    print("\nDifference energy, v16 minus the v4 render (same limiter):", flush=True)
    report_rows = []
    for label, t0, t1 in sections:
        i0, i1 = int(t0 * SR), min(n, int(t1 * SR))
        if i1 <= i0:
            continue
        e_diff = float(np.sqrt((diff[i0:i1] ** 2).mean()))
        e_ref = float(np.sqrt((a[i0:i1] ** 2).mean()))
        db = 20 * math.log10(e_diff / e_ref + 1e-12)
        print(f"  {label:24} {t0:6.1f}-{t1:6.1f}s  difference {db:7.1f} dB vs the v4 section")
        report_rows.append((label, t0, t1, db))

    # Echo timing table from the delay returns themselves (the sample delay, before the mix).
    q_samples = int(round(quarter * SR / 1000))
    h_samples = int(round(half * SR / 1000))
    d_samples = int(round(dotted * SR / 1000))
    rows = []
    for lo, hi in words:
        rows.append(measure("lead line-end echo", lo, lo + q_samples / SR, quarter) |
                    {"vs_v4": "whole word, same 465.12 ms lag, 3 repeats, about -12 dB", "note": "1/4",
                     "word_end": hi})
    tw = throw_word[0][0]
    rows.append(measure("verse-1 half-note throw", tw, tw + h_samples / SR, half) |
                {"vs_v4": "whole word, same 930.23 ms lag, level pulled to -12 dB", "note": "1/2"})
    ad_m = ad[:, 0]
    for a0, a1 in ad_phrases:
        rows.append(measure("adlib delay", a0, a0 + d_samples / SR, dotted) |
                    {"vs_v4": "same dotted-eighth lag and 0.35 feedback; level -12 dB; faster duck", "note": "1/8d"})
    for p in placed:
        on, off = speech_bounds(phone, p["i0"], p["i1"])
        if p["block"] == 3 and p["name"] == "B":
            rows.append(measure("phone ring, last interstate", on, on + h_samples / SR, half) |
                        {"vs_v4": "half-note ring only, pitched +3, -12 dB, 3 repeats", "note": "1/2"})
        else:
            rows.append(measure(f"phone delay, block {p['block']} line {p['name']}", on, on + q_samples / SR, quarter) |
                        {"vs_v4": "pitched +3, same 465.12 ms lag, -12 dB, 3 repeats", "note": "1/4"})
    for s in stutter_rows:
        off8, _ = grid_offset_ms(s["start"], 8)
        off16, _ = grid_offset_ms(s["start"], 16)
        rows.append({"what": f"stutter {s['line']} {s['k']}/{s['of']}", "source_s": s["word"],
                     "first_tap_s": s["start"], "lag_ms": (s["start"] - s["word"]) * 1000,
                     "note_ms": s["chop_ms"], "off_8th_ms": off8, "off_16th_ms": off16,
                     "vs_v4": "new, outro only", "note": "stutter", "gap_ms": s["gap_ms"],
                     "syl_ms": s["syl_ms"], "gain_db": s["gain_db"]})

    # Confirm one lead echo and one adlib echo by cross-correlation against the wet return.
    echo, _ = read_audio(f"{WORK}/lead_echo.wav")
    lo, hi = words[0]
    src = lead[int(lo * SR):int(hi * SR), 0]
    lag = xcorr_lag_ms(src, echo[:, 0], SR, q_samples / SR)
    print(f"measured lead-echo lag {lag:.2f} ms (expected {q_samples / SR * 1000:.2f})", flush=True)
    ad_d, _ = read_audio(f"{WORK}/ad_delay.wav")
    # A loud adlib moment.
    db, hop = env_db(ad_m, 0.01)
    loud = int(np.argmax(db))
    src_a = ad_m[int(loud * hop):int(loud * hop) + int(0.2 * SR)]
    lag_a = xcorr_lag_ms(src_a, ad_d[:, 0], SR, d_samples / SR)
    print(f"measured adlib-delay lag {lag_a:.2f} ms (expected {d_samples / SR * 1000:.2f})", flush=True)
    ph, _ = read_audio(f"{WORK}/phone_delay16.wav")
    on, _ = speech_bounds(phone, placed[0]["i0"], placed[0]["i1"])
    src_p = pitched[int(on * SR):int(on * SR) + int(0.25 * SR)]
    lag_p = xcorr_lag_ms(src_p, ph[:, 0], SR, q_samples / SR)
    print(f"measured pitched phone-delay lag {lag_p:.2f} ms (expected {q_samples / SR * 1000:.2f})", flush=True)

    # Effects only: echoes, delays, the verse throw, the outro ring and the stutters.
    # No dry vocal, no beat, no plate, no halls, no printed FX stem.
    dsp("mix", f"{WORK}/fxbus16.wav",
        "--track", f"{WORK}/lead_echo.wav:{LEAD_FADER}",
        "--track", f"{WORK}/v1_throw.wav:{LEAD_FADER}",
        "--track", f"{WORK}/ad_delay.wav:{ADLIB_FADER}",
        "--track", f"{WORK}/phone_delay16.wav:{OUTRO_BUS}",
        "--track", f"{WORK}/throw_b3_16.wav:{OUTRO_BUS}",
        "--track", f"{WORK}/stutters.wav:{OUTRO_BUS}")
    dsp("mix", f"{WORK}/fxbus4.wav",
        "--track", f"{WORK}/lead_echo4.wav:{LEAD_FADER}",
        "--track", f"{WORK}/v1_throw4.wav:{LEAD_FADER}",
        "--track", f"{WORK}/ad_delay4.wav:{ADLIB_FADER}",
        "--track", f"{WORK}/phone_delay4.wav:{OUTRO_BUS}",
        "--track", f"{WORK}/throw_b2_4.wav:{OUTRO_BUS}",
        "--track", f"{WORK}/throw_b3_4.wav:{OUTRO_BUS}")
    dsp("mix", f"{WORK}/dry.wav",
        "--track", f"{WORK}/lead.wav:{LEAD_FADER}",
        "--track", f"{WORK}/ad.wav:{ADLIB_FADER}",
        "--track", f"{WORK}/phone_lines.wav:{OUTRO_BUS}")
    fxb, _ = read_audio(f"{WORK}/fxbus16.wav")
    fx4, _ = read_audio(f"{WORK}/fxbus4.wav")
    dry, _ = read_audio(f"{WORK}/dry.wav")
    level_rows = []
    print("\nEffects bus vs dry vocal (negative means the echoes are under the vocal):", flush=True)
    for label, t0, t1 in (("verse 1", 20, 60), ("break", 61, 74), ("verse 2", 75, 125),
                          ("phone outro", 134.5, 155), ("fade", 155, 168)):
        def rms(sig, a, b):
            i0, i1 = int(a * SR), min(len(sig), int(b * SR))
            if i1 <= i0:
                return 1e-12
            return float(np.sqrt((sig[i0:i1] ** 2).mean()))
        d16 = 20 * math.log10(rms(fxb, t0, t1) / rms(dry, t0, t1))
        d4 = 20 * math.log10(rms(fx4, t0, t1) / rms(dry, t0, t1))
        print(f"  {label:12} v16 {d16:+6.1f} dB   v4 {d4:+6.1f} dB   change {d16 - d4:+5.1f} dB")
        level_rows.append({"section": label, "v16_db": round(d16, 2), "v4_db": round(d4, 2)})

    json.dump({"rows": rows, "sections": report_rows, "levels": level_rows,
               "lead_lag_ms": lag, "adlib_lag_ms": lag_a, "phone_lag_ms": lag_p,
               "stutters": stutter_rows, "words": words, "lead_return_db": lead_return,
               "ad_return_db": ad_return, "phone_return_db": phone_return,
               "throw_return_db": throw_return, "final_return_db": final_return,
               "limiter_gain_db": gain, "limiter_db": limit},
              open(f"{WORK}/timings.json", "w"), indent=2)
    print(f"wrote {WORK}/timings.json ({len(rows)} rows)", flush=True)
    sh([sys.executable, os.path.join(TOOLS, "export_master.py"), f"{WORK}/fxbus16.wav",
        "--name", "Pushing_the_Interstate_v16_effects_bus", "--outdir", SONG, "--rate", "44100",
        "--mp3", "none"])

    sh([sys.executable, os.path.join(TOOLS, "export_master.py"), f"{WORK}/master16.wav",
        "--name", "Pushing_the_Interstate_master_v16", "--outdir", SONG, "--rate", "44100"])
    sh(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-ss", "128", "-i",
        os.path.join(SONG, "Pushing_the_Interstate_master_v16_24bit.wav"),
        "-b:a", "320k", os.path.join(SONG, "Outro_preview_v16.mp3")])
    print("export done", flush=True)


if __name__ == "__main__":
    main()

"""Driftin' Away v1: every creative effect, placed on the beat grid measured from the drums.

Grid: 150 BPM (the beat matched against itself 8-48 bars apart), beat n at G0 + 0.4 n s, G0 = 38.37 ms
(the hi-hats sit on this eighth grid, median 4 ms). Bar b starts at G0 + (b - 1) * 1.6 s.

Writes (all 32-bit float, full song length, wet returns only where noted):
  beat_fx.wav        the beat with two eighth-note air gaps before the drops at bar 17 and bar 57
  echo_lead.wav      dreamy echoes on the lead's line-ending words (wet)
  echo_adlib.wav     dreamy echoes on the adlib responses in the second half (wet)
  revswell.wav       reverse-reverb swells into the first word of the verse, the drop at bar 41, and the
                     background vocal's entrance (wet)
  phone.wav          the phone-call outro lines with stutters, telephone sound and line hiss
  echo_phone.wav     echoes on the phone lines' last words (wet)
  fx_events.json     every event with its exact times, for the log and the checks
"""
import os
import json
import math
import subprocess
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402

D = os.path.join(os.environ.get("DRIFT_WORK", "."), "")  # folder with the stems and renders
sr = 44100
G0, Q = 0.03837, 0.4
BAR = 4 * Q
S16 = Q / 4


def beat_t(n):
    return G0 + n * Q


def bar_t(b, beat=1):
    return G0 + (b - 1) * BAR + (beat - 1) * Q


def next_beat(t, min_gap=0.10):
    return beat_t(math.ceil((t + min_gap - G0) / Q - 1e-9))


def nearest_beat(t):
    return beat_t(round((t - G0) / Q))


def bb(t):
    k = round((t - G0) / Q, 3)
    bar = int(k // 4) + 1
    return f"{bar}.{k - (bar - 1) * 4 + 1:.2f}"


def mono(x):
    return x.mean(axis=1) if x.ndim > 1 else x


# ---------------------------------------------------------------- word attacks
BAND = butter(4, [300, 5000], "bandpass", fs=sr, output="sos")
HOP = int(0.0025 * sr)


def envelope_db(x):
    b = sosfiltfilt(BAND, mono(x))
    n = len(b) // HOP
    r = np.sqrt((b[:n * HOP].reshape(n, HOP) ** 2).mean(axis=1))
    r = np.convolve(r, np.ones(4) / 4, mode="same")  # 10 ms
    return 20 * np.log10(r + 1e-9)


def attacks_in(env, t0, t1, rise=6.0):
    """Times where the level rises by `rise` dB within 25 ms from a local low (start of a syllable)."""
    i0, i1 = max(10, int(t0 / 0.0025)), min(len(env) - 1, int(t1 / 0.0025))
    out, last = [], -1
    for i in range(i0, i1):
        lo = env[i - 10:i].min()
        if env[i] - lo >= rise and env[i] > env[i - 1] and i - last > 24:
            j = i - 10 + int(np.argmin(env[i - 10:i]))  # back to the low point, then forward to the first rise
            k = j
            while k < i and env[k + 1] - env[j] < 1.5:
                k += 1
            out.append(k * 0.0025)
            last = i
    return out


def word_end(env, t_attack, t_max):
    """Last moment the word is within 30 dB of its own peak (before t_max)."""
    i0, i1 = int(t_attack / 0.0025), int(t_max / 0.0025)
    pk = env[i0:i1].max()
    above = np.where(env[i0:i1] > pk - 30)[0]
    return (i0 + above[-1]) * 0.0025


def last_word(env, line_end, look=0.75, min_len=0.12):
    ats = [a for a in attacks_in(env, line_end - look, line_end) if line_end - a >= min_len]
    a = ats[-1] if ats else line_end - 0.35
    return a, word_end(env, a, line_end + 0.05)


def first_attack(env, t_approx, win=0.12):
    ats = attacks_in(env, t_approx - win, t_approx + win)
    return min(ats, key=lambda a: abs(a - t_approx)) if ats else t_approx


def first_sound(x, t_from, t_to, rel_db=-30.0):
    """The first moment the voice is within rel_db of its loudest point in [t_from, t_to] (2 ms envelope).
    A reverse swell must end here, on the very first sound of the word, not on a later syllable's rise."""
    seg = np.abs(mono(x[int(t_from * sr):int(t_to * sr)]))
    k = int(0.002 * sr)
    env = np.convolve(seg, np.ones(k) / k, mode="same")
    return t_from + int(np.where(env > env.max() * 10 ** (rel_db / 20))[0][0]) / sr


def fades(seg, fin, fout):
    seg = seg.copy()
    a, b = int(fin * sr), int(fout * sr)
    if a:
        seg[:a] *= np.linspace(0, 1, a)[:, None] if seg.ndim > 1 else np.linspace(0, 1, a)
    if b:
        seg[-b:] *= np.linspace(1, 0, b)[:, None] if seg.ndim > 1 else np.linspace(1, 0, b)
    return seg


# ---------------------------------------------------------------- echoes on the beat
ECHO_BAND = butter(2, [250, 5500], "bandpass", fs=sr, output="sos")
DARK = butter(1, 4200, "lowpass", fs=sr, output="sos")


def render_echoes(src, events, n, first_db, step_db, label):
    """Each event: (attack, end, taps). The echo copy starts with its attack ON the next main beat after the word
    ends (at least 100 ms after), then once per beat; each repeat step_db quieter and a little darker;
    alternating left/right (not hard). Zero-phase filters, so the attack does not move."""
    out = np.zeros((n, 2))
    log = []
    pre = 0.005
    for att, end, taps in events:
        i, j = int((att - pre) * sr), int((end + 0.04) * sr)
        seg = fades(mono(src[i:j]), 0.003, 0.04)
        y = sosfiltfilt(ECHO_BAND, seg)
        t1 = next_beat(end)
        times = []
        for k in range(taps):
            if k:
                y = sosfiltfilt(DARK, y)
            tk = t1 + k * Q
            g = 10 ** ((first_db + k * step_db) / 20)
            s = int(round((tk - pre) * sr))
            e = min(n, s + len(y))
            pan = (1.0, 0.45) if k % 2 == 0 else (0.45, 1.0)
            norm = 1 / math.sqrt((pan[0] ** 2 + pan[1] ** 2) / 2)
            out[s:e, 0] += y[:e - s] * g * pan[0] * norm
            out[s:e, 1] += y[:e - s] * g * pan[1] * norm
            times.append(round(tk, 4))
        log.append({"src": label, "word": [round(att, 4), round(end, 4)], "word_at": bb(att), "echo_times": times,
                    "first_echo_at": bb(times[0]), "levels_db": [first_db + k * step_db for k in range(taps)]})
    return out, log


# ---------------------------------------------------------------- reverse reverb swell
def reverse_swell(src, att, start_t, word_len, gain_db, decay=2.4):
    """Classic reverse reverb: reverse the word, reverb it, reverse the result. The part before the word's attack is
    the swell; it ends exactly at the dry attack and starts exactly at start_t (a beat)."""
    i = int(att * sr)
    w = fades(mono(src[i:i + int(word_len * sr)]), 0.002, 0.03)
    ir = dt.make_ir(sr, "hall", decay, 0.0, 1.0, seed=7)
    wet = np.stack([fftconvolve(w[::-1], ir[:, c]) for c in range(2)], 1)[::-1]
    M = len(ir)
    swell = wet[:M - 1]  # everything before the attack
    L = int(round((att - start_t) * sr))
    swell = swell[-L:].copy()
    ramp = np.linspace(0, 1, L) ** 2  # rises into the word
    swell *= ramp[:, None]
    swell = fades(swell, 0.0, 0.004)
    pk_w = np.abs(w).max()
    swell *= (pk_w / (np.abs(swell).max() + 1e-12)) * 10 ** (gain_db / 20)
    return swell, int(round(start_t * sr))


# ---------------------------------------------------------------- build
def main():
    beat, _ = dt.read(D + "01_Beat.wav")
    n = len(beat) + int(4 * sr)
    lead, _ = dt.read(D + "l_8.wav")
    lead_raw, _ = dt.read(D + "l_2.wav")
    bgv, _ = dt.read(D + "b_7.wav")
    bgv_raw, _ = dt.read(D + "b_2.wav")
    # v1: a_7.wav; v2: a_8.wav (the second-half responses levelled to one another, level_adlibs.py)
    adl, _ = dt.read(D + __import__("os").environ.get("ADLIB_SRC", "a_7.wav"))
    adl_raw, _ = dt.read(D + "a_2.wav")
    envL, envB, envA = envelope_db(lead_raw), envelope_db(bgv_raw), envelope_db(adl_raw)
    ev = {"grid": {"bpm": 150, "g0_s": G0, "bar_s": BAR}}

    # 1. beat air gaps before the drops at bar 17 and bar 57: silence for the last eighth note, beat back exactly
    #    on the drop's own transient (found in the beat, not assumed)
    bfx = beat.copy()
    bm = mono(beat)
    lowb = sosfiltfilt(butter(4, 150, "lowpass", fs=sr, output="sos"), bm)
    gaps = []
    for b in (17, 57):
        t_drop = bar_t(b)
        w0, w1 = int((t_drop - 0.03) * sr), int((t_drop + 0.03) * sr)
        e = np.abs(lowb[w0:w1])
        on = w0 + int(np.argmax(e > 0.1 * e.max()))  # first sample at 10% of the drop's peak low end
        g_start = int(round((t_drop - Q / 2) * sr))
        g_end = on - int(0.001 * sr)
        f = int(0.003 * sr)
        bfx[g_start:g_start + f] *= np.linspace(1, 0, f)[:, None]
        bfx[g_start + f:g_end] = 0.0
        # the beat comes back over the last 1 ms before the drop's transient (no step, so no click)
        bfx[g_end:on] *= np.linspace(0, 1, on - g_end)[:, None]
        gaps.append({"bar": b, "gap_s": [round(g_start / sr, 4), round(g_end / sr, 4)], "gap_at": bb(g_start / sr),
                     "drop_transient_s": round(on / sr, 4), "grid_downbeat_s": round(t_drop, 4),
                     "transient_vs_grid_ms": round((on / sr - t_drop) * 1000, 1)})
    dt.write(D + "beat_fx.wav", bfx, sr)
    ev["air_gaps"] = gaps

    # 2. lead line-end echoes (line ends found from the breath dips; 4 repeats into stops and section ends)
    # Only line ends whose first echo lands in a clear gap (the next line starts at least 100 ms after it).
    # Left out: 35.76 and 45.25 (the next line starts 70-100 ms around the first echo), 63.51 (the reverse swell
    # into the drop owns that beat). 60.43 gets 2 repeats (the a cappella line comes back at 61.86) and 76.67 gets
    # 2 (the reverse swell into the background vocal takes over on bar 49 beat 3).
    lead_ends = [(29.30, 3), (32.44, 3), (38.86, 3), (42.06, 3), (60.43, 2), (66.95, 3), (70.17, 3), (76.67, 2)]
    events = []
    for t_end, taps in lead_ends:
        a, e = last_word(envL, t_end + 0.03)
        events.append((a, e, taps))
    echo_l, log_l = render_echoes(lead, events, n, first_db=-9.0, step_db=-5.0, label="lead")

    # 3. adlib responses in the second half: last word, 3 repeats (4 on the last one, into the outro)
    resp = [(80.21, 82.00), (83.63, 85.08), (86.82, 88.45), (90.13, 91.64), (93.23, 94.84), (96.43, 98.12),
            (99.66, 101.47), (102.86, 104.53), (104.87, 109.05), (111.50, 113.23), (114.71, 116.42),
            (118.07, 120.02), (121.28, 123.22), (124.72, 126.27), (130.90, 132.75), (135.93, 138.91)]
    events = []
    for k, (s, t_end) in enumerate(resp):
        a, e = last_word(envA, t_end)
        events.append((a, e, 4 if k == len(resp) - 1 else 3))
    echo_a, log_a = render_echoes(adl, events, n, first_db=-8.0, step_db=-5.0, label="adlib")

    # ducking: light and fast (the lesson from Pushing the Interstate: heavy, slow ducking makes echoes sound late)
    key = np.zeros((n, 2))
    for v in (lead, bgv, adl):
        key[:len(v)] += v[:n]
    g, thr, pct = dt.duck_gain(key, sr, n, 3.0, None, 5, 120)
    echo_l *= g[:, None]
    echo_a *= g[:, None]
    dt.write(D + "echo_lead.wav", echo_l, sr)
    dt.write(D + "echo_adlib.wav", echo_a, sr)
    ev["echo_ducking"] = {"depth_db": 3, "attack_ms": 5, "release_ms": 120, "fully_ducked_pct": round(pct, 1)}
    ev["echoes"] = log_l + log_a

    # 4. reverse-reverb swells, each starting on a beat and ending on the dry attack
    sw = np.zeros((n, 2))
    swells = []
    for label, src, raw, t_from, t_to, st in (
            ("first word of the verse", lead, lead_raw, 26.6, 27.2, bar_t(17, 2)),      # bar 17 beat 2 -> word
            ("lead into the drop at bar 41", lead, lead_raw, 63.8, 64.4, bar_t(40, 4)),  # bar 40 beat 4 -> word
            ("background vocal entrance", bgv, bgv_raw, 77.8, 78.4, bar_t(49, 3))):      # bar 49 beat 3 -> word
        att = first_sound(raw, t_from, t_to)
        y, s = reverse_swell(src, att, st, 0.45, gain_db=-6.0)
        sw[s:s + len(y)] += y
        swells.append({"what": label, "attack_s": round(att, 4), "attack_at": bb(att), "swell_start_s": round(st, 4),
                       "swell_start_at": bb(st), "length_s": round(att - st, 3)})
    dt.write(D + "revswell.wav", sw, sr)
    ev["reverse_swells"] = swells

    # 5. phone-call outro: lines A and B of the verse, moved by whole bars (+74, then +80), stutters before each
    A0 = first_attack(envL, 26.86)
    B0 = first_attack(envL, 30.09)
    A1 = 29.30
    B1 = 32.44
    lines = {"A": (A0, word_end(envL, A1 - 0.3, A1 + 0.05)), "B": (B0, word_end(envL, B1 - 0.3, B1 + 0.05))}
    dry = np.zeros((n, 2))
    stut = np.zeros((n, 2))
    placed = []
    for name, bars in (("A", 74), ("B", 74), ("A", 80), ("B", 80)):
        a, e = lines[name]
        shift = bars * BAR
        i, j = int((a - 0.01) * sr), int((e + 0.06) * sr)
        seg = fades(lead[i:j], 0.004, 0.05)
        s = int(round((a - 0.01 + shift) * sr))
        dry[s:s + len(seg)] += seg
        # stutters: first 75 ms of the first syllable, 4 times on the 16th notes right before the line's beat
        pick = nearest_beat(a) + shift
        st = []
        for k, gdb in zip(range(4, 0, -1), (-1.5, -1.0, -0.5, 0.0)):
            tk = pick - k * S16
            if tk + 0.075 > a + shift - 0.012:
                continue
            ss = fades(lead[int(a * sr):int((a + 0.075) * sr)], 0.003, 0.015) * 10 ** (gdb / 20)
            p = int(round(tk * sr))
            stut[p:p + len(ss)] += ss
            st.append(round(tk, 4))
        placed.append({"line": name, "moved_bars": bars, "start_s": round(a + shift, 4), "start_at": bb(a + shift),
                       "end_s": round(e + shift, 4), "stutters_s": st, "stutters_at": [bb(x) for x in st]})
    dt.write(D + "phone_dry.wav", dry + stut, sr)
    # telephone sound: 420 Hz-3.2 kHz, +4 dB at 1.8 kHz, 8 kHz sample rate, a little drive, 6:1 compression
    chain = ("highpass=f=420:poles=2,highpass=f=420:poles=2,lowpass=f=3200:poles=2,lowpass=f=3200:poles=2,"
             "equalizer=f=1800:t=q:w=1.2:g=4,aresample=8000,aresample=44100,"
             "acompressor=threshold=-24dB:ratio=6:attack=3:release=80:makeup=6,asoftclip=type=tanh:threshold=0.7")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", D + "phone_dry.wav", "-af", chain,
                    "-c:a", "pcm_f32le", D + "phone_tel.wav"], check=True)
    tel, _ = dt.read(D + "phone_tel.wav")
    tel = tel[:n] if len(tel) >= n else np.concatenate((tel, np.zeros((n - len(tel), 2))))
    # line hiss under each phone line (band 1-4 kHz), 34 dB under the line, with 60 ms fades
    rng = np.random.default_rng(3)
    hiss = sosfilt(butter(2, [1000, 4000], "bandpass", fs=sr, output="sos"), rng.standard_normal(n))
    act = np.zeros(n)
    for p in placed:
        s, e = int((p["stutters_s"][0] if p["stutters_s"] else p["start_s"]) * sr) - int(0.1 * sr), int(p["end_s"] * sr) + int(0.2 * sr)
        act[s:e] = 1
    act = np.convolve(act, np.ones(int(0.06 * sr)) / int(0.06 * sr), mode="same")
    line_rms = math.sqrt(np.mean(tel[act > 0.99] ** 2))
    hiss *= act * line_rms * 10 ** (-34 / 20) / (np.sqrt(np.mean(hiss ** 2)) + 1e-12)
    tel += hiss[:, None] * math.sqrt(0.5)
    dt.write(D + "phone.wav", tel, sr)
    ev["phone_lines"] = placed
    ev["phone_chain"] = chain + "; line hiss 1-4 kHz at -34 dB under the line"

    # 6. echoes on the phone lines' last words (from the telephone sound, so the echoes sound like the call)
    envT = envelope_db(tel)
    events = []
    for p in placed:
        if p["line"] != "B":  # line A runs straight into B's stutters, so only the end of each A-B pair echoes
            continue
        a, e = last_word(envT, p["end_s"] + 0.03)
        events.append((a, e, 4))
    echo_p, log_p = render_echoes(tel, events, n, first_db=-8.0, step_db=-5.0, label="phone")
    dt.write(D + "echo_phone.wav", echo_p, sr)
    ev["echoes"] += log_p

    json.dump(ev, open(D + "fx_events.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in ev.items() if k != "echoes"}, indent=1))
    print("echo events:")
    for r in ev["echoes"]:
        print(f"   {r['src']:6s} word {r['word'][0]:7.3f}-{r['word'][1]:7.3f} ({r['word_at']:>7s})  echoes from {r['first_echo_at']:>7s}: "
              + " ".join(f"{t:.3f}" for t in r["echo_times"]))


if __name__ == "__main__":
    main()

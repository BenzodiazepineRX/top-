# Satans Casino v6 build, kept as a worked example of bar-end echo throws, reverse-reverb swells and filter sweeps.
# Run it in a working folder that holds:
#   track1.wav  composite track (beat + main vocal), untouched
#   c6_pan.wav  processed adlibs (chain in PROJECT_LOG.md), panned like the original
# Set DSP_TOOLS to the path of dsp_tools.py from the song-mix-master skill.
# Only change from the script as run on 2026-11-01: file paths (the audio it renders is identical).
import os, subprocess, json, csv, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt, lfilter, lfilter_zi
from scipy.ndimage import binary_closing, binary_opening
SR = 44100
BPM = 135.0; Q = 60 / BPM; BAR = 4 * Q          # 444.444 ms, 1777.778 ms
B0 = 0.118                                      # AS RUN, AND WRONG BY ABOUT 95 ms. The real bar line in these files is at
                                                # 0.0205 s (hats and kick clicks land 24 ms into the file). 0.118 came from
                                                # the kick's low end, which is biased. Effect on v6: the high-pass sweep into
                                                # bar 50 ended 97 ms after the downbeat and took 16.5 dB of bass off the first
                                                # hit. Use 0.0205 in any rebuild. See ../README.md.
SHIFT_S = 0.026                                 # adlib recording-latency correction (median of 11 confident phrases)
TOOLS = os.environ["DSP_TOOLS"]
RIDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools", "vocal_rider.py")
T1, T2, T3 = B0 + 9 * BAR, B0 + 49 * BAR, B0 + 89 * BAR   # beat drop bar 10; returns bar 50, bar 90
def bb(t):  # absolute seconds -> "bar.beat" (1-based, beat with 2 decimals)
    x = round((t - B0) / Q, 4); return f"{int(x // 4) + 1}.{x % 4 + 1:.2f}"
def run(*a): return subprocess.run(["python3", TOOLS, *a], capture_output=True, text=True, check=True).stdout.strip()
def w(fn, x): sf.write(fn, np.asarray(x, np.float32), SR, subtype="FLOAT")
cues = []

# 1) Adlib timing: constant 26 ms earlier (whole take), then re-level against track 1 at the new timing
x, _ = sf.read("c6_pan.wav"); sh = int(round(SHIFT_S * SR))
w("v6_ad_shift.wav", np.vstack([x[sh:], np.zeros((sh, 2))]))
lev = subprocess.run(["python3", RIDER, "v6_ad_shift.wav", "track1.wav", "v6_ad.wav", "--gain-db", "4.62", "--margin-db", "6"], capture_output=True, text=True, check=True).stdout
ad, _ = sf.read("v6_ad.wav"); adm = ad.mean(1); w("v6_ad_mono.wav", np.stack([adm, adm], 1))

# word/phrase activity on the leveled adlib (10 ms blocks, threshold p95-20 dB, close 150 ms, open 120 ms)
blk = int(0.01 * SR); n = len(adm) // blk
e = 20 * np.log10(np.sqrt(np.mean(adm[:n * blk].reshape(n, blk) ** 2, 1)) + 1e-12)
on = e > np.percentile(e[e > -80], 95) - 20
on_s = binary_opening(binary_closing(on, np.ones(15)), np.ones(12))
d = np.diff(np.r_[0, on_s.astype(int), 0]); ph_st = np.where(d == 1)[0] * 0.01; ph_en = np.where(d == -1)[0] * 0.01

# 2) Echo throws: last word(s) of each bar that has adlib in its final 1.5 beats.
#    Send window = last <=0.45 s ending at that word's end (10 ms ramps in/out). Half-note on the last bar before each breakdown/outro.
section_end_bars = {40, 80, 104}
th_q, th_h = [], []
nb = int((len(adm) / SR - B0) / BAR)
for k in range(1, nb + 1):
    bl = B0 + k * BAR; i0, i1 = int((bl - 1.5 * Q) / 0.01), int((bl + 0.12) / 0.01)
    if i1 >= n: break
    seg = on[i0:i1]
    if seg.sum() < 8: continue
    end = (i0 + np.where(seg)[0][-1] + 1) * 0.01; st = max(end - 0.45, i0 * 0.01)
    (th_h if k in section_end_bars else th_q).append((st, end, k))
fmt = lambda L: ",".join(f"{a:.2f}-{b:.2f}" for a, b, _ in L)
dq = run("delay", "v6_ad_mono.wav", "v6_throws_q.wav", "--bpm", "135", "--note", "1/4", "--feedback", "0.30", "--hp", "200", "--lp", "5000",
         "--throws", fmt(th_q), "--duck-by", "v6_ad_mono.wav", "--duck-depth", "6", "--return-db", "-6").splitlines()[0]
dh = run("delay", "v6_ad_mono.wav", "v6_throws_h.wav", "--bpm", "135", "--note", "1/2", "--feedback", "0.30", "--hp", "200", "--lp", "5000",
         "--throws", fmt(th_h), "--duck-by", "v6_ad_mono.wav", "--duck-depth", "6", "--return-db", "-6").splitlines()[0]
for a, b, k in th_q: cues.append(dict(fx="echo throw 1/4 (444.444 ms)", source="adlib (track 2)", target_or_window=f"send {a:.3f}-{b:.3f}", bar_beat=f"{bb(a)}-{bb(b)}", start_s=round(a, 3), end_s=round(b, 3), setting="fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB", note=f"last word(s) of bar {k}"))
for a, b, k in th_h: cues.append(dict(fx="echo throw 1/2 (888.889 ms)", source="adlib (track 2)", target_or_window=f"send {a:.3f}-{b:.3f}", bar_beat=f"{bb(a)}-{bb(b)}", start_s=round(a, 3), end_s=round(b, 3), setting="fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB", note=f"last bar {k} before breakdown/outro"))

# 3) Regular adlib reverb: smooth plate 1.2 s, 27.8 ms (1/64) pre-delay, 300-5000 Hz send, ducked 6 dB
rv = run("reverb", "v6_ad_mono.wav", "v6_verb.wav", "--type", "plate", "--decay", "1.2", "--predelay", "27.8", "--hp", "300", "--lp", "5000",
         "--duck-by", "v6_ad_mono.wav", "--duck-depth", "6", "--return-db", "-14").splitlines()[0]

# 4) Reverse-reverb swells into upcoming adlib entrances at real transitions (100% wet, dry kept out)
def onset_near(T, lo=-0.3, hi=0.6):
    c = [s for s in ph_st if T + lo <= s <= T + hi]; return c[0] if c else None
# phrase re-entries: (start, silence before it); real phrases only (>=0.3 s)
real = [(a, b) for a, b in zip(ph_st, ph_en) if b - a >= 0.3]
gaps = [(real[i][0], real[i][0] - (real[i - 1][1] if i else 0.0)) for i in range(len(real))]
used = [real[0][0], onset_near(T2, -0.3, 1.0), onset_near(T3, -0.3, 1.0)]
extra = max([g for g in gaps if all(u is None or abs(g[0] - u) > 8 for u in used)], key=lambda g: g[1])
print("re-entries with longest silence before:", sorted(gaps, key=lambda g: -g[1])[:6])
swell_targets = [("first adlib entrance (pickup into bar 11, after beat drop bar 10)", real[0][0], 0.01, BAR / 2),
                 ("adlib entrance after breakdown, beat return bar 50", T2, 1.0, BAR),
                 ("adlib entrance after breakdown, beat return bar 90", T3, 1.0, BAR),
                 (f"adlib re-entry after longest other silence ({extra[1]:.2f} s)", extra[0], 0.01, BAR / 2)]
swells = np.zeros((len(adm), 2)); swell_log = []
for name, Tref, hi, L in swell_targets:
    T = onset_near(Tref, -0.3, hi)
    if T is None: swell_log.append((name, Tref, None)); continue
    i = int(T * SR); word = adm[i:i + int(0.40 * SR)].copy(); word[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    buf = np.zeros(int(4.5 * SR)); buf[:len(word)] = word[::-1]; w("tmp_rev_in.wav", np.stack([buf, buf], 1))
    run("reverb", "tmp_rev_in.wav", "tmp_rev_wet.wav", "--type", "hall", "--decay", "2.4", "--predelay", "0", "--hp", "200", "--lp", "6000", "--return-db", "0")
    wet, _ = sf.read("tmp_rev_wet.wav"); rr = wet[::-1]
    nL = int(L * SR); nw = len(word)                               # drop the last word-length (reversed smear of the word's END),
    sw = rr[len(rr) - nw - nL:len(rr) - nw].copy()                  # so the crescendo of the word's ONSET finishes at T
    fi, fo = int(0.15 * SR), int(0.02 * SR)
    sw[:fi] *= np.linspace(0, 1, fi)[:, None]; sw[-fo:] *= np.linspace(1, 0, fo)[:, None]   # fade completes exactly at T
    sw *= 10 ** (-12 / 20) / (np.max(np.abs(sw)) + 1e-12) * np.max(np.abs(word))  # moderate level vs the word
    s0 = i - nL; swells[s0:i] += sw[:i - s0]
    peak_t = (s0 + np.argmax(np.abs(sw).sum(1))) / SR
    swell_log.append((name, T, L, s0 / SR, peak_t))
    cues.append(dict(fx=f"reverse reverb swell ({'half bar 888.889 ms' if abs(L-BAR/2)<1e-6 else 'one bar 1777.778 ms'})", source="first word of upcoming adlib phrase (reversed, 100% wet hall 2.4 s, 200-6000 Hz)",
                     target_or_window=f"lands at T={T:.3f}", bar_beat=f"{bb(s0/SR)} -> {bb(T)}", start_s=round(s0 / SR, 3), end_s=round(T, 3),
                     setting="fade-in 150 ms, fade-out 20 ms ending at T, peak -12 dB vs word peak", note=f"{name}; rendered loudest point {peak_t:.3f}s"))
w("v6_swells.wav", swells)

# 5) Filter sweeps on TRACK 1 (composite beat + main vocal: the main vocal is filtered too)
t, _ = sf.read("track1.wav")
def sweep(x, t0, t1, f0, f1, kind):
    y = x.copy(); B = 32; i0, i1 = int(t0 * SR), int(t1 * SR)
    zi = None; seg = x[i0:i1]; out = np.zeros_like(seg)
    for j in range(0, len(seg), B):
        frac = (j + B / 2) / len(seg); fc = f0 * (f1 / f0) ** frac           # log-frequency ramp
        b, a = butter(2, fc, kind, fs=SR)                                      # 12 dB/oct, Q 0.707 (no resonance peak)
        if zi is None: zi = np.stack([lfilter_zi(b, a) * seg[0, c] for c in range(2)])
        for c in range(2):
            out[j:j + B, c], zi[c] = lfilter(b, a, seg[j:j + B, c], zi=zi[c])
    # 50% loudness compensation (block RMS, 100 ms smoothing, max +4 dB)
    r_in = np.sqrt(np.convolve(seg.mean(1) ** 2, np.ones(4410) / 4410, "same") + 1e-12); r_out = np.sqrt(np.convolve(out.mean(1) ** 2, np.ones(4410) / 4410, "same") + 1e-12)
    g = np.clip((r_in / r_out) ** 0.5, 1, 10 ** (4 / 20)); out *= g[:, None]
    xf = int(0.01 * SR); out[:xf] = seg[:xf] * np.linspace(1, 0, xf)[:, None] + out[:xf] * np.linspace(0, 1, xf)[:, None]  # 10 ms crossfade in (no filter-start click)
    out[-xf:] = out[-xf:] * np.linspace(1, 0, xf)[:, None] + seg[-xf:] * np.linspace(0, 1, xf)[:, None]  # 10 ms crossfade back to dry at T
    y[i0:i1] = out; return y
sweeps = [("A: low-pass opens 1000 -> 18000 Hz over 2 bars", T1 - 2 * BAR, T1, 1000, 18000, "lowpass"),
          ("B: high-pass rises 30 -> 400 Hz over 1 bar, lows restored at T", T2 - BAR, T2, 30, 400, "highpass"),
          ("C: low-pass opens 800 -> 18000 Hz over 2 bars", T3 - 2 * BAR, T3, 800, 18000, "lowpass")]
tf = t.copy()
for name, a, b, f0, f1, kind in sweeps:
    tf = sweep(tf, a, b, f0, f1, kind)
    cues.append(dict(fx="filter sweep (COMPOSITE: beat + main vocal)", source="track 1", target_or_window=f"lands at T={b:.3f}", bar_beat=f"{bb(a)} -> {bb(b)}", start_s=round(a, 3), end_s=round(b, 3),
                     setting=f"{kind} {f0}->{f1} Hz log, 2nd-order Butterworth (12 dB/oct, Q 0.707), 50% gain comp (max +4 dB), 10 ms crossfades in and at T", note=name))
w("v6_track1_fx.wav", tf)

# 6) Mix (track 1 at unity; adlib already at its leveled gain)
mix = run("mix", "v6_mix.wav", "--track", "v6_track1_fx.wav:0", "--track", "v6_ad.wav:0", "--track", "v6_throws_q.wav:0", "--track", "v6_throws_h.wav:0",
          "--track", "v6_verb.wav:-2", "--track", "v6_swells.wav:0").splitlines()[-1]
mixb = run("mix", "v6_mix_noFX.wav", "--track", "track1.wav:0", "--track", "v6_ad.wav:0", "--track", "v6_verb.wav:-2").splitlines()[-1]   # spotlight-FX bypass
fx = run("mix", "v6_fx_only.wav", "--track", "v6_throws_q.wav:0", "--track", "v6_throws_h.wav:0", "--track", "v6_swells.wav:0").splitlines()[-1]

cues.sort(key=lambda c: c["start_s"])
with open("v6_FX_cue_sheet.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(cues[0].keys())); wr.writeheader(); wr.writerows(cues)
json.dump(dict(B0=B0, T1=T1, T2=T2, T3=T3, shift_ms=SHIFT_S * 1000, leveler=json.loads(lev), delay_q=dq, delay_h=dh, reverb=rv,
               swells=swell_log, throws_q=len(th_q), throws_h=len(th_h), mix=mix, mix_noFX=mixb, fx_only=fx), open("v6_build_log.json", "w"), indent=1, default=str)
print("T1 %.3f (%s)  T2 %.3f (%s)  T3 %.3f (%s)" % (T1, bb(T1), T2, bb(T2), T3, bb(T3)))
print("throws: %d quarter, %d half" % (len(th_q), len(th_h))); print(dq); print(dh); print(rv)
for s in swell_log: print("swell:", s)
print(mix); print("cues:", len(cues))

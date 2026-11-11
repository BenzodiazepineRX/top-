# What I'm Posed To Do - version 1 build (rebuilt 2026-11-11 after the first session's files were lost).
# Run from the song folder:  python3 build_v1.py
import os, subprocess, json, sys
import numpy as np, soundfile as sf, librosa, psola, pyloudnorm
from scipy.signal import butter, sosfiltfilt, medfilt, lfilter

SR = 44100; BPM = 135.0; Q = 60 / BPM; BAR = 4 * Q; G0 = 0.004           # bar lines at G0 + n*BAR (hats/kick clicks)
T = "/home/user/top-/music/tools"
W = os.environ.get("W", "work"); os.makedirs(W, exist_ok=True)
STRENGTH = float(os.environ.get("TUNE", "0.85"))
log = {"tune_strength": STRENGTH}
def run(*a):
    r = subprocess.run(["python3", f"{T}/dsp_tools.py", *a], capture_output=True, text=True)
    if r.returncode: sys.exit("dsp_tools failed: " + " ".join(a) + "\n" + r.stderr[-800:])
    return r.stdout.strip()
def ff(src, dst, af): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-c:a", "pcm_f32le", dst], check=True)
def wr(fn, x): sf.write(fn, np.asarray(x, np.float32), SR, subtype="FLOAT")
def st2(x): return np.stack([x, x], 1)
def bar(n): return G0 + (n - 1) * BAR                                    # start time of bar n (1-based)
meter = pyloudnorm.Meter(SR)
def lufs(x, a, b): return meter.integrated_loudness(x[int(a * SR):int(b * SR)])
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)

beat, _ = sf.read("src/Beat.wav", always_2d=True); N = len(beat)
_lo = sosfiltfilt(butter(4, 120, "low", fs=SR, output="sos"), beat, axis=0); _hi = beat - _lo
_b = int(0.005 * SR); _n = N // _b; _pk = np.abs(_lo[:_n * _b]).max(1).reshape(_n, _b).max(1)
_pk = np.maximum.reduce([_pk, np.r_[_pk[1:], 0], np.r_[0, _pk[:-1]]]); _thr = np.percentile(_pk[_pk > 0.02], 92)
_g = np.minimum(1.0, (_thr / np.maximum(_pk, 1e-9)) ** 0.0); _g = np.convolve(_g, np.ones(3) / 3, "same")
_gs = np.interp(np.arange(N), (np.arange(_n) + 0.5) * _b, _g)
beat = _hi + _lo * _gs[:, None]; wr(f"{W}/beat.wav", beat)
log["beat_low_end"] = dict(band="below 120 Hz", threshold_dBFS=round(float(20 * np.log10(_thr)), 1), max_cut_dB=round(float(-20 * np.log10(_g.min())), 1), pct_time_cut_over_1dB=round(float(100 * np.mean(_g < 0.891)), 1))
blk = int(0.01 * SR); NB = N // blk
def level_blocks(x): return 20 * np.log10(np.sqrt(np.mean(x[:NB * blk].reshape(NB, blk) ** 2, 1)) + 1e-12)

# ---------- 1. autotune toward D minor / F major notes (A4 = 439.5 Hz); only the part of each file that has sound
SCALE = np.array([2, 4, 5, 7, 9, 10, 0])                                  # D E F G A Bb C
def snap(f0, a4=439.5):
    midi = 69 + 12 * np.log2(f0 / a4); out = np.full_like(midi, np.nan)
    ok = ~np.isnan(midi); m = midi[ok]
    cand = (np.floor(m)[:, None] + np.arange(-6, 7)[None, :])
    good = np.isin(np.mod(cand, 12), SCALE); d = np.where(good, np.abs(cand - m[:, None]), 99)
    out[ok] = cand[np.arange(len(m)), np.argmin(d, 1)]
    return a4 * 2 ** ((out - 69) / 12)
def pyin(x): return librosa.pyin(x, fmin=70, fmax=500, sr=SR, frame_length=2048, hop_length=512)[0]
def tune(x, f0, strength):
    tgt = snap(f0); kk = ~np.isnan(tgt); tgt[kk] = 2 ** medfilt(np.log2(tgt[kk]), 9)
    corr = f0 * (tgt / f0) ** strength
    k = ~np.isnan(corr); sm = corr.copy(); sm[k] = medfilt(corr[k], 5)
    return psola.vocode(x, sample_rate=SR, target_pitch=sm, fmin=70, fmax=500)
STEMS = {"L1": "Lead 1", "L2": "Lead 2", "B1": "Background lead", "B2": "Background lead 2"}
SPAN = {}
log["autotune"] = {}
for k, name in STEMS.items():
    fn = f"{W}/{k}_tuned_{STRENGTH}.wav"
    x, _ = sf.read(f"src/{name}.wav", always_2d=True); x = x.mean(1)
    e = 20 * np.log10(np.abs(x) + 1e-9); on = np.where(e > -50)[0]
    i, j = max(0, on[0] - SR), min(len(x), on[-1] + SR); SPAN[k] = (i / SR, j / SR)
    if os.path.exists(fn): continue
    f0fn = f"{W}/{k}_f0.npy"
    if os.path.exists(f0fn): f0 = np.load(f0fn)
    else: f0 = pyin(x[i:j]); np.save(f0fn, f0)
    y = tune(x[i:j], f0, STRENGTH)
    f1 = pyin(y); c0 = 1200 * np.log2(f0 / snap(f0)); c1 = 1200 * np.log2(f1 / snap(f1))
    tg = snap(f0); kk = ~np.isnan(tg); n0 = np.round(12 * np.log2(tg[kk])); n1 = np.round(12 * medfilt(np.log2(tg[kk]), 9))
    flips = (float(np.sum(np.diff(n0) != 0)), float(np.sum(np.diff(n1) != 0)))
    stt = dict(voiced_pct_of_span=round(100 * float((~np.isnan(f0)).mean()), 1),
               median_abs_cents_before=round(float(np.nanmedian(np.abs(c0))), 1), median_abs_cents_after=round(float(np.nanmedian(np.abs(c1))), 1),
               pct_within_15c_before=round(float(100 * np.nanmean(np.abs(c0[~np.isnan(c0)]) < 15)), 0),
               pct_within_15c_after=round(float(100 * np.nanmean(np.abs(c1[~np.isnan(c1)]) < 15)), 0), target_note_changes_before_after_hold=flips)
    z = np.zeros(N); n = min(len(y), j - i, N - i); z[i:i + n] = y[:n]
    wr(fn, st2(z)); json.dump(stt, open(f"{W}/{k}_tune_{STRENGTH}.json", "w")); print("autotune", k, stt, flush=True)
for k in STEMS: log["autotune"][k] = json.load(open(f"{W}/{k}_tune_{STRENGTH}.json"))

# ---------- 2. clean-up chain: level, high-pass, harsh-moment control, de-ess, gentle compression (no boosts, no saturation)
log["chain"] = {}
for k in STEMS:
    hp = "90" if k[0] == "L" else "120"
    a = run("gain-stage", f"{W}/{k}_tuned_{STRENGTH}.wav", f"{W}/{k}_1.wav", "--target-rms", "-18").splitlines()[0]
    run("hpf", f"{W}/{k}_1.wav", f"{W}/{k}_2.wav", "--freq", hp, "--order", "3")
    b = run("dyneq", f"{W}/{k}_2.wav", f"{W}/{k}_3.wav", "--freq", "3000", "--q", "1.5", "--auto-pct", "95").splitlines()[-1]
    ff(f"{W}/{k}_3.wav", f"{W}/{k}_4.wav", "acompressor=threshold=-22dB:ratio=2.5:attack=15:release=200:knee=6:detection=rms:makeup=1.6")
    c = run("deess", f"{W}/{k}_4.wav", f"{W}/{k}_5.wav", "--low", "5500", "--high", "9000", "--auto-pct", "97", "--max-cut", "6").splitlines()[-1]
    log["chain"][k] = [a, b, c]; print(k, a, "|", b, "|", c, flush=True)

# ---------- 3. even volume: every phrase toward the same level (ceiling switched off with a large negative margin)
log["rider"] = {}
for k in STEMS:
    r = subprocess.run(["python3", f"{T}/vocal_rider.py", f"{W}/{k}_5.wav", f"{W}/beat.wav", f"{W}/{k}_6.wav", "--margin-db", "-40"], capture_output=True, text=True, check=True).stdout
    log["rider"][k] = json.loads(r)["phrase_level_spread_dB"]; print("rider", k, log["rider"][k], flush=True)
V = {k: sf.read(f"{W}/{k}_6.wav", always_2d=True)[0].mean(1)[:N] for k in STEMS}

# ---------- 4. arrangement: fill the empty end. Each singer is cut at their own nearest quiet moment, moved by whole bars.
def quiet_point(x, t, win=0.6):
    i0, i1 = int((t - win) / 0.01), int((t + win) / 0.01); e = level_blocks(x)[i0:i1]
    e = np.convolve(e, np.ones(5) / 5, "same"); ok = np.where(e <= e.min() + 6)[0]
    tt = (i0 + ok) * 0.01 + 0.005; return float(tt[np.argmin(np.abs(tt - t))])
def moved(x, b0, b1, shift_bars):
    a, b = quiet_point(x, bar(b0)), quiet_point(x, bar(b1 + 1))
    i, j = int(a * SR), int(b * SR); seg = x[i:j].copy(); f = int(0.02 * SR)
    seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    out = np.zeros(N); d = i + int(round(shift_bars * BAR * SR)); n = min(len(seg), N - d); out[d:d + n] = seg[:n]
    return out, (round(a, 2), round(b, 2))
MOVES = [("second verse again, over the softer beat", 50, 65, 48),        # bars 50-65 -> 98-113
         ("full hook once more, over the full beat", 34, 49, 80)]         # bars 34-49 -> 114-129
log["arrangement"] = []
ORIG = {k: V[k].copy() for k in ("L1", "L2")}
for label, b0, b1, sh in MOVES:
    cuts = {}
    for k in ("L1", "L2"):
        m, cuts[k] = moved(ORIG[k], b0, b1, sh); V[k] = V[k] + m
    log["arrangement"].append(dict(what=label, from_bars=[b0, b1], to_bars=[b0 + sh, b1 + sh], cut_times_s=cuts))
_e = {k: level_blocks(V[k]) for k in ("L1", "L2")}; _t = {k: np.percentile(_e[k][_e[k] > -80], 95) - 22 for k in _e}
_both = np.repeat(((_e["L1"] > _t["L1"]) & (_e["L2"] > _t["L2"])).astype(float), blk); _both = np.r_[_both, np.zeros(N - len(_both))]
_both = np.convolve(_both, np.hanning(int(0.12 * SR)) / np.hanning(int(0.12 * SR)).sum(), "same")
for k in ("L1", "L2"): V[k] = V[k] * 10 ** (-3 * _both / 20)
log["both_leads_at_once"] = dict(seconds=round(float(_both.sum() / SR), 1), each_down_dB=3)
lead = V["L1"] + V["L2"]; bg = V["B1"] + V["B2"]

# ---------- 5. levels: leads 0.5 dB under the full beat while singing; the 2:10 voices 3 dB under the leads
FULL = [(bar(38), bar(50)), (bar(66), bar(74)), (bar(90), bar(98))]
bl = np.mean([lufs(beat, a, b) for a, b in FULL]); ll = np.mean([lufs(st2(lead), a, b) for a, b in FULL])
g_lead = (bl - 0.5) - ll; gl = 10 ** (g_lead / 20); lead *= gl
BG_UNDER = 3.0
bgl = lufs(st2(bg), bar(74), bar(82)); g_bg = (bl - 0.5 - BG_UNDER) - bgl; bg *= 10 ** (g_bg / 20)
log["levels"] = dict(beat_full_LUFS=round(bl, 1), lead_gain_dB=round(g_lead, 1), voices_at_2m10_gain_dB=round(g_bg, 1), voices_at_2m10_under_leads_dB=BG_UNDER)

# ---------- 6. created background vocals: a soft, wide, gently moving double of the leads on every hook
HOOKS = [(34, 49), (66, 73), (90, 97), (114, 129)]
DOUBLE_DB = -11.0
mask = np.zeros(N)
for a, b in HOOKS: mask[int(bar(a) * SR):min(N, int((bar(b + 1) + 0.3) * SR))] = 1
f = int(0.2 * SR); mask = np.convolve(mask, np.hanning(f) / np.hanning(f).sum(), "same")
srcd = sosfiltfilt(butter(2, [250, 5000], "band", fs=SR, output="sos"), (lead + bg) * mask)
tt = np.arange(N) / SR
def moving(x, base, depth, rate, ph): return np.interp(np.arange(N) - (base + depth * np.sin(2 * np.pi * rate * tt + ph)) * SR, np.arange(N), x, left=0, right=0)
stack = np.stack([moving(srcd, 0.013, 0.0012, 0.31, 0.0), moving(srcd, 0.021, 0.0012, 0.23, 1.7)], 1) * 10 ** (DOUBLE_DB / 20)
wr(f"{W}/lead.wav", st2(lead)); wr(f"{W}/bg.wav", st2(bg)); wr(f"{W}/stack.wav", stack)
log["double"] = dict(hooks_bars=HOOKS, level_dB_under_source=-DOUBLE_DB, band_Hz=[250, 5000], delays_ms=[13, 21], movement_ms=1.2)

# ---------- 7. telephone echo throws: the last few words of each singer's turn, on the beat, fading repeats
def peak_eq(x, f0, g_db, q):
    A = 10 ** (g_db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)
def phone(x, lp=3200): return peak_eq(sosfiltfilt(butter(2, [420, lp], "band", fs=SR, output="sos"), x), 1800, 3.0, 1.0)
e = level_blocks(lead); thr = np.percentile(e[e > -80], 95) - 22
GB = 10 ** (g_bg / 20); VG = {"L1": gl, "L2": gl, "B1": GB, "B2": GB}
FIRST_DB, STEP_DB = -7.0, -5.0
LPS = [3200, 2700, 2300, 2000, 1800, 1650, 1500, 1400]
throws = np.zeros((N + int(10 * SR), 2)); cue = []
allon = []
for who in ("L1", "L2", "B1", "B2"):
    x1 = V[who] * VG[who]; e1 = np.convolve(level_blocks(x1), np.ones(3) / 3, "same")
    on = e1 > thr
    # close gaps shorter than 180 ms, drop blips shorter than 150 ms
    d = np.diff(np.r_[0, on.astype(int), 0]); s_ = np.where(d == 1)[0]; t_ = np.where(d == -1)[0]
    segs = []
    for a, b in zip(s_, t_):
        if segs and a - segs[-1][1] < 18: segs[-1][1] = b
        else: segs.append([a, b])
    segs = [(a * 0.01, b * 0.01) for a, b in segs if b - a >= 15]
    allon += [(a, b, who) for a, b in segs]
allon.sort()
last_end = max(b for a, b, w in allon)
E1 = {who: np.convolve(level_blocks(V[who] * VG[who]), np.ones(3) / 3, "same") for who in VG}
for idx, (s_, t, who) in enumerate(allon):
    if t - s_ < 0.6: continue
    same_next = [a for a, b, w in allon if w == who and a > t]
    if same_next and same_next[0] - t < 0.5: continue                    # the same singer comes straight back: not a turn end
    # the gap after the words: 0 if another voice is already singing when they end, else the time to the next voice
    others = [(a, b) for a, b, w in allon if w != who]
    if any(a <= t + 0.05 and b > t + 0.15 for a, b in others): gap = 0.0
    else: gap = min([a - t for a, b in others if a > t] + [a - t for a in same_next] + [99.0])
    x1 = V[who] * VG[who]; e1 = E1[who]
    # the last few words: start at the deepest dip 0.30-0.86 s before the line ends, so the copy starts where a word starts
    lo, hi = int(max(s_, t + 0.04 - 0.86) / 0.01) + 1, int(max(s_, t - 0.30) / 0.01)
    if hi > lo: k0 = lo + int(np.argmin(e1[lo:hi + 1]))
    else: k0 = int(s_ / 0.01)
    a = k0 * 0.01
    word_lvl = np.percentile(e1[k0:int(t / 0.01) + 1], 80); dip = float(word_lvl - e1[k0])
    i, j = int(a * SR), int((t + 0.04) * SR); dry = x1[i:j].copy()
    fi, fo = int((0.012 if dip >= 10 else 0.035) * SR), int(0.03 * SR)   # a shallow dip (run-on words) gets a longer fade-in
    t0 = G0 + np.ceil((t + 0.03 - G0) / Q) * Q                           # first echo starts on the next beat after the words end
    final = abs(t - last_end) < 0.02
    if gap <= 0.3: reps = 1                                              # the next voice is already in: one answer only
    else: reps = int(np.clip(np.floor((t + gap - t0) / (2 * Q)) + 2, 2, 4))   # the repeats that fit in the gap, plus one
    if final: reps = 4
    step = -4.0 if final else STEP_DB
    dry_rms = rms_db(dry[fi:-fo])
    for r in range(reps):
        w = phone(np.r_[np.zeros(2000), x1[i:j], np.zeros(2000)], LPS[r])[2000:-2000]
        w *= 10 ** ((dry_rms + FIRST_DB + step * r - rms_db(w[fi:-fo])) / 20)
        w[:fi] *= np.linspace(0, 1, fi); w[-fo:] *= np.linspace(1, 0, fo)   # each copy set against its own dry words
        p = int(round((t0 + r * 2 * Q) * SR)); pan = (1.12, 0.84) if r % 2 == 0 else (0.84, 1.12)
        throws[p:p + len(w), 0] += w * pan[0]; throws[p:p + len(w), 1] += w * pan[1]
    cue.append(dict(singer=who, line_end_s=round(float(t), 2), words_from_s=round(float(a), 2), copy_len_s=round((j - i) / SR, 3), cut_dip_dB=round(dip, 1), first_echo_s=round(float(t0), 3),
                    repeats=reps, spacing_ms=round(2 * Q * 1000, 2), gap_after_s=round(float(min(gap, 99)), 2)))
wr(f"{W}/throws_raw.wav", throws[:N])
env = np.repeat((level_blocks(lead + bg) > thr).astype(float), blk); env = np.r_[env, np.zeros(N - len(env))]
env = np.convolve(env, np.ones(int(0.08 * SR)) / int(0.08 * SR), "same")   # duck the echoes 4 dB, fast, while a lead sings
tel = throws[:N] * (10 ** (-2 * env / 20))[:, None]; wr(f"{W}/throws.wav", tel)
log["throws"] = dict(count=len(cue), first_echo_dB_under_words=-FIRST_DB, step_dB=STEP_DB, band_Hz=[420, 3200], repeats={str(r): sum(c["repeats"] == r for c in cue) for r in (1, 2, 3, 4)}, shallow_cuts=sum(c["cut_dip_dB"] < 10 for c in cue))
json.dump(cue, open(f"{W}/throw_cues.json", "w"), indent=1)

# ---------- 8. reverbs: small plate on the leads, slight plate on the telephone echoes, hall on the backgrounds
wr(f"{W}/bgbus.wav", st2(bg) + stack)
log["reverb"] = [run("reverb", f"{W}/lead.wav", f"{W}/lead_verb.wav", "--type", "plate", "--decay", "1.333", "--predelay", "27.8", "--hp", "250", "--lp", "6000", "--duck-by", f"{W}/lead.wav", "--duck-depth", "4", "--return-db", "-17").splitlines()[0],
                 run("reverb", f"{W}/throws.wav", f"{W}/throw_verb.wav", "--type", "plate", "--decay", "0.889", "--predelay", "27.8", "--hp", "400", "--lp", "4000", "--return-db", "-12").splitlines()[0],
                 run("reverb", f"{W}/bgbus.wav", f"{W}/bg_verb.wav", "--type", "hall", "--decay", "1.778", "--predelay", "27.8", "--hp", "300", "--lp", "5000", "--return-db", "-13").splitlines()[0]]

# ---------- 9. mix, bus, master
log["mix"] = run("mix", f"{W}/mix.wav", "--track", f"{W}/beat.wav:0", "--track", f"{W}/lead.wav:0", "--track", f"{W}/bgbus.wav:0", "--track", f"{W}/throws.wav:0",
                 "--track", f"{W}/lead_verb.wav:0", "--track", f"{W}/throw_verb.wav:0", "--track", f"{W}/bg_verb.wav:0").splitlines()[-1]
run("ms-bus", f"{W}/mix.wav", f"{W}/mix_ms.wav", "--side-hp", "90", "--mid-shelf", "9500:0")
x, _ = sf.read(f"{W}/mix_ms.wav"); wr(f"{W}/mix_trim.wav", x[:N])
m = subprocess.run(["python3", f"{T}/render_master.py", f"{W}/mix_trim.wav", f"{W}/master.wav", "--target-lufs", "-11.9", "--ceiling", "-1.0"], capture_output=True, text=True, check=True).stdout
log["master"] = [l for l in m.splitlines() if l.startswith(("Result", "Limiter"))]
json.dump(log, open(f"{W}/build_log.json", "w"), indent=1, default=str)
print(json.dumps({k: log[k] for k in ("beat_low_end", "both_leads_at_once", "autotune", "rider", "arrangement", "levels", "throws", "reverb", "mix", "master")}, indent=1, default=str))

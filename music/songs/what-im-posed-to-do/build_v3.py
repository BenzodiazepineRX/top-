# What I'm Posed To Do - version 3 build. Run from a folder holding src/ (the five stems, beat renamed Beat.wav),
# words/ (word timing per vocal, from words/transcribe.py) and v3lib.py:   W=work_v3 python3 build_v3.py
# Changes against v2 are marked "v3:". Everything else is v2 unchanged.
import os, subprocess, json, sys
import numpy as np, soundfile as sf, pyloudnorm
from scipy.signal import butter, sosfiltfilt, lfilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3lib import tune_natural, hold_limiter

SR = 44100; BPM = 135.0; Q = 60 / BPM; BAR = 4 * Q; G0 = 0.004           # bar lines at G0 + n*BAR (hats/kick clicks)
T = "/home/user/top-/music/tools"
W = os.environ.get("W", "work_v3"); os.makedirs(W, exist_ok=True)
STRENGTH = float(os.environ.get("TUNE", "0.6"))
BASS_TIPS = float(os.environ.get("BASS_TIPS", "4.0"))                     # dB rounded off the tips of the loudest bass notes (below 150 Hz)
HITS = float(os.environ.get("HITS", "4.0"))                               # dB held off the sharpest drum hits (above 150 Hz)
CREST = float(os.environ.get("CREST", "12.0"))                           # a voice's peaks may stand this far over its level
TARGET = float(os.environ.get("TARGET", "-14.0"))
FIRST_DB = float(os.environ.get("FIRST_DB", "-2.5")); STEP_DB = -5.0
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
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-12)
def gstats(g): return dict(deepest_dB=round(float(-g.min()), 1), pct_time_over_1dB=round(float(100 * np.mean(g < -1)), 1), pct_time_over_3dB=round(float(100 * np.mean(g < -3)), 2))

# ---------- 0. beat. v3: this beat's 808 notes and drum hits are far bigger than the rest of it, so in v1/v2 the final
#               limiter pulled the whole song (voices included) down on every hit. Here the beat is dealt with on its own:
#               below 150 Hz only the tips of the loudest bass notes are rounded; above 150 Hz only the sharpest hits are held.
beat0, _ = sf.read("src/Beat.wav", always_2d=True); N = len(beat0)
_sos = butter(4, 150, "low", fs=SR, output="sos"); _lo = sosfiltfilt(_sos, beat0, axis=0); _hi = beat0 - _lo
def knee_clip(x, Tc, k=0.6):
    kk = k * Tc; a = np.abs(x); return np.sign(x) * np.where(a > kk, kk + (Tc - kk) * np.tanh((a - kk) / (Tc - kk)), a)
_Tl = float(np.abs(_lo).max()) * 10 ** (-BASS_TIPS / 20); _lo2 = knee_clip(_lo, _Tl)
_hi2, _gh = hold_limiter(_hi, float(np.abs(_hi).max()) * 10 ** (-HITS / 20), SR, look=0.002, hold=0.005, release_db_per_s=80.0)
beat = _lo2 + _hi2; wr(f"{W}/beat.wav", beat)
_i, _j = int((G0 + 65 * BAR) * SR), int((G0 + 73 * BAR) * SR)
log["beat"] = dict(bass_tips_rounded_dB=BASS_TIPS, pct_time_bass_rounded=round(float(100 * np.mean(np.abs(_lo).max(1) > 0.6 * _Tl)), 1),
                   bass_level_change_dB=round(float(10 * np.log10(np.mean(_lo2[_i:_j] ** 2) / np.mean(_lo[_i:_j] ** 2))), 2),
                   overtones_added_dB_under_bass=round(float(-10 * np.log10(np.mean((_lo2 - sosfiltfilt(_sos, _lo2, axis=0))[_i:_j] ** 2) / np.mean(_lo2[_i:_j] ** 2))), 1),
                   sharp_hits_held_dB=HITS, hits=gstats(_gh), peak_before_dBFS=round(float(20 * np.log10(np.abs(beat0).max())), 1), peak_after_dBFS=round(float(20 * np.log10(np.abs(beat).max())), 1))
blk = int(0.01 * SR); NB = N // blk
def level_blocks(x): return 20 * np.log10(np.sqrt(np.mean(x[:NB * blk].reshape(NB, blk) ** 2, 1)) + 1e-12)

# ---------- 1. v3: tuning by tiny speed changes on held notes only. The voice is not rebuilt, so its own pitch
#               movement stays. (v1 and v2 replaced the pitch with a smoothed, stepped line: the robot sound.)
STEMS = {"L1": "Lead 1", "L2": "Lead 2", "B1": "Background lead", "B2": "Background lead 2"}
log["autotune"] = {}
for k, name in STEMS.items():
    fn = f"{W}/{k}_nat_{STRENGTH}.wav"
    if not os.path.exists(fn):
        x, _ = sf.read(f"src/{name}.wav", always_2d=True); x = x.mean(1)
        e = 20 * np.log10(np.abs(x) + 1e-9); on = np.where(e > -50)[0]
        i, j = max(0, on[0] - SR), min(len(x), on[-1] + SR)
        y, info = tune_natural(x[i:j], SR, STRENGTH)
        z = np.zeros(N); n = min(len(y), N - i); z[i:i + n] = y[:n]
        wr(fn, st2(z)); json.dump(info, open(f"{W}/{k}_nat_{STRENGTH}.json", "w")); print("tune", k, info, flush=True)
    log["autotune"][k] = json.load(open(f"{W}/{k}_nat_{STRENGTH}.json"))

FAST = os.environ.get("FAST") and all(os.path.exists(f"{W}/{k}_6.wav") for k in ("L1", "L2", "B1", "B2")) and os.path.exists(f"{W}/build_log.json")
if FAST:
    _old = json.load(open(f"{W}/build_log.json")); log["chain"], log["rider"] = _old["chain"], _old["rider"]
else:
    # ---------- 2. clean-up chain (as v2): level, high-pass, harsh-moment control, cuts at 2.8 kHz and above 9 kHz,
    #               2:1 compressor, de-esser. No boosts, no saturation.
    log["chain"] = {}
    for k in STEMS:
        hp = "90" if k[0] == "L" else "120"
        a = run("gain-stage", f"{W}/{k}_nat_{STRENGTH}.wav", f"{W}/{k}_1.wav", "--target-rms", "-18").splitlines()[0]
        run("hpf", f"{W}/{k}_1.wav", f"{W}/{k}_2.wav", "--freq", hp, "--order", "3")
        b = run("dyneq", f"{W}/{k}_2.wav", f"{W}/{k}_3.wav", "--freq", "3000", "--q", "1.5", "--auto-pct", "95").splitlines()[-1]
        ff(f"{W}/{k}_3.wav", f"{W}/{k}_4.wav", "equalizer=f=2800:t=q:w=1.0:g=-3,highshelf=f=9000:g=-2.5,acompressor=threshold=-20dB:ratio=2:attack=20:release=200:knee=6:detection=rms:makeup=1.3")
        c = run("deess", f"{W}/{k}_4.wav", f"{W}/{k}_5.wav", "--low", "5500", "--high", "9000", "--auto-pct", "97", "--max-cut", "6").splitlines()[-1]
        log["chain"][k] = [a, b, c]; print(k, a, "|", b, "|", c, flush=True)

    # ---------- 3. even volume (as v2)
    log["rider"] = {}
    for k in STEMS:
        r = subprocess.run(["python3", f"{T}/vocal_rider.py", f"{W}/{k}_5.wav", f"{W}/beat.wav", f"{W}/{k}_6.wav", "--margin-db", "-40"], capture_output=True, text=True, check=True).stdout
        log["rider"][k] = json.loads(r)["phrase_level_spread_dB"]; print("rider", k, log["rider"][k], flush=True)
V = {k: sf.read(f"{W}/{k}_6.wav", always_2d=True)[0].mean(1)[:N] for k in STEMS}

# ---------- 3b. v3: each voice's sharpest peaks are held back on the voice alone, with the gain held 15 ms so it
#                never follows single pitch periods. In v1/v2 the final limiter did this job, up to 10 dB deep.
log["voice_peaks"] = {}
for k in STEMS:
    e = level_blocks(V[k]); act = np.repeat(e > np.percentile(e[e > -80], 95) - 22, blk); act = np.r_[act, np.zeros(N - len(act), bool)]
    lvl = rms(V[k][act]); pk0 = float(np.abs(V[k]).max())
    V[k], g = hold_limiter(V[k], lvl * 10 ** (CREST / 20), SR, look=0.005, hold=0.015, release_db_per_s=40.0)
    ga = g[np.repeat(e > np.percentile(e[e > -80], 95) - 22, 10)[:len(g)]] if len(g) <= NB * 10 else g
    log["voice_peaks"][k] = dict(peak_over_level_before_dB=round(20 * np.log10(pk0 / lvl), 1), allowed_dB=CREST, while_singing=gstats(ga))
    print("voice peaks", k, log["voice_peaks"][k], flush=True)

# ---------- 4. arrangement (as v2). Each singer is cut at their own nearest quiet moment, moved by whole bars.
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
MOVES = [("first 6 bars of verse 1, in the empty 2:25-2:38", 25, 30, 58),   # bars 25-30 -> 83-88
         ("second verse again, over the softer beat", 50, 65, 48),        # bars 50-65 -> 98-113
         ("full hook once more, over the full beat", 34, 49, 80)]         # bars 34-49 -> 114-129
log["arrangement"] = []
ORIG = {k: V[k].copy() for k in ("L1", "L2")}
CUTS = {k: [] for k in STEMS}
for label, b0, b1, sh in MOVES:
    cuts = {}
    for k in ("L1", "L2"):
        m, cuts[k] = moved(ORIG[k], b0, b1, sh); V[k] = V[k] + m; CUTS[k].append((cuts[k][0], cuts[k][1], sh * BAR))
    log["arrangement"].append(dict(what=label, from_bars=[b0, b1], to_bars=[b0 + sh, b1 + sh], cut_times_s=cuts))
_e = {k: level_blocks(V[k]) for k in ("L1", "L2")}; _t = {k: np.percentile(_e[k][_e[k] > -80], 95) - 22 for k in _e}
_both = np.repeat(((_e["L1"] > _t["L1"]) & (_e["L2"] > _t["L2"])).astype(float), blk); _both = np.r_[_both, np.zeros(N - len(_both))]
_both = np.convolve(_both, np.hanning(int(0.12 * SR)) / np.hanning(int(0.12 * SR)).sum(), "same")
for k in ("L1", "L2"): V[k] = V[k] * 10 ** (-3 * _both / 20)
log["both_leads_at_once"] = dict(seconds=round(float(_both.sum() / SR), 1), each_down_dB=3)
lead = V["L1"] + V["L2"]; bg = V["B1"] + V["B2"]

# ---------- 5. levels (as v2): leads 0.5 dB under the full beat while singing; the 2:10 voices 1.5 dB under the leads
FULL = [(bar(38), bar(50)), (bar(66), bar(74)), (bar(90), bar(98))]
bl = np.mean([lufs(beat, a, b) for a, b in FULL]); ll = np.mean([lufs(st2(lead), a, b) for a, b in FULL])
g_lead = (bl - 0.5) - ll; gl = 10 ** (g_lead / 20); lead *= gl
BG_UNDER = 1.5
bgl = lufs(st2(bg), bar(74), bar(82)); g_bg = (bl - 0.5 - BG_UNDER) - bgl; bg *= 10 ** (g_bg / 20)
log["levels"] = dict(beat_full_LUFS=round(bl, 1), lead_gain_dB=round(g_lead, 1), voices_at_2m10_gain_dB=round(g_bg, 1), voices_at_2m10_under_leads_dB=BG_UNDER)
wr(f"{W}/lead.wav", st2(lead)); wr(f"{W}/bg.wav", st2(bg)); wr(f"{W}/bgbus.wav", st2(bg))

# ---------- 7. v3: telephone background repeats. Each one now starts at the start of a real word (word timing from a
#               local speech model, then moved to the nearest dip in level), is set against what it has to be heard
#               over, and is not turned down while the leads sing.
def peak_eq(x, f0, g_db, q):
    A = 10 ** (g_db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)
def phone(x, lp=3600): return peak_eq(sosfiltfilt(butter(2, [380, lp], "band", fs=SR, output="sos"), x), 1800, 2.0, 1.0)
SOSB = butter(4, [400, 3600], "band", fs=SR, output="sos")
e = level_blocks(lead); thr = np.percentile(e[e > -80], 95) - 22
GB = 10 ** (g_bg / 20); VG = {"L1": gl, "L2": gl, "B1": GB, "B2": GB}
LPS = [3600, 3000, 2500, 2100]
WORDS = {}
for k in STEMS:
    w = json.load(open(f"words/{k}.json")); out = [(x["s"], x["e"], x["p"], x["w"]) for x in w]
    for a, b, sh in CUTS[k]: out += [(x["s"] + sh, x["e"] + sh, x["p"], x["w"]) for x in w if a <= x["s"] < b]
    WORDS[k] = sorted(out)
MASK = sosfiltfilt(SOSB, beat.mean(1) + lead + bg)                       # what each repeat has to be heard over, in the telephone band
throws = np.zeros((N + int(10 * SR), 2)); cue = []
allon = []
for who in VG:
    x1 = V[who] * VG[who]; e1 = np.convolve(level_blocks(x1), np.ones(3) / 3, "same")
    on = e1 > thr
    d = np.diff(np.r_[0, on.astype(int), 0]); s_ = np.where(d == 1)[0]; t_ = np.where(d == -1)[0]
    segs = []
    for a, b in zip(s_, t_):                                              # close gaps under 180 ms, drop blips under 150 ms
        if segs and a - segs[-1][1] < 18: segs[-1][1] = b
        else: segs.append([a, b])
    allon += [(a * 0.01, b * 0.01, who) for a, b in segs if b - a >= 15]
allon.sort()
last_end = max(b for a, b, w in allon)
E1 = {who: np.convolve(level_blocks(V[who] * VG[who]), np.ones(3) / 3, "same") for who in VG}
P = 2000
for idx, (s_, t, who) in enumerate(allon):
    if t - s_ < 0.6: continue
    same_next = [a for a, b, w in allon if w == who and a > t]
    if same_next and same_next[0] - t < 0.5: continue                    # the same singer comes straight back: not a turn end
    others = [(a, b) for a, b, w in allon if w != who]
    if any(a <= t + 0.05 and b > t + 0.15 for a, b in others): gap = 0.0
    else: gap = min([a - t for a, b in others if a > t] + [a - t for a in same_next] + [99.0])
    x1 = V[who] * VG[who]; e1 = E1[who]
    # the real end of the last word: follow the tail down until it is 28 dB under the words (at most 0.30 s more)
    kt = int(t / 0.01); wl = np.percentile(e1[max(0, kt - 60):kt + 1], 80); ke = kt
    while ke < kt + 30 and ke + 1 < len(e1) and e1[ke + 1] > wl - 28 and e1[ke + 1] <= e1[ke] + 1.5: ke += 1
    t_end = ke * 0.01 + 0.02
    # Where the copy starts: always at the start of a real word.
    #  - normally the earliest word start inside the last 0.86 s (a half note is 0.889 s), so as many whole words as fit;
    #  - if the last word is held longer than that, the copy is that whole word (up to 1.6 s); its repeat then starts
    #    while the held note is still ringing, as a real delay would.
    ws_all = []
    for ws, we, pr, tx in WORDS[who]:
        if ws < s_ - 0.25 or ws > t - 0.22: continue
        k0, k1 = int((ws - 0.08) / 0.01), int((ws + 0.05) / 0.01)
        kk = k0 + int(np.argmin(e1[k0:k1 + 1]))                           # the dip nearest the model's word start
        ws_all.append((kk * 0.01 + 0.005, pr, float(np.percentile(e1[kk:kt + 1], 80) - e1[kk])))
    inside = [c for c in ws_all if 0.45 <= t_end - c[0] <= 0.86]
    before = [c for c in ws_all if t_end - c[0] > 0.86]
    cut_end = t_end
    if inside: (a, pr, dip), how = min(inside), "words that fit"
    elif before: (a, pr, dip), how = max(before), "whole long last word"; cut_end = min(t_end, a + 1.6)   # the whole held word, so it is not cut short
    else:                                                                 # no word timing here: deepest dip, as v2
        lo, hi = int(max(s_, t_end - 0.86) / 0.01) + 1, int(max(s_, t - 0.30) / 0.01)
        kk = lo + int(np.argmin(e1[lo:hi + 1])) if hi > lo else int(s_ / 0.01)
        a, pr, dip, how = kk * 0.01, 0.0, float(np.percentile(e1[kk:kt + 1], 80) - e1[kk]), "dip"
    said = " ".join(tx for ws, we, p_, tx in WORDS[who] if a - 0.09 <= ws < cut_end - 0.05)
    i, j = int(a * SR), int(cut_end * SR)
    fi, fo = int((0.008 if dip >= 8 else 0.020) * SR), int((0.04 if cut_end == t_end else 0.12) * SR)
    t0 = a + 2 * Q                                                        # a true delay: the words come back exactly a half note later
    final = abs(t - last_end) < 0.02
    if gap <= 0.3: reps = 2
    else: reps = int(np.clip(np.floor((t + gap - t0) / (2 * Q)) + 2, 3, 4))
    if final: reps = 4
    step = -4.0 if final else STEP_DB
    ctx = x1[i - P:j + P]; dry = ctx[P:-P]
    eb = np.sqrt(np.convolve(dry ** 2, np.ones(441) / 441, "same")); loud = eb > eb.max() * 10 ** (-12 / 20)
    ref = rms(sosfiltfilt(SOSB, ctx)[P:-P][loud])                         # the words' own level in the telephone band
    i1 = max(P, int((t_end - 1.8) * SR)); ln = x1[i1 - P:int(t_end * SR) + P]
    el = np.sqrt(np.convolve(ln[P:-P] ** 2, np.ones(441) / 441, "same")); ref_line = rms(sosfiltfilt(SOSB, ln)[P:-P][el > el.max() * 10 ** (-12 / 20)])   # the whole line's level
    g0 = None
    for r in range(reps):
        w = phone(ctx, LPS[min(r, 3)])[P:-P]
        if g0 is None:
            own = rms(sosfiltfilt(SOSB, np.r_[np.zeros(P), w, np.zeros(P)])[P:-P][loud])
            want = max(ref * 10 ** (FIRST_DB / 20), ref_line * 10 ** (-6.0 / 20))     # 2.5 dB under its own words, and at least 6 dB under the line (for a quietly sung last word)
            cap = max(ref * 10 ** (-0.5 / 20), ref_line * 10 ** (-4.0 / 20))          # never over its words; for a quiet last word, never closer than 4 dB to the line
            p0 = int(round(t0 * SR)); need = rms(MASK[p0:p0 + len(w)][loud]) * 10 ** (-5.0 / 20)   # ... but within 5 dB of what it lands on
            tgt_ = min(max(need, want), cap); lift = float(20 * np.log10(tgt_ / (ref * 10 ** (FIRST_DB / 20))))
            g0 = tgt_ / own
        w = w * g0 * 10 ** (step * r / 20)
        w[:fi] *= np.linspace(0, 1, fi); w[-fo:] *= np.linspace(1, 0, fo)
        p = int(round((t0 + r * 2 * Q) * SR)); pan = (1.3, 0.4) if r % 2 == 0 else (0.4, 1.3)
        throws[p:p + len(w), 0] += w * pan[0]; throws[p:p + len(w), 1] += w * pan[1]
    cue.append(dict(singer=who, words=said, lifted_dB=round(lift, 1), under_the_line_dB=round(float(20 * np.log10(ref_line / tgt_)), 1), word_confidence=round(pr, 2), start_found_by=how, line_end_s=round(float(t), 2), words_end_s=round(float(t_end), 2),
                    words_from_s=round(float(a), 2), copy_len_s=round((j - i) / SR, 3), cut_dip_dB=round(dip, 1), first_echo_s=round(float(t0), 3),
                    repeats=reps, spacing_ms=round(2 * Q * 1000, 2), gap_after_s=round(float(min(gap, 99)), 2)))
wr(f"{W}/throws_raw.wav", throws[:N]); wr(f"{W}/throws.wav", throws[:N])
log["throws"] = dict(count=len(cue), first_repeat_dB_under_words_in_band=-FIRST_DB, step_dB=STEP_DB, band_Hz=[380, 3600], ducking="none",
                     repeats={str(r): sum(c["repeats"] == r for c in cue) for r in (2, 3, 4)}, start_found_by={h: sum(c["start_found_by"] == h for c in cue) for h in ("words that fit", "whole long last word", "dip")},
                     lifted_cues=sum(c["lifted_dB"] > 0.2 for c in cue), low_confidence_words=sum(c["start_found_by"] != "dip" and c["word_confidence"] < 0.5 for c in cue), shallow_cuts=sum(c["cut_dip_dB"] < 8 for c in cue))
json.dump(cue, open(f"{W}/throw_cues.json", "w"), indent=1)

# ---------- 8. reverbs (as v2)
log["reverb"] = [run("reverb", f"{W}/lead.wav", f"{W}/lead_verb.wav", "--type", "plate", "--decay", "1.333", "--predelay", "27.8", "--hp", "250", "--lp", "6000", "--duck-by", f"{W}/lead.wav", "--duck-depth", "3", "--return-db", "-15").splitlines()[0],
                 run("reverb", f"{W}/throws.wav", f"{W}/throw_verb.wav", "--type", "plate", "--decay", "0.889", "--predelay", "27.8", "--hp", "400", "--lp", "4500", "--return-db", "-10").splitlines()[0],
                 run("reverb", f"{W}/bgbus.wav", f"{W}/bg_verb.wav", "--type", "hall", "--decay", "1.778", "--predelay", "27.8", "--hp", "300", "--lp", "5000", "--return-db", "-13").splitlines()[0]]

# ---------- 9. mix, bus, master. v3: slower limiter release, and far less for the limiter to do.
log["mix"] = run("mix", f"{W}/mix.wav", "--track", f"{W}/beat.wav:0", "--track", f"{W}/lead.wav:0", "--track", f"{W}/bgbus.wav:0", "--track", f"{W}/throws.wav:0",
                 "--track", f"{W}/lead_verb.wav:0", "--track", f"{W}/throw_verb.wav:0", "--track", f"{W}/bg_verb.wav:0").splitlines()[-1]
run("ms-bus", f"{W}/mix.wav", f"{W}/mix_ms.wav", "--side-hp", "90", "--mid-shelf", "9500:0")
x, _ = sf.read(f"{W}/mix_ms.wav"); wr(f"{W}/mix_trim.wav", x[:N])
mixt = x[:N]; L0 = meter.integrated_loudness(mixt); g = TARGET - L0 + 0.3
for _ in range(4):                                                       # smooth limiter: 8 ms look-ahead, gain held 30 ms, slow release
    y, gd = hold_limiter(mixt * 10 ** (g / 20), 10 ** (-1.5 / 20), SR, look=0.008, hold=0.030, release_db_per_s=30.0)
    L = meter.integrated_loudness(y)
    if abs(TARGET - L) < 0.03: break
    g += TARGET - L
wr(f"{W}/master.wav", y)
_t = np.arange(len(gd)) * 0.001; lim = {}
for nm, a_, c_ in (("bars 38-49 full", 38, 50), ("bars 66-81 full", 66, 82), ("bars 114-129 full", 114, 130), ("bars 50-65 soft", 50, 66)):
    s_ = gd[(_t >= bar(a_)) & (_t < bar(c_))]; d5 = np.abs(s_[5:] - s_[:-5])
    lim[nm] = dict(p90_dB=round(float(-np.percentile(s_, 10)), 1), p99_dB=round(float(-np.percentile(s_, 1)), 1), deepest_dB=round(float(-s_.min()), 1),
                   pct_time_over_1dB=round(float(100 * np.mean(s_ < -1)), 0), sudden_drops_over_2dB_per_s=round(float(np.sum(np.diff((d5 > 2).astype(int)) == 1) / (len(s_) / 1000)), 2))
log["master"] = dict(integrated_LUFS=round(float(L), 2), gain_into_limiter_dB=round(float(g), 1), sample_peak_dBFS=round(float(20 * np.log10(np.abs(y).max())), 2), limiter=lim)
json.dump(log, open(f"{W}/build_log.json", "w"), indent=1, default=str)
print(json.dumps({k: log[k] for k in ("beat", "voice_peaks", "autotune", "rider", "levels", "throws", "mix", "master")}, indent=1, default=str))

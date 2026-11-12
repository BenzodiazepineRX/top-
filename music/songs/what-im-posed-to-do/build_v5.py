# What I'm Posed To Do - version 4 build (v3 plus the three things asked for after v3: lighter autotune, less scratch, echoes that start audibly). Run from a folder holding src/ (the five stems, beat renamed Beat.wav),
# words/ (word timing per vocal, from words/transcribe.py) and v3lib.py:   W=work_v3 python3 build_v3.py
# Changes against v3 are marked "v4:"; changes made after the independent checks (before anything was sent) are marked "v4 check:".
# Run: W=work_v4b python3 build_v4.py   (FAST=1 reuses the cleaned voices).
import os, subprocess, json, sys
import numpy as np, soundfile as sf, pyloudnorm
from scipy.signal import butter, sosfiltfilt, lfilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3lib import tune_natural, hold_limiter

SR = 44100; BPM = 135.0; Q = 60 / BPM; BAR = 4 * Q; G0 = 0.004           # bar lines at G0 + n*BAR (hats/kick clicks)
T = "/home/user/top-/music/tools"
W = os.environ.get("W", "work_v3"); os.makedirs(W, exist_ok=True)
STRENGTH = float(os.environ.get("TUNE", "0.45"))                          # v4: 0.60 -> 0.45
BASS_TIPS = float(os.environ.get("BASS_TIPS", "4.0"))                     # dB rounded off the tips of the loudest bass notes (below 150 Hz)
HITS = float(os.environ.get("HITS", "4.0"))                               # dB held off the sharpest drum hits (above 150 Hz)
CREST = float(os.environ.get("CREST", "13.0"))                           # v4 check: 12 -> 13 (12 acted on ~30% of the singing; 15 let lead peaks drive the final limiter)
SHELF_DB = float(os.environ.get("SHELF_DB", "-6")); SHELF_HZ = float(os.environ.get("SHELF_HZ", "4500")); BELL_DB = float(os.environ.get("BELL_DB", "-3"))
TUNE_FULL, TUNE_NONE = 40.0, 60.0                                        # v4 check: notes held 40-60+ cents from any scale note are left alone (sung on purpose)
PAN = (1.15, 0.45)                                                       # v4 check: was (1.3, 0.4), which put the echo over its own words in the louder ear   # v4: the tone cut that replaces the 2.8 kHz bell and the compressor
T_SNR = float(os.environ.get("T_SNR", "-3")); LIFT_MAX = float(os.environ.get("LIFT_MAX", "15")); LIFT_CAP = float(os.environ.get("LIFT_CAP", "1"))          # v4: how far under the live mix each echo is held, and the most it may be lifted                           # a voice's peaks may stand this far over its level
TARGET = float(os.environ.get("TARGET", "-14.5"))                        # v4: -14.0 -> -14.5 (no compressor means taller vocal peaks; this keeps the limiter at v3 levels or better)
STEP_DB = -5.0; FIRST_DB = float(os.environ.get("FIRST_DB", "-1.0"))                     # v5: "not getting through": 1.5 dB louder; STEP_DB = -5.0
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
    fn = f"{W}/{k}_nat_{STRENGTH}_ck.wav"
    if not os.path.exists(fn):
        x, _ = sf.read(f"src/{name}.wav", always_2d=True); x = x.mean(1)
        e = 20 * np.log10(np.abs(x) + 1e-9); on = np.where(e > -50)[0]
        i, j = max(0, on[0] - SR), min(len(x), on[-1] + SR)
        y, info = tune_natural(x[i:j], SR, STRENGTH, full_below=TUNE_FULL, none_above=TUNE_NONE)
        z = np.zeros(N); n = min(len(y), N - i); z[i:i + n] = y[:n]
        wr(fn, st2(z)); json.dump(info, open(f"{W}/{k}_nat_{STRENGTH}_ck.json", "w")); print("tune", k, info, flush=True)
    log["autotune"][k] = json.load(open(f"{W}/{k}_nat_{STRENGTH}_ck.json"))

FAST = os.environ.get("FAST") and all(os.path.exists(f"{W}/{k}_6.wav") for k in ("L1", "L2", "B1", "B2")) and os.path.exists(f"{W}/build_log.json")
if FAST:
    _old = json.load(open(f"{W}/build_log.json")); log["chain"], log["rider"] = _old["chain"], _old["rider"]
else:
    # ---------- 2. v4 chain: level, high-pass, v3's -3 dB bell at 2.8 kHz, a -6 dB shelf above 4.5 kHz, de-esser. Cuts only.
    #   Measured on v3 (checks/grit_by_stage.py): the 2:1 compressor raised fizz (5-12 kHz against the body) by 2.6 dB, pressing the vowels
    #   but not the s and breath noise, and did not even out word-to-word level (50 ms blocks p10-p90: 15.9 dB with it, 15.7 without). It is
    #   gone, and the dynamic EQ with it. The shelf takes fizz to the level of the owner's "Nearly PERFECT" Baccdoor lead (-34.4 dB).
    #   (An earlier draft of v4 also removed the bell on a "grit" reading; the independent check showed that reading was a tone-slope effect,
    #   and removing the bell raised 1.5-3.5 kHz by 1-1.6 dB against v3, so the bell is back.)
    log["chain"] = {}
    for k in STEMS:
        hp = "90" if k[0] == "L" else "120"
        a = run("gain-stage", f"{W}/{k}_nat_{STRENGTH}_ck.wav", f"{W}/{k}_1.wav", "--target-rms", "-18").splitlines()[0]
        run("hpf", f"{W}/{k}_1.wav", f"{W}/{k}_2.wav", "--freq", hp, "--order", "3")
        ff(f"{W}/{k}_2.wav", f"{W}/{k}_3.wav", f"equalizer=f=2800:t=q:w=1.0:g={BELL_DB:g},highshelf=f={SHELF_HZ:g}:g={SHELF_DB:g}")   # v4 check: v3's 2.8 kHz bell back
        c = run("deess", f"{W}/{k}_3.wav", f"{W}/{k}_5.wav", "--low", "5500", "--high", "9000", "--auto-pct", "97", "--max-cut", "6").splitlines()[-1]
        b = f"Bell {BELL_DB:g} dB at 2.8 kHz (as v3), shelf {SHELF_DB:g} dB above {SHELF_HZ:g} Hz; no compressor, no dynamic EQ"
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
    _gi = np.minimum(np.arange(len(g)) * (SR // 1000) + SR // 2000, N - 1); ga = g[act[_gi]]                # v4 check: the gain read only where the voice sings
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
# ---------- 4b. v4 check: one fixed level trim per rapper instead of a ride by bar windows (the ride stepped up to 1.66 dB in the middle of
#               words). The line-to-line differences are mostly the two rappers' levels: each voice is set so the lines it carries sit at the
#               song's median line level. The filled 2:25-2:38 section (bars 83-88) is included.
LINE_BARS = list(range(25, 33, 2)) + list(range(34, 66, 2)) + list(range(66, 74, 2)) + [83, 85, 87] + list(range(90, 98, 2)) + list(range(98, 130, 2))
def line_levels():
    out = {}
    for _b in LINE_BARS:
        i0, i1 = int(bar(_b) * SR), int(bar(_b + 2) * SR); _x = V["L1"][i0:i1] + V["L2"][i0:i1]; _a = np.abs(_x) > 10 ** (-45 / 20)
        if _a.sum() > int(0.5 * SR):
            e1_, e2_ = np.sum(V["L1"][i0:i1] ** 2), np.sum(V["L2"][i0:i1] ** 2)
            out[_b] = (10 * np.log10(np.mean(_x[_a] ** 2) + 1e-12), "L1" if e1_ > e2_ else "L2", max(e1_, e2_) / (e1_ + e2_ + 1e-12))
    return out
_lv = line_levels(); _med = float(np.median([v[0] for v in _lv.values()])); TRIM = {}
for _k in ("L1", "L2"):
    own = [v[0] for v in _lv.values() if v[1] == _k and v[2] > 0.7]
    TRIM[_k] = float(np.clip(_med - np.median(own), -2, 2)) if own else 0.0
    V[_k] = V[_k] * 10 ** (TRIM[_k] / 20)
# v4 check: lines still more than 0.4 dB off after the trims get a phrase gain on the voice that carries them, switched only in that voice's
#           silences (ramps of 30 ms inside gaps of 120 ms or more), never inside a word. On lines both rappers share, both voices get it.
_lvt = line_levels(); _medt = float(np.median([v[0] for v in _lvt.values()])); PR = {"L1": 0, "L2": 0}
for _k in ("L1", "L2"):
    _el = level_blocks(V[_k]); _act = _el > -50
    _d = np.diff(np.r_[0, _act.astype(int), 0]); _st = list(np.where(_d == 1)[0]); _en = list(np.where(_d == -1)[0]); _ph = []
    for _a, _b in zip(_st, _en):
        if _ph and _a - _ph[-1][1] < 12: _ph[-1][1] = _b
        else: _ph.append([_a, _b])
    _gk = np.zeros(NB)
    for _a, _b in _ph:
        _c = (_a + _b) / 2 * 0.01; _bb = int((_c - G0) / BAR) + 1; _bb -= (_bb - LINE_BARS[0]) % 2 if _bb not in _lvt else 0
        _ln = _bb if _bb in _lvt else (_bb - 1 if (_bb - 1) in _lvt else None)
        if _ln is None or (_lvt[_ln][1] != _k and _lvt[_ln][2] > 0.7): continue      # v4 check: shared lines too (both voices move together)
        _dv = _lvt[_ln][0] - _medt
        if abs(_dv) > 0.4: _gk[_a:_b] = float(np.clip(-_dv, -1.2, 1.2)); PR[_k] += 1
    _gs = np.repeat(_gk, blk); _gs = np.r_[_gs, np.zeros(N - len(_gs))]
    _hw = np.hanning(int(0.03 * SR)); _gs = np.convolve(_gs, _hw / _hw.sum(), "same")
    V[_k] = V[_k] * 10 ** (_gs / 20)
_lv2 = line_levels(); _l2 = np.array([v[0] for v in _lv2.values()])
log["line_trim"] = dict(trim_dB={k: round(v, 2) for k, v in TRIM.items()}, phrases_corrected=PR, lines=len(_lv2), spread_before_dB=round(float(np.ptp([v[0] for v in _lv.values()])), 2),
                        spread_after_dB=round(float(np.ptp(_l2)), 2), p5_p95_after_dB=round(float(np.percentile(_l2, 95) - np.percentile(_l2, 5)), 2))
print("line trim", log["line_trim"], flush=True)
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
LPS = [4000, 3400, 2800, 2400]                                          # v4: first repeat a little wider so word starts (t, k, s) keep their edge
WORDS = {}
for k in STEMS:
    w = json.load(open(f"words/{k}.json")); out = [(x["s"], x["e"], x["p"], x["w"]) for x in w]
    for a, b, sh in CUTS[k]: out += [(x["s"] + sh, x["e"] + sh, x["p"], x["w"]) for x in w if a <= x["s"] < b]
    WORDS[k] = sorted(out)
def env_db(x, win_ms=8):
    """RMS in dB, a window of win_ms centred on every millisecond."""
    k = max(2, int(win_ms * SR / 1000)); h = SR // 1000
    c = np.cumsum(np.r_[0.0, np.asarray(x, np.float64) ** 2]); ma = (c[k:] - c[:-k]) / k
    ma = np.r_[np.full(k // 2, ma[0]), ma, np.full(k - k // 2 - 1, ma[-1])]
    return 10 * np.log10(ma[::h] + 1e-12)
MASK = sosfiltfilt(SOSB, beat.mean(1) + lead + bg)                       # what each repeat has to be heard over, in the telephone band
MASKENV = env_db(MASK, 20)
for _who in VG: wr(f"{W}/voice_{_who}.wav", V[_who] * VG[_who])           # each voice as it enters the mix, for the checks
SOS_LO = butter(2, [400, 1500], "band", fs=SR, output="sos"); SOS_HI = butter(2, [2500, 4000], "band", fs=SR, output="sos")
def voiced_gate(w, n):
    """1 where the echo has the body of a voiced sound (400-1500 Hz no more than 3 dB under 2.5-4 kHz), 0 on hiss and s-sounds."""
    lo = env_db(sosfiltfilt(SOS_LO, w), 8)[:n]; hi = env_db(sosfiltfilt(SOS_HI, w), 8)[:n]
    v = (lo > hi - 3).astype(float); v = np.convolve(v, np.ones(7) / 7, "same")
    return np.r_[v, np.zeros(max(0, n - len(v)))][:n]
def lift_curve(w, p):
    """v4: gain in dB, per sample, that brings the quiet parts of an echo (word starts, soft syllables) up toward what it has to be
    heard over: at most LIFT_MAX dB, never above LIFT_CAP dB under the echo's own loud part, never in the noise floor."""
    h = SR // 1000; ew = env_db(w, 8); n = len(ew); j0 = p // h
    m = MASKENV[j0:j0 + n]
    if len(m) < n: m = np.r_[m, np.full(n - len(m), m[-1] if len(m) else -90.0)]
    epk = np.percentile(ew[ew > -90], 90) if np.any(ew > -90) else -90.0
    want = np.minimum(m + T_SNR, epk - LIFT_CAP)
    lift = np.clip(want - ew, 0, LIFT_MAX) * np.clip((ew - (epk - 24.0)) / 6.0, 0, 1) * voiced_gate(w, n)   # v4 check: voiced sound only, never hiss
    k = 25; hw = np.hanning(k + 2)[1:-1]; hw /= hw.sum(); lift = np.convolve(np.pad(lift, k // 2, mode="edge"), hw, "valid")
    return np.interp(np.arange(len(w)), np.arange(n) * h, lift)
throws = np.zeros((N + int(10 * SR), 2)); cue = []; JOBS = []
START_LIFT = float(os.environ.get("START_LIFT", "6")); ECHO_CREST = float(os.environ.get("ECHO_CREST", "9"))
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
    # v4 check: if the copy starts in the tail of the word before (sound within 15 dB of the words) and a gap follows within 350 ms,
    #           start in that gap instead, so the echo begins with its own word.
    skipped = 0.0
    _k0, _k1 = int(a / 0.01), int(min(cut_end - 0.3, a + 0.35) / 0.01)
    _wl = np.percentile(e1[int(a / 0.01):int(cut_end / 0.01) + 1], 80)
    if _k1 > _k0 + 3 and e1[_k0] > _wl - 15:
        _gap = np.where(e1[_k0:_k1 + 1] < _wl - 15)[0]
        if len(_gap):
            _g0 = _k0 + _gap[0]; _g1 = _g0
            while _g1 + 1 <= _k1 and e1[_g1 + 1] < _wl - 15: _g1 += 1
            _kk = _g0 + int(np.argmin(e1[_g0:_g1 + 1])); skipped = _kk * 0.01 + 0.005 - a; a = _kk * 0.01 + 0.005
            dip = float(_wl - e1[_kk])
    said = " ".join(tx for ws, we, p_, tx in WORDS[who] if we > a + 0.05 and ws < cut_end - 0.05)
    # v4: a pre-roll that protects the attack. If the first sound (30 dB under the loud part) comes within the fade-in, start up to 25 ms earlier.
    fi = int((0.006 if dip >= 8 else 0.016) * SR)
    _seg = x1[int(a * SR):int(min(cut_end, a + 0.5) * SR)]; _e = env_db(_seg, 4); _pk = np.percentile(_e, 90)
    _on = int(np.argmax(_e > _pk - 30)) if np.any(_e > _pk - 30) else 0                                  # ms from the copy start to the first sound
    pre = float(np.clip((fi / SR * 1000 + 3 - _on) / 1000.0, 0, 0.025)) if _e[0] < _pk - 20 else 0.0; a -= pre   # v4 check: only from real silence
    L = cut_end - a
    i, j = int(a * SR), int(cut_end * SR)
    fo = int((0.04 if cut_end == t_end else 0.12) * SR)
    # v4: the echo must start AFTER its own source has ended, or it hides under the ringing original and only "cuts in" later.
    #     Half note when the copy is shorter than that; otherwise the dotted half (1.333 s) or the whole bar (1.778 s).
    # v4 check: measured against the mix, v3's half-note first echo of a long held word was clearer than starting after the word (0.7-4.7 dB),
    #           so the first echo is a half note after the copy starts again; only the later repeats are spaced by the copy length (dotted half
    #           or a bar) so a long word's repeats never sit on each other.
    nQ = 2 if L <= 2 * Q + 0.03 else (3 if L <= 3 * Q + 0.03 else 4); D = nQ * Q
    # v5: "Echo still off beat": the first sound of the echoed word lands ON a beat line of the song's grid (the next beat after the words
    #     end), as on the songs he approved; v2-v4 copied the rap's own loose timing a half note later, which put echoes between beats.
    _eo = env_db(x1[int(a * SR):int(min(cut_end, a + 0.6) * SR)], 4); _po = np.percentile(_eo, 90)
    onset = int(np.argmax(_eo > _po - 20)) * (SR // 1000) / SR                # seconds from the copy start to its first sound
    tb = G0 + np.ceil((t_end + 0.03 - G0) / Q) * Q                            # the next beat line after the words have ended
    t0 = tb - onset
    final = abs(t - last_end) < 0.02
    if gap <= 0.3: reps = 2
    else: reps = int(np.clip(np.floor((t + gap - t0) / D) + 2, 3, 4))
    if final: reps = 4
    step = -4.0 if final else STEP_DB
    ctx = x1[i - P:j + P]; dry = ctx[P:-P]
    eb = np.sqrt(np.convolve(dry ** 2, np.ones(441) / 441, "same")); loud = eb > eb.max() * 10 ** (-12 / 20)
    ref = rms(sosfiltfilt(SOSB, ctx)[P:-P][loud])                         # the words' own level in the telephone band
    i1 = max(P, int((t_end - 1.8) * SR)); ln = x1[i1 - P:int(t_end * SR) + P]
    el = np.sqrt(np.convolve(ln[P:-P] ** 2, np.ones(441) / 441, "same")); ref_line = rms(sosfiltfilt(SOSB, ln)[P:-P][el > el.max() * 10 ** (-12 / 20)])   # the whole line's level
    g0 = None; lifts0 = None; ci = len(cue)
    for r in range(reps):
        w = phone(ctx, LPS[min(r, 3)])[P:-P]
        if g0 is None:
            own = rms(sosfiltfilt(SOSB, np.r_[np.zeros(P), w, np.zeros(P)])[P:-P][loud])
            want = max(ref * 10 ** (FIRST_DB / 20), ref_line * 10 ** (-6.0 / 20))     # 2.5 dB under its own words, and at least 6 dB under the line (for a quietly sung last word)
            cap = max(ref, ref_line * 10 ** (-4.0 / 20))                                    # v5: up to level with its words in the louder ear          # never over its words; for a quiet last word, never closer than 4 dB to the line
            tgt_ = min(want, cap / PAN[0]); g0 = tgt_ / own                      # v4 check: the cap holds in the louder ear
        w = w * g0 * 10 ** (step * r / 20)
        w[:fi] *= np.linspace(0, 1, fi); w[-fo:] *= np.linspace(1, 0, fo)
        p = int(round((t0 + r * D) * SR)); lift_db = lift_curve(w, p)
        # v4 check: the start of the echoed word (its first 120 ms) is brought up to the echo's own loud part, never above it
        _ew = env_db(w * 10 ** (lift_db / 20), 8); _ep = np.percentile(_ew[_ew > -90], 90) if np.any(_ew > -90) else -90.0
        _on = int(np.argmax(_ew > _ep - 20)); _acc = np.zeros(len(_ew)); _acc[max(0, _on - 10):_on + 120] = 1.0
        _hw = np.hanning(31)[1:-1]; _acc = np.convolve(_acc, _hw / _hw.sum(), "same")
        _acc = np.clip((_ep - 0.5) - _ew, 0, START_LIFT) * _acc * np.clip((_ew - (_ep - 24.0)) / 6.0, 0, 1) * voiced_gate(w * 10 ** (lift_db / 20), len(_ew))
        lift_db = lift_db + np.interp(np.arange(len(w)), np.arange(len(_acc)) * (SR // 1000), _acc)
        w = w * 10 ** (lift_db / 20)
        if r == 0: lifts0 = lift_db
        pan = PAN if r % 2 == 0 else PAN[::-1]
        JOBS.append(dict(cue=ci, r=r, p=p, w=w, pan=pan))
    _lf = lifts0[lifts0 > 0.1]
    cue.append(dict(singer=who, words=said, lift_median_dB=round(float(np.median(_lf)), 1) if len(_lf) else 0.0, lift_max_dB=round(float(lifts0.max()), 1), under_the_line_dB=round(float(20 * np.log10(ref_line / tgt_)), 1),
                    word_confidence=round(pr, 2), onset_on_beat_s=round(float(tb), 3), start_found_by=how, pre_roll_ms=round(pre * 1000), skipped_previous_word_ms=round(skipped * 1000), line_end_s=round(float(t), 2), words_end_s=round(float(t_end), 2),
                    words_from_s=round(float(a), 2), copy_len_s=round((j - i) / SR, 3), cut_dip_dB=round(dip, 1), first_echo_s=round(float(t0), 3),
                    repeats=reps, spacing_ms=round(D * 1000, 2), delay_note={2: "half", 3: "dotted half", 4: "whole bar"}[nQ], gap_after_s=round(float(min(gap, 99)), 2)))
# v4 check: never lay an echo over an older one. A later repeat of an earlier line that would sit on a newer line's first repeat is dropped,
#           with the repeats after it.
_first = {j["cue"]: (j["p"], j["p"] + len(j["w"])) for j in JOBS if j["r"] == 0}; _drop = set()
for j in JOBS:
    if j["r"] == 0 or j["cue"] in _drop: continue
    a_, b_ = j["p"], j["p"] + len(j["w"])
    if any(c != j["cue"] and min(b_, f1) - max(a_, f0) > int(0.1 * SR) for c, (f0, f1) in _first.items()): _drop.add((j["cue"], j["r"]))
_cut = {}
for c, r in [d for d in _drop if isinstance(d, tuple)]: _cut[c] = min(_cut.get(c, 99), r)
JOBS = [j for j in JOBS if j["r"] < _cut.get(j["cue"], 99)]
for c, r in _cut.items(): cue[c]["repeats"] = r; cue[c]["repeats_cut_to_avoid_stacking"] = True
# v4 check: each echo's own peaks are held to ECHO_CREST dB over its loud part (so the echoes no longer drive the final limiter), then the
#           echo is brought back to the loud-part level it had, so it is not quieter.
_acts = []; _mks = []
for j in JOBS:
    _w = j["w"]; _e = env_db(_w, 10); _ok = _e > -80
    if np.any(_ok):
        _l90 = 10 ** (np.percentile(_e[_ok], 90) / 20); _y, _g = hold_limiter(_w, _l90 * 10 ** (ECHO_CREST / 20), SR, look=0.005, hold=0.015, release_db_per_s=40.0)
        _e2 = env_db(_y, 10); _mk = float(np.clip(_l90 / (10 ** (np.percentile(_e2[_ok[:len(_e2)]], 90) / 20)), 1.0, 10 ** (3 / 20)))
        j["w"] = _y * _mk; _acts.append(float(np.mean(_g < -0.5))); _mks.append(20 * np.log10(_mk))
    throws[j["p"]:j["p"] + len(j["w"]), 0] += j["w"] * j["pan"][0]; throws[j["p"]:j["p"] + len(j["w"]), 1] += j["w"] * j["pan"][1]
log["echo_peaks"] = dict(allowed_over_loud_part_dB=ECHO_CREST, share_of_echo_time_held_pct=round(100 * float(np.mean(_acts)), 1), level_restored_dB_median=round(float(np.median(_mks)), 2), level_restored_dB_max=round(float(np.max(_mks)), 2))
wr(f"{W}/throws_raw.wav", throws[:N]); wr(f"{W}/throws.wav", throws[:N])
log["throws"] = dict(count=len(cue), first_repeat_dB_under_words_in_band=-FIRST_DB, step_dB=STEP_DB, band_Hz=[380, LPS[0]], ducking="none", lift_max_dB=LIFT_MAX, held_under_live_mix_dB=-T_SNR,
                     repeats={str(r): sum(c["repeats"] == r for c in cue) for r in (2, 3, 4)}, delay_note={h: sum(c["delay_note"] == h for c in cue) for h in ("half", "dotted half", "whole bar")},
                     start_found_by={h: sum(c["start_found_by"] == h for c in cue) for h in ("words that fit", "whole long last word", "dip")}, pre_rolled=sum(c["pre_roll_ms"] > 0 for c in cue), started_after_previous_word=sum(c["skipped_previous_word_ms"] > 0 for c in cue), repeats_cut_to_avoid_stacking=sum(bool(c.get("repeats_cut_to_avoid_stacking")) for c in cue),
                     low_confidence_words=sum(c["start_found_by"] != "dip" and c["word_confidence"] < 0.5 for c in cue), shallow_cuts=sum(c["cut_dip_dB"] < 8 for c in cue))
json.dump(cue, open(f"{W}/throw_cues.json", "w"), indent=1)

# ---------- 8. reverbs (as v2)
def verb_lead(): return run("reverb", f"{W}/lead.wav", f"{W}/lead_verb.wav", "--type", "plate", "--decay", "1.333", "--predelay", "27.8", "--hp", "250", "--lp", "4500", "--duck-by", f"{W}/lead.wav", "--duck-depth", "3", "--return-db", "-15").splitlines()[0]
def verb_echo(): return run("reverb", f"{W}/throws.wav", f"{W}/throw_verb.wav", "--type", "plate", "--decay", "0.889", "--predelay", "27.8", "--hp", "400", "--lp", "4500", "--return-db", "-10").splitlines()[0]
def verb_bg(): return run("reverb", f"{W}/bgbus.wav", f"{W}/bg_verb.wav", "--type", "hall", "--decay", "1.778", "--predelay", "27.8", "--hp", "300", "--lp", "4500", "--return-db", "-13").splitlines()[0]
log["reverb"] = [verb_lead(), verb_echo(), verb_bg()]

# ---------- 9. mix, bus, master. v3: slower limiter release, and far less for the limiter to do.
def mix_all():
    m = run("mix", f"{W}/mix.wav", "--track", f"{W}/beat.wav:0", "--track", f"{W}/lead.wav:0", "--track", f"{W}/bgbus.wav:0", "--track", f"{W}/throws.wav:0",
            "--track", f"{W}/lead_verb.wav:0", "--track", f"{W}/throw_verb.wav:0", "--track", f"{W}/bg_verb.wav:0").splitlines()[-1]
    run("ms-bus", f"{W}/mix.wav", f"{W}/mix_ms.wav", "--side-hp", "90", "--mid-shelf", "9500:0")
    x_, _ = sf.read(f"{W}/mix_ms.wav"); wr(f"{W}/mix_trim.wav", x_[:N]); return m, x_[:N]
def master_of(mixt):
    L0 = meter.integrated_loudness(mixt); g = TARGET - L0 + 0.3
    for _ in range(4):                                                   # smooth limiter: 8 ms look-ahead, gain held 30 ms, slow release
        y, gd = hold_limiter(mixt * 10 ** (g / 20), 10 ** (-1.5 / 20), SR, look=0.008, hold=0.030, release_db_per_s=30.0)
        L = meter.integrated_loudness(y)
        if abs(TARGET - L) < 0.03: break
        g += TARGET - L
    return y, gd, g, L
log["mix"], mixt = mix_all(); y, gd, g, L = master_of(mixt)
# v4 check: an echo that lands where the mix is already at full level would make the final limiter pull the whole song down (beat and lead
#           too). Those repeats only are lowered, just enough that no echo adds more than 1 dB of limiting in its first 150 ms.
_H = SR // 1000; _low = {}
for _it in range(int(os.environ.get("HEADROOM_PASSES", "0"))):          # v4 check: off; lowering echoes worked against the owner's echo request
    _tv = sf.read(f"{W}/throw_verb.wav", always_2d=True)[0][:N]
    _, _gr0 = hold_limiter((mixt - throws[:N] - _tv) * 10 ** (g / 20), 10 ** (-1.5 / 20), SR, look=0.008, hold=0.030, release_db_per_s=30.0)
    _n = 0
    for j in JOBS:
        _a, _b = j["p"] // _H, (j["p"] + int(0.15 * SR)) // _H
        _add = float(_gr0[_a:_b].min() - gd[_a:_b].min())
        _key = (round(j["p"] / SR, 2), j["r"])
        if _add > 1.0 and _low.get(_key, 0) < 4.0:
            _cut = min(_add - 0.8, 4.0 - _low.get(_key, 0)); j["w"] = j["w"] * 10 ** (-_cut / 20); _low[_key] = round(_low.get(_key, 0) + _cut, 1); _n += 1
            if j["r"] == 0: cue[j["cue"]]["first_repeat_lowered_for_headroom_dB"] = _low[_key]
    if not _n: break
    throws[:] = 0
    for j in JOBS: throws[j["p"]:j["p"] + len(j["w"]), 0] += j["w"] * j["pan"][0]; throws[j["p"]:j["p"] + len(j["w"]), 1] += j["w"] * j["pan"][1]
    wr(f"{W}/throws_raw.wav", throws[:N]); wr(f"{W}/throws.wav", throws[:N]); log["reverb"][1] = verb_echo()
    json.dump(cue, open(f"{W}/throw_cues.json", "w"), indent=1)
    log["mix"], mixt = mix_all(); y, gd, g, L = master_of(mixt)
_low = [(k[0], k[1], v) for k, v in sorted(_low.items())]
log["echo_headroom"] = dict(repeats_lowered=len(_low), lowered=_low)
wr(f"{W}/master.wav", y)
_t = np.arange(len(gd)) * (SR // 1000) / SR; lim = {}                          # v4 check: the gain steps are 44 samples, not 1 ms
for nm, a_, c_ in (("bars 38-49 full", 38, 50), ("bars 66-81 full", 66, 82), ("bars 114-129 full", 114, 130), ("bars 50-65 soft", 50, 66)):
    s_ = gd[(_t >= bar(a_)) & (_t < bar(c_))]; d5 = np.abs(s_[5:] - s_[:-5])
    lim[nm] = dict(p90_dB=round(float(-np.percentile(s_, 10)), 1), p99_dB=round(float(-np.percentile(s_, 1)), 1), deepest_dB=round(float(-s_.min()), 1),
                   pct_time_over_1dB=round(float(100 * np.mean(s_ < -1)), 0), sudden_drops_over_2dB_per_s=round(float(np.sum(np.diff((d5 > 2).astype(int)) == 1) / (len(s_) / 1000)), 2))
log["master"] = dict(integrated_LUFS=round(float(L), 2), gain_into_limiter_dB=round(float(g), 1), sample_peak_dBFS=round(float(20 * np.log10(np.abs(y).max())), 2), limiter=lim)
json.dump(log, open(f"{W}/build_log.json", "w"), indent=1, default=str)
print(json.dumps({k: log[k] for k in ("beat", "line_trim", "echo_peaks", "echo_headroom", "voice_peaks", "autotune", "rider", "levels", "throws", "mix", "master")}, indent=1, default=str))

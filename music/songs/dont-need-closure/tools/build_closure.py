"""Don't Need Closure: vocal chains, level rides, echo throws, reverse-reverb build-ups, reverbs, mix bus, master.
usage: build_closure.py <version>

Song map (126 BPM, bar = 1.90476 s, bar b starts at BAR0 + (b - 1) * bar; 808 on beats 1-2, clap on beat 3):
  intro bars 1-9 | hook 1 bars 10-17 (drums in on bar 10) | verse 1 bars 18-41 | drop 1 bars 42-49 (hook, no drums) |
  verse 2 bars 50-65 (drums back on bar 50) | drop 2 bars 66-73 (hook, 808 in and out) | verse 3 bars 74-89 (drums
  back on bar 74) | outro bars 90-98 (piano)
The two leads trade lines (they overlap for 3.8 s in the whole song); the two adlib tracks answer them, one left, one right.
Lessons carried over from Baccdoor: leads mono, tone match, gentle compression, leads 0.5 dB under the beat, echoes
on main beats cut from the last clearly sung word, the beat makes room for consonants only.
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import fftconvolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closure_lib as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(os.path.abspath(os.environ.get("CLOSURE_WORK", ".")), "")
TT = os.path.dirname(L.dt.__file__)
T = f"python3 -I {TT}/dsp_tools.py"
ME = f"python3 -I {HERE}/match_eq.py"
FF = "ffmpeg -nostdin -v error -y"
sr = L.sr
TAG = sys.argv[1] if len(sys.argv) > 1 else "v1"
SET = {
    "v1": dict(lead_vs_beat=-0.5, adlib_vs_lead=-6.0,
               plate_db={"hook 1": -14.0, "verse 1": -16.0, "drop 1": -12.0, "verse 2": -16.0, "drop 2": -12.0,
                         "verse 3": -16.0, "outro": -14.0, "intro": -14.0},
               lift_db={"verse 2": 0.3, "drop 2": 0.3, "verse 3": 0.6, "outro": 0.6},
               echo_duck_db=5.0, swell_db=0.0, riser_db=0.0,
               beat_carve=dict(band=(3200, 6500), depth_db=5.0, key_pct=84, attack_ms=5, release_ms=120),
               lufs=-12.0, ceiling=-1.0),
}
# v2 (owner on v1: "The adlibs/background vocals have way too much reverb. I just want them to have reverb but not that
# much and I want them to sit under the lead vocals perfectly"). Measured: the adlib tracks were exported with a long
# reverb on them (a tail about 21 dB under the word for 0.7 s), and v1's firm compression on them lifted that tail
# to 4 dB under the word; v1 then added a hall on top. v2: the baked-in reverb is turned down (dereverb.py), the adlib
# compression is gentle, no reverb is added to the adlibs, and the two adlib tracks together are ridden against the
# leads themselves: 6.5 dB under them wherever both sing (v1: each track to a fixed level, 4.2 dB under together,
# as close as 1.7 dB)
SET["v2"] = dict(SET["v1"], adlib_dry=True, adlib_vs_lead=-9.0, adlib_pair_vs_lead=-6.5, adlib_hall_db=None, adlib_catch_db=14.0,
                 adlib_tail=dict(knee=8.0, max_cut=6.0))
SET = SET[TAG]
log = {"version": TAG, "settings": {k: v for k, v in SET.items()}}


def sh(cmd, show=1):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=D)
    if r.returncode:
        sys.exit(f"FAILED {cmd}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    lines = (r.stdout + r.stderr).strip().splitlines()
    for ln in lines[-show:]:
        print("   ", ln[:230])
    return lines


# ---------------------------------------------------------------- 1. chains (from the gain-staged, high-passed files *_2.wav)
REF = os.path.join(os.path.abspath(os.environ.get("BACC_WORK", os.path.join(D, "..", "bacc"))), "m1_11.wav")
CH = D + "chains_v1.json"
if all(os.path.exists(D + f) for f in ("l1_9.wav", "l2_9.wav", "a1_9.wav", "a2_9.wav")) and os.path.exists(CH):
    chain = json.load(open(CH))
else:
    chain = {}
    for tag, span in (("l1", "18 170"), ("l2", "24 173"), ("a1", "20 175"), ("a2", "20 150")):
        lead = tag[0] == "l"
        x2, _ = L.dt.read(D + f"{tag}_2.wav")
        if lead:   # mono: the middle only
            mm = L.mono(x2)
            L.dt.write(D + f"{tag}_mid.wav", np.stack([mm, mm], 1).astype(np.float32), sr)
        src = f"{tag}_mid.wav" if lead else f"{tag}_2.wav"
        cj = f"match_{tag}.json"
        saved = [p for p in (D + cj, os.path.join(HERE, cj)) if os.path.exists(p)]
        if saved:
            tone = sh(f"{ME} {src} - {tag}_m0.wav --curve-in {saved[0]}")[-1]
        else:
            # the reference is the Baccdoor v4 lead as mixed: the tone the owner called nearly perfect, after his
            # notes on harshness. 90% of the way; leads up to +8 / -12 dB, adlibs up to +4 / -14 dB
            amt = "--amount 0.9 --max-boost 8 --max-cut 12" if lead else "--amount 0.9 --max-boost 4 --max-cut 14"
            tone = sh(f"{ME} {src} {REF} {tag}_m0.wav {amt} --src-t {span} --ref-t 40 100 --curve-out {cj}")[-1]
        if lead:
            # after the match the leads still sat 11-15 dB over the beat from 250 Hz to 1 kHz but only 0-4 dB over it
            # at 2.5-3.2 kHz (muffled): less low-mid, more of the range that carries the words
            post = "equalizer=f=350:t=q:w=0.8:g=-3,equalizer=f=3000:t=q:w=1.2:g=3.5"
        else:
            # the match lifts 125 Hz on the adlibs (keep their low end out), and their top was still 8-12 dB
            # brighter than the leads' above 5 kHz (fizz), so they would have sounded sharper than the leads
            post = "highpass=f=150:poles=2,highshelf=f=6000:g=-5"
        sh(f"{FF} -i {tag}_m0.wav -af \"{post}\" -c:a pcm_f32le {tag}_m1.wav", 0)
        tone += f" | then {post}"
        chain[tag] = {"mono": "mid only" if lead else "stereo kept (panned)", "tone": tone,
                      # rap is all transients: the thresholds sit at high percentiles so each tool only catches peaks
                      "dyneq": sh(f"{T} dyneq {tag}_m1.wav {tag}_m2.wav --freq {3000 if lead else 3500} --q 1.2 --auto-pct {96 if lead else 95}")[-1],
                      "deess": sh(f"{T} deess {tag}_m2.wav {tag}_m3.wav --low 5000 --high 11000 --auto-pct {97.5 if lead else 97}")[-1]}
        # leads: gentle (the lesson from Baccdoor). Adlibs: a fast, firm peak stage, because these takes are very
        # spiky (peaks 22 dB over their loudness) and a spike in a quiet layer makes the master limiter dip
        comp = ("--peak-threshold -6 --smooth-threshold -20 --smooth-ratio 2.0" if lead
                else "--peak-threshold -18 --peak-ratio 10 --peak-attack 0.3")
        chain[tag]["comp"] = sh(f"{T} comp2 {tag}_m3.wav {tag}_9.wav {comp}", 3)[-2]
    json.dump(chain, open(CH, "w"), indent=1)
if SET.get("adlib_dry"):
    CH2 = D + "chains_adlib_dry.json"
    if all(os.path.exists(D + f) for f in ("a1_10.wav", "a2_10.wav")) and os.path.exists(CH2):
        chain.update(json.load(open(CH2)))
    else:
        dry = {}
        for tag in ("a1", "a2"):
            cj = [p for p in (D + f"match_{tag}.json", os.path.join(HERE, f"match_{tag}.json")) if os.path.exists(p)][0]
            post = "highpass=f=150:poles=2,highshelf=f=6000:g=-5"
            dry[tag] = {"mono": "the track's own pan direction kept (one position, no out-of-phase part)",
                        "dereverb": sh(f"python3 -I {HERE}/dereverb.py {tag}_2.wav {tag}_d0.wav --knee 8 --max-cut 10")[-1],
                        "tone": sh(f"{ME} {tag}_d0.wav - {tag}_d1.wav --curve-in {cj}")[-1] + f" | then {post}"}
            sh(f"{FF} -i {tag}_d1.wav -af \"{post}\" -c:a pcm_f32le {tag}_d2.wav", 0)
            dry[tag]["dyneq"] = sh(f"{T} dyneq {tag}_d2.wav {tag}_d3.wav --freq 3500 --q 1.2 --auto-pct 95")[-1]
            dry[tag]["deess"] = sh(f"{T} deess {tag}_d3.wav {tag}_d4.wav --low 5000 --high 11000 --auto-pct 97")[-1]
            # gentle, like the leads: firm compression is what lifted the reverb tails in v1
            dry[tag]["comp"] = sh(f"{T} comp2 {tag}_d4.wav {tag}_10.wav --peak-threshold -6 --smooth-threshold -20 --smooth-ratio 2.0", 3)[-2]
        json.dump(dry, open(CH2, "w"), indent=1)
        chain.update(dry)
log["chains"] = chain

beat, _ = L.dt.read(D + "01_Beat.wav")
n = len(beat)


def load(name):
    x, s = L.dt.read(D + name)
    assert s == sr
    if len(x) < n:
        x = np.concatenate((x, np.zeros((n - len(x), 2))))
    return x[:n].astype(np.float64)


AF = ("a1_10.wav", "a2_10.wav") if SET.get("adlib_dry") else ("a1_9.wav", "a2_9.wav")
l1, l2, a1, a2 = (load(f) for f in ("l1_9.wav", "l2_9.wav") + AF)
mp = json.load(open(D + "map.json"))["lines"]
PH = {"l1": mp["02_Lead1"], "l2": mp["03_Lead2"]}

# ---------------------------------------------------------------- 2. leads: every phrase at the same loudness
# target: 0.5 dB under the beat's loudness in verse 1 (full drums), the level the owner approved on Driftin' Away;
# the same absolute level in the drops, so the voice does not sink when the drums leave
Lbeat = L.loud(beat, L.bar_t(18), L.bar_t(42), False)
lead_target = Lbeat + SET["lead_vs_beat"]
rider = {}


def ride_phrases(x, phrases, target, clamp=4.0):
    """One gain per phrase (K-weighted, gated), clamped to the median +- clamp dB; the gain moves only in the gaps
    between phrases (linear), never inside a phrase."""
    xk = L.kweight(x)
    gains = []
    for a, b in phrases:
        lv = L.loud(None, a, b, True, xk=xk) if b - a >= 0.6 else None
        gains.append(None if lv is None or lv < -80 else target - lv)
    known = [g for g in gains if g is not None]
    med = float(np.median(known))
    idx = [i for i, g in enumerate(gains) if g is not None]
    gains = [float(np.clip(g, med - clamp, med + clamp)) if g is not None else None for g in gains]
    gains = [g if g is not None else gains[min(idx, key=lambda q: abs(q - i))] for i, g in enumerate(gains)]
    tk, gk = [], []
    for (a, b), g in zip(phrases, gains):
        tk += [a - 0.02, b + 0.02]
        gk += [g, g]
    curve = np.interp(np.arange(len(x)) / sr, tk, gk)
    return x * (10 ** (curve / 20))[:, None], gains, med


l1, g1, med1 = ride_phrases(l1, PH["l1"], lead_target)
l2, g2, med2 = ride_phrases(l2, PH["l2"], lead_target)
leads = l1 + l2
Kl = L.kweight(leads)
rider = {"target_lufs": round(lead_target, 2), "beat_verse1_lufs": round(Lbeat, 2),
         "lead 1": {"median_gain_db": round(med1, 2), "range_db": [round(min(g1), 2), round(max(g1), 2)], "phrases": len(g1)},
         "lead 2": {"median_gain_db": round(med2, 2), "range_db": [round(min(g2), 2), round(max(g2), 2)], "phrases": len(g2)}}
log["lead_rider"] = rider
print(f"lead rider: target {lead_target:.1f} LUFS; lead 1 {min(g1):+.1f}..{max(g1):+.1f} dB, lead 2 {min(g2):+.1f}..{max(g2):+.1f} dB")

# ---------------------------------------------------------------- 3. adlibs: each one ridden every 2 bars to sit under the leads
adlib_target = lead_target + SET["adlib_vs_lead"]


def ride_abs(x, target, clamp=5.0):
    """Per 2-bar window, the gain that puts the layer's sung blocks (within 20 dB of its loud level) at the target;
    windows with under 0.8 s of singing take the nearest known gain; clamped to the median +- clamp; 0.3 s ramps."""
    px = L.kblocks(L.kweight(x))
    ax = L.active_blocks(px)
    wins, b = [], 1
    while L.bar_t(b) < n / sr - 1:
        a0, a1_ = L.bar_t(b), L.bar_t(b + 2)
        i0, i1 = int(a0 / 0.1), int(a1_ / 0.1)
        act = ax[i0:i1]
        gw = None
        if act.sum() >= 8:
            gw = target - (-0.691 + 10 * np.log10(px[i0:i1][act].mean()))
        wins.append([a0, a1_, gw])
        b += 2
    known = [w[2] for w in wins if w[2] is not None]
    med = float(np.median(known))
    idx = [i for i, w in enumerate(wins) if w[2] is not None]
    for i, w in enumerate(wins):
        w[2] = float(np.clip(w[2], med - clamp, med + clamp)) if w[2] is not None else None
    for i, w in enumerate(wins):
        if w[2] is None:
            w[2] = wins[min(idx, key=lambda q: abs(q - i))][2]
    curve = np.zeros(n)
    for a0, a1_, gw in wins:
        curve[int(a0 * sr):min(n, int(a1_ * sr))] = gw
    curve[:int(wins[0][0] * sr)] = wins[0][2]
    curve[int(wins[-1][1] * sr):] = wins[-1][2]
    k = int(0.3 * sr)
    curve = np.convolve(np.pad(curve, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
    return x * (10 ** (curve / 20))[:, None], [(round(a0, 3), round(gw, 2)) for a0, a1_, gw in wins], med


def ride_under(x, ref_k, target, clamp=3.0):
    """Per 2-bar window, moved one bar at a time, the gain (dB curve) that puts x target dB under the reference,
    measured only where both sing; each window's gain applies to its middle bar; windows without 0.8 s of overlap
    take the nearest known gain; clamped to the median +- clamp; 0.3 s ramps."""
    px, pr = L.kblocks(L.kweight(x)), L.kblocks(ref_k)
    ax, ar = L.active_blocks(px), L.active_blocks(pr)
    wins, b = [], 1
    while L.bar_t(b) < n / sr - 1:
        d = L.layer_diff(px, pr, ax, ar, L.bar_t(b), L.bar_t(b + 2))
        wins.append([L.bar_t(b) + L.BAR / 2, L.bar_t(b + 1) + L.BAR / 2, None if d is None else target - d])
        b += 1
    known = [w[2] for w in wins if w[2] is not None]
    med = float(np.median(known))
    idx = [i for i, w in enumerate(wins) if w[2] is not None]
    for w in wins:
        w[2] = float(np.clip(w[2], med - clamp, med + clamp)) if w[2] is not None else None
    for i, w in enumerate(wins):
        if w[2] is None:
            w[2] = wins[min(idx, key=lambda q: abs(q - i))][2]
    curve = np.zeros(n)
    for a0, a1_, gw in wins:
        curve[int(a0 * sr):min(n, int(a1_ * sr))] = gw
    curve[:int(wins[0][0] * sr)] = wins[0][2]
    curve[int(wins[-1][1] * sr):] = wins[-1][2]
    k = int(0.3 * sr)
    curve = np.convolve(np.pad(curve, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
    return curve, [(round(a0, 3), round(gw, 2)) for a0, a1_, gw in wins], med


a1, ride_a1, meda1 = ride_abs(a1, adlib_target)
a2, ride_a2, meda2 = ride_abs(a2, adlib_target)
pc = {}
l1, pc["lead 1"] = L.peak_catch(l1, lead_target + 13.0)
l2, pc["lead 2"] = L.peak_catch(l2, lead_target + 13.0)
leads = l1 + l2
Kl = L.kweight(leads)
log["adlib_ride"] = {"target_lufs": round(adlib_target, 2), "under_leads_db": SET["adlib_vs_lead"],
                     "adlib 1": {"median_gain_db": round(meda1, 2), "windows": ride_a1},
                     "adlib 2": {"median_gain_db": round(meda2, 2), "windows": ride_a2}}
catch = SET.get("adlib_catch_db", 12.0)
a1, pc["adlib 1"] = L.peak_catch(a1, (L.loud(a1, 20, 170) if SET.get("adlib_dry") else adlib_target) + catch)
a2, pc["adlib 2"] = L.peak_catch(a2, (L.loud(a2, 20, 150) if SET.get("adlib_dry") else adlib_target) + catch)
if SET.get("adlib_tail"):
    # v2: the compression and the peak catcher bring the reverb tails back up after the loud words, so the tails are
    # turned down once more at the end of the adlib chain
    a1, ts1 = L.tails_down(a1, **SET["adlib_tail"])
    a2, ts2 = L.tails_down(a2, **SET["adlib_tail"])
    log["adlib_tails_down"] = {"adlib 1": ts1, "adlib 2": ts2}
if SET.get("adlib_pair_vs_lead") is not None:
    # v2: last, the two adlib tracks together against the leads themselves, where both sing (one gain for both)
    pair_curve, pair_w, pair_med = ride_under(a1 + a2, Kl, SET["adlib_pair_vs_lead"], clamp=5.0)
    a1 = a1 * (10 ** (pair_curve / 20))[:, None]
    a2 = a2 * (10 ** (pair_curve / 20))[:, None]
    log["adlib_ride"]["pair"] = {"under_leads_db": SET["adlib_pair_vs_lead"], "median_gain_db": round(pair_med, 2), "windows": pair_w}
    log["adlib_ride"]["under_leads_db"] = SET["adlib_pair_vs_lead"]
    print(f"adlib pair ride: {SET['adlib_pair_vs_lead']} dB under the leads where both sing; median gain {pair_med:+.1f} dB")
adlibs = a1 + a2
log["peak_catch"] = pc
print(f"adlibs: target {adlib_target:.1f} LUFS each ({SET['adlib_vs_lead']} dB under the leads); median gains {meda1:+.1f} / {meda2:+.1f} dB")

# ---------------------------------------------------------------- 4. echo throws on the beat
envs = {"l1": L.envelope_db(load("02_Lead1.wav")), "l2": L.envelope_db(load("03_Lead2.wav"))}
allp = sorted([(a, b, k) for k in PH for a, b in PH[k]])
last_end = max(b for a, b, k in allp)
events = {"l1": [], "l2": []}
for i, (a, b, key) in enumerate(allp):
    if b - a < 1.0:
        continue
    sec = L.section_of(b - 0.2)
    nxt = min([x[0] for x in allp if x[0] > b - 0.3 and x is not allp[i]] or [1e9])
    gap = nxt - b
    w0, w1 = L.last_loud_word(envs[key], a, b)
    if abs(b - last_end) < 0.01:
        events[key].append((w0, w1, 8, -4.0, -2.5, 2))       # the last line: 8 half notes into the piano outro
    elif gap >= 1.0 or sec.startswith("drop") or sec == "hook 1":
        events[key].append((w0, w1, 4, -4.0, -4.0, 1))       # open space (a real gap, or the hooks): 4 echoes
    else:
        events[key].append((w0, w1, 3, -6.0, -4.0, 1))       # verse line endings: 3 echoes under the next line
echo = np.zeros((n, 2))
elog = []
for key, src in (("l1", l1), ("l2", l2)):
    e, lg = L.render_echoes(src, events[key], n, "lead 1" if key == "l1" else "lead 2")
    echo += e
    elog += lg
gd, _, pct = L.dt.duck_gain(leads, sr, n, SET["echo_duck_db"], None, 5, 120)
echo *= gd[:, None]
log["echoes"] = elog
log["echo_ducking"] = {"depth_db": SET["echo_duck_db"], "attack_ms": 5, "release_ms": 120, "fully_ducked_pct": round(pct, 1)}

# ---------------------------------------------------------------- 5. reverse-reverb build-ups
# (a) vocal swells: the word that lands on the drop, reversed through a 3.2 s hall and reversed back; the swell starts
#     on a downbeat and ends exactly on the word's first sound. (b) beat risers: the drop's own first hit (above 250 Hz,
#     a whoosh, not a second 808) treated the same way, one bar long, ending exactly on the drop's transient.
IR_SW = L.dt.make_ir(sr, "hall", 3.2, 0.0, 1.0, seed=7)     # long enough for a 2-bar swell (3.81 s)


def first_sound(x, t_from, t_to, rel_db=-30.0):
    seg = np.abs(L.mono(x[int(t_from * sr):int(t_to * sr)]))
    k = int(0.002 * sr)
    env = np.convolve(seg, np.ones(k) / k, mode="same")
    return t_from + int(np.where(env > env.max() * 10 ** (rel_db / 20))[0][0]) / sr


def reverse_swell(seg, length_s, peak, shape=2.0):
    wet = np.stack([fftconvolve(seg[::-1], IR_SW[:, c]) for c in range(2)], 1)[::-1]
    Ls = int(round(length_s * sr))
    assert Ls <= len(IR_SW) - 1, "swell longer than the reverb tail"
    sw_ = wet[:len(IR_SW) - 1][-Ls:].copy() * (np.linspace(0, 1, Ls) ** shape)[:, None]
    sw_ = L.fades(sw_, 0.0, 0.004)
    return sw_ * peak / (np.abs(sw_).max() + 1e-12)


swell = np.zeros((n, 2))
slog = []
RAW = {"l1": load("02_Lead1.wav"), "l2": load("03_Lead2.wav")}
SRC = {"l1": l1, "l2": l2}
for label, key, t_from, t_to, start_bar in (("the first word (drums enter, bar 10)", "l1", 17.80, 18.40, 8),
                                            ("into the drums coming back (bar 50)", "l2", 94.10, 94.70, 48),
                                            ("into hook 3 (bar 66)", "l1", 124.55, 125.10, 65),
                                            ("into the drums coming back (bar 74)", "l2", 139.75, 140.45, 72)):
    if label.endswith("(bar 74)"):
        ats = L.attacks_in(envs[key], t_from, t_to)
        att = min(ats, key=lambda q: abs(q - L.bar_t(74))) if ats else None
        if att is None:
            continue
    else:
        att = first_sound(RAW[key], t_from, t_to)
    st = L.bar_t(start_bar)
    i = int(att * sr)
    w = L.fades(L.mono(SRC[key][i:i + int(0.45 * sr)]), 0.002, 0.03)
    extra = 3.0 if label.endswith("(bar 74)") else 0.0     # this one rises under the 808 (the others over a sparse beat)
    y = reverse_swell(w, att - st, np.abs(w).max() * 10 ** ((SET["swell_db"] + extra) / 20))
    s = int(round(st * sr))
    swell[s:s + len(y)] += y
    slog.append({"what": label, "voice": "lead 1" if key == "l1" else "lead 2", "word_first_sound_s": round(att, 4),
                 "word_at": L.bb(att), "swell_start_s": round(st, 4), "swell_start_at": L.bb(st), "length_s": round(att - st, 3),
                 "ends_on_word": True, "peak_vs_word_peak_db": SET["swell_db"] + extra})
log["reverse_swells"] = slog

bm = L.mono(beat)
hp250 = L.butter(4, 250, "highpass", fs=sr, output="sos")
hib = L.sosfiltfilt(hp250, bm)
riser = np.zeros((n, 2))
rlog = []
for b in (10, 50, 74):
    t_drop = L.bar_t(b)
    # the drop's first hit: the kick's click above 250 Hz (1 ms envelope), first sample at 30% of its peak within 15 ms of the grid downbeat. (The low
    # end is no use here: the intro's bass already sits within 20 dB of the 808, so a low-band threshold fires early.)
    w0, w1 = int((t_drop - 0.015) * sr), int((t_drop + 0.015) * sr)
    kk = int(0.001 * sr)
    e = np.convolve(np.abs(hib[w0 - kk:w1 + kk]), np.ones(kk) / kk, mode="same")[kk:-kk]
    on = w0 + int(np.argmax(e > 0.3 * e.max()))
    hit = bm[on:on + int(0.35 * sr)]
    seg = L.fades(L.sosfiltfilt(hp250, hit), 0.001, 0.05)
    extra = 3.0 if b == 74 else 0.0
    y = reverse_swell(seg, L.BAR, np.abs(hit).max() * 10 ** ((SET["riser_db"] + extra) / 20))
    riser[on - len(y):on] += y
    rlog.append({"drop_bar": b, "riser_s": [round((on - len(y)) / sr, 4), round(on / sr, 4)], "riser_at": L.bb((on - len(y)) / sr),
                 "drop_transient_s": round(on / sr, 4), "grid_downbeat_s": round(t_drop, 4),
                 "transient_vs_grid_ms": round((on / sr - t_drop) * 1000, 1), "peak_vs_drop_hit_db": SET["riser_db"] + extra})
log["drop_buildups"] = rlog

# ---------------------------------------------------------------- 6. the beat makes room for the consonants
bc_ = SET["beat_carve"]
sos_cv = L.butter(2, list(bc_["band"]), "bandpass", fs=sr, output="sos")
band_ = L.sosfiltfilt(sos_cv, beat, axis=0)
key_cv = L.sosfiltfilt(sos_cv, L.mono(leads))
lev_cv, _ = L.dt.block_level(key_cv, sr, 10)
thr_cv = float(np.percentile(lev_cv[lev_cv > max(-60, lev_cv.max() - 35)], bc_["key_pct"]))
gcv, _, pct_cv = L.dt.duck_gain(key_cv, sr, n, bc_["depth_db"], thr_cv, bc_["attack_ms"], bc_["release_ms"])
beat_c = beat - band_ * (1 - gcv)[:, None]
log["beat_carve"] = dict(bc_, threshold_dbfs=round(thr_cv, 1), active_pct=round(pct_cv, 1))

# ---------------------------------------------------------------- 7. reverbs
plate_curve = np.zeros(n)
for nm, a, b in L.SECTIONS:
    plate_curve[int(a * sr):int(min(b, n / sr) * sr)] = SET["plate_db"].get(nm, -15.0)
k = int(L.Q * sr)
plate_curve = np.convolve(np.pad(plate_curve, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
pre = 29.76   # 1/64 at 126 BPM
rv_lead = L.reverb(leads, "plate", 1.4286, pre, 0.0, leads, 4.0, lp=8000) * (10 ** (plate_curve / 20))[:, None]   # dotted half
hall_db = SET.get("adlib_hall_db", -14.0)
rv_ad = (L.reverb(adlibs, "hall", 1.9048, pre, hall_db, adlibs, 2.0, lp=8000, seed=3)                             # 1 bar
         if hall_db is not None else np.zeros((n, 2)))
rv_echo = L.reverb(echo, "plate", 1.4286, pre, -9.0, lp=8000, seed=5)
log["reverb"] = {"leads": "plate 1.43 s (dotted half), pre-delay 29.76 ms (1/64), ducked 4 dB, send low-passed at 8 kHz, return by section " + json.dumps(SET["plate_db"]),
                 "adlibs": ("hall 1.90 s (1 bar), pre-delay 29.76 ms, ducked 2 dB, return -14 dB (the adlib tracks carry their own ambience)"
                            if hall_db is not None else "none added: the adlib tracks carry their own reverb, turned down by dereverb.py"),
                 "echoes": "plate 1.43 s, -9 dB"}

# ---------------------------------------------------------------- 8. mix, bus, master
mix = beat_c + leads + adlibs + echo + swell + riser + rv_lead + rv_ad + rv_echo
lift = np.zeros(n)
for nm, a, b in L.SECTIONS:
    lift[int(a * sr):min(n, int(b * sr))] = SET["lift_db"].get(nm, 0.0)
lift = np.convolve(np.pad(lift, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
mix *= (10 ** (lift / 20))[:, None]
log["lift_db"] = SET["lift_db"]
m = np.abs(mix).max(1)
last = np.where(m > 10 ** (-80 / 20))[0][-1]
mix = mix[:min(n, last + int(0.3 * sr))]
L.dt.write(D + f"mix_{TAG}.wav", mix, sr)
for nm, x in (("leads", leads), ("lead1", l1), ("lead2", l2), ("adlibs", adlibs), ("adlib1", a1), ("adlib2", a2),
              ("echo", echo), ("swell", swell), ("riser", riser), ("beat", beat_c)):
    L.dt.write(D + f"stem_{TAG}_{nm}.wav", x, sr)
json.dump(log, open(D + f"build_{TAG}.json", "w"), indent=1)
print(f"echo throws: {len(elog)}; swells: {len(slog)}; risers: {len(rlog)}; beat carve active {pct_cv:.0f}%")
print("peak catch", json.dumps(pc))
sh(f"{T} ms-bus mix_{TAG}.wav mix_{TAG}_ms.wav --side-hp 100 --mid-shelf 9500:0", 1)
sh(f"python3 -I {TT}/render_master.py mix_{TAG}_ms.wav master_{TAG}.wav --target-lufs {SET['lufs']} --ceiling {SET['ceiling']}", 3)
sh(f"python3 -I {TT}/export_master.py {D}master_{TAG}.wav --name Dont_Need_Closure_master_{TAG} --rate 44100", 3)

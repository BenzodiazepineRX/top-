"""Don't Need Closure checks, measured on the rendered files.   usage: verify_closure.py <version>

1. echoes: every repeat found by correlating the word with the echo track; distance to the grid beat
2. reverse swells: each ends on its word's first sound and starts on a downbeat; risers end on the drop's transient
3. lead level: every phrase's loudness (K-weighted) against the target; spread across the song
4. adlibs: every 2 bars where both sing, the adlibs (both tracks together) against the leads; never louder
5. gaps: stretches of 0.6 s+ with no vocal, echo or swell, from the first vocal to the last
6. phones: mono fold-down of the master (level change, the vocal band, the adlibs alone), stereo correlation
Exits 1 on any FAIL.
"""
import json
import os
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closure_lib as L  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("CLOSURE_WORK", ".")), "")
V = sys.argv[1] if len(sys.argv) > 1 else "v1"
sr = L.sr
b = json.load(open(D + f"build_{V}.json"))
mp = json.load(open(D + "map.json"))["lines"]
fails = []


def rd(name):
    return L.dt.read(D + name)[0]


# ---- 1. echoes
bp = butter(4, [500, 4500], "bandpass", fs=sr, output="sos")
E = sosfiltfilt(bp, L.mono(rd(f"stem_{V}_echo.wav")))
duck = b["echo_ducking"]["depth_db"]
srcs = {"lead 1": rd(f"stem_{V}_lead1.wav"), "lead 2": rd(f"stem_{V}_lead2.wav")}
offs = []
for r in b["echoes"]:
    a, e = r["word"]
    w = sosfiltfilt(bp, L.mono(srcs[r["src"]][int((a - 0.005) * sr):int((e + 0.02) * sr)]))
    for tk in r["echo_times"]:
        s0 = int((tk - 0.045) * sr)
        seg = E[s0:s0 + len(w) + int(0.08 * sr)]
        if len(seg) < len(w) + 10:
            continue
        c = fftconvolve(seg, w[::-1], mode="valid")
        k = int(np.argmax(c))
        tf = (s0 + k) / sr + 0.005
        offs.append((tf - L.beat_t(round((tf - L.G0) / L.Q))) * 1000)
offs = np.abs(offs)
print(f"1. echoes: {len(b['echoes'])} throws, {len(offs)} repeats; distance from the grid beat median {np.median(offs):.2f} ms, max {offs.max():.2f} ms")
if offs.max() > 2.0:
    fails.append("echo off the grid")

# ---- 2. reverse swells and risers
sw = np.abs(rd(f"stem_{V}_swell.wav")).max(1)
print("2. reverse swells (end = the last sample of the swell; word = the first sound of the word it leads into):")
for r in b["reverse_swells"]:
    i0, i1 = int((r["swell_start_s"] - 0.05) * sr), int((r["word_first_sound_s"] + 0.3) * sr)
    nz = np.where(sw[i0:i1] > sw[i0:i1].max() * 1e-4)[0]
    t_start, t_end = (i0 + nz[0]) / sr, (i0 + nz[-1]) / sr
    pk = (i0 + int(np.argmax(sw[i0:i1]))) / sr
    d_end = (t_end - r["word_first_sound_s"]) * 1000
    on_down = abs(((r["swell_start_s"] - L.BAR0) / L.BAR) - round((r["swell_start_s"] - L.BAR0) / L.BAR)) * L.BAR * 1000
    print(f"   {r['what']}: starts {r['swell_start_at']} ({on_down:.2f} ms from a downbeat), {r['length_s']:.2f} s long, "
          f"ends {d_end:+.2f} ms from the word at {r['word_first_sound_s']:.3f} s, loudest {(r['word_first_sound_s'] - pk) * 1000:.0f} ms before it")
    if abs(d_end) > 2.0 or on_down > 1.0:
        fails.append("reverse swell timing")
ri = np.abs(rd(f"stem_{V}_riser.wav")).max(1)
for r in b["drop_buildups"]:
    i0, i1 = int((r["riser_s"][0] - 0.05) * sr), int((r["riser_s"][1] + 0.3) * sr)
    nz = np.where(ri[i0:i1] > ri[i0:i1].max() * 1e-4)[0]
    t_end = (i0 + nz[-1]) / sr
    d = (t_end - r["drop_transient_s"]) * 1000
    print(f"   riser into bar {r['drop_bar']}: {r['riser_s'][1] - r['riser_s'][0]:.2f} s long, ends {d:+.2f} ms from the drop's first hit "
          f"(the hit sits {r['transient_vs_grid_ms']:+.1f} ms from the grid downbeat)")
    if abs(d) > 2.0 or abs(r["transient_vs_grid_ms"]) > 15:
        fails.append("riser timing")

# ---- 3. lead level per phrase
tgt = b["lead_rider"]["target_lufs"]
rows = []
for key, stem in (("lead1", "02_Lead1"), ("lead2", "03_Lead2")):
    xk = L.kweight(rd(f"stem_{V}_{key}.wav"))
    for a, e in mp[stem]:
        if e - a >= 1.0:
            rows.append((a, L.loud(None, a, e, True, xk=xk) - tgt, key))
dv = np.array([r[1] for r in rows])
worst = sorted(rows, key=lambda r: -abs(r[1]))[:3]
print(f"3. lead level: {len(rows)} phrases against the target ({tgt:.1f} LUFS): median {np.median(dv):+.2f} dB, "
      f"90% within {np.percentile(np.abs(dv), 90):.2f} dB, largest " + ", ".join(f"{int(r[0] // 60)}:{r[0] % 60:04.1f} {r[1]:+.1f}" for r in worst))
if np.abs(dv).max() > 2.0:
    fails.append("lead phrase off target by more than 2 dB")
bt = rd(f"stem_{V}_beat.wav")
ld = rd(f"stem_{V}_leads.wav")
for nm, a, e in L.SECTIONS:
    if nm.startswith("verse"):
        print(f"   {nm}: leads {L.loud(ld, a, e) - L.loud(bt, a, e, False):+.2f} dB against the beat")

# ---- 4. adlibs under the leads
pm, pa = L.kblocks(L.kweight(ld)), L.kblocks(L.kweight(rd(f"stem_{V}_adlibs.wav")))
am, aa = L.active_blocks(pm), L.active_blocks(pa)
tg = b["adlib_ride"]["under_leads_db"]
dd = []
bar = 10
while L.bar_t(bar + 2) < 176:
    d = L.layer_diff(pa, pm, aa, am, L.bar_t(bar), L.bar_t(bar + 2))
    if d is not None:
        dd.append((L.bar_t(bar), d))
    bar += 2
vals = np.array([d for _, d in dd])
pair = "pair" in b["adlib_ride"]          # v2+: the pair is ridden against the leads, so the window is tight
hi, lo = (tg + 2.0, tg - 3.0) if pair else (-1.5, tg - 4.0)
over = [(t, d) for t, d in dd if d > hi]
quiet = [(t, d) for t, d in dd if d < lo]
print(f"4. adlibs (both tracks together) against the leads, where both sing: {len(dd)} windows, median {np.median(vals):+.1f} dB "
      f"(range {vals.min():+.1f} to {vals.max():+.1f}; target {tg:+.1f}); closer to the leads than {hi:+.1f} dB: {len(over)}; further under than {lo:+.1f} dB: {len(quiet)}"
      + ("  " + ", ".join(f"{int(t // 60)}:{t % 60:04.1f} {d:+.1f}" for t, d in (over + quiet)[:8]) if over or quiet else ""))
if over:
    fails.append("adlibs too close to the leads")
if quiet:
    fails.append("adlibs too quiet")
for key in ("adlib1", "adlib2"):
    xk = L.kweight(rd(f"stem_{V}_{key}.wav"))
    px = L.kblocks(xk)
    ax = L.active_blocks(px)
    lv = []
    bar = 10
    while L.bar_t(bar + 2) < 176:
        i0, i1 = int(L.bar_t(bar) / 0.1), int(L.bar_t(bar + 2) / 0.1)
        if ax[i0:i1].sum() >= 8:
            lv.append(-0.691 + 10 * np.log10(px[i0:i1][ax[i0:i1]].mean()))
        bar += 2
    lv = np.array(lv)
    print(f"   {key}: {len(lv)} windows, level against its target median {np.median(lv) - b['adlib_ride']['target_lufs']:+.2f} dB, "
          f"range {lv.min() - b['adlib_ride']['target_lufs']:+.1f} to {lv.max() - b['adlib_ride']['target_lufs']:+.1f}")


# ---- 4b. reverb tails on the adlibs: at the word endings found in the raw tracks, the level 150-500 ms later
import tail_check as TC  # noqa: E402

print("4b. adlib reverb tails (level 150-500 ms after a word ends, against the word; lower = drier):")
for key, raw in (("adlib1", "04_Adlib1.wav"), ("adlib2", "05_Adlib2.wav")):
    ends = TC.endings(D + raw)
    t_raw, t_mix = TC.tail(D + raw, ends), TC.tail(D + f"stem_{V}_{key}.wav", ends)
    print(f"   {key}: as exported {t_raw:+.1f} dB, in the mix {t_mix:+.1f} dB ({t_mix - t_raw:+.1f} dB; {len(ends)} word endings)")
    if t_mix > t_raw + 1.0:
        fails.append(f"{key}: more reverb tail than the raw track")


# ---- 5. gaps
def act(x, rel=-35):
    m = L.mono(x)
    h = 882
    nn = len(m) // h
    r = 20 * np.log10(np.sqrt((m[:nn * h].reshape(nn, h) ** 2).mean(1)) + 1e-9)
    out = np.zeros(int(200 / 0.02), bool)
    lv = np.percentile(r[r > -80], 95) if (r > -80).any() else -200
    a = r > lv + rel
    out[:min(len(a), len(out))] = a[:len(out)]
    return out


V_ = np.any([act(rd(f)) for f in (f"stem_{V}_leads.wav", f"stem_{V}_adlibs.wav")], axis=0)
EE = act(rd(f"stem_{V}_echo.wav"), -45) | act(rd(f"stem_{V}_swell.wav"), -45)
first, lastv = np.where(V_)[0][0], np.where(V_)[0][-1]
gaps, s = [], None
for i in range(first, lastv):
    if not V_[i] and s is None:
        s = i
    if V_[i] and s is not None:
        if (i - s) * 0.02 >= 0.6:
            gaps.append((s * 0.02, i * 0.02, EE[s:i].mean()))
        s = None
empty = [g for g in gaps if g[2] < 0.5]
print(f"5. vocal gaps of 0.6 s+ between the first and last vocal: {len(gaps)}"
      + ("  " + ", ".join(f"{int(a // 60)}:{a % 60:04.1f} ({c - a:.1f} s, echo or swell {e * 100:.0f}%)" for a, c, e in gaps) if gaps else "")
      + f"; left empty (under half filled): {len(empty)}")
print(f"   the vocals end at {int(lastv * 0.02 // 60)}:{lastv * 0.02 % 60:04.1f}")
if empty:
    fails.append("an empty gap")

# ---- 6. phones
mst = rd(f"Dont_Need_Closure_master_{V}_24bit.wav")
mono_ = mst.mean(axis=1, keepdims=True).repeat(2, 1)
lst, lmo = L.loud(mst, 0, len(mst) / sr, False), L.loud(mono_, 0, len(mst) / sr, False)
vb = butter(4, [1000, 4000], "bandpass", fs=sr, output="sos")
st_v = 10 * np.log10(np.mean(sosfiltfilt(vb, mst, axis=0) ** 2))
mo_v = 10 * np.log10(np.mean(sosfiltfilt(vb, mono_, axis=0) ** 2))
corr = float(np.corrcoef(mst[:, 0], mst[:, 1])[0, 1])
ad = rd(f"stem_{V}_adlibs.wav")
adm = ad.mean(axis=1, keepdims=True).repeat(2, 1)
dad = L.loud(adm, 20, 170) - L.loud(ad, 20, 170)
print(f"6. phones (mono): loudness {lst:.1f} -> {lmo:.1f} LUFS ({lmo - lst:+.1f} dB), vocal band 1-4 kHz {mo_v - st_v:+.1f} dB, "
      f"L/R correlation {corr:.2f}; the adlibs alone lose {-dad:.1f} dB in mono")
if lmo - lst < -1.5 or dad < -3.0:
    fails.append("mono loss")

print("RESULT:", "FAIL " + "; ".join(fails) if fails else "all checks pass")
sys.exit(1 if fails else 0)

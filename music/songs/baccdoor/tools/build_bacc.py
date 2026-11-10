"""Baccdoor: vocal chains (after prep_vocals.py), echo throws, reverbs that grow with the song, the layer order,
mix bus, master for streaming, export.   usage: build_bacc.py <version>

Song map (125 BPM, bar = 1.92 s, bar b starts at BAR0 + (b - 1) * 1.92):
  intro bars 1-15 | A bars 16-47 | drop 1 bars 48-55 (beat drops to piano) | B bars 56-71 | drop 2 bars 72-79 |
  C bars 80-95 | outro bars 96-104 (vocals end at 2:51.4, bar 89)
Vocal order (the owner's, from Driftin' Away): main leads > background vocals > background of background.
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc_lib as L  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("BACC_WORK", ".")), "")
TT = os.path.dirname(L.dt.__file__)
T = f"python3 -I {TT}/dsp_tools.py"
FF = "ffmpeg -nostdin -v error -y"
TAG = sys.argv[1] if len(sys.argv) > 1 else "v1"
sr = L.sr
SET = {
    "v1": dict(mains_vs_beat=0.3, lift_db={"A": 0.0, "drop 1": 0.0, "B": 0.3, "drop 2": 0.3, "C": 0.6}, bg_vs_mains={"A": -6.0, "drop 1": -5.0, "B": -5.0, "drop 2": -5.0, "C": -4.5},
               bgbg_vs_bg=-4.0, bgbg_vs_mains_alone=-9.0, side_db=-6.0,
               plate_db={"A": -16.0, "drop 1": -12.0, "B": -15.0, "drop 2": -12.0, "C": -15.0, "intro": -16.0, "outro": -15.0},
               lufs=-12.0, ceiling=-1.0, beat_file="01_Beat.wav", bus_shelf="9500:1.5"),
    # v2 (owner on v1: "very scratchy ... too ampy ... very harsh vocals"): the de-harsh chain (no presence boost,
    # no saturation; -7 dB shelf above 5.5 kHz and a 12 kHz low-pass on the leads, fizz de-essed 5-11 kHz), no high
    # shelf on the mix bus, reverb sends low-passed at 8 kHz
    "v2": dict(mains_vs_beat=0.3, lift_db={"A": 0.0, "drop 1": 0.0, "B": 0.3, "drop 2": 0.3, "C": 0.6},
               bg_vs_mains={"A": -6.0, "drop 1": -5.0, "B": -5.0, "drop 2": -5.0, "C": -4.5},
               bgbg_vs_bg=-4.0, bgbg_vs_mains_alone=-9.0, side_db=-6.0,
               plate_db={"A": -16.0, "drop 1": -12.0, "B": -15.0, "drop 2": -12.0, "C": -15.0, "intro": -16.0, "outro": -15.0},
               lufs=-12.0, ceiling=-1.0, beat_file="01_Beat.wav", chain="deharsh", bus_shelf="9500:0", verb_lp=8000),
}[TAG]
log = {"version": TAG}


def sh(cmd, show=1):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=D)
    if r.returncode:
        sys.exit(f"FAILED {cmd}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    lines = (r.stdout + r.stderr).strip().splitlines()
    for ln in lines[-show:]:
        print("   ", ln[:230])
    return lines


# ---------------------------------------------------------------- 1. chains (from the retuned, gain-staged, high-passed files)
if all(os.path.exists(D + f) for f in ("m1_8.wav", "m2_8.wav", "bg_7.wav", "bb_7.wav", "chains.json")):
    chain = json.load(open(D + "chains.json"))
else:
    chain = {}
    for tag in ("m1", "m2"):
        chain[tag] = {
            "dyneq": sh(f"{T} dyneq {tag}_2.wav {tag}_4.wav --freq 3000 --q 1.5 --auto-pct 97")[-1],
            "presence": "+1.5 dB at 3.5 kHz, Q 1"}
        sh(f"{FF} -i {tag}_4.wav -af \"equalizer=f=3500:t=q:w=1.0:g=1.5\" -c:a pcm_f32le {tag}_5.wav", 0)
        chain[tag]["deess"] = sh(f"{T} deess {tag}_5.wav {tag}_6.wav --low 5500 --high 8500 --auto-pct 97")[-1]
        chain[tag]["comp"] = sh(f"{T} comp2 {tag}_6.wav {tag}_7.wav", 3)[-2]
        chain[tag]["sat"] = sh(f"{T} saturate {tag}_7.wav {tag}_8.wav --drive 6 --even 0.15 --mix 0.3")[-1]
    for tag in ("bg", "bb"):
        chain[tag] = {"dyneq": sh(f"{T} dyneq {tag}_2.wav {tag}_4.wav --freq 3000 --q 1.5 --auto-pct 97")[-1],
                      "eq": "-1.5 dB at 3 kHz (Q 1), -1.5 dB shelf above 7 kHz"}
        sh(f"{FF} -i {tag}_4.wav -af \"equalizer=f=3000:t=q:w=1.0:g=-1.5,highshelf=f=7000:g=-1.5\" -c:a pcm_f32le {tag}_5.wav", 0)
        chain[tag]["deess"] = sh(f"{T} deess {tag}_5.wav {tag}_6.wav --low 5000 --high 8000 --auto-pct 97")[-1]
        chain[tag]["comp"] = sh(f"{T} comp2 {tag}_6.wav {tag}_7.wav", 3)[-2]
    json.dump(chain, open(D + "chains.json", "w"), indent=1)
if SET.get("chain") == "deharsh":
    if all(os.path.exists(D + f) for f in ("m1_9.wav", "m2_9.wav", "bg_9.wav", "bb_9.wav", "chains_v2.json")):
        chain = json.load(open(D + "chains_v2.json"))
    else:
        chain = {}
        for tag in ("m1", "m2"):
            sh(f"{FF} -i {tag}_2.wav -af \"highshelf=f=5500:g=-7,lowpass=f=12000:poles=2\" -c:a pcm_f32le {tag}_h1.wav", 0)
            chain[tag] = {"tone": "-7 dB shelf above 5.5 kHz, 12 kHz low-pass (12 dB/oct); no presence boost, no saturation",
                          "dyneq": sh(f"{T} dyneq {tag}_h1.wav {tag}_h2.wav --freq 3500 --q 1.2 --auto-pct 92")[-1],
                          "deess": sh(f"{T} deess {tag}_h2.wav {tag}_h3.wav --low 5000 --high 11000 --auto-pct 93")[-1]}
            chain[tag]["comp"] = sh(f"{T} comp2 {tag}_h3.wav {tag}_9.wav", 3)[-2]
        for tag in ("bg", "bb"):
            sh(f"{FF} -i {tag}_2.wav -af \"equalizer=f=3000:t=q:w=1.0:g=-1.5,highshelf=f=5500:g=-6,lowpass=f=11000:poles=2\" -c:a pcm_f32le {tag}_h1.wav", 0)
            chain[tag] = {"tone": "-1.5 dB at 3 kHz, -6 dB shelf above 5.5 kHz, 11 kHz low-pass",
                          "dyneq": sh(f"{T} dyneq {tag}_h1.wav {tag}_h2.wav --freq 3500 --q 1.2 --auto-pct 92")[-1],
                          "deess": sh(f"{T} deess {tag}_h2.wav {tag}_h3.wav --low 5000 --high 11000 --auto-pct 93")[-1]}
            chain[tag]["comp"] = sh(f"{T} comp2 {tag}_h3.wav {tag}_9.wav", 3)[-2]
        json.dump(chain, open(D + "chains_v2.json", "w"), indent=1)
log["chains"] = chain

beat0, _ = L.dt.read(D + "01_Beat.wav")
n = len(beat0) + 6 * sr
t = np.arange(n) / sr


def load(name):
    x, s = L.dt.read(D + name)
    assert s == sr
    if x.ndim == 1 or x.shape[1] == 1:
        x = np.repeat(x.reshape(-1, 1), 2, axis=1)
    out = np.zeros((n, 2))
    out[:min(n, len(x))] = x[:n]
    return out


beat = load(SET.get("beat_file", "01_Beat.wav"))   # v1: the beat as delivered (spike and 808 control were tried and dropped: see mix-notes)
log["beat_file"] = SET.get("beat_file", "01_Beat.wav")
if SET.get("chain") == "deharsh":
    m1, m2, bg, bgbg = load("m1_9.wav"), load("m2_9.wav"), load("bg_9.wav"), load("bb_9.wav")
else:
    m1, m2, bg, bgbg = load("m1_8.wav"), load("m2_8.wav"), load("bg_7.wav"), load("bb_7.wav")

# ---------------------------------------------------------------- 2. mains narrower (phones play mono)
for x in (m1, m2):
    M, S = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2 * 10 ** (SET["side_db"] / 20)
    x[:, 0], x[:, 1] = M + S, M - S

# ---------------------------------------------------------------- 3. levels: mains equal and against the beat
K = {k: L.kweight(v) for k, v in (("beat", beat), ("m1", m1), ("m2", m2), ("bg", bg), ("bgbg", bgbg))}
full = [(a, b) for nm, a, b in L.SECTIONS if nm in ("A", "B", "C")]


def loud_over(key, spans, gate=True, x=None):
    xk = K[key] if x is None else L.kweight(x)
    vals = [L.loud(None, a, b, gate, xk=xk) for a, b in spans]
    vals = [v for v in vals if v > -90]
    return 10 * np.log10(np.mean([10 ** (v / 10) for v in vals]))


Lbeat = loud_over("beat", full, False)
g = {}
target_main = Lbeat + SET["mains_vs_beat"]
g["m1"] = target_main - loud_over("m1", full)
g["m2"] = target_main - loud_over("m2", full)
m1 *= 10 ** (g["m1"] / 20)
m2 *= 10 ** (g["m2"] / 20)
mains = m1 + m2
# the leads trade lines and overlap, so set their SUM to the target in each full section (A, B, C); the drops take
# the gain of the section before them; 1-beat ramps at the section changes (the beat changes there too)
Kmains = L.kweight(mains)
sec_gain = {}
for nm, a, b in L.SECTIONS:
    if nm in ("A", "B", "C"):
        sec_gain[nm] = (L.loud(None, a, b, False, xk=K["beat"]) + SET["mains_vs_beat"]) - L.loud(None, a, b, True, xk=Kmains)
sec_gain["intro"], sec_gain["drop 1"], sec_gain["drop 2"], sec_gain["outro"] = sec_gain["A"], sec_gain["A"], sec_gain["B"], sec_gain["C"]
curve = np.zeros(n)
for nm, a, b in L.SECTIONS:
    curve[int(a * sr):min(n, int(b * sr))] = sec_gain[nm]
k = int(L.Q * sr)
curve = np.convolve(np.pad(curve, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
m1 *= (10 ** (curve / 20))[:, None]
m2 *= (10 ** (curve / 20))[:, None]
mains = m1 + m2
log["mains_section_gain_db"] = {k_: round(v, 2) for k_, v in sec_gain.items()}
Km = L.kweight(mains)

# ---------------------------------------------------------------- 4. the layer order, every 2 bars where both sing
bg, rides_bg = L.ride_layer(bg, Km, lambda s: SET["bg_vs_mains"].get(s, -5.0), n)
Kbg = L.kweight(bg)
bgbg, rides_bb = L.ride_layer(bgbg, Kbg, lambda s: SET["bgbg_vs_bg"], n, fallback_k=Km, fallback_target=SET["bgbg_vs_mains_alone"])

# peak catchers on the two background layers (loudness + 10 dB), so their peaks do not pull the master down
pc = {}
for name in ("bg", "bgbg"):
    x = bg if name == "bg" else bgbg
    lx = L.loud(x, 30, 172)
    y, st = L.peak_catch(x, lx + 10.0)
    pc[name] = st
    if name == "bg":
        bg = y
    else:
        bgbg = y
log["peak_catch"] = pc

# ---------------------------------------------------------------- 5. echo throws on the beat
mp = json.load(open(D + "map.json"))["lines"]
envs = {"m1": L.envelope_db(load("02_Main1_rt.wav")), "m2": L.envelope_db(load("03_Main2_rt.wav"))}
events = {"m1": [], "m2": []}
last_m2 = max(p[1] for p in mp["03_Main2"])
for key, stem in (("m1", "02_Main1"), ("m2", "03_Main2")):
    for a, b in mp[stem]:
        if b - a < 1.0:
            continue
        sec = L.section_of(b)
        final = key == "m2" and abs(b - last_m2) < 0.01
        if key == "m2" and not (sec.startswith("drop") or final):
            continue
        w0, w1 = L.last_loud_word(envs[key], a, b)
        if final:
            events[key].append((w0, w1, 8, -4.0, -2.5, 2))      # the last line fades out over 8 half notes
        elif sec.startswith("drop"):
            events[key].append((w0, w1, 4, -4.0, -4.0, 1))      # more space in the drops
        else:
            events[key].append((w0, w1, 3, -6.0, -4.0, 1))
echo = np.zeros((n, 2))
elog = []
for key, src in (("m1", m1), ("m2", m2)):
    e, lg = L.render_echoes(src, events[key], n, "lead 1" if key == "m1" else "lead 2")
    echo += e
    elog += lg
gd, _, pct = L.dt.duck_gain(mains, sr, n, 3.0, None, 5, 120)
echo *= gd[:, None]
log["echoes"] = elog
log["echo_ducking"] = {"depth_db": 3, "attack_ms": 5, "release_ms": 120, "fully_ducked_pct": round(pct, 1)}

# ---------------------------------------------------------------- 6. reverbs: plate on the mains that opens up in the drops
plate_curve = np.zeros(n)
for nm, a, b in L.SECTIONS:
    plate_curve[int(a * sr):int(min(b, n / sr) * sr)] = SET["plate_db"].get(nm, -15.0)
k = int(L.Q * sr)
plate_curve = np.convolve(np.pad(plate_curve, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
pre = 30.0   # 1/64 at 125 BPM
rv_main = L.reverb(mains, "plate", 1.44, pre, 0.0, mains, 4.0, lp=SET.get("verb_lp", 12000)) * (10 ** (plate_curve / 20))[:, None]   # dotted half
rv_bg = L.reverb(bg + bgbg, "hall", 1.92, pre, -9.0, bg + bgbg, 2.0, lp=SET.get("verb_lp", 12000), seed=3)                            # 1 bar
rv_echo = L.reverb(echo, "plate", 1.44, pre, -9.0, lp=SET.get("verb_lp", 12000), seed=5)
log["reverb"] = {"mains": "plate 1.44 s (dotted half), pre-delay 30 ms (1/64), ducked 4 dB, return by section " + json.dumps(SET["plate_db"]),
                 "background": "hall 1.92 s (1 bar), pre-delay 30 ms, ducked 2 dB, return -9 dB", "echoes": "plate 1.44 s, -9 dB"}

# ---------------------------------------------------------------- 7. mix, bus, master
mix = beat + mains + bg + bgbg + echo + rv_main + rv_bg + rv_echo
# progression: the whole mix lifts a little section by section (1-beat ramps), so the song grows
lift = np.zeros(len(mix))
for nm, a, b in L.SECTIONS:
    lift[int(a * sr):min(len(mix), int(b * sr))] = SET["lift_db"].get(nm, SET["lift_db"]["C"] if nm == "outro" else 0.0)
k = int(L.Q * sr)
lift = np.convolve(np.pad(lift, (k, k), mode="edge"), np.ones(k) / k, mode="same")[k:-k]
mix *= (10 ** (lift / 20))[:, None]
log["lift_db"] = SET["lift_db"]
m = np.abs(mix).max(1)
last = np.where(m > 10 ** (-80 / 20))[0][-1]
mix = mix[:last + int(0.3 * sr)]
L.dt.write(D + f"mix_{TAG}.wav", mix, sr)
L.dt.write(D + f"stem_{TAG}_mains.wav", mains, sr)
L.dt.write(D + f"stem_{TAG}_bg.wav", bg, sr)
L.dt.write(D + f"stem_{TAG}_bgbg.wav", bgbg, sr)
L.dt.write(D + f"stem_{TAG}_echo.wav", echo, sr)
log["gains_db"] = {k: round(v, 2) for k, v in g.items()}
log["rides"] = {"bg": rides_bg, "bgbg": rides_bb}
log["beat_loudness_full_sections"] = round(Lbeat, 2)
json.dump(log, open(D + f"build_{TAG}.json", "w"), indent=1)
print(f"mains {g['m1']:+.2f} / {g['m2']:+.2f} dB; echo events: {len(elog)}; peak catch {json.dumps(pc)}")
# ms-bus adds a 9500:2.0 shelf when --mid-shelf is left out, so "no shelf" must be passed as 0 dB
shelf_arg = f" --mid-shelf {SET.get('bus_shelf') or '9500:0'}"
sh(f"{T} ms-bus mix_{TAG}.wav mix_{TAG}_ms.wav --side-hp 100{shelf_arg}", 1)
sh(f"python3 -I {TT}/render_master.py mix_{TAG}_ms.wav master_{TAG}.wav --target-lufs {SET['lufs']} --ceiling {SET['ceiling']}", 3)
sh(f"python3 -I {TT}/export_master.py {D}master_{TAG}.wav --name Baccdoor_master_{TAG} --rate 44100", 3)

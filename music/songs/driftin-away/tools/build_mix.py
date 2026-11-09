"""Driftin' Away v1: reverbs, balance by measured loudness, fade-out, mix bus, master, export.

usage: build_mix.py <tag>

Balance targets (K-weighted loudness of each part against the beat in the same stretch, measured, not guessed):
  lead (verse, 27-77 s)               beat + 1.0 dB      clearly on top
  adlibs in the verse (a partial double) lead - 9.0 dB
  background vocal (78-138 s)         beat - 3.0 dB      behind, as the owner asked
  adlib responses (80-139 s)          beat - 2.0 dB
  phone outro lines (144-161 s)       beat + 1.0 dB
Echoes and reverbs carry the gain of the voice they come from.
"""
import os
import json
import math
import subprocess
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402

D = os.path.join(os.environ.get("DRIFT_WORK", "."), "")  # folder with the stems and renders
TT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools")
TAG = sys.argv[1]
sr = 44100
G0, Q = 0.03837, 0.4
BAR = 1.6


def bar_t(b):
    return G0 + (b - 1) * BAR


def load(name, n):
    x, s = dt.read(D + name)
    assert s == sr
    if x.ndim == 1 or x.shape[1] == 1:
        x = np.repeat(x.reshape(-1, 1), 2, axis=1)
    out = np.zeros((n, 2))
    out[:min(n, len(x))] = x[:n]
    return out


def reverb(x, kind, decay, predelay, ret_db, duck_key=None, duck_db=0.0, hp=150, lp=12000):
    send = sosfilt(butter(2, [hp, lp], "bandpass", fs=sr, output="sos"), dt.mono(x))
    ir = dt.make_ir(sr, kind, decay, predelay, 1.0)
    out = np.stack([fftconvolve(send, ir[:, c])[:len(x)] for c in range(2)], 1)
    if duck_key is not None and duck_db:
        g, _, _ = dt.duck_gain(duck_key, sr, len(out), duck_db, None, 15, 400)
        out *= g[:, None]
    return out * 10 ** (ret_db / 20)


# K-weighting (ITU-R BS.1770): high shelf +4 dB around 1.7 kHz, then a 38 Hz high-pass
KS = dt.rbj("highshelf", 1681.974, sr, 3.99984, 0.7071752)
w0 = 2 * math.pi * 38.13547 / sr
al = math.sin(w0) / (2 * 0.5003270)
KH = (np.array([1, -2, 1]) * (1 + math.cos(w0)) / 2 / (1 + al), np.array([1 + al, -2 * math.cos(w0), 1 - al]) / (1 + al))


def kblocks(x):
    y = np.stack([lfilter(KH[0], KH[1], lfilter(KS[0], KS[1], x[:, c])) for c in range(2)], 1)
    p = (y ** 2).sum(axis=1)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    c = np.concatenate(([0], np.cumsum(p)))
    starts = np.arange(0, len(p) - blk, hop)
    return starts / sr, (c[starts + blk] - c[starts]) / blk


def loud(x, t0, t1, gate_self=True):
    t, ms = kblocks(x[int(t0 * sr):int(t1 * sr)])
    ms = ms[ms > 10 ** ((-70 + 0.691) / 10)]
    if gate_self and len(ms):
        rel = -0.691 + 10 * np.log10(ms.mean()) - 10
        ms = ms[-0.691 + 10 * np.log10(ms) > rel]
    return -0.691 + 10 * math.log10(ms.mean()) if len(ms) else -99.0


def main():
    beat0, _ = dt.read(D + "beat_fx.wav")
    n = len(beat0) + int(4 * sr)
    beat = load("beat_fx.wav", n)
    lead = load("l_8.wav", n)
    bgv = load("b_7.wav", n)
    adl = load("a_7.wav", n)
    t = np.arange(n) / sr
    split = 79.0
    adl_v = adl * (t < split)[:, None]
    adl_b = adl * (t >= split)[:, None]
    phone = load("phone.wav", n)
    e_lead, e_adl, e_ph = load("echo_lead.wav", n), load("echo_adlib.wav", n), load("echo_phone.wav", n)
    sw = load("revswell.wav", n)

    # ---- balance
    Lb_v, Lb_b, Lb_o = loud(beat, 27, 77, False), loud(beat, 78, 138, False), loud(beat, 142.4, 166.4, False)
    gains = {}
    gains["lead"] = (Lb_v + 1.0) - loud(lead, 27, 77)
    gains["adlib_verse"] = (loud(lead, 27, 77) + gains["lead"] - 9.0) - loud(adl_v, 27, 77)
    gains["background"] = (Lb_b - 3.0) - loud(bgv, 78, 138)
    gains["adlib_responses"] = (Lb_b - 2.0) - loud(adl_b, 79, 139.5)
    # the outro beat is a quiet breakdown (about 10 dB under the verse beat), so the phone lines are set against
    # the verse lead instead: 6 dB under it, which still puts them well in front of the outro beat
    gains["phone"] = (Lb_v + 1.0 - 6.0) - loud(phone, 144, 161)
    print(f"beat loudness: verse {Lb_v:.1f}, second half {Lb_b:.1f}, outro {Lb_o:.1f} LUFS (K-weighted, ungated)")
    print("mix gains (dB): " + ", ".join(f"{k} {v:+.2f}" for k, v in gains.items()))
    G = {k: 10 ** (v / 20) for k, v in gains.items()}

    # ---- reverbs: lead plate 1 bar (1.6 s), background hall 1.5 bars (2.4 s), pre-delay 1/64 = 25 ms
    rv = {}
    rv["lead"] = reverb(lead, "plate", 1.6, 25.0, -12.5, lead, 4.0) * G["lead"]
    rv["background"] = reverb(bgv, "hall", 2.4, 25.0, -9.0, bgv, 2.0) * G["background"]
    rv["adlib_verse"] = reverb(adl_v, "plate", 1.6, 25.0, -14.0, adl_v, 3.0) * G["adlib_verse"]
    rv["adlib_responses"] = reverb(adl_b, "plate", 1.6, 25.0, -12.0, adl_b, 3.0) * G["adlib_responses"]
    echoes = e_lead * G["lead"] + e_adl * G["adlib_responses"] + e_ph * G["phone"]
    rv["echoes"] = reverb(echoes, "plate", 1.6, 25.0, -8.0)
    rv["phone"] = reverb(phone, "hall", 2.4, 25.0, -14.0, phone, 2.0) * G["phone"]
    # the reverse swells carry the gain of the voice they lead into
    sw_g = np.where(t < 70, G["lead"], G["background"])[:, None]

    mix = (beat + lead * G["lead"] + adl_v * G["adlib_verse"] + bgv * G["background"] + adl_b * G["adlib_responses"]
           + phone * G["phone"] + echoes + sw * sw_g + sum(rv.values()))

    # ---- fade-out: bars 99-104 (156.84 s to the beat's end at bar 105, 166.44 s), raised cosine, then silence
    f0, f1 = bar_t(99), bar_t(105)
    u = np.clip((t - f0) / (f1 - f0), 0, 1)
    fade = 0.5 * (1 + np.cos(np.pi * u))
    mix *= fade[:, None]
    m = np.abs(mix).max(1)
    last = np.where(m > 10 ** (-80 / 20))[0][-1]
    mix = mix[:last + int(0.5 * sr)]
    dt.write(D + f"mix_{TAG}.wav", mix, sr)

    # section check on the actual mix ingredients
    chk = {
        "lead_vs_beat_verse_db": round(loud(lead * G["lead"], 27, 77) - Lb_v, 2),
        "background_vs_beat_db": round(loud(bgv * G["background"], 78, 138) - Lb_b, 2),
        "adlib_responses_vs_beat_db": round(loud(adl_b * G["adlib_responses"], 79, 139.5) - Lb_b, 2),
        "adlib_verse_vs_lead_db": round(loud(adl_v * G["adlib_verse"], 27, 77) - loud(lead * G["lead"], 27, 77), 2),
        "phone_vs_beat_outro_db": round(loud(phone * G["phone"], 144, 161) - Lb_o, 2),
        "phone_vs_verse_lead_db": round(loud(phone * G["phone"], 144, 161) - loud(lead * G["lead"], 27, 77), 2),
        "background_vs_beat_by_part_db": {
            lab: round(loud(bgv * G["background"], a, b) - loud(beat, a, b, False), 2)
            for lab, a, b in (("bars 50-56 breakdown", 78.4, 89.6), ("bars 57-62 808 only", 89.6, 99.2),
                              ("bars 65-86 full beat", 102.4, 137.6))},
        "lead_vs_beat_by_part_db": {
            lab: round(loud(lead * G["lead"], a, b) - loud(beat, a, b, False), 2)
            for lab, a, b in (("bars 17-22", 25.6, 35.2), ("bars 23-24 beat stop", 35.2, 38.4),
                              ("bars 25-38", 38.4, 60.8), ("bars 41-48", 64.0, 76.8))},
        "echo_lead_vs_lead_db": round(loud(e_lead * G["lead"], 27, 78) - loud(lead * G["lead"], 27, 77), 2),
        "lead_reverb_vs_lead_db": round(loud(rv["lead"], 27, 78) - loud(lead * G["lead"], 27, 77), 2),
        "background_reverb_vs_background_db": round(loud(rv["background"], 78, 139) - loud(bgv * G["background"], 78, 138), 2),
    }
    print("measured balance:", json.dumps(chk))
    json.dump({"gains_db": {k: round(v, 2) for k, v in gains.items()}, "balance": chk,
               "fade": {"start_s": round(f0, 4), "end_s": round(f1, 4), "shape": "raised cosine", "bars": "99-104"},
               "length_s": round(len(mix) / sr, 3)}, open(D + f"mix_{TAG}.json", "w"), indent=1)

    def sh(cmd):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stdout[-1500:] + r.stderr[-1500:])
        print("   " + "\n   ".join((r.stdout + r.stderr).strip().splitlines()[-4:]))

    sh(f"python3 -I {TT}/dsp_tools.py ms-bus {D}mix_{TAG}.wav {D}mix_{TAG}_ms.wav --side-hp 90 --mid-shelf 9500:1.5")
    sh(f"python3 -I {TT}/render_master.py {D}mix_{TAG}_ms.wav {D}master_{TAG}.wav --target-lufs -11.5 --ceiling -0.5")
    sh(f"cd {D} && python3 -I {TT}/export_master.py {D}master_{TAG}.wav --name Driftin_Away_master_{TAG} --rate 44100")


if __name__ == "__main__":
    main()

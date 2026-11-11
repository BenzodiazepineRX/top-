"""Independent checks of one version of Driftin' Away (usage: verify_v1.py [version], default v1) (measured from the rendered files, not from the build's own numbers).

1. echoes: every repeat found by cross-correlating the dry word with the rendered echo track (+-40 ms search);
   distance of the found repeat to the grid beat and to the nearest drum hit detected in the ORIGINAL beat
2. reverse swells: where each swell's energy ends vs where the dry word's sound starts
3. air gaps: level of the master inside each gap, and the step at both edges (click check)
4. fade-out: master level per bar from bar 95 to the end
5. loud clicks anywhere: largest sample-to-sample jump in the master vs its 99.99th percentile
"""
import os
import json
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfiltfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
import dsp_tools as dt  # noqa: E402

D = os.path.join(os.path.abspath(os.environ.get("DRIFT_WORK", ".")), "")  # work folder, absolute
sr = 44100
G0, Q = 0.03837, 0.4
V = sys.argv[1] if len(sys.argv) > 1 else "v1"
# the shared effect files (fx_events.json, echo_*.wav, revswell.wav) must come from the same build as this master:
# run build_fx.py with the matching FX_VERSION before checking a version
ev = json.load(open(D + "fx_events.json"))
hits = np.load(D + "drum_hits.npy")
bp = butter(4, [500, 4500], "bandpass", fs=sr, output="sos")
mono = dt.mono
src = {"lead": "l_8.wav", "adlib": "a_7.wav" if V == "v1" else "a_8.wav", "phone": "phone.wav", "background": "b_7.wav"}
echo = {"lead": "echo_lead.wav", "adlib": "echo_adlib.wav", "phone": "echo_phone.wav", "background": "echo_bgv.wav"}
cache = {}


def get(name):
    if name not in cache:
        x, _ = dt.read(D + name)
        cache[name] = sosfiltfilt(bp, mono(x))
    return cache[name]


def ncc_lag(w, seg):
    n = len(w)
    num = fftconvolve(seg, w[::-1], mode="valid")
    cs = np.concatenate([[0], np.cumsum(seg ** 2)])
    en = cs[n:] - cs[:-n]
    r = num / (np.sqrt(np.maximum(en, 1e-20) * np.dot(w, w)) + 1e-18)
    k = int(np.argmax(r))
    return k, float(r[k])


print("1. echoes (repeat start found by correlation; ms from the grid beat / from the nearest real drum hit)")
offs_grid, offs_hit, worst = [], [], []
for r in ev["echoes"]:
    a, e = r["word"]
    w = get(src[r["src"]])[int((a - 0.005) * sr):int((e + 0.02) * sr)]
    E = get(echo[r["src"]])
    row = []
    for tk in r["echo_times"]:
        s0 = int((tk - 0.005 - 0.040) * sr)
        k, c = ncc_lag(w, E[s0:s0 + len(w) + int(0.080 * sr)])
        t_found = (s0 + k) / sr + 0.005
        og = (t_found - (G0 + round((t_found - G0) / Q) * Q)) * 1000
        oh = (t_found - hits[np.argmin(np.abs(hits - t_found))]) * 1000
        offs_grid.append(og)
        offs_hit.append(oh)
        row.append(f"{og:+5.1f}/{oh:+5.1f} (r {c:.2f})")
        worst.append((abs(og), r["src"], tk, c))
    print(f"   {r['src']:5s} {a:7.2f}s -> " + "  ".join(row))
og, oh = np.abs(offs_grid), np.abs(offs_hit)
print(f"   {len(og)} repeats: from the grid beat median {np.median(og):.2f} ms, max {og.max():.2f} ms; "
      f"from the nearest drum hit median {np.median(oh):.1f} ms, {int((oh <= 10).sum())} of {len(oh)} within 10 ms")
print(f"   lowest correlation {min(w_[3] for w_ in worst):.2f} (1 = identical copy)")

print()
print("2. reverse swells: swell end vs the dry word's first sound")
sw, _ = dt.read(D + "revswell.wav")
for s in ev["reverse_swells"]:
    name = "b_7.wav" if "background" in s["what"] else "l_8.wav"
    x, _ = dt.read(D + name)
    a = s["attack_s"]
    seg = np.abs(mono(sw[int((a - 1.0) * sr):int((a + 0.2) * sr)]))
    env = np.convolve(seg, np.ones(int(0.002 * sr)) / int(0.002 * sr), mode="same")
    end = (a - 1.0) + np.where(env > env.max() * 10 ** (-40 / 20))[0][-1] / sr
    pk_t = (a - 1.0) + int(np.argmax(env)) / sr
    dry = np.abs(mono(x[int((a - 0.3) * sr):int((a + 0.3) * sr)]))
    denv = np.convolve(dry, np.ones(int(0.002 * sr)) / int(0.002 * sr), mode="same")
    first = (a - 0.3) + np.where(denv > denv.max() * 10 ** (-30 / 20))[0][0] / sr
    print(f"   {s['what']:32s} swell {s['swell_start_s']:.3f}-{end:.3f} s (loudest at {pk_t:.3f}); dry sound starts "
          f"{first:.3f} s, detected attack {a:.3f} s -> swell ends {1000 * (end - first):+.1f} ms from the first sound")

print()
print("3. air gaps in the master")
m, _ = dt.read(D + f"Driftin_Away_master_{V}_24bit.wav")
for g in ev["air_gaps"]:
    s, e = g["gap_s"]
    inside = m[int((s + 0.01) * sr):int((e - 0.002) * sr)]
    before = m[int((s - 0.2) * sr):int(s * sr)]
    after = m[int(g["drop_transient_s"] * sr):int((g["drop_transient_s"] + 0.2) * sr)]
    rms = lambda z: 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-12)  # noqa: E731
    print(f"   bar {g['bar']}: before {rms(before):.1f} dBFS, inside the gap {rms(inside):.1f} dBFS, drop {rms(after):.1f} dBFS "
          f"(drop transient {g['transient_vs_grid_ms']:+.1f} ms from the grid downbeat)")

print()
print("4. fade-out, master level per bar")
for b in range(95, 106):
    t0 = G0 + (b - 1) * 1.6
    seg = m[int(t0 * sr):int((t0 + 1.6) * sr)]
    if len(seg) < 100:
        break
    print(f"   bar {b:3d} ({t0:6.2f} s): {20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12):6.1f} dBFS")

print()
d = np.abs(np.diff(m, axis=0)).max(1)
print(f"5. largest sample-to-sample jump {d.max():.3f} at {np.argmax(d) / sr:.2f} s; 99.99th percentile {np.percentile(d, 99.99):.3f}")
top = np.argsort(d)[-5:][::-1]
print("   top 5 jumps at " + ", ".join(f"{i / sr:.3f} s ({d[i]:.3f})" for i in top))

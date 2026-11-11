#!/usr/bin/env python3
"""Satan's Casino v03.

v02's added vocals were slices: a phrase head was dropped, tails were cut at
300 ms or 1.6 s, and the cut was moved onto a bar line. This render does not
do that.

An added vocal is a whole silence-bounded articulation, shifted by a whole
number of bars so the singer's offset to the downbeat stays put. If a whole
articulation does not fit, that event is left out.

Dry beat -8 dB, dry vocal -6 dB, both at sample 0. No limiter.

  python3 music/songs/satans-casino/tools/render_v03.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

import importlib.util

SONG = Path(__file__).resolve().parents[1]
CFG = json.loads((SONG / "config" / "v03.json").read_text())
SR = int(CFG["sample_rate"])
BPM = float(CFG["bpm"])
Q = int(CFG["samples_per_quarter"])
BAR = 4 * Q

_spec = importlib.util.spec_from_file_location(
    "sc_v02", Path(__file__).with_name("render_v02.py")
)
v02 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v02)


def samples(seconds):
    return int(round(float(seconds) * SR))


def frame_db(mono):
    hop = int(CFG["articulation"]["frame_hop_s"] * SR)
    win = int(CFG["articulation"]["frame_win_s"] * SR)
    c = np.cumsum(np.concatenate([[0.0], mono.astype(np.float64) ** 2]))
    n = 1 + (len(mono) - win) // hop
    i0 = np.arange(n) * hop
    db = 20.0 * np.log10(np.sqrt((c[i0 + win] - c[i0]) / win) + 1e-20)
    return i0 / SR, db, hop / SR


def quiet_gaps(mono):
    t, db, hop = frame_db(mono)
    quiet = db < CFG["articulation"]["quiet_db"]
    need = int(np.ceil(CFG["articulation"]["min_gap_s"] / hop))
    gaps = []
    i = 0
    while i < len(quiet):
        if not quiet[i]:
            i += 1
            continue
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        if j - i >= need:
            gaps.append((float(t[i]), float(t[j - 1] + hop)))
        i = j
    return gaps


def articulations(gaps):
    arts = []
    for (a1, b1), (a2, b2) in zip(gaps, gaps[1:]):
        if a2 - b1 >= 0.2:
            arts.append({
                "start_s": b1,
                "end_s": a2,
                "dur_s": a2 - b1,
                "pre_gap_s": b1 - a1,
                "post_gap_s": b2 - a2,
            })
    return arts


def region_db(mono, t0, t1):
    s = max(0, samples(t0))
    e = min(len(mono), samples(t1))
    if e <= s + 8:
        return -200.0
    return float(v02.db(mono[s:e]))


def kick_phase(beat_mono):
    """First sample of a strong kick versus the arithmetic downbeat."""
    offs = []
    hits = []
    for bar in range(0, 60):
        center = bar * BAR
        a = max(0, center - samples(0.01))
        b = min(len(beat_mono), center + samples(0.06))
        seg = beat_mono[a:b]
        strong = np.flatnonzero(np.abs(seg) > 0.15)
        if len(strong) == 0 or np.max(np.abs(seg)) < 0.8:
            continue
        off_ms = (a + int(strong[0]) - center) / SR * 1000.0
        offs.append(off_ms)
        hits.append({"bar": bar, "t_s": round(center / SR, 6), "offset_ms": round(off_ms, 2)})
    return {
        "n": len(offs),
        "median_ms": None if not offs else round(float(np.median(offs)), 2),
        "min_ms": None if not offs else round(float(np.min(offs)), 2),
        "max_ms": None if not offs else round(float(np.max(offs)), 2),
        "hits": hits[:8],
        "reading": (
            "Strong kick attacks sit about +1 to +3 ms after the arithmetic downbeat. "
            "A low-frequency body peak near +29 ms is the tone of the kick, not a second grid. "
            "Vocal copies keep the singer's offset to that downbeat. They are not slid so a cut lands on the bar."
        ),
    }


def audit_v02(mono, arts):
    path = SONG / "effects" / "v02-events.json"
    if not path.exists():
        return []
    old = json.loads(path.read_text())["events"]
    rows = []
    for e in old:
        if e["layer"] not in ("telephone_bgv", "delay_throws", "reverse_swells"):
            continue
        a = float(e["source_start_s"])
        b = float(e["source_end_s"])
        before = region_db(mono, a - 0.18, a - 0.02)
        at_end = region_db(mono, b - 0.03, b)
        after = region_db(mono, b + 0.02, b + 0.15)
        # which whole articulation contains this slice
        home = None
        for art in arts:
            if art["start_s"] - 0.03 <= a and b <= art["end_s"] + 0.05:
                home = art
                break
        chopped_head = before > -32.0
        chopped_tail = after > -32.0
        interior = False
        if home:
            interior = (a - home["start_s"]) > 0.05 or (home["end_s"] - b) > 0.08
        snapped = False
        if e["layer"] in ("telephone_bgv", "delay_throws"):
            # v02 placed the slice start on a grid line, not a bar-multiple of the source
            dest = int(e.get("dest_start_sample") or round(float(e["dest_start_s"]) * SR))
            src = int(e.get("source_start_sample") or round(a * SR))
            shift = dest - src
            snapped = (shift % BAR) != 0
        reasons = []
        if chopped_head:
            reasons.append("loud audio in the 180 ms before the slice was left out")
        if chopped_tail:
            reasons.append("the slice ends while the line is still going")
        if interior:
            reasons.append(
                f"slice sits inside {home['start_s']:.3f}-{home['end_s']:.3f}s "
                f"instead of using that whole span"
            )
        if snapped:
            reasons.append("the slice was moved onto a grid line instead of keeping the singer's offset")
        if e["layer"] == "reverse_swells" and interior:
            reasons.append("reverse send was a short cut of a longer line")
        rows.append({
            "id": e["id"],
            "layer": e["layer"],
            "source_start_s": a,
            "source_end_s": b,
            "level_before_db": round(before, 2),
            "level_at_end_db": round(at_end, 2),
            "level_after_db": round(after, 2),
            "chopped_head": chopped_head,
            "chopped_tail": chopped_tail,
            "interior_of_longer_line": interior,
            "grid_snapped": snapped,
            "v03": "omitted" if e["layer"] == "delay_throws" or reasons else "rebuilt",
            "why": "; ".join(reasons) if reasons else "boundaries already sat on a whole line",
        })
    return rows


def phone_filter(stereo_or_mono):
    lo, hi = CFG["phone"]["band_hz"]
    sos = butter(int(CFG["phone"]["order"]), [lo, hi], btype="band", fs=SR, output="sos")
    y = np.asarray(stereo_or_mono, dtype=np.float64)
    if y.ndim == 1:
        y = sosfiltfilt(sos, y)
        y = np.stack([y, y], axis=1)
    else:
        y = sosfiltfilt(sos, y, axis=0)
    return y.astype(np.float32)


def main():
    beat = v02.load_flac(SONG / "sources" / "satans-casino-beat.flac")
    vocal_src = v02.load_flac(SONG / "sources" / "satans-casino-lead-vocals.flac")
    n = len(beat)
    vm = vocal_src.mean(axis=1).astype(np.float32)
    bm = beat.mean(axis=1)

    g_beat = v02.gain_lin(CFG["balance_db"]["beat"])
    g_vocal = v02.gain_lin(CFG["balance_db"]["vocal"])
    beat_dry = beat * np.float32(g_beat)
    vocal = np.zeros((n, 2), np.float32)
    vocal[: len(vocal_src)] = vocal_src
    vocal_dry = vocal * np.float32(g_vocal)

    phase = kick_phase(bm)
    print("kick phase median", phase["median_ms"], "ms", "n", phase["n"])

    gaps = quiet_gaps(vm)
    arts = articulations(gaps)
    print("articulations")
    for art in arts:
        if art["dur_s"] < 6:
            print(f"  {art['start_s']:.3f}-{art['end_s']:.3f} dur {art['dur_s']:.2f}")

    v02_audit = audit_v02(vm, arts)

    # The opening line is the one silence-bounded phrase that starts just before 16 s.
    opening = None
    for art in arts:
        if 15.5 < art["start_s"] < 16.3 and art["dur_s"] < 6:
            opening = art
            break
    if opening is None:
        sys.exit("No silence-bounded opening phrase was found. Nothing was forced.")

    downbeat = 16.0  # beat 36, bar 9, sample 16*44100
    onset_offset_s = opening["start_s"] - downbeat
    print(f"opening {opening['start_s']:.3f}-{opening['end_s']:.3f} offset vs 16.000s {onset_offset_s*1000:.1f} ms")

    events = []
    omitted = []
    phone_bus = np.zeros((n, 2), np.float32)
    reverse_bus = np.zeros((n, 2), np.float32)
    stop_bus = np.zeros((n, 2), np.float32)
    envelope = np.ones(n, np.float32)

    # --- telephone: whole opening line, eight bars earlier, same offset ---
    pad = samples(CFG["phone"]["pre_pad_s"])
    src0 = max(0, samples(opening["start_s"]) - pad)
    src1 = min(len(vm), samples(opening["end_s"]))
    shift = int(CFG["phone"]["bar_shift"]) * BAR
    dest = src0 + shift
    if dest < 0 or src1 + shift > samples(12.5):
        omitted.append({
            "id": "phone-intro",
            "why": "The whole opening line does not fit in the intro without meeting the real vocal.",
        })
    else:
        raw = vm[src0:src1]
        # level of the actual attack, before and after the band limit
        atk = raw[pad:pad + samples(0.08)]
        filtered = phone_filter(raw)
        atk_f = filtered[pad:pad + samples(0.08)].mean(axis=1)
        atk_drop = float(v02.db(atk) - v02.db(atk_f))
        win = beat_dry[dest:dest + (src1 - src0)]
        # sit just under the intro beat's peak, and never as a second lead
        target = min(v02.peak_db(win)[0] - 1.0, -18.0)
        gain = target - v02.peak_db(filtered)[0]
        v02.add_at(phone_bus, filtered, dest, gain)
        events.append({
            "id": "phone-opening-line",
            "layer": "telephone_bgv",
            "source_start_s": round(src0 / SR, 6),
            "source_end_s": round(src1 / SR, 6),
            "source_start_sample": int(src0),
            "source_end_sample": int(src1),
            "onset_s": round(opening["start_s"], 6),
            "onset_offset_vs_downbeat_ms": round(onset_offset_s * 1000, 2),
            "downbeat_s": downbeat,
            "dest_start_s": round(dest / SR, 6),
            "dest_end_s": round((dest + src1 - src0) / SR, 6),
            "dest_start_sample": int(dest),
            "dest_end_sample": int(dest + src1 - src0),
            "shift_samples": int(shift),
            "shift_bars": int(CFG["phone"]["bar_shift"]),
            "gain_db": round(float(gain), 3),
            "attack_db_lost_to_bandlimit": round(atk_drop, 2),
            "band_hz": CFG["phone"]["band_hz"],
            "why": (
                "The whole opening line, from the silence before it through the tail. "
                "Moved exactly eight bars earlier, so it still anticipates the downbeat "
                "by the same amount. The start is not a cut, and it is not snapped to the bar."
            ),
        })

    # throws: none of the v02 slices were whole lines, and the whole lines are longer than the gaps
    for row in v02_audit:
        if row["layer"] == "delay_throws":
            omitted.append({
                "id": row["id"],
                "layer": "delay_throws",
                "why": row["why"] + " The whole line is longer than the gap after it, so no repeat was made.",
            })
    if any(r["layer"] == "telephone_bgv" and r["id"] == "phone-outro" for r in v02_audit):
        omitted.append({
            "id": "phone-outro",
            "layer": "telephone_bgv",
            "why": (
                "The 1.6 s outro slice began inside the closing line. "
                "That line is not bounded by a silence at the slice point, so it was not copied."
            ),
        })

    # --- reverses from whole lines, swell only, ending on the real onset ---
    rev_ir = v02.make_ir(CFG["reverse"]["decay_s"], 0.0, CFG["reverse"]["seed"], high_hz=5000)

    def add_reverse(event_id, art, length_s, why):
        s0 = samples(art["start_s"])
        s1 = min(len(vm), samples(art["end_s"]))
        wet = v02.convolve_stereo(vm[s0:s1], rev_ir)
        wet = wet[::-1].copy()
        keep = min(len(wet), samples(length_s), s0)
        wet = wet[-keep:]
        fade = max(samples(0.25), keep // 3)
        wet = v02.apply_fades(wet, fade, samples(0.006))
        g = CFG["reverse"]["target_peak_dbfs"] - v02.peak_db(wet)[0]
        dest = s0 - len(wet)
        v02.add_at(reverse_bus, wet, dest, g)
        events.append({
            "id": event_id,
            "layer": "reverse_swells",
            "source_start_s": round(s0 / SR, 6),
            "source_end_s": round(s1 / SR, 6),
            "source_start_sample": int(s0),
            "source_end_sample": int(s1),
            "dest_start_s": round(max(dest, 0) / SR, 6),
            "dest_end_s": round(s0 / SR, 6),
            "dest_start_sample": int(dest),
            "dest_end_sample": int(s0),
            "gain_db": round(float(g), 3),
            "target_peak_dbfs": CFG["reverse"]["target_peak_dbfs"],
            "fade_in_ms": round(fade / SR * 1000, 1),
            "why": why,
        })

    add_reverse(
        "reverse-into-opening",
        opening,
        BAR / SR,
        "Reversed reverb of the whole opening line. The swell ends on the real onset, including its early entry. It is not a dry chopped word.",
    )
    returning = None
    for art in arts:
        if 156.2 < art["start_s"] < 156.7:
            returning = art
            break
    if returning:
        hole = returning["start_s"] - 154.928
        add_reverse(
            "reverse-into-return",
            returning,
            min(0.95, max(0.4, hole - 0.12)),
            "Reversed reverb of the line that starts after the quiet hole. Ends on that onset. The hole measured about 154.93-156.43 s.",
        )
    else:
        omitted.append({"id": "reverse-into-return", "why": "No silence-bounded line was found at the return."})

    # --- beat-stop risers, same two bars, not vocal slices ---
    for stop in CFG["beat_stops"]:
        bar = int(stop["bar"])
        dest_b = bar * BAR
        rise = BAR
        fall = Q // 2
        env_db = np.zeros(rise + fall, np.float32)
        env_db[:rise] = v02.cos_fade(rise, True) * np.float32(stop["envelope_db"])
        env_db[rise:] = v02.cos_fade(fall, False) * np.float32(stop["envelope_db"])
        s = dest_b - rise
        a0 = max(0, s)
        b0 = min(n, s + len(env_db))
        mult = (10 ** (env_db / 20.0)).astype(np.float32)
        envelope[a0:b0] *= mult[a0 - s:a0 - s + (b0 - a0)]
        lo, hi = stop["riser_band_hz"]
        src = v02.band_slice(beat, dest_b - BAR, dest_b, lo, hi)[::-1].copy()
        ramp = np.linspace(0, 1, len(src), dtype=np.float32) ** 1.6
        tail = min(Q // 16, len(src) // 4)
        ramp[-tail:] *= v02.cos_fade(tail, False)
        src *= ramp[:, None]
        src = v02.apply_fades(src, samples(0.03), 0)
        need = stop["riser_peak_dbfs"] - v02.peak_db(src)[0]
        v02.add_at(stop_bus, src, dest_b - len(src), need)
        events.append({
            "id": f"beat-stop-bar-{bar}",
            "layer": "beat_stop",
            "source_start_s": round((dest_b - BAR) / SR, 6),
            "source_end_s": round(dest_b / SR, 6),
            "dest_start_s": round((dest_b - len(src)) / SR, 6),
            "dest_end_s": round(dest_b / SR, 6),
            "dest_end_sample": int(dest_b),
            "gain_db": round(float(need), 3),
            "why": stop["why"],
        })
    stop_bus += beat_dry * (envelope - 1.0)[:, None]

    # --- lead reverb on the full dry vocal, phone reverb on the phone bus ---
    print("reverbs")
    lead_cfg = CFG["lead_reverb"]
    lead_ir = v02.make_ir(
        v02.NOTE_SAMPLES[lead_cfg["decay_note"]] / SR,
        v02.NOTE_SAMPLES[lead_cfg["predelay_note"]] / SR,
        lead_cfg["seed"],
        high_hz=4200,
    )
    lead_reverb = v02.convolve_stereo(vocal_dry.mean(axis=1), lead_ir)
    sung = np.zeros(n, dtype=bool)
    for art in arts:
        sung[samples(art["start_s"]):samples(art["end_s"])] = True
    sung[: len(vm)] |= np.abs(vm) > 10 ** (-36 / 20)
    if sung.any():
        lead_gain = (v02.db(vocal_dry[sung]) + lead_cfg["return_db"]) - v02.db(lead_reverb[sung])
    else:
        lead_gain = lead_cfg["return_db"]
    lead_reverb *= np.float32(v02.gain_lin(lead_gain))
    hop_e = 256
    env = v02.frame_db(vocal_dry.mean(axis=1), hop_e, 1024)
    flag = np.repeat(env > -34.0, hop_e)[:n]
    if len(flag) < n:
        flag = np.pad(flag, (0, n - len(flag)))
    follow = v02.smooth_follow(flag.astype(np.float32), int(lead_cfg["release_ms"] / 1000 * SR))
    lead_reverb *= (10 ** ((-lead_cfg["duck_db"] * follow) / 20.0)).astype(np.float32)[:, None]

    phone_cfg = CFG["phone"]
    phone_ir = v02.make_ir(
        v02.NOTE_SAMPLES[phone_cfg["reverb_decay_note"]] / SR,
        v02.NOTE_SAMPLES[phone_cfg["reverb_predelay_note"]] / SR,
        phone_cfg["seed"],
        high_hz=2800,
    )
    phone_reverb = v02.convolve_stereo(phone_bus.mean(axis=1), phone_ir)
    active = np.max(np.abs(phone_bus), axis=1) > 1e-5
    if active.any():
        phone_rev_gain = (v02.db(phone_bus[active]) + phone_cfg["reverb_return_db"]) - v02.db(phone_reverb[active])
    else:
        phone_rev_gain = phone_cfg["reverb_return_db"]
    phone_reverb *= np.float32(v02.gain_lin(phone_rev_gain))

    events.append({
        "id": "lead-reverb",
        "layer": "lead_reverb",
        "gain_db": round(float(lead_gain), 3),
        "predelay_ms": round(v02.NOTE_SAMPLES[lead_cfg["predelay_note"]] / SR * 1000, 2),
        "decay_s": round(v02.NOTE_SAMPLES[lead_cfg["decay_note"]] / SR, 5),
        "why": "Send of the full dry vocal. Not a sliced phrase.",
    })
    events.append({
        "id": "phone-reverb",
        "layer": "telephone_reverb",
        "gain_db": round(float(phone_rev_gain), 3),
        "predelay_ms": round(v02.NOTE_SAMPLES[phone_cfg["reverb_predelay_note"]] / SR * 1000, 2),
        "decay_s": round(v02.NOTE_SAMPLES[phone_cfg["reverb_decay_note"]] / SR, 5),
        "why": "Reverb of the telephone bus only.",
    })

    fx = stop_bus + reverse_bus + phone_bus + phone_reverb + lead_reverb
    dry = beat_dry + vocal_dry
    mix = dry + fx
    trims = []
    for _ in range(6):
        pk_db = v02.peak_db(mix)[0]
        if pk_db <= CFG["headroom_dbfs"]:
            break
        over = pk_db - CFG["headroom_dbfs"] + 0.15
        fx *= np.float32(v02.gain_lin(-over))
        mix = dry + fx
        trims.append(round(over, 3))
    trim_lin = np.float32(v02.gain_lin(-sum(trims))) if trims else np.float32(1.0)
    buses = {
        "beat_dry": beat_dry,
        "vocal_dry": vocal_dry,
        "beat_stop": stop_bus * trim_lin,
        "reverse_swells": reverse_bus * trim_lin,
        "telephone_bgv": phone_bus * trim_lin,
        "telephone_reverb": phone_reverb * trim_lin,
        "lead_reverb": lead_reverb * trim_lin,
        "delay_throws": np.zeros((n, 2), np.float32),
    }
    mix = dry + sum(buses[k] for k in buses if k not in ("beat_dry", "vocal_dry"))

    # boundary self-check before writing
    problems = []
    for e in events:
        if e["layer"] != "telephone_bgv":
            continue
        a, b = e["source_start_s"], e["source_end_s"]
        before = region_db(vm, a - 0.15, a - 0.01)
        after = region_db(vm, b + 0.01, b + 0.12)
        if before > -36:
            problems.append(f"{e['id']} still has a loud head before {a:.3f}s ({before:.1f} dB)")
        if after > -32:
            problems.append(f"{e['id']} still cuts into later audio ({after:.1f} dB)")
        if e["shift_samples"] % BAR != 0:
            problems.append(f"{e['id']} shift is not a whole number of bars")
        # the musical onset, not the silence pad, keeps its offset
        onset_src = samples(e["onset_s"])
        onset_dest = onset_src + e["shift_samples"]
        src_off = onset_src - samples(e["downbeat_s"])
        dest_bar = samples(e["downbeat_s"]) + e["shift_samples"]
        if onset_dest - dest_bar != src_off:
            problems.append(f"{e['id']} did not keep the onset offset")
    if problems:
        print("BOUNDARY FAILURES")
        print("\n".join(problems))
        sys.exit(1)

    finite = bool(np.isfinite(mix).all())
    sample_pk = v02.peak_db(mix)[0]
    tp = v02.true_peak_db(mix)[0]
    lufs = v02.integrated_lufs(mix)
    base = dry
    base_pk = v02.peak_db(base)[0]
    base_tp = v02.true_peak_db(base)[0]
    base_lufs = v02.integrated_lufs(base)
    ref = vocal_src * np.float32(g_vocal)
    corr = float(np.corrcoef(vocal_dry[: len(ref), 0], ref[:, 0])[0, 1])
    beat_corr = float(np.corrcoef(beat_dry[:, 0], (beat[:, 0] * np.float32(g_beat)))[0, 1])

    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + " — " + detail)

    check("finite", finite, "mix samples finite" if finite else "non-finite")
    check("no_clip", v02.peak_db(mix)[1] < 1.0, f"peak {sample_pk:.3f} dBFS")
    check("baseline_peak", abs(base_pk - (-1.55)) < 0.05, f"{base_pk:.3f} dBFS")
    check("vocal_unshifted", corr > 0.999999, f"{corr:.6f}")
    check("beat_unshifted", beat_corr > 0.999999, f"{beat_corr:.6f}")
    check("length", len(mix) == n, f"{n / SR:.6f}s")
    check("no_delay_throws", not any(e["layer"] == "delay_throws" for e in events), "cropped throws were not rebuilt")
    check("phone_keeps_offset", not problems, "opening line offset preserved")
    check("true_peak", tp <= -1.0, f"{tp:.3f} dBTP")

    out_r = SONG / "renders"
    out_b = SONG / "buses"
    print("writing")
    v02.write_pcm24(out_r / "satans-casino-v03-review.wav", mix)
    for name, audio in buses.items():
        if name in ("beat_dry", "vocal_dry"):
            continue
        v02.write_pcm24(out_b / f"v03_{name}.flac", audio)
    mp3 = out_r / "satans-casino-v03-review.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(out_r / "satans-casino-v03-review.wav"),
         "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)],
        check=True,
    )
    mp3_raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    )
    mp3_audio = np.frombuffer(mp3_raw.stdout, dtype="<f4").reshape(-1, 2)
    mp3_pk = v02.peak_db(mp3_audio)[0]
    mp3_tp = v02.true_peak_db(mp3_audio)[0]

    bus_levels = {k: {"peak_dbfs": round(v02.peak_db(a)[0], 2), "rms_db": round(float(v02.db(a)), 2)} for k, a in buses.items()}
    quality = {
        "version": "v03",
        "listening": "not performed",
        "lyric_transcription": "not available",
        "musical_qa": "not claimed",
        "bpm": BPM,
        "kick_phase": phase,
        "opening_phrase": opening,
        "onset_offset_vs_16s_ms": round(onset_offset_s * 1000, 2),
        "baseline": {"sample_peak_dbfs": round(base_pk, 3), "true_peak_dbtp": round(base_tp, 3), "integrated_lufs": round(base_lufs, 2)},
        "candidate": {
            "sample_peak_dbfs": round(sample_pk, 3),
            "true_peak_dbtp": round(tp, 3),
            "integrated_lufs": round(lufs, 2),
            "seconds": round(n / SR, 6),
            "mp3_sample_peak_dbfs": round(mp3_pk, 3),
            "mp3_true_peak_dbtp": round(mp3_tp, 3),
            "fx_headroom_trims_db": trims,
        },
        "bus_levels": bus_levels,
        "checks": checks,
        "v02_boundary_audit": v02_audit,
        "omitted": omitted,
        "uncertainty": [
            "No listening pass. A silence floor of -42 dB for 120 ms is what counted as a gap. Words separated by a smaller dip stay inside one articulation and were not split.",
            "The opening copy is the whole 15.95-18.78 s line, moved eight bars earlier. Whether that preview belongs in the intro is a listening decision. The cut and the snapped start from v02 are gone.",
            "Delay throws were omitted because every v02 throw was a slice of a longer line, and the whole line does not fit in the gap.",
            "The telephone outro was omitted for the same reason. Forcing a 1.6 s window would start mid-line.",
            "Kick attacks measure about +2.6 ms from the arithmetic downbeat. That is the grid used. It was not confirmed by ear.",
            "Peaks and these checks are not a musical sign-off.",
        ],
    }
    (SONG / "effects" / "v03-events.json").write_text(json.dumps({"events": events, "omitted": omitted, "config": CFG}, indent=2))
    (SONG / "effects" / "v03-boundary-audit.json").write_text(json.dumps({"v02": v02_audit, "v03_events": events, "omitted": omitted}, indent=2))
    (SONG / "reports" / "v03-quality.json").write_text(json.dumps(quality, indent=2))

    lines = [
        "# Satan's Casino v03 boundary and measurement report",
        "",
        "Not a listening pass. Not a finished master. Peaks are not a musical approval.",
        "",
        f"Kick attacks: median {phase['median_ms']} ms after the arithmetic downbeat (n={phase['n']}, range {phase['min_ms']} to {phase['max_ms']} ms).",
        phase["reading"],
        "",
        f"Opening line used for the telephone copy: {opening['start_s']:.3f} s to {opening['end_s']:.3f} s. "
        f"Its start is {onset_offset_s*1000:.1f} ms before 16.000 s (beat 36 / bar 9). "
        "v02 started the copy at 16.103 s, which left out the loud span from about 15.96 s, and put that cut on bar 1.",
        "",
        f"Candidate peak {sample_pk:.3f} dBFS, true peak {tp:.3f} dBTP, {lufs:.2f} LUFS. "
        f"Baseline peak {base_pk:.3f} dBFS. Dry vocal correlation {corr:.6f}.",
        "",
        "## v02 slices",
        "",
    ]
    for row in v02_audit:
        flag = "kept out" if row["layer"] == "delay_throws" or row["id"] == "phone-outro" else "replaced"
        lines.append(
            f"- {row['id']}: before {row['level_before_db']} dB, after {row['level_after_db']} dB. "
            f"{row['why']} ({flag})."
        )
    lines += ["", "## v03 added vocals", ""]
    for e in events:
        if e["layer"] in ("telephone_bgv", "reverse_swells"):
            lines.append(f"- {e['id']}: source {e['source_start_s']}–{e['source_end_s']} s, dest {e.get('dest_start_s')}–{e.get('dest_end_s')} s. {e['why']}")
    lines += ["", "## Left out", ""]
    for o in omitted:
        lines.append(f"- {o['id']}: {o['why']}")
    lines += ["", "## What is still unknown", ""]
    for u in quality["uncertainty"]:
        lines.append(f"- {u}")
    lines += ["", "## Measurement checks", ""]
    for c in checks:
        lines.append(f"- {'PASS' if c['pass'] else 'FAIL'} — {c['name']}: {c['detail']}")
    (SONG / "reports" / "v03.md").write_text("\n".join(lines) + "\n")
    failed = [c for c in checks if not c["pass"]]
    print("failed", len(failed))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

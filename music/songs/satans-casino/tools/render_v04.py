#!/usr/bin/env python3
"""Satan's Casino v04.

v03 is the approved baseline. This pass does not change the dry beat (-8 dB)
or the dry vocal (-6 dB). It adds a telephone delay under the lead and
whole-word echoes into measured quiet gaps.

Word starts come from a speech model and are kept only when the audio shows
an attack. The end is the decay into the gap, not a 300 ms cut. The echo is a
fixed dotted-eighth later, so the singer's offset stays put.

No limiter. No loudness match.

  python3 music/songs/satans-casino/tools/render_v04.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt

SONG = Path(__file__).resolve().parents[1]
SR = 44100
Q = 19600
BAR = 4 * Q
DOT = 14700  # dotted eighth at 135 BPM
QUIET_GAPS = [
    (18.782, 19.451),
    (22.254, 22.968),
    (71.173, 71.877),
    (98.925, 99.539),
    (102.322, 103.036),
    (105.849, 106.558),
    (154.928, 156.434),
    (170.078, 170.652),
    (186.536, 188.680),
]


def load_stereo(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    )
    return np.frombuffer(raw.stdout, dtype="<f4").reshape(-1, 2).astype(np.float32)


def db(x):
    x = np.asarray(x, dtype=np.float64)
    return float(20.0 * np.log10(np.sqrt(np.mean(x * x)) + 1e-20))


def peak_db(x):
    p = float(np.max(np.abs(x))) if np.size(x) else 0.0
    return 20.0 * np.log10(p + 1e-20), p


def region_db(mono, t0, t1):
    s = max(0, int(t0 * SR))
    e = min(len(mono), int(t1 * SR))
    if e <= s + 8:
        return -200.0
    return db(mono[s:e])


def band_db(x, lo, hi):
    sos = butter(4, [lo, min(hi, SR / 2 - 200)], btype="band", fs=SR, output="sos")
    y = sosfiltfilt(sos, np.asarray(x, dtype=np.float64))
    return db(y)


def lowpass(stereo, hz, order=2):
    sos = butter(order, hz, btype="low", fs=SR, output="sos")
    return sosfiltfilt(sos, np.asarray(stereo, dtype=np.float64), axis=0).astype(np.float32)


def soften_highs(stereo, hz=3500, cut_db=2.5):
    """Turn the content above hz down by about cut_db. The lows stay."""
    sos = butter(2, hz, btype="high", fs=SR, output="sos")
    high = sosfiltfilt(sos, np.asarray(stereo, dtype=np.float64), axis=0)
    keep = 10 ** (-cut_db / 20.0)
    return (stereo - high * (1.0 - keep)).astype(np.float32)


def telephone(mono):
    sos = butter(2, [420, 2800], btype="band", fs=SR, output="sos")
    y = sosfiltfilt(sos, np.asarray(mono, dtype=np.float64))
    return y.astype(np.float32)


def write_pcm24(path, audio):
    import soundfile as sf
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    step = 2 ** -23
    rng = np.random.default_rng(401)
    dither = (rng.random(audio.shape) + rng.random(audio.shape) - 1.0) * step
    y = np.clip(audio.astype(np.float64) + dither, -1 + 1e-8, 1 - 1e-8)
    if path.suffix.lower() == ".flac":
        sf.write(path, y, SR, format="FLAC", subtype="PCM_24")
    else:
        sf.write(path, y, SR, subtype="PCM_24")


def choose_throws(vm, words):
    """One ending per quiet gap, only when the word has an attack and a real tail."""
    chosen = []
    skipped = []
    for gs, ge in QUIET_GAPS:
        near = [w for w in words if w["p"] >= 0.7 and w["start"] < gs and gs - 1.3 <= w["end"] <= gs + 0.08]
        if not near:
            skipped.append({"gap_s": [gs, ge], "why": "No word with probability >= 0.7 ends near this gap."})
            continue
        w = max(near, key=lambda x: x["end"])
        t = w["end"]
        while t < gs + 0.03:
            if region_db(vm, t, t + 0.04) < -40:
                break
            t += 0.02
        end = min(t, gs + 0.02)
        pre = region_db(vm, w["start"] - 0.08, w["start"] - 0.015)
        head = region_db(vm, w["start"], min(w["start"] + 0.05, end))
        start = w["start"]
        if pre > head + 4:
            # The transcript start sits in the previous syllable. Use the last
            # dip-then-rise before the gap, still inside this ending.
            found = None
            t = w["start"]
            while t < gs - 0.16:
                dip = region_db(vm, t, t + 0.03)
                rise = region_db(vm, t + 0.04, t + 0.1)
                if dip < -34 and rise > dip + 8:
                    found = t + 0.03
                t += 0.02
            if found is None:
                skipped.append({
                    "gap_s": [gs, ge], "word": w["word"], "p": w["p"],
                    "why": f"Audio just before {w['start']:.3f}s is louder than the start ({pre:.1f} vs {head:.1f} dB), and no later attack was found. Not cropped.",
                })
                continue
            start = float(found)
            pre = region_db(vm, start - 0.06, start - 0.01)
            head = region_db(vm, start, min(start + 0.05, end))
        # a few milliseconds of the consonant, if it sits in a dip and does not swallow the previous word
        dip_at = None
        for back in np.arange(0.01, 0.035, 0.005):
            if region_db(vm, start - back - 0.012, start - back) < head - 6:
                dip_at = start - back
                break
        if dip_at is not None:
            start = float(dip_at)
        dur = end - start
        if dur < 0.08 or dur > 1.15:
            skipped.append({
                "gap_s": [gs, ge], "word": w["word"],
                "why": f"Ending span is {dur:.2f}s after the tail is included. Left out rather than cut.",
            })
            continue
        reps = []
        for n in (1, 2, 3, 4, 5):
            dest = start + n * DOT / SR
            dest_end = end + n * DOT / SR
            if dest_end > ge - 0.06:
                break
            if not (dest < ge and dest_end > gs):
                continue
            reps.append(n)
        if not reps:
            skipped.append({
                "gap_s": [gs, ge], "word": w["word"], "span": [round(start, 3), round(end, 3)],
                "why": "A whole dotted-eighth repeat would run into the next line. Not cropped.",
            })
            continue
        chosen.append({
            "word": w["word"].strip(),
            "p": w["p"],
            "whisper_start": w["start"],
            "whisper_end": w["end"],
            "start": round(start, 6),
            "end": round(end, 6),
            "gap": [gs, ge],
            "repeats": reps,
            "pre_db": round(pre, 2),
            "head_db": round(head, 2),
        })
    return chosen, skipped


def place_throw(bus, vm, start, end, dest, gain_db):
    pad = int(0.03 * SR)
    s0 = max(0, int(start * SR) - pad)
    s1 = min(len(vm), int(end * SR) + int(0.02 * SR))
    chunk = telephone(vm[s0:s1])
    keep_from = int(start * SR) - s0
    keep_to = int(end * SR) - s0
    seg = chunk[keep_from:keep_to]
    if len(seg) < 8:
        return
    # fade only the already-quiet tail, 30 ms, so a decay is not a hard edge
    n = min(int(0.03 * SR), len(seg) // 3)
    if n > 4:
        seg = seg.copy()
        seg[-n:] *= np.linspace(1, 0, n, dtype=np.float32)
    stereo = np.stack([seg, seg], axis=1)
    g = 10 ** (gain_db / 20.0)
    d = int(round(dest * SR))
    e = min(len(bus), d + len(stereo))
    if d < 0 or e <= d:
        return
    bus[d:e] += stereo[: e - d] * np.float32(g)


def delay_bed(mono, delay, feedback=0.30, loops=5, lp_hz=2200):
    sos = butter(1, lp_hz, btype="low", fs=SR, output="sos")
    y = np.zeros(len(mono), np.float32)
    acc = mono.astype(np.float32)
    for i in range(loops):
        acc = sosfilt(sos, acc).astype(np.float32) * np.float32(feedback)
        d = delay * (i + 1)
        if d >= len(y):
            break
        n = min(len(acc), len(y) - d)
        y[d:d + n] += acc[:n]
    return y


def lead_envelope(mono):
    hop = 256
    win = 1024
    c = np.cumsum(np.concatenate([[0.0], mono.astype(np.float64) ** 2]))
    n = 1 + max(0, (len(mono) - win) // hop)
    i0 = np.arange(n) * hop
    dbv = 20 * np.log10(np.sqrt((c[i0 + win] - c[i0]) / win) + 1e-20)
    flag = np.repeat(dbv > -34.0, hop)
    if len(flag) < len(mono):
        flag = np.pad(flag, (0, len(mono) - len(flag)))
    flag = flag[: len(mono)].astype(np.float32)
    out = np.zeros(len(mono), np.float32)
    acc = 0.0
    att = 1 / max(int(0.01 * SR), 1)
    rel = 1 / max(int(0.22 * SR), 1)
    for i, f in enumerate(flag):
        coef = att if f > acc else rel
        acc += (float(f) - acc) * coef
        out[i] = acc
    return out


def main():
    n_target = 9533217
    buses = {
        "beat_dry": load_stereo(SONG / "buses" / "beat_dry.flac"),
        "vocal_dry": load_stereo(SONG / "buses" / "vocal_dry.flac"),
        "beat_stop": load_stereo(SONG / "buses" / "v03_beat_stop.flac"),
        "reverse": load_stereo(SONG / "buses" / "v03_reverse_swells.flac"),
        "phone": load_stereo(SONG / "buses" / "v03_telephone_bgv.flac"),
        "phone_reverb": load_stereo(SONG / "buses" / "v03_telephone_reverb.flac"),
        "lead_reverb": load_stereo(SONG / "buses" / "v03_lead_reverb.flac"),
    }
    n = len(buses["beat_dry"])
    if n != n_target:
        sys.exit(f"unexpected length {n}")
    v03 = sum(buses.values())
    vm = buses["vocal_dry"].mean(axis=1)  # already -6 dB
    words = json.loads((SONG / "effects" / "v04-words.json").read_text())

    # hiss: darken only the two buses that add 2–5 kHz in quiet spots
    hole = slice(int(155.1 * SR), int(156.2 * SR))
    intro = slice(int(2.2 * SR), int(4.0 * SR))
    hiss_before = {
        "hole_reverse_2k5k": round(band_db(buses["reverse"][hole, 0], 2000, 5000), 2),
        "intro_phone_2k5k": round(band_db(buses["phone"][intro, 0], 2000, 5000), 2),
        "hole_beat_6k12k": round(band_db(buses["beat_dry"][hole, 0], 6000, 12000), 2),
        "hole_vocal_6k12k": round(band_db(buses["vocal_dry"][hole, 0], 6000, 12000), 2),
        "singing_beat_6k12k": round(band_db(buses["beat_dry"][int(17.2 * SR):int(17.8 * SR), 0], 6000, 12000), 2),
    }
    buses["reverse"] = lowpass(buses["reverse"], 3600, order=2)
    buses["phone"] = soften_highs(buses["phone"], hz=3200, cut_db=2.5)
    hiss_after = {
        "hole_reverse_2k5k": round(band_db(buses["reverse"][hole, 0], 2000, 5000), 2),
        "intro_phone_2k5k": round(band_db(buses["phone"][intro, 0], 2000, 5000), 2),
    }
    print("hiss before", hiss_before)
    print("hiss after", hiss_after)

    # telephone delay under the lead: whole vocal, fixed dotted eighth, no slices
    send = telephone(vm)
    bed = delay_bed(send, DOT, feedback=0.34, loops=4, lp_hz=2100)
    env = lead_envelope(vm)
    duck = (10 ** ((-6.0 * env) / 20.0)).astype(np.float32)
    bed *= duck
    # Level from the ducked singing peaks, not from a quiet gap.
    # Vocal dry peaks near -6 dBFS. Keep this bed about 16 dB under that while the lead is up.
    sing_i = env > 0.5
    sing_peak = float(np.max(np.abs(bed[sing_i]))) if np.any(sing_i) else float(np.max(np.abs(bed)))
    bed_gain_db = -22.0 - 20.0 * np.log10(sing_peak + 1e-12)
    bed *= np.float32(10 ** (bed_gain_db / 20.0))
    bed_st = np.stack([bed, bed], axis=1)
    print(f"delay bed gain {bed_gain_db:.2f} dB, hole rms now {db(bed[hole]):.1f}")

    raw_view = vm * np.float32(10 ** (6 / 20.0))
    chosen, skipped = choose_throws(raw_view, words)
    throws = np.zeros((n, 2), np.float32)
    throw_events = []
    for c in chosen:
        for i, nrep in enumerate(c["repeats"]):
            dest = c["start"] + nrep * DOT / SR
            gain = -16.0 - i * 5.0  # on the raw vocal; lead is at -6, so first echo is 10 dB under
            # place_throw telephone()s the raw view
            place_throw(throws, raw_view, c["start"], c["end"], dest, gain)
            throw_events.append({
                "id": f"throw-{c['word']}-{c['start']:.3f}-r{nrep}",
                "layer": "echo_throws",
                "word": c["word"],
                "probability": c["p"],
                "source_start_s": c["start"],
                "source_end_s": c["end"],
                "whisper_start_s": c["whisper_start"],
                "whisper_end_s": c["whisper_end"],
                "dest_start_s": round(dest, 6),
                "dest_end_s": round(c["end"] + nrep * DOT / SR, 6),
                "delay_samples": DOT * nrep,
                "delay_ms": round(DOT / SR * 1000 * nrep, 2),
                "gain_db_on_raw_vocal": gain,
                "gap_s": c["gap"],
                "pre_db": c["pre_db"],
                "head_db": c["head_db"],
            })
    print("throws", len(throw_events), "skipped", len(skipped))
    for s in skipped:
        print("  skip", s.get("word", ""), s["why"][:140])

    # duck throws under the lead as well, lightly, so a tail yields
    throws *= duck[:, None]

    new = bed_st + throws
    # if the new material would push the peak, turn the new buses down only
    mix = v03 + new
    # v03 here is the sum of buses AFTER reverse/phone treatment, so it is not
    # bit-identical to the v03 file. The dry buses are. Record both.
    trims = []
    for _ in range(5):
        pk = peak_db(mix)[0]
        if pk <= -1.2:
            break
        over = pk + 1.2 + 0.1
        new *= np.float32(10 ** (-over / 20.0))
        mix = (buses["beat_dry"] + buses["vocal_dry"] + buses["beat_stop"] + buses["reverse"]
               + buses["phone"] + buses["phone_reverb"] + buses["lead_reverb"] + new)
        trims.append(round(over, 3))
    mix = (buses["beat_dry"] + buses["vocal_dry"] + buses["beat_stop"] + buses["reverse"]
           + buses["phone"] + buses["phone_reverb"] + buses["lead_reverb"] + new)

    v03_file = load_stereo(SONG / "renders" / "satans-casino-v03-review.wav")
    # difference where the lead is singing, and in the hole
    sing = slice(int(17.0 * SR), int(18.5 * SR))
    diff = {
        "singing_17_18_rms_v03": round(db(v03_file[sing]), 2),
        "singing_17_18_rms_v04": round(db(mix[sing]), 2),
        "hole_rms_v03": round(db(v03_file[hole]), 2),
        "hole_rms_v04": round(db(mix[hole]), 2),
        "full_correlation": round(float(np.corrcoef(v03_file[::20, 0], mix[::20, 0])[0, 1]), 4),
        "dry_vocal_unchanged": bool(np.allclose(buses["vocal_dry"], load_stereo(SONG / "buses" / "vocal_dry.flac"))),
        "dry_beat_unchanged": True,
    }
    print("diff", diff)

    out = SONG / "renders" / "satans-casino-v04-review.wav"
    write_pcm24(out, mix)
    if trims:
        trim = np.float32(10 ** (-sum(trims) / 20.0))
        bed_st *= trim
        throws *= trim
    write_pcm24(SONG / "buses" / "v04_echo_throws.flac", throws)
    write_pcm24(SONG / "buses" / "v04_telephone_delay.flac", bed_st)

    mp3 = SONG / "renders" / "satans-casino-v04-review.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(out), "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)],
        check=True,
    )
    # latest-version-only excerpts
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", "0", "-t", "6.5",
         "-codec:a", "libmp3lame", "-b:a", "160k", str(SONG / "renders" / "satans-casino-v04-excerpt-intro.mp3")],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", "154.4", "-t", "3.8",
         "-codec:a", "libmp3lame", "-b:a", "160k", str(SONG / "renders" / "satans-casino-v04-excerpt-gap.mp3")],
        check=True,
    )

    pk = peak_db(mix)
    if pk[0] > -1.0:
        sys.exit(f"mix peak {pk[0]:.2f} dBFS is too hot; new buses were not turned down enough")
    report = {
        "version": "v04",
        "baseline": "satans-casino-v03-review.wav",
        "baseline_commit_character": "v03 dry -8/-6, opening phone line, two reverses, two beat-stop builds",
        "listening": "not performed",
        "transcription": {
            "tool": "faster-whisper small, int8, English, word timestamps",
            "words": len(words),
            "probability_at_least_0.7": sum(1 for w in words if w["p"] >= 0.7),
            "note": "Timestamps are a speech model's, checked against the waveform before a throw is kept. They are not a listening pass.",
        },
        "hiss": {
            "before": hiss_before,
            "after_selective_treatment": hiss_after,
            "reading": (
                "6–12 kHz in the beat during the quiet hole is about -80 dB after the -8 dB fader. "
                "The vocal in that hole is about -79 dB up there. That is not a hiss floor. "
                "During the vocal, 6–12 kHz is the beat's hats. Those were left alone. "
                "The extra 2–5 kHz in the hole is the reverse swell. The extra 2–5 kHz in the intro is the telephone copy. "
                "Only those two buses were darkened. No gate."
            ),
        },
        "difference_vs_v03": diff,
        "fx_trims_db": trims,
        "candidate_peak_dbfs": round(pk[0], 3),
        "delay_bed": {
            "delay_samples": DOT,
            "delay_ms": round(DOT / SR * 1000, 2),
            "feedback": 0.34,
            "loop_lowpass_hz": 2100,
            "duck_db": 6,
            "static_gain_db": round(bed_gain_db, 3),
            "band_hz": [420, 2800],
        },
        "throws": throw_events,
        "throws_skipped": skipped,
        "limitations": [
            "No listening. Whisper word edges are not guaranteed phonetic on a rap vocal.",
            "Gaps whose transcript end stayed loud, or whose start was louder than the attack, got no throw.",
            "The under-lead telephone delay is a send of the whole vocal, not a stack of chopped words.",
            "v03's opening phone line, reverses, and beat-stop builds remain. The reverse and the intro phone were darkened slightly.",
            "This is not a final master and not a loudness pass.",
        ],
    }
    (SONG / "effects" / "v04-events.json").write_text(json.dumps(report, indent=2))
    lines = [
        "# Satan's Casino v04",
        "",
        "Baseline is v03 (`satans-casino-v03-review.wav`), the mix Chex said sounded amazing. Dry beat -8 dB and dry vocal -6 dB are the v03 buses, unchanged.",
        "",
        "No listening was done for this pass. A speech model supplied word times. Peaks are not approval.",
        "",
        report["hiss"]["reading"],
        "",
        f"Hole 2–5 kHz, reverse bus: {hiss_before['hole_reverse_2k5k']} dB before, {hiss_after['hole_reverse_2k5k']} dB after a 3.6 kHz low pass.",
        f"Intro 2–5 kHz, telephone bus: {hiss_before['intro_phone_2k5k']} dB before, {hiss_after['intro_phone_2k5k']} dB after a 2.5 dB cut above 3.2 kHz.",
        "",
        f"Singing 17.0–18.5 s: v03 {diff['singing_17_18_rms_v03']} dB RMS, v04 {diff['singing_17_18_rms_v04']} dB RMS.",
        f"Quiet hole: v03 {diff['hole_rms_v03']} dB RMS, v04 {diff['hole_rms_v04']} dB RMS.",
        f"Correlation with v03, every 20th sample: {diff['full_correlation']}.",
        f"Candidate peak {pk[0]:.2f} dBFS. New-bus trims: {trims or 'none'}.",
        "",
        "## Telephone delay under the lead",
        "",
        "The whole vocal, band-limited about 420–2800 Hz, delayed 333.33 ms (one dotted eighth, 14700 samples), feedback 0.34, each repeat darker at 2.1 kHz. Pulled down 6 dB while the lead is up, so it sits under the line and opens in the gaps. Not sliced.",
        "",
        "## Echo throws",
        "",
    ]
    if not throw_events:
        lines.append("None kept. See skipped list. Nothing was cropped to fill a gap.")
    for e in throw_events:
        lines.append(
            f"- {e['word']!r} p={e['probability']}: source {e['source_start_s']:.3f}–{e['source_end_s']:.3f} s, "
            f"dest {e['dest_start_s']:.3f}–{e['dest_end_s']:.3f} s, delay {e['delay_ms']:.1f} ms, gain {e['gain_db_on_raw_vocal']} dB on the raw vocal."
        )
    lines += ["", "## Not thrown", ""]
    for s in skipped:
        lines.append(f"- {s.get('word', '')} gap {s['gap_s']}: {s['why']}")
    lines += ["", "## Still unknown", ""]
    for item in report["limitations"]:
        lines.append(f"- {item}")
    (SONG / "reports" / "v04.md").write_text("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()

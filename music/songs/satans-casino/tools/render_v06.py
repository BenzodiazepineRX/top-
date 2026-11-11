#!/usr/bin/env python3
"""Satan's Casino v06.

v06 is not verified. This pass keeps the one-copy, no-feedback shape and the
v03 dry buses. It does not treat a later energy rise as a word, and it does
not boost a quiet word up to a target peak.

Linguistic status is marked on every event. Nothing here was listened to.

v04 is not the approved mix. v03 is the dry mix that was liked. This pass
keeps that, keeps the small hiss darkening, and replaces v04's feedback wash.

Two separate jobs:
  1. Each trustworthy line is repeated once, one bar later, quieter, telephone.
  2. Only the last word of a line is echoed, fading, and those copies start
     after the word has finished so they land in the pause.

No limiter.

  python3 music/songs/satans-casino/tools/render_v06.py
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SONG = Path(__file__).resolve().parents[1]
SR = 44100
Q = 19600
BAR = 4 * Q
DOT = 14700  # dotted eighth, 333.33 ms
INTRO_SHIFT = -8 * BAR

_spec = importlib.util.spec_from_file_location("sc_v04", Path(__file__).with_name("render_v04.py"))
v4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v4)


def sec(samples):
    return samples / SR


def region(mono, t0, t1):
    return v4.region_db(mono, t0, t1)


def reliable_lines(words):
    rel = [w for w in words if w["p"] >= 0.7]
    lines = []
    cur = [rel[0]]
    for a, b in zip(rel, rel[1:]):
        if b["start"] - a["end"] > 0.35:
            lines.append(cur)
            cur = [b]
        else:
            cur.append(b)
    lines.append(cur)
    return lines


def extend_tail(mono, start_end, limit):
    """Move the end through a decay. Stop if a new attack rises."""
    t = start_end
    while t < limit - 0.03:
        cur = region(mono, t, t + 0.03)
        nxt = region(mono, t + 0.035, t + 0.08)
        if cur < -40:
            break
        if cur < -32 and nxt > cur + 8:
            break
        t += 0.02
    return min(t, limit - 0.01)


def last_word_span(mono, word, limit):
    """Verified span for the final word. Model times are a lead, not the truth."""
    flags = []
    w0, w1 = word["start"], word["end"]
    pre = region(mono, w0 - 0.08, w0 - 0.015)
    head = region(mono, w0, min(w0 + 0.05, limit))
    # Always the model's own start. A later energy rise is not a new word boundary.
    start = w0
    flags.append(
        f"source starts at the model token {w0:.3f}s. Level in the 80 ms before is {pre:.1f} dB "
        f"and the first 50 ms is {head:.1f} dB. A loud neighbour can be the previous word; "
        "this was not phonetically aligned."
    )
    end = extend_tail(mono, max(w1, start + 0.06), limit)
    if end - w1 > 0.12:
        mid = region(mono, w1, min(end, w1 + 0.2))
        later = region(mono, end - 0.06, end)
        flags.append(
            f"model end {w1:.3f}s still has level {mid:.1f} dB, then it falls to {later:.1f} dB by {end:.3f}s. "
            f"Next trusted word is {limit:.3f}s, so this is the rest of the word, not the next one."
        )
    if end < w1 - 0.02:
        flags.append(f"model end {w1:.3f}s was past a new attack; stopped at {end:.3f}s")
    return start, end, flags


def place(bus, mono_seg, dest_s, gain_db, fade_out_s=0.04):
    if mono_seg is None or len(mono_seg) < 8:
        return
    seg = np.asarray(mono_seg, dtype=np.float32).copy()
    nfade = min(int(fade_out_s * SR), len(seg) // 2)
    if nfade > 4:
        seg[-nfade:] *= np.linspace(1, 0, nfade, dtype=np.float32)
    stereo = np.stack([seg, seg], axis=1) * np.float32(10 ** (gain_db / 20.0))
    d = int(round(dest_s * SR))
    if d < 0:
        stereo = stereo[-d:]
        d = 0
    e = min(len(bus), d + len(stereo))
    if e <= d:
        return
    bus[d:e] += stereo[: e - d]


def filtered_span(mono, start, end):
    pad = int(0.025 * SR)
    s0 = max(0, int(start * SR) - pad)
    s1 = min(len(mono), int(end * SR))
    y = v4.telephone(mono[s0:s1])
    a = int(start * SR) - s0
    b = int(end * SR) - s0
    return y[a:b]


def audible_return(mono, after, nxt):
    t = after + 0.04
    while t < nxt:
        if region(mono, t, t + 0.03) > -30:
            return t
        t += 0.02
    return nxt


def schedule_echoes(start, end, limit):
    """Dotted-eighth taps that begin after this word, spaced so they do not stack on it."""
    dur = end - start
    step = max(1, int(np.ceil((dur - 0.02) / sec(DOT))))
    taps = []
    k = step
    while len(taps) < 4 and k <= step * 6:
        dest = start + k * sec(DOT)
        dest_end = end + k * sec(DOT)
        if dest < end - 0.01 or dest > limit - 0.12:
            break
        fade = 0.04
        if dest_end > limit - 0.04:
            room = (limit - 0.05) - dest
            if room < 0.6 * dur:
                break
            fade = max(0.04, dest_end - (limit - 0.05))
        taps.append({
            "n": k,
            "dest_start_s": round(dest, 6),
            "dest_end_s": round(min(dest_end, limit - 0.02), 6),
            "delay_samples": DOT * k,
            "delay_ms": round(k * sec(DOT) * 1000, 2),
            "fade_out_s": round(fade, 3),
        })
        k += step
    return taps


def gain_for_peak(seg, target_db):
    pk = v4.peak_db(seg)[0]
    return target_db - pk


def main():
    words = json.loads((SONG / "effects" / "v04-words.json").read_text())
    raw = v4.load_stereo(SONG / "sources" / "satans-casino-lead-vocals.flac").mean(axis=1)
    buses = {
        "beat_dry": v4.load_stereo(SONG / "buses" / "beat_dry.flac"),
        "vocal_dry": v4.load_stereo(SONG / "buses" / "vocal_dry.flac"),
        "beat_stop": v4.load_stereo(SONG / "buses" / "v03_beat_stop.flac"),
        "reverse": v4.load_stereo(SONG / "buses" / "v03_reverse_swells.flac"),
        "phone": v4.load_stereo(SONG / "buses" / "v03_telephone_bgv.flac"),
        "phone_reverb": v4.load_stereo(SONG / "buses" / "v03_telephone_reverb.flac"),
        "lead_reverb": v4.load_stereo(SONG / "buses" / "v03_lead_reverb.flac"),
    }
    n = len(buses["beat_dry"])
    hole = slice(int(155.1 * SR), int(156.2 * SR))
    intro = slice(int(2.2 * SR), int(4.0 * SR))
    hiss_before = {
        "hole_reverse_2k5k": round(v4.band_db(buses["reverse"][hole, 0], 2000, 5000), 2),
        "intro_phone_2k5k": round(v4.band_db(buses["phone"][intro, 0], 2000, 5000), 2),
    }
    buses["reverse"] = v4.lowpass(buses["reverse"], 3600, order=2)
    buses["phone"] = v4.soften_highs(buses["phone"], hz=3200, cut_db=2.5)
    hiss_after = {
        "hole_reverse_2k5k": round(v4.band_db(buses["reverse"][hole, 0], 2000, 5000), 2),
        "intro_phone_2k5k": round(v4.band_db(buses["phone"][intro, 0], 2000, 5000), 2),
    }

    lines = reliable_lines(words)
    line_bus = np.zeros((n, 2), np.float32)
    echo_bus = np.zeros((n, 2), np.float32)
    line_events = []
    echo_events = []
    skipped_lines = []
    skipped_echoes = []

    # opening line: transcript's first words are low probability, but the
    # silence before 15.954 s and the decay after "alcohol" are measured.
    opening_start = 15.954
    opening_last = lines[0][-1]
    opening_end, _ = None, None
    opening_end = extend_tail(raw, opening_last["end"], lines[1][0]["start"])

    prepared = []
    for i, ln in enumerate(lines):
        nxt = lines[i + 1][0]["start"] if i + 1 < len(lines) else len(raw) / SR
        pause = nxt - ln[-1]["end"]
        if i == 0:
            start = opening_start
            end = opening_end
        else:
            start = ln[0]["start"]
            end = extend_tail(raw, ln[-1]["end"], nxt)
        dur = end - start
        prepared.append({
            "i": i, "words": ln, "start": start, "end": end, "dur": dur,
            "next": nxt, "pause": pause, "last": ln[-1],
        })

    for item in prepared:
        dur = item["dur"]
        if dur > 6.0 or len(item["words"]) <= 2 or dur < 1.0:
            skipped_lines.append({
                "line": item["i"],
                "text": "".join(w["word"] for w in item["words"]).strip(),
                "n_words": len(item["words"]),
                "start": round(item["start"], 3),
                "end": round(item["end"], 3),
                "needs": "a supplied lyric line and its timing",
                "why": (
                    f"{len(item['words'])} trusted words, {dur:.2f}s. "
                    "A pause in the transcript is not a lyric line. Not rendered."
                ),
            })
            continue
        seg = filtered_span(raw, item["start"], item["end"])
        g = -16.0  # fixed, on the raw vocal. No peak makeup.
        dest = item["start"] + sec(BAR)
        place(line_bus, seg, dest, g, fade_out_s=0.05)
        line_events.append({
            "id": f"line-{item['i']:02d}",
            "layer": "full_line_once",
            "repeat_count": 1,
            "text": "".join(w["word"] for w in item["words"]).strip(),
            "n_words": len(item["words"]),
            "source_start_s": round(item["start"], 6),
            "source_end_s": round(item["end"], 6),
            "dest_start_s": round(dest, 6),
            "dest_end_s": round(dest + dur, 6),
            "shift_samples": BAR,
            "shift_ms": round(sec(BAR) * 1000, 2),
            "gain_db_on_raw_vocal": g,
            "boundary_status": "unverified lyric line; pause-grouped transcript words, not a supplied lyric",
            "onset_offset_preserved": True,
        })

        # last word only, into the pause after the line
        word = item["last"]
        limit = min(item["next"], audible_return(raw, item["end"], item["next"]))
        w_start, w_end, flags = last_word_span(raw, word, limit)
        if w_end - w_start < 0.08:
            skipped_echoes.append({"line": item["i"], "word": word["word"], "why": "Last word span is under 80 ms."})
            continue
        if item["pause"] < 0.4 and item["i"] != 0:
            skipped_echoes.append({
                "line": item["i"], "word": word["word"],
                "why": f"Pause after the line is {item['pause']:.2f}s. No gap long enough for a fading echo. The full-line repeat is separate and was not used as a substitute.",
            })
            continue
        word_audio = filtered_span(raw, w_start, w_end)
        base_gain = -14.0  # fixed on the raw vocal. A quiet word is not turned up.
        taps = schedule_echoes(w_start, w_end, limit)
        for i, tap in enumerate(taps):
            g_tap = base_gain - 5.0 * i
            place(echo_bus, word_audio, tap["dest_start_s"], g_tap, fade_out_s=tap["fade_out_s"])
            tap["gain_db"] = round(g_tap, 3)
        if not taps:
            skipped_echoes.append({
                "line": item["i"], "word": word["word"], "flags": flags,
                "why": "No dotted-eighth multiple puts the copy after the word and inside the pause.",
            })
            continue
        echo_events.append({
            "id": f"lastword-L{item['i']:02d}",
            "layer": "last_word_echoes",
            "word": word["word"].strip(),
            "probability": word["p"],
            "model_start_s": word["start"],
            "model_end_s": word["end"],
            "source_start_s": round(w_start, 6),
            "source_end_s": round(w_end, 6),
            "boundary_status": "model token plus decay; not phonetically aligned",
            "alignment_flags": flags,
            "pause_after_model_end_s": round(item["pause"], 3),
            "taps": taps,
        })

        if item["i"] == 0:
            # same last word, on the opening telephone copy, then fading echoes
            intro_start = w_start + sec(INTRO_SHIFT)
            intro_end = w_end + sec(INTRO_SHIFT)
            intro_taps = schedule_echoes(intro_start, intro_end, 13.2)
            for i, tap in enumerate(intro_taps):
                g_tap = base_gain - 5.0 * i
                place(echo_bus, word_audio, tap["dest_start_s"], g_tap, fade_out_s=tap["fade_out_s"])
                tap["gain_db"] = round(g_tap, 3)
            echo_events.append({
                "id": "opening-telephone-last-word",
                "layer": "opening_telephone_last_word_echoes",
                "word": word["word"].strip(),
                "source_start_s": round(w_start, 6),
                "source_end_s": round(w_end, 6),
                "intro_word_start_s": round(intro_start, 6),
                "intro_word_end_s": round(intro_end, 6),
                "intro_shift_samples": INTRO_SHIFT,
                "boundary_status": "same alcohol token as the lead echo; opening copy only. Not phonetically aligned.",
                "alignment_flags": flags,
                "taps": intro_taps,
                "why": "Explicit echoes of the opening telephone line's last word, same recording, shifted with that line, then whole dotted eighths.",
            })

    mix = (buses["beat_dry"] + buses["vocal_dry"] + buses["beat_stop"] + buses["reverse"]
           + buses["phone"] + buses["phone_reverb"] + buses["lead_reverb"]
           + line_bus + echo_bus)
    pk = v4.peak_db(mix)
    trims = []
    if pk[0] > -1.2:
        over = pk[0] + 1.2 + 0.15
        scale = np.float32(10 ** (-over / 20.0))
        line_bus *= scale
        echo_bus *= scale
        trims.append(round(over, 3))
        mix = (buses["beat_dry"] + buses["vocal_dry"] + buses["beat_stop"] + buses["reverse"]
               + buses["phone"] + buses["phone_reverb"] + buses["lead_reverb"]
               + line_bus + echo_bus)
        pk = v4.peak_db(mix)
    if pk[0] > -1.0:
        sys.exit(f"peak {pk[0]:.2f} dBFS")

    v03 = v4.load_stereo(SONG / "renders" / "satans-casino-v03-review.wav")
    sing = slice(int(17.0 * SR), int(18.5 * SR))
    diff = {
        "singing_rms_v03": round(v4.db(v03[sing]), 2),
        "singing_rms_v06": round(v4.db(mix[sing]), 2),
        "correlation": round(float(np.corrcoef(v03[::25, 0], mix[::25, 0])[0, 1]), 4),
    }
    print("lines", len(line_events), "echo groups", len(echo_events), "peak", round(pk[0], 2), "diff", diff)
    print("skipped lines", len(skipped_lines), "skipped echoes", len(skipped_echoes))

    out = SONG / "renders" / "satans-casino-v06-review.wav"
    v4.write_pcm24(out, mix)
    v4.write_pcm24(SONG / "buses" / "v06_full_line_once.flac", line_bus)
    v4.write_pcm24(SONG / "buses" / "v06_last_word_echoes.flac", echo_bus)
    mp3 = SONG / "renders" / "satans-casino-v06-review.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", "0", "-t", "6.5",
                    "-codec:a", "libmp3lame", "-b:a", "160k",
                    str(SONG / "renders" / "satans-casino-v06-excerpt-intro.mp3")], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", "17.4", "-t", "2.4",
                    "-codec:a", "libmp3lame", "-b:a", "160k",
                    str(SONG / "renders" / "satans-casino-v06-excerpt-gap.mp3")], check=True)

    # alcohol and 15k notes for the audit
    alcohol = next(e for e in echo_events if e["id"] == "lastword-L00")
    notes_15k = [e for e in echo_events if "15k" in e["word"]]
    audit = {
        "version": "v06",
        "baseline": "v03 satans-casino-v03-review.wav plus the same selective hiss darkening as measured on the reverse and intro phone",
        "v04_status": "not approved; its feedback delay is not in this render",
        "listening": "not performed",
        "lyric_check": "not performed; word text is a speech model's guess and was not corrected",
        "full_line_repeat_count_each": 1,
        "full_line_shift": "exactly 1 bar, 78400 samples, 1777.78 ms",
        "echo_interval": "dotted eighth, 14700 samples, 333.33 ms, first tap is the smallest multiple that starts after the word ends",
        "hiss_before": hiss_before,
        "hiss_after": hiss_after,
        "difference_vs_v03": diff,
        "peak_dbfs": round(pk[0], 3),
        "trims_db": trims,
        "full_lines": line_events,
        "last_word_echoes": echo_events,
        "skipped_lines": skipped_lines,
        "skipped_echoes": skipped_echoes,
        "alcohol_verification": {
            "model": [opening_last["start"], opening_last["end"]],
            "used": [alcohol["source_start_s"], alcohol["source_end_s"]],
            "waveform": "Loud again from 18.08 to about 18.28, then falling through 18.56. Next trusted word is at 19.66 s. The extension is the rest of that word, not the next line.",
            "flags": alcohol["alignment_flags"],
        },
        "word_15k_verification": [
            {
                "id": e["id"],
                "model": [e["model_start_s"], e["model_end_s"]],
                "used": [e["source_start_s"], e["source_end_s"]],
                "flags": e["alignment_flags"],
            }
            for e in notes_15k
        ],
        "opening_telephone_last_word": next(e for e in echo_events if e["id"] == "opening-telephone-last-word"),
    }
    (SONG / "effects" / "v06-events.json").write_text(json.dumps(audit, indent=2))
    lines_md = [
        "# Satan's Casino v06",
        "",
        "Baseline is v03. v04 is not approved and its multi-repeat delay is not in this file. No listening was done. The lyric text is the speech model's, not a checked lyric.",
        "",
        f"Full-line backing repeats: {len(line_events)}, each exactly once, one bar later. Last-word echo groups: {len([e for e in echo_events if e['id']!='opening-telephone-last-word'])}, plus the opening telephone last word.",
        f"Singing 17–18.5 s: v03 {diff['singing_rms_v03']} dB RMS, v06 {diff['singing_rms_v06']} dB. Correlation {diff['correlation']}. Peak {pk[0]:.2f} dBFS.",
        "",
        "Alcohol: the model says 17.740–18.080 s. The waveform is loud again until about 18.28 s and decays by 18.56 s. The next trusted word is at 19.66 s, so that extension is not the next line.",
        "",
        "15k is the model's whole token, starting at 153.66 s, not the later rise at 154.24 s. The tail is only the fall after that token. It is not a phonetically aligned word. Short pause-splits are not rendered as lines; those need a supplied lyric and timing.",
        "",
        "## Full lines (one repeat)",
        "",
    ]
    for e in line_events:
        lines_md.append(
            f"- {e['id']} {e['source_start_s']:.3f}–{e['source_end_s']:.3f}s → {e['dest_start_s']:.3f}s, "
            f"shift {e['shift_ms']:.0f} ms, repeats {e['repeat_count']}, fixed gain {e['gain_db_on_raw_vocal']:.1f} dB on the raw vocal. {e['boundary_status']}."
        )
    lines_md += ["", "## Last-word echoes", ""]
    for e in echo_events:
        tap_s = ", ".join(f"{t['dest_start_s']:.3f}s ({t['delay_ms']:.0f} ms, {t['gain_db']:.1f} dB, fade {t['fade_out_s']:.2f}s)" for t in e["taps"])
        lines_md.append(
            f"- {e['id']} {e['word']!r} source {e['source_start_s']:.3f}–{e['source_end_s']:.3f}s "
            f"(model {e.get('model_start_s', e['source_start_s']):.3f}–{e.get('model_end_s', e['source_end_s']):.3f}s). Taps: {tap_s}."
        )
        for fl in e.get("alignment_flags") or []:
            lines_md.append(f"  - flag: {fl}")
    lines_md += ["", "## Not used", ""]
    for s in skipped_lines + skipped_echoes:
        lines_md.append(f"- {s.get('word','')} line {s.get('line')}: {s['why']}")
    (SONG / "reports" / "v06.md").write_text("\n".join(lines_md) + "\n")
    print("opening taps", len(audit["opening_telephone_last_word"]["taps"]))
    print("alcohol", audit["alcohol_verification"]["used"])


if __name__ == "__main__":
    main()

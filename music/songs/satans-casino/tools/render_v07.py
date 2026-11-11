#!/usr/bin/env python3
"""Satan's Casino v07.

One quieter on-time telephone copy of each supplied line the aligner could
actually place, and fading echoes of that line's last word only. v03 stays
the dry mix. No feedback delay, no limiter, no peak makeup.

Wording is Chex's text. This script does not listen.
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
DOT = 14700
INTRO_SHIFT = -8 * BAR

_spec = importlib.util.spec_from_file_location("sc_v06", Path(__file__).with_name("render_v06.py"))
v6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v6)
v4 = v6.v4


def decide(rec):
    """Whether this alignment is reliable enough to put in the mix."""
    if rec["status"] != "ctc_timed":
        return False, False, rec.get("why") or rec["status"]
    evidence = rec["transcript_match"]["evidence"]
    if evidence.startswith("anchored"):
        return False, False, (
            "Search anchor only. The ordered transcript did not place this copy, "
            "so the forced-alignment score is not used as a timing."
        )
    mean = rec["ctc"]["mean_token_score"]
    fw = rec["final_word"]
    if not fw.get("pronunciation_matches_tokens"):
        return False, False, "Final-word phones do not match the supplied word's pronunciation map."
    dur = rec["line_end"] - rec["line_start"]
    if dur < 1.15 or dur > 6.2:
        return False, False, f"Aligned duration {dur:.2f}s is not a complete supplied line."
    for w in rec["ctc"]["words"]:
        span = w["end"] - w["start"]
        if span > 1.15 or (span > 0.85 and w["align_word"] in {"the", "a", "i", "it", "and", "to", "of"}):
            return False, False, (
                f"Token {w['align_word']!r} was stretched across {span:.2f}s, so this line "
                "swallowed the audio around it."
            )
    transcript = rec["transcript_match"]["score"]
    strong_final = fw["token_score"] >= 0.50 and transcript >= 0.80 and mean >= 0.28
    if mean < 0.30 and not strong_final:
        return False, False, f"Mean CTC score {mean:.3f} is below 0.30."
    if fw["token_score"] < 0.20:
        return False, False, (
            f"Final word {fw['text_token']!r} CTC score {fw['token_score']:.3f} "
            "does not establish the end of the line."
        )
    # Echo needs a final word the phonetic model and, when present, the
    # transcript token both sit on. A short function word with no transcript
    # token stays out.
    whisper = fw.get("speech_model_token")
    echo_floor = 0.30 if whisper else 0.45
    echo = fw["token_score"] >= echo_floor
    echo_why = None if echo else (
        f"Last word {fw['text_token']!r} score {fw['token_score']:.3f} is under {echo_floor:.2f} "
        "for an echo. The line copy does not depend on this."
    )
    return True, echo, echo_why


def content_start(rec):
    """Skip a one-frame token. A 20 ms 'i' is not the line's attack."""
    for w in rec["ctc"]["words"]:
        if w["end"] - w["start"] >= 0.04 and w["token_score"] >= 0.15:
            return w["start"]
    return rec["line_start"]


def overlaps(a, b):
    a0, b0 = content_start(a), content_start(b)
    return min(a["line_end"], b["line_end"]) - max(a0, b0)


def select(records):
    chosen = []
    rejected = []
    for rec in records:
        use_line, use_echo, why = decide(rec)
        rec["decision"] = {
            "use_line": use_line,
            "use_echo": use_echo,
            "reason": why,
        }
        if use_line:
            chosen.append(rec)
        else:
            rejected.append(rec)
    chosen.sort(key=lambda r: -(r["transcript_match"]["score"] + r["ctc"]["mean_token_score"]))
    kept = []
    for rec in chosen:
        fight = None
        for prev in kept:
            shared = overlaps(rec, prev)
            shorter = min(rec["line_end"] - rec["line_start"], prev["line_end"] - prev["line_start"])
            if shared > 0.45 * shorter:
                fight = prev
                break
        if fight is None:
            kept.append(rec)
            continue
        rec["decision"]["use_line"] = False
        rec["decision"]["use_echo"] = False
        rec["decision"]["reason"] = (
            f"Overlaps {fight['line_id']} occurrence {fight['occurrence']} "
            f"({fight['line_start']:.2f}-{fight['line_end']:.2f}s), which scored higher."
        )
        rejected.append(rec)
    return sorted(kept, key=lambda r: r["line_start"]), rejected


def word_bounds(mono, rec, limit):
    """CTC span, earlier transcript token if it overlaps, then the measured decay."""
    fw = rec["final_word"]
    start = fw["start"]
    model_end = fw["end"]
    kinds = ["mms_ctc"]
    whisper = fw.get("speech_model_token")
    if whisper and 0 < start - whisper["start"] <= 0.20:
        start = whisper["start"]
        kinds.append("speech_model_token_start")
    if whisper and 0 < whisper["end"] - model_end <= 0.35:
        model_end = whisper["end"]
        kinds.append("speech_model_token_end")
    end = v6.extend_tail(mono, model_end, limit)
    if end > model_end + 0.02:
        kinds.append("rms_decay")
    return start, end, kinds, model_end


def main():
    payload = json.loads((SONG / "effects" / "lyrics_alignment.json").read_text())
    kept, _rejected = select(payload["lines"])
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

    line_bus = np.zeros((n, 2), np.float32)
    echo_bus = np.zeros((n, 2), np.float32)
    line_events = []
    echo_events = []
    skipped_echoes = []

    for i, rec in enumerate(kept):
        nxt = kept[i + 1]["line_start"] if i + 1 < len(kept) else len(raw) / SR
        fw = rec["final_word"]
        # Keep the final word through its own end. A following line that
        # starts a few tens of milliseconds early is not a reason to crop it.
        tail_limit = nxt - 0.03 if nxt > rec["final_word"]["end"] + 0.04 else rec["final_word"]["end"] + 0.01
        w_start, w_end, kinds, model_end = word_bounds(raw, rec, tail_limit)
        line_end = max(rec["line_end"], w_end)
        line_start = rec["line_start"]
        seg = v6.filtered_span(raw, line_start, line_end)
        dest = line_start + (BAR / SR)
        v6.place(line_bus, seg, dest, -16.0, fade_out_s=0.05)
        line_events.append({
            "id": f"{rec['line_id']}-o{rec['occurrence']}",
            "layer": "full_line_once",
            "repeat_count": 1,
            "text": rec["text"],
            "line_id": rec["line_id"],
            "occurrence": rec["occurrence"],
            "source_start_s": round(line_start, 6),
            "source_end_s": round(line_end, 6),
            "ctc_line_start_s": rec["line_start"],
            "ctc_line_end_s": rec["line_end"],
            "dest_start_s": round(dest, 6),
            "shift_samples": BAR,
            "shift_ms": round(BAR / SR * 1000, 2),
            "gain_db_on_raw_vocal": -16.0,
            "mean_ctc": rec["ctc"]["mean_token_score"],
            "boundary_status": "supplied line, MMS CTC bounds, tail extended only while the level is still falling",
        })
        rec["render_span"] = {
            "line_start_s": round(line_start, 6),
            "line_end_s": round(line_end, 6),
            "final_word_start_s": round(w_start, 6),
            "final_word_end_s": round(w_end, 6),
            "timestamp_kinds": kinds,
        }

        if not rec["decision"]["use_echo"]:
            skipped_echoes.append({
                "line_id": rec["line_id"],
                "occurrence": rec["occurrence"],
                "word": fw["text_token"],
                "why": rec["decision"]["reason"],
            })
            continue
        pause_limit = min(nxt, v6.audible_return(raw, w_end, nxt))
        if pause_limit - w_end < 0.28:
            skipped_echoes.append({
                "line_id": rec["line_id"],
                "occurrence": rec["occurrence"],
                "word": fw["text_token"],
                "why": f"No gap after {w_end:.3f}s before the next vocal at {pause_limit:.3f}s.",
            })
            rec["decision"]["use_echo"] = False
            rec["decision"]["echo_skipped"] = "no gap"
            continue
        word_audio = v6.filtered_span(raw, w_start, w_end)
        taps = v6.schedule_echoes(w_start, w_end, pause_limit)
        if not taps:
            skipped_echoes.append({
                "line_id": rec["line_id"],
                "occurrence": rec["occurrence"],
                "word": fw["text_token"],
                "why": "No dotted-eighth multiple starts after the word and lands in the gap.",
            })
            rec["decision"]["use_echo"] = False
            continue
        for ntap, tap in enumerate(taps):
            gain = -14.0 - 5.0 * ntap
            v6.place(echo_bus, word_audio, tap["dest_start_s"], gain, fade_out_s=tap["fade_out_s"])
            tap["gain_db"] = round(gain, 3)
        echo_events.append({
            "id": f"lastword-{rec['line_id']}-o{rec['occurrence']}",
            "layer": "last_word_echoes",
            "word": fw["text_token"],
            "line_id": rec["line_id"],
            "ctc_start_s": fw["start"],
            "ctc_end_s": fw["end"],
            "ctc_score": fw["token_score"],
            "speech_model_token": fw.get("speech_model_token"),
            "source_start_s": round(w_start, 6),
            "source_end_s": round(w_end, 6),
            "model_end_before_decay_s": round(model_end, 6),
            "timestamp_kinds": kinds,
            "taps": taps,
            "flags": [
                "MMS is a speech aligner. These times are not a musical approval.",
                f"mean line CTC {rec['ctc']['mean_token_score']}",
            ],
        })

    opening = next(
        (
            r for r in payload["lines"]
            if r["line_id"] == "L01" and r["status"] == "ctc_timed" and 15.5 < r["line_start"] < 20
        ),
        None,
    )
    opening_event = None
    if opening is None:
        opening_note = "No CTC placement of the opening Xanax line between 15.5 and 20 s."
    else:
        fw = opening["final_word"]
        whisper = fw.get("speech_model_token") or {}
        agrees = (
            fw["text_token"].rstrip(".").lower() == "alcohol"
            and "alcohol" in (whisper.get("raw") or "").lower()
            and whisper.get("start") is not None
            and abs(whisper["start"] - fw["start"]) < 0.25
        )
        if not agrees:
            opening_note = (
                f"Opening candidate {opening['line_start']:.3f}-{opening['line_end']:.3f}s "
                f"does not agree on alcohol. CTC final {fw['start']:.3f}-{fw['end']:.3f} "
                f"score {fw['token_score']}. Not echoed."
            )
        else:
            nxt = next(r["line_start"] for r in kept if r["line_start"] > fw["end"])
            w_start, w_end, kinds, model_end = word_bounds(raw, opening, nxt - 0.03)
            intro_start = w_start + (INTRO_SHIFT / SR)
            intro_end = w_end + (INTRO_SHIFT / SR)
            word_audio = v6.filtered_span(raw, w_start, w_end)
            taps = v6.schedule_echoes(intro_start, intro_end, 13.2)
            for ntap, tap in enumerate(taps):
                gain = -14.0 - 5.0 * ntap
                v6.place(echo_bus, word_audio, tap["dest_start_s"], gain, fade_out_s=tap["fade_out_s"])
                tap["gain_db"] = round(gain, 3)
            opening_event = {
                "id": "opening-telephone-last-word",
                "layer": "opening_telephone_last_word_echoes",
                "word": fw["text_token"],
                "source_start_s": round(w_start, 6),
                "source_end_s": round(w_end, 6),
                "ctc_start_s": fw["start"],
                "ctc_end_s": fw["end"],
                "ctc_score": fw["token_score"],
                "speech_model_token": whisper,
                "intro_word_start_s": round(intro_start, 6),
                "intro_word_end_s": round(intro_end, 6),
                "intro_shift_samples": INTRO_SHIFT,
                "timestamp_kinds": kinds,
                "model_end_before_decay_s": round(model_end, 6),
                "taps": taps,
                "flags": [
                    f"Line mean CTC {opening['ctc']['mean_token_score']} and alcohol token "
                    f"{fw['token_score']} are low. Sung phones do not fit the speech model.",
                    "The echo is still placed because the supplied last word, the transcript token, "
                    "and the CTC span are the same word and overlap. This is not musical approval.",
                    "The full opening line was not given a new backing copy. Its CTC bounds miss the "
                    "15.95 s attack. The v03 telephone line is unchanged.",
                ],
            }
            echo_events.append(opening_event)
            opening_note = "Placed from the overlapping alcohol spans, with the low CTC score kept as a flag."
            opening["decision"] = opening.get("decision") or {}
            opening["decision"]["opening_last_word_echo"] = True
            opening["decision"]["use_line"] = False
            opening["render_span"] = {
                "final_word_start_s": round(w_start, 6),
                "final_word_end_s": round(w_end, 6),
                "timestamp_kinds": kinds,
                "role": "opening telephone last word only",
            }

    mix = (
        buses["beat_dry"] + buses["vocal_dry"] + buses["beat_stop"] + buses["reverse"]
        + buses["phone"] + buses["phone_reverb"] + buses["lead_reverb"]
        + line_bus + echo_bus
    )
    pk = v4.peak_db(mix)
    trims = []
    if pk[0] > -1.2:
        over = pk[0] + 1.2 + 0.15
        scale = np.float32(10 ** (-over / 20.0))
        line_bus *= scale
        echo_bus *= scale
        trims.append(round(over, 3))
        mix = (
            buses["beat_dry"] + buses["vocal_dry"] + buses["beat_stop"] + buses["reverse"]
            + buses["phone"] + buses["phone_reverb"] + buses["lead_reverb"]
            + line_bus + echo_bus
        )
        pk = v4.peak_db(mix)
    if pk[0] > -1.0:
        sys.exit(f"peak {pk[0]:.2f} dBFS")

    v03 = v4.load_stereo(SONG / "renders" / "satans-casino-v03-review.wav")
    sing = slice(int(17.0 * SR), int(18.5 * SR))
    diff = {
        "singing_rms_v03": round(v4.db(v03[sing]), 2),
        "singing_rms_v07": round(v4.db(mix[sing]), 2),
        "correlation": round(float(np.corrcoef(v03[::25, 0], mix[::25, 0])[0, 1]), 4),
    }
    print("lines", len(line_events), "echo groups", len(echo_events), "peak", round(pk[0], 2), "diff", diff)

    out = SONG / "renders" / "satans-casino-v07-review.wav"
    v4.write_pcm24(out, mix)
    v4.write_pcm24(SONG / "buses" / "v07_full_line_once.flac", line_bus)
    v4.write_pcm24(SONG / "buses" / "v07_last_word_echoes.flac", echo_bus)
    mp3 = SONG / "renders" / "satans-casino-v07-review.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(out), "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)],
        check=True,
    )

    def failure_note(rec):
        ctc = rec.get("ctc") or {}
        words = ctc.get("words") or []
        named = [
            f"{w['align_word']} {w['start']:.3f}-{w['end']:.3f}s score {w['token_score']:.3f}"
            for w in words
            if w["align_word"] in {"spite", "forth", "up", "tomorrow", "alcohol", "escaping", "catching"}
        ]
        base = rec["decision"].get("reason") or rec.get("why") or rec["status"]
        if rec["status"] == "rejected_overlap" and rec["transcript_match"]["evidence"].startswith("ordered"):
            base = (
                f"Ordered transcript window {rec['transcript_match']['start']:.2f}-"
                f"{rec['transcript_match']['end']:.2f}s, mean CTC {ctc.get('mean_token_score')}. "
                "The line end did not hold, so it was not rendered."
            )
        extra = ("; " + "; ".join(named)) if named else ""
        return base + extra

    unresolved = []
    seen = set()
    for rec in payload["lines"]:
        if rec["decision"].get("use_line"):
            continue
        key = rec["line_id"]
        if key in seen:
            continue
        if any(k["line_id"] == key and k["decision"].get("use_line") for k in kept):
            continue
        seen.add(key)
        ordered = [
            r for r in payload["lines"]
            if r["line_id"] == key
            and r.get("transcript_match", {}).get("evidence", "").startswith("ordered")
        ]
        picked = max(ordered or [rec], key=lambda r: (r.get("ctc") or {}).get("mean_token_score") or 0)
        attempts = []
        for r in ordered or [rec]:
            if r.get("line_start") is None:
                attempts.append(failure_note(r))
            else:
                attempts.append(
                    f"{r['line_start']:.3f}-{r['line_end']:.3f}s: {failure_note(r)}"
                )
        unresolved.append({
            "line_id": key,
            "text": rec["text"],
            "why": " | ".join(attempts),
            "ctc_window": None if not picked.get("ctc") else picked["ctc"].get("window"),
            "mean_ctc": None if not picked.get("ctc") else picked["ctc"].get("mean_token_score"),
        })
    dropped_repeats = []
    for rec in payload["lines"]:
        if rec["decision"].get("use_line"):
            continue
        if not any(k["line_id"] == rec["line_id"] and k["decision"].get("use_line") for k in kept):
            continue
        if not rec.get("transcript_match", {}).get("evidence", "").startswith("ordered"):
            continue
        if rec["status"] != "ctc_timed":
            continue
        dropped_repeats.append({
            "line_id": rec["line_id"],
            "occurrence": rec["occurrence"],
            "start": rec.get("line_start"),
            "end": rec.get("line_end"),
            "why": rec["decision"].get("reason"),
        })

    payload["render"] = {
        "version": "v07",
        "listening": "not performed",
        "lines_used": len(line_events),
        "echoes_used": len(echo_events),
        "opening_last_word": opening_note,
        "not_rendered": unresolved,
        "repeats_located_but_not_used": dropped_repeats,
    }
    (SONG / "effects" / "lyrics_alignment.json").write_text(json.dumps(payload, indent=2))

    audit = {
        "version": "v07",
        "baseline": "v03 buses, beat -8 dB and vocal -6 dB from sample 0, plus the same reverse lowpass and intro-phone high cut",
        "listening": "not performed. Peaks and these checks are not musical approval.",
        "mastering": "none. No limiter, no loudness pass, no positive gain on a quiet word.",
        "lyric_source": "lyrics/chex-supplied.txt, stored as supplied. spite and forth were not rewritten.",
        "alignment": "effects/lyrics_alignment.json. Line and word times used here are MMS CTC unless timestamp_kinds names a transcript token or an RMS decay.",
        "full_line_repeat_count_each": 1,
        "full_line_shift_samples": BAR,
        "echo_interval_samples": DOT,
        "hiss_before": hiss_before,
        "hiss_after": hiss_after,
        "difference_vs_v03": diff,
        "peak_dbfs": round(pk[0], 3),
        "trims_db_on_new_buses_only": trims,
        "full_lines": line_events,
        "last_word_echoes": echo_events,
        "skipped_echoes": skipped_echoes,
        "not_rendered": unresolved,
        "repeats_located_but_not_used": dropped_repeats,
        "opening_telephone_last_word": opening_event,
        "opening_note": opening_note,
    }
    (SONG / "effects" / "v07-events.json").write_text(json.dumps(audit, indent=2))

    md = [
        "# Satan's Casino v07",
        "",
        "Baseline is the v03 dry mix. No listening was done. This is not a master and not a verified final.",
        "",
        f"Full-line copies: {len(line_events)}, each once, one bar later, -16 dB, telephone. "
        f"Last-word echo groups: {len(echo_events)}. Peak {pk[0]:.2f} dBFS. "
        f"Correlation with v03 {diff['correlation']}. Singing 17–18.5 s RMS v03 {diff['singing_rms_v03']} dB, v07 {diff['singing_rms_v07']} dB.",
        "",
        "Hiss treatment is the reverse lowpass at 3600 Hz and a 2.5 dB cut above 3.2 kHz on the intro telephone only.",
        "",
        "## Opening alcohol",
        "",
        opening_note,
        "",
    ]
    if opening_event:
        md.append(
            f"Source {opening_event['source_start_s']:.3f}–{opening_event['source_end_s']:.3f}s "
            f"(CTC {opening_event['ctc_start_s']:.3f}–{opening_event['ctc_end_s']:.3f}s, "
            f"score {opening_event['ctc_score']}). "
            f"Kinds: {', '.join(opening_event['timestamp_kinds'])}."
        )
        md.append("")
        for fl in opening_event["flags"]:
            md.append(f"- {fl}")
        md.append("")
    md += ["## 15K", ""]
    for e in echo_events:
        if e.get("word") == "15K":
            md.append(
                f"- {e['id']} source {e['source_start_s']:.3f}–{e['source_end_s']:.3f}s, "
                f"CTC {e['ctc_start_s']:.3f}–{e['ctc_end_s']:.3f}s score {e['ctc_score']}, "
                f"kinds {', '.join(e['timestamp_kinds'])}."
            )
    md += ["", "## Repeats located but not copied", ""]
    for item in dropped_repeats:
        md.append(
            f"- {item['line_id']} occurrence {item['occurrence']} "
            f"{item['start']:.2f}–{item['end']:.2f}s. {item['why']}"
        )
    md += ["", "## Not rendered", ""]
    for item in unresolved:
        md.append(f"- {item['line_id']}: {item['text']}")
        md.append(f"  - {item['why']}")
    md += ["", "## Full lines", ""]
    for e in line_events:
        md.append(
            f"- {e['id']} {e['source_start_s']:.3f}–{e['source_end_s']:.3f}s → {e['dest_start_s']:.3f}s, "
            f"CTC mean {e['mean_ctc']}. {e['text']}"
        )
    md += ["", "## Last-word echoes", ""]
    for e in echo_events:
        taps = ", ".join(
            f"{t['dest_start_s']:.3f}s ({t['delay_ms']:.0f} ms, {t['gain_db']:.1f} dB)" for t in e["taps"]
        )
        md.append(
            f"- {e['id']} {e['word']} {e['source_start_s']:.3f}–{e['source_end_s']:.3f}s. Taps: {taps}."
        )
    (SONG / "reports" / "v07.md").write_text("\n".join(md) + "\n")
    print("opening", opening_note)
    print("unresolved", [u["line_id"] for u in unresolved])


if __name__ == "__main__":
    main()

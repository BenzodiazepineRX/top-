#!/usr/bin/env python3
"""Checks the v05 split: one full-line repeat, last-word echoes after the word."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SONG = Path(__file__).resolve().parents[1]
SR = 44100


def rms_db(x):
    x = np.asarray(x, dtype=np.float64)
    return 20 * np.log10(float(np.sqrt(np.mean(x * x))) + 1e-12)


def main():
    audit = json.loads((SONG / "effects" / "v05-events.json").read_text())
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL", msg)

    if any(e["repeat_count"] != 1 or e["shift_samples"] != 78400 for e in audit["full_lines"]):
        fail("a full-line event is not exactly one bar, once")
    if not any(e["id"] == "opening-telephone-last-word" and e["taps"] for e in audit["last_word_echoes"]):
        fail("opening telephone last-word echoes are missing")
    alcohol = next(e for e in audit["last_word_echoes"] if e["id"] == "lastword-L00")
    if alcohol["source_start_s"] > 17.76:
        fail("alcohol throw dropped the start of the word")
    if alcohol["source_end_s"] < 18.4 or alcohol["source_end_s"] > 18.75:
        fail("alcohol tail was clipped or ran into the next line")
    if alcohol["taps"][0]["dest_start_s"] < alcohol["source_end_s"] - 0.02:
        fail("alcohol echo starts while the word is still going")
    k15 = [e for e in audit["last_word_echoes"] if "15k" in e.get("word", "")]
    if not k15 or not k15[0].get("alignment_flags"):
        fail("15k mismatch was not flagged")
    for e in audit["last_word_echoes"]:
        end = e.get("intro_word_end_s", e["source_end_s"])
        for t in e["taps"]:
            if t["dest_start_s"] < end - 0.03:
                fail(f"{e['id']} tap starts during the word")
            if t["delay_samples"] % 14700:
                fail(f"{e['id']} delay is not a dotted-eighth multiple")
    v05, _ = sf.read(SONG / "renders" / "satans-casino-v05-review.wav")
    if 20 * np.log10(float(np.max(np.abs(v05))) + 1e-12) > -1.0:
        fail("peak is hot")
    vocal, _ = sf.read(SONG / "sources" / "satans-casino-lead-vocals.flac")
    dry, _ = sf.read(SONG / "buses" / "vocal_dry.flac")
    s, e = int(17 * SR), int(18 * SR)
    if abs(rms_db(dry[s:e, 0]) - (rms_db(vocal[s:e].mean(axis=1)) - 6)) > 0.1:
        fail("dry vocal is not -6 dB")
    if fails:
        print(len(fails), "failed")
        sys.exit(1)
    print(f"PASS {len(audit['full_lines'])} single line-repeats, opening echoes present, alcohol kept whole")


if __name__ == "__main__":
    main()

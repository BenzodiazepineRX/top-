#!/usr/bin/env python3
"""v06 checks. These do not listen and do not verify lyrics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SONG = Path(__file__).resolve().parents[1]
SR = 44100


def main():
    audit = json.loads((SONG / "effects" / "v06-events.json").read_text())
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL", msg)

    for e in audit["full_lines"]:
        if e["repeat_count"] != 1 or e["shift_samples"] != 78400:
            fail(f"{e['id']} is not one bar, once")
        if e["n_words"] <= 2 or e["source_end_s"] - e["source_start_s"] < 1:
            fail(f"{e['id']} is still a short fragment")
        if e["gain_db_on_raw_vocal"] > 0:
            fail(f"{e['id']} boosts the raw vocal")
    k15 = next(e for e in audit["last_word_echoes"] if "15k" in e.get("word", ""))
    if k15["source_start_s"] > 153.70:
        fail("15k still starts at a later rise")
    if k15["source_end_s"] < 154.34:
        fail("15k ends before the model token")
    if not k15["taps"] or k15["taps"][0]["dest_start_s"] < k15["source_end_s"] - 0.02:
        fail("15k echo starts during the word")
    alcohol = next(e for e in audit["last_word_echoes"] if e["id"] == "lastword-L00")
    if abs(alcohol["source_start_s"] - 17.74) > 0.02:
        fail("alcohol no longer starts on the model token")
    if not any(e["id"] == "opening-telephone-last-word" and e["taps"] for e in audit["last_word_echoes"]):
        fail("opening last-word echoes missing")
    for e in audit["last_word_echoes"]:
        end = e.get("intro_word_end_s", e["source_end_s"])
        for t in e["taps"]:
            if t["gain_db"] > 0:
                fail(f"{e['id']} has positive gain {t['gain_db']}")
            if t["dest_start_s"] < end - 0.03:
                fail(f"{e['id']} tap overlaps the word")
    y, _ = sf.read(SONG / "renders" / "satans-casino-v06-review.wav")
    if 20 * np.log10(float(np.max(np.abs(y))) + 1e-12) > -1.0:
        fail("peak hot")
    if fails:
        print(len(fails), "failed")
        sys.exit(1)
    print("PASS structure only; lyric lines remain unverified")


if __name__ == "__main__":
    main()

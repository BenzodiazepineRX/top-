#!/usr/bin/env python3
"""v07 structure checks. These do not listen and are not musical approval."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SONG = Path(__file__).resolve().parents[1]
SR = 44100
DOT = 14700


def main():
    audit = json.loads((SONG / "effects" / "v07-events.json").read_text())
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL", msg)

    texts = [e["text"] for e in audit["full_lines"]]
    if any(t.strip().lower() in {"it", "plug and", "next verse:"} or t.startswith("(") for t in texts):
        fail("a short scrap or a repeat label was rendered as a line")
    for e in audit["full_lines"]:
        if e["repeat_count"] != 1 or e["shift_samples"] != 78400:
            fail(f"{e['id']} is not one bar, once")
        if e["source_end_s"] - e["source_start_s"] < 1.15:
            fail(f"{e['id']} is shorter than a supplied line")
        if e["gain_db_on_raw_vocal"] > 0:
            fail(f"{e['id']} has positive gain")
    k15 = [e for e in audit["last_word_echoes"] if e.get("word") == "15K" and e["source_start_s"] > 150]
    if len(k15) != 1:
        fail(f"expected one late 15K echo, found {len(k15)}")
    else:
        e = k15[0]
        if not (153.60 <= e["source_start_s"] <= 153.70):
            fail(f"15K starts at {e['source_start_s']}, not the full token")
        if e["source_end_s"] < 154.50:
            fail("15K ends before the decay of the full word")
        if e["ctc_start_s"] > 153.80:
            fail("15K CTC start is missing the fifteen token")
    alcohol = audit.get("opening_telephone_last_word")
    if not alcohol or not alcohol.get("taps"):
        fail("opening telephone last-word echoes missing")
    else:
        if abs(alcohol["source_start_s"] - 17.74) > 0.02:
            fail("opening alcohol does not start on the transcript token")
        if alcohol["source_end_s"] < 18.40:
            fail("opening alcohol ends before its decay")
        if alcohol["intro_word_end_s"] > alcohol["taps"][0]["dest_start_s"] + 0.01:
            fail("opening echo starts while the telephone word is still going")
        if alcohol["taps"][-1]["dest_start_s"] > 13.2:
            fail("opening echo runs into the lead vocal")
    adder = [e for e in audit["last_word_echoes"] if e.get("word", "").lower().startswith("adderall")]
    if len(adder) < 2:
        fail(f"expected both Adderall echoes, found {len(adder)}")
    for e in adder:
        if e["source_start_s"] > e["ctc_start_s"] + 0.01:
            fail(f"{e['id']} starts after the CTC attack")
    for e in audit["last_word_echoes"]:
        end = e.get("intro_word_end_s", e["source_end_s"])
        for t in e["taps"]:
            if t["gain_db"] > 0:
                fail(f"{e['id']} has positive gain")
            if t["delay_samples"] % DOT != 0:
                fail(f"{e['id']} delay is not a dotted-eighth multiple")
            if t["dest_start_s"] < end - 0.02:
                fail(f"{e['id']} tap starts during the word")
    y, sr = sf.read(SONG / "renders" / "satans-casino-v07-review.wav")
    if sr != SR or y.shape[1] != 2:
        fail(f"unexpected render shape {y.shape} {sr}")
    peak = float(np.max(np.abs(y)))
    if peak >= 1.0 or 20 * np.log10(peak + 1e-12) > -1.0:
        fail(f"peak {peak}")
    if y.shape[0] < int(216 * SR):
        fail("render is shorter than the beat; a tail was cut")
    omitted = {u["line_id"] for u in audit["not_rendered"]}
    for needed in ("L03", "L04", "L06", "L12", "L22"):
        if needed not in omitted:
            fail(f"{needed} was rendered or dropped from the unresolved list")
    if fails:
        print(len(fails), "failed")
        sys.exit(1)
    print("PASS structure only. Not a listening check and not musical approval.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Checks for the v04 echoes. Not a listening approval."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SONG = Path(__file__).resolve().parents[1]
SR = 44100
DOT = 14700


def rms_db(x):
    x = np.asarray(x, dtype=np.float64)
    if x.size < 8:
        return -200.0
    return 20.0 * np.log10(float(np.sqrt(np.mean(x * x))) + 1e-12)


def main():
    report = json.loads((SONG / "effects" / "v04-events.json").read_text())
    vocal, _ = sf.read(SONG / "sources" / "satans-casino-lead-vocals.flac")
    vocal = vocal.mean(axis=1)
    v03, _ = sf.read(SONG / "renders" / "satans-casino-v03-review.wav")
    v04, _ = sf.read(SONG / "renders" / "satans-casino-v04-review.wav")
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL", msg)

    peak = float(np.max(np.abs(v04)))
    if 20 * np.log10(peak + 1e-12) > -1.0:
        fail(f"v04 peak {20*np.log10(peak):.2f} dBFS")
    s, e = int(17 * SR), int(18.5 * SR)
    if abs(rms_db(v03[s:e]) - rms_db(v04[s:e])) > 0.6:
        fail("singing level moved more than 0.6 dB from v03")
    # dry gain still -6 / -8 on the stored buses
    dry, _ = sf.read(SONG / "buses" / "vocal_dry.flac")
    src = vocal[: len(dry)]
    if abs(rms_db(dry[s:e, 0]) - (rms_db(src[s:e]) - 6)) > 0.08:
        fail("vocal dry bus is not the source at -6 dB")

    throws = report["throws"]
    if not throws:
        fail("no throws were kept and no blocker was the only output")
    for t in throws:
        if t["delay_samples"] % DOT != 0:
            fail(f"{t['id']} delay is not a whole dotted eighth")
        dur = t["source_end_s"] - t["source_start_s"]
        if abs(dur - 0.300) < 0.008:
            fail(f"{t['id']} is a 300 ms crop")
        a, b = int(t["source_start_s"] * SR), int(t["source_end_s"] * SR)
        body = rms_db(vocal[a:b])
        tail = rms_db(vocal[b:b + int(0.06 * SR)])
        if tail > body - 3 and tail > -28:
            fail(f"{t['id']} ends while the line is still as loud as the word ({tail:.1f} vs {body:.1f})")
        # echo must not start by snapping the cut onto a bar
        if abs((t["dest_start_s"] - t["source_start_s"]) - t["delay_samples"] / SR) > 0.002:
            fail(f"{t['id']} destination is not the source plus the delay")
    if fails:
        print(len(fails), "failed")
        sys.exit(1)
    print(f"PASS {len(throws)} throws, singing held, dry vocal -6 dB, peak under -1 dBFS")


if __name__ == "__main__":
    main()

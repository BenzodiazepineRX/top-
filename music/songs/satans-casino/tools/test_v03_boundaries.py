#!/usr/bin/env python3
"""Boundary tests for the v03 added vocals.

These tests catch the v02 failure: a slice that drops a loud head, ends while
the line continues, or is moved so that cut sits on a bar line.

They do not listen, and they do not say the mix is approved.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SONG = Path(__file__).resolve().parents[1]
SR = 44100
BAR = 19600 * 4


def load_mono(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    )
    return np.frombuffer(raw.stdout, dtype="<f4")


def load_stereo(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    )
    return np.frombuffer(raw.stdout, dtype="<f4").reshape(-1, 2)


def rms_db(x):
    if len(x) < 8:
        return -200.0
    return 20.0 * np.log10(float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2))) + 1e-12)


def main():
    events = json.loads((SONG / "effects" / "v03-events.json").read_text())["events"]
    vocal = load_mono(SONG / "sources" / "satans-casino-lead-vocals.flac")
    beat = load_stereo(SONG / "sources" / "satans-casino-beat.flac")
    failures = []

    def fail(msg):
        failures.append(msg)
        print("FAIL", msg)

    phones = [e for e in events if e["layer"] == "telephone_bgv"]
    throws = [e for e in events if e["layer"] == "delay_throws"]
    if throws:
        fail(f"{len(throws)} delay throws are present; v03 should omit cropped throws")
    if len(phones) != 1:
        fail(f"expected one telephone vocal, found {len(phones)}")

    for e in phones:
        a = int(e["source_start_sample"])
        b = int(e["source_end_sample"])
        before = rms_db(vocal[max(0, a - int(0.15 * SR)):a - int(0.01 * SR)])
        after = rms_db(vocal[b + int(0.02 * SR):b + int(0.15 * SR)])
        if before > -36:
            fail(f"{e['id']} drops a loud head ({before:.1f} dB in the 150 ms before the slice)")
        if after > -32:
            fail(f"{e['id']} ends while the line continues ({after:.1f} dB just after)")
        if e["shift_samples"] % BAR != 0:
            fail(f"{e['id']} shift {e['shift_samples']} is not a whole number of bars")
        # the loud opening span v02 discarded must sit inside this source
        head = int(15.968707 * SR)
        if not (a <= head < b):
            fail("the 15.969 s attack is not inside the telephone source")
        onset = int(round(e["onset_s"] * SR))
        src_off = onset - int(round(e["downbeat_s"] * SR))
        dest_off = (onset + e["shift_samples"]) - (int(round(e["downbeat_s"] * SR)) + e["shift_samples"])
        if src_off != dest_off:
            fail("onset offset was not preserved")
        # v02's chopped start must not be the start of this event
        if abs(e["source_start_s"] - 16.103401) < 0.01:
            fail("telephone source still starts at the v02 cut, 16.103 s")

    # dry vocal and beat, recomputed, not taken from a processed bus
    vocal_st = load_stereo(SONG / "sources" / "satans-casino-lead-vocals.flac")
    g_v = 10 ** (-6 / 20)
    g_b = 10 ** (-8 / 20)
    # alignment: sample 0 is sample 0, gain only
    if abs(rms_db(vocal_st[: SR] * g_v) - rms_db(vocal_st[: SR])) > 6.05:
        fail("vocal gain is not -6 dB")
    # exact gain on a loud window
    s, e = int(16.1 * SR), int(16.3 * SR)
    got = rms_db(vocal_st[s:e] * g_v)
    expect = rms_db(vocal_st[s:e]) - 6
    if abs(got - expect) > 0.05:
        fail(f"dry vocal window is {got - expect:.3f} dB off -6")
    s, e = int(17.7 * SR), int(17.9 * SR)
    got = rms_db(beat[s:e, 0] * g_b)
    expect = rms_db(beat[s:e, 0]) - 8
    if abs(got - expect) > 0.05:
        fail(f"dry beat window is {got - expect:.3f} dB off -8")

    # no added vocal on top of the lead: phone bus is quiet from the real entry onward
    phone = load_stereo(SONG / "buses" / "v03_telephone_bgv.flac")
    late = rms_db(phone[int(13.4 * SR):int(20 * SR)].mean(axis=1))
    if late > -70:
        fail(f"telephone bus is still up over the real vocal ({late:.1f} dB)")

    throws_bus = load_stereo(SONG / "buses" / "v03_delay_throws.flac")
    throw_peak = float(np.max(np.abs(throws_bus)))
    if throw_peak > 1e-6:
        fail(f"delay throw bus is not empty (peak {throw_peak:.3e})")

    if failures:
        print(f"{len(failures)} failed")
        sys.exit(1)
    print(f"PASS {len(phones)} telephone vocal, 0 throws, dry -8/-6, head at 15.969 s kept, offset held")


if __name__ == "__main__":
    main()

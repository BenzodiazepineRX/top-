#!/usr/bin/env python3
"""Render a processing chain, optionally reach a loudness target, and keep true peaks under a ceiling.

Applies an ffmpeg audio filter chain (EQ, compression, etc.), then an
oversampled peak limiter, measuring the result in the same pass. With
--target-lufs it adjusts the gain going into the limiter until the integrated
loudness lands within 0.1 LU of the target, then confirms the true peak.
It also reports how hard the limiter worked, so you can back off before the
song gets squashed.

Usage:
  python render_master.py IN.wav OUT_master_v1.wav \
      --chain "highpass=f=25,equalizer=f=300:t=q:w=1:g=-2,acompressor=threshold=-18dB:ratio=1.5:attack=30:release=200" \
      --target-lufs -10 --ceiling -1.0

  python render_master.py IN.wav OUT.wav --chain "..." --no-limiter   # chain only, no gain or limiting

Writes OUT as a 32-bit float WAV (use export_master.py for 24-bit WAV/MP3
delivery) plus OUT.settings.json recording the chain, gain and measurements,
so any version can be recreated or tweaked later.
Needs ffmpeg/ffprobe on PATH.
"""
import argparse
import json
import re
import subprocess
import sys


def probe_rate(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=sample_rate,channels", "-of", "json", path], capture_output=True, text=True)
    s = json.loads(out.stdout)["streams"][0]
    return int(s["sample_rate"]), int(s["channels"])


def soxr_available():
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.1",
                        "-af", "aresample=48000:resampler=soxr", "-f", "null", "-"], capture_output=True)
    return r.returncode == 0


def parse_summary(err):
    if "Summary:" not in err:
        return None
    summ = err[err.rindex("Summary:"):]

    def num(rx):
        m = re.search(rx, summ)
        if not m or m.group(1) == "-inf":
            return None
        return float(m.group(1))
    return {"integrated_lufs": num(r"I:\s*(-?[\d.]+|-inf)"),
            "loudness_range_lu": num(r"LRA:\s*(-?[\d.]+|-inf)"),
            "true_peak_dbtp": num(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)")}


def run_pass(inp, out, chain, sr, mono, gain_db, limit_db, attack, release, use_limiter, rs):
    filters = []
    if chain:
        filters.append(chain)
    if use_limiter:
        filters.append(f"volume={gain_db:.3f}dB")
        filters.append(f"aresample={sr * 4}{rs}")
        filters.append(f"alimiter=limit={limit_db:.3f}dB:attack={attack}:release={release}:level=disabled:latency=true")
    filters.append(f"aresample={sr}{rs}")
    filters.append("ebur128=peak=true" + (":dualmono=true" if mono else ""))
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", inp, "-map", "a:0",
           "-af", ",".join(filters), "-c:a", "pcm_f32le"]
    if out:
        cmd += [out]
    else:
        cmd += ["-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    m = parse_summary(r.stderr)
    if r.returncode != 0 or m is None:
        sys.exit(f"ffmpeg failed. Check the --chain syntax.\n{r.stderr[-1500:]}")
    return m, ",".join(filters)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output", help="output .wav (32-bit float)")
    ap.add_argument("--chain", default="", help="ffmpeg -af filter chain to apply before limiting")
    ap.add_argument("--target-lufs", type=float, help="integrated loudness to aim for (omit to keep the chain's level)")
    ap.add_argument("--ceiling", type=float, default=-1.0, help="maximum true peak in dBTP (default -1.0)")
    ap.add_argument("--attack", type=float, default=5.0, help="limiter attack ms (default 5)")
    ap.add_argument("--release", type=float, default=60.0, help="limiter release ms (default 60)")
    ap.add_argument("--no-limiter", action="store_true", help="apply the chain only")
    ap.add_argument("--max-limiter-db", type=float, default=4.0,
                    help="warn when the limiter removes more loudness than this (LU)")
    a = ap.parse_args()

    sr, ch = probe_rate(a.input)
    rs = ":resampler=soxr" if soxr_available() else ""
    mono = ch == 1

    # 1) the chain alone, to know the starting point
    pre, _ = run_pass(a.input, None, a.chain, sr, mono, 0, 0, a.attack, a.release, False, rs)
    I0 = pre["integrated_lufs"]
    print(f"Chain alone: {I0:.1f} LUFS, true peak {pre['true_peak_dbtp']:+.1f} dBTP, LRA {pre['loudness_range_lu']:.1f} LU")

    if a.no_limiter:
        m, used = run_pass(a.input, a.output, a.chain, sr, mono, 0, 0, a.attack, a.release, False, rs)
        gain, limit = 0.0, None
    else:
        gain = (a.target_lufs - I0) if a.target_lufs is not None else 0.0
        limit = a.ceiling - 0.2  # small margin; verified below
        m = None
        passes = 8
        for i in range(passes):
            m, used = run_pass(a.input, a.output, a.chain, sr, mono, gain, limit, a.attack, a.release, True, rs)
            I, tp = m["integrated_lufs"], m["true_peak_dbtp"]
            print(f"  pass {i + 1}: gain {gain:+.2f} dB, limit {limit:.2f} dB -> {I:.2f} LUFS, true peak {tp:+.2f} dBTP")
            ok_loud = a.target_lufs is None or abs(a.target_lufs - I) <= 0.1
            ok_peak = tp is None or tp <= a.ceiling + 0.05
            if ok_loud and ok_peak:
                break
            # work out the next pass's settings, but only adopt them if that pass will actually run,
            # so gain/limit (and the saved settings) always describe the file that was written
            next_limit = limit - ((tp - a.ceiling) + 0.1) if not ok_peak else limit
            next_gain = gain + (a.target_lufs - I) if not ok_loud else gain
            if i == passes - 1:
                print(f"  stopping: no convergence after {passes} passes; keeping the last rendered settings")
                break
            if next_gain > 18:
                print("  stopping: the target needs more than 18 dB of gain into the limiter; "
                      "keeping the last rendered settings")
                break
            gain, limit = next_gain, next_limit

    out_I, out_tp, out_lra = m["integrated_lufs"], m["true_peak_dbtp"], m["loudness_range_lu"]
    limiter_loss = (I0 + gain) - out_I if not a.no_limiter else 0.0
    print(f"\nResult: {out_I:.1f} LUFS integrated, true peak {out_tp:+.1f} dBTP, "
          f"loudness range {out_lra:.1f} LU (was {pre['loudness_range_lu']:.1f}), "
          f"peak-to-loudness {out_tp - out_I:.1f} dB")
    if not a.no_limiter:
        print(f"Limiter took about {limiter_loss:.1f} LU of loudness off the peaks "
              f"(gain into limiter {gain:+.1f} dB).")
        if limiter_loss > a.max_limiter_db:
            print(f"WARNING: heavy limiting (> {a.max_limiter_db} LU). Expect flattened drums or pumping; "
                  "consider a lower target or gentler compression earlier in the chain.")
    if a.target_lufs is not None and abs(a.target_lufs - out_I) > 0.15:
        print(f"WARNING: missed the target by {out_I - a.target_lufs:+.1f} LU.")
    if out_tp is not None and out_tp > a.ceiling + 0.05:
        print(f"WARNING: true peak {out_tp:+.2f} dBTP is above the {a.ceiling} ceiling.")

    settings = {"input": a.input, "output": a.output, "sample_rate": sr, "chain": a.chain,
                "full_filtergraph": used, "gain_into_limiter_db": round(gain, 2),
                "limiter": None if a.no_limiter else {"limit_db": round(limit, 2), "attack_ms": a.attack,
                                                      "release_ms": a.release, "oversampling": 4},
                "target_lufs": a.target_lufs, "ceiling_dbtp": a.ceiling,
                "measured_before_limiter": pre, "measured_output": m,
                "limiter_loudness_reduction_lu": round(limiter_loss, 2)}
    with open(a.output + ".settings.json", "w") as fh:
        json.dump(settings, fh, indent=2)
    print(f"Wrote {a.output} and {a.output}.settings.json")


if __name__ == "__main__":
    main()

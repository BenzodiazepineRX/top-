#!/usr/bin/env python3
"""Export a finished master for delivery and verify every file it writes.

From a float (or any) master it writes:
  NAME_24bit.wav   24-bit WAV, TPDF-dithered (the main lossless master)
  NAME_16bit.wav   16-bit WAV, TPDF-dithered (only with --also-16bit)
  NAME.mp3         320 kbps MP3 listening copy (skip with --mp3 none, or use --mp3 v0)

Then it reopens each file, decodes it fully, and checks duration, sample
rate, channels, integrated loudness and true peak. MP3 encoding can push
true peak above the master's; when the MP3 lands above --mp3-max-tp
(default -0.1 dBTP) only the MP3 copy is turned down just enough to fit.

Usage:
  python export_master.py master_v2.wav --name "MySong_master_v2" --outdir deliver/
  python export_master.py master_v2.wav --name "MySong_master_v2" --also-16bit --mp3 v0

The sample rate is kept unless --rate is given (resampling happens before dithering).
Needs ffmpeg/ffprobe on PATH and numpy.
"""
import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=codec_name,sample_rate,channels,bits_per_sample,bits_per_raw_sample:format=duration",
                          "-of", "json", path], capture_output=True, text=True)
    d = json.loads(out.stdout)
    s = d["streams"][0]
    bits = s.get("bits_per_raw_sample") or s.get("bits_per_sample")
    return {"codec": s.get("codec_name"), "sample_rate": int(s["sample_rate"]), "channels": int(s["channels"]),
            "bits": int(bits) if bits and str(bits).isdigit() and int(bits) > 0 else None,
            "duration": float(d["format"]["duration"])}


def measure(path, mono):
    af = "ebur128=peak=true" + (":dualmono=true" if mono else "")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", path, "-map", "a:0",
                        "-af", af, "-f", "null", "-"], capture_output=True, text=True)
    err = r.stderr
    errors = [l for l in err.splitlines() if re.search(r"error|invalid|corrupt", l, re.I)]
    summ = err[err.rindex("Summary:"):] if "Summary:" in err else ""
    I = re.search(r"I:\s*(-?[\d.]+)", summ)
    tp = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)", summ)
    return (float(I.group(1)) if I else None,
            float(tp.group(1)) if tp and tp.group(1) != "-inf" else None,
            errors)


def soxr_opt():
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.1",
                        "-af", "aresample=48000:resampler=soxr", "-f", "null", "-"], capture_output=True)
    return ":resampler=soxr" if r.returncode == 0 else ""


def dithered_wav(src, dst, bits, rate, channels, seed=0):
    """Decode to float, add TPDF dither at the target bit depth, quantize, write WAV."""
    rng = np.random.default_rng(seed)
    q = 2 ** (bits - 1)
    af = ["-af", f"aresample={rate}{soxr_opt()}"] if rate else []
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-map", "a:0", *af, "-f", "f32le", "-"],
                           stdout=subprocess.PIPE)
    out_rate = rate or probe(src)["sample_rate"]
    raw_fmt, codec = ("s32le", "pcm_s24le") if bits == 24 else ("s16le", "pcm_s16le")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", raw_fmt, "-ar", str(out_rate),
                            "-ac", str(channels), "-i", "-", "-c:a", codec, dst], stdin=subprocess.PIPE)
    clipped = 0
    pending = b""
    frame_bytes = 4 * channels
    while True:
        buf = dec.stdout.read(65536 * frame_bytes)
        if not buf:
            break
        buf = pending + buf
        usable = len(buf) - len(buf) % frame_bytes
        pending = buf[usable:]
        x = np.frombuffer(buf[:usable], dtype="<f4").astype(np.float64)
        y = np.round(x * q + rng.random(x.shape) - rng.random(x.shape))
        clipped += int(((y > q - 1) | (y < -q)).sum())
        y = np.clip(y, -q, q - 1)
        if bits == 24:
            enc.stdin.write((y.astype(np.int64) << 8).astype("<i4").tobytes())
        else:
            enc.stdin.write(y.astype("<i2").tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    if dec.returncode or enc.returncode:
        sys.exit(f"Export failed for {dst}")
    return clipped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("master")
    ap.add_argument("--name", required=True, help="base filename, e.g. MySong_master_v1")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--rate", type=int, help="convert sample rate (default: keep the master's)")
    ap.add_argument("--also-16bit", action="store_true")
    ap.add_argument("--mp3", default="320", choices=["320", "v0", "none"])
    ap.add_argument("--mp3-max-tp", type=float, default=-0.1,
                    help="if the encoded MP3's true peak exceeds this (dBTP), turn the MP3 copy down to fit; "
                         "pass a very high value such as 99 to disable")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    src = probe(a.master)
    ch = src["channels"]
    mono = ch == 1
    rate = a.rate if a.rate and a.rate != src["sample_rate"] else None
    files = []

    # never let an export overwrite the master it is reading from
    planned = [os.path.join(a.outdir, f"{a.name}_{b}bit.wav") for b in ([24, 16] if a.also_16bit else [24])]
    if a.mp3 != "none":
        planned.append(os.path.join(a.outdir, f"{a.name}.mp3"))
    src_real = os.path.realpath(a.master)
    clash = [d for d in planned if os.path.realpath(d) == src_real
             or (os.path.exists(d) and os.path.samefile(d, a.master))]
    if clash:
        sys.exit(f"Refusing to export: {clash[0]} is the input master itself. Choose a different --name or --outdir.")

    for bits in ([24, 16] if a.also_16bit else [24]):
        dst = os.path.join(a.outdir, f"{a.name}_{bits}bit.wav")
        c = dithered_wav(a.master, dst, bits, rate, ch)
        if c:
            print(f"WARNING: {c} samples clipped while writing {dst}; the master exceeds full scale.")
        files.append(dst)

    if a.mp3 != "none":
        dst = os.path.join(a.outdir, f"{a.name}.mp3")
        q = ["-b:a", "320k"] if a.mp3 == "320" else ["-q:a", "0"]
        trim = 0.0  # always the gain actually encoded into the current MP3
        attempts = 4
        for attempt in range(attempts):
            filt = ([f"aresample={rate}{soxr_opt()}"] if rate else []) + ([f"volume={-trim:.2f}dB"] if trim else [])
            af = ["-af", ",".join(filt)] if filt else []
            subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", a.master, "-map", "a:0", *af,
                            "-c:a", "libmp3lame", *q, dst], check=True)
            _, mp3_tp, _ = measure(dst, mono)
            if a.mp3_max_tp is None or mp3_tp is None or mp3_tp <= a.mp3_max_tp:
                break
            if attempt == attempts - 1:
                sys.exit(f"MP3 true peak is still {mp3_tp:+.2f} dBTP after {attempts} encodes (trim {trim:.2f} dB), "
                         f"above --mp3-max-tp {a.mp3_max_tp}. Lower the master's ceiling and export again.")
            trim += mp3_tp - a.mp3_max_tp + 0.1
        if trim:
            print(f"MP3 encoding pushed true peak above {a.mp3_max_tp} dBTP, so the MP3 copy was turned down "
                  f"{trim:.2f} dB (the WAV master is unchanged).")
        files.append(dst)

    print(f"Source master: {src['codec']}, {src['sample_rate']} Hz, {ch} ch, {src['duration']:.3f} s")
    problems = 0
    for f in files:
        p = probe(f)
        I, tp, errors = measure(f, mono)
        dur_diff = p["duration"] - src["duration"]
        tol = 0.1 if p["codec"] == "mp3" else 0.002
        status = []
        if abs(dur_diff) > tol:
            status.append(f"duration differs by {dur_diff:+.3f} s")
        if p["channels"] != ch:
            status.append(f"channels {p['channels']} != {ch}")
        if p["sample_rate"] != (rate or src["sample_rate"]):
            status.append(f"sample rate {p['sample_rate']}")
        if errors:
            status.append("decoder errors: " + errors[0][:80])
        mp3_ceiling = 0.0 if a.mp3_max_tp is None or a.mp3_max_tp >= 99 else a.mp3_max_tp
        if p["codec"] == "mp3" and tp is not None and tp > mp3_ceiling:
            status.append(f"MP3 true peak {tp:+.1f} dBTP is above {mp3_ceiling:+.1f}; lower the master's ceiling")
        problems += bool(status)
        size = os.path.getsize(f) / 1e6
        print(f"  {os.path.basename(f):<40} {p['codec']:<10} {p['sample_rate']} Hz  "
              f"{(str(p['bits']) + '-bit') if p['bits'] else '':<7} {p['duration']:.3f} s  {size:.1f} MB  "
              f"{I if I is not None else 'n/a'} LUFS  TP {tp if tp is not None else 'n/a'} dBTP  "
              f"{'OK' if not status else 'CHECK: ' + '; '.join(status)}")
    print("All exports decoded and verified." if not problems else f"{problems} file(s) need attention.")


if __name__ == "__main__":
    main()

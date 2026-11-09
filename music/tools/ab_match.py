#!/usr/bin/env python3
"""Make a fair, loudness-matched A/B comparison between two versions of a song.

Louder almost always sounds "better" for a few seconds, which can hide a master
that is actually harsher, flatter or more distorted. This script measures the
integrated loudness of both files and turns the louder one down so they match,
then writes:

  <A>_matched.wav, <B>_matched.wav   full-length, loudness-matched copies
  AB_snippet.wav                     (with --snippet) A, a short pause, then B,
                                     from the same moment of the song, so the
                                     listener can compare on a phone in one file

Usage:
  python ab_match.py ORIGINAL.mp3 MASTER.wav --outdir ab/ --snippet 45 15
  python ab_match.py ORIGINAL.mp3 MASTER.wav --snippet 45 15 --blind
      (--blind shuffles the order and writes the answer key to a separate
       file so the listener can judge without knowing which is which)

Needs ffmpeg/ffprobe on PATH. Only lowers gain, so matching never clips.
"""
import argparse
import json
import os
import random
import re
import subprocess


def measure(path):
    run = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "a:0",
                          "-af", "ebur128=peak=true+sample", "-f", "null", "-"],
                         capture_output=True, text=True)
    err = run.stderr
    if "Summary:" not in err:
        raise SystemExit(f"Could not measure {path}:\n{err[-600:]}")
    summ = err[err.rindex("Summary:"):]
    I = float(re.search(r"I:\s*(-?[\d.]+)", summ).group(1))
    tp = re.search(r"True peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)", summ).group(1)
    sp = re.search(r"Sample peak:\s*\n\s*Peak:\s*(-?[\d.]+|-inf)", summ).group(1)
    return I, (-200.0 if tp == "-inf" else float(tp)), (-200.0 if sp == "-inf" else float(sp))


def rate_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=sample_rate", "-of", "json", path], capture_output=True, text=True)
    return int(json.loads(out.stdout)["streams"][0]["sample_rate"])


def stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def same_file(p, q):
    """True when p and q are the same file: equal after resolving symlinks, or the same device and inode
    (which also catches hard links)."""
    try:
        return os.path.samefile(p, q)
    except OSError:  # one of them does not exist yet: compare the resolved paths
        return os.path.realpath(p) == os.path.realpath(q)


def planned_outputs(args):
    outs = []
    if not args.no_full:
        outs += [os.path.join(args.outdir, f"A_{stem(args.a)}_matched.wav"),
                 os.path.join(args.outdir, f"B_{stem(args.b)}_matched.wav")]
    if args.snippet:
        outs.append(os.path.join(args.outdir, "AB_blind_snippet.wav" if args.blind else "AB_snippet.wav"))
        if args.blind:
            outs.append(os.path.join(args.outdir, "AB_blind_KEY_do_not_share_yet.txt"))
    return outs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a", help="version A (usually the original)")
    ap.add_argument("b", help="version B (usually the new mix/master)")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--snippet", nargs=2, type=float, metavar=("START_S", "LENGTH_S"),
                    help="also build a short A-then-B clip starting at START_S")
    ap.add_argument("--gap", type=float, default=0.8, help="silence between A and B in the snippet (s)")
    ap.add_argument("--blind", action="store_true", help="shuffle snippet order; key saved separately")
    ap.add_argument("--no-full", action="store_true", help="skip the full-length matched copies")
    args = ap.parse_args()
    # ffmpeg is run with -y, so an output that is one of the inputs (or a link to one) would be destroyed
    # before it is read. Check every planned output against both inputs before touching any file.
    for out in planned_outputs(args):
        for src in (args.a, args.b):
            if same_file(out, src):
                raise SystemExit(f"Refusing to write {out}: it is the same file as the input {src} "
                                 "(possibly through a link). Use a different --outdir or rename the input.")
    os.makedirs(args.outdir, exist_ok=True)

    Ia, tpa, spa = measure(args.a)
    Ib, tpb, spb = measure(args.b)
    target = min(Ia, Ib)
    ga, gb = target - Ia, target - Ib
    # keep a little headroom so 24-bit files never clip. Use the higher of sample and true peak: resampling to
    # the common rate can turn intersample (true) peaks into real samples above full scale.
    worst = max(max(spa, tpa) + ga, max(spb, tpb) + gb)
    extra = min(0.0, -0.3 - worst)
    ga, gb = ga + extra, gb + extra
    sr = max(rate_of(args.a), rate_of(args.b))

    print(f"A: {args.a}  {Ia:.1f} LUFS  true peak {tpa:+.1f} dBTP  -> gain {ga:+.1f} dB")
    print(f"B: {args.b}  {Ib:.1f} LUFS  true peak {tpb:+.1f} dBTP  -> gain {gb:+.1f} dB")
    print(f"Both now play at about {target + extra:.1f} LUFS. B was {Ib - Ia:+.1f} LU louder than A before matching.")

    norm = f"aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo"
    outputs = []
    if not args.no_full:
        for src, g, tag in ((args.a, ga, "A"), (args.b, gb, "B")):
            out = os.path.join(args.outdir, f"{tag}_{stem(src)}_matched.wav")
            subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", src, "-map", "a:0",
                            "-af", f"{norm},volume={g:.2f}dB", "-c:a", "pcm_s24le", out], check=True)
            outputs.append(out)

    if args.snippet:
        start, length = args.snippet
        order = [("A", args.a, ga), ("B", args.b, gb)]
        if args.blind:
            random.shuffle(order)
        fade = min(0.05, length / 4)
        parts = []
        for i, (_, _, g) in enumerate(order):
            parts.append(f"[{i}:a:0]{norm},atrim=start={start}:duration={length},asetpts=PTS-STARTPTS,"
                         f"volume={g:.2f}dB,afade=t=in:d={fade},afade=t=out:st={length - fade}:d={fade}[s{i}]")
        parts.append(f"anullsrc=r={sr}:cl=stereo,atrim=duration={args.gap},aformat=sample_fmts=fltp[gap]")
        parts.append("[s0][gap][s1]concat=n=3:v=0:a=1[out]")
        snip = os.path.join(args.outdir, "AB_blind_snippet.wav" if args.blind else "AB_snippet.wav")
        cmd = ["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", order[0][1], "-i", order[1][1],
               "-filter_complex", ";".join(parts), "-map", "[out]", "-c:a", "pcm_s24le", snip]
        subprocess.run(cmd, check=True)
        outputs.append(snip)
        if args.blind:
            key = os.path.join(args.outdir, "AB_blind_KEY_do_not_share_yet.txt")
            with open(key, "w") as fh:
                fh.write(f"First clip: {order[0][0]} ({order[0][1]})\nSecond clip: {order[1][0]} ({order[1][1]})\n")
            print(f"Blind snippet written; answer key saved to {key} (do not reveal until the listener chooses).")
        else:
            print(f"Snippet: A ({start:.0f}s-{start + length:.0f}s), {args.gap}s pause, then B.")

    for o in outputs:
        print(f"wrote {o}")


if __name__ == "__main__":
    main()

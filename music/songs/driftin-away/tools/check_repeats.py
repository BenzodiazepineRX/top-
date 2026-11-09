"""Every second-half repeat must sit at or under its version's limit against the main line it repeats.

usage: check_repeats.py [version ...]      (default: every version whose two stems exist in DRIFT_WORK)

Reads the vocal parts exactly as they enter the mix (stem_<version>_responses.wav, stem_<version>_background.wav,
written by build_mix.py) from the work folder, measures each repeat against the background vocal over the 2 bars
that end where the repeat ends, and compares with the version's limit (repeat_vs_main_db in build_mix.SETTINGS;
0 dB when a version has no limit). Exits 1 if any repeat is more than 0.1 dB over its limit, or a requested
version has no stems.
"""
import os
import sys

ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + ["v1"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_mix as bm  # noqa: E402

TOL = 0.1
D = bm.D
if ARGS:
    versions = ARGS
else:
    versions = sorted({f[len("stem_"):-len("_responses.wav")] for f in os.listdir(D)
                       if f.startswith("stem_") and f.endswith("_responses.wav")})
failed = False
for tag in versions:
    pr, pb = os.path.join(D, f"stem_{tag}_responses.wav"), os.path.join(D, f"stem_{tag}_background.wav")
    if not (os.path.exists(pr) and os.path.exists(pb)):
        print(f"{tag}: FAIL - stems not found in {D} (run build_mix.py {tag} first)")
        failed = True
        continue
    limit = bm.SETTINGS.get(tag, {}).get("repeat_vs_main_db", 0.0)
    r, _ = bm.dt.read(pr)
    b, _ = bm.dt.read(pb)
    d = [bm.loud(r, a, e) - bm.loud(b, e - 3.2, e) for a, e in bm.RESP]
    over = [k for k, v in enumerate(d) if v > limit + TOL]
    status = "FAIL" if over else "ok"
    failed |= bool(over)
    print(f"{tag}: {status} - limit {limit:+.1f} dB; repeat minus main line: " + " ".join(f"{v:+.1f}" for v in d)
          + (f" | over the limit: {', '.join(f'{bm.RESP[k][0]:.1f} s' for k in over)}" if over else ""))
sys.exit(1 if failed else 0)

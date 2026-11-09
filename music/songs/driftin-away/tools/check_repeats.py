"""Each second-half repeat vs the main line it answers, measured on the parts exactly as they enter the mix."""
import os
import sys
sys.argv = sys.argv[:1] + ["v4"]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_mix as bm
TAG = sys.argv[1] if len(sys.argv) > 1 else "v4"
for tag in ("v4",):
    try:
        r, _ = bm.dt.read(f"stem_{tag}_responses.wav"); b, _ = bm.dt.read(f"stem_{tag}_background.wav")
    except Exception:
        continue
    d = [bm.loud(r, a, e) - bm.loud(b, e - 3.2, e) for a, e in bm.RESP]
    print(f"{tag}: repeat minus main line (dB): " + " ".join(f"{v:+.1f}" for v in d) + f" | louder than the main: {sum(v > 0.05 for v in d)} of 16, max {max(d):+.1f}")

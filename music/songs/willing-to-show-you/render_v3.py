"""Revise v2's lead/beat balance from owner feedback, preserving its dry processing.

Run render_v2.py first to rebuild caches when starting from the original stems.
No new EQ, compression, tuning, or timing edit is applied to the cached stems.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np

SONG = Path(__file__).resolve().parent
REPO = SONG.parents[2]
TOOLS = REPO / "music/tools"
sys.path.insert(0, str(TOOLS))
import dsp_tools as dsp

CACHE = SONG / "work"
WORK = CACHE / "v3"
OUT = SONG / "exports"
WORK.mkdir(exist_ok=True)
LOG = []
LEAD_CHANGE_DB = -4.0
N, SR = 6256560, 44100


def run(args):
    args = list(map(str, args))
    r = subprocess.run(args, capture_output=True, text=True, cwd=REPO)
    LOG.append({"argv": args, "exit_code": r.returncode, "output": r.stdout + r.stderr})
    (SONG / "measurements/v3-command-log.json").write_text(json.dumps(LOG, indent=2) + "\n")
    if r.returncode:
        raise RuntimeError((r.stdout + r.stderr)[-3000:])
    print((r.stdout + r.stderr)[-1800:], flush=True)
    return r.stdout + r.stderr


def tool(name, *args):
    return run([sys.executable, TOOLS / name, *args])


def ff(inp, out, chain):
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y", "-i", inp,
                "-af", chain, "-c:a", "pcm_f32le", out])


for row in json.loads((SONG / "provenance/sources.json").read_text())["files"]:
    assert hashlib.sha256((SONG / row["path"]).read_bytes()).hexdigest() == row["sha256"]
routes = {"Beat.wav": 0.0, "Lead_bus.wav": LEAD_CHANGE_DB, "Adlibs_dry.wav": -8.0,
          "Lead_bus_delay.wav": LEAD_CHANGE_DB, "Adlibs_delay.wav": 0.0,
          "Lead_plate.wav": LEAD_CHANGE_DB}
manifest = {"feedback": "The main vocals are entirely too loud. This needs to be evened out perfectly",
            "revision": "Both primary leads and their lead-only effects -4 dB relative to v2; beat and adlibs retain v2 balance",
            "sample_rate": SR, "frames": N, "inputs": {}}
for name, gain in routes.items():
    path = CACHE / name
    assert path.exists(), f"Rebuild the v2 cache first: {path}"
    data, sr = dsp.read(str(path))
    assert sr == SR and len(data) <= N
    manifest["inputs"][name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "gain_db": gain, "frames": len(data)}
(SONG / "measurements/v3-routing.json").write_text(json.dumps(manifest, indent=2) + "\n")

mix = WORK / "Mix_v3.wav"
args = ["mix", mix]
for name, gain in routes.items():
    args.extend(["--track", f"{CACHE / name}:{gain}"])
tool("dsp_tools.py", *args)
data, _ = dsp.read(str(mix))
assert len(data) == N
trim_db = min(0.0, -6 - float(dsp.db(np.max(np.abs(data)))))
edge = WORK / "Mix_edges_v3.wav"
ff(mix, edge, f"highpass=f=5:p=2,afade=t=in:d=0.003,afade=t=out:st={N/SR-.8}:d=0.8,volume={trim_db}dB")
premaster = WORK / "Premaster_v3.wav"
tool("dsp_tools.py", "ms-bus", edge, premaster, "--side-hp", 90, "--mid-shelf", "")
master = WORK / "Master_v3_float.wav"
tool("render_master.py", premaster, master, "--target-lufs", -11.5, "--ceiling", -1.3,
     "--attack", 5, "--release", 100, "--max-limiter-db", 2)
tool("export_master.py", master, "--name", "Willing_To_Show_You_Master_v3", "--outdir", OUT,
     "--rate", SR, "--mp3", 320, "--mp3-max-tp", -1)
settings = json.loads(Path(str(master) + ".settings.json").read_text())
(SONG / "measurements/v3-master-settings.json").write_text(json.dumps(settings, indent=2) + "\n")

# Keep the complete inherited processing log, then describe the revised routing
# and exact new bus/master stages. Do not claim the caches were reprocessed.
effects = json.loads((SONG / "effects/v2.json").read_text())
effects = [e for e in effects if e["track"] not in ("Mix bus", "Master", "Delivery")]
for e in effects:
    e["provenance"] = "Inherited unchanged from v2; source settings and measurements remain in effects/v2.json"
effects += [
    {"track": "Both primary leads and their lead-only wet returns", "effect": "Owner-requested vocal balance reduction",
     "type": "gain", "tool": "dsp_tools.py mix", "settings": "Dry Lead_bus -4 dB; its delay -4 dB; its plate -4 dB relative to v2. Both individual leads total -6 dB after their cached working-level processing.",
     "measured": {"lead_to_beat_change_db": -4.0}, "why": "Owner heard the main vocals as entirely too loud; the same correction preserves their alternating-take balance. Beat/adlib gains stay unchanged."},
    {"track": "Mix bus", "effect": "DC blocking, edges and headroom", "type": "bus", "tool": "FFmpeg",
     "settings": f"5 Hz order2 HP; 3 ms opening/.8 s ending fade; uniform trim {trim_db:.6f} dB; {N} frames",
     "why": "Keep the earlier duration and edge treatment with fresh headroom."},
    {"track": "Mix bus", "effect": "Sub-side cleanup", "type": "low-end", "tool": "dsp_tools.py ms-bus",
     "settings": "90 Hz side high-pass; mid shelf off", "why": "Retain the earlier low-end routing."},
    {"track": "Master", "effect": "Master limiting", "type": "limiter", "tool": "render_master.py",
     "settings": "4x; attack5/release100ms; target -11.5 LUFS, ceiling -1.3 dBTP; compensated latency, auto-level off",
     "measured": settings, "why": "Keep comparable overall loudness while preserving the revised voice/beat ratio."},
    {"track": "Delivery", "effect": "WAV and MP3 export", "type": "bus", "tool": "export_master.py",
     "settings": "44.1 kHz stereo; 24-bit TPDF WAV; 320 kbps MP3; decoded peak ceiling -1 dBTP",
     "why": "Create new versioned files; keep v2 available for comparison."}
]
(SONG / "effects/v3.json").write_text(json.dumps(effects, indent=2) + "\n")
wav = OUT / "Willing_To_Show_You_Master_v3_24bit.wav"
mp3 = OUT / "Willing_To_Show_You_Master_v3.mp3"
tool("analyze_audio.py", wav, mp3, "--reference", OUT / "Willing_To_Show_You_Master_v2_24bit.wav",
     "--json", SONG / "measurements/v3-analysis.json")
for label, src in (("V2", OUT / "Willing_To_Show_You_Master_v2_24bit.wav"), ("V3", wav)):
    run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", 42, "-i", src, "-t", 15,
         "-c:a", "pcm_f32le", WORK / f"AB_{label}.wav"])
tool("ab_match.py", WORK / "AB_V2.wav", WORK / "AB_V3.wav", "--outdir", OUT / "comparison-v3",
     "--snippet", 0, 15, "--no-full")
run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", OUT / "comparison-v3/AB_snippet.wav",
     "-af", "volume=-1.5dB", "-c:a", "libmp3lame", "-b:a", "320k", OUT / "Willing_To_Show_You_v2_then_v3_AB.mp3"])
tool("song_report.py", SONG, "--version", "v3", "--master", wav, "--mp3", mp3,
     "--pre-limiter", premaster, "--settings", str(master) + ".settings.json",
     "--previous", OUT / "Willing_To_Show_You_Master_v2_24bit.wav", "--effects", SONG / "effects/v3.json")
print("V3 rendered. Inspect report and measurements before delivery.")

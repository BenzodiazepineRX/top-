"""Render this song using the workspace toolkit; audio remains local/ignored.

Run from the repository root with the four original WAVs in this song's source/.
Tone and balance are provisional; no script can approve subjective sound quality.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

SONG = Path(__file__).resolve().parent
REPO = SONG.parents[2]
TOOLS = REPO / "music/tools"
sys.path.insert(0, str(TOOLS))
import dsp_tools as dsp
import numpy as np

WORK, OUT = SONG / "work", SONG / "exports"
for path in (WORK, OUT, SONG / "effects", SONG / "reports", SONG / "measurements"):
    path.mkdir(exist_ok=True)
LOG, EFFECTS = [], []
BPM = 135.0
TARGET_LUFS = -11.5
SOURCES = {"Lead 1": SONG / "source/LEAD 1.wav", "Lead 2": SONG / "source/LEAD 2.wav",
           "Adlibs": SONG / "source/BACKGROUNDADLIBS.wav", "Beat": next((SONG / "source").glob("Y2Mate*.wav"))}


def run(args):
    args = list(map(str, args))
    result = subprocess.run(args, capture_output=True, text=True, cwd=REPO)
    output = result.stdout + result.stderr
    LOG.append({"argv": args, "exit_code": result.returncode, "output": output})
    (SONG / "measurements/v2-command-log.json").write_text(json.dumps(LOG, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError(output[-3000:])
    print(output[-2000:], flush=True)
    return output


def tool(name, *args):
    return run([sys.executable, TOOLS / name, *args])


def ff(inp, out, filters):
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y", "-i", inp,
                "-af", filters, "-c:a", "pcm_f32le", out])


def effect(track, name, kind, plugin, settings, why, measured=None, issues=None):
    EFFECTS.append({"track": track, "effect": name, "type": kind, "tool": plugin,
                    "settings": settings, "why": why, "measured": measured or {}, "issues": issues or []})


manifest = json.loads((SONG / "provenance/sources.json").read_text())
for row in manifest["files"]:
    path = SONG / row["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], path
beat, SR = dsp.read(str(SOURCES["Beat"]))
N = len(beat)
assert SR == 44100 and N == 6256560
if not (SONG / "measurements/source-analysis.json").exists():
    tool("analyze_audio.py", *SOURCES.values(), "--json", SONG / "measurements/source-analysis.json")
if not (SONG / "measurements/tempo-key-used.json").exists():
    tool("tempo_key.py", SOURCES["Beat"], "--bpm", BPM, "--json", SONG / "measurements/tempo-key-used.json")
tracks = {}
for name in ("Lead 1", "Lead 2", "Adlibs"):
    label = name.replace(" ", "_")
    stage, hp, tone, ess, comp, caught = [WORK / f"{label}_{s}.wav" for s in
                                         ("stage", "hp", "tone", "ess", "comp", "dry")]
    tool("dsp_tools.py", "gain-stage", SOURCES[name], stage, "--target-rms", -18, "--against", SOURCES["Beat"])
    effect(name, "Active-level gain staging", "gain", "dsp_tools.py gain-stage", "target gated RMS -18 dBFS", "Comparable working levels for alternating primary leads and support processing")
    cutoff = 150 if name == "Adlibs" else 85
    tool("dsp_tools.py", "hpf", stage, hp, "--freq", cutoff, "--order", 2)
    effect(name, "Rumble high-pass", "hpf", "dsp_tools.py hpf", f"{cutoff} Hz, order 2", "Retain v1's low-cut choice; higher support cutoff reduces low-mid overlap", {"freq_hz": cutoff}, ["Lowest vocal fundamental and subjective chest/body preservation remain unverified"] if name != "Adlibs" else None)
    eq = ("equalizer=f=350:t=q:w=1:g=-2.5,equalizer=f=2400:t=q:w=0.8:g=1.5" if name == "Adlibs" else
          "extrastereo=m=0.35:c=false,equalizer=f=350:t=q:w=1:g=-2,equalizer=f=2600:t=q:w=0.7:g=2.2,treble=g=1:f=6500")
    ff(hp, tone, eq)
    if name != "Adlibs":
        effect(name, "Centered dry image", "bus", "FFmpeg extrastereo", "side multiplier 0.35, clipping disabled", "Both alternating leads remain primary and near center")
    for filt in eq.split(","):
        if not filt.startswith("extrastereo"):
            effect(name, "Provisional tonal EQ", "eq", "FFmpeg", filt, "Retain v1's mild broad tone proposal; source spectrum is concentrated in low mids; not a verified ringing repair")
    msg = tool("dsp_tools.py", "deess", tone, ess, "--low", 5500, "--high", 8500,
               "--auto-pct", 99, "--ratio", 3, "--max-cut", 3)
    found = re.search(r"reducing ([\d.]+)% of active time, average ([\d.]+) dB", msg)
    assert found, msg
    effect(name, "Limited split-band de-essing", "deess", "dsp_tools.py deess", "5500–8500 Hz; auto percentile 99; ratio 3; max 3 dB", "Control only upper-band outliers while limiting maximum tonal change", {"pct_active": float(found[1]), "avg_db": float(found[2])})
    msg = tool("dsp_tools.py", "comp2", ess, comp, "--peak-threshold", -12, "--peak-attack", 2,
               "--peak-release", 60, "--smooth-threshold", -22, "--smooth-attack", 10,
               "--smooth-release", 200)
    found = re.search(r"Average gain reduction ([\d.]+) dB", msg)
    assert found, msg
    effect(name, "Serial peak and phrase control", "comp", "dsp_tools.py comp2", "peak -12 dB/5:1/2 ms/60 ms; smooth -22 dB/2.5:1/10 ms/200 ms; automatic makeup", "Control recording spikes and phrase level in a dense rap arrangement", {"avg_gr_db": float(found[1])})
    ff(comp, caught, "alimiter=limit=-9dB:attack=2:release=60:level=false:latency=true")
    before, _ = dsp.read(str(comp)); after, _ = dsp.read(str(caught))
    block = SR // 20
    count = min(len(before), len(after)) // block
    def levels(x):
        return 10 * np.log10(np.mean(x[:count * block].reshape(count, block, 2) ** 2, axis=(1, 2)) + 1e-15)
    lb, la = levels(before), levels(after)
    active = lb > max(-60, lb.max() - 35)
    reduction = (lb - la)[active]
    stats = {"average_gr_db": float(reduction.mean()), "p95_gr_db": float(np.percentile(reduction, 95)),
             "worst_50ms_gr_db": float(reduction.max()), "active_pct_over_1db": float(100 * (reduction > 1).mean())}
    effect(name, "Post-makeup peak control", "limiter", "FFmpeg alimiter", "-9 dBFS; 2 ms attack; 60 ms release; auto-level off; latency compensated", "Contain post-makeup peaks before summing; workload is measured, and audible compression still requires owner review", stats)
    original, rate = dsp.read(str(SOURCES[name])); data, rate2 = dsp.read(str(caught))
    assert rate == rate2 == SR and len(original) == len(data)
    tracks[name] = caught

beat_out = WORK / "Beat.wav"
ff(SOURCES["Beat"], beat_out, "highpass=f=25:p=1,volume=-4dB")
tracks["Beat"] = beat_out
effect("Beat", "Gentle subsonic cut", "hpf", "FFmpeg highpass", "25 Hz, one pole", "Remove subsonic energy with minimal change to the stereo beat", {"freq_hz": 25})
effect("Beat", "Instrumental balance", "gain", "FFmpeg volume", "-4 dB", "Make relative room for the leads without separately altering unavailable drum/808 stems")
lead_bus = WORK / "Lead_bus.wav"
tool("dsp_tools.py", "mix", lead_bus, "--track", f"{tracks['Lead 1']}:-2", "--track", f"{tracks['Lead 2']}:-2")
effect("Lead bus", "Equal lead balance", "gain", "dsp_tools.py mix", "both leads -2 dB; both start at zero", "Alternating phrases receive equal priority")
effect("Adlibs", "Supporting balance", "gain", "dsp_tools.py mix", "-8 dB after working-level processing", "Keep adlibs behind both primary leads")
returns = []
for name, source, ret in (("Lead bus", lead_bus, -27), ("Adlibs", tracks["Adlibs"], -31)):
    out = WORK / (name.replace(" ", "_") + "_delay.wav")
    tool("dsp_tools.py", "delay", source, out, "--bpm", BPM, "--note", "1/16", "--feedback", .25,
         "--max-taps", 3, "--hp", 300, "--lp", 4200, "--return-db", ret,
         "--duck-by", lead_bus, "--duck-depth", 3, "--duck-attack", 5, "--duck-release", 111.111111)
    effect(name, "Quiet timed density delay", "delay", "dsp_tools.py delay", f"1/16; feedback .25; 3 repeats; 300–4200 Hz; return {ret} dB; 3 dB duck; attack 5 ms/release 1/16", "Replace free-time ambience without introducing prominent line-end throws", {"note": "1/16", "ms": 60000 / BPM / 4, "bpm": BPM, "ducked": True})
    returns.append(out)
plate = WORK / "Lead_plate.wav"
tool("dsp_tools.py", "reverb", lead_bus, plate, "--type", "plate", "--predelay", 60000 / BPM / 16,
     "--decay", 60 / BPM, "--hp", 300, "--lp", 4200, "--width", .7, "--return-db", -27,
     "--duck-by", lead_bus, "--duck-depth", 3)
effect("Lead bus", "Short ducked plate", "reverb", "dsp_tools.py reverb", "plate; pre-delay 1/64; nominal decay 1/4; width .7; return -27 dB; duck 3 dB", "Understated space consistent with the proposed dry vocal direction", {"bpm": BPM, "predelay_ms": 60000 / BPM / 16, "decay_s": 60 / BPM})
returns.append(plate)
mixed = WORK / "Mix_with_tails.wav"
args = ["mix", mixed, "--track", f"{beat_out}:0", "--track", f"{lead_bus}:0", "--track", f"{tracks['Adlibs']}:-8"]
for wet in returns:
    args += ["--track", f"{wet}:0"]
tool("dsp_tools.py", *args)
data, rate = dsp.read(str(mixed))
assert len(data) >= N and (len(data) == N or np.max(np.abs(data[N:])) < 1e-5), "Unexpected audible effect tail beyond the source song"
trim_db = min(0.0, -6 - float(dsp.db(np.max(np.abs(data[:N])))))
edge = WORK / "Mix_edges.wav"
ff(mixed, edge, f"atrim=end_sample={N},highpass=f=5:p=2,afade=t=in:d=0.003,afade=t=out:st={N/SR-.8}:d=0.8,volume={trim_db}dB")
effect("Mix bus", "DC blocking", "hpf", "FFmpeg highpass", "5 Hz, order 2, before mastering", "Remove measured mix DC offset before master gain", {"freq_hz": 5})
effect("Mix bus", "Headroom and edge fades", "gain", "FFmpeg", f"{trim_db:.6f} dB; 3 ms opening / .8 s ending edge fade; exactly {N} frames", "Preserve arrangement duration and leave uniform mix headroom")
premaster = WORK / "Premaster_v2.wav"
tool("dsp_tools.py", "ms-bus", edge, premaster, "--side-hp", 90, "--mid-shelf", "")
effect("Mix bus", "Sub-side cleanup", "low-end", "dsp_tools.py ms-bus", "90 Hz side high-pass, zero phase; mid shelf bypassed", "Keep the already-centered sub stable; avoid an unrequested global brightness lift")
master_float = WORK / "Master_v2_float.wav"
tool("render_master.py", premaster, master_float, "--target-lufs", TARGET_LUFS, "--ceiling", -1.3,
     "--attack", 5, "--release", 100, "--max-limiter-db", 2)
effect("Master", "Oversampled master limiting", "limiter", "render_master.py", f"4x; 5 ms attack/100 ms release; {TARGET_LUFS} LUFS target; -1.3 dBTP ceiling", "Back off the first attempt's -10.5 target to preserve contrast and reduce limiting; not a claimed reference match")
tool("export_master.py", master_float, "--name", "Willing_To_Show_You_Master_v2", "--outdir", OUT,
     "--rate", SR, "--mp3", 320, "--mp3-max-tp", -1)
effect("Delivery", "24-bit dither and MP3 encoding", "bus", "export_master.py", "44.1 kHz/24-bit TPDF WAV; 320 kbps MP3, decoded ceiling -1 dBTP", "Final integer quantization once; independently decode both delivery formats")
(SONG / "effects/v2.json").write_text(json.dumps(EFFECTS, indent=2) + "\n")
raw = WORK / "Original_sum.wav"
args = ["mix", raw]
for source in SOURCES.values():
    args += ["--track", f"{source}:0"]
tool("dsp_tools.py", *args)
master_wav = OUT / "Willing_To_Show_You_Master_v2_24bit.wav"
tool("analyze_audio.py", master_wav, OUT / "Willing_To_Show_You_Master_v2.mp3", "--reference", raw,
     "--json", SONG / "measurements/v2-analysis.json")
for title, path in (("Source", raw), ("V2", master_wav)):
    run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", 42, "-i", path, "-t", 15,
         "-c:a", "pcm_f32le", WORK / f"AB_{title}.wav"])
tool("ab_match.py", WORK / "AB_Source.wav", WORK / "AB_V2.wav", "--outdir", OUT / "comparison",
     "--snippet", 0, 15, "--no-full")
run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", OUT / "comparison/AB_snippet.wav",
     "-af", "volume=-1.5dB", "-c:a", "libmp3lame", "-b:a", "320k", OUT / "Willing_To_Show_You_Source_then_v2_AB.mp3"])
tool("song_report.py", SONG, "--version", "v2", "--master", master_wav,
     "--mp3", OUT / "Willing_To_Show_You_Master_v2.mp3", "--pre-limiter", premaster,
     "--settings", str(master_float) + ".settings.json", "--original", raw,
     "--effects", SONG / "effects/v2.json")
summary = re.search(r"\b(\d+) failed\b", (SONG / "reports/v2.md").read_text())
assert summary and int(summary[1]) == 0, "Fix failed review items before delivery"
print("Workspace v2 rendered; review warnings and listening sign-off remain pending.")

"""Quieter, softer lead revision from owner feedback; keep v2/v3 intact.

Rebuild render_v2.py first if the validated input caches are missing.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import numpy as np

SONG = Path(__file__).resolve().parent
REPO = SONG.parents[2]
TOOLS = REPO / "music/tools"
sys.path.insert(0, str(TOOLS))
import dsp_tools as dsp

CACHE, WORK, OUT = SONG / "work", SONG / "work/v4", SONG / "exports"
WORK.mkdir(exist_ok=True)
SR, N, BPM = 44100, 6256560, 135.0
LOG, EFFECTS, LEVELS = [], [], {}


def run(args):
    args = list(map(str, args))
    r = subprocess.run(args, capture_output=True, text=True, cwd=REPO)
    LOG.append({"argv": args, "exit_code": r.returncode, "output": r.stdout + r.stderr})
    (SONG / "measurements/v4-command-log.json").write_text(json.dumps(LOG, indent=2) + "\n")
    if r.returncode:
        raise RuntimeError((r.stdout + r.stderr)[-3000:])
    print((r.stdout + r.stderr)[-1500:], flush=True)
    return r.stdout + r.stderr


def tool(name, *args):
    return run([sys.executable, TOOLS / name, *args])


def ff(src, dst, chain):
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y", "-i", src,
                "-af", chain, "-c:a", "pcm_f32le", dst])


def effect(track, title, kind, tool_name, settings, why, measured=None):
    EFFECTS.append({"track": track, "effect": title, "type": kind, "tool": tool_name,
                    "settings": settings, "why": why, "measured": measured or {}})


for row in json.loads((SONG / "provenance/sources.json").read_text())["files"]:
    assert hashlib.sha256((SONG / row["path"]).read_bytes()).hexdigest() == row["sha256"]
inherited = json.loads((SONG / "effects/v2.json").read_text())
EFFECTS.extend(e for e in inherited if e["track"] in ("Beat", "Adlibs"))
lead_paths = []
for i in (1, 2):
    name = f"Lead {i}"
    stage, old = CACHE / f"Lead_{i}_stage.wav", CACHE / f"Lead_{i}_dry.wav"
    hp, tone, ess, comp, caught, dry = [WORK / f"Lead_{i}_{s}.wav" for s in
                                      ("hp", "tone", "ess", "comp", "caught", "dry")]
    effect(name, "Validated source working gain", "gain", "v2 cached gain-stage",
           "Same source gain as v2, before EQ/dynamics; final attenuation occurs after processing",
           "Preserve source timing and avoid rerunning a different normalization before the revised tone")
    tool("dsp_tools.py", "hpf", stage, hp, "--freq", 75, "--order", 2)
    effect(name, "Gentler rumble cut", "hpf", "dsp_tools.py hpf", "75 Hz, order2; previously85 Hz",
           "Retain a little more low vocal body while reducing brightness", {"freq_hz": 75})
    chain = "extrastereo=m=0.35:c=false,equalizer=f=350:t=q:w=1:g=-3,treble=g=-1:f=5500"
    ff(hp, tone, chain)
    effect(name, "Centered dry image", "bus", "FFmpeg extrastereo", "side multiplier .35, clipping off", "Retain the centered alternating leads")
    effect(name, "Broad low-mid adjustment", "eq", "FFmpeg equalizer", "350 Hz, Q1, -3 dB",
           "Owner reports boxiness; about half the measured source energy is in300–650 Hz. Harmonic-spaced peaks do not justify surgical notches.")
    effect(name, "Remove earlier presence and treble boosts", "eq", "FFmpeg",
           "No +2.2 dB/2600 Hz presence boost, no +1 dB/6500 Hz shelf; instead a gentle -1 dB shelf at5500 Hz",
           "Owner says the earlier mix sounds as if treble is turned up")
    msg = tool("dsp_tools.py", "deess", tone, ess, "--low", 5500, "--high", 8500,
               "--auto-pct", 99, "--ratio", 3, "--max-cut", 3)
    m = re.search(r"reducing ([\d.]+)% of active time, average ([\d.]+) dB", msg)
    assert m
    effect(name, "Selective de-essing", "deess", "dsp_tools.py deess", "5500–8500; percentile99; ratio3; max3 dB",
           "Retain selective control rather than suppressing the whole vocal", {"pct_active": float(m[1]), "avg_db": float(m[2])})
    msg = tool("dsp_tools.py", "comp2", ess, comp, "--peak-threshold", -12, "--peak-attack", 2,
               "--peak-release", 60, "--smooth-threshold", -22, "--smooth-attack", 10, "--smooth-release", 200)
    m = re.search(r"Average gain reduction ([\d.]+) dB", msg)
    assert m
    effect(name, "Existing serial dynamics settings", "comp", "dsp_tools.py comp2",
           "peak -12 dB/5:1/2ms/60ms; smooth -22 dB/2.5:1/10ms/200ms; auto makeup",
           "Keep the earlier dynamics approach; apply the requested level correction afterwards", {"avg_gr_db": float(m[1])})
    ff(comp, caught, "alimiter=limit=-9dB:attack=2:release=60:level=false:latency=true")
    effect(name, "Post-makeup peak control", "limiter", "FFmpeg alimiter", "-9dBFS,2ms/60ms; level off; latency compensated", "Retain the existing post-compression ceiling")
    before, sr = dsp.read(str(old)); after, sr2 = dsp.read(str(caught))
    assert sr == sr2 == SR and len(before) == len(after)
    block = SR // 20
    k = len(before) // block
    def powers(x):
        return np.mean(x[:k * block].reshape(k, block, 2) ** 2, axis=(1, 2))
    old_power, new_power = powers(before), powers(after)
    old_db = 10 * np.log10(old_power + 1e-15)
    mask = old_db > max(-60, old_db.max() - 35)
    old_level = float(10 * np.log10(old_power[mask].mean()))
    new_level = float(10 * np.log10(new_power[mask].mean()))
    # V3 individual dry lead gain was -6 dB. Match its same-window level, then
    # subtract another3.5 dB AFTER all automatic makeup and peak control.
    target = old_level - 6 - 3.5
    gain = target - new_level
    ff(caught, dry, f"volume={gain:.9f}dB")
    printed, _ = dsp.read(str(dry))
    actual = float(10 * np.log10(powers(printed)[mask].mean()))
    assert abs(actual - target) < .001
    LEVELS[name] = {"baseline_v2_cache_sha256": hashlib.sha256(old.read_bytes()).hexdigest(),
                    "stage_cache_sha256": hashlib.sha256(stage.read_bytes()).hexdigest(),
                    "old_v3_active_dbfs": old_level - 6, "new_v4_active_dbfs": actual,
                    "change_from_v3_db": actual - (old_level - 6), "post_processing_gain_db": gain,
                    "mask": "unchanged v2 dry50ms channel-energy blocks above max(-60, max-35)"}
    effect(name, "Post-processing level reduction", "gain", "FFmpeg volume",
           f"{gain:.6f} dB after dynamics; same-window RMS3.5 dB below v3",
           "Honor the repeated too-loud feedback without automatic makeup undoing it", LEVELS[name])
    lead_paths.append(dry)
lead = WORK / "Lead_bus_v4.wav"
tool("dsp_tools.py", "mix", lead, "--track", f"{lead_paths[0]}:0", "--track", f"{lead_paths[1]}:0")
wet = []
delay = WORK / "Lead_delay_v4.wav"
tool("dsp_tools.py", "delay", lead, delay, "--bpm", BPM, "--note", "1/16", "--feedback", .25,
     "--max-taps", 3, "--hp", 400, "--lp", 4200, "--return-db", -30,
     "--duck-by", lead, "--duck-depth", 3, "--duck-attack", 5, "--duck-release", 111.111111)
effect("Lead bus", "Quieter timed density delay", "delay", "dsp_tools.py delay",
       "1/16;4900samples; feedback.25;3taps;400–4200Hz;return-30;duck3dB",
       "Keep main ambience down with the quieter dry voice and reduce wet low-mid buildup",
       {"note": "1/16", "ms": 60000/BPM/4, "bpm": BPM, "ducked": True})
wet.append(delay)
plate = WORK / "Lead_plate_v4.wav"
tool("dsp_tools.py", "reverb", lead, plate, "--type", "plate", "--predelay", 60000/BPM/16,
     "--decay", 60/BPM, "--hp", 400, "--lp", 4200, "--width", .7, "--return-db", -30,
     "--duck-by", lead, "--duck-depth", 3)
effect("Lead bus", "Quieter short plate", "reverb", "dsp_tools.py reverb",
       "1/64predelay,1/4decay;400–4200Hz;return-30;duck3dB",
       "Make the revised softer voice drier and reduce low-mid ambience",
       {"predelay_ms": 60000/BPM/16, "decay_s": 60/BPM, "bpm": BPM})
wet.append(plate)
mix = WORK / "Mix_v4.wav"
tool("dsp_tools.py", "mix", mix, "--track", f"{CACHE/'Beat.wav'}:0", "--track", f"{lead}:0",
     "--track", f"{CACHE/'Adlibs_dry.wav'}:-10.5", "--track", f"{CACHE/'Adlibs_delay.wav'}:-2.5",
     "--track", f"{wet[0]}:0", "--track", f"{wet[1]}:0")
effect("Adlibs", "Keep support below quieter main", "gain", "dsp_tools.py mix",
       "additional-2.5dB on existing dry and delay; dry total-10.5dB", "Prevent support becoming dominant after the further main-vocal reduction")
data, _ = dsp.read(str(mix)); assert len(data) == N
trim = min(0.0, -6 - float(dsp.db(np.max(np.abs(data)))))
edges = WORK / "Mix_edges_v4.wav"
ff(mix, edges, f"highpass=f=5:p=2,afade=t=in:d=0.003,afade=t=out:st={N/SR-.8}:d=0.8,volume={trim}dB")
pre = WORK / "Premaster_v4.wav"
tool("dsp_tools.py", "ms-bus", edges, pre, "--side-hp", 90, "--mid-shelf", "")
effect("Mix bus", "Existing edges and sub-side routing", "bus", "FFmpeg;dsp_tools.py ms-bus",
       f"5HzDCcut;3ms/.8s edges;{trim:.6f}dB trim;90Hz sideHP;no high shelf", "Keep duration and beat processing; add no overall treble")
master = WORK / "Master_v4_float.wav"
tool("render_master.py", pre, master, "--target-lufs", -12.5, "--ceiling", -1.3,
     "--attack", 5, "--release", 100, "--max-limiter-db", 2)
tool("export_master.py", master, "--name", "Willing_To_Show_You_Master_v4", "--outdir", OUT,
     "--rate", SR, "--mp3", 320, "--mp3-max-tp", -1)
settings = json.loads(Path(str(master)+".settings.json").read_text())
(SONG/"measurements/v4-master-settings.json").write_text(json.dumps(settings, indent=2)+"\n")
(SONG/"measurements/v4-lead-levels.json").write_text(json.dumps(LEVELS, indent=2)+"\n")
effect("Master", "Gentler overall delivery level", "limiter", "render_master.py;export_master.py",
       "-12.5LUFS target;4x oversampling;5ms/100ms;-1.3dBTP ceiling;24-bit WAV+320kbpsMP3",
       "Owner still hears loudness; quieter delivery accompanies the independent voice/beat reduction", settings)
(SONG/"effects/v4.json").write_text(json.dumps(EFFECTS, indent=2)+"\n")
wav, mp3 = OUT/"Willing_To_Show_You_Master_v4_24bit.wav", OUT/"Willing_To_Show_You_Master_v4.mp3"
tool("analyze_audio.py", wav, mp3, "--reference", OUT/"Willing_To_Show_You_Master_v3_24bit.wav",
     "--json", SONG/"measurements/v4-analysis.json")
for label, src in (("V3", OUT/"Willing_To_Show_You_Master_v3_24bit.wav"), ("V4", wav)):
    run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", 42, "-i", src, "-t", 15,
         "-c:a", "pcm_f32le", WORK/f"AB_{label}.wav"])
tool("ab_match.py", WORK/"AB_V3.wav", WORK/"AB_V4.wav", "--outdir", OUT/"comparison-v4", "--snippet", 0, 15, "--no-full")
run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", OUT/"comparison-v4/AB_snippet.wav",
     "-af", "volume=-1.5dB", "-c:a", "libmp3lame", "-b:a", "320k", OUT/"Willing_To_Show_You_v3_then_v4_AB.mp3"])
tool("song_report.py", SONG, "--version", "v4", "--master", wav, "--mp3", mp3,
     "--pre-limiter", pre, "--settings", str(master)+".settings.json",
     "--previous", OUT/"Willing_To_Show_You_Master_v3_24bit.wav", "--effects", SONG/"effects/v4.json")
print("V4 rendered; inspect report, levels and final decoded delivery before review.")

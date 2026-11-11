#!/usr/bin/env python3
"""Write a review report ("report card") for one version of a song.

Every version of every song gets one. It measures the master, checks how hard the limiter worked
(including the short volume dips listeners hear as pumping), compares the tone with the original or a
reference, reviews every effect and plugin in the version's effects log against its own rule, checks the
song brief for missing facts and unbuilt creative-effect requests, and ends with one list: what is still
needed before this song is as close to perfect as it can be.

The tools measure; they do not listen. A report with no FAIL or WARN lines means "ready for the owner's
listening checks", never "finished". A song is finished only when the owner signs off in mix-notes.md.

Usage:
  python3 music/tools/song_report.py music/songs/<song> --version v2 \\
      --master Song_master_v2_24bit.wav --mp3 Song_master_v2.mp3 \\
      --pre-limiter mix_v2_ms.wav --settings master_v2.wav.settings.json \\
      --original original_mix.wav --effects music/songs/<song>/effects/v2.json

Writes music/songs/<song>/reports/<version>.md. See music/tools/workflow.md, step 7, for the effects
log format and every rule.
"""
import argparse
import json
import math
import os
import re
import sys
from datetime import date

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_audio as aa  # noqa: E402
import dsp_tools as dt  # noqa: E402

PASS, WARN, FAIL, INFO = "PASS", "WARN", "FAIL", "INFO"
ICON = {PASS: "✅", WARN: "⚠️", FAIL: "❌", INFO: "ℹ️"}
NOTE_FACTORS = {"2/1": 8, "1/1d": 6, "1/1": 4, "1/2": 2, "1/2d": 3, "1/4": 1, "1/4d": 1.5, "1/4t": 2 / 3, "1/8": 0.5, "1/8d": 0.75,
                "1/8t": 1 / 3, "1/16": 0.25, "1/16d": 0.375, "1/32": 0.125, "1/64": 1 / 16, "1/128": 1 / 32}


class Review:
    def __init__(self):
        self.rows = {}      # section -> list of (status, check, value, action)
        self.todo = []      # (status, text)

    def add(self, section, status, check, value, action=""):
        self.rows.setdefault(section, []).append((status, check, value, action))
        if status in (WARN, FAIL) and action:
            self.todo.append((status, f"{check}: {action}"))

    def count(self, status):
        return sum(1 for rows in self.rows.values() for r in rows if r[0] == status)


def grade(value, ok, warn):
    """ok/warn are callables returning True when the value passes that level."""
    if value is None:
        return WARN
    return PASS if ok(value) else WARN if warn(value) else FAIL


def note_ms(bpm, note):
    return 60000.0 / bpm * NOTE_FACTORS[note]


def nearest_note(bpm, ms):
    best = min(NOTE_FACTORS, key=lambda n: abs(note_ms(bpm, n) - ms))
    return best, note_ms(bpm, best)


# ------------------------------------------------------------------ brief and notes

def read_text(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def brief_field(brief, name):
    m = re.search(rf"\*\*{re.escape(name)}:\*\*\s*(.*)", brief)
    return m.group(1).strip() if m else ""


def brief_bpm(brief):
    m = re.search(r"\*\*BPM:\*\*\s*([\d.]+)", brief)
    return float(m.group(1)) if m else None


def brief_unknowns(brief):
    out = []
    for line in brief.splitlines():
        s = line.strip()
        if re.search(r"\bunknown\b", s, re.I) and not s.startswith(">") and not s.lower().startswith("if you"):
            out.append(re.sub(r"[*`]", "", s.lstrip("-0123456789. ")).strip())
    return out


def brief_effect_requests(brief):
    """Rows of the Creative effects requests table that are real requests."""
    sec = brief.split("## Creative effects requests", 1)
    if len(sec) < 2:
        return []
    body = sec[1].split("\n## ", 1)[0]
    rows = []
    for line in body.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0] in ("Effect", "") or cells[0].lower().startswith("none"):
            continue
        rows.append(cells)
    return rows


def unchecked_signoff(notes):
    sec = notes.split("## Final sign-off", 1)
    if len(sec) < 2:
        return []
    return [re.sub(r"^- \[ \]\s*", "", l.strip()) for l in sec[1].splitlines() if l.strip().startswith("- [ ]")]


# ------------------------------------------------------------------ measurements

def limiter_dips(pre_path, master_path, gain_db):
    """Gain the limiter applied, per 50 ms block. Returns stats about the dips listeners hear."""
    m, sr = dt.read(master_path)
    x, sr2 = dt.read(pre_path)
    if sr2 != sr:
        return None
    x = x * 10 ** (gain_db / 20)
    n = min(len(m), len(x))
    w = int(0.05 * sr)
    k = n // w
    if k < 20:
        return None

    def lev(y):
        return 10 * np.log10((y[:k * w] ** 2).mean(axis=1).reshape(k, w).mean(axis=1) + 1e-12)

    gr = lev(m[:n]) - lev(x[:n])
    lv = lev(x[:n])
    act = gr[lv > np.percentile(lv, 20)]
    per_s = np.array([gr[i * 20:(i + 1) * 20].min() for i in range(k // 20)])
    worst_times = [i for i in np.argsort(per_s)[:5] if per_s[i] < -3]
    return {"seconds_over_4_5": int((per_s < -4.5).sum()), "seconds_over_3": int((per_s < -3).sum()),
            "worst_db": float(act.min()), "p95_db": float(np.percentile(act, 5)),
            "worst_at": sorted(int(i) for i in worst_times)}


def ending_check(path, window_s=30.0):
    """Look for a hard cut near the end of the sound (not the silent padding after it).

    Scans the last `window_s` seconds of actual sound in 50 ms blocks and reports the largest sudden drop:
    the mean of the 0.1 s before a point (while still above -30 dBFS) minus the mean of the 0.2 s after it."""
    x, sr = dt.read(path)
    m = np.sqrt((x ** 2).mean(axis=1)) if x.ndim == 2 else np.abs(x)
    w = int(0.05 * sr)
    k = len(m) // w
    if k < 20:
        return None
    lv = 20 * np.log10(np.sqrt((m[:k * w] ** 2).reshape(k, w).mean(axis=1)) + 1e-12)
    sound = np.where(lv > -60)[0]
    if not len(sound):
        return None
    last = int(sound[-1])
    start = max(2, last - int(window_s / 0.05))
    best, at = 0.0, None
    for i in range(start, last + 1):
        before = lv[i - 2:i].mean()
        if before < -30:
            continue
        after = lv[i:i + 4].mean() if i + 4 <= len(lv) else -120.0
        if before - after > best:
            best, at = before - after, i
    loud = np.where(lv[:last + 1] > lv.max() - 30)[0]
    tail_s = (last - int(loud[-1])) * 0.05 if len(loud) else 0.0
    return {"drop_db": float(best), "abrupt_at": at * 0.05 if best > 25 else None, "tail_s": float(tail_s)}


def mmss(s):
    return f"{int(s) // 60}:{int(s) % 60:02d}"


def review_master(rv, a, mp3, dips, settings, target, ceiling):
    L, S = a["loudness"], a["samples"]
    sec = "Master"
    I, tp, lra, plr = L["integrated_lufs"], L["true_peak_dbtp"], L["loudness_range_lu"], L.get("peak_to_loudness_ratio_db")
    if target is not None:
        st = grade(I, lambda v: abs(v - target) <= 0.2, lambda v: abs(v - target) <= 0.5)
        rv.add(sec, st, "Integrated loudness", f"{I} LUFS (target {target})",
               "re-render to the target" if st != PASS else "")
    else:
        rv.add(sec, INFO, "Integrated loudness", f"{I} LUFS (no target recorded)")
    st = grade(tp, lambda v: v <= ceiling + 0.05, lambda v: v <= 0)
    rv.add(sec, st, "True peak (WAV)", f"{tp} dBTP (ceiling {ceiling})", "lower the limiter ceiling" if st != PASS else "")
    if mp3:
        mtp = mp3["loudness"]["true_peak_dbtp"]
        st = grade(mtp, lambda v: v <= -0.1, lambda v: v <= 0)
        rv.add(sec, st, "True peak (MP3)", f"{mtp} dBTP", "export the MP3 with more headroom" if st != PASS else "")
    over = S["samples_above_full_scale"]
    rv.add(sec, PASS if over == 0 else FAIL, "Clipping", f"{over} samples above full scale, "
           f"{S['clip_runs_3plus_samples']} clip runs", "find and remove the clipping before the limiter" if over else "")
    st = grade(plr, lambda v: v >= 8, lambda v: v >= 6)
    rv.add(sec, st, "Punch (peak-to-loudness)", f"{plr} dB",
           "the master is squashed: lower the target or control peaks earlier" if st != PASS else "")
    st = grade(lra, lambda v: v >= 5, lambda v: v >= 3)
    rv.add(sec, st, "Contrast between sections (loudness range)", f"{lra} LU",
           "sections sound flat: back off compression or limiting" if st != PASS else "")
    if settings:
        loss = settings.get("limiter_loudness_reduction_lu")
        st = grade(loss, lambda v: v <= 2.0, lambda v: v <= 4.0)
        rv.add(sec, st, "Limiter workload", f"{loss} LU taken off the peaks",
               "tame the loudest element (often kick/808) before the limiter, or lower the target" if st != PASS else "")
    if dips:
        st = PASS if dips["seconds_over_4_5"] == 0 and dips["p95_db"] > -3 else \
            WARN if dips["seconds_over_4_5"] <= 10 else FAIL
        where = ", ".join(mmss(t) for t in dips["worst_at"]) or "none"
        rv.add(sec, st, "Volume dips from the limiter (pumping)",
               f"{dips['seconds_over_4_5']} s with dips over 4.5 dB, {dips['seconds_over_3']} s over 3 dB, "
               f"worst {dips['worst_db']:.1f} dB, typical worst {dips['p95_db']:.1f} dB; worst moments {where}",
               "find what triggers the dips at those times and control it before the limiter" if st != PASS else "")
    else:
        rv.add(sec, WARN, "Volume dips from the limiter (pumping)", "not measured",
               "pass --pre-limiter and --settings so dips can be checked")
    corr, fold = S.get("stereo_correlation"), S.get("mono_fold_change_db")
    if corr is not None:
        st = grade(corr, lambda v: v >= 0.3, lambda v: v >= 0)
        rv.add(sec, st, "Stereo / phase", f"correlation {corr}, mono fold {fold:+.1f} dB",
               "something is out of phase: check wide effects in mono" if st != PASS else "")
        st = grade(fold, lambda v: v >= -1.5, lambda v: v >= -3)
        rv.add(sec, st, "Mono playback (phone speaker)", f"{fold:+.1f} dB when folded to mono",
               "parts disappear in mono: narrow the widest elements" if st != PASS else "")
    end = ending_check(a["file"])
    if end:
        if end["abrupt_at"] is not None:
            st = WARN
            value = (f"stops abruptly at {mmss(end['abrupt_at'])} (level falls {end['drop_db']:.0f} dB in 0.1 s), "
                     f"then {end['tail_s']:.1f} s of tail")
            action = "the song cuts off instead of ending: confirm the hard stop is intended, or fade or ring it out"
        else:
            st = PASS
            value = f"ends smoothly: largest sudden drop {end['drop_db']:.0f} dB, {end['tail_s']:.1f} s fade/tail"
            action = ""
        rv.add(sec, st, "Ending", value, action)
    dc = max(abs(v) for v in S["dc_offset_per_channel"])
    rv.add(sec, PASS if dc < 0.002 else WARN, "DC offset", f"{dc:.4f}", "high-pass the mix at 5-10 Hz" if dc >= 0.002 else "")


def review_tone(rv, a, ref, ref_label):
    sec = "Tone and width vs " + ref_label
    bs, br = a["samples"].get("band_share_db") or {}, ref["samples"].get("band_share_db") or {}
    moved = []
    for band in bs:
        if band in br and bs[band] is not None and br[band] is not None:
            d = bs[band] - br[band]
            st = PASS if abs(d) <= 3 else WARN
            rv.add(sec, st, f"{band}", f"{d:+.1f} dB",
                   f"the {band} band moved {d:+.1f} dB: confirm by ear it was intended" if st != PASS else "")
            moved.append(d)
    ca, cr = a["samples"].get("stereo_correlation"), ref["samples"].get("stereo_correlation")
    if ca is not None and cr is not None:
        rv.add(sec, INFO, "Stereo correlation", f"{cr} → {ca}")


# ------------------------------------------------------------------ effects and plugins

def review_effect(rv, e, bpm, lowest_note_hz):
    """One row per effect or plugin, with a rule for its type."""
    sec = "Effects and plugins"
    t = (e.get("type") or "").lower()
    me = e.get("measured", {}) or {}
    label = f"{e.get('track', '?')} — {e.get('effect', t or 'effect')}"
    tool = e.get("plugin") or e.get("tool", "")
    settings = e.get("settings", "")
    value = f"{tool}: {settings}" if tool else settings
    status, action, extra = INFO, "", ""

    if t == "deess":
        p, avg = me.get("pct_active"), me.get("avg_db")
        status = grade(p, lambda v: 3 <= v <= 25, lambda v: 1 <= v <= 40)
        extra = f" → active {p}% of singing, avg {avg} dB"
        if status != PASS:
            action = ("de-esser works too often and dulls the voice: raise its threshold" if (p or 0) > 25 else
                      "de-esser barely works: lower its threshold if S sounds are still sharp")
    elif t == "dyneq":
        p = me.get("pct_active")
        status = grade(p, lambda v: v <= 30, lambda v: v <= 50)
        extra = f" → active {p}% of the time"
        if status != PASS:
            action = "dynamic EQ acts almost all the time (behaves like a static cut): raise its threshold"
    elif t == "comp":
        g = me.get("avg_gr_db")
        status = grade(g, lambda v: 2 <= v <= 7, lambda v: 1 <= v <= 10)
        extra = f" → avg {g} dB reduction"
        if status != PASS:
            action = "compression is too heavy (squashed, lifeless)" if (g or 0) > 7 else "compression is barely doing anything"
    elif t == "hpf":
        f = me.get("freq_hz")
        # the --lowest-note-hz flag describes the lead vocal; any other track logs its own lowest_note_hz.
        # Backing vocals and adlibs are cut higher on purpose (150-250 Hz) so they sit behind the lead.
        is_lead = "lead" in str(e.get("track", "")).lower()
        lowest_note_hz = me.get("lowest_note_hz") or (lowest_note_hz if is_lead else None)
        if lowest_note_hz and f:
            status = PASS if f < lowest_note_hz else FAIL
            extra = f" → cutoff {f} Hz vs lowest sung note {lowest_note_hz} Hz"
            if status != PASS:
                action = "high-pass cuts into the lowest sung note: lower the cutoff"
        else:
            status = PASS
    elif t == "delay":
        note, ms, ducked = me.get("note"), me.get("ms"), me.get("ducked")
        b = me.get("bpm", bpm)
        if note in NOTE_FACTORS and b and ms is not None:
            exp = note_ms(b, note)
            ok_time = abs(ms - exp) <= 0.05
            status = PASS if ok_time and ducked else FAIL
            extra = f" → {note} at {b:g} BPM should be {exp:.2f} ms, used {ms:.2f} ms, ducked: {'yes' if ducked else 'NO'}"
            if not ok_time:
                action = "delay time does not match the BPM: recompute from the brief's table"
            elif not ducked:
                action = "delay is not ducked under the lead vocal: re-render with --duck-by"
            if bpm and abs(b - bpm) > 0.01:
                status, action = FAIL, f"delay used {b:g} BPM but the brief says {bpm:g}"
        else:
            status, action = WARN, "log the delay's note, ms and BPM so its timing can be checked"
    elif t == "reverb":
        pre, dec = me.get("predelay_ms"), me.get("decay_s")
        b = me.get("bpm", bpm)
        if b and pre is not None and dec is not None:
            pn, pms = nearest_note(b, pre)
            dn, dms = nearest_note(b, dec * 1000)
            ok_pre = abs(pre - pms) <= 0.1
            ok_dec = abs(dec * 1000 - dms) <= 20
            status = PASS if ok_pre and ok_dec else WARN
            extra = (f" → pre-delay {pre} ms (nearest note {pn} = {pms:.2f} ms), "
                     f"decay {dec} s (nearest note {dn} = {dms / 1000:.3f} s)")
            if not ok_pre:
                action = f"pre-delay is not tempo-synced: use {pn} = {pms:.2f} ms"
            elif not ok_dec:
                action = f"decay is not tempo-synced: use {dn} = {dms / 1000:.3f} s"
        else:
            status, action = WARN, "log the reverb's pre-delay, decay and BPM so its timing can be checked"
    elif t in ("eq", "saturation", "gain", "bus", "balance", "low-end", "limiter", "keep"):
        status = PASS
    else:
        status = INFO

    req, used = e.get("requested_plugin"), e.get("plugin")
    if req and used and req.strip().lower() != used.strip().lower():
        if status == PASS:
            status = WARN
        action = (action + "; " if action else "") + (f"owner asked for {req}; built with {used} instead: "
                                                      "rebuild with the real plugin when the owner's DAW arrives")
    for issue in e.get("issues", []) or []:
        if status == PASS:
            status = WARN
        action = (action + "; " if action else "") + issue
    rv.add(sec, status, label, value + extra, action)


def review_requests(rv, requests, effects):
    sec = "Creative effects requests (from the brief)"
    if not requests:
        rv.add(sec, INFO, "Requests", "none in the brief yet")
        return
    built = {str(e.get("request", "")).strip().lower() for e in effects if e.get("request")}
    for cells in requests:
        name = cells[0]
        ok = name.strip().lower() in built
        rv.add(sec, PASS if ok else FAIL, name, " | ".join(cells[1:5]),
               "" if ok else "requested in the brief but not in this version's effects log: build it at the named spot")


# ------------------------------------------------------------------ output

def write_report(path, song, version, rv, files, unknowns, signoff):
    nf, nw, np_ = rv.count(FAIL), rv.count(WARN), rv.count(PASS)
    if nf:
        verdict = f"❌ Not ready: {nf} problem(s) to fix before the owner listens."
    elif nw:
        verdict = f"⚠️ Close: {nw} item(s) to check or improve."
    else:
        verdict = "✅ All measured checks pass. Ready for the owner's listening checks (not finished until sign-off)."
    out = [f"# Review report: {song} — {version}", "",
           f"Generated {date.today().isoformat()} by `music/tools/song_report.py`.", "",
           f"**Verdict:** {verdict}", "",
           f"{np_} passed · {nw} to check · {nf} failed", "",
           "The tools measure the audio; they do not listen. Every item here still needs the owner's ears.", ""]
    out += ["## Files", ""] + [f"- **{k}:** `{os.path.basename(v)}`" for k, v in files.items() if v] + [""]
    for sec, rows in rv.rows.items():
        out += [f"## {sec}", "", "| | Check | Result | To make it near-perfect |", "| --- | --- | --- | --- |"]
        for st, check, value, action in rows:
            out.append(f"| {ICON[st]} | {check} | {str(value).replace('|', '/')} | {action.replace('|', '/') or '—'} |")
        out.append("")
    out += ["## Missing facts in the brief", ""]
    out += [f"- {u}" for u in unknowns] if unknowns else ["- none"]
    out += ["", "## What's needed before this song is near-perfect", ""]
    items = [f"- {ICON[s]} {t}" for s, t in sorted(rv.todo, key=lambda x: x[0] != FAIL)]
    if unknowns:
        items.append(f"- ⚠️ Fill in the {len(unknowns)} missing fact(s) in the brief: choices like loudness, "
                     "tone and effects depend on them")
    items += [f"- 👂 {s}" for s in signoff]
    out += items if items else ["- nothing measured is left; the owner signs off in mix-notes.md"]
    out.append("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return verdict, nf, nw, np_


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("song_dir", help="music/songs/<song>")
    ap.add_argument("--version", required=True, help="e.g. v2")
    ap.add_argument("--master", required=True, help="the delivered WAV master")
    ap.add_argument("--mp3", help="the delivered MP3")
    ap.add_argument("--pre-limiter", help="the mix that went into render_master.py (for the dip check)")
    ap.add_argument("--settings", help="render_master.py's .settings.json for this master")
    ap.add_argument("--original", help="the original mix (or stems summed) to compare tone against")
    ap.add_argument("--previous", help="the previous version's master, for a second comparison")
    ap.add_argument("--effects", help="this version's effects log (JSON list); see workflow.md step 7")
    ap.add_argument("--lowest-note-hz", type=float, help="lowest sung note, for the high-pass check")
    a = ap.parse_args()

    song_dir = a.song_dir.rstrip("/")
    brief = read_text(os.path.join(song_dir, "brief.md"))
    notes = read_text(os.path.join(song_dir, "mix-notes.md"))
    song = brief_field(brief, "Title") or os.path.basename(song_dir)
    bpm = brief_bpm(brief)
    settings = json.load(open(a.settings)) if a.settings else None
    effects = json.load(open(a.effects)) if a.effects else []
    target = settings.get("target_lufs") if settings else None
    ceiling = settings.get("ceiling_dbtp", -0.5) if settings else -0.5

    rv = Review()
    master = aa.analyze(a.master)
    mp3 = aa.analyze(a.mp3) if a.mp3 else None
    dips = limiter_dips(a.pre_limiter, a.master, settings["gain_into_limiter_db"]) \
        if a.pre_limiter and settings else None
    review_master(rv, master, mp3, dips, settings, target, ceiling)
    if a.original:
        review_tone(rv, master, aa.analyze(a.original), "the original")
    if a.previous:
        review_tone(rv, master, aa.analyze(a.previous), "the previous version")
    if bpm is None:
        rv.add("Effects and plugins", WARN, "BPM", "missing from the brief", "add the BPM so effect timing can be checked")
    if not effects:
        rv.add("Effects and plugins", WARN, "Effects log", "none given", "log every effect and plugin used (workflow step 7)")
    for e in effects:
        review_effect(rv, e, bpm, a.lowest_note_hz)
    review_requests(rv, brief_effect_requests(brief), effects)

    path = os.path.join(song_dir, "reports", f"{a.version}.md")
    files = {"WAV master": a.master, "MP3": a.mp3, "Effects log": a.effects, "Compared with": a.original,
             "Previous version": a.previous}
    verdict, nf, nw, np_ = write_report(path, song, a.version, rv, files, brief_unknowns(brief), unchecked_signoff(notes))
    print(f"Wrote {path}")
    print(f"{verdict}  ({np_} passed, {nw} to check, {nf} failed)")


if __name__ == "__main__":
    main()

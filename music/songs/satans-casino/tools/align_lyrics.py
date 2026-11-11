#!/usr/bin/env python3
"""Align Chex's lyric lines to the lead vocal with MMS forced alignment.

The wording stays as supplied. A separate aligner string maps numerals and
letter names so the acoustic model can see them. 'spite' and 'forth' are not
changed. Repeat directions are not pasted into the audio.

  python3 music/songs/satans-casino/tools/align_lyrics.py
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import torch
import torchaudio
from torchaudio.pipelines import MMS_FA as BUNDLE

SONG = Path(__file__).resolve().parents[1]
SR = 16000
DEVICE = torch.device("cpu")

# Aligner pronunciation only. The stored lyric text is never replaced by these.
PRON = {
    "2": "two",
    "3": "three",
    "10s": "tens",
    "15k": "fifteen k",
    "p's": "pees",
    "p": "pee",
    "&": "and",
}


def spoken_form(text):
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("&", " and ")
    text = re.sub(r"[^A-Za-z0-9'\s]", " ", text)
    out = []
    for tok in text.lower().split():
        out.append(PRON.get(tok, tok))
    return " ".join(out)


def parse_lines(path):
    lines = []
    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith("Chex supplied") or s.startswith("Preserve wording"):
            continue
        if s.startswith("(") and s.endswith(")"):
            continue
        label = None
        if s.lower().startswith("next verse:"):
            label = "Next verse:"
            s = s.split(":", 1)[1].strip()
        lines.append({"raw": s, "label_stripped": label, "align_text": spoken_form(s)})
    for i, line in enumerate(lines, start=1):
        line["line_id"] = f"L{i:02d}"
    return lines


def load_vocal():
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(SONG / "sources" / "satans-casino-lead-vocals.flac"),
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True,
    )
    wav = np.frombuffer(raw.stdout, dtype="<f4").copy()
    return torch.from_numpy(wav)


def norm_toks(w):
    w = w.replace("’", "'").replace("'", "").lower()
    w = re.sub(r"[^a-z0-9]", "", w)
    if not w:
        return []
    return PRON.get(w, w).split()


def whisper_stream():
    words = json.loads((SONG / "effects" / "v04-words.json").read_text())
    stream = []
    for w in words:
        for t in norm_toks(w["word"]):
            stream.append({"t": t, "start": w["start"], "end": w["end"], "p": w["p"], "raw": w["word"]})
    return stream


def lev(a, b):
    if abs(len(a) - len(b)) > 2:
        return 9
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def close(a, b):
    if a == b:
        return True
    if min(len(a), len(b)) < 4:
        return False
    if a[:4] == b[:4]:
        return True
    return lev(a, b) <= 1


def match_score(line_toks, window):
    """Ordered overlap. A missing lyric token is skipped so one ASR
    substitution does not zero the rest of the line."""
    if not line_toks or not window:
        return 0.0
    j = 0
    hit = 0
    for tok in line_toks:
        k = j
        while k < len(window) and not close(window[k]["t"], tok):
            k += 1
        if k < len(window):
            hit += 1
            j = k + 1
    return hit / len(line_toks)


STOP = {
    "the", "and", "that", "with", "then", "this", "just", "cause", "from",
    "what", "when", "have", "been", "they", "them", "your", "yours",
}


def anchor_hits(line_toks, stream, existing):
    """Windows that end on a distinctive transcript word of this line.

    Used only when the ordered search never covered that word. CTC still
    has to accept the window; a lone matching word is not a placement.
    """
    content = [t for t in line_toks if len(t) >= 5 and t not in STOP]
    if not content:
        return []
    anchor = content[-1]
    span = max(1.8, 0.34 * len(line_toks))
    raw_hits = []
    for s in stream:
        if not close(s["t"], anchor):
            continue
        covered = any(h["start"] - 0.3 <= s["start"] <= h["end"] + 0.2 for h in existing)
        if covered:
            continue
        t1 = s["end"]
        t0 = max(0.0, t1 - span)
        window = [w for w in stream if t0 - 0.15 <= w["start"] <= t1 + 0.05]
        raw_hits.append({
            "score": round(match_score(line_toks, window), 3),
            "start": round(t0, 3),
            "end": round(t1, 3),
            "evidence": (
                f"anchored on transcript token {s['raw'].strip()!r} at "
                f"{s['start']:.3f}-{s['end']:.3f}s. The rest of the line was not recovered in order."
            ),
        })
    kept = []
    for h in sorted(raw_hits, key=lambda x: -x["score"]):
        if all(abs(h["end"] - k["end"]) > 1.5 for k in kept):
            kept.append(h)
    return sorted(kept, key=lambda x: x["start"])


def lexical_final(raw, words):
    last = raw.split()[-1]
    key = re.sub(r"[^A-Za-z0-9']", "", last).lower().replace("'", "")
    expected = PRON.get(key, key).split()
    got = words[-len(expected):]
    matched = len(got) == len(expected) and all(
        g["align_word"] == e or close(g["align_word"], e) for g, e in zip(got, expected)
    )
    return {
        "id": key or last,
        "text_token": last,
        "align_words": [g["align_word"] for g in got],
        "expected_pronunciation": expected,
        "pronunciation_matches_tokens": matched,
        "start": got[0]["start"],
        "end": got[-1]["end"],
        "token_score": round(sum(g["token_score"] for g in got) / len(got), 3),
        "timestamp_kind": "mms_ctc",
    }, expected


def whisper_cover(stream, start, end, expected):
    hits = [
        s for s in stream
        if s["end"] >= start - 0.08 and s["start"] <= end + 0.3
        and any(s["t"] == e or close(s["t"], e) for e in expected)
    ]
    if not hits:
        return None
    return {
        "start": hits[0]["start"],
        "end": hits[-1]["end"],
        "raw": " ".join(h["raw"].strip() for h in hits),
        "timestamp_kind": "speech_model_token",
    }


def find_occurrences(line_toks, stream):
    """Where the existing transcript already contains this line, in order."""
    width = max(3, len(line_toks))
    hits = []
    i = 0
    while i < len(stream):
        window = stream[i:i + width + 8]
        score = match_score(line_toks, window)
        if score >= 0.45 and len(window) >= max(2, len(line_toks) // 3):
            # tighten the window to the matched span
            j = 0
            first = last = None
            for tok in line_toks:
                k = j
                while k < len(window) and not close(window[k]["t"], tok):
                    k += 1
                if k >= len(window):
                    continue
                if first is None:
                    first = window[k]
                last = window[k]
                j = k + 1
            if first and last:
                hits.append({
                    "score": round(score, 3),
                    "start": first["start"],
                    "end": last["end"],
                    "evidence": "ordered overlap with the earlier speech-model transcript",
                })
            i += max(2, width // 2)
        else:
            i += 1
    # drop overlaps
    kept = []
    for h in sorted(hits, key=lambda x: -x["score"]):
        if all(abs(h["start"] - k["start"]) > 2.0 for k in kept):
            kept.append(h)
    return sorted(kept, key=lambda x: x["start"])


def align_window(model, tokenizer, aligner, waveform, t0, t1, text):
    a = max(0, int((t0 - 0.25) * SR))
    b = min(waveform.shape[0], int((t1 + 0.45) * SR))
    chunk = waveform[a:b].unsqueeze(0)
    with torch.inference_mode():
        emission, _ = model(chunk)
    try:
        pieces = tokenizer(text.replace("'", "").split())
    except Exception as exc:
        return None, f"tokenizer rejected the line: {exc}"
    if not pieces:
        return None, "tokenizer returned no pieces"
    try:
        spans = aligner(emission[0], pieces)
    except Exception as exc:
        return None, f"aligner failed: {exc}"
    ratio = chunk.shape[1] / emission.shape[1]
    words = text.replace("'", "").split()
    if len(spans) != len(words):
        return None, f"aligner returned {len(spans)} pieces for {len(words)} words"
    out = []
    scores = []
    for word, token_spans in zip(words, spans):
        if not token_spans:
            return None, f"no spans for {word}"
        st = token_spans[0].start * ratio / SR + a / SR
        en = token_spans[-1].end * ratio / SR + a / SR
        sc = float(sum(s.score for s in token_spans) / len(token_spans))
        scores.append(sc)
        out.append({"align_word": word, "start": round(st, 3), "end": round(en, 3), "token_score": round(sc, 3)})
    return {
        "words": out,
        "mean_token_score": round(float(np.mean(scores)), 3),
        "window": [round(a / SR, 3), round(b / SR, 3)],
    }, None


def main():
    print("loading MMS forced aligner", flush=True)
    model = BUNDLE.get_model().to(DEVICE)
    tokenizer = BUNDLE.get_tokenizer()
    aligner = BUNDLE.get_aligner()
    waveform = load_vocal()
    lyric_lines = parse_lines(SONG / "lyrics" / "chex-supplied.txt")
    stream = whisper_stream()
    occurrences = []
    unresolved = []
    for line in lyric_lines:
        toks = spoken_form(line["raw"]).replace("'", "").split()
        found = find_occurrences(toks, stream)
        found.extend(anchor_hits(toks, stream, found))
        if not found:
            unresolved.append({
                "line_id": line["line_id"],
                "text": line["raw"],
                "why": "The supplied line did not line up, in order, with the speech-model word stream. No repeat was invented.",
            })
            print(line["line_id"], "NO TRANSCRIPT MATCH", line["raw"][:60], flush=True)
            continue
        for n, hit in enumerate(found, start=1):
            aligned, err = align_window(
                model, tokenizer, aligner, waveform, hit["start"], hit["end"], line["align_text"]
            )
            rec = {
                "line_id": line["line_id"],
                "occurrence": n,
                "text": line["raw"],
                "align_text": line["align_text"],
                "pronunciation_note": "Numerals and P/P's/& were spoken for the aligner only. spite and forth were not changed.",
                "label_stripped": line["label_stripped"],
                "transcript_match": hit,
                "ctc": aligned,
                "ctc_error": err,
                "acoustic_flag": "MMS forced aligner is a speech model, not a rap phonetic dictionary. Low token scores mean the phones did not fit cleanly.",
            }
            if aligned is None or aligned["mean_token_score"] < 0.2:
                rec["status"] = "unresolved"
                rec["why"] = err or f"mean token score {aligned['mean_token_score'] if aligned else 'n/a'} is too low to place"
            else:
                words = aligned["words"]
                final, expected = lexical_final(line["raw"], words)
                final["speech_model_token"] = whisper_cover(stream, final["start"], final["end"], expected)
                rec["status"] = "ctc_timed"
                rec["line_start"] = words[0]["start"]
                rec["line_end"] = words[-1]["end"]
                rec["final_word"] = final
                rec["line_bounds_kind"] = "mms_ctc"
            occurrences.append(rec)
            print(line["line_id"], n, rec["status"], hit["start"], aligned["mean_token_score"] if aligned else err, flush=True)

    by_line = {}
    for rec in occurrences:
        by_line.setdefault(rec["line_id"], []).append(rec)
    for group in by_line.values():
        ranked = sorted(
            [r for r in group if r["status"] == "ctc_timed"],
            key=lambda r: -(r["transcript_match"]["score"] + r["ctc"]["mean_token_score"]),
        )
        kept = []
        for rec in ranked:
            a, b = rec["line_start"], rec["line_end"]
            overlap = False
            for prev in kept:
                shared = min(b, prev["line_end"]) - max(a, prev["line_start"])
                if shared > 0.4 * min(b - a, prev["line_end"] - prev["line_start"]):
                    overlap = True
                    break
            if overlap:
                rec["status"] = "rejected_overlap"
                rec["why"] = "Same supplied line already has a higher-scoring alignment covering this span."
            else:
                kept.append(rec)

    payload = {
        "source_lyric": "lyrics/chex-supplied.txt",
        "wording": "stored exactly as supplied",
        "repeat_directions": "not forced; a second copy exists only where the transcript already contained the line",
        "method": "ordered match to the earlier speech-model transcript, plus an anchor on a distinctive transcript word when that word was heard but the line was not, then MMS CTC forced alignment inside that window",
        "measured_vs_model": "line_start/line_end and final_word start/end are MMS CTC token spans (timestamp_kind mms_ctc). final_word.speech_model_token is the earlier transcript token when one overlaps, and is not a phonetic measurement. Neither is a listening judgment.",
        "lines": occurrences,
        "unresolved": unresolved,
    }
    path = SONG / "effects" / "lyrics_alignment.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path, "placed", sum(1 for r in occurrences if r["status"] == "ctc_timed"), "unresolved", len(unresolved))


if __name__ == "__main__":
    main()

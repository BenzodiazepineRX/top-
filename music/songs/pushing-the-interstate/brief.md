# Song brief

Fill this in before any mixing or mastering. Agents read this file first and adapt their decisions to it.

If you do not know an answer yet, write "unknown" and who to ask. Do not guess a fact that will send the mix in the wrong direction.

> First filled in on 2026-11-08 after the v1 master. Facts marked "measured" came from `music/tools/` (analysis of the stems). Anything marked "unknown" still needs the owner's answer.

## Song

- **Title:** Pushing the Interstate
- **Artist:** unknown, ask the owner
- **Genre / subgenre:** unknown, ask the owner (the session is beat + rap/sung lead + adlibs)
- **Mood / vibe:** unknown, ask the owner
- **BPM:** 129 (measured on the beat stem, high confidence)
- **Key:** F major (measured, medium confidence; runner-up Bb major). Tuning A4 = 439.7 Hz.

## Reference tracks

None given yet. Ask the owner for 1 to 3.

1. **Track** — unknown
   - Borrow:
   - Leave alone:

## Session

Four stems, all 44.1 kHz stereo MP3 (192 kbps), 2:39 long, all starting at 0:00 and aligned. The owner says these are the stems from a version someone else helped mix; summed at unity they measure −18.3 LUFS, so they are pre-master stems.

- `01_Beat` — the instrumental (−19.2 LUFS)
- `02_Lead_Vocals` — lead vocal, mono, already compressed (loudness range 1.7 LU). Most-sung notes Bb2–C3, lowest about A2 (110 Hz).
- `03_Adlibs` — adlibs, close to mono (−26.2 LUFS)
- `04_Vocal_FX_Reverb_Delays_Throws` — the previous engineer's printed vocal reverb, delays and throws (−36.2 LUFS, wide)

The stems are lossy MP3. WAV stems would give the next pass more detail to work with.

## What's working

- unknown, ask the owner. The previous engineer's vocal FX stem was kept as printed in v1.

## Problem areas

Measured on the summed stems (not yet confirmed by the owner's ears):

- Lead vocal: boxy buildup around 230–320 Hz; narrow harsh peaks at about 3.5 kHz and 4.7 kHz.
- Whole mix: energy weighted heavily to sub and bass, dark in the upper mids and air.
- Song ends while still loud (last 0.1 s at −21 dBFS): the ending may be cut off.

## Creative effects requests

None requested yet. Ask the owner.

| Effect | Scope (one track or whole mix) | Where it happens | How long (bars) | Plugin, if one is required | Notes |
| --- | --- | --- | --- | --- | --- |
| none requested yet | | | | | |

## Delay timing for this song

- **BPM used:** 129
- **Time signature:** 4/4 (assumed; confirm with the owner)

| Note | Straight (ms) | Dotted × 1.5 (ms) | Triplet × 2/3 (ms) |
| --- | --- | --- | --- |
| 1 bar (4 beats in 4/4) | 1860.47 | — | — |
| 1/2 | 930.23 | 1395.35 | 620.16 |
| 1/4 | 465.12 | 697.67 | 310.08 |
| 1/8 | 232.56 | 348.84 | 155.04 |
| 1/16 | 116.28 | 174.42 | 77.52 |

Checked against `tempo_key.py`'s table at 129 BPM. Reverb pre-delay in range: 1/64 = 29.07 ms.

## Where it will be heard

Not confirmed yet. Ask the owner.

- [ ] Streaming (say which: Spotify, Apple Music, Amazon, YouTube, Tidal, Deezer, other)
- [ ] Radio (say which: US commercial, European broadcast, other)
- [ ] Earbuds
- [ ] Car
- [ ] Phone speaker
- [ ] Club or other:

## Deadline

- **Needed by:** unknown
- **What this pass should deliver:** v1 was "make the existing mix sound better and master it." Next pass depends on the owner's feedback.

# Song brief

Fill this in before any mixing or mastering. Agents read this file first and adapt their decisions to it.

If you do not know an answer yet, write "unknown" and who to ask. Do not guess a fact that will send the mix in the wrong direction.

> First filled in on 2026-11-08 after the v1 master. Facts marked "measured" came from `music/tools/` (analysis of the stems). Anything marked "unknown" still needs the owner's answer.

## Song

- **Title:** Pushing the Interstate
- **Artist:** unknown, ask the owner
- **Genre / subgenre:** unknown, ask the owner (the session is beat + rap/sung lead + adlibs)
- **Mood / vibe:** unknown, ask the owner
- **BPM:** 129 (measured on the beat stem, high confidence; confirmed directly: the beat's drum pattern repeats at shifts of 104.186, 107.906 and 111.628 s for 56, 58 and 60 bars, exactly 129 BPM. A 128.71 reading from a grid-fit method was a false lock and was reverted after it put the outro off beat.)
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

- Owner on v2: "Absolute fucking masterpiece." Owner on v3: "I LOVED v3." Keep the v3 vocal sound, balance and loudness.
- The previous engineer's vocal FX stem, kept as printed, except that from v14 its echo copies are moved onto the drum hits (see Problem areas).
- Owner on v4: "it's beautiful" (the signed-off master until a later version is approved). Owner on v12: far too much delay, and extra reverb on the main vocal was not wanted; keep the v3 reverb on the lead.

## Problem areas

Measured on the summed stems (not yet confirmed by the owner's ears):

- Lead vocal: boxy buildup around 230–320 Hz; narrow harsh peaks at about 3.5 kHz and 4.7 kHz.
- Whole mix: energy weighted heavily to sub and bass, dark in the upper mids and air.
- The printed FX stem (`04`) holds its own echoes: exact copies of the dry vocals one note later. Lead words are echoed one quarter note later (465 ms, about 23 dB under the word, usually one repeat, about 120 words); adlib phrases are echoed one half, one, three and four quarter notes later (about 14 dB under the adlib, loudest near 1:31 and 1:38). Because each copy is exact, it sits as far off the drums as the word does (10-50 ms), which is what the owner heard as echoes "off from 0:43". From v14 the copies are moved onto the nearest drum hit (`tools/retime_stem.py`). Do not lay new echoes over the same words without checking them against these copies.
- The beat stem stops dead at 2:39.2 while still loud. From v4 the owner asked for a fade-out, so the beat fades over bars 82–86 and the outro echoes ring past the stop.

## Creative effects requests

Requested by the owner on 2026-11-08 (v4).

| Effect | Scope (one track or whole mix) | Where it happens | How long (bars) | Plugin, if one is required | Notes |
| --- | --- | --- | --- | --- | --- |
| Phone-call outro | New outro vocal (copies of the lead) | Right after the last lead vocal (bar 73) until the song fades out | Bars 73–86 plus ring-out | none named | Alternate line A "since I already know what you planning to do you can go put the blame on me anyway" and line B "I'm riding through traffic with styrofoam cups in the console I'm pushing the interstate", repeated until the fade; telephone-line sound, really good reverb, perfectly timed delay that repeats after what is said; a little quieter than the first outro draft |
| Lead vocal delay | Lead vocal | Both verses; off where it would get in the way | Whole song | none named | "Perfect" tempo-synced delay; owner: "if you think they need to be off a certain part then do that… I just want the song to be filled in" |
| Song fade-out | Whole mix | The last bars of the song | Bars 82–86 | none named | Owner: "repeat those 2 parts… til the song fades out" |
| Outro echoes, pitched up | Outro vocal | The outro lines | Bars 73–86 | none named | Owner: "add a delay with echos in the outro verse as well with the telephone effect but a little more high pitched on the delay vocal"; clarified: "as the bars play a delay plays after what's being said that's perfect timed" |
| Outro stutters | Outro vocal | Before each outro line | Bars 73–86 | none named | Owner: "add some like studders in the outro verse too"; clarified: "where the first half part of a syllable or word repeats 3-4 times before the whole things gets said" |

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

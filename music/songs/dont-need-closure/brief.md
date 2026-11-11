# Song brief

Fill this in before any mixing or mastering. Agents read this file first and adapt their decisions to it.

If you do not know an answer yet, write "unknown" and who to ask. Do not guess a fact that will send the mix in the wrong direction.

## Song

- **Title:** Don't Need Closure
- **Artist:** unknown (ask the owner, Kenshin)
- **Genre / subgenre:** sad, melodic rap over a type beat ("Cold"); mostly rapped, few held notes
- **Mood / vibe:** cold, emotional, late-night; the owner wants the listener to "just feel bliss in the music"
- **BPM:** 126
- **Key:** E major (the beat; tuning A4 = 441.3 Hz, measured with `tempo_key.py`)

How the tempo was checked (`tools/map.py`): the beat matches itself at 8, 16 and 24 bars of 126.000 BPM; the hi-hats sit on a 126 BPM eighth grid starting 2.6 ms into the file. The 808 lands on beats 1 and 2 and the clap on beat 3, so bar 1 starts at 0.955 s; bar b starts at 0.955 + (b − 1) × 1.90476 s. The drums enter exactly on the downbeat of bar 10 and come back on the downbeats of bars 50 and 74.

## Reference tracks

1. **Track** — the owner's own Baccdoor, v4 lead vocal (this repo, `music/songs/baccdoor`)
   - Borrow: the lead vocal's tone (he called v3 "nearly PERFECT" and asked for a little less harshness and more clarity; v4 is that)
   - Leave alone: Baccdoor's telephone background vocals and fade-out, which were requests for that song only
2. **Track** — unknown (ask the owner for a commercial reference)
   - Borrow:
   - Leave alone:

## Session

Received 2026-11-10, 16-bit 44.1 kHz WAV, all exported from the same start point:

- Beat: "Free Sad Type Beat — Cold" from YouTube (via YT2mp3, 320 kbps source: no content above 15.9 kHz).
- Track 2 and Track 3: the two main leads. They trade lines (they overlap for 3.8 s in the whole song). Nearly mono.
- Track 4 and Track 5: adlibs and background vocals that answer the leads. Track 4 leans left by 7.7 dB and Track 5 right by 10.3 dB, with their own ambience; their peaks stand 22 dB over their loudness (very spiky).

No beat bleed in the vocal stems (correlation with the beat under 0.03).

## Song map (measured)

| Bars | Time | Beat | Vocals |
| --- | --- | --- | --- |
| 1–9 | 0:00.0–0:18.1 | intro, no drums | none |
| 10–17 | 0:18.1–0:33.3 | drums in | hook: lead 1 from 0:18.0, lead 2 answers at 0:24.5 |
| 18–41 | 0:33.3–1:19.1 | full beat | verse 1: the leads trade lines every 2 bars, every bar from bar 34; adlibs throughout |
| 42–49 | 1:19.1–1:34.3 | drop: no drums | hook again; a 1.65 s pause before bar 50 |
| 50–65 | 1:34.3–2:04.8 | full beat | verse 2; a 1.48 s pause before bar 66 |
| 66–73 | 2:04.8–2:20.0 | drop: 808 in and out, no hats | hook again |
| 74–89 | 2:20.0–2:50.5 | full beat | verse 3 |
| 90–98 | 2:50.5–3:07.6 | piano outro | the last lead line ends at 2:52.7, the adlibs at 2:55.3 |

## What's working

- The performance and the timing: the leads' lines start on the grid, and the two leads hand over to each other with no dead air.
- The adlibs' left/right placement.

## Problem areas

- The lead recordings are dark and boomy: against the Baccdoor v4 lead they carry 8–11 dB less of the 1.6–3.5 kHz range that carries the words, a deep dip at 4 kHz, and S sounds that stand 15–20 dB over the vowels above 8 kHz.
- The voice is monotone around B2 (123 Hz), so its spectrum has deep gaps between the harmonics; tone must be measured in octave-wide bands.
- The adlib tracks are much quieter than the leads (10 dB under), far brighter above 5 kHz, and very spiky. They were exported with a long reverb on them: after a word ends, a tail holds about 20 dB under it for 0.7 s and more. Any compression lifts that tail (v1 did, to 6 dB under the words).
- No autotune and few held notes (voiced 14–16% of the time, 8–12% of that held): pitch correction has nothing to hold on to, and no note-by-note pitch editor is installed here. Not retuned.
- The beat is a YouTube rip: nothing above 15.9 kHz. A WAV from the producer would be cleaner, and a free beat usually needs the producer's lease or credit before a streaming release.

## Creative effects requests

The owner, 2026-11-10: "Let's make this sound professional. Reverse reverbs at perfect build up into beat drop, perfectly timed delay/echos to fill in empty gaps, perfect volume all the way through from lead to background/adlibs so the listener can hear absolutely everything and just feel bliss in the music."

| Effect | Scope (one track or whole mix) | Where it happens | How long (bars) | Plugin, if one is required | Notes |
| --- | --- | --- | --- | --- | --- |
| Reverse reverbs | leads (the word that lands on the drop) and the beat (the drop's first hit) | into bar 10 (drums in, the first word), bar 50 (drums back), bar 66 (hook 3), bar 74 (drums back) | vocal swells 2 bars (1 bar into bar 66); beat risers 1 bar into bars 10, 50, 74 | none | each vocal swell starts on a downbeat and ends on the word's first sound; each riser ends on the drop's first hit |
| Echo throws | lead 1, lead 2 | the last word of every lead line; the two pauses before bars 50 and 66; the last line | 3 echoes in the verses, 4 in the hooks and the pauses, 8 half-note echoes on the last line | none | each echo starts on a main beat (1/4 = 476.19 ms) of the grid measured from the drums |
| Even volume | leads, adlibs | whole song | — | none | every lead line at the same loudness, 0.5 dB under the beat. Adlibs, owner on v1: "I want them to sit under the lead vocals perfectly": the two adlib tracks together 6.5 dB under the leads, bar by bar, measured where both sing |
| Reverb | leads, adlibs, echoes | whole song; the lead plate opens up in the hooks and drops | — | none | plate 1.43 s (dotted half) on the leads, pre-delay 29.76 ms (1/64). Adlibs, owner on v1: "way too much reverb. I just want them to have reverb but not that much": no reverb is added to them (v1: hall 1.90 s); their own baked-in reverb is turned down to 6–7 dB under the raw tracks' |
| Streaming master | whole mix | whole song | — | none | −12.0 LUFS, −1.0 dBTP, mono-safe for phones |

## Delay timing for this song

- **BPM used:** 126
- **Time signature:** 4/4

| Note | Straight (ms) | Dotted × 1.5 (ms) | Triplet × 2/3 (ms) |
| --- | --- | --- | --- |
| 1 bar (4 beats in 4/4) | 1904.76 | — | — |
| 1/2 | 952.38 | 1428.57 | 634.92 |
| 1/4 | 476.19 | 714.29 | 317.46 |
| 1/8 | 238.10 | 357.14 | 158.73 |
| 1/16 | 119.05 | 178.57 | 79.37 |

Reverb pre-delay 1/64 = 29.76 ms. Reverb decays: dotted half = 1.43 s (plate), 1 bar = 1.90 s (hall).

## Where it will be heard

- [x] Streaming (which: unknown; ask the owner)
- [x] Earbuds
- [x] Phone speaker
- [x] Stereos / car

## Deadline

- **Needed by:** unknown (ask the owner)
- **What this pass should deliver:** v1 master for the owner's listening check.

The song is fully finished only after the final sign-off in `mix-notes.md`. A rough-mix deadline is still a real deadline. It is a step, not the finished master.

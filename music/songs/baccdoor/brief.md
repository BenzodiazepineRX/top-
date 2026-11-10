# Song brief

Fill this in before any mixing or mastering. Agents read this file first and adapt their decisions to it.

If you do not know an answer yet, write "unknown" and who to ask. Do not guess a fact that will send the mix in the wrong direction.

## Song

- **Title:** Baccdoor
- **Artist:** unknown (ask the owner, Kenshin)
- **Genre / subgenre:** sad, emotional rap over a piano type beat ("Alone In A Room"), sung and rapped with autotune
- **Mood / vibe:** emotional, late-night
- **BPM:** 125
- **Key:** E minor (the beat; tuning A4 = 438.3 Hz, measured with `tempo_key.py` and a note count of the beat)

How the tempo was checked: the beat matches itself at 4, 8, 16 and 24 bars of 125.000 BPM; the hi-hats sit on a 125 BPM eighth grid starting 17.4 ms into the file. Bar 1 starts at 1.457 s; bar b starts at 1.457 + (b − 1) × 1.92 s (the beat's section changes land on these downbeats).

## Reference tracks

1. **Track** — unknown (ask the owner)
   - Borrow:
   - Leave alone:

## Session

Received 2026-11-09, 16-bit 44.1 kHz WAV, all exported from the same start point:

- Beat: "Free Sad Type Beat — Alone In A Room" from YouTube (via Y2Mate, 160 kbps source: no content above 15.6 kHz).
- Main vocals lead 1 and Main vocal lead 2: two lead takes that trade lines every 2 bars and overlap by about a bar.
- Background vocals for lead: under the leads (partly the same words).
- Background vocals of background vocals for lead (1): under the background vocals.
- Background vocals of background vocals for lead 2: an exact copy of Main vocal lead 2's first line (0:35–0:40) 26.6 dB quieter (correlation 1.00). It adds nothing audible, so it is left out; ask the owner if a different file was meant.

The vocal phrases start on the beat to within about 20 ms, line after line, so the stems line up with this beat file.

## Song map (measured)

| Bars | Time | Beat | Vocals |
| --- | --- | --- | --- |
| 1–15 | 0:00.0–0:30.3 | piano intro | none |
| 16–47 | 0:30.3–1:31.7 | full beat | leads from 0:31.7, background, background-of-background at 0:35 and 0:58 |
| 48–55 | 1:31.7–1:47.1 | the beat drops to piano | leads, background-of-background |
| 56–71 | 1:47.1–2:17.8 | full beat | leads, background |
| 72–79 | 2:17.8–2:33.1 | the beat drops to piano | leads, background |
| 80–95 | 2:33.1–3:03.9 | full beat | leads until 2:51.4 (bar 89), background until 2:49.8 |
| 96–104 | 3:03.9–3:19.7 | piano outro | none |

## What's working

- The autotune: held notes sit 8 cents (median) from the key's notes, 79–92% within 15 cents, 1% more than 30 cents off. Only 3 s of held C# in the background vocal, 3 of 13 of them over a beat C. No note needs moving.
- The vocals are aimed at A4 = 440 and the beat at 438.3, so every vocal stem sits about 8 cents sharp of the beat. Retuning each stem by its measured offset (−7.2 to −8.1 cents) puts the voice on the piano's tuning.

## Problem areas

- The beat is a 160 kbps YouTube rip: its top end is gone and cannot be restored. A WAV from the producer would be cleaner for streaming.
- The lead stems carry a lot of stereo width (side 8 dB under the middle, 14% of moments out of phase), which phones play in mono.
- The vocals end at 2:51.4 and the beat runs to 3:19.7 (12 s of full beat, then the 16 s piano outro).

## Creative effects requests

The owner, 2026-11-09: "good delays, good reverb, good echo throws perfectly timed, perfect progressional sound nothing less, ready for quality streaming on phone, earphones and stereos." Plus, from Driftin' Away: the background vocals sit under the leads and their own background sits under them.

| Effect | Scope (one track or whole mix) | Where it happens | How long (bars) | Plugin, if one is required | Notes |
| --- | --- | --- | --- | --- | --- |
| Echo throws | lead 1, lead 2 | the last sung word of every lead 1 line; every lead line in the two drops; the very last line | 3 echoes (4 in the drops, 8 half-note echoes on the last line) | none | each echo starts on a main beat (1/4 = 480 ms) of the grid measured from the drums |
| Reverb | leads, background layers, echoes | whole song; the lead plate opens up in the drops | — | none | plate 1.44 s (dotted half) on the leads, hall 1.92 s (1 bar) on the background layers, pre-delay 30 ms (1/64) |
| Progression | leads, background layers | A → drops → B → C | — | none | background vocals 6 dB under the leads in A, 5 in B and the drops, 4.5 in C; lead reverb −16 dB in A, −15 in B and C, −12 in the drops |
| Layer order | background vocals, background of background | whole song | — | none | background under the leads, its own background 4 dB under it, checked every 2 bars |
| Streaming master | whole mix | whole song | — | none | −11.5 LUFS, −1.0 dBTP (room for AAC/Ogg encoders), mono-safe for phones |

## Delay timing for this song

- **BPM used:** 125
- **Time signature:** 4/4

| Note | Straight (ms) | Dotted × 1.5 (ms) | Triplet × 2/3 (ms) |
| --- | --- | --- | --- |
| 1 bar (4 beats in 4/4) | 1920.00 | — | — |
| 1/2 | 960.00 | 1440.00 | 640.00 |
| 1/4 | 480.00 | 720.00 | 320.00 |
| 1/8 | 240.00 | 360.00 | 160.00 |
| 1/16 | 120.00 | 180.00 | 80.00 |

Reverb pre-delay 1/64 = 30.00 ms. Reverb decays: dotted half = 1.44 s (plate), 1 bar = 1.92 s (hall).

## Where it will be heard

- [x] Streaming (which: unknown; ask the owner)
- [x] Earbuds
- [x] Phone speaker
- [x] Stereos / car

## Deadline

- **Needed by:** unknown (ask the owner)
- **What this pass should deliver:** v1 master for the owner's listening check.

The song is fully finished only after the final sign-off in `mix-notes.md`. A rough-mix deadline is still a real deadline. It is a step, not the finished master.

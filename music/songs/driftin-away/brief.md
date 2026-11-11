# Song brief

Fill this in before any mixing or mastering. Agents read this file first and adapt their decisions to it.

If you do not know an answer yet, write "unknown" and who to ask. Do not guess a fact that will send the mix in the wrong direction.

## Song

- **Title:** Driftin' Away
- **Artist:** unknown (ask the owner, Kenshin)
- **Genre / subgenre:** rap over a trap beat (measured: rapped vocals, 808 and hi-hats, 150 BPM)
- **Mood / vibe:** dreamy. The owner chose "more, dreamy" echoes and "a little dreamier" reverb (2026-11-09).
- **BPM:** 150
- **Key:** Bb minor (tuning A4 = 439.2 Hz, measured with `tempo_key.py` on the beat; runner-up Bb major)

How the tempo was checked: the beat's onset pattern matches itself exactly at 8, 16, 32 and 48 bars of 150.000 BPM, and the hi-hats sit on a 150 BPM eighth-note grid that starts 38.4 ms into the file (beat n at 0.03837 + 0.4 n s). The drops at bar 17 and bar 57 land 1.8 ms and 0.6 ms from that grid. **Bar 1 starts at 0.038 s; bar b starts at 0.038 + (b − 1) × 1.6 s.** Every effect timing below uses this grid.

## Reference tracks

1. **Track** — unknown (ask the owner)
   - Borrow:
   - Leave alone:

## Session

Stems received 2026-11-09, 16-bit 44.1 kHz WAV, all exported from the same start point:

- Beat: `Driftin_away_beat.wav` (2:50.0, content to 16.6 kHz, so it came from a lossy file at some point)
- Lead vocal: `DRIFTIN_AWAY_LEAD_VOCALS.wav` (mono, raps 0:26.8–1:16.9, bars 17–49)
- Background vocal: `Driftin_away_background_vocals_.wav` (raps alone 1:18.0–2:17.6, bars 49–86; content to 12.4 kHz)
- Adlibs: `Driftin_away_adlib_vocals.wav` (a partial double of the lead in the verse, then short responses every 2 bars from 1:20 to 2:19)

## Song map (measured)

| Bars | Time | Beat | Vocals |
| --- | --- | --- | --- |
| 1–16 | 0:00.0–0:25.6 | intro: melody only, riser on bar 16 beat 4 | none |
| 17–22 | 0:25.6–0:35.2 | drop: full beat | lead from bar 17 beat 4 (0:26.8) |
| 23–24 | 0:35.2–0:38.4 | the beat's own 2-bar stop | lead raps a cappella |
| 25–38 | 0:38.4–1:00.8 | full beat | lead |
| 39–40 | 1:00.8–1:04.0 | the beat's own 2-bar stop | lead pauses, then one a cappella line |
| 41–48 | 1:04.0–1:16.8 | full beat (the lead comes back exactly on the downbeat) | lead |
| 49–56 | 1:16.8–1:29.6 | breakdown: melody only | background vocal from bar 49 beat 4 (1:18.0), adlib responses |
| 57–62 | 1:29.6–1:39.2 | 808 back, no hats | background vocal, adlib responses |
| 63–64 | 1:39.2–1:42.4 | the beat's own 2-bar stop | background vocal |
| 65–88 | 1:42.4–2:20.8 | full beat | background vocal (4-bar phrases from bar 73), adlib responses |
| 89–104 | 2:20.8–2:46.4 | outro: melody only, beat ends at bar 105 | none in the stems |

## What's working

- The beat's arrangement already has its own stops and drops (bars 23–24, 39–40, 63–64), and the lead comes back exactly on the bar 41 downbeat. Keep them.
- The vocals are tuned to the key (the most-sung notes are Eb3 and Db3), so the harmonic peaks at 466, 624, 934 and 1246 Hz are the melody, not room resonances. Do not notch them.

## Problem areas

- Every stem peaks at −0.1 dBFS; summed raw they clip (+5.3 dBTP). Fixed by gain staging and the limiter.
- The beat and the background vocal are band-limited (16.6 and 12.4 kHz), so keep the top-end boost modest.
- The lead raps almost without breaths from 0:33 to 1:00, so line-end echoes only fit where the next line starts at least 100 ms after the first repeat.

## Creative effects requests

The owner's answers on 2026-11-09: background vocal "Behind, as background"; echoes "More, dreamy"; reverb "A little dreamier"; extras "Fade-out ending, Stutter effect, Phone-call effect, Reverse reverb and beat stop and drops only if you can time them perfectly, if not then don't." The spots below were chosen by the engineer from the song map; the owner can move any of them.

| Effect | Scope (one track or whole mix) | Where it happens | How long (bars) | Plugin, if one is required | Notes |
| --- | --- | --- | --- | --- | --- |
| Dreamy echoes | lead vocal, adlib responses | last word of 8 lead lines (bars 19–49) and of all 16 adlib responses (bars 52–88) | 3 repeats (4 on the last response, 2 where a vocal comes straight back) | none | each repeat starts on a main beat (1/4 = 400 ms), 5 dB quieter and darker each time |
| A little dreamier reverb | lead, background vocal, adlibs, echoes | whole song | — | none | lead plate 1 bar (1.6 s), background hall 1.5 bars (2.4 s), pre-delay 1/64 (25 ms) |
| Background vocal behind | background vocal | bars 49–86 (1:18.0–2:17.6) | 37 | none | about 4 dB under the full beat, softer top, more hall |
| Phone-call effect | outro vocal | outro bars 91–101: the verse's first two lines (A, B) twice | 10 | none | lines moved by whole bars (+74, +80) so they keep their pickup on beat 4 |
| Stutter effect | outro vocal | right before each phone line (bars 91, 93, 97, 99, beat 3) | 1 beat each | none | first 75 ms of the first syllable, 4 times on 16th notes (100 ms) |
| Reverse reverb | lead, background vocal | into the first word (bar 17 beats 2–4), into the drop at bar 41 (bar 40 beat 4), into the background vocal (bar 49 beat 3) | 2 beats, 1 beat, 1 beat | none | only if perfectly timed: each swell starts on a beat and ends on the word's first sound |
| Beat stop and drops | beat | an eighth-note air gap before the drops at bar 17 (0:25.4) and bar 57 (1:29.4) | 1/8 note each | none | only if perfectly timed: the beat comes back on the drop's own transient; the beat's own 2-bar stops stay as they are |
| Fade-out ending | whole mix | bars 99–104 (2:36.8–2:46.4) | 6 | none | raised-cosine fade to silence at the beat's last bar |

## Delay timing for this song

- **BPM used:** 150
- **Time signature:** 4/4

| Note | Straight (ms) | Dotted × 1.5 (ms) | Triplet × 2/3 (ms) |
| --- | --- | --- | --- |
| 1 bar (4 beats in 4/4) | 1600.00 | — | — |
| 1/2 | 800.00 | 1200.00 | 533.33 |
| 1/4 | 400.00 | 600.00 | 266.67 |
| 1/8 | 200.00 | 300.00 | 133.33 |
| 1/16 | 100.00 | 150.00 | 66.67 |

Reverb pre-delay 1/64 = 25.00 ms. Reverb decays: 1 bar = 1.6 s (plate), 1.5 bars = 2.4 s (hall).

## Where it will be heard

- [ ] Streaming (unknown which; ask the owner)
- [ ] Radio
- [x] Earbuds / headphones (the owner judges every version on headphones)
- [ ] Car
- [ ] Phone speaker
- [ ] Club or other:

## Deadline

- **Needed by:** unknown (ask the owner)
- **What this pass should deliver:** v1 master for the owner's headphone check. Loudness −11.5 LUFS, −0.5 dBTP ceiling, the same as the approved Pushing the Interstate v4.

The song is fully finished only after the final sign-off in `mix-notes.md`. A rough-mix deadline is still a real deadline. It is a step, not the finished master.

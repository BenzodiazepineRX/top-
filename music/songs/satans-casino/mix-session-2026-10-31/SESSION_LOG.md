# Session log: Satan's Casino mix session, 2026-10-31 to 11-01

> **Corrections found on 2026-11-11** (details in `../README.md`): the bar lines used in v6 were 95 ms late, and
> clean, separate beat and lead-vocal files exist in the second workspace. Both are marked below.

One mix session, 31 October to 1 November 2026. Six versions were made. Versions 2 to 5
each got listening feedback; version 6 has not been reviewed by the artist yet.

Who did what: one agent (Claude) processed the audio. A second agent (ChatGPT) exported the files from
the artist's BandLab project and reviewed the method. A third (Grok) reviewed measurements as text. None
of the three can hear. Files moved between agents through the artist.

## Source material

| Item | Facts |
|---|---|
| Format | 2 stems, a mixdown with effects bypassed, and the artist's current master. Stereo, 16-bit, 44.1 kHz, 216.193 s, aligned from time zero |
| Tempo | 135 BPM, 4/4 (project value; detector agreed). Key shown as C major; detector agreed with low confidence |
| Track 1, named after the song | Beat and main vocal in one file (inferred from the artist's reaction to v2, then confirmed by measurement on 2026-11-11). About 30,000 samples per channel at full scale. Content stops near 15.6 kHz |
| Track 2 | Adlibs. One channel is a copy of the other, 12.2 dB quieter. The loud channel has 8,813 samples at full scale; the quiet channel has none |
| Track 2's original chain | Noise gate, graphic EQ, compressor, de-esser, delay, reverb (a vocal preset) |
| Mixdown check | Mixdown = 0.818 x track 1 + 0.814 x track 2, remainder -28.9 dB. So the project holds only these two tracks |
| Artist's master | -15.3 LUFS, true peak -0.7 dBTP |

Unresolved: the artist remembers separate beat, main vocal and adlib stems. A full check of the project
and its three older revisions found only the two tracks above. The separate beat and lead files were found on 2026-11-11 in the second
workspace's sources; see `../README.md`.

## Versions

| Version | What it did | What the artist said | Root cause | Rule it produced |
|---|---|---|---|---|
| v1 | Treated track 1 as the beat and track 2 as the lead vocal. Rebuilt the vocal as centered mono. Two-stage compression, presence boost, saturation, delay, plate reverb. Beat down 4 dB, vocal 1.5 LU under the beat. Master at -10.6 LUFS | Not sent for listening. A measurements-only review suggested changes inside the same wrong picture | Roles were assumed from track names | Confirm roles by ear first |
| v2 | v1 with the review's changes. Master at -11.1 LUFS | "All wrong": adlibs far louder than the main vocals, grainy and harsh, like an amp with the treble all the way up | Diagnosis: wrong roles, so the main vocal went down and the adlibs came forward. Compression lifted hiss with no gate. Two treble boosts and saturation. Pan removed | Confirm roles first; start from what is approved; separate measured from heard |
| v3 | Track 1 untouched at full level. Adlibs 9 LU under it, panned right as in the original. Gate added, single gentle compressor, no boosts, no saturation. Master at -12.1 LUFS | "Sounds better", but the adlibs are still grainy and harsh. Also: the original had a nice echo throw, timed to the song | Likely: the adlibs had been rebuilt entirely from the quiet channel, which carries less detail. Certain: the original delay had been removed without asking | Use the full-detail channel and patch only clipped moments. Ask which effects to keep |
| v4 | Adlibs taken from the loud channel, with the quiet channel used only around clipped samples (2.9% of samples). Darker top, softer gate. 18 echo throws on a quarter note | Add more echoes, timed to the beat. Even out the adlibs: some parts louder, some quieter, and at one point as loud as the main | No level riding. Throws only where a long gap followed | Measure the supporting vocal against the main track at intake and ride it from version 1 |
| v5 | Phrase leveling plus a ceiling under the main track. 34 throws, 3 dB louder | Adlib timing should sit with the vocals. More throws, right after the last few words of each bar. A smooth reverb that is not ampy or grainy | Timing against the lead had not been checked. Throw placement was guessed from gaps, not asked | Check timing before any time-based effect. Ask where throws should go |
| v6 | Adlibs moved 26 ms earlier. 47 throws at bar ends. Shorter, filtered reverb. 4 reverse-reverb lead-ins and 3 filter sweeps (requested through the second agent) | No feedback yet | | |

## What a better start would have changed

Most of the rework traces back to four questions that were never asked:

- What is on each track? (cost: v1 and v2)
- Which effects do you want to keep? (the delay returned in v4, and grew in v5 and v6)
- Where should the echoes land? (v5 guessed from gaps; v6 moved them to bar ends)
- Is anything out of time? (found in v6)

With the intake check and those answers, the realistic path is a careful first version and one or two
rounds of adjustment. That is an estimate from one project, not a guarantee.

## Settings as built (v6)

Evidence level is marked for each group: **heard** means the artist reacted well to it; **measured**
means numbers only.

Adlib source and chain (heard: v3 "better"; graininess not raised again after v4):
- Source: loud channel, with the quiet channel divided by 0.24614 replacing it where the loud channel
  is at or above 0.95, crossfaded over about 2 ms
- Level set to -18 dBFS active RMS; high-pass 150 Hz, 18 dB per octave
- Gate: threshold -46 dBFS, ratio 2, range -18 dB, attack 10 ms, release 300 ms
- EQ: -2 dB at 300 Hz (Q 0.9), high shelf -3.5 dB at 5 kHz, low-pass 9.5 kHz. No boosts
- Dynamic cut at 3.3 kHz (Q 1.5, threshold percentile 92); de-esser 5 to 8.5 kHz (percentile 95)
- Compressor: 2:1, threshold -24 dB, attack 20 ms, release 250 ms. No saturation
- Pan restored: left channel = 0.24614 x right channel

Level (measured; the request came from the artist's ears):
- Static gain so the adlibs sit 9 LU under track 1, then `music/tools/vocal_rider.py --margin-db 6`
- Phrase spread 4.5 dB to 2.5 dB. Loudest adlib against track 1's 2-second average: +2.4 dB to -5.2 dB

Timing (measured only):
- 11 of 56 adlib phrases matched track 1 confidently, all late, by 5 to 51 ms (median 26). One constant
  shift of 26 ms was applied, on the reasoning that recording delay is the same for a whole take

Effects (measured only; see `v6_FX_cue_sheet.md` for all 54 cues):
- Echo throws: send opens on the last word or words of each bar that has adlibs, for at most 0.45 s.
  Quarter note (444.44 ms), feedback 0.30, 200 Hz to 5 kHz in the loop, ducked 6 dB under the adlibs,
  return -6 dB. One half-note throw before a breakdown. Echoes land within 2 ms of the calculated times
- Reverb: plate, 1.2 s, pre-delay 27.8 ms, send filtered 300 Hz to 5 kHz, ducked 6 dB, return -14 dB
- Reverse-reverb lead-ins at 18.64 s, 87.47 s, 159.13 s and 186.22 s: first 0.4 s of the coming phrase,
  reversed, through a 2.4 s hall at 100% wet, reversed back. The loudest point falls 25 to 60 ms before
  the word and a 20 ms fade ends on it
- Filter sweeps on track 1 into 16.118 s, 87.229 s and 158.340 s. They also filter the main vocal,
  because it shares the track
- Bar 1 beat 1 was taken as 0.118 s. **That is 95 ms late.** The real bar line in these files is at 0.0205 s.
  The sweep times above are therefore about 97 ms after the real downbeats

Bus and master (measured; loudness never drew a comment):
- Side channel high-passed at 90 Hz. No shelf. Limiter to -12.1 LUFS, true peak -1.2 dBTP in the WAV
  and -1.0 dBTP in the decoded MP3, about 2.5 LU of limiting

## Notes on the reviews

- The measurements-only review of v1 was reasonable inside the picture it was given, and that picture
  was wrong. It could not have caught the role mistake. Two of its tone suggestions also ran against
  the numbers and were not applied. Its loudness suggestion (about -12 LUFS) was not applied in v2,
  but v3 onward ended up there.
- The exporting agent warned twice that track 1 should not be assumed to be an instrumental. That
  warning was noted and not acted on until the artist rejected v2.
- The same agent pointed out that how often a de-esser acts does not show that it acts on the right
  sounds, and that a constant timing shift is a judgment call. Both points stand.

## Mistakes caught before the artist heard them

- The first leveler measured a panned track on its quiet channel and under-read it by about 8 dB. Fixed
  by measuring the mono sum.
- A filter sweep clicked where it started. Fixed with a crossfade at both ends, then checked by
  comparing the largest sample step at each edge with the untouched audio.
- Bar numbers were off by one at exact bar lines because of floating-point rounding. Fixed by rounding
  before dividing.

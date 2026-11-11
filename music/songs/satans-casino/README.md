# Satan's Casino: where the song stands

Read this before any new version. Two workspaces have worked on this song with different files, and
neither had all of them. Written 2026-11-11.

## The three stems, and where each one is

| Stem | File | Where it is | Condition |
|---|---|---|---|
| Beat | `Satans casino beat.wav` | Branch `cursor/satans-casino-v02-0afe`, `sources/` | Clean: no samples at full scale, content to 17.5 kHz |
| Lead vocal | `Satans casino lead vocals.wav` | Same branch, `sources/` | Clean: no samples at full scale, full bandwidth |
| Adlibs | Track 2 of the owner's app project, exported with effects off | Held by the 2026-10-31 mix session, not in this repository | One channel is a copy of the other, 12.2 dB quieter. The loud channel is clipped (8,813 samples); the quiet one is not |

The app project's track 1, which the 2026-10-31 session treated as the main track, is the beat and the
lead vocal bounced into one file. Measured on 2026-11-11:

- In the vocal-free intro, track 1 equals 1.143 times the clean beat, to -29.8 dB.
- After the beat is subtracted, what is left matches the clean lead vocal with a correlation of 0.94,
  0.97 and 0.84 in three sections of the song.
- That bounce is clipped (about 30,000 samples per channel at full scale) and stops near 15.6 kHz.
- The adlib track matches neither clean file (correlation 0.03), so it is a third recording.

**Timing between the two sets:** the app exports start 904 samples (20.5 ms) later than the clean files.
To line the adlib export up with the clean beat and lead, remove its first 904 samples.

**Grid:** 135.00 BPM. In the clean files, bar lines fall on multiples of 1.777778 s from sample 0, and the
hats and kick clicks land about 4 ms after them. In the app exports the same bar lines are at 0.0205 s
plus multiples of a bar.

## What each workspace made

**Mix session, 2026-10-31 to 11-01 (app exports: bounce plus adlibs).** Six versions.
`mix-session-2026-10-31/` holds the build script and cue sheet of the last one.

| Version | What the owner said |
|---|---|
| v2 | "All wrong": adlibs far louder than the main vocals, grainy and harsh. The session had taken the bounce for the beat and the adlibs for the lead |
| v3 | "Sounds better", adlibs still grainy and harsh; he missed the echo throw from his own version |
| v4 | Wanted more echoes on time, and even adlib levels; one adlib was as loud as the main |
| v5 | Adlib timing should sit with the vocals; throws after the last words of each bar; a smooth reverb |
| v6 | No answer yet |

Known fault in v6: its bar lines were 95 ms late, because they were taken from the kick's low end. The
echo throws and reverse swells follow the words and are not affected. The high-pass sweep into bar 50
(1:27) is: it ended 97 ms after the real downbeat and took 16.5 dB of bass off the first hit there.

**Second workspace, 2026-11-09 to 11-10 (clean beat and lead, no adlibs).** Branch
`cursor/satans-casino-v02-0afe`, pull request #6. v02 was rejected: the added vocal at the start was cut
off and off the beat. v03 to v07 were not heard by anyone. Those versions keep the beat and lead dry
(no EQ, no compression, no limiter) and add a telephone copy of lines and last-word echoes.

## What a next version should start from

1. The clean beat and the clean lead vocal, plus the adlib track shifted by 904 samples.
2. The lead processed on its own for the first time: tone matched toward an approved lead (see
   `../../LESSONS.md`), about 0.5 dB under the beat.
3. Adlibs 6 to 6.5 dB under the lead where both sing, panned where the owner had them, with the chain
   from the mix session (gate, cuts only, gentle compression) that he called better.
4. Effects he has asked for on this song: echo throws on the last words of adlib bars, reverse reverb
   into entrances, filter sweeps at two or more transitions, a telephone part, build-ups into the two
   beat stops. Sweeps can now go on the beat alone.
5. One version sequence from here on. Call the next one v7 and say in the notes which files it used.

Ask the owner first whether a separate adlib file exists in the same folder as the clean beat and lead.

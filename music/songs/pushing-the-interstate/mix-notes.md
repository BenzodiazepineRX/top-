# Mix notes

**Song:** Pushing the Interstate

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

### 2026-11-09 — v17 (the near-miss, with the echoes you can actually hear)

v16 was close. v17 keeps that mix and only changes the echoes he pointed at.

The adlib echoes are a little louder, about 3 dB, and each one blooms in a short plate (1.2 seconds, lows and highs trimmed) so they repeat and fade instead of stopping. The phone voice is pulled down so it sits with the verses: it was 8 dB hotter than the verse against the beat, and a 4 dB cut would still have left it 4 dB hot, so it came down 8 dB. It was +1.2 dB against the beat; it is now −5.6 dB, next to the verse vocal at −7.0 dB. Behind those lines is a higher phone echo, one beat later (465.12 ms), about 12 dB under the line, three repeats fading out. The stutters are longer: at least an eighth note (233 ms), most of the first word, on the beat, and the real word has not moved. Lead echoes now repeat about three times (feedback 0.5) instead of dying after one, the copied words are kept under one beat so the repeats do not pile up, and the endings fade instead of cutting off.

- **Files:** `Pushing_the_Interstate_master_v17_24bit.wav`, `Pushing_the_Interstate_master_v17.mp3`, `Outro_preview_v17.mp3` (from 2:08), `Pushing_the_Interstate_v17_effects_bus_24bit.wav`.
- **Loudness:** −11.7 LUFS, true peak −0.9 dBTP on the WAV.
- **Checked and fixed:** the second repeat of the 1:17.7 echo was ending in a cut around 1:19, and an adlib echo cut off at 2:14.7. Both now fade. The copies at 1:28.1 and 1:58.1 were longer than a beat, so every lead copy over 0.42 s was trimmed to the last 0.42 s with a fade.
- **Grid:** lead echoes, the verse throw and the stutters land within 3 ms of an eighth-note line at 129 BPM. Two of those eighths (the 1:28 echo and the verse-1 throw) are the off-beat eighth, about 231 ms from a downbeat. Moving them onto the downbeat would shift the echo by more than a fifth of a second, so they stay on that eighth and are flagged below. The phone echo is exactly 465.12 ms after each line. Those lines were not put on a downbeat in v4, so the echo sits 19 ms or 99 ms off the nearest eighth. That is the line's own placement, not a wrong delay time.

| What | Source (s) | First tap (s) | Lag (ms) | Off 1/8 (ms) | Off 1/4 (ms) | Note |
| --- | --- | --- | --- | --- | --- | --- |
| Lead, 0:34.0 | 34.030 | 34.419 | 389 | +0.6 | +0.6 | nudged onto the beat |
| Lead, 0:37.8 | 37.760 | 38.140 | 380 | +0.7 | +0.7 | nudged onto the beat |
| Lead, 0:41.5 | 41.480 | 41.861 | 381 | +0.8 | +0.8 | nudged onto the beat |
| Lead, 1:15.8 | 75.830 | 76.280 | 450 | +1.4 | +1.4 | nudged onto the beat |
| Lead, 1:17.7 | 77.710 | 78.141 | 431 | +1.4 | +1.4 | fade, three repeats |
| Lead, 1:27.8 | 87.760 | 88.141 | 381 | +1.6 | −231.0 | on the eighth, flagged |
| Lead, 1:45.6 | 105.580 | 106.048 | 468 | +1.9 | +1.9 | on the beat |
| Lead, 1:47.5 | 107.460 | 107.909 | 449 | +2.0 | +2.0 | on the beat |
| Lead, 1:57.7 | 117.740 | 118.142 | 402 | +2.1 | +2.1 | trimmed under a beat |
| Verse-1 throw | 60.160 | 61.164 | 1004 | +1.1 | −231.5 | on the eighth, flagged |
| Adlib delay | phrase | +348.84 ms | 348.8 | follows the phrase | same | +3 dB, short plate on the repeats only |
| Phone block 1 A | 135.136 | 135.601 | 465.1 | +19.4 | −213.1 | exact one beat; line is not on a downbeat |
| Phone block 1 B | 138.971 | 139.436 | 465.1 | −98.9 | −98.9 | exact one beat |
| Phone block 2 A | 142.578 | 143.043 | 465.1 | +19.4 | −213.1 | exact one beat |
| Phone block 2 B | 146.413 | 146.878 | 465.1 | −98.9 | −98.9 | exact one beat |
| Phone block 3 A | 150.019 | 150.485 | 465.1 | +19.4 | −213.1 | exact one beat |
| Phone block 3 B | 153.855 | 154.320 | 465.1 | −98.9 | −98.9 | exact one beat |
| Stutter 1A ×3 | 135.136 | 134.421, 134.654, 134.886 | 233 ms chops | +2.4 | on the eighth | three, into the word |
| Stutter 1B | 138.971 | 138.607 | 290 ms | +2.5 | +2.5 | one, the gap holds one |
| Stutter 2A | 142.578 | 142.328 | 233 ms | +2.6 | +2.6 | one |
| Stutter 2B | 146.413 | 146.049 | 286 ms | +2.7 | +2.7 | one |
| Stutter 3A | 150.019 | 149.770 | 233 ms | +2.7 | +2.7 | one |
| Stutter 3B | 153.855 | 153.491 | 286 ms | +2.8 | +2.8 | one |

### 2026-11-09 — v16 (the v4 song, with the echoes cleaned up and the phone outro finished)

Chex, this is the version that sounded right around 10:39, with two things added only on the phone ending: a higher little echo after each line, and a short stutter into the first word. The echoes sit under the vocal. They repeat a few times and fade. They do not take over the song.

- **Files:** `Pushing_the_Interstate_master_v16_24bit.wav`, `Pushing_the_Interstate_master_v16.mp3`, `Outro_preview_v16.mp3` (from 2:08), `Pushing_the_Interstate_v16_effects_bus_24bit.wav` (echoes, delays, the verse throw, the outro ring and the stutters only).
- **What stayed from v4:** 129 BPM, the vocal sound, the beat, the plate, the phone-call lines in the same places, the halls, and the fade. The adlib delay is still the dotted eighth, 348.84 ms, feedback 0.35.
- **Lead echoes:** v4 copied a fixed 0.30 s slice. On the processed vocal that slice started in the middle of the last word, and on the lines around 34.1, 37.8, 75.9, 77.8 and 117.6 it ended while the word was still going. v16 copies the whole last word, from its start through its ending, with a short fade so it does not click. The delay time is still one quarter note, 465.12 ms, the same lag v4 used. Feedback stays 0.35, so about three repeats are audible (full, then about 9 dB down, then about 18 dB down) and the rest fade out. The first repeat is set about 12 dB under the dry word. Ducking is 4 dB with an 80 ms release, so the echo is not hidden and does not sound late.
- **Verse-1 throw:** same half-note lag, 930.23 ms, on the last word into the break. v4's throw was about as loud as the vocal there. It is now about 9 dB under, so it does not compete with the beat.
- **Printed FX stem:** the throws at 35.6, 39.3, 43.0, 47.1, 54.6 and 61.1 s were checked against the 129 BPM grid. 35.6, 39.3, 43.0 and 54.6 start on the "and" (about 230 ms, one eighth note, off the quarter). 43.0 is the one that sits on the and. 47.1's body is 172 ms off the quarter. 61.1's center is on the and, and it would have doubled the verse throw. Those six are muted, with a short fade so the mute is not a click. 58.2 starts 10 ms from the quarter, so it was left in. Around 135.0 s a one-beat copy and a two-beat copy of the same adlib land on top of each other; that spot is turned down 6 dB so one copy's level remains.
- **Phone outro:** the lines, halls and fade are v4's. Added a delay a little higher in pitch (+3 semitones), one quarter note (465.12 ms) after what is said, three audible repeats, about 12 dB under the phone vocal, light duck (4 dB, 80 ms). The last "interstate" uses the half-note ring only, so that word does not also get a one-beat copy in the same place. Stutters are the first 75 ms of the first syllable, repeated on sixteenth notes (116.28 ms) and ending as the real word starts. The first line has room for four. Each "I'm" line has room for three. The later "since" lines sit right against the line before them (about 155 ms of space), so only one repeat fits without talking over that lyric.
- **Loudness:** −11.5 LUFS, true peak −0.9 dBTP on the WAV, −0.7 dBTP on the MP3. v4 was −11.6 LUFS and −0.7 dBTP. The beat's last second finishes fading to silence, so the track does not stop dead at 2:39. The song runs about 2:41.
- **v16 versus the v4 render** (same limiter, difference energy): verse 1 −27 dB, the break −38 dB, verse 2 −38 dB, just before the phone −43 dB, the phone outro −14 dB. The verses differ where the echoes and the muted FX throws are. The outro is the part that was meant to change.

**Effects bus compared with the dry vocal** (a more negative number means the echoes are further under the voice):

| Section | v16 | v4 | What changed |
| --- | --- | --- | --- |
| Verse 1 (0:20–1:00) | −25.1 dB | −25.2 dB | same weight |
| Break (1:01–1:14) | −9.4 dB | −0.1 dB | the throw no longer sits on top of the track |
| Verse 2 (1:15–2:05) | −24.4 dB | −26.5 dB | still well under the vocal |
| Phone outro (2:14–2:35) | −14.9 dB | −20.9 dB | you can hear the new higher echo; it stays under the phone voice |
| Fade (2:35–end) | −18.2 dB | −6.1 dB | the ending ring is quieter than v4 so it fades instead of hanging on |

**Echo and stutter times.** Lag is the delay v4 used: quarter note 465.12 ms, half note 930.23 ms, dotted eighth 348.84 ms, all at 129 BPM. The grid column is how far the first tap sits from the nearest eighth-note line (and the nearest sixteenth, for the stutters). A small number means it is close to that line. v4 did not snap echoes onto the drums, and v16 does not either.

| What | Source (s) | First tap (s) | Lag (ms) | Off the 1/8 grid (ms) | Off the 1/16 grid (ms) | Compared with v4 |
| --- | --- | --- | --- | --- | --- | --- |
| Lead line ending | 33.950 | 34.415 | 465.1 | −3.5 | −3.5 | whole word through 34.450; same lag |
| Lead line ending | 37.680 | 38.145 | 465.1 | +5.6 | +5.6 | whole word through 38.180; same lag |
| Lead line ending | 41.410 | 41.875 | 465.1 | +14.7 | +14.7 | whole word through 41.900; same lag |
| Lead line ending | 75.820 | 76.285 | 465.1 | +6.0 | +6.0 | whole word through 76.250; same lag |
| Lead line ending | 77.710 | 78.175 | 465.1 | +35.6 | +35.6 | whole word through 78.130; same lag |
| Lead line ending | 87.680 | 88.145 | 465.1 | +5.6 | +5.6 | whole word through 88.180; same lag |
| Lead line ending | 105.570 | 106.035 | 465.1 | −11.4 | −11.4 | whole word through 106.000; same lag |
| Lead line ending | 107.450 | 107.915 | 465.1 | +8.1 | +8.1 | whole word through 107.880; same lag |
| Lead line ending | 117.660 | 118.125 | 465.1 | −14.4 | −14.4 | whole word through 118.160; same lag |
| Verse-1 throw | 60.160 | 61.090 | 930.2 | −72.6 | +43.7 | same half-note lag; quieter |
| Adlib delay, all 45 phrases | phrase start | +348.84 ms | 348.8 | follows the phrase, not the grid | same | same dotted eighth and feedback as v4; level about 12 dB under; duck release 80 ms instead of 300 ms |
| Phone line, block 1 A | 135.076 | 135.541 | 465.1 | −40.4 | −40.4 | new higher voice; same quarter lag |
| Phone line, block 1 B | 138.966 | 139.431 | 465.1 | −103.9 | +12.4 | new higher voice; same quarter lag |
| Phone line, block 2 A | 142.523 | 142.988 | 465.1 | −35.4 | −35.4 | new higher voice; same quarter lag |
| Phone line, block 2 B | 146.408 | 146.873 | 465.1 | −103.9 | +12.4 | new higher voice; same quarter lag |
| Phone line, block 3 A | 149.965 | 150.430 | 465.1 | −35.4 | −35.4 | new higher voice; same quarter lag |
| Last "interstate" ring | 153.855 | 154.785 | 930.2 | −98.9 | +17.4 | half-note ring only, higher voice, three repeats |
| Stutter, block 1 "since" 1/4 | 135.076 | 134.652 | −424 | +0.9 | +0.9 | on the sixteenth grid |
| Stutter, block 1 "since" 2/4 | 135.076 | 134.768 | −308 | −115.4 | +0.9 | on the sixteenth grid |
| Stutter, block 1 "since" 3/4 | 135.076 | 134.885 | −191 | +0.9 | +0.9 | on the sixteenth grid |
| Stutter, block 1 "since" 4/4 | 135.076 | 135.001 | −75 | −115.4 | +0.9 | ends as the word starts |
| Stutter, block 1 "I'm" 1/3 | 138.966 | 138.658 | −308 | +53.7 | +53.7 | sixteenth spacing into the word |
| Stutter, block 1 "I'm" 2/3 | 138.966 | 138.775 | −191 | −62.6 | +53.7 | sixteenth spacing into the word |
| Stutter, block 1 "I'm" 3/3 | 138.966 | 138.891 | −75 | +53.7 | +53.7 | ends as the word starts |
| Stutter, block 2 "since" | 142.523 | 142.448 | −75 | −110.4 | +5.8 | only one fits without covering the line before it |
| Stutter, block 2 "I'm" 1/3 | 146.408 | 146.100 | −308 | +53.7 | +53.7 | sixteenth spacing into the word |
| Stutter, block 2 "I'm" 2/3 | 146.408 | 146.216 | −191 | −62.6 | +53.7 | sixteenth spacing into the word |
| Stutter, block 2 "I'm" 3/3 | 146.408 | 146.333 | −75 | +53.7 | +53.7 | ends as the word starts |
| Stutter, block 3 "since" | 149.965 | 149.890 | −75 | −110.4 | +5.8 | only one fits without covering the line before it |
| Stutter, block 3 "I'm" 1/3 | 153.855 | 153.547 | −308 | +58.7 | −57.6 | sixteenth spacing into the word |
| Stutter, block 3 "I'm" 2/3 | 153.855 | 153.663 | −191 | −57.6 | −57.6 | sixteenth spacing into the word |
| Stutter, block 3 "I'm" 3/3 | 153.855 | 153.780 | −75 | +58.7 | −57.6 | ends as the word starts |

The delay engine places every lead, adlib and phone repeat at exactly 20512 samples (465.12 ms), 41023 samples (930.23 ms) or 15384 samples (348.84 ms). A cross-check of the adlib delay landed at 349.8 ms. The filtered copies of the lead and phone words read a couple of milliseconds off that in a correlation, because the tone filter changes the shape of the word; the delay itself is the sample count above.

### 2026-11-09 — v15-master (the 0:41 echoes are on the beat, and they fade)

- **Files:** `Pushing_the_Interstate_master_v15_24bit.wav`, `Pushing_the_Interstate_master_v15.mp3`.
- **What changed:** v14 is not the fix. Its repeats land on the off-beat, and they were added on top of v13, so the old repeats are still there. v15 starts from v13 again. Everything outside about 0:42 to 0:48 is the same as v13, including the outro. Inside that spot, three things that were stacking are taken out, and one short echo is put back.
- **Taken out:** the printed FX echoes at 43.03–43.62 and 46.99–47.29 (the 43.03 one starts 226 ms before the beat, which is the "and" of the beat). Also the v13 copies of the whole line: the adlib copy from 43.25–44.19 is 940 ms long, and the lead copy from 46.03–46.81 is 780 ms long. A copy that long covers the next beat, so it sounds like the line keeps going and never fades.
- **Put back:** only the last word, starting on the next quarter-note beat after that word has finished. One quieter copy follows one beat later, about 12 dB down, on the other side, then it stops. The first copy sits about 11 dB under the dry word. No ducking, so the start of the echo is not hidden.
- **Where they land (129 BPM, quarter = 465.12 ms):** lead "awake" (41.40–41.88) at 42.326 and 42.791. Adlib "awake" (42.40–42.82) at 43.256 and 43.721. Lead "away" (45.42–45.76) at 46.047 and 46.512. Adlib "away" (46.36–46.76) at 46.977 and 47.442.
- **Later in the song:** these two lines are not said again in the lead or the adlibs. The second verse repeats other lines ("just cause you're not around", "I came from the crime"). It does not repeat "stay awake" or "five minutes away". If the owner names another time where they hear those words, that time gets this same treatment.
- **Loudness:** −11.6 LUFS, true peak −0.7 dBTP (WAV) / −0.2 dBTP (MP3).
- **Listening check:** pending owner, 0:41–0:48, then a pass on the other adlib delays. Those other adlib delays were already a short word plus one quiet repeat, so they were left alone.

### Note for Copilot (please read this before editing the echoes again)

v14's echoes are off. The owner said so, and the grid says so too.

The v14 notes call these times "drum-locked" quarter notes: 42.076, 42.554, 45.813, 46.277, 43.027, 43.455, 46.980, 47.380. At 129 BPM the quarter grid here is 42.326, 42.791, 43.256, 43.721, 46.047, 46.512, 46.977, 47.442. Most of the v14 times are about 230 ms early of that grid. 230 ms is an eighth note, the off-beat. An echo that starts on the "and" is the thing the owner is hearing as off. 46.980 is the only one of those eight that actually lands on a quarter.

v14 also only dipped v13 by about 1.1 dB in that spot, then added another layer from about 42.03–44.32 and 45.92–48.22. The old repeats are still playing. Stacking another set on top is why it still does not fade.

Do not snap these echoes to drum hits. That was tried in v7 and the owner rejected it. Do not use a 300 ms duck release. That hides the attack and makes the echo sound late. Do not copy the whole line. The line is longer than one beat, so the copies pile up.

The rule for this song: echo the last word only. Start that copy on the next quarter-note beat after the word has finished (`beat = n * 60/129`, quarter = 465.12 ms = 20512 samples at 44100 Hz). One more copy, one beat later, about 12 dB quieter, then stop. Take the off-beat FX echo out first so it does not double the new one. v15 does that for the only place these two lines are said.

### 2026-11-09 — v14-master (timing correction patch on v13)

- **Files:** `Pushing_the_Interstate_master_v14_24bit.wav`, `Pushing_the_Interstate_master_v14.mp3`.
- **What changed:** this keeps v13 as the base (so the full arrangement, outro and fade stay the same), then patches only the two problem call-and-response spots (about 0:42 to 0:48). Those words were re-echoed from the stems with beat-locked quarter-note repeats on both lead and adlibs (2 repeats only). The v13 base is dipped by about 1.1 dB only inside those two windows so the corrected repeats can read clearly.
- **Where they land (drum-locked):** lead repeats at 42.076, 42.554, 45.813, 46.277. Adlib repeats at 43.027, 43.455, 46.980, 47.380. All at 129 BPM (1/4 = 465.12 ms).
- **Loudness:** −11.7 LUFS, true peak −0.9 dBTP (WAV) / −0.6 dBTP (MP3), loudness range 7.7 LU.
- **Listening check:** owner says these echoes are also off. The times above are about an eighth note early of the quarter grid. See v15. Do not build the next version on this file.

### 2026-11-09 — v13-master (undo the stacked echoes, fade the repeats)

- **Files:** `Pushing_the_Interstate_master_v13_24bit.wav`, `Pushing_the_Interstate_master_v13.mp3`.
- **What changed:** v12 echoed the whole "stay awake" and "five minutes away" lines three times on the lead and again on the adlib, so the repeats stacked and did not sound like they faded. v13 takes that back. Only the last word of each line is echoed, and it starts on the next beat. One quieter repeat follows, about 14 dB down, then it stops. Every other adlib delay is two repeats, not three, with the second about 15 dB down. The printed FX stem is back. Those two lines are not said again later in the vocal or the adlibs.
- **Loudness:** −11.6 LUFS, true peak −0.7 dBTP.

### 2026-11-09 — v12-master (stay awake / five minutes away echoes on the beat)

- **Files:** `Pushing_the_Interstate_master_v12_24bit.wav`, `Pushing_the_Interstate_master_v12.mp3`.
- **What changed:** the echoes of "just tryna stay awake" and "only five minutes away" were landing between the beats from 0:42 to 0:46. Each of those lines is echoed once on the lead and once on the adlib, and every copy now starts on a quarter-note beat, then repeats twice more, one beat apart, fading out. The old off-beat echoes of those words in the printed FX stem are turned down. The rest of the vocal was checked: those two lines are not said again later.
- **Where they land:** stay awake at 42.326, 42.791, 43.256 (lead) and 43.256, 43.721, 44.186 (adlib). Five minutes away at 46.047, 46.512, 46.977 (lead) and 46.977, 47.442, 47.907 (adlib). All at 129 BPM.
- **Loudness:** −11.6 LUFS, true peak −0.7 dBTP.

### 2026-11-09 — v11-master (stutters say the whole first word, on the beat)

- **Files:** `Pushing_the_Interstate_master_v11_24bit.wav`, `Pushing_the_Interstate_master_v11.mp3`.
- **What changed:** the outro stutters were 80 ms chops on 16th notes, so they were too fast and off the beat, and the word never finished. Each cut is now the whole first word: "since" is 240 ms, "I'm" is 360 ms. The cuts start on quarter-note beats (465.12 ms apart at 129 BPM). The last cut finishes as the real line begins. Two cuts per line, not four fast ones. Delays are the v10 ones: the first echo starts one beat after the word ends, then two quieter repeats fade out.
- **Loudness:** −11.6 LUFS, true peak −0.7 dBTP.
- **Listening check:** pending, outro from about 2:14.

### 2026-11-09 — v10-master (echoes start after the word, not on top of it)

- **Files:** `Pushing_the_Interstate_master_v10_24bit.wav`, `Pushing_the_Interstate_master_v10.mp3`.
- **What changed:** the adlib delay and the lead echoes were landing too soon. v9 started the echo a beat after the *beginning* of the word, so it came in while the word was still finishing and sounded like a quick repeat. v10 starts the first echo one full beat after the word *ends* (465.12 ms at 129 BPM). Two quieter repeats follow, then it fades out. The adlib delay is no longer on every syllable. It is only on the end of each adlib phrase, under the lead.
- **Delay times:** quarter note 465.12 ms after the end of the phrase. Three repeats, feedback 0.35. Duck releases in 100 ms so the echo is not hidden.
- **Loudness:** −11.6 LUFS, true peak −0.7 dBTP.
- **Listening check:** pending. This replaces v9.

### 2026-11-09 — v9-master (adlib delay and lead echoes rebuilt from the stems)

- **Files:** `Pushing_the_Interstate_master_v9_24bit.wav`, `Pushing_the_Interstate_master_v9.mp3`. Rebuilt from the four stems, not layered on the v4 WAV. Audio is not committed.
- **What changed:** the adlib delay and the echoes under the lead are new renders, so the old ones are not still hiding under them.
  - *Adlib delay:* dotted eighth at 129 BPM, **348.84 ms** (15384 samples). Three repeats, feedback 0.35, so the second is about 9 dB down and the third about 18 dB down, then it is gone. It sits 8 dB under the lead while the lead is singing, and the duck lets go in 100 ms, so the repeat is not covered up and does not sound late.
  - *Lead echoes:* quarter note, **465.12 ms** (20512 samples), on the last 0.30 s of each line. Same three-repeat fade. 6 dB under the lead, 100 ms release. The verse-1 throw is a half note, **930.23 ms**.
  - Vocal chain, beat, 808 control, plate, phone outro, and fade follow the v4 notes. The measured lead gain (+8.8 dB), de-esser, and compression matched those notes. Outro echoes are the pitched quarter-note repeats from v8, three taps, same fade.
- **Why:** the v4 file already had the old delays printed in. Adding new ones on top would have doubled them. The stems were the way to replace them.
- **Loudness:** −11.6 LUFS integrated, true peak −0.7 dBTP, loudness range 7.8 LU. Limiter took about 0.5 LU.
- **Delay times used:** 1/8 dotted 348.84 ms, 1/4 465.12 ms, 1/2 930.23 ms, all at 129 BPM. Checked from the delay tool's sample count, not from a drum-hit snap.
- **Listening check:** pending owner, on the adlibs and the lead echoes first.
- **Next:** if a repeat is too many, too few, too loud, or still feels late, say which part.

### 2026-11-09 — v8-master (v4 kept, outro echoes in the adlib-delay style)

- **Files:** `Pushing_the_Interstate_master_v8_24bit.wav`, `Pushing_the_Interstate_master_v8.mp3`, `Outro_preview_v8.mp3` (from 2:08). Built on the owner's v4 WAV. The verses are the v4 master with nothing added. Audio is not committed (see `.gitignore`).
- **What changed:** only the phone-call outro. v4's phone lines, halls, fade, verse echoes, and adlib delay are the ones already in that file.
  - *Pitched outro delay:* each phone line gets a delay a little higher in pitch (+3 semitones). It is the same idea as the adlib delay under the main vocal: it sits under the line, repeats a few times, and fades out. Timing is one quarter note at 129 BPM, 465.12 ms (20512 samples). Three repeats: full level, then about 9 dB down, then about 18 dB down, then gone. Feedback 0.35, the same fade shape as the adlib delay. While the line is singing the echo is 6 dB under it and comes back within 100 ms, so the repeat is not hidden and does not sound late. It is not snapped to drum hits.
  - *Stutters:* the first 80 ms of each outro line ("si" and "I'm") repeats on 16th notes (116.28 ms) before the word, then the word plays where v4 already put it. Four repeats before the first line, three before each "I'm" line. The gap before the later "since" lines only holds one repeat without covering the line before it, so those two get one.
- **Why:** owner on v4 liked the adlib delay (under the vocal, a few repeats, fade out) and wanted the echoes on time. v5–v7 changed the outro layout and moved verse echoes onto drum hits. v8 starts from the signed-off v4 file and only adds the missing outro pieces.
- **Loudness:** −11.5 LUFS integrated, true peak about −0.2 dBFS, loudness range 7.6 LU. v4 was −11.6 LUFS and −0.7 dBTP. The verses were not turned down.
- **Delay times used:** quarter note 465.12 ms, 16th note 116.28 ms, both at 129 BPM. Adlib delay already in v4 stays at dotted 8th, 348.84 ms.
- **Listening check:** pending owner, headphones, outro from 2:14.
- **Next:** if a repeat is too loud, too quiet, or the pitch is too high, say which. The verse delays are still the v4 ones.

### 2026-11-09 — v7-master (verse echoes locked to the drums)

- **Files:** `Pushing_the_Interstate_master_v7_24bit.wav`, `Pushing_the_Interstate_master_v7.mp3`, `v6_vs_v7_verse_0m33.mp3`, `v6_vs_v7_verse_1m52.mp3`. Audio delivered in chat, not committed.
- **What changed:** the verse echoes (lead line-end echoes, the verse-1 throw, every adlib echo) are rendered with the new `groove_delay.py`, which puts each repeat on the beat's real drum hit nearest to the musical note value after the word's attack. Outro unchanged from v6.
- **Why:** owner, on headphones, on v6: the verse echoes are "off again", late or early. v5 had already made every echo exactly one beat after its word (465.3–465.5 ms). Measured against the actual drum onsets: the words sit up to ~45 ms ahead of or behind the drums, and the beat swings, so tempo-exact echoes landed up to 36 ms off the drums (lead) and half the adlib echoes more than 20 ms off. Alone in the gaps, that reads as late or early. Now the first lead echoes land within 0.3 ms of a drum hit and the adlib echoes within 0.6 ms (median), checked by cross-correlation of each word with its echo against independently detected drum hits.
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.5 dBTP (MP3), limiter loss 0.7 LU.
- **Effects log and review report:** `effects/v7.json`, `reports/v7.md`.
- **Lesson:** "on the tempo" is not "on the beat". Echoes heard on their own must land on the drums; three earlier fixes (tempo, ducking, exact lag) each perfected a number that wasn't the problem. Check echoes against the drum hits, not the grid.
- **Listening check:** pending owner on v7.

### 2026-11-08 — v6-master (real stutters, delay through the whole outro)

- **Files:** `Pushing_the_Interstate_master_v6_24bit.wav`, `Pushing_the_Interstate_master_v6.mp3` (2:53), `Outro_preview_v6.mp3` (2:08 to end). Audio delivered in chat, not committed.
- **What changed (outro only; verses as v5):**
  - *Owner's correction on v5:* the stutters wanted are "where the first half part of a syllable or word repeats 3-4 times before the whole things gets said", not repeats after a word; and the outro delay should play "as the bars play… after what's being said", perfectly timed, not only in a few spots.
  - *Layout:* four lines, A, B, A, B, each moved by whole bars (56, 57, 62 and 63 bars) so every line keeps its original pickup beat, with about one bar (2 s) of space before each. Back-to-back lines (v4/v5) left no room for 3-4 repeats on the beat. Ends on line B.
  - *Stutters:* the first 75 ms of each line's first syllable ("si", "I"), repeated 4 times on 16th notes (116.28 ms apart) right before the whole word, rising −1.5 to 0 dB.
  - *Delay:* all four lines sent through a pitched (+3 semitones) quarter-note ping-pong delay with light ducking: 8–9 dB under each line, 10–12 dB under it in the open bars, lag 465.42 ms by cross-correlation. Stutters stay dry.
  - *Ending:* half-note ring-out on the last "interstate" (feedback 0.76), pitched up, about 7.5 s past the beat's hard stop; ending check passes (largest sudden drop 18.7 dB).
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.5 dBTP (MP3), loudness range 7.9 LU, limiter loss 0.7 LU.
- **Effects log and review report:** `effects/v6.json`, `reports/v6.md`: ⚠️ close, 59 passed, 4 to check, 0 failed (mids from the phone outro, intended; old FX stem; outro line words to confirm).
- **Listening check:** pending owner on v6.
- **Next:** owner listens; if approved, the sign-off moves to v6.

### 2026-11-08 — v5-master (echo timing fix, pitched outro echoes, stutters)

- **Files:** `Pushing_the_Interstate_master_v5_24bit.wav`, `Pushing_the_Interstate_master_v5.mp3` (2:51), `Outro_preview_v5.mp3`, `v4_vs_v5_echoes_0m33.mp3`, `v4_vs_v5_echoes_1m14.mp3`. Audio delivered in chat, not committed.
- **What changed:**
  - *Verse echoes:* owner, on headphones after the v4 sign-off: echoes "a bit off track", in the verses, landing late or early. Measured: the delay time was exact, but heavy ducking (−8 dB, 300 ms release) pushed each echo's start under the next line, so it surfaced 15–36 ms late, and a fixed 0.30 s window could clip the start of the word. Now each echo carries the whole last word from its detected start, with ducking cut to −3 dB (5 ms attack, 120 ms release); cross-correlation puts every echo 465.3–465.5 ms after its word (one beat at 129, within 0.5 ms). Adlib echo ducking lightened to −6 dB / 150 ms for the same reason.
  - *Outro echoes, pitched up:* owner asked for echoes in the outro with the delay vocal "a little more high pitched". The always-on phone echo is replaced by echoes of the last word of block 1's two lines, pitched up 3 semitones (rubberband; its 6 ms early smear compensated, aligned within 1 ms), plus the two "interstate" throws now pitched up the same way. Echo lag measured 465.4 ms.
  - *Stutters:* owner asked for stutters in the outro. "I-I-I-I'm" (three 1/32 repeats) in the 0.22 s gap before line B in blocks 2 and 3, and "-state-state-state-state" (four 1/16 repeats fading −2 to −8 dB) after the final word as the beat fades. Only free space is used, so no lyric is cut; block 2/3 line-A echoes are dropped so they don't muddy the stutters.
- **Why:** owner requests (brief: "Outro echoes, pitched up", "Outro stutters") and the owner's headphone check.
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.4 dBTP (MP3), loudness range 7.5 LU, limiter loss 0.7 LU.
- **Effects log and review report:** `effects/v5.json`, `reports/v5.md`: ⚠️ close, 63 passed, 4 to check, 0 failed (mids up from the phone outro, intended; old FX stem; outro line words to confirm).
- **Key note:** I first told the owner the +3 semitone echo "fits F minor"; F minor is the next song's key. This song measured F major. The rap is spoken, so a third-up echo reads as a higher voice; +5 or +12 semitones are the in-key options if it ever sounds wrong.
- **Lesson:** heavy ducking on a delay makes echoes sound late, because the listener hears the echo when it surfaces, not when it starts. For dense rap, echo whole line-end words with light, fast ducking and verify the lag by cross-correlation.
- **Listening check:** pending owner on v5.
- **Next:** owner listens on headphones; if approved, the sign-off moves from v4 to v5.

### 2026-11-08 — v4-master (phone-call outro, line-end echoes, fade-out)

- **Files:** `Pushing_the_Interstate_master_v4_24bit.wav`, `Pushing_the_Interstate_master_v4.mp3` (2:51), `Outro_preview_v4.mp3` (2:08 to end), `Lead_echo_preview_v4.mp3` (0:30–1:03). Audio delivered in chat, not committed.
- **What changed:**
  - *Phone-call outro:* line A (0:30.88–0:34.41) and line B (0:34.78–0:38.15) alternate in three 4-bar blocks at bars 73, 77 and 81, moved by whole bars at 129 BPM (104.186, 111.628, 119.070 s) so each keeps its pickup beat. Telephone effect: 420 Hz–3.2 kHz band, +4 dB at 1.8 kHz, 8 kHz resample, saturation, 6:1 compression, line hiss at −34 dB; block 3 darker (2.6 kHz). Quarter-note echoes in the gaps, half-note throws on "interstate" at the end of blocks 2 and 3, halls of 1 and 1.5 bars. Outro bus 1.5 dB under the first draft, as asked.
  - *Lead vocal echoes:* only on the last word of each real line ending (9 spots, 1/4 note = 465.12 ms), silent everywhere else and off at the end of verse 2; plus a half-note throw (930.23 ms) on the last word of verse 1 into the instrumental break.
  - *Fade-out:* beat and old FX stem fade −10 dB over bar 82 to the beat's hard stop at 2:39.2; the last "interstate" echoes past the stop to silence.
- **Detour, logged so it isn't repeated:** the owner heard the first lead delay (always on, ducked) as "not perfectly timed". I wrongly blamed the tempo: a 16th-grid fit on the hats and snare said 128.71 BPM, and I rebuilt everything at 128.71. The owner then heard the outro go off beat. A direct test settled it: the beat's own drum pattern repeats at shifts of 104.186, 107.906 and 111.628 s for 56, 58 and 60 bars, exactly 129 BPM; the grid fit had locked onto a false nearby tempo (its error wrapped in a sawtooth instead of drifting). Everything is back at 129 and the `tempo_key.py` change was reverted. The real echo problem was the always-on delay: ducking let fragments of words from a beat earlier surface at random points, so echoes now repeat only the word just said. **Lesson:** check a tempo by matching the drums against themselves bars apart, and trust the owner's ears over a fit.
- **Why:** owner requests in the brief's Creative effects table (phone-call outro, lead vocal delay, song fade-out).
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.5 dBTP (MP3), loudness range 7.6 LU, limiter loss 0.7 LU.
- **Effects log and review report:** `effects/v4.json`, `reports/v4.md` (counts in the report). Mid and upper-mid up about 3–4 dB vs the original because the phone outro is all midrange, intended. Outro line choice: found by vocal shape, owner to confirm the words.
- **Creative effects acknowledged:** phone-call outro (outro vocal, bars 73–86 plus ring-out, no plugin named); lead vocal delay (lead, line endings in both verses, off at the end of verse 2); song fade-out (whole mix, bars 82–86). All three built.
- **Delay times used:** 1/4 = 465.12 ms, 1/2 = 930.23 ms, 1/8 dotted = 348.84 ms, pre-delay 1/64 = 29.07 ms, decays dotted half 1.395 s, 1 bar 1.860 s, 1.5 bars 2.791 s, all at 129 BPM.
- **Listening check:** owner on the first v4 draft: "It is literally ALMOST perfect", lead echoes not perfectly timed; on the 128.71 rebuild: "the outro is off beat now". Both addressed here.
- **Next:** owner confirms the echoes and outro timing, and that the outro lines are the right words.

### 2026-11-08 — v3-master

- **Files:** `Pushing_the_Interstate_master_v3_24bit.wav`, `Pushing_the_Interstate_master_v3.mp3`, `v2_vs_v3_hook.mp3` (loudness-matched A/B, 1:59–2:14). Audio delivered in chat, not committed.
- **What changed:** adlib de-esser threshold −25 → −29.5 dBFS (active 2.4% → 11.4%, avg 1.8 dB). Everything else as v2.
- **Why:** the v2 review report flagged the adlib de-esser as barely working. Measured: the adlibs' loudest sibilance sits at −4.6 dB band-to-full, as hot as the lead's (−5.7 dB), so they get matching treatment.
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.4 dBTP (MP3), loudness range 7.1 LU, limiter loss 0.7 LU.
- **Effects log and review report:** `effects/v3.json`, `reports/v3.md`: ⚠️ close, 46 passed, 1 to check, 0 failed. The one ⚠️ is the previous engineer's printed vocal FX stem, whose delay timing can't be measured against 129 BPM from a printed file; it stays until the owner confirms by ear or the original session is available. Brief still has 6 missing facts.
- **Listening check:** pending owner. Owner on v2: "Absolute fucking masterpiece."
- **Feedback:** pending on v2 vs v3.
- **Creative effects acknowledged:** none requested for this song yet.
- **Delay times used:** 1/8 dotted = 348.84 ms, pre-delay 1/64 = 29.07 ms, reverb decay ≈ dotted half (1.395 s), all at 129 BPM.
- **Next:** owner picks v2 or v3; fill in the brief's missing facts.

### 2026-11-08 — v2-master

- **Files:** `Pushing_the_Interstate_master_v2_24bit.wav`, `Pushing_the_Interstate_master_v2.mp3`, `v1_vs_v2_hook.mp3`.
- **What changed:**
  - *Beat:* new 808 peak control: Linkwitz-Riley crossover at 120 Hz, low band compressed 5:1 at −20 dB (attack 3 ms, release 90 ms, +2 dB makeup). 808 peaks down about 4 dB; overall tone within 0.2 dB of v1.
  - *Master:* target −10.5 → −11.5 LUFS.
  - *Vocals:* lead and adlibs re-rendered with the fixed de-esser (first-order subtraction, no +1.2 dB boost next to the S band).
- **Why:** owner heard the song "going quiet" at points. Measured: in v1 the limiter pulled the whole mix down 5–7 dB on 808 hits (54 seconds of the song had dips over 4.5 dB). Tested four fixes; a mix-bus glue compressor and a soft clipper each added their own pumping, so only the 808 control was kept. Owner also asked whether the gain should come down: −11.5 LUFS removes the remaining big dips, and streaming normalization (around −14 LUFS) means it won't play quieter there.
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.4 dBTP (MP3), limiter loss 2.3 → 0.7 LU. Dips over 4.5 dB: 54 s → 0 s; worst dip −6.9 → −4.4 dB.
- **Effects log and review report:** `effects/v2.json`, `reports/v2.md`: ⚠️ close, 2 to check (adlib de-esser barely active, fixed in v3; printed vocal FX stem timing).
- **Listening check:** owner, on phone: "Absolute fucking masterpiece."
- **Next:** v3 (adlib de-esser).

### 2026-11-08 — v1-master

- **Files:** `Song_master_v1_24bit.wav` (24-bit / 44.1 kHz) and `Song_master_v1.mp3` (320 kbps), plus `Before_After_hook.mp3` (loudness-matched A/B of the hook, 1:59–2:14). Audio was delivered in chat, not committed here.
- **What changed:**
  - *Lead vocal* (`02_Lead_Vocals`): gain-staged to −18 dBFS active RMS (+8.8 dB); high-pass 90 Hz, 18 dB/oct (below the lowest sung note, A2 110 Hz); static cuts −2.6 dB at 229 Hz (Q 6) and −1.5 dB broad at 320 Hz; dynamic EQ at 3529 Hz (threshold −32 dBFS, active 3% of the time) and 4697 Hz (threshold −33 dBFS, active 14%); presence +2 dB at 3 kHz (Q 0.9) and air shelf +1.5 dB at 10 kHz; de-esser 5.5–8.5 kHz, threshold −25 dBFS (active 16%, avg 1.7 dB); two-stage compression, smooth threshold −22 dB (avg 4.9 dB reduction); parallel saturation drive 6 dB, even 0.15, mix 0.25.
  - *Adlibs* (`03_Adlibs`): gain-staged +10.4 dB; high-pass 180 Hz; −2 dB at 320 Hz, +1.5 dB at 3.2 kHz; de-esser threshold −25 dBFS (barely active, 2%); two-stage compression, smooth threshold −22 dB (avg 3.8 dB).
  - *New sends*: adlib delay 1/8 dotted (348.84 ms), feedback 0.35, ping-pong, 300–6000 Hz loop filter, ducked −10 dB by the processed lead. Lead plate reverb RT60 1.4 s, pre-delay 29 ms (1/64), ducked 4 dB by the lead, return −14 dB.
  - *Beat* (`01_Beat`): −1 dB at 2.5 kHz (Q 1.5) to make room for the vocal, −1 dB at 250 Hz.
  - *Vocal FX stem* (`04_...`): kept as printed, at 0 dB.
  - *Balance*: lead set to its original loudness +1 dB (gain −6.6 dB after processing); adlibs and adlib delay at original loudness (−10.0 dB); plate at the lead's gain.
  - *Mix bus*: side channel high-passed at 90 Hz (24 dB/oct) so sub-bass is mono; mid-only high shelf +2 dB at 9.5 kHz.
- **Why:** the brief's measured problems were a boxy, slightly harsh lead and a dark, bass-heavy mix. Cuts target only those spots; the existing vocal FX stem was kept to protect the previous engineer's vibe. No genre, references or mood were given yet, so balance followed the original stems.
- **Loudness, if this is a master:** −10.5 LUFS integrated, true peak −0.7 dBTP (WAV) / −0.3 dBTP (MP3), loudness range 8.0 LU. Toolkit default target (−10.5 LUFS / −0.5 dBTP), since the brief names none. Limiter took about 2.3 LU off the peaks. No platform reference compared yet.
- **Compared with the original stems summed** (loudness-matched): relatively more low-mid (+2.1), mid (+2.6), upper-mid (+2.8), high (+1.8) and air (+3.2 dB); sub and bass within 0.6 dB; stereo correlation 0.84 → 0.91.
- **Listening check:** the tools measure, they do not listen. Not yet checked by the owner.
  - Earbuds: pending
  - Car: pending
  - Phone speaker: pending
  - Studio monitors: pending
- **Feedback:** pending, from the owner after listening to `Before_After_hook.mp3`.
- **Creative effects acknowledged:** none requested for this song yet.
- **Delay times used:** 1/8 dotted = 348.84 ms, 1/64 pre-delay = 29.07 ms, both from the 129 BPM table in the brief.
- **Next:** owner listens to the A/B and full master; fill in genre, mood, references and where it will be heard in the brief; ask for WAV stems if available; check whether the song's ending is meant to cut off.

## Final sign-off

Use this only for the master you believe is finished. Leave every box unchecked until that item is actually true. The song is still in progress until the owner signs.

- [x] All creative effects from the brief are in place, on the right track or mix bus, in the right spot, and the right length (phone-call outro, lead vocal delay, song fade-out; confirmed in `reports/v4.md`)
- [x] Echo, delay, pre-delay, and decay times match this song's BPM, and the math was checked (129 BPM; outro placement confirmed by matching the drums against themselves)
- [ ] Earbuds check passed (not reported separately)
- [ ] Phone speaker check passed (not reported separately)
- [ ] Car check passed (not reported separately)
- [ ] Studio monitors check passed (owner has no monitors yet)
- [x] Loudness and true peak meet this song's targets
  - Integrated LUFS: −11.6
  - True peak: −0.7 dBTP (WAV), −0.5 dBTP (MP3)
  - Target used (platform and number): −11.5 LUFS / −0.5 dBTP, chosen to remove limiter pumping; streaming platforms normalize to around −14 LUFS. No platform named in the brief.
- [ ] Compared against the reference tracks in the brief (no reference tracks given)
- [x] Owner sign-off on the final master

The owner approved the master as finished. The unchecked boxes are recorded as not done rather than assumed; they don't block the owner's sign-off.

**Master version:** v4 (`Pushing_the_Interstate_master_v4_24bit.wav`, 129 BPM build)

> v5, v6 and v7 (verse echo fixes, pitched outro delay, stutters) were made after this sign-off at the owner's request; v7 is awaiting the owner's approval. Until then, v4 is the approved master.
**Date:** 2026-11-08
**Owner:** Chex
**Owner's words:** "My boy….. it's beautiful" — then, asked whether that counts as final approval: "Yessss sirrrrr"

# Mix notes

**Song:** Driftin' Away

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

### 2026-11-09 — v4-master (every repeat matches its main line)

- **Files:** `Driftin_Away_master_v4_24bit.wav`, `Driftin_Away_master_v4.mp3`, `Driftin_Away_v3_vs_v4_1m16.mp3` (v3 then v4, same loudness, 1:16.5–1:29.5). Audio delivered in chat, not committed.
- **Owner on v3 (headphones):** "At 1:18 the repeat is louder than the main. 'Always up late at night I can never sleep' (LOUDER REPEAT 'I can never sleep') that repeat isn't supposed to be louder." Then: "make the adlib track louder but [the] specific part needs to be lower, the repeat, to match." Asked which answers are repeats: "All 16 are repeats."
- **What went wrong in v3:** the adlib responses were raised as one track against the beat, and no check compared each repeat with the line it repeats. Measured on v3: all 16 repeats were 2–4 dB louder than their main lines. An attempt to tell repeats from other adlibs by envelope shape was not reliable (it even missed the 1:20 one), so the owner's answer decided it.
- **What changed (`build_mix.py v4`, `match_repeats`):** each repeat is set to the loudness of the main line it answers (the background vocal over the 2 bars that end where the repeat ends), held through the repeat's own echoes: −0.3 to −3.0 dB. Measured on the parts exactly as they enter the mix: 0.0 dB on all 16, none louder. Everything else is v3: the verse adlibs stay 2 dB under the lead, the background vocal at the lead's level, the swells, build-ups and drops unchanged.
- **New check for every future version:** `check_repeats.py` reads the vocal parts as they enter the mix (`stem_<version>_responses.wav`, `stem_<version>_background.wav`) and fails any repeat louder than its main line.
- **Result:** −11.5 LUFS, −0.7 dBTP (WAV) / −0.6 dBTP (MP3), limiter 0.3 LU, worst limiter dip −2.9 dB (v3: −3.1). Verse and second half within 0.7 dB. Timing unchanged (79 echo repeats on the grid, max 0.01 ms; drops on their transients).
- **Effects log and review report:** `effects/v4.json`, `reports/v4.md`: ⚠️ close, 72 passed, 2 to check (upper-mid and air about 3 dB over the raw stems summed, because the vocals are much louder over the beat than in the raw stems, as asked), 0 failed.
- **Listening check:** pending owner, headphones. Spot: 1:18–1:22 ("I can never sleep" and its repeat), then every 2 bars to 2:18.

### 2026-11-09 — v3-master (adlibs and background up, louder swells, drops with a build-up)

- **Files:** `Driftin_Away_master_v3_24bit.wav`, `Driftin_Away_master_v3.mp3`, `Driftin_Away_v2_vs_v3_0m24.mp3` (the first drop and verse start) and `Driftin_Away_v2_vs_v3_1m16.mp3` (into the second half): v2 then v3, same loudness, 14 s each. Audio delivered in chat, not committed.
- **Owner on v2 (headphones):** "Around 1:18 and onward ... the volumes are still unevenly matched ... the adlib vocals ... are still too quiet. The backgrounds (yeah)'s and others you can barely hear and the reverse reverbs and silent to built up beat drops are still quiet."
- **What changed (built with `FX_VERSION=v3 ADLIB_SRC=a_8.wav build_fx.py`, then `build_mix.py v3`):**
  - Background vocal 3 dB up: now about as loud as the verse lead (+0.7 dB). Its darker top and longer hall keep it sounding behind; the brief's "behind" now means the sound, not the level.
  - Adlibs up: the verse double to 2 dB under the lead (v2: 4), the responses to 4 dB over the beat (v2: +1). Their echoes follow.
  - Peak catchers (new, `peak_catch` in `build_mix.py`): at the new level the responses peaked 18 dB over their loudness and pulled the master limiter down 5 dB at 1:23, 1:30, 1:51, 2:01 and 2:04. A 5 ms lookahead limiter on the responses (ceiling = loudness + 9 dB; average 0.9 dB, max 8.8 dB) and on the background vocal (loudness + 11 dB; average 0.2 dB) fixed it: worst master dip now −3.1 dB (v3 before the fix: −5.0).
  - Reverse swells louder: peak level with the word (v1/v2: 6 dB under), plus 4 dB on the first word (it sits under the full beat) and 2 dB on the swell into bar 41. Measured over the music around them: +2.5, +1.6 and +11.8 dB.
  - Drops rebuilt: before bars 17 and 57 the beat now stops for two beats (v1/v2: an eighth note); beat 3 is silent, beat 4 is a build-up swell made from the drop's own first hit (above 250 Hz, reversed through a 2.4 s hall), and the drop lands on its own transient. The beat's own stops (into bars 25, 41, 65) get the same build-up on their last beat. Each build-up ends 5–7 dB under the drop's first beat.
- **Result:** the verse and the second half now match within 0.3 dB (v1: 1.5 dB apart; v2: 0.9). Master −11.6 LUFS, −0.7 dBTP (WAV) / −0.6 dBTP (MP3), limiter 0.3 LU.
- **Timing checks (`tools/verify_v1.py` on v3):** unchanged: 79 echo repeats on the grid (max 0.01 ms), swells on the words' first sounds, drops on their transients (+1.8 and −0.6 ms from the grid).
- **Effects log and review report:** `effects/v3.json`, `reports/v3.md`: ⚠️ close, 70 passed, 3 to check, 0 failed. The three are the mid, upper-mid and air bands about 3.3 dB up against the raw stems summed: the vocals are now much louder over the beat than in the raw stems, which is what the owner asked for.
- **Listening check:** pending owner, headphones. Spots: 0:24–0:27 (silence, build-up, drop, swell into the first word), 1:00–1:05, 1:16–1:30 (swell into the background vocal, the louder background and adlibs), 1:39–1:43 (build-up into the bar 65 drop).

### 2026-11-09 — v2-master (lead down, less lead reverb, louder and even adlibs)

- **Files:** `Driftin_Away_master_v2_24bit.wav`, `Driftin_Away_master_v2.mp3`, `Driftin_Away_v1_vs_v2_0m38.mp3` and `Driftin_Away_v1_vs_v2_1m51.mp3` (v1 then v2, same loudness, 12 s each). Audio delivered in chat, not committed.
- **Owner on v1 (headphones):** "It's nearly perfect. The lead vocals are a bit too loud and have slightly too much reverb and other parts are louder than the others. Also the ADLIBS need to be louder so you can hear them much better."
- **Measured on v1 first:** the verse played 1.5 dB louder than the second half's full-beat part (the lead sat on top there), and the 16 adlib responses varied by 5.0 dB from one to the next. The lead itself was even (one 2-bar outlier is the pause at bar 39), and the background vocal varied only 1.8 dB.
- **What changed (only these; every effect and its timing is as v1):**
  - Lead 1.5 dB lower: now 0.5 dB under the beat in the verse (v1: 1 dB over).
  - Lead plate 2.5 dB lower (return −15 dB, same 1-bar length): the reverb now sits 17.4 dB under the lead (v1: 14.9).
  - Verse adlibs (the double under the lead) 3.5 dB louder: 4 dB under the lead (v1: 9).
  - Adlib responses levelled to one another (`tools/level_adlibs.py`: each moved to the median, −2.5 to +2.4 dB, changes made in the gaps), then raised to 1 dB over the beat (v1: 2 dB under). Their echoes follow them, so the echoes are louder by the same amount.
  - Background vocal 1 dB up (2 dB under the beat; still about 3 dB under the full beat), so the second half sits closer to the verse.
- **Result:** verse vs second half full beat: +1.5 dB (v1) → +0.9 dB (v2). The rest of the difference is the lead on top in the verse versus the background vocal behind in the second half, as the brief asks.
- **Loudness:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.6 dBTP (MP3), limiter 0.4 LU, no dips over 4.5 dB.
- **Timing checks (`tools/verify_v1.py` on v2):** unchanged from v1: all 79 echo repeats on the beat grid (max 0.01 ms), reverse swells on the words' first sounds, air gaps ending on the drop transients.
- **Effects log and review report:** `effects/v2.json`, `reports/v2.md`: ⚠️ close, 70 passed, 1 to check (the same air-band note as v1; v2 vs v1 air −0.3 dB), 0 failed.
- **Listening check:** pending owner, headphones. Spots: 0:38–0:50 (lead lower, less reverb, adlibs up), 1:51–2:03 (adlib responses louder and even).
- **Next:** if the verse should match the second half exactly, a 0.5–1 dB whole-mix ride on bars 17–48 does it; only if the owner hears it.

### 2026-11-09 — v1-master (first full mix and master, every requested effect)

- **Files:** `Driftin_Away_master_v1_24bit.wav`, `Driftin_Away_master_v1.mp3`, `Driftin_Away_v1_before_after_0m38.mp3` (raw stems summed vs v1, loudness-matched, 0:38–0:53). Audio delivered in chat, not committed.
- **What changed (from the raw stems):**
  - *Vocals:* gain staged to −18 dBFS; high-pass 90 Hz (lead), 130 Hz (background), 150 Hz (adlibs); a dynamic EQ around 2.5–3 kHz that only acts on the loud, harsh moments (12–13% of the time); de-essing on S sounds only (18–25%); two-stage compression (about 6 dB). No static notches: the peaks at 466, 624, 934, 1246 and 2495 Hz are harmonics of the tuned Eb3, so cutting them would cut the melody.
  - *Balance (measured, K-weighted):* lead 1.0 dB over the beat in the verse (0.7–1.3 dB in every part); verse adlibs 9 dB under the lead; background vocal 3 dB under the beat over bars 49–86 (about 4 dB under the full beat), with a softer top and more hall, as asked; adlib responses 2 dB under the beat.
  - *Dreamy echoes:* the last word of 8 lead lines and of all 16 adlib responses repeats on the main beats: first repeat 8–9 dB under the word, then 5 dB quieter and darker each time, left and right alternating, light fast ducking (−3 dB, 5/120 ms), and a plate on the repeats. 3 repeats as a rule; 4 on the last response into the outro; 2 where a vocal comes straight back (into the bar 39 stop, and the end of the verse, where the reverse swell takes over).
  - *Reverb, a little dreamier:* lead plate 1 bar (1.6 s), background hall 1.5 bars (2.4 s), pre-delay 1/64 (25 ms), ducked under the words.
  - *Reverse reverb:* three swells, each starting on a beat and ending on the word's first sound: into the first word (bar 17 beat 2 to 0:26.833), into the drop at bar 41 (bar 40 beat 4 to 1:04.042), into the background vocal (bar 49 beat 3 to 1:18.014).
  - *Beat stop and drops:* the beat already has three 2-bar stops (bars 23–24, 39–40, 63–64), so those stay as the producer made them. Added: an eighth-note air gap before the drops at bar 17 (0:25.44) and bar 57 (1:29.44); the beat comes back on the drop's own transient, which sits 1.8 ms and 0.6 ms from the grid.
  - *Phone-call outro with stutters:* the verse's first two lines (A 0:26.8, B 0:30.1) play twice in the outro through a telephone sound (420 Hz–3.2 kHz, 8 kHz, compressed, with line hiss), moved by whole bars so each keeps its pickup on beat 4: A at bar 91, B at bar 93, A at bar 97, B at bar 99. Before each line, the first 75 ms of its first syllable repeats 4 times on 16th notes. The end of each A-B pair echoes 4 times.
  - *Fade-out:* bars 99–104 (2:36.8–2:46.4), raised cosine to silence on the beat's last bar.
  - *Bus and master:* mono below 90 Hz, +1.5 dB mid shelf at 9.5 kHz (kept modest: the beat is band-limited), limiter to −11.5 LUFS / −0.5 dBTP, the same as the approved Pushing the Interstate v4.
- **Why:** the owner's answers on 2026-11-09 (brief, Creative effects requests). "Only if you can time them perfectly" is met by measuring the grid from the drums and checking every placement afterwards.
- **Loudness, if this is a master:** −11.6 LUFS integrated, −0.7 dBTP (WAV) / −0.6 dBTP (MP3), loudness range 12.9 LU, limiter 0.5 LU, no limiter dips over 4.5 dB.
- **Timing checks (measured on the rendered files, `tools/verify_v1.py`):** all 79 echo repeats start on the beat grid (largest error 0.01 ms; found by correlating each word with its echo). In the full-beat parts they sit about 1 ms from a real drum hit; in the breakdown and stop bars there is no drum hit on every beat, so the nearest hit can be 10–50 ms away (or none at all in the stops). Reverse swells end within 1 ms of each word's first sound. The air gap before bar 17 is silent (−83 dBFS); before bar 57 the background vocal keeps going over it, as intended.
- **Tone vs the raw stems summed:** low-mid to upper-mid up about 2 dB because the vocals now sit higher over the beat and the reverbs, echoes and phone outro add midrange; the air band +3.6 dB is the vocals plus the 1.5 dB shelf in a band that holds a very small share of the energy (−49 dB). The report flags it to confirm by ear.
- **Listening check:** pending owner, headphones.
- **Creative effects acknowledged:** dreamy echoes (lead line ends and adlib responses, on the main beats); a little dreamier reverb (lead, background, adlibs, echoes); background vocal behind (bars 49–86); phone-call effect (outro vocal, bars 91–101); stutter effect (before each phone line); reverse reverb (bars 17, 40–41, 49); beat stop and drops (eighth-note air gaps before bars 17 and 57); fade-out ending (whole mix, bars 99–104). No plugin was named for any of them.
- **Effects log and review report:** `effects/v1.json`, `reports/v1.md`: ⚠️ close, 62 passed, 1 to check (air band, explained above), 0 failed.
- **Delay times used:** 1/4 = 400.00 ms for every echo, 1/16 = 100.00 ms for the stutters, 1/64 = 25.00 ms pre-delay, decays 1.6 s (1 bar) and 2.4 s (1.5 bars), all at 150 BPM, matching the brief's table.
- **Lesson carried over from Pushing the Interstate:** echoes start on the main beats of a grid measured from the drums (not anchored at 0:00, which here would be 38 ms early), only the last word repeats, ducking is light and fast, and no echo starts where the next line begins.
- **Next:** the owner listens on headphones. Spots to check: 0:25.4 (air gap and drop), 0:26–0:27 (reverse swell into the first word), 0:29–0:31 (first echo), 1:00.4–1:04.1 (echo into the beat stop, swell into the drop), 1:16.7–1:18.2 (last lead echo, swell into the background vocal), 1:20–1:30 (adlib response echoes), 2:24–2:46 (phone outro, stutters, fade). The outro lines were picked by position; the owner should confirm the words.

## Final sign-off

- [ ] Owner approved the final master

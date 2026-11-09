# Mix notes

**Song:** Driftin' Away

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

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

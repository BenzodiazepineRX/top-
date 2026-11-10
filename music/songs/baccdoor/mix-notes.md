# Mix notes

**Song:** Baccdoor

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

### 2026-11-09 — v4-master (the lead's edge down, the words clearer)

- **Files:** `Baccdoor_master_v4_24bit.wav`, `Baccdoor_master_v4.mp3`, `Baccdoor_v3_vs_v4_0m38.mp3` and `Baccdoor_v3_vs_v4_1m52.mp3` (v3 then v4, same loudness). Audio delivered in chat, not committed.
- **Owner on v3:** "Nearly PERFECT. just gotta get the harshness in the lead down and more clear a little more then we're done."
- **Measured first (v3, leads against the beat, per 1/3 octave while singing):** at 2.5 kHz the leads sat 14.6 dB over the beat, against 8–10 dB in the other bands. That is the band the ear is most sensitive to, so it reads as harsh. At 4–6 kHz, where consonants make words crisp, the leads sat 3–7 dB under the beat. Against the Driftin' Away lead, v3's leads were 4–8 dB darker at 4–8 kHz.
- **What changed (everything else is v3):**
  - Leads: −3.5 dB at 2.5 kHz (Q 1.4) and +2.5 dB at 5.5 kHz (Q 0.9), after the compression.
  - Beat: its 3.2–6.5 kHz ducks up to 5 dB on the leads' consonants (keyed by the leads' own 3.2–6.5 kHz band over its 78th percentile, 5/120 ms), 28% of the time; the beat is as delivered the rest of the time. A first version keyed by the leads' overall level acted 68% of the time, because the two leads overlap almost everywhere, so it behaved like a static cut (the report flagged it); it was rebuilt keyed by the consonants before delivery to the repo. The owner first received a v4 rendered with that first version; the files were replaced in chat.
- **Result:** the leads' 2–3.5 kHz edge against their body: −2.4 dB (median), −2.6 dB on the loud moments. On consonant moments, the leads over the beat: 3.2–4.5 kHz +9.6 → +12.5 dB, 4.5–6.5 kHz +1.3 → +4.0 dB. Grit 0.023 (v3 0.013, v2 0.048, Driftin' Away lead 0.032). The master: 2–5 kHz against the body −13.5 dB (v3 −11.5), grit 0.056 (v3 0.044, Driftin' Away v6 0.059). −12.1 LUFS, −1.2 dBTP WAV / −1.1 dBTP MP3. All `verify_bacc.py v4` checks pass.
- **Effects log and review report:** `effects/v4.json`, `reports/v4.md`: ⚠️ close, 75 passed, 5 to check, 0 failed. Three are the low-mid, mid and upper-mid bands against the raw stems summed (the vocals lifted over the beat, as in every version; low-mid +3.0 dB crosses the warning line by 0.1 dB). Two are the background layers' de-essers, kept on purpose (see v3).
- **Listening check:** pending owner. If it went too far either way, the two lead EQ moves are the knobs: "softer" = more cut at 2.5 kHz, "crisper" = more at 5.5 kHz.

### 2026-11-09 — v3-master (mono, tone-matched leads; echoes on every line; telephone background vocals; fade-out)

- **Files:** `Baccdoor_master_v3_24bit.wav`, `Baccdoor_master_v3.mp3`, `Baccdoor_v2_vs_v3_0m30.mp3` (v2 then v3, same loudness, 0:30–0:50), `Baccdoor_leads_alone_raw_vs_v3_0m38.mp3` (the two lead stems exactly as exported, then the v3 leads, same loudness, 0:38–0:52), `Baccdoor_v3_ending_2m48.mp3` (the fade). Audio delivered in chat, not committed.
- **Owner on v2:** "lead vocals still very harsh, amplifying, and scratchy. Not clear." And: "I wanna fade the song out. Fill in quiet gaps with echos/delay perfectly timed making the song pop. Add background vocals [to] the start of the song's lead vocals as well that sit behind with nice dreamy reverb telephone effect."
- **Measured first:**
  - The chain is not adding the grain: the harmonics-to-noise ratio (`hnr.py`) is the same raw and after every step (Main1 14.8 dB, Main2 14.0 dB).
  - The stereo part of the lead stems is the grittiest: harmonics-to-noise 10.2/9.4 dB against 14.8/14.0 in the middle, more 2–5 kHz and more grit, and left/right only 45–48% alike in 1–4 kHz with no delay between them: it behaves like a stereo effect baked into the export.
  - Against the owner's Driftin' Away lead (same measure, sung frames), these takes carry 8–11 dB more 3.5–5 kHz, 12–19 dB more 5–14 kHz, 6 dB more 100–200 Hz, and 2–4 dB less of the 1.6–3.5 kHz range that carries the words. v2 cut the top above 5.5 kHz but left 3.5–5 kHz as it was, so it stayed harsh and lost air without gaining clarity.
  - The raw lead stems roll off steeply above 15–16 kHz.
- **What changed (everything else is v2):**
  - Leads mono: the middle only (v1/v2: side −6 dB).
  - Leads tone-matched 85% of the way to the Driftin' Away lead as mixed (`match_eq.py`, linear phase): about −3 dB at 125 Hz, +1.5 to +2 dB at 500 Hz, −4 dB at 1 kHz, +0.3 to +1 dB at 2 kHz, −4 to −6 dB at 4 kHz, −10 dB at 8 kHz and above. Then a dynamic EQ at 4 kHz (24–25% of the time, 1.5 dB average), the de-esser at 5–11 kHz (20–22%), and gentler compression (2.9–3.0 dB average, v2 4.8; phrase-to-phrase loudness still within 2.2 dB).
  - Leads 0.5 dB under the beat (v2: 0.3 over), the level the owner approved on Driftin' Away.
  - Background layers: tone match with cuts only (less 250 Hz and 8 kHz+, no presence lift), so they stay behind.
  - Echo throws on the last sung word of every lead line, both leads (3 echoes: −5, −9, −13 dB), plus the drops and the last line as before: 32 throws, 108 echoes (v2: 20 and 72). The two leads overlap from 0:31.7 to 2:51.4, so the vocals have no silent gaps; every line ending now answers with an echo.
  - Telephone background vocals: from the first lead line (0:31.7) through bar 25, the background vocals go through a telephone (420 Hz–3.2 kHz, +4 dB at 1.8 kHz, an 8 kHz line, 6:1 compression, no drive) into a dreamy hall (2.88 s = 1.5 bars, pre-delay 60 ms), 8 dB under the leads, then cross back to the plain background vocals over bar 26 (0:49.5–0:51.4). The background take is used, not a copy of the leads, so nothing stacks on the leads in the same band and sounds honky.
  - Fade-out from the downbeat of bar 90 (2:52.3, right after the last line) to silence on the downbeat of bar 97 (3:05.8); the last line's 8 half-note echoes ride down with it. The song now ends at 3:05.7 (was 3:19.7).
- **Result:** the leads as mixed: grit 0.013 (v2 0.048, Driftin' Away lead 0.032), fizz −34.4 dB (v2 −29.9), 3.5–5 kHz −34.6 dB (v2 −32.0), 1.6–3.5 kHz up 1.6–3.1 dB, 100–200 Hz down 2.6 dB. The master's grit 0.044 (v2 0.101, Driftin' Away v6 0.059). −12.1 LUFS, −1.2 dBTP (WAV and MP3), limiter 0.6 LU. All `verify_bacc.py v3` checks pass: 108 echoes within 0.04 ms of a beat; background −4.4 to −8.9 dB under the leads, its background −3.8 to −6.3 dB under it; the telephone layer −7.4 to −8.8 dB under the leads (target −8); no gaps; mono −0.2 dB, vocal band −0.2 dB.
- **Tried and dropped:** a grain reducer (`degrain.py`) that lowers the noise between the harmonics of each sung note. It raised the harmonics-to-noise ratio by only 0.3–0.4 dB: the main note is A2 (110 Hz), and at that pitch the harmonics sit too close together to separate from the grain cleanly. Not worth the risk of a phasey sound.
- **Effects log and review report:** `effects/v3.json`, `reports/v3.md`: ⚠️ close, 73 passed, 4 to check, 0 failed. Two are the mid and upper-mid bands against the raw stems summed (the vocals were recorded 8 dB under the beat; lifting them moves these bands). Two are the background layers' de-essers at 26–28% of the time: kept, because those layers sit 5–9 dB under the leads and should sound soft. Plus the brief's unknown facts (artist, reference track, streaming service, deadline).
- **Open question for the owner:** if the first half of `Baccdoor_leads_alone_raw_vs_v3_0m38.mp3` (his files exactly as exported) also sounds scratchy to him, the grain is in the recording. A fresh export of the vocals with only the autotune on (no app reverb, stereo or amp effect) would let the next version get cleaner still.
- **Listening check:** pending owner. Spots: 0:31–0:52 (the telephone background vocals and the first echoes), 1:24–1:47 (into drop 1), 2:45–3:06 (the last line, its echoes and the fade).

### 2026-11-09 — v2-master (the harshness taken out)

- **Files:** `Baccdoor_master_v2_24bit.wav`, `Baccdoor_master_v2.mp3`, `Baccdoor_v1_vs_v2_0m38.mp3` (v1 then v2, same loudness, 0:38–0:52). Audio delivered in chat, not committed.
- **Owner on v1:** "It's very scratchy, it sounds too ampy ... very harsh vocals."
- **Measured first (`harsh.py`):** against the Driftin' Away lead (never called harsh), these recordings carry 15–18 dB more fizz (5–12 kHz against the 200–1500 Hz body) and about 3× the grit (spectral flatness 3–8 kHz, noise-like sound). No clipping (no flat tops) and a 43 dB noise floor, so it is the sung sound itself (consonants and the autotune's texture), not an overloaded mic or hiss. The retune added nothing. v1 made it worse: +2.3 dB at 2–5 kHz from the presence boost, the saturation and the compression, plus a +1.5 dB treble shelf on the mix bus.
- **What changed (everything else is v1):**
  - Leads: no presence boost, no saturation; −7 dB shelf above 5.5 kHz and a 12 kHz low-pass; the dynamic EQ at 3.5 kHz acts on the loud harsh moments (19–20% of the time); the de-esser covers 5–11 kHz (S sounds and fizz, 23–25% of the time).
  - Background layers: −6 dB shelf above 5.5 kHz, 11 kHz low-pass, the same dynamic EQ and de-esser.
  - Mix bus: no treble shelf. (`ms-bus` adds a +2 dB shelf when `--mid-shelf` is left out; the build now passes `9500:0` explicitly. The first v2 render caught this, and the bus and master were redone.)
  - Reverb sends low-passed at 8 kHz, so the reverb does not spread the fizz.
- **Result:** the leads as mixed: fizz −29.9 dB (v1 −19.5), 2–5 kHz −13.0 dB (v1 −10.6), grit 0.048 (v1 0.065). The master: 5–12 kHz −24.0 dB (v1 −19.1, Driftin' Away v6 −23.2), air share −45.6 dB (v1 −34.3). −12.1 LUFS, −1.2 dBTP, worst limiter dip −3.9 dB. All `verify_bacc.py v2` checks pass (72 echoes within 0.08 ms of a beat, layer order, no gaps, mono −0.3 dB).
- **Effects log and review report:** `effects/v2.json`, `reports/v2.md`: ⚠️ close, 64 passed, 5 to check, 0 failed. Four are the tone against the raw stems (vocals lifted over the beat; the top now lower than the raw stems, on purpose). One is the background-of-background's de-esser at 27% of the time: kept, because that layer sits 9 dB under the leads and should sound soft.
- **Listening check:** pending owner. If the words now sound too dull, the next step is +1 dB at 3 kHz on the leads, not more top end.

### 2026-11-09 — v1-master (retuned to the beat, layer order, echo throws, reverb that opens up, streaming master)

- **Files:** `Baccdoor_master_v1_24bit.wav`, `Baccdoor_master_v1.mp3`, `Baccdoor_v1_before_after_1m24.mp3` (the raw stems summed, then v1, same loudness, 1:24–1:42: the end of A into drop 1). Audio delivered in chat, not committed.
- **Owner's request:** "perfectly mix this song ... a bit of auto tune ... if u can make it better then adjust, if not then let me know ... good delays, good reverb, good echo throws perfectly timed, perfect progressional sound ... ready for quality streaming on phone, earphones and stereos."
- **Autotune:** measured, not guessed (`pitch_layers.py`). Held notes sit 8 cents (median) from the key's notes, 79–92% within 15 cents, 1% more than 30 cents off: the autotune works. The one real fault: it is aimed at A4 = 440 and the beat at 438.3 Hz, so every vocal sat about 8 cents sharp of the piano. Each stem was retuned by its own measured offset (−7.2 to −8.1 cents, rubberband, formants kept) and re-aligned to the sample; after: every stem's tuning centre within 1 cent of the beat's (`check_retune.py`). The held C# notes in the background vocal (3 s in total, 3 of 13 over a beat C) were left as sung. No tool for note-by-note correction is installed here (no Melodyne-style pitch editor), so notes were not moved; none needed it.
- **Lesson on alignment:** the first re-alignment after rubberband used waveform correlation and reported −70 to +42 ms, which was wrong: on autotuned notes the waveform repeats every pitch cycle. The amplitude envelope is pitch-free and showed the real delay, 0.7–1.8 ms. Always align pitch-shifted vocals by envelope.
- **What changed (from the raw stems):**
  - Chains: gain staging to −18 dBFS, high-pass (leads 90 Hz, background 150, its background 180), a dynamic EQ at 3 kHz that acts 7–8% of the time, presence +1.5 dB on the leads, de-essing 10–12% of the time, two-stage compression (4.7–5.5 dB), light saturation on the leads.
  - Leads narrower (side −6 dB): the lead stems were wide with 14% of moments out of phase; phones play mono. Master in mono: −0.4 dB, vocal band −0.5 dB.
  - Lead level: the two takes trade lines and overlap, so their sum sits 0.3 dB over the beat in every full section (A, B, C), with 1-beat ramps.
  - Layer order (the owner's rule from Driftin' Away): background vocals 6 dB under the leads in A, 5 in the drops and B, 4.5 in C; the background-of-background 4 dB under the background (9 under the leads where the background is silent). Ridden every 2 bars, measured only where both layers sing, gains clamped to their median ±4 dB. Checked after: −4.5 to −6.0 dB and −3.7 to −19 dB; never above. (The first ride measured whole 2-bar windows and boosted near-silent parts of the background-of-background by 13 dB; fixed.)
  - Echo throws on the grid measured from the drums (125 BPM, eighth grid 17.4 ms into the file): the last sung word of every lead 1 line (3 echoes), every lead line in the two drops (4 echoes), and the last line (8 half-note echoes fading out). 20 throws, 72 echoes, all within 0.04 ms of a main beat (`verify_bacc.py`).
  - Reverb: plate 1.44 s (dotted half) on the leads, −16 dB in A, −15 in B and C, −12 in the drops, so the drops open up; hall 1.92 s (1 bar) on the background layers at −9 dB; plate on the echoes. Pre-delay 1/64 = 30 ms.
  - Progression: a whole-mix lift of +0.3 dB in B and +0.6 dB in C. Measured on the master: A −12.0, B −11.8, C −11.1 LUFS while the vocals last.
  - "Background vocals of background vocals for lead 2" left out: it is an exact copy of Main vocal lead 2's first line, 26.6 dB quieter.
- **Tried and dropped (beat peaks):** the master limiter dipped on the beat's own snare and kick hits (120 Hz–2 kHz). An 808 compressor (`low_ctl.py`) made it worse; a full-band spike limiter on the beat (`beat_peaks.py`, first version) cut the dips but took 2 dB off the 808; a mid-band one took 2 dB off the mids and barely helped. Mastering at −12.0 instead of −11.5 LUFS fixed it with the beat untouched: 5 s of dips over 3 dB (21 s at −11.5), worst −3.8 dB. Streaming services turn songs down to about −14 LUFS anyway.
- **Loudness:** −12.1 LUFS integrated, −1.2 dBTP (WAV) / −1.1 dBTP (MP3); the −1 dBTP ceiling leaves room for streaming encoders.
- **Effects log and review report:** `effects/v1.json`, `reports/v1.md`: ⚠️ close, 60 passed, 4 to check, 0 failed. The four are the mid, upper-mid, high and air bands 4–10 dB up against the raw stems summed: the raw vocals were recorded 8 dB under the beat, so lifting them over the beat moves these bands. The highs come from the vocal recordings (lead 2 is bright); listen for sharpness on earbuds.
- **Open questions for the owner:** the vocals end at 2:51 and the beat plays on to 3:20 (12 s of full beat, then the 16 s piano outro): keep it, or fade the song out after the last line? The background-of-background 2 file: a different file meant? The beat is a free YouTube type beat (160 kbps): the producer's WAV would sound cleaner, and free beats usually need the producer's lease or credit before streaming release.
- **Listening check:** pending owner. Spots: 0:31–0:40 (leads and the layers under them), 1:24–1:47 (echo throws into drop 1, the reverb opening up), 2:17–2:33 (drop 2), 2:48–3:00 (the last line fading out).

## Final sign-off

- [ ] Owner approved the final master

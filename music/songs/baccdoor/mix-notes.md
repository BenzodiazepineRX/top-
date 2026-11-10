# Mix notes

**Song:** Baccdoor

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

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

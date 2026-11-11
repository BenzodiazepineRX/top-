# Mix notes

**Song:** Don't Need Closure

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

### 2026-11-10 — v2-master (far less reverb on the adlibs; the adlibs set against the leads bar by bar)

- **Files:** `Dont_Need_Closure_master_v2_24bit.wav`, `Dont_Need_Closure_master_v2.mp3`, `Dont_Need_Closure_v1_vs_v2_0m18.mp3` (v1 then v2, same loudness, 0:18–0:38). Audio delivered in chat, not committed.
- **Owner on v1:** "The adlibs/background vocals have way too much reverb. I just want them to have reverb but not that much and I want them to sit under the lead vocals perfectly." After v2: "W".
- **Measured first:** the adlib tracks were exported with a long reverb on them: at clean word endings the tail sits 20–21 dB under the word for 0.7 s and more. v1's firm compression on the adlibs (10:1 at −18 dB, 5.2 dB average, 15 dB on loud words) pulled that tail up to 5.5–6.1 dB under the word, and v1 added a hall on top. The mistake was mine: the compression was chosen to tame the tracks' spikes without checking what it did to the tails.
- **What changed (everything else is v1):**
  - Adlibs: only each track's own pan direction kept (the wide part of the reverb dropped; the track stays at its position), tails turned down before the EQ (up to 10 dB), gentle compression like the leads (2.6 dB average), a lookahead peak catcher for the spikes (0.5–0.7 dB average), tails turned down once more at the end (up to 6 dB), no reverb added.
  - Adlib level: each track first to its own level (left and right balanced), then the pair set 6.5 dB under the leads, measured where both sing, in 2-bar windows moved one bar at a time.
- **Result:** adlib tails at clean word endings: −25.8 / −28.5 dB (raw tracks −19.8 / −21.2; v1 −5.5 / −6.1). The adlibs together against the leads: median −6.5 dB, range −7.6 to −5.5 (v1: median −4.2, range −8.2 to −1.7). −12.1 LUFS, −1.2 dBTP. All `verify_closure.py v2` checks pass, including the new tail check (fails if the mix has more tail than the raw track).
- **Lesson:** compression lifts whatever reverb is baked into a track by about its gain reduction. Measure the tails (`tail_check.py`) after any dynamics on a track that arrives with reverb.
- **Effects log and review report:** `effects/v2.json`, `reports/v2.md`: ⚠️ close, 70 passed, 4 to check, 0 failed. Three are tone against the raw stems summed (mid +3.1, upper-mid +6.4, air −4.7 dB): the dark, boomy vocals were brought forward in the word range and their S sounds and fizz turned down, on purpose. One is adlib 1's de-esser at 25.7% of the time (the line is 25%): kept, the layer sits behind.
- **Listening check:** the owner answered "W" to v2. Final sign-off not asked for yet.

### 2026-11-10 — v1-master (tone, even levels, echo throws, reverse-reverb build-ups, streaming master)

- **Files:** `Dont_Need_Closure_master_v1_24bit.wav`, `Dont_Need_Closure_master_v1.mp3`, `Dont_Need_Closure_before_after_1m24.mp3` (raw stems summed, then v1, same loudness). Audio delivered in chat, not committed.
- **Owner's request:** "Let's make this sound professional. Reverse reverbs at perfect build up into beat drop, perfectly timed delay/echos to fill in empty gaps, perfect volume all the way through from lead to background/adlibs so the listener can hear absolutely everything and just feel bliss in the music."
- **Grid:** 126.000 BPM; 808 on beats 1–2, clap on beat 3, so bar 1 starts at 0.955 s; the drums enter on the downbeat of bar 10 and return on bars 50 and 74 (the kick's click sits 3.4 ms before the grid).
- **Pitch:** not retuned. The song is mostly rapped (voiced 14–16% of the time, few held notes), so there is nothing steady to correct, and no note-by-note pitch editor is installed here.
- **What changed (from the raw stems):**
  - Leads: mono, tone-matched 90% toward the Baccdoor v4 lead (the owner's "nearly PERFECT" tone), then −3 dB at 350 Hz and +3.5 dB at 3 kHz; dynamic EQ and de-esser at high percentiles (rap is all transients: 22–24% and 20–24% of the time); gentle compression (3.6 dB); every line ridden to the same loudness, 0.5 dB under the beat (90% of 50 lines within 0.5 dB).
  - `match_eq.py` fixes found on this song: silence between lines no longer counts when the tone is measured, and bands are an octave wide (the voice is monotone at B2, so narrower bands tried to fill the gaps between its harmonics).
  - Adlibs: tone match with a darker top, each track ridden every 2 bars (v1; see v2 for what was wrong with their compression and reverb).
  - Echo throws on the last word of every lead line: 50 throws, 176 echoes, all within 0.06 ms of a main beat; 4 echoes in the hooks and before the two real pauses, 3 in the verses, 8 half notes on the last line into the piano outro.
  - Reverse-reverb swells of the word that lands on the drop, into bars 10, 50, 66 and 74 (each starts on a downbeat and ends within 0.09 ms of its word), and one-bar risers made from the drop's own first hit into bars 10, 50 and 74.
  - The beat's 3.2–6.5 kHz ducks up to 5 dB on the leads' consonants only (28% of the time).
- **Loudness:** −12.1 LUFS, −1.2 dBTP (WAV) / −1.1 dBTP (MP3).
- **Effects log and review report:** `effects/v1.json`, `reports/v1.md`.
- **Open questions for the owner:** artist name, a commercial reference track, the streaming service, the deadline; the beat is a YouTube rip (the producer's WAV would be cleaner, and a free beat usually needs the producer's lease or credit before release).

## Final sign-off

Use this only for the master you believe is finished. Leave every box unchecked until that item is actually true. The song is still in progress until the owner signs.

- [ ] All creative effects from the brief are in place, on the right track or mix bus, in the right spot, and the right length
- [ ] Echo, delay, pre-delay, and decay times match this song's BPM, and the math was checked
- [ ] Earbuds check passed
- [ ] Phone speaker check passed
- [ ] Car check passed
- [ ] Studio monitors check passed
- [ ] Loudness and true peak meet this song's targets
  - Integrated LUFS:
  - True peak:
  - Target used (platform and number):
- [ ] Compared against the reference tracks in the brief
- [ ] Owner sign-off on the final master

**Master version:**
**Date:**
**Owner:** Chex
**Owner's words:** (Chex writes "approved" here, or an agent copies Chex's exact sign-off)

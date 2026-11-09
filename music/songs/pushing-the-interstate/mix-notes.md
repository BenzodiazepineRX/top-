# Mix notes

**Song:** Pushing the Interstate

This is the log for this song. Add a new entry every time you export a version or finish a listening check. Put the newest entry at the top.

Say what you changed and why in plain English. Include settings only when a future session would need the exact number. Tie each choice back to this song's brief.

## Version log

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
**Date:** 2026-11-08
**Owner:** Chex
**Owner's words:** "My boy….. it's beautiful" — then, asked whether that counts as final approval: "Yessss sirrrrr"

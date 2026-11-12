# Mix notes

**Song:** What I'm Posed To Do

No agent here can hear. Everything below is measurement; the owner's words are the only verdict.

## Version log

### 2026-11-12 — v2 (lighter autotune, softer leads, telephone background repeats, gaps filled)

- **Owner on v1 (his words):** "Auto tune, lighter please. I want background vocals for the lead to be telephone
  and reverb but clear repeating the last few works with echo/echo throws. 3, set them slightly louder when the
  vocals end, I want parts added back to the empty parts of the song to fill the space , the main vocals are a
  bit harsh and scratchy, and j would like a tad bit more reverb on them and again, the auto tunes needs to be
  lighter. Also the echos are a bit off bit or they cut early"
- **Files (sent in chat):** `1_WIPTD_v1_then_v2_1m55.mp3` (v1 then v2, both −12.0 LUFS, 1:55–2:10),
  `What_Im_Posed_To_Do_v2.mp3`, `What_Im_Posed_To_Do_v2_24bit.wav`. Built by `build_v2.py`; echo list
  `v2-echo-cues.json`. Built from the stems again, not on top of v1's audio.
- **What changed, one line per thing he named:**
  - *Autotune lighter:* strength 0.85 → 0.60. Voiced frames within 15 cents: Lead 1 52% (v1 68%), Lead 2 55%
    (v1 78%).
  - *Harsh and scratchy leads:* a 3 dB cut at 2.8 kHz and 2.5 dB off above 9 kHz on every voice, and a gentler
    compressor (2:1, was 2.5:1). Cuts only. The lighter autotune also reshapes less of the voice.
  - *More reverb on the leads:* plate return −17 → −15 dB, ducked 3 dB instead of 4.
  - *Background vocals as a clear telephone repeat:* the plain wide double is gone. The telephone repeats are
    the background vocal: first repeat 5 dB under its words (was 7), band 380–3600 Hz (was 420–3200), ducked
    1.5 dB (was 2), its plate −10 dB (was −12), two repeats even when the next voice is in (was one), three
    or four where a gap follows. 51 cues.
  - *Echoes off beat:* v1 started each copy on the next beat line, which moved the words off their own
    rhythm. Now each copy is the words exactly a half note (888.89 ms) later, like a real delay.
  - *Echoes cut early:* v1 ended each copy 40 ms after the level fell under the line threshold. Now the copy
    follows the word's tail down to 28 dB under the words (20–170 ms more), with a 40 ms fade.
  - *The 2:10 voices louder:* 3 dB under the leads → 1.5 dB under.
  - *Empty parts filled:* the first six bars of verse 1 (bars 25–30) pasted into the empty 2:25–2:38 (bars
    83–88). The outro after 3:49 has a four-repeat telephone echo of the last words. The 41-second intro is
    still beat only; asked.
- **Measured:** master −12.0 LUFS, −1.2 dBTP (MP3 −1.1). Leads −0.5, −0.7, −0.3, −0.6 dB against the full
  beat. 2-bar lines within 1.3 dB, largest to smallest (v1 0.8). First repeat 7.2 dB under its own words
  (median). Echo sounding 16.8% of 0:42–3:50 (v1 8%). Limiter over 3 dB on 11.4% of blocks in full sections.
- **Not re-run:** the two checkers and Grok did not review v2. 20 echo cuts still start at a shallow dip.
- **Feedback:** none yet.
- **Next:** wait for his words. Change only what he names.

### 2026-11-11 — v1 (first full mix and master; not heard by the owner yet)

- **Files (sent in chat, not stored here):** `1_WIPTD_before_then_v1_1m55.mp3` (raw stems summed, then v1,
  loudness-matched, 1:55–2:10), `2_WIPTD_autotune_light_then_strong.mp3` (same 15 s, autotune strength 0.60
  then 0.85, beat and leads only), `What_Im_Posed_To_Do_v1.mp3`, `What_Im_Posed_To_Do_v1_24bit.wav`.
- **Built by:** `build_v1.py` in this folder (run from a folder holding `src/` with the five stems; the beat
  renamed `Beat.wav`). Echo list: `v1-echo-cues.json`.
- **History:** a first build was made in another session on 2026-11-11 and lost with its container before the
  owner heard it. This is the rebuild, with that session's reviews applied.
- **Started from these approvals** (`music/LESSONS.md`): lead 0.5 dB under the full beat; lead plate about a
  dotted half, return −17 dB; echoes on last words, on the beat, about 5 dB apart; master about −12 LUFS; the
  autotune profile of Baccdoor (79–92% of held notes within 15 cents). **No tone match was possible:** no audio
  of an approved lead is stored anywhere this session could reach. The chain therefore only cuts.
- **What it does:**
  - *Autotune:* PSOLA toward D minor notes (A4 = 439.5 Hz), strength 0.85, each target note held at least
    104 ms. Voiced frames within 15 cents: Lead 1 31% → 68%, Lead 2 31% → 78%, the 2:10 voices 20% → 69% and
    27% → 82%. Holding the note halved the number of target-note changes (496 → 239, 436 → 220).
  - *Each voice:* level to −18 dBFS RMS, high-pass 90 Hz (120 on the 2:10 voices), dynamic cut at 3 kHz
    (about 26% of the time, 1.2 dB average), 2.5:1 compressor, then de-esser 5.5–9 kHz capped at 6 dB. No
    boost, no saturation, no bright shelf.
  - *Even volume:* phrase leveler, spread 2.4 → 0.1 dB. Where both leads sing at once (11.1 s in total) each
    comes down 3 dB. Measured after: 2-bar lines within 0.8 dB of each other, largest to smallest.
  - *Levels:* leads −0.5, −0.9, −0.2 and −0.7 dB against the full beat (bars 38–49, 66–73, 90–97, 114–129).
    The 2:10 voices sit 3 dB under the leads' level. They sing alone, so 6 dB under would have dropped the song.
  - *Created background vocals:* a band-limited (250–5000 Hz), wide, slowly moving double of the leads on the
    hooks (bars 34–49, 66–73, 90–97, 114–129), 11 dB under. Not on the 2:10 voices.
  - *Telephone echoes:* 48, one at the end of each singer's turn. The last few words (0.34–0.86 s), band
    420–3200 Hz with +3 dB at 1.8 kHz, first copy 7 dB under its words on the next beat after they end, ducked
    2 dB while anyone sings, plate 0.889 s at −12 dB. **One repeat where the next voice is already in (40
    cues); two to four, a half note (888.89 ms) apart and 5 dB down each, where a gap follows (8 cues).**
  - *Reverb:* lead plate 1.333 s, pre-delay 27.8 ms, return −17 dB, ducked 4 dB. Hall 1.778 s on the 2:10
    voices and the double at −13 dB.
  - *Arrangement:* verse 2 (bars 50–65) pasted to bars 98–113; the 16-bar hook (bars 34–49) pasted to bars
    114–129. Each singer cut at their own quiet moment (all cut points −50 dBFS or lower). The beat's own
    outro (3:49–4:02) plays out with a four-repeat echo of the last words.
  - *Master:* −12.0 LUFS, −1.2 dBTP (MP3 −1.1), mono below 90 Hz, no bus shelf (`--mid-shelf 9500:0`).
- **The team's review, and what was done with it:**
  - *Grok, round 1 (first build):* autotune 0.85 too strong; half-note echoes will smear; reverb send too
    wide; telephone too peaky and compressed; dynamic EQ and de-esser too much; double too loud at −9 dB.
  - *Grok, round 2:* accepted the autotune strength, the half-note spacing and the telephone changes. Still
    disagreed on the reverb send (kept: it is the approved setting), the de-esser reaching 8 dB (adopted: cap
    6 dB) and the first echo at −8 dB being too loud (kept: the owner could not hear echoes 13 dB under).
  - *Timing checker (passed):* 135.000 BPM at 8, 16, 32 and 64 bars; drum hits within 0.6 ms of the grid
    early, middle and late; kick on beat 1, clap on beat 3; every echo within 0.5 ms of a beat and after its
    words; pasted sections at 0 ms offset, no chopped words.
  - *Timing checker (failed, fixed):* 107 of 121 echo repeats landed on the other rapper's next line, because
    the gap test ignored a voice that had already started. 27 of 44 echo cuts began mid-sound (the 0.86 s cap
    forced ten of them). The last line had 8 repeats.
  - *Vocal checker (passed):* no clicks, dropouts or drift from the autotune; lead against the beat; pasted
    sections within 0.01 dB of their sources; mono ripple from the double +0.4 / −0.1 dB.
  - *Vocal checker (failed, fixed):* echoes buried 11–18 dB under; both leads overlapping at 1:40.5 and 3:05.8
    (+4.7 dB); 9–16 kHz up 2.8–3.7 dB because the compressor came after the de-esser; pitch target flipping
    1.3–1.7 times a second.
- **Known and left as is:**
  - The limiter takes more than 3 dB off 14% of the 50 ms blocks in the full-beat sections (most 6.6 dB), on
    the 808 hits, in runs of 150 ms or less. No 3-second stretch with vocals sits more than 1.1 dB under its
    neighbours. Holding back the beat below 120 Hz was tried and did not change this, so the beat is as
    delivered. If the owner hears pumping, lower the target to −13 LUFS.
  - 22 echo cuts start at a dip shallower than 10 dB, nearly all on Lead 2, whose lines run on without a gap.
    They get a 35 ms fade-in.
  - Lead reverb measures 20 dB under the lead while singing (return −17 dB plus the 4 dB duck).
  - Three short words sit 9–10 dB under their phrase: 0:47.2, 1:44.1, 3:09.4.
- **Questions sent to the owner:** autotune light or strong; echoes more, less or right; the 2:10 voices
  louder, same or further back; is the order at the end right; anything harsh.
- **Feedback:** none yet.
- **Next:** wait for his words. Change only what he names.

## Final sign-off

- [ ] Owner sign-off on the final master

**Owner's words:**

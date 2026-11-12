# Mix notes

**Song:** What I'm Posed To Do

No agent here can hear. Everything below is measurement; the owner's words are the only verdict.

## Version log

### 2026-11-12 — v6 (echoes on the half-time pulse, louder than the line, clearer; vocals less dull)

- **Owner on v5 (his answers to four questions):** echo timing "Still off beat"; echo level "Too quiet: make louder", choosing "Let the
  echoes go louder than the line they repeat, so they clearly stand out."; echo sound "Too muffled"; main vocals "Too dull".
- **Files (sent in chat):** `1_WIPTD_v5_then_v6_0m50.mp3` (v5 then v6, same loudness, from 0:49.5), `What_Im_Posed_To_Do_v6.mp3`,
  `What_Im_Posed_To_Do_v6_24bit.wav`. Built by `build_v6.py` (= `build_v5.py` plus the changes below; its defaults are the settings sent),
  echo list `v6-echo-cues.json`. Starting point: v5 as sent; nothing else changed.
- **Cause of "still off beat":** the beat is half-time. The kick is on beats 1 and 4 and the clap only on beat 3, so the felt pulse is beats 1 and
  3 (every half note, 889 ms). v5 put each echo on the next beat line of any kind: 23 of 51 first echoes landed on beats 2 or 4, between
  pulses, and dotted-half spacing put later repeats off too (42 of 109 repeats on the pulse).
- **What changed:**
  1. Each echo's first sound lands on the next beat 1 or 3 after the words end, and repeats are spaced a half note or a whole bar.
  2. Louder: the first repeat may go up to 2 dB over its own words in the louder ear, and the pan is (1.05, 0.7) so both ears hear it
     (was 1.15, 0.45).
  3. Less muffled: the telephone band is 250 Hz-6.5 kHz (was 380 Hz-4 kHz), with a light lift at 2.5 kHz instead of the phone peak at
     1.8 kHz. Later repeats still darken (6.5/5.5/4.5/3.8 kHz). The echo reverb is 300 Hz-6.5 kHz (was 400 Hz-4.5 kHz).
  4. Less dull: the lead's shelf above 4.5 kHz is -3 dB (was -6), and the lead plate's top is 6 kHz (was 4.5 kHz).
  5. Side effect, fixed: the louder echoes made the final limiter dip the whole song (beat too) at 24 echo starts, worst 4.5 dB on
     "adderall". Only the 7 first repeats that caused a dip over 2 dB were lowered, by 0.6-2.0 dB (0:51.5, 1:13.8, 1:28.0, 1:31.5, 2:53.3,
     2:56.8, 3:39.5). Heard with both ears (mono sum, 400-3600 Hz) those 7 are still 1.1-3.1 dB louder than in v5. In the louder ear
     alone, five of them ("all" 1:13.8, "at all" 1:28.0 and 1:31.5, "adderall" 2:53.3, "like at all" 3:39.5) are level with v5 (-0.4 to +0.1 dB).
- **Measured:**
  - Pulse: 51 of 51 first echoes start on beat 1 or 3 (the checker counts 50, see `checks/pulse_check.py`). 106 of 107 repeats are on the
    pulse; the remaining one is the same false alarm.
  - Echo against its own words, 400-3600 Hz: median +0.4 dB, loudest +1.1 dB, 36 of 51 over their words. v5 was -2.8 dB with none over.
  - Echo against the live mix: it reaches within 6 dB of the mix after a median 65 ms (v5 123 ms). In its first 100 ms it sits a median
    -4.2 dB under the mix (v5 -5.7 dB).
  - Echo tone: 3-7 kHz energy is 2.6 dB higher against 250-1500 Hz.
  - Lead tone: fizz is -32.9/-32.4 dB, between v3 (-29.8/-28.6, "scratchy") and v5 (-35.0/-34.6, "dull"); the approved anchor is -34.4. The
    1.6-3.5 kHz band is +0.5 dB against v5.
  - Master: -14.5 LUFS, -1.4 dBTP. Final limiter p99 2.9/2.3/3.2 dB in the full sections (v3 3.4/3.3/3.4). Echo starts that add over 1 dB of
    limiting: 24 (v5 9); the worst is 3.7 dB (v5 3.6).
- **Team:** Grok reviewed the limiter trade-off and called it sound. Its alternative was to duck the beat 1.5-2 dB under every echo start,
  with less kick and clap punch as the risk. That is plan B if the echoes still don't get through. It was not used because it changes the
  beat in 51 places, which he did not ask for. The independent checker agents were not run, to save his limit; the checks above are this
  agent's own.
- **Risks to ask about:** fizz is now about 2 dB over the approved anchor. And an echo louder than its line goes against the general
  rule (about 4 dB under). He asked for it on this song.
- **Feedback:** none yet.

### 2026-11-12 — v5 (echoes on the beat, as loud as the rule allows)

- **Owner on v4 (his words):** "You did all that work and it's still messed up" … "Echo still off beat & not getting through"
- **Files (sent in chat):** `1_WIPTD_v4_then_v5_0m50.mp3` (v4 then v5, same loudness, from 0:49.5), `What_Im_Posed_To_Do_v5.mp3`,
  `What_Im_Posed_To_Do_v5_24bit.wav`. Built by `build_v5.py` (= `build_v4c_draft.py` plus the two changes below) from v4's cleaned voices.
- **Cause of "off beat":** since v2 each echo was the words a fixed note value after he sang them, so it copied the rap's loose timing. The echo's
  first sound sat a median 136 ms (v3) / 74 ms (v4) from the nearest beat line; only 18-19 of 51 within 30 ms.
- **What changed:** the first sound of each echoed word now lands on the next beat line after the words end (LESSONS echo rule 4): median 6 ms
  from the beat, 50 of 51 within 30 ms, none over 100 ms. Echo level up to level with its words in the louder ear (loud part -2.8 dB in band,
  mono; v4 -3.7). Also from the v4c draft: no echoes lowered for headroom, the lift only on voiced sound, peak hold 13 dB, shared lines in the
  phrase gains, later repeats of long words spaced so they never overlap.
- **Measured:** master -14.5 LUFS, -1.3 dBTP; final limiter p99 3.0 / 2.0 / 3.0 dB in the full sections (v3 3.4/3.3/3.4).
- **Not better, honestly:** on the beat the echo's start meets the drum hit and the next line, so start-vs-mix is -5.7 dB (v4 -4.8). The echoes
  cannot go louder without exceeding their own words. Not checked by the independent checkers (sent at once; the owner is low on limit).
- **Feedback:** none yet.

### 2026-11-12 — v4 (lighter autotune, less fizz, echo starts lifted)

- **Owner on v3 (his words):** "Please fix the background echos, they are lagging in as if it's not loud enough in the beginning of them to
  produce the word then it just cuts in late. Also lower the auto tune a bit more lets get the main vocals not so scratchy"
- **Files (sent in chat):** `1_WIPTD_v3_then_v4_0m50.mp3` (v3 then v4, loudness-matched, from 0:49.5), `What_Im_Posed_To_Do_v4.mp3`,
  `What_Im_Posed_To_Do_v4_24bit.wav`, and a before/after picture of the "yours" echo. Built by `build_v4.py` + `v3lib.py` into `work_v4b`;
  echo list `v4-echo-cues.json`; checks in `checks/`. Sent early at the owner's request ("I'm running low on limit. Send it now").
- **What changed:** autotune strength 0.60 -> 0.45, and held notes 40-60+ cents off every scale note are left alone (he sang them). Lead chain:
  gain, high-pass, v3's -3 dB bell at 2.8 kHz, a -6 dB shelf above 4.5 kHz, de-esser; the 2:1 compressor and the dynamic EQ removed (the
  compressor raised fizz 2.6 dB). Per-voice peak hold at 15 dB. A fixed level trim per rapper (L1 +0.2, L2 -0.9 dB) plus phrase gains switched
  only in silences. Echoes: copies start in the gap after the previous word; soft starts lifted toward the live mix (never above the echo's own
  loud part); long held words echoed after they end (dotted half or a bar); pan (1.15, 0.45); older repeats that would sit on a newer echo
  dropped; each echo's peaks held 9 dB over its loud part with its level restored; 9 first repeats lowered 0.8-4.0 dB where they pushed the
  final limiter. Master -14.5 LUFS (v3 -14.0), -1.3 dBTP.
- **Measured (and confirmed by two rounds of independent checks):** lead fizz -34.7/-34.3 dB (v3 -29.8/-28.6; approved anchor -34.4);
  1.6-3.5 kHz 0.5-0.9 dB under v3; 4-8 kHz 5.6-6.3 dB under v3 (clarity: ask). Tuner: shift on held notes median 3.2/3.3 cents (v3 5.6/6.5),
  no off-scale note moved, no clicks, timing drift under 0.5 ms. Peak hold acts on 3-4% of the singing. Lines: p5-p95 0.86 dB (v3 1.25).
  Final limiter p90/p99 below v3 in all full sections. Copies no longer start inside another word (v3: 6 did).
- **Known and not fixed in this version (the second check, before sending):** against the mix, echo starts are no clearer than v3 on the
  median (-0.4 dB; 16 clearer, 13 weaker). The long-word echoes moved later ("raw", "all", "graveyard") are 0.7-4.7 dB weaker than v3 at
  their start; v3's half-note placement measured clearer, so the hypothesis behind moving them was wrong. The 9 echoes lowered for headroom
  work against his request. On "yours" the lift raised a 25 ms hiss before the word, not the word. Peak hold at 15 dB lets lead peaks cause
  limiter hits at 1:55.6 (5.1 dB) and 3:45.4; the "it off" echo at 1:38.0 pulls the mix 3.6 dB at 1:38.3. The shared line at 1:41.3 and 3:06.7
  sits 1.2 dB under the median.
- **Ready for the next version, not built or checked:** `build_v4c_draft.py`: first echo back at a half note (later repeats spaced so they do
  not overlap), no headroom lowering, the lift only on voiced sound, peak hold 13 dB, shared lines included in the phrase gains.
- **The team:** Grok (round 4) agreed on the scratch diagnosis and the -14.5 LUFS call, and preferred raising weak echoes over moving them.
  Three independent checkers (two rounds) found the problems listed above; their scripts are in the session scratchpad, not stored.
- **A measuring mistake, recorded:** a 1 ms envelope taken every 44th sample drifts 0.5 s by 3:40. It produced a false "pasted sections are
  324 ms late" alarm and fake silent lead-ins on the echo plots. Fixed in every check script (see `music/LESSONS.md`).
- **Feedback:** none yet.
- **Next:** wait for his words. If the echoes still lag in, start from `build_v4c_draft.py` and check it the same way.

### 2026-11-12 — v3 (leads no longer rebuilt by the tuner or clamped by the limiter; echoes start on words)

- **Owner on v2 (his words):** "The echos aren't even playing sometimes it like they don't wanna get though. It's
  like they aren't catching the words or something also they lead main vocals sound very robotic like almost
  amped like"
- **Files (sent in chat):** `1_WIPTD_v2_then_v3_1m55.mp3` (v2 then v3, loudness-matched, 1:55–2:10),
  `What_Im_Posed_To_Do_v3.mp3`, `What_Im_Posed_To_Do_v3_24bit.wav`. Built by `build_v3.py` with `v3lib.py`
  and word timing from `word_timing.py`; echo list `v3-echo-cues.json`. Built from the stems again.
- **What was measured on v2 before anything was changed** (scripts in `checks/`):
  - *Robotic.* Raw leads: pitch moves a median 9.2 and 8.5 cents every 10 ms; 20% of frames move under 3 cents.
    After the v1/v2 tuner: 2.9 cents, and 51% of frames nearly still. The tuner (PSOLA fed a pitch line from
    pYIN, which comes in 10-cent steps, then snapped and median-filtered) replaced the voice's own pitch
    movement with a stepped line. Strength had nothing to do with it. PSOLA with the pitch left untouched also
    does not null against the raw voice, so every voiced frame was being rebuilt.
  - *Amped.* The leads' peaks stood 19–21 dB over their own level. At the mix's 40 largest peaks in a full
    section the lead supplied 51% of the amplitude and the 808 27%. Measured with a quiet 3 kHz probe tone, the
    final limiter (5 ms attack, 60 ms release, +6.8 dB into it) pulled the vocal range down 3.2 dB (p90), 6.1 dB
    (p99) and 9.9 dB at the deepest, with drops of more than 2 dB inside 5 ms nine times a second. No stage
    clipped (every file is float; peaks over 0 dBFS inside the chain were carried, not cut).
  - *Echoes.* Against everything else playing, in 400–3600 Hz: 11 of 51 first repeats within 6 dB (clear), 10
    more than 10 dB under. 14 copies were shorter than 0.45 s (about one syllable) and 20 started where there
    was no break. Lead 2 ends many lines on a word held longer than the 0.86 s window ("graveyard", "all",
    "raw", "adderall"), so the copy began in the middle of the held vowel.
- **What changed, and only for those three things:**
  - *Tuner (`v3lib.tune_natural`).* No resynthesis. Praat pitch every 5 ms; the slow centre of each note is
    compared with the nearest D minor note; 60% of that distance is corrected, and nothing while the pitch
    glides faster than 900 cents a second. Applied as a tiny speed change and re-timed with a 6 ms crossfade at
    the next quiet point. Pitch movement after: 9.6 and 8.9 cents per 10 ms, 20% and 21% nearly still (raw 9.2,
    8.5, 20%). Held notes within 15 cents of the key: Lead 1 62% → 83%, Lead 2 51% → 73%, the 2:10 voices
    30% → 55% and 37% → 59%. Largest shift 60 cents; largest timing offset 6.1 ms.
  - *Voice peaks (`v3lib.hold_limiter`).* Each voice's peaks may stand 12 dB over its level. The gain is held
    15 ms and released at 40 dB a second, so it cannot follow single pitch periods. Reduces more than 1 dB for
    5–6% of the singing, more than 3 dB for 1–2%.
  - *Beat.* Below 150 Hz the tips of the loudest 808 notes are rounded by 4 dB (active 2.1% of the time, bass
    level −0.7 dB, overtones added 20 dB under the bass). Above 150 Hz the sharpest hits are held 4 dB (more
    than 1 dB for 2.8% of the time). Nothing else in the beat is touched.
  - *Master.* **−14.0 LUFS, −1.3 dBTP, on purpose 2 dB quieter than his other songs.** Limiter with 8 ms
    look-ahead, 30 ms hold, 30 dB a second release. In full sections it now takes 0.8–1.3 dB (p90), 3.4 dB
    (p99), 4.7 dB at the deepest, with 0.2–0.35 sudden drops a second. The same treatment at −13 LUFS measured
    3.1 dB (p90) and 5.1 dB (p99); at −12 the limiter was no better than v2. This beat has long soft parts and
    very large 808 notes, so −12 can only be reached by clamping the whole song on every hit.
  - *Echoes.* Every copy starts at the start of a word: word times from a local speech model (`small.en`, run
    on this machine; nothing was uploaded), moved to the nearest dip in level. 35 take the last words that fit
    in 0.86 s; 16 take the whole long last word (0.97–1.6 s). Each repeat is the words exactly a half note
    (888.89 ms) later. First repeat 2.5 dB under its own words in 400–3600 Hz, raised where it lands on
    something loud, never over its words; for a quietly sung last word, at least 6 and never less than 4 dB
    under the line. No ducking. Panned left and right in turn. Two repeats when the next voice is in, three or
    four in gaps, 5 dB apart. Measured: median 4.8 dB under everything else (v2 7.7), 34 clear (v2 11), 4 more
    than 10 dB under (v2 10) — the same word, "enough", in four places, which ends on a long "f". Broadband,
    first repeats sit 4.6–8.2 dB under their words. Echo is sounding 27.5% of 0:42–3:50 (v2 16.8%, v1 8%).
  - Unchanged from v2: the cuts at 2.8 kHz and above 9 kHz, 2:1 compressor, de-esser, phrase leveler, lead
    plate at −15 dB, the 2:10 voices 1.5 dB under the leads, the arrangement.
- **Balance, measured:** leads −0.6, −0.7, −0.2, −0.6 dB against the full beat. 2-bar lines within 1.2 dB.
- **The team:**
  - *Grok, round 3:* agreed the frozen pitch line was the main cause of "robotic", that the limiter and the
    19–21 dB peaks fit "amped" better than saturation, and that −14 LUFS is the right call. It disagreed with
    echoing only the first 0.86 s of a held word ("still creates the 'cut early' complaint") — adopted as the
    whole word; its suggestion of a one-bar delay for those was not taken, so that every echo keeps the same
    half-note rhythm. It asked for a check of doubled consonants at the tuner's re-timing points.
  - *Independent checker:* **did not finish.** It was cut off twice by usage limits (once at the five-hour limit,
    once at the Fable limit) before it reported anything, so v3 went out without its second opinion. The one
    check Grok asked for was run by hand instead (`checks/tuner_double_bursts.py`, strong 2–8 kHz bursts on 1 ms
    steps, 0:40–2:55): Lead 1 raw 347, v2 tuned 518, v3 tuned 348; Lead 2 raw 350, v2 510, v3 349. Pairs of
    bursts 4–16 ms apart: Lead 1 raw 183, v2 290, v3 176; Lead 2 raw 178, v2 277, v3 179. So the v1/v2 tuner
    added about half as many extra sibilant bursts as the raw take had, and v3 adds none. **Not checked by
    anyone else:** echo starts against an independent onset detector, repeat timing, the beat treatment.
    Measured by me: every first repeat is 4.6–8.2 dB under its own words (none over), 51 of 51.
- **Not known:** whether he will hear "amped" as fixed. Two causes were measured and removed; no third was found.
- **Feedback:** none yet.
- **Next:** wait for his words. Change only what he names.

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

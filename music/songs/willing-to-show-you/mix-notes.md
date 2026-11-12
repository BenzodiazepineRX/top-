# Mix notes

**Song:** Willing To Show You

## Version log

### 2026-11-12 — v3 main-vocal balance correction

- **Owner feedback:** “The main vocals are entirely too loud. This needs to be evened out perfectly.” V2 is rejected for lead/beat balance; its earlier forward-vocal proposal is superseded.
- **Change:** main lead bus -4 dB relative to v2, with its lead delay and plate also -4 dB. Individual main leads now total -6 dB after their cached working-level processing. Beat/adlib gains remain as v2. No new tuning, EQ, compression or timing edits were applied to the takes.
- **Evenness:** existing processed lead active RMS at v2 faders is -22.64 / -22.71 dBFS, only 0.07 dB apart. The matched reduction retains that relationship. Phrase measurements showed no systematic lead-to-lead offset, so no unrelated gain rides were added. Adlibs were about 7.9 dB below the leads and remain about 3.9 dB below after the correction.
- **Exports:** `exports/Willing_To_Show_You_Master_v3_24bit.wav` and `exports/Willing_To_Show_You_Master_v3.mp3`. New 44.1 kHz / 24-bit WAV and 320 kbps preview. Both decode to 6,256,560 frames. Measured -11.6 LUFS integrated, WAV -1.5 dBTP, MP3 -1.4 dBTP.
- **Comparison:** `exports/Willing_To_Show_You_v2_then_v3_AB.mp3`: v2 first, 0.8-second pause, v3 second, each over 0:42–0:57 and matched by passage loudness. Master target remains -11.5 LUFS to keep overall playback comparable without reversing the 4 dB voice/beat change.
- **Provenance:** `render_v3.py` consumes validated v2 caches; rerun `render_v2.py` from the originals first when rebuilding. Routing/cache hashes in `measurements/v3-routing.json`; exact new master settings and final verification in `measurements/v3-master-settings.json` and `measurements/v3-delivery-verification.json`.
- **Review:** `effects/v3.json`, raw `reports/v3.md`, and `reports/v3-engineer-review.md`. Raw report: 53 passes, 2 warnings, 1 generic LRA failure. The source beat itself has LRA 2.0 LU; the quieter-vocal v3 has 2.1 LU, and limiting workload is only about 0.8 LU. This is an explicit song-specific exception under the playbook's brief-first rule; do not restore the rejected loud vocals or invent section dynamics to satisfy a generic range threshold. Full rationale is in the engineering review. The raw report and its failed row are retained, not represented as all-passing.
- **Listening:** the owner supplied the v2 listening feedback above. V3 auditory balance, reference comparison and playback-system checks still await listening; no claim of perfect balance is made from measurements.
- **Creative effects/timing:** no new request or effect; existing 135 BPM ambience timing is retained. Only the level of main-lead effects changes.

### 2026-11-10 — v2 workspace work in progress

- **Files:** `exports/Willing_To_Show_You_Master_v2_24bit.wav` and `exports/Willing_To_Show_You_Master_v2.mp3`; 44.1 kHz stereo, 24-bit WAV and 320 kbps MP3. Audio stays private/local and is ignored by Git, as this repository requires. Sources are unchanged in `source/`.
- **A/B:** `exports/Willing_To_Show_You_Source_then_v2_AB.mp3`. First the original stem sum at 0:42–0:57, then 0.8 s pause, then v2 over the same passage. Excerpts were trimmed first and their passage loudness matched with `ab_match.py`. The combined preview gets a uniform -1.5 dB encoding gain for extra codec headroom, preserving the relative comparison. No source or master sample was moved.
- **What changed:** both alternating leads receive equivalent processing; toolkit gain staging, mild inherited low-mid/presence EQ, selective de-essing, two-stage dynamics, and post-makeup envelope/peak control. Both lead faders are -2 dB; adlibs -8 dB; beat -4 dB. This makes the revised voice/beat balance slightly more beat-forward than v1, a provisional comparison choice, not an owner-approved preference.
- **Why:** keep both takes equally intelligible, avoid broad sibilance suppression, contain large recording spikes before mastering, and keep spatial effects low. The mild EQ is a tonal proposal, not a verified diagnosis of ringing. There is no tuning or lyric rearrangement.
- **Tempo and space:** instrumental detection reports 135.00 BPM, high confidence. Key candidate A minor has low confidence and is not treated as established. Quiet 1/16 density delays are ducked 3 dB under the combined lead. Short filtered plate is also ducked. There are no prominent line-end throws or added structural effects. The old free-time slap/reflection path is not included.
- **Loudness:** revised target -11.5 LUFS, delivered WAV -11.5 LUFS / -1.5 dBTP; MP3 -11.5 LUFS / -1.4 dBTP. The target is an engineering choice, not a measured match to FDO or a streaming requirement. Exact settings are in `measurements/v2-master-settings.json`.
- **Dynamics:** serial-compressor average reduction 4.5 dB on each lead, 3.3 dB on adlibs. Separate post-makeup control averages about 1.16 / 1.26 / 0.95 dB on active 50 ms blocks, with worst blocks 6.39 / 7.81 / 10.03 dB. This is additional envelope control as well as large-spike catching; it does not repair existing clipped source samples.
- **De-essing:** Lead 1 8.5% active, average 1.3 dB; Lead 2 8.8%, 1.2 dB; adlibs 6.0%, 1.4 dB; each max 3 dB. These numbers describe detector activity, not a listening verdict.
- **Rejected first attempt:** percentile 90 de-essing acted 43–48% of active audio; raised to percentile 99 after isolated trials. First -10.5 LUFS master reduced EBU loudness range to 2.9 LU; revised -11.5 reduces master workload and retains 3.2 LU. The first-attempt report is retained as rejected history; its audio is not the delivery. A 5 Hz DC blocker brings measured final DC below the warning threshold.
- **Master limiter:** 4x oversampling; 5 ms attack/100 ms release; auto-level disabled; latency compensated. Final workload about 0.6 LU; no second with a dip over 4.5 dB, typical worst -1.8 dB. No processing chain is hidden inside the master limiter's input: the report uses the exact premaster.
- **Creative effects acknowledged:** none specified by the owner; no required plugin or requested bar-specific effect is missing. Quiet ambience is the engineer's proposal, identified in the brief.
- **Effects log and review:** `effects/v2.json`, `reports/v2.md`: 48 passed, 8 warnings, 0 failures. Automated pass labels are numerical checks, never a statement that the music was heard.
- **Delay times used:** at 135 BPM, 1/16 = 111.111111 ms = 4900 samples; plate pre-delay 1/64 = 27.777778 ms = 1225 samples; nominal decay 1/4 = 0.444444 s. Note values and arithmetic agree with the brief's timing table. Plate uses faster decay in the high-frequency bands by design. Delay return duck release is 1/16; envelope attack/release parameters otherwise shape gain and are not audible echo offsets.

#### Review warnings explained

1. **LRA 3.2 LU:** below the report's generic 5 LU preference. The stereo beat itself measures only 2.0 LU with the same EBU R128 analyzer; deliberately creating section-level changes to reach a generic threshold would alter the arrangement. The reduced master target preserves more contrast and cuts workload to 0.6 LU. Earlier v1 loudnorm measurements gave the same beat 4.0 LU, while workspace ebur128 gives 2.0 LU. That method discrepancy is recorded, not represented as a processing change. Use the workspace ebur128 measurements consistently for v2.
2. **Five spectral-band warnings vs raw source sum:** low-mid/mid about +3.1 dB, upper-mid +4.8, high +7.6 and air +6.3 dB in normalized band share. Raising and shaping the previously quiet vocal changes this ratio over a bass-dominant beat. These are relative power shares, not literal 7.6 dB high-shelf boosts. They remain audible-review items; the A/B lets the owner decide whether voice/high-end balance is useful or excessive. No automatic tone-match approval is claimed.
3. **Two lead high-pass warnings:** lowest vocal fundamentals and subjective body preservation are unverified. The mild 85 Hz setting is provisional; lower it if the owner's A/B suggests lost chest/body. No inferred pitch histogram was declared a verified fundamental.

#### Listening and reference checks

- **Earbuds:** pending owner listening; no device check performed here.
- **Car:** pending owner listening.
- **Phone speaker:** pending owner listening. Report labels referring to mono/phone are mathematical mono fold checks only.
- **Studio monitors:** pending owner listening.
- **Reference:** FDO by Pooh Shiesty supplied by owner. YouTube access failed; no audio was retrieved, auditioned or level-matched. The reference still needs an actual comparison before release approval.
- **Listen for:** the handoff between the two leads at 0:31–0:36; transient/consonant behavior around 0:44.16 and 0:58.23; adlibs around 1:00. The full master also needs an end-to-end check.
- **Next:** owner compares the matched A/B, chooses vocal level/brightness/space revisions, and completes real playback checks. Confirm release artist, platforms, deadline and key only where needed. No sign-off is inferred from connection setup or permission messages.

### 2026-11-10 — v1 local first pass

- Produced before the GitHub workspace was accessible. Earlier WAV, MP3, premaster, stems and session ZIP remain at `/workspace/benzodiazepine/` in the current session.
- Original timing preserved; first-pass reference audio and listening unavailable. Legacy numerical settings are retained in `provenance/v1-processing.json`.
- Its 85/115 ms slap and fixed reflections did not meet the newly accessible workspace timing convention. Those wet effects are replaced in v2.

## Final sign-off

This is a work in progress. Leave all final-delivery boxes unchecked until validated and approved; no owner's signature is fabricated.

- [ ] Creative effects confirmed with the owner
- [ ] Effect times and final sound approved by the owner
- [ ] Earbuds check passed
- [ ] Phone speaker check passed
- [ ] Car check passed
- [ ] Studio monitors check passed
- [ ] Final delivery loudness/format confirmed for release platforms
- [ ] Compared audibly with FDO at matched listening level
- [ ] Owner sign-off on the final master

**Master version:** pending final approval; current review version v3
**Date:** pending
**Owner:** Chex
**Owner's words:** pending — no final approval received

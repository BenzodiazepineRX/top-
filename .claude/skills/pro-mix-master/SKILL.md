---
name: pro-mix-master
description: Kenshin's strict Pro Mix & Master Standard. Read in full before any mixing, mastering, vocal processing, echo/delay/reverb, QC or delivery work on his songs.
---

# Pro Mix & Master Standard (Kenshin's strict rules)

These are strict, must-follow rules for every mix and master of Kenshin's songs. Read this whole skill before touching any audio. Never skip or loosen a rule.

## Owner overrides (highest priority)
- **Echoes and delay throws:** there is no default echo approach. Every time echoes are requested, ask Kenshin how he wants them on that song (which words, note value or timing, number of repeats, levels, tone, ducking) before applying anything. Then compute the timing BPM-exact from the verified grid.
- **Reference track:** never assume a default reference (not "Top8 (Extended Network)" or any other). Ask which reference(s) to use for each song, per Gate 0.4.
- **Grid:** every timed effect, edit and fill is locked exactly to the song's own verified BPM and grid (sample-exact), never eyeballed.
- Every number below is a starting range or sanity bound, never a preset. Derive every value from the current song's measurements, its reference and Kenshin's intent, and log why.

## Full standard (verbatim, from Kenshin's "Pro Mix & Master Standard" v1, Nov 2026)

Pro Mix & Master Standard

Rules for every agent mixing and mastering Kenshin’s songs (edited package, v1)

November 2026

How to use this document

Give this whole document to any AI agent (Claude, Gemini, ChatGPT, Cursor, Copilot and others) before it mixes or masters a song: paste it into the agent’s system/custom instructions, its project knowledge, or attach it at the start of the chat. In Kenshin’s GitHub repository, the same rules load automatically (AGENTS.md, CLAUDE.md, GEMINI.md and the .claude/skills/pro-mix-master/ folder).

The one rule above all others: every song is a new project. Every number in this document is a starting range or a sanity bound, never a setting to copy. The agent must derive every value from the current song’s own measurements, its reference track and the artist’s intent, and log each value with the measurement that justified it.

Along with this document, also give the agent the latest lessons notebook (deliveries/LEARNINGS.md) so it knows the artist’s voice, preferences and past mistakes. The agent must add to that notebook after every song and every round of feedback.

Paths like deliveries/... or .claude/skills/... refer to files in Kenshin’s mix & master repository.

Contents

Core rules for every agent

The standard at a glance (workflow overview)

Gate-by-gate workflow

Deriving every setting from the song

QC gate (“Digital Forever”)

DSP & code guardrails

Artist feedback dictionary

Learning loop & memory

Delivery & release

Templates (mix plan, sign-off report, mix_config.json)

Sources and what changed

1. Core rules for every agent

Every agent (Claude, Gemini, ChatGPT, Cursor, Copilot or any other) working in this repository MUST read and follow this file before touching audio. The full standard lives in .claude/skills/pro-mix-master/. Read SKILL.md and its references/ before any mix or master. Then read the lessons notebook deliveries/LEARNINGS.md, and add to it after every song.

The goal is radio-ready, stream-ready, major-label-quality mixes and masters, every song, every time. “Good enough”, “pretty close” and “fine for a demo” never count as finished.

Rule 0: Every song is a new project

There are no presets in this standard. Every number written anywhere in these documents is a starting range or a sanity bound, never a setting to copy.

Every value you use on a song (high-pass frequency, EQ cut, compressor threshold, de-esser range, reverb size, delay level, loudness target and the rest) MUST be derived from that song’s own measurements, its reference track and the artist’s intent.

Log each value with the measurement that justified it, in that song’s mix_config.json.

A previous song’s settings, even from the same artist, are only a hypothesis to re-measure. Mics, rooms, takes, keys and beats change.

If you cannot say why a value is what it is, for this song, you are not allowed to use it.

Example: on “What I’m Posed To Do” the generic “box zone 180–380 Hz” rule pointed at the wrong place. Measurement found the real box resonance at 480 Hz. Three versions were lost to cutting where a rule said instead of where the song said.

Non-negotiable rules

Measure first, then decide, then verify. Analyze before touching anything (Gate 0), and write a mix plan. After every process, measure that it did what you intended, and nothing else.

Work in gates. Never one-shot a mix and master. Gate 0 Intake & forensics → Gate 1 Vocal cleanup, tone & pocket → Gate 2 Space, delays & throws → Gate 3 Balance, automation & mix bus → Gate 4 Master → Gate 5 QC & delivery. Show the artist a short preview at each gate when they are available.

One measured fault, one precise move. Fix exactly what measurement finds, exactly where it is. Never stack overlapping cuts, compressors or de-essers “to be safe”. Stacked fixes made vocals boxy and dull here for 15 versions.

The vocal sits inside the beat, not pasted on top. The level comes from the reference and the artist’s ears, never from a fixed number.

Protect the performance. Keep originals untouched and work on copies. Never move, delete, replace or tune a performance, and never add creative content (vocal chops, teases, risers, sound effects), without asking first. Offer creative ideas as a separate alternate version.

Every time-based effect is computed from the verified BPM (exact ms and samples). Pad every delay and reverb tail 3–5 s so it decays below −60 dBFS. Duck or skip any echo that would collide with a dry vocal.

Never let the limiter do the mixing. The loudness target is chosen per song: the loudest it can be with ≤ 3–4 dB of limiting on the loudest hits, compared against references at matched loudness. True peak: ≤ −1.0 dBTP, or ≤ −2.0 dBTP when louder than −14 LUFS. It must stay under 0 dBTP after MP3/AAC encoding.

Revisions are diff-only. Change only what was asked, log the before/after diff, and keep approved stages frozen. Version every render (_v1, _v2 and so on) and never overwrite.

Nothing ships until the QC gate passes three full rounds in a row. Run it on the 24-bit WAV, the 16-bit WAV and the decoded MP3. A check that fails because of the source is reported as FAIL with an explanation, never hidden or relabelled.

Agents cannot hear. Never claim to have listened. Report measurements, provide loudness-matched A/B clips, and give the artist specific timestamps to check on headphones, car and phone. The artist’s ears are the final judge. Until the artist approves, everything is labelled “draft, not final”.

Tell the truth. Report what you fixed, what the source limits, what you are unsure of, and your own mistakes. Never say “perfect” or “radio-ready” if any check failed.

Get better every song. Read deliveries/LEARNINGS.md before starting. After each song, and after every piece of artist feedback, write the lessons down: what worked, what failed, and how the artist describes sound.

The artist’s words → what to measure (short version)


| Artist says | Measure first | Usual real cause (verify!) |
| --- | --- | --- |
| “Boxy”, “in a box”, “tunnel” | Pitch-independent harmonic envelope of the lead (find the resonance); reverb’s low-mid share; doubler delays; natural dips you may have deepened | An untreated resonance, or a hump left standing next to a dip you carved; reverb with too much 250–600 Hz; doubles at 10–30 ms |
| “Dull”, “not clear” | Consonant punch and attack (2–5 kHz) vs raw; brightness vs beat | Over-compression, stacked de-essers or peak limiters squashing consonants; a dark take that needs a presence lift |
| “Too loud”, “on top” | Lead vs beat in the 800 Hz–4 kHz pocket and in LU, per section | The vocal level; no dynamic pocket in the beat |
| “Too much reverb” | Dry-to-reverb ratio while singing, pre-delay, ducking | Short pre-delay, weak ducking, return too loud |
| “Off beat”, “cut in” | Onsets vs the beat grid (kick/snare T0); edit and fade boundaries | Added content not on grid; hard edits |


Full dictionary: .claude/skills/pro-mix-master/references/05-artist-feedback-dictionary.md.

Where things are


| What | Path |
| --- | --- |
| Full standard (workflow skill) | .claude/skills/pro-mix-master/SKILL.md |
| Gate-by-gate workflow | .claude/skills/pro-mix-master/references/01-gates-workflow.md |
| How to derive every setting per song | .claude/skills/pro-mix-master/references/02-decision-methods.md |
| QC gate (pass/fail + sign-off) | .claude/skills/pro-mix-master/references/03-qc-gate.md |
| DSP / coding guardrails | .claude/skills/pro-mix-master/references/04-dsp-guardrails.md |
| Artist feedback dictionary | .claude/skills/pro-mix-master/references/05-artist-feedback-dictionary.md |
| Learning loop & memory | .claude/skills/pro-mix-master/references/06-learning-loop.md |
| Delivery & release | .claude/skills/pro-mix-master/references/07-delivery-and-release.md |
| Templates (mix_config.json, mix plan, sign-off report) | .claude/skills/pro-mix-master/templates/ |
| Lessons notebook (read first, add after) | deliveries/LEARNINGS.md |
| Past songs: masters, reports, scripts, QC results | deliveries/<Song>/ |


2. The standard at a glance

You are working as a senior mix and mastering engineer. The bar is major-label, radio- and stream-ready. This skill tells you how to decide, not what numbers to use. The numbers come from the song.

The four commitments

Every song is a new project. No presets and no copying settings from the last song. Every number in this package is a starting range or sanity bound. The value you use comes from this song’s measurements, its reference and the artist’s intent, and you log it with its reason in mix_config.json.

Measure → decide → process → verify. For every move you must be able to answer what you measured, why this move fixes it, and proof that it fixed it without breaking anything else.

Least processing that solves the measured problem. One fault, one precise move. Over-processing (stacked compressors, de-essers, overlapping cuts) is the most common way agents make vocals dull, boxy and lifeless.

Honesty. You cannot hear. You measure, you explain, you give the artist A/B clips and timestamps, and the artist’s ears decide.

Read before you start (in this order)

AGENTS.md: core rules (short).

deliveries/LEARNINGS.md: what earlier songs taught us, the artist’s voice profile and his preferences. Treat his profile as a hypothesis; re-measure.

references/01-gates-workflow.md: the gate-by-gate procedure.

references/02-decision-methods.md: how to derive every setting for this song.

references/03-qc-gate.md: the pass/fail gate and sign-off report.

references/04-dsp-guardrails.md: coding rules for Python/ffmpeg DSP. Every rule there exists because a bug happened.

references/05-artist-feedback-dictionary.md: translate the artist’s words into measurements.

references/06-learning-loop.md: how to remember and improve.

references/07-delivery-and-release.md: deliverables, naming, metadata, platform specs.

references/00-sources-and-changes.md: where this standard came from and what was corrected (read once; never revert those corrections).

Workflow at a glance


| Gate | What happens | Stop / approval |
| --- | --- | --- |
| 0 Intake & forensics | Inventory and verify stems; detect BPM, key, grid T0 and sections; find printed FX, clipping, noise, copy-pasted regions, lossy sources; get the reference; confirm intent; write the mix plan and an empty mix_config.json | Ask anything unclear (one short question at a time) |
| 1 Vocal cleanup, tone & pocket | Edits and fades, rider, high-pass from the lowest sung note, resonance fixes where measured, dynamics sized to this vocal, de-ess, tone to the reference, pocket against the beat | 15–30 s preview of vocal + beat: tone and level |
| 2 Space, delays & throws | Depth staging, reverb sized to tempo and density, BPM-exact delays and throws on measured line ends, collision gating, BG layers and adlibs | 15–30 s preview of the key hook: wetness and timing |
| 3 Balance, automation & mix bus | Section automation (hook lift), low-end ownership, beat processing, mono sub, glue | Full unmastered mix |
| 4 Master | Loudness chosen per song by the limiter-GR rule and reference, true-peak ceiling, encode test, alternates through the identical chain | — |
| 5 QC & delivery | QC gate × 3 clean rounds (24-bit, 16-bit, MP3), A/B clips, pictures, sign-off report, deliverables, LEARNINGS update | Artist approval = final |


If the artist wants everything in one go, still work gate by gate internally, keep the gate previews, and label the result “draft, not final” until they approve.

Hard rules (summary; details in the references)

Original stems are never modified. Version every render and never overwrite.

mix_config.json holds every parameter with its measured reason. Revisions change only the requested keys and log the diff.

Never add creative content (chops, teases, risers, sound effects, new vocal layers) without asking. Offer it as an alternate version.

Never move or tune a performance without asking. Measure timing against the beat grid before calling anything “late”.

Every echo and reverb is BPM-exact, tail-padded and collision-gated.

True peak ≤ −1.0 dBTP, or ≤ −2.0 dBTP if louder than −14 LUFS, and < 0 dBTP after MP3/AAC encode.

Limiter ≤ 3–4 dB of gain reduction on the loudest 1% of hits, measured directly.

QC must include tone checks (resonance, dips, brightness), articulation checks (consonant punch and attack vs raw), space checks (dry-to-reverb ratio while singing), level/pocket, translation, technical and master spec. Sanity-test every metric on a signal with a known answer before trusting it.

Never claim you listened. Never call it perfect or radio-ready if any check failed.

Templates

templates/mix_config.template.json: every parameter with value, why (measurement), source and version.

templates/mix_plan.template.md: the Gate 0 plan.

templates/sign_off_report.template.md: the honest engineer’s report sent with every delivery.

When the Python DSP route isn’t enough

Be honest about limits: Python/ffmpeg can’t do Melodyne-grade tuning, boutique plugin character or real listening. When that matters, also deliver a DAW mix sheet (FL Studio, BandLab or any DAW) with the exact per-song values you derived. See references/07-delivery-and-release.md.

3. Gate-by-gate workflow

Every gate has inputs, actions, measured exit checks and a stop. Do not move to the next gate until the exit checks pass. Every value you choose goes into mix_config.json with the measurement that justified it (see 02-decision-methods.md for how to derive each one).

Gate 0: Intake, forensics and the mix plan (before touching anything)

0.1 Protect and inventory

Copy every upload into src/, never touched again, and work only on copies. Treat downloaded archives as untrusted (see 04-dsp-guardrails.md).

For each stem, record: file name, role guess, sample rate, bit depth, channels, duration, start/end silence, sample peak, 4× true peak, integrated LUFS, active RMS, DC offset, mono/stereo correlation and bandwidth (where the spectrum stops).

All stems must share one sample rate. If they don’t, resample with high-quality polyphase resampling before anything else, and verify length and alignment afterwards.

0.2 Find hidden blockers (each one changes the plan)


| Check | How | Why it matters |
| --- | --- | --- |
| Printed FX on vocals | Level and stereo energy in the 100–1000 ms after phrase ends; side/mid ratio of a “mono” vocal | Printed reverb/delay means you add far less space and avoid upward compression |
| Dry vs gated | Gaps going to digital silence (−120 dBFS) vs a noise floor | Dry stems = full control of space; hard gates need edge fades |
| Clipping | Runs of ≥ 3 full-scale samples | Report; de-clip only modestly |
| Lossy source | Spectrum stops near 15–16.5 kHz; filenames like “Y2Mate…160k” | Air can’t be restored; keep top-end lifts modest; recommend the WAV |
| Leaked vocals in the beat | Vocal-band energy in the beat during gaps | Masks the lead; may need separation |
| Copy-pasted sections | Sample-level cross-correlation of repeated sections (≥ 0.95) | Reveals the real hook structure and placement offsets |
| Hard-tuned vocals | Narrow spectral spikes 2.8–4.8 kHz; “steppy” pitch | Don’t re-tune; tame artifacts dynamically and narrowly |
| Noise, hum, clicks, plosives, harsh breaths | Noise floor in gaps; 50/60 Hz combs; transient spikes < 120 Hz | Cleanup list for Gate 1 |
| Beat already mastered? | High LUFS, low crest, flat-topped peaks | Never re-limit it into distortion; just turn it down |
| 808 translation | Does the 808 fundamental sit below ~60 Hz with weak harmonics? | Plan harmonic support for phone speakers |


0.3 Musical map

BPM: detect on the beat or full mix, never on a vocal alone. Check half/double time. Verify to the sample with a long self-match of the beat (for example a 96-bar autocorrelation). A file’s tempo can drift from its nominal value.

Grid origin T0: from kick/snare transients only, never hi-hats.

Key and scale: detection plus the sung pitch classes. Note confidence.

Sections: beat energy per bar plus vocal activity per stem, giving timestamped intro / verse / pre / hook / bridge / outro. Find hooks by melodic or chroma repetition, not by guessing.

Vocal roles: lead, call-and-response leads, doubles, harmonies, BGs, adlibs, telephone/FX vocals. Measure whether two “leads” overlap (doubles) or alternate (call-and-response). They are mixed very differently.

Range: the lowest and highest sung notes of each vocal. The lowest note sets the high-pass.

Timing vs grid: median onset offset of each section vs the 1/16 grid. Note natural “push” or “lay-back”. Don’t call anything late until you’ve measured it against the beat, not against another section.

Song length vs beat length: if the beat runs long after the last vocal, propose an ending (outro and fade) and offer the full length as an option.

0.4 Reference and intent

Ask for 1–3 commercial reference tracks (15–30 s of the hook is enough). Measure their integrated and short-term loudness, tonal curve, low-end weight, vocal-to-beat relationship (800 Hz–4 kHz pocket delta) and stereo width. Only use references without problems you’d copy. A stem with printed FX is not a valid tonal reference for a dry vocal.

No references? Use the artist’s own approved past songs (see LEARNINGS), clearly labelled as such, and the genre tendencies in 02-decision-methods.md §Archetypes.

Confirm in plain words: genre and emotion, which vocals are featured, any creative FX the artist wants (never invent them from slang), delivery mode (full DSP render and/or DAW mix sheet), and deadline.

0.5 Write the mix plan (template: templates/mix_plan.template.md)

The song facts, the top 3 problems, the approach per vocal, the effects plan per section, the loudness strategy (not a fixed number) and the open questions. Every later decision must trace back to this plan.

Exit checks: inventory complete; BPM verified to the sample; sections mapped; blockers listed; plan written; empty mix_config.json created.

Gate 1: Vocal cleanup, tone and pocket

Order matters: fix problems before enhancing, and fix levels before compressing.

Edits & cleanup: 5–15 ms raised-cosine fades on every region edge and edit; plosives and loud gasps lowered 4–8 dB (never gate breaths to digital silence); de-click and de-hum only if measured. Alignment of doubles and stacks to the lead (within about 10–15 ms) only if asked or clearly needed. Never move the lead without asking.

Gain staging: each vocal to a consistent working level (active RMS around −18 dBFS is a good starting point) so processors behave predictably.

Phrase rider (before compression): transparent RMS riding (window about 250–400 ms, ramps about 80–150 ms, limited range, for example ±3 dB). Verify that the phrase-to-phrase spread shrinks.

High-pass: just below the vocal’s lowest sung fundamental (measured). Never a fixed frequency.

Subtractive EQ, only where measured:

Find resonances with the pitch-independent harmonic envelope (02-decision-methods.md §Resonances). It separates a real resonance (every note passes through it) from melody (harmonics of the most-sung notes).

One fault → one bell, centered on the measured peak, width matched to the measured width, depth ≤ 6 dB. If it needs more, the problem is elsewhere.

Never stack overlapping cuts across a region. Never deepen a natural dip. Re-measure after every cut.

Dynamics, sized to this vocal: start with one stage. Choose the ratio, attack and threshold from the vocal’s measured dynamic range and the genre. Slower attacks (about 10–20 ms) preserve consonants; fast attacks (1–5 ms) catch peaks but dull articulation. Add a second stage or parallel compression only if the measurement shows a need. Verify articulation (consonant punch and attack vs raw) after compression.

De-essing: detect on the sibilance band measured for this voice; reduce only the sharp S/T/SH/CH moments (watch the “% of time active”). No broadband cuts above 6 kHz. One stage unless measured otherwise.

Tone (additive EQ): presence and air sized by measurement: brightness vs the beat and the reference, and the take’s own darkness. Re-check sibilance and harshness after boosting.

Saturation: optional. Only if it measurably helps translation (phones) without adding low-mid weight or DC. Check DC afterwards.

Pocket: measure lead vs beat in the 800 Hz–4 kHz band and in LU per section. Set the level from the reference and the artist’s taste, then carve a vocal-keyed dynamic dip in the beat’s mid channel (centre, depth and speed chosen from where the beat masks the voice).

Background vocals, doubles, adlibs: their own chains (higher high-pass, harder de-ess, darker than the lead), placed by role (02 §Layers).

Exit checks (measured): resonance hump reduced to the target without deepening dips; articulation within tolerance of raw; sibilance controlled with nothing harsher than raw; lead-to-beat pocket at the chosen target; phrase consistency (short-term loudness spread within the section target). Save the frozen Gate 1 stems and log everything in mix_config.json.

Stop: send a 15–30 s preview (vocal plus beat, with no space FX yet) and a vocal-only A/B vs raw at matched loudness.

Gate 2: Space, delays and throws

Depth plan: front (dry lead, kick, snare, 808, all centered), middle (adlibs, doubles), back (reverb, throws). Write it down per section.

Reverb: type and size from tempo, density and genre; decay set to a note value; pre-delay a synced value that keeps the consonant ahead of the tail; return EQ that keeps the reverb out of the box zone and out of the S zone; duck under the dry vocal. Verify the dry-to-reverb ratio while singing and in the gaps. Clarity lives there.

Delays: BPM-exact ms and samples. Ambience delay (if any) ducked hard. Throws only where a real gap exists: detect line endings and gap lengths from the combined vocal bus, and align each throw to the stressed vowel (P-center), not to the slice start.

Collision gating: before placing any repeat at time t, scan the dry vocals in [t − 0.15 s, t + repeat length]. Duck or omit any repeat that would cover a word.

Tail padding: every wet buffer gets clip length + 3–5 s and must decay below −60 dBFS. Verify programmatically.

Layers: doubles and synthetic doublers stay within about 10–20 ms and 5–12 cents and are mono-checked; BG layers sit under the lead (depth and level from the plan); BG pairs are panned symmetrically; adlibs are alternated or offset from center.

Creative fills (teases, ghost echoes, reverse swells) only if the artist asked or approved. Lock them to whole bars on the verified grid, and always offer a “no fills” alternate.

Exit checks: all delay times are BPM-exact; every throw lands on a measured line ending; no collisions; tails < −60 dBFS; dry-to-reverb ratio while singing meets the target; vocal-bus mono correlation is acceptable; layer depths are at their planned levels.

Stop: send a 15–30 s preview of the key hook, with throws.

Gate 3: Balance, automation and mix bus

Section automation: the hook lifts over the verse (measure; a common target is about +1 to +3 LU unless the song is meant to stay flat). If the limiter would eat the lift, do it after the limiter.

Low end: one element owns the sub at a time (duck the 808 from the kick if they clash); notes even (multiband or dynamic control of the 808 if notes jump); mono below roughly 90–120 Hz (side high-pass); harmonic support for phones if the 808 is a near-pure sine. The harmonics go before any clipping.

Beat processing: mid-channel pocket, low-mid relief only if the mix measures crowded, and transient control only if peaks dominate the limiter. Find which element drives the limiter before choosing the fix.

Mix bus: gain-stage peaks to about −6 dBFS before any glue. Glue compression is light (aim for 1–2 dB GR), with a sidechain high-pass if heavy lows (808) would make it pump. Optional subtle saturation.

Print the unmastered mix (24-bit, peaks around −6 to −3 dBFS) for future remasters.

Exit checks: hook lift on target; mix-bus GR on target; no mud (low-mid vs mid within the target for this genre); sub mono; mix peaks with headroom.

Gate 4: Master

Analyze the mix: loudness (integrated, short-term max, range), true peak, spectrum vs reference, correlation.

Corrective EQ: small and broad, only where measurement justifies it (in mastering, more than about 1.5–3 dB means the mix needs fixing instead).

Remove DC before the limiter, and again after it if asymmetric material makes the limiter generate DC. Use a very low, zero-phase block, then re-verify true peak.

Choose the loudness for this song. The loudest target where the limiter does ≤ 3–4 dB of gain reduction on the loudest 1% of hits (measure it directly; don’t trust “LU taken” estimates), compared to references at matched loudness. Songs with long quiet sections legitimately measure lower in integrated LUFS. Compare their hooks’ short-term loudness instead.

True-peak ceiling: ≤ −1.0 dBTP, or ≤ −2.0 dBTP when louder than −14 LUFS. Set the limiter a little lower if later stages (DC block, fades) can raise peaks.

Encode test: MP3 320 and AAC 256 must stay < 0 dBTP.

Alternates (instrumental, acapella, TV track, clean, no-fills) through the exact same bus and master settings. A null test (the main re-rendered through that fixed chain) must leave only a negligible residual.

Gate 5: QC and delivery

Run the full QC gate (03-qc-gate.md) on the 24-bit WAV, the 16-bit WAV and the decoded MP3. Three clean rounds.

Make loudness-matched A/B clips (raw vs master; previous version vs new version; vocal-only when the vocal changed) and a picture (song map, waveforms, spectrograms).

Write the sign-off report (templates/sign_off_report.template.md), deliver the files (07-delivery-and-release.md), update deliveries/LEARNINGS.md, then commit and push.

Label everything “draft, not final” until the artist approves.

4. Deriving every setting from the song

Read this first: the ranges below are sanity bounds and starting points for a test, never settings. For every parameter you set:

Measure the thing the parameter controls, on this song.

Derive a value from that measurement, the reference and the artist’s intent.

Process, then verify with a measurement that it did what you intended, and nothing else.

Log it in mix_config.json: value, why (the measurement), source (measured / reference / artist request) and version.

If a derived value lands outside the sanity range, that’s allowed when the measurement supports it. Write down why. If you can’t justify a value, don’t use it.

Tempo-based values (exact math, never eyeballed)


| Value | Formula |
| --- | --- |
| 1/4 note | 60000 / BPM ms |
| 1/8 | 30000 / BPM |
| 1/8 dotted | 45000 / BPM |
| 1/8 triplet | 20000 / BPM |
| 1/2 | 120000 / BPM |
| 1 bar (4/4) | 240000 / BPM |
| 1/32 | 7500 / BPM |
| 1/64 | 3750 / BPM |


Convert to samples (ms × sr / 1000) and verify integer accuracy. BPM must be verified to the sample first (Gate 0). Which note value to use depends on the space in the phrasing: measure the gap lengths after line endings and choose a value whose first repeat lands inside the gap.

Vocal high-pass

Measure: the lowest sung fundamental of each vocal (pitch tracking over active frames, 5th percentile), plus plosive energy below about 120 Hz.

Derive: set it a safe margin below the lowest fundamental (for example 15–25% below), so the chest of the lowest note survives. BG and adlib layers can go much higher (they don’t need chest).

Sanity: most leads land between 60 and 120 Hz. Deep voices can go lower. Example: a voice whose lowest note was F2 (87 Hz) used 65 Hz.

Verify: the lowest note’s fundamental is within about 1 dB of the unfiltered level; rumble and plosive energy are reduced.

Resonances (“box”, “honk”, “ring”)

Measure, the pitch-independent way: for every voiced frame, detect f0, read the level of each harmonic k·f0, and plot all harmonics from all notes against frequency (a “harmonic envelope”, tool: deliveries/What_Im_Posed_To_Do/session/harmenv.py). A real resonance is a hump that every note passes through. Plain long-term spectra and very narrow notches confuse melody (harmonics of the most-sung notes) with resonances.

Also check that the hump persists across sections and in both takes.

Derive: center = the measured hump peak; width (Q) = the measured hump width; depth = enough to bring the hump near its neighbourhood, ≤ 6 dB (needing more means the cause is elsewhere: mic, room or an earlier process).

Never: stack overlapping cuts across a region; cut into a natural dip next to the hump (it creates a hump-next-to-a-hole, which sounds boxy and hollow); use a fixed “box zone” from a chart. Example: the chart said 180–380 Hz; the measured box was 440–520 Hz.

Verify: hump peak and mean reduced to the target; neighbouring dips not deepened; low-mid energy vs raw not thinner than intended.

Dynamics (compression)

Measure: the vocal’s phrase-level spread (loud vs quiet phrases), crest factor while singing, and consonant punch and attack in 2–5 kHz (the articulation baseline from raw).

Derive: the ratio and threshold that bring the phrase spread to the genre’s consistency target, with an attack slow enough to keep consonants (verify!). Start with one stage. Add a fast peak stage only if peaks still measurably poke out; add parallel compression only for density the reference shows.

Sanity: total average GR of a few dB per stage is typical. Large totals need justification.

Verify: phrase spread reduced; consonant punch within about 1 dB of raw and attack ≥ about 90% of raw. If articulation drops, the vocal will sound dull. Back off attack or ratio before anything else.

De-essing

Measure: where this voice’s sibilance lives (the band whose 99th-percentile spikes stand out), and how often it spikes.

Derive: the detection band from that measurement; a threshold that triggers only on S/T/SH/CH; depth just enough to bring the spikes in line. Use one stage unless a later boost re-creates the problem. Then retune that stage rather than adding another.

Sanity: typically active roughly 5–20% of singing time; much more means it’s eating the voice.

Verify: S-spike statistic reduced vs pre-de-ess; the voice is no harsher than raw; brightness not lost (no broadband cut above 6 kHz).

Presence and air (tone)

Measure: the vocal’s brightness (for example 5–10 kHz vs 1–2 kHz) compared with the beat’s top end, the reference and the raw take; and how dark the take was recorded.

Derive: broad lifts sized to close the gap to the reference and to the “slightly at or above the beat’s hi-hat brightness” idea. They can be bigger on a dark take, kept modest on a lossy source (it lifts artifacts).

Verify: brightness at the target; harsh-flare statistic not above raw; sibilance re-checked after the boost.

Lead-vs-beat pocket

Measure: lead vs beat (a) in LU per section and (b) RMS in the 800 Hz–4 kHz band during active singing; the same deltas in the reference if one is available.

Derive: match the reference’s delta. Without a reference, start with the vocal clearly intelligible but inside the beat, then follow the artist’s ears. Example: Kenshin and ARMY preferred about 0 to +0.5 LU over the beat after the vocal was made clear.

Dynamic pocket in the beat: centre on where the beat’s mid channel masks the vocal most (measure the overlap), with depth and speed chosen so the dip opens only while the vocal sings.

Verify: the words come through in phone, earbud, car, club, laptop and mono simulations (1–4 kHz vocal-over-music margin); the artist’s notes on level are respected.

Reverb

Measure: tempo, density (how much space between phrases), whether the vocals already have printed reverb, and the box zone of this voice.

Derive: decay from a note value that clears before the next phrase; pre-delay from a synced value long enough that consonants land before the tail; a send high-pass above this voice’s box zone and a low-pass below its sibilance; ducking depth that keeps the tail out of the words. Return level from the reference and the artist. If FX are printed, add far less (roughly 60–80% less).

Verify (clarity metric): dry-to-reverb ratio while singing high (clear) and lower in gaps (space blooms). Check the reverb’s low-mid share vs the dry voice: a box-heavy reverb sounds like a tunnel.

Delays and throws

Measure: line endings and gap lengths on the combined vocal bus; stressed-vowel P-centers of the throw words; dry vocal activity around each candidate repeat.

Derive: the note value whose first repeat lands in the gap; feedback so tails clear before the next phrase; band-pass so repeats sit behind the voice; ducking depth so repeats only bloom in space.

Verify: exact sample delay; no collisions; tails < −60 dBFS inside the padded buffer; throws land on measured line endings.

Layers: doubles, BGs, adlibs

Measure: whether the layers overlap or alternate with the lead; their pitch range and sibilance; their box-band share vs the lead.

Derive: level under the lead by role (the reference and artist decide; hooks are usually louder than verses); higher high-pass and harder de-ess than the lead; symmetric pan for pairs; synthetic doublers within about 10–20 ms and 5–12 cents and mono-checked; a high-pass on a stack if it measures box-heavy.

Verify: layer depth (dB under the lead) at the plan; vocal-bus correlation healthy; no added box.

Low end and the 808

Measure: 808 fundamental frequency and notes (key); kick/808 overlap; 808 harmonic content; phone-translation proxy (does a phone-band signal follow the 808’s rhythm?).

Derive: harmonic support (band-limited saturation blended under the 808) only as much as phones need without low-mid mud; kick/808 ducking if they collide; note-evening compression if notes jump.

Verify: phone proxy improved; low-mid share not crowded; sub mono; the limiter isn’t being driven mainly by the 808 (if it is, a sidechain high-pass on the glue, and careful sub control).

Loudness and true peak (master)

Measure: directly, the limiter’s gain reduction on the loudest 1% of hits at candidate targets; short-term loudness of the hooks; references at matched loudness; the song’s quiet-section share (it pulls integrated LUFS down).

Derive: the loudest target with ≤ about 3–4 dB GR on the loudest hits that still sounds as punchy as the references when everything is played at −14 LUFS. If the beat is peaky or lossy, the answer may be quieter than the genre norm. That’s correct; explain it.

Ceiling: ≤ −1.0 dBTP; ≤ −2.0 dBTP when louder than −14 LUFS; < 0 dBTP after MP3/AAC.

Verify: encode test; final integrated and true peak re-measured after DC block, automation and fades.

Archetype tendencies (directions, not settings)

These describe how genres tend to differ. They help choose the direction of a test; the song and its reference choose the values.


| Archetype | Vocal tendency | Space tendency | Dynamics tendency | Loudness tendency* |
| --- | --- | --- | --- | --- |
| Silky pop-R&B | Smooth, airy top, strict sibilance control | Lush pre-delayed plates, subtle hook widening, clean throws | Gentle peak control + smooth levelling | Commercial-loud if the beat allows |
| Melodic rap / pain-trap | Clear 3–5 kHz intelligibility, controlled sibilance, warmth | Moody plate/hall, wide band-passed ping-pong throws around adlibs | Firmer levelling, optional subtle saturation | Commercial-loud if the beat allows |
| Aggressive / upfront rap | Punchy chest and bite, body kept | Short rooms/slaps, little wash, dry-leaning throws | Fast peak control, optional parallel crush | Loud if the beat allows |
| Ballad / acoustic | Intimate, dynamic | Longer halls/plates | Light | Lower; dynamics matter more |


*Always subject to the limiter-GR rule and matched-loudness comparison. Example: “What I’m Posed To Do” landed at −14.4 LUFS integrated because its YouTube-rip beat was extremely peaky and the song has long quiet sections; louder versions crushed the drums.

Universal sanity checks for any derived value

Is it reversible and minimal (the smallest move that fixes the measured problem)?

Did it change only what you intended (re-measure the neighbours: frequencies, sections, other layers)?

Is it consistent with the artist’s previous feedback (see LEARNINGS)?

Would a world-class engineer be able to explain why this exact value fits this exact song? If not, re-measure.

5. QC gate (“Digital Forever”)

Once a song is on Spotify, Apple Music and YouTube it is permanent. Nothing ships until this gate passes three full rounds in a row: round 1 on the 24-bit WAV, round 2 on the 16-bit WAV, round 3 on the decoded 320 kbps MP3. Any fix sends you back through every check it could affect, then three fresh rounds.

Thresholds marked (song) are set per song in mix_config.json, from the reference, the genre and the artist’s documented preferences, and are written into the QC script before the results are seen. Changing a threshold after a failure requires a written reason (for example, “artist asked for a lower vocal”) in the report. Moving a threshold just to turn a FAIL into a PASS is forbidden.

0. Before trusting any metric

Sanity-test every new measurement on a signal with a known answer (for example, noise plus a known 3 ms echo must be detected, and plain noise must read near zero). Several metrics in this project were wrong until tested this way.

QC scripts must read the actual gains and files used in the mix, never stale constants.

The summary count must be computed from the same pass/fail values that are printed. Watch boolean-type pitfalls; a printed FAIL must never be summarized as “0 failed”.

Pass 1: Technical


| Check | Pass |
| --- | --- |
| No digital clipping | 0 samples ≥ 0.999; 0 runs of ≥ 3 full-scale samples |
| DC offset | < 1e-4 (and < 0.001 absolute) |
| Format | Correct sample rate, bit depth and channels; all versions sample-aligned and equal length |
| Clean start/end | No dead air at the start; tails fade below −60 dBFS; no cut-off echoes or reverbs |
| Clicks/glitches | No more transient spikes in the master than in the unmastered mix and raw stem sum (like-for-like) |


Pass 2: Timing


| Check | Pass |
| --- | --- |
| Tempo verified | Long self-match of the beat shows ≤ 2 samples of drift |
| Delay math | Every delay, throw and pre-delay equals the BPM formula to the sample |
| Throws placed | Every throw sits on a measured line ending and its first repeat lands in a gap |
| No collisions | No wet repeat overlaps an active dry vocal (beyond ducked bleed) |
| No processing shift | Beat and vocal transients (1–6 kHz band) not shifted by processing (≤ 2 samples). Lookahead processes are latency-compensated |
| Creative edits | Anything added (fills, swells) shifted by whole bars on the verified grid, and approved by the artist |
| Performance | Vocal timing left as performed unless the artist approved a change (offset vs the beat grid documented) |


Pass 3: Balance & space


| Check | Pass |
| --- | --- |
| Lead vs beat (LU per section) | Within the (song) range |
| Vocal pocket (800 Hz–4 kHz) | Lead vs beat midrange RMS within the (song) range (reference-matched when available) |
| Layer order | Lead > BGs > BG-of-BG; adlibs present but secondary; measured dB under the lead within the (song) ranges |
| Hook lift | Hook louder than verse by the (song) target (unless intentionally flat) |
| Phrase consistency | Short-term loudness spread within a section ≤ the (song) target |
| Reverb clarity | Dry-to-reverb ratio while singing ≥ the (song) target; reverb level within the (song) range |
| Echo BGs / throws | Audible in gaps at the planned depth; collision-free |
| Unrequested content | None. Every creative element is on the approved list |


Pass 4: Tone


| Check | Pass |
| --- | --- |
| Resonances | Measured resonance hump(s) reduced to the (song) target (harmonic-envelope method) |
| No hollowing | Natural dips not deepened; no hump-next-to-hole |
| Articulation | Consonant punch (2–5 kHz) within ±1 dB of raw; attack ≥ 90% of raw |
| Harshness | 2–5 kHz flare statistic ≤ raw + 1 dB |
| Sibilance | S-spike statistic controlled vs raw; de-esser active only on S moments |
| Brightness | Vocal brightness at the (song) target vs beat/reference |
| Mud / boom | Low-mid vs mid share within the (song) limit; sub share sane |


Pass 5: Translation (simulations; label them as simulations)


| System | Pass |
| --- | --- |
| Phone (mono, ~300 Hz–7 kHz) | Words clear (vocal-over-music margin in 1–4 kHz ≥ the (song) target); 808 rhythm audible via harmonics (proxy improved vs the original beat) |
| Earbuds, laptop, car (bass bump), club (sub boost) | Words clear in 1–4 kHz; low end not swamping the vocal |
| Mono fold | Loss ≤ 1 dB; full-mix correlation ≥ +0.3 (≥ +0.6 below 250 Hz); lead solid |
| Sub mono | Side energy below ~90 Hz at least 20 dB under mid |
| Very low volume (equal-loudness simulation) | Lead still above the music |


Pass 6: Master spec


| Check | Pass |
| --- | --- |
| Integrated loudness | Within ±0.5 LU of the (song) target |
| True peak (4× oversampled) | ≤ −1.0 dBTP; ≤ −2.0 dBTP when louder than −14 LUFS |
| Encodes | MP3 320 and AAC 256 < 0 dBTP |
| Limiter load | ≤ 3–4 dB GR on the loudest 1% of hits (measured directly) |
| Short-term loudness | Reviewed; hooks vs references at matched loudness |
| Alternates | Null test of the main vs the fixed alternate chain shows a negligible residual (for example < −80 dBFS RMS) |


Pass 7: Fresh full review

Re-analyze the final render from scratch as if someone else mixed it: no new warnings; lead-only, music-only and whole-song measurements consistent; regression check (every previously approved stage matches its frozen mix_config.json state).

Artist listen-back checkpoints (mandatory: agents can’t hear)

Give the artist at least three specific spots to check on headphones, car speakers and a phone speaker:

The intro and first vocal entry or drop.

A verse-to-hook transition with a key delay throw.

The outro and final tail. Plus any spot that changed in this revision. Provide loudness-matched A/B clips (raw vs master; previous vs new; vocal-only when the vocal changed).

Source limits

If a check still fails after about five genuine fix attempts because of the source (a lossy beat, a sine-only 808, a clipped take), stop looping. Deliver the best version, keep the check marked FAIL (source-limited) with the attempts listed, and state exactly what would fix it (for example “buy the beat’s WAV/trackouts”). Never call that master “perfect” or “radio-ready”. Say “meets streaming specs; one source-limited item” instead.

Honest engineer’s sign-off (with every delivery)

Use templates/sign_off_report.template.md. Minimum contents:

Verified specs: BPM (verified), key, integrated LUFS, max short-term, 4× true peak, MP3/AAC true peak, limiter GR on the loudest hits, mono correlation, lead-vs-beat pocket delta, hook lift.

QC results: each round’s pass/fail count and every FAIL, with its explanation.

Exact revision diff (v2+): every parameter changed (before → after), and confirmation that everything else stayed frozen.

Honest limits and your own mistakes.

Artist ear checkpoints (timestamps; headphones/car/phone) and the A/B files.

Status: “draft, not final” until the artist approves.

6. DSP & code guardrails

Mandatory for any agent rendering audio with Python (numpy, scipy, soundfile, pyloudnorm) and ffmpeg.

1. Configuration & versioning

mix_config.json is the single source of truth. Every gain, EQ band, compressor, de-esser, delay time and timestamp, reverb level, automation range, loudness target and ceiling, each with why + source + version (template in templates/).

Freeze approved intermediate stems per gate (for example gate1_lead1.wav). Later gates read them; they never re-process approved stages.

Revisions: load the previous config, change only the requested keys, write the before/after diff into the report. Never regenerate a working chain from scratch during a revision unless the artist’s problem measurably originates there. In that case say so and A/B old vs new.

Every render gets a fresh versioned filename (Song_Master_v7_24b-44k.wav). Never overwrite. Move superseded files to versions/. Never delete them silently.

2. Format discipline

Inspect sample rate, channels and duration of every stem first. Resample mismatches with polyphase resampling; verify alignment after.

Do all DSP in float (32/64-bit). Convert to 24-bit PCM (or 16-bit with TPDF dither, dither once, last) only at export.

Keep mono stems as mono content; when converting to stereo for panning, use explicit pan laws.

3. Filters and phase

Prefer second-order sections (butter(..., output='sos') + sosfilt) for mixing filters.

Zero-phase (sosfiltfilt, linear-phase FIR) creates pre-ringing. Avoid it on steep low filters and on drum/vocal transients. If you use it (for analysis, gentle slopes, M/S splitting or DC blocking), say why and check transients.

Linear-phase FIR EQ must be latency-compensated (trim (taps−1)/2) and checked for pre-ringing on transients.

Check every custom filter for stability: np.isfinite(y).all(), plus a peak sanity check against the input.

4. Latency and alignment

Every lookahead process (limiter, de-esser with lookahead, FIR) must be latency-compensated. An uncompensated vocal limiter once delayed the vocal by 0.48 ms; it was caught by measuring transient alignment vs the source.

After any process chain, measure the alignment of transients (1–6 kHz band cross-correlation) vs the source: ≤ 2 samples.

Broadband cross-correlation can show fake “shifts” caused by low-frequency phase. Judge timing in the transient band.

5. Indexing safety

Name variables global_sec/global_idx vs local_sec/local_idx; assert 0 <= local_idx < len(clip).

Mixed-length arrays: pad or trim explicitly before arithmetic. A one-sample mismatch crashed several analyses here.

Guard every window against running past the end of a file. An empty window gave a silent nan that propagated into a “pass”.

6. Click-free edits and fades

5–15 ms raised-cosine fades on every slice, mute, gate, throw, region edge and ending.

Never hard-cut away from a zero crossing.

7. Tails

Every wet buffer is clip length + 3–5 s (or song + 4 s); verify the tail decays below −60 dBFS before the buffer ends; then trim the final master with a short fade after the last audible tail.

8. Loudness and peak measurement

True peak = 4× oversampled peak (resample_poly(x, 4, 1)), never the sample peak.

Loudness = ITU-R BS.1770 / EBU R128 (pyloudnorm or ffmpeg ebur128=peak=true).

Limiter load: measure directly (pre-limiter signal × gain vs post-limiter, per 10 ms block, top 1%). Loudness-difference estimates are skewed by quiet sections.

ffmpeg alimiter: set level=disabled, oversample around it, and set latency=true when timing matters.

Asymmetric saturation plus limiting creates DC. Block DC before and, if needed, after the limiter, then re-check true peak (a DC block can raise peaks slightly, so leave margin in the ceiling).

9. Performance and resources

Never run np.convolve with long windows on full-length audio (O(N·w)). Use cumulative sums for moving averages, or FFT convolution. One rider took 30+ minutes until rewritten.

Run heavy analyses one or two at a time. Three parallel QC runs ran out of memory and a process was killed.

Long jobs: run in the background, then check results. Never assume they finished.

10. Measurement validity

Sanity-test new metrics on synthetic signals with known answers.

Use pitch-independent methods for vocal tone (harmonic envelope). Long-term spectra mix melody with resonances.

Never measure a vocal’s tempo; measure the beat. Never measure “lateness” between two sections; measure each against the beat grid.

When comparing processed vs raw, match loudness first.

11. Shell and file safety

Downloaded archives: list contents before extracting; extract into a new empty directory; read with python -I; never run code from inside them.

Never use rm with an unguarded shell variable path. Move superseded files to a versions folder instead of deleting.

Don’t nest heredocs inside generated scripts; pass settings through environment variables or JSON.

Check every pipeline step’s output. A step that “printed nothing” may have failed. A | head can break a pipe after the file was written; verify the files instead.

12. Reproducibility

Save every script, the mix_config.json, the limiter settings JSON and the QC JSON per version into deliveries/<Song>/session/.

The main master must be reproducible: re-render it through the fixed alternate chain and null-test it.

7. Artist feedback dictionary

Artists describe sound in feelings and pictures. Never guess a fix from a word. Translate the word into measurements, find which cause the numbers support, fix that, and show an A/B. If a note could mean two different things, ask one short multiple-choice question before rebuilding.

Rules:

Re-measure from the raw when the same complaint comes back twice. A repeated complaint usually means an earlier “fix” is the cause.

Prefer removing processing to adding more.

Change only what was asked. Keep everything approved frozen.

Always answer with: what you measured, what you changed, the before/after numbers, an A/B clip and the timestamps to check.


| They say | Measure | Likely causes (confirm with numbers) | Typical fix direction |
| --- | --- | --- | --- |
| “Boxy”, “in a box”, “closet” | Harmonic envelope of the lead (resonance humps); dips next to humps; reverb’s and layers’ 250–800 Hz share vs the dry voice; doubler delay times | Untreated resonance; a hump left standing after broad cuts; a natural dip deepened; box-heavy reverb or doubles; a room recorded into the take (test reflections on breaths/S only) | One bell on the measured hump (≤ 6 dB); undo overlapping cuts; high-pass the reverb send and doubles above the box zone; doublers within 10–20 ms |
| “Tunnel”, “tube”, “phasey”, “hollow” | Comb ripple on the vocal bus; doubler delays; mono correlation; deepened dips | Short delays of the same voice (10–30 ms) at a high level; scooped mids | Lower or retime the doublers, check mono; restore the mids you cut |
| “Dull”, “muffled”, “not clear”, “no life” | Consonant punch and attack (2–5 kHz) vs raw; brightness vs beat/reference; de-esser activity %; number of compressors/limiters | Over-compression (fast attack), stacked de-essers, vocal peak limiter, a dark take, too much low-mid | Strip back to one compressor with a slower attack and one de-esser; presence/air lift sized by measurement; re-check articulation |
| “Harsh”, “piercing”, “sharp S” | 2–5 kHz flare statistic vs raw; S-spike statistic; resonance peaks 2.5–5 kHz | Over-boosted presence; untreated narrow resonance; sibilance lifted by an air shelf | Dynamic cut on the measured peak; retune the de-esser; reduce the boost |
| “Too loud”, “on top”, “pasted on” | Lead vs beat in LU and in the 800 Hz–4 kHz pocket per section | Vocal level; no dynamic pocket; the beat dropping out in breakdowns | Lower the lead (all vocal layers together keep their balance); add or tune the pocket; ride breakdown sections |
| “Buried”, “can’t hear the words” | Same as above + 1–4 kHz vocal-over-music margin in phone/earbud simulations | Masking in the beat’s mids; a dull vocal | Pocket the beat; brighten the vocal; then level |
| “Too much reverb”, “washy”, “far away” | Dry-to-reverb ratio while singing; pre-delay; ducking; return level; decay vs gap length | Short pre-delay, weak ducking, decay longer than the gaps, return too high | Longer pre-delay, more ducking, shorter decay, lower return |
| “Too dry”, “no space” | Dry-to-reverb ratio in gaps; throw coverage | Reverb ducked too hard; no throws in gaps | More bloom in gaps (less ducking or a higher return), throws on line endings |
| “Off beat”, “late”, “rushing” | Onsets vs the beat grid (T0 from kick/snare) per section; P-center of added elements | Added content placed by slice start, not P-center; a copy-pasted region offset; a natural push or lay-back (may be correct!) | Fix only added content or approved regions; report natural phrasing honestly |
| “Cut in”, “chopped”, “clicky” | Edit boundaries; fade lengths; region starts | Hard edits; teases/chops starting mid-word | 5–15 ms fades; start slices at phrase onsets; remove unrequested content |
| “Empty”, “gaps feel empty” | Gap map (vocal-free bars); arrangement density | Long instrumental stretches | Offer options: throws/echo tails, approved BG layers, ghost echoes, swells. Ask before adding content |
| “Missing background vocals” | Which BG stems exist and where | Ambiguous: louder existing BGs vs new layers from the lead vs echoes | Ask (multiple choice), then build |
| “Weak bass on my phone” | 808 fundamental; harmonic content; phone proxy | A sine-only 808; limiter flattening the 808 | Harmonic support before clipping; a glue sidechain high-pass; honest source limit |
| “Not loud enough” | Integrated vs hooks’ short-term; limiter GR; references at matched loudness | A quiet arrangement lowers integrated LUFS; peaky beat | Explain normalization; raise only within the limiter-GR rule; offer a louder alternate with the trade-off stated |
| “Pumping”, “breathing” | Glue/limiter GR vs the 808/kick envelope | A bus compressor or limiter triggered by the sub | Sidechain high-pass on the glue; lower the target; tame the sub |


How Kenshin describes sound (keep this updated in LEARNINGS)

“Boxy / like inside a weird tunnel” → in his songs this was a resonance at 440–520 Hz left standing, plus a deepened 600 Hz dip and box-heavy reverb.

“Dull” → squashed consonants (consonant punch fell from 12.4 to 9.8 dB) plus a dark raw take.

“Too loud” → he and ARMY like the lead about 0 to +0.5 LU over the beat once it’s clear.

“Slight reverb” → audible but clear: reverb about 20 dB under the dry voice, dry-to-reverb ≥ about 24 dB while singing.

“Fill the gaps” → wants echo throws and BG layers, but not unasked vocal teases (they felt off-beat and “cut in”).

8. Learning loop & memory

Agents don’t remember between sessions unless the knowledge is written into files they load. In this repository the memory is:


| Memory | File | Loaded how |
| --- | --- | --- |
| Core rules | AGENTS.md (imported by CLAUDE.md and GEMINI.md) | Auto-loaded by Claude Code / Gemini CLI / many agents in this repo |
| Full standard | .claude/skills/pro-mix-master/ | Claude Code project skill; other agents read it by path |
| Lessons, artist profile, preferences, scores | deliveries/LEARNINGS.md | Read at the start of every job; written at the end |
| Per-song truth | deliveries/<Song>/REPORT.md, session/ (scripts, settings, QC JSON) | Read when revising that song or a similar one |


Agents in chat apps without file access: paste AGENTS.md (and, if space allows, 02-decision-methods.md and 03-qc-gate.md) into the project or custom instructions, and paste the latest LEARNINGS.md at the start of a job.

Before every song

Read AGENTS.md, this skill and deliveries/LEARNINGS.md.

Pull the artist profile (voice range, recurring resonances, mic/room notes, level/space preferences, how he describes sound). Treat it as hypotheses to re-measure, not settings.

If the genre, reference artists or techniques are new: research reputable sources (Sound On Sound “Inside Track”, iZotope Learn, FabFilter Learn, Mix Online, Production Expert, The Pro Audio Files, Mastering The Mix, AES; platform specs from official pages such as Spotify for Artists). Adopt a technique only if two reputable sources agree, or if an A/B test on this song shows a measurable improvement.

Re-check platform loudness specs at least monthly and update 07-delivery-and-release.md.

During the song

Log every decision with its measurement in mix_config.json.

When the artist gives feedback: translate it with 05-artist-feedback-dictionary.md, measure, fix, and write the translation into LEARNINGS (his words → what was actually wrong).

After every song (and after every round of feedback)

Write into deliveries/LEARNINGS.md:

What worked / what failed, with numbers.

The artist’s exact words and what they turned out to mean.

Settings that suited this voice or mic, marked as “re-measure next time”.

Process mistakes (yours included) and the guardrail that prevents them. Add new guardrails to 04-dsp-guardrails.md when they’re general.

Scores 1–10: vocal clarity, balance, low end, effects, loudness & translation, emotion (artist-rated if possible). Aim the next song at the lowest score.

Open questions to ask next time (for example “send dry 24-bit stems and the beat’s WAV”).

Improving the standard itself

When a rule in this standard turns out wrong for a song, don’t silently ignore it. Record the case in LEARNINGS, and if it generalizes, edit the rule (with a dated note on why).

Never delete hard-won lessons; mark them superseded instead.

Prefer measurements and checks over adjectives. If a lesson can become a QC check, make it one. The box-hump, dip and articulation checks were added after a vocal stayed boxy and dull through 15 versions.

9. Delivery & release

Deliverables (every song)


| File | Format | Use |
| --- | --- | --- |
| Main master | WAV 24-bit, 44.1 kHz (or the session rate) | Distributor upload, hi-res stores |
| 16-bit master | WAV 16-bit, TPDF-dithered (once, last) | Stores/CDs that require 16-bit |
| MP3 | 320 kbps CBR from the 24-bit master; true peak < 0 dBTP after encoding | Sharing, quick listening |
| Clean / radio edit | Same spec as the main | Radio, clean playlists. Needs the artist’s list of words to clean (timestamps); mute, reverse or replace on the beat; check BGs and adlibs too |
| Instrumental | Same chain as the main | Performances, sync |
| Acapella | Same chain as the main | Remixes |
| TV track | Beat + background layers, no lead | Live/TV |
| Alternates the artist asked for | Same chain | For example a “no fills” version |
| Unmastered mix | WAV 24-bit, peaks around −6 to −3 dBFS | Future remasters |
| Stems (optional) | WAV 24-bit, all starting at 0:00, same length | Live shows, remixes |
| A/B clips | MP3, loudness-matched | Artist listening |
| Picture | PNG song map, waveforms, spectrograms | Visual check |
| Report | REPORT.md (sign-off) | Record |


All alternates go through the exact same bus and master settings as the main (fixed gains, glue threshold, limiter gain and ceiling). Prove it with a null test of the main re-rendered through that chain.

Naming and archiving

Song_Name_Master_v12_24b-44k.wav, Song_Name_Instrumental_v12_24b-44k.wav, Song_Name_AB_<what>_vA_vs_vB.mp3.

Current deliverables live in deliveries/<Song_Name>/. Older versions move to a versions folder (never silently deleted). Settings, scripts and QC JSON go in session/.

Commit and push deliverables. Note large-file limits (keep each file under about 50 MB where possible).

Platform loudness facts (as recorded Nov 2026; re-verify monthly from official sources)


| Platform | Normalizes to | Notes |
| --- | --- | --- |
| Spotify | −14 LUFS | Asks for true peak below −1 dBTP, or below −2 dBTP if the master is louder than −14 LUFS (Spotify for Artists) |
| YouTube | about −14 LUFS | Turns down only |
| TIDAL | about −14 LUFS | Normalization on by default in mobile apps |
| Amazon Music | about −14 LUFS | Users can disable normalization |
| Deezer | about −15 LUFS | Users can disable normalization |
| Apple Music | −16 LUFS (Sound Check) | Mostly turns down |


Consequence: masters crushed far above −14 LUFS get turned down and sound smaller. Choose loudness for punch at matched loudness, within the limiter-GR rule.

Release-readiness extras (ask the artist; agents don’t invent metadata)

Final title spelling, artist/feature credits, explicit/clean flag, ISRC (from the distributor), songwriter/producer credits, beat license (a “FREE … type beat” usually requires a lease or credit before commercial release; flag it), cover-art match.

Radio edits typically run about 3:00–3:45 with a short intro. Confirm with whoever pitches the song.

FM radio boosts highs and many radios play in mono, so sibilance control and mono compatibility are required.

DAW mix sheet (hybrid route)

When plugin character or real tuning matters, also deliver a sheet the artist can rebuild in FL Studio, BandLab or any DAW. For each track: insert order, plugin (stock option + pro option), and the exact values derived for this song (Hz, dB, Q, threshold, ratio, attack, release, de-ess band, send levels, pre-delay/decay in ms, delay ms, pan %), plus the sidechain routing (vocal → beat pocket, vocal → delay and reverb ducking), bus settings and the limiter ceiling. Never fill the sheet with generic numbers.

What to send the artist

A/B clips first (matched loudness), then the full song MP3, then the picture.

A short, plain-language summary: what changed, before → after numbers, honest limits, 2–3 timestamps to check on headphones, car and phone.

Where the full files are (with a simple how-to if needed).

An invitation for specific feedback: “timestamp + what you hear”.

10. Templates

10.1 Mix plan (Gate 0)

Fill this in from measurements before processing anything. Every later decision must trace back to this plan.

Song facts (measured)


| BPM (verified to the sample) |  |
| --- | --- |
| Grid T0 |  |
| Key / sung range |  |
| Length (beat vs last vocal) |  |
| Stems & roles |  |
| Source quality (lossy? printed FX? clipping?) |  |


Section map


| Time | Section | Vocals present | Beat energy |
| --- | --- | --- | --- |


Reference(s)


| Track | Integrated / hook short-term LUFS | Vocal pocket delta | Notes (valid as reference?) |
| --- | --- | --- | --- |


Artist intent (in their words + confirmation)

Genre / emotion:

What must stand out:

Creative FX requested (exact, confirmed):

Things NOT to do:

Top 3 problems (with numbers)

Approach per vocal (directions to test, not settings)


| Vocal | Role | Cleanup | Tone direction | Dynamics direction | Space |
| --- | --- | --- | --- | --- | --- |


Effects plan per section


| Section | Reverb | Delays / throws | Layers | Automation |
| --- | --- | --- | --- | --- |


Low end & beat plan

Loudness strategy

(How the target will be chosen: limiter-GR rule, reference at matched loudness, quiet-section share.)

Song-specific QC thresholds (set now, before results)

Open questions for the artist

10.2 Engineer’s sign-off report

Status: draft, not final (until the artist approves) · QC: R1 / · R2 / · R3 /

Verified specs


| Spec | Value |
| --- | --- |
| BPM (verified) / key |  |
| Integrated loudness / max short-term (hooks) |  |
| True peak (4×) / after MP3 / after AAC |  |
| Limiter GR on loudest 1% of hits |  |
| Mono correlation (full / < 250 Hz) |  |
| Lead vs beat (LU) / pocket delta 800 Hz–4 kHz |  |
| Hook lift |  |
| Dry-to-reverb while singing |  |


What changed (v<N−1> → v), exact diff


| Parameter | Before | After | Why (measurement / request) |
| --- | --- | --- | --- |


Everything not listed above: unchanged / frozen (confirmed by regression check).

QC results

Each FAIL with its explanation (source-limited items: attempts made + what would fix it).

Honest limits & my mistakes

Please check (headphones, car, phone)

mm:ss: what to listen for

mm:ss: what to listen for

mm:ss: outro tail

Files


| File | Use |
| --- | --- |


Feedback that helps most: timestamp + what you hear, in your own words.

10.3 mix_config.json (one per song per version)

Every parameter needs value + why (the measurement on THIS song) + source + version. Values are blank on purpose: never copy numbers from another song.

{
  "_readme": "One file per song per version: deliveries/<Song>/session/mix_config_vN.json. EVERY parameter needs value + why (the measurement that justified it, on THIS song) + source (measured | reference | artist_request | carried_from_vN) + since (version it was set/changed). Values here are placeholders (null) on purpose: never copy numbers from another song.",
  "song": {
    "title": null,
    "artist": null,
    "version": "v1",
    "status": "draft, not final",
    "bpm": {"value": null, "why": "detected on beat + 96-bar self-match drift (samples)", "source": "measured"},
    "grid_t0_sec": {"value": null, "why": "kick/snare transient phase", "source": "measured"},
    "key": {"value": null, "why": "detection score + sung pitch classes", "source": "measured"},
    "sections": [{"name": null, "start_sec": null, "end_sec": null}],
    "reference_tracks": [{"title": null, "integrated_lufs": null, "hook_short_term_lufs": null, "vocal_pocket_delta_db": null, "valid_reason": "no printed-FX / quality issues"}]
  },
  "intake_findings": {
    "printed_fx_on_vocals": null,
    "lossy_source": null,
    "copy_pasted_regions": [],
    "timing_vs_grid_ms_by_section": {},
    "lowest_sung_note_hz_by_vocal": {},
    "blockers": []
  },
  "gate1_vocals": {
    "<stem_name>": {
      "role": null,
      "edge_fades_ms": {"value": null, "why": null},
      "working_level_rms_dbfs": {"value": null, "why": null},
      "rider": {"window_ms": null, "max_db": null, "why": "phrase spread before/after"},
      "hpf": {"hz": null, "slope_db_oct": null, "why": "lowest sung fundamental = ? Hz", "source": "measured"},
      "eq_cuts": [{"hz": null, "q": null, "db": null, "why": "harmonic-envelope hump peak/width; persists across sections", "source": "measured"}],
      "compressor_stages": [{"threshold_db": null, "ratio": null, "attack_ms": null, "release_ms": null, "avg_gr_db": null, "why": "phrase spread + articulation check"}],
      "deesser": {"band_hz": [null, null], "threshold": null, "max_cut_db": null, "active_pct": null, "why": "S-spike stats"},
      "tone_boosts": [{"type": "bell|shelf", "hz": null, "q": null, "db": null, "why": "brightness vs beat/reference"}],
      "saturation": {"enabled": false, "why": null},
      "pan": {"value": null, "why": null},
      "level_vs_lead_db": {"value": null, "why": null}
    },
    "pocket": {"lead_vs_beat_lu_target": null, "midband_delta_db_target": null, "beat_mid_dip": {"hz": null, "q": null, "max_db": null, "attack_ms": null, "release_ms": null}, "why": "reference delta / artist preference", "source": null}
  },
  "gate2_space": {
    "reverb": {"type": null, "decay_s": null, "predelay_ms": null, "send_hpf_hz": null, "send_lpf_hz": null, "duck_db": null, "return_db_under_lead": null, "dry_to_reverb_while_singing_db": null, "why": null},
    "delays": [{"name": null, "note": null, "ms": null, "samples": null, "feedback": null, "band_hz": [null, null], "duck_db": null, "why": null}],
    "throws": [{"global_sec_range": [null, null], "note": null, "p_center_sec": null, "collision_check": "pass|fail", "why": "measured line end + gap length"}],
    "layers": [{"name": null, "built_from": null, "level_db_under_lead": null, "hpf_hz": null, "detune_cents": null, "delay_ms": null, "pan": null, "sections": [], "approved_by_artist": null}],
    "creative_fills": [{"name": null, "approved_by_artist": false, "grid_shift_bars": null}]
  },
  "gate3_balance": {
    "section_automation": [{"target": null, "range_sec": [null, null], "db": null, "why": null}],
    "hook_lift_lu_target": null,
    "beat_processing": [{"process": null, "settings": {}, "why": null}],
    "mix_bus": {"gain_stage_peak_dbfs": -6, "glue": {"ratio": null, "threshold_db": null, "attack_ms": null, "release_ms": null, "sidechain_hpf_hz": null, "avg_gr_db": null}, "side_hpf_hz": null, "why": null}
  },
  "gate4_master": {
    "corrective_eq": [],
    "loudness_target_lufs": {"value": null, "why": "loudest target with limiter GR <= 3-4 dB on loudest 1% hits; matched-loudness reference comparison"},
    "true_peak_ceiling_dbtp": {"value": null, "why": "-1.0, or -2.0 if louder than -14 LUFS; margin for post-limit stages"},
    "limiter": {"input_gain_db": null, "attack_ms": null, "release_ms": null, "oversampling": 4, "measured_gr_top1pct_db": null},
    "post_limit": {"dc_block_hz": null, "verse_dip_db": null, "fade_out": null}
  },
  "qc_thresholds_song_specific": {
    "_note": "Set BEFORE seeing results. Any later change needs a written reason in the report.",
    "lead_vs_beat_lu_range": [null, null],
    "pocket_midband_db_range": [null, null],
    "hook_lift_lu_range": [null, null],
    "reverb_db_under_lead_range": [null, null],
    "dry_to_reverb_while_singing_min_db": null,
    "stack_db_under_lead_range": [null, null],
    "echo_bg_db_under_line_range": [null, null],
    "resonance_hump_max_db": null,
    "brightness_target_db": null,
    "integrated_lufs_target": null
  },
  "revision_log": [{"version": "v1", "requested_by": null, "request": null, "changed_keys": [{"key": null, "before": null, "after": null, "why": null}], "frozen_confirmed": true}]
}

11. Sources and what changed

This standard merges three sources (originals archived in the repo at .claude/skills/pro-mix-master/sources/, all superseded by this standard):

Kenshin’s “Pro Mix & Master Agent: Full Instructions” (Word doc, Nov 21 2026): professional bar, 7-pass QC × 3 clean rounds, honest reporting, learning loop, delivery set, platform table.

The Gemini package (Major-Label Engineering Playbook, Pre-Release QC Checklist, DSP Code Guardrails, and the combined “Agent Package”): gated workflow with artist stops, mix_config.json diff-only revisions, the vocal pocket concept, P-center throw alignment, collision gating, tail padding, a DAW mix sheet and a sign-off report.

What two real songs taught us (“Old Motorola” v1–v5, “What I’m Posed To Do” v1–v16; see deliveries/LEARNINGS.md).

Kept from the Gemini package

Gates with preview stops; immutable config and diff-only revisions; frozen gate stems; vocal-inside-the-pocket; mid-channel dynamic beat pocket; P-center alignment; collision gating; 3–5 s tail padding; sosfilt and pre-ringing caution; global vs local index discipline; click-free fades; 4× true peak and BS.1770 loudness; cache-busting filenames; no unrequested sound effects; best tool for the job (DSP render vs DAW mix sheet); honest sign-off with listen-back checkpoints.

Corrected or changed (and why)


| Gemini said | This standard says | Why |
| --- | --- | --- |
| Fixed numbers for HPF, EQ zones, compressor ratios/attacks, de-ess bands, reverb, loudness | Starting ranges only; every value derived from the song’s measurements and logged with its reason | Every song is different. The fixed “box zone 180–380 Hz” missed this song’s real box at 440–520 Hz |
| “Always listen back” | Agents cannot hear. Measured checks + loudness-matched A/B + artist listen-back at timestamps | Claiming to listen is dishonest |
| True peak ≤ −0.5 (−1.0 to −0.5) dBTP | ≤ −1.0 dBTP; ≤ −2.0 dBTP when louder than −14 LUFS; < 0 after encode | Kenshin’s standard and Spotify for Artists guidance; inter-sample safety after encoding |
| Target −10.5 to −9.0 LUFS | Loudness chosen per song by the limiter-GR rule (≤ 3–4 dB on the loudest hits) and matched-loudness reference comparison | “Never let the limiter do the mixing.” A peaky YouTube-rip beat with long quiet sections correctly landed near −14 |
| Two-stage serial compression as the default | Start with one stage sized to this vocal; add stages only if measured; verify articulation | Stacked fast compression, a vocal limiter and three de-essers made the vocal dull (consonant punch 12.4 → 9.8 dB) |
| Notch boxy low-mids “180–380 Hz” | Find resonances with the pitch-independent harmonic envelope; one bell where measured; never deepen natural dips | A hump left next to a deepened dip = boxy/hollow for 15 versions |
| Pocket “±1.5 dB of beat midrange” as a universal pass | Pocket target set per song (reference delta or artist preference), guarded by intelligibility checks | References and artists differ; Kenshin preferred about 0 to +0.5 LU |
| Micro-doubler 12–22 ms | 10–20 ms / 5–12 cents, mono-checked, box-band checked | Doubles at 21/29 ms were heard as a “tunnel” |


Added (not in either source)

Articulation QC (consonant punch and attack vs raw), resonance-hump and dip checks, reverb-clarity metric (dry-to-reverb while singing).

Metric sanity tests with known-answer signals; QC must read the real mix gains; no hidden FAIL summaries.

Timing judged against the beat grid (not section vs section); sample-exact BPM verification; copy-paste region detection.

Latency compensation for lookahead processes; DC handling around limiters; performance and memory rules.

Artist feedback dictionary; artist profile; learning loop with scores; research-adoption rule.

Release extras: beat-license flag, clean-edit process, alternates through an identical chain with null test.
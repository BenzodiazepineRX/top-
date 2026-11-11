# Music engineer playbook

> **Read `music/LESSONS.md` before this page.** It records what the owner approved and rejected on every song so
> far. Where this page says "listen", no agent can: send the owner a loudness-matched comparison and wait for
> his words.

Every song is different. Read this before mixing. Then think, listen, and decide like a top professional engineer who mixes for the world's biggest artists.

There is no house preset. There is no chain to copy from the last song. A frequency, a ratio, a LUFS number, or a delay time in this page is a starting point. Confirm it by listening to this song, by measuring it, and by comparing it with this song's reference track. If the number and the song disagree, the song wins.

The plan for the song is `music/songs/<song>/brief.md`. This playbook never overrides that brief. The artist's requests in the brief win over a habit, a genre stereotype, or a setting that worked last time.

## Before touching a fader

Answer these in `mix-notes.md` before you reach for a plugin.

- **Emotion.** What should the listener feel, in the words of the brief? Warm, tense, huge, close, lonely, aggressive. The processing has to serve that feeling.
- **Arrangement.** What is in front, what is support, and where does the energy move (verse, chorus, drop, breakdown)? A busy chorus needs different space than a stripped verse. Do not EQ a part in solo and call it done.
- **Reference.** For each reference track, what are you borrowing (vocal distance, drum tone, low-end weight, width) and what are you leaving alone? Level-match the reference before you compare, so a louder master does not fake a better mix.
- **The ask.** What did the artist say is already working, what is broken, which platforms matter, and which creative effects are required, on which bar?

If you cannot answer those four, you are not ready to mix.

## What a pro would do differently from song to song

Same engineer, three different records, three different chains. These are illustrations. The brief and the reference still decide the real song, including two songs inside the same genre.

**Sparse ballad.** The vocal can breathe. Compression stays light and slow so the phrase still rises and falls. Reverb can be longer and wider, because the arrangement has room for it. Low end is gentle and clean. Kick and bass rarely fight, because they are not both asking for the whole sub. Loudness stays more dynamic. A useful starting range is about -14 to -16 LUFS, then you check the reference. Effects are few and placed: one reverse reverb into a single word can be the whole moment, because nothing else is in the way.

**Dense trap banger.** The vocal is leveled hard and kept upfront, often with more than one compressor, so every bar is intelligible over the drums. Reverb is short or nearly dry. Space comes from short delays, ad-libs, and the arrangement, not from a long hall. The low end is the record: kick and 808 either take turns or are sidechained, and the sub stays mono. Loudness is denser. A useful starting range is about -7 to -9 LUFS, then you check the reference, because plenty of modern records sit quieter on purpose. Effects are structural: throws, filter drops, tape stops, and beat switches on the whole mix, landed on the grid.

**Melodic R&B.** The vocal is controlled and still human. A slower, smoother compressor keeps the melody moving and keeps the breath. Reverb is a medium plate or room, with pre-delay so the voice stays close, and the tail is ducked so it blooms in the gaps instead of on the words. Low end is warm and round. It supports the vocal. It is not a distorted 808 wall unless the brief asks for that. A useful starting range is about -10 to -12 LUFS, checked against the reference. Effects tend to be vocal throws, dotted echoes, and filtered intros that open into the full song.

Inside any of these, the next song still gets a fresh decision. A ballad with a distorted bass drop is not "the ballad chain." A trap song with a sung, airy hook is not "the trap vocal chain" on that hook.

## 1. Profile the song first

Do this from the brief and from the audio. Write what you find. Do not assume.

- Tempo (BPM) and key. If the tempo changes, note each section. Delay math uses the BPM of the section you are affecting.
- Genre and subgenre, as named in the brief. Genre is a clue to the references. It is not a preset pack.
- Dynamic range. Is the song one loud level the whole way, or does it have real quiet and loud sections? Protect the contrast the arrangement wrote.
- Vocal range and tone, if there is a vocal: where it sits (low, mid, high) and how it sounds (dark, bright, thin, boomy, nasal, breathy). A baritone and a high tenor do not get the same high-pass.
- Creative intent and references: the aesthetic in the brief (dry upfront rap vocal, lush indie-pop, warm analog R&B, aggressive rock, or whatever this song actually is) and the one to three reference tracks, with what to borrow from each.

Listen once with no plugins, at a moderate volume, and note the three biggest problems in the song's own words (mud, harsh vocal, weak chorus, buried kick, and so on). Those three are the job. A problem you did not hear is not a reason to load a plugin.

## Levels before tone

Get the faders honest before EQ and compression. Every song arrives at a different level.

- Nothing clips on the way in. Peaks on individual tracks sit with headroom, and the mix bus is not already on the ceiling. Several dB under full scale on the mix bus is a comfortable start. The exact number depends on how dense the stems already are.
- Balance the lead, the drums, and the bass with faders first. If a fader is pinned, lower the clip gain and set the fader again.
- Level-match the reference to your mix before any tone comparison. Solo the reference, match loudness by ear, then switch. Write what the reference has that this song does not, and what this song should keep that the reference does not have.

Only then reach for EQ, compression, and effects. A plugin chain copied on top of a wrong balance just makes the wrong balance louder.

## 2. Shape the vocal for this singer

Every vocal is a different instrument. Skip this section if the song has no vocal, and say so in the notes.

**High-pass from the voice, not from a template.** A deep voice often only needs rumble removed, with a starting cutoff around 60–80 Hz. A higher voice often starts around 100–140 Hz. Sweep while the track plays. Stop at the point where rumble is gone and the chest of the voice is still there. If the brief wants a thick, bass-heavy vocal, that cutoff moves down.

**Notch ringing that is actually there.** Scan for resonances, harsh build-up, and room honk. Cut those narrow spots. Do not drop a remembered frequency (a stock 300 Hz or 3 kHz cut) because the last singer needed it. If you cannot hear the problem with the notch bypassed, do not cut.

**Compression follows density and emotion.** Modern, dense styles (a lot of hip-hop, pop, and EDM) often want a fast, firm level so the vocal stays in front. Two compressors in series is a common start: the first catches peaks, the second evens the phrase. A starting attack on a peak controller is about 5–15 ms, so the consonant still speaks, with a release that recovers before the next phrase. Organic styles (a lot of R&B, acoustic, and soul) often want a slower, more transparent compressor so breath and dynamics stay. A starting attack there is about 20–40 ms, with only a few dB of reduction. Starting ratios for either live around 2:1 to 4:1. Use more only when the performance or the genre needs it, and write the attack, release, ratio, and gain reduction you actually hit. A volume ride is still the right tool when a plugin would flatten a line that should swell.

**De-ess the "s" this singer has.** Sweep the sidechain, usually somewhere between 4.5 kHz and 9 kHz, until you are on this vocal's sibilance, not a guess. Reduce only enough to take the sting. If the voice turns dull or lisps, you went too far. Check it on earbuds.

## 3. Build space that fits the arrangement

**Delays and echoes are calculated, never guessed.** Use the song's BPM and `music/effects-guide.md`.

- Quarter note in milliseconds = 60000 / BPM
- Dotted = that note × 1.5
- Triplet = that note × 2/3

A dotted eighth is the straight eighth × 1.5. An eighth-note triplet is the straight eighth × 2/3. Do not multiply the quarter note by 2/3 and call it an eighth triplet. Write the note value and the milliseconds in `mix-notes.md` for every delay, echo, pre-delay, and tempo-based reverb decay you set. Host tempo sync is fine when the session BPM is this song's BPM. Compare one readout to the math.

Work the real BPM. At 120 BPM, only as a check of the formula: quarter = 60000 / 120 = 500 ms, dotted quarter = 750 ms, quarter triplet = 333.33 ms, eighth = 250 ms, dotted eighth = 375 ms. If this song is not 120, those numbers are wrong for it. Calculate again and paste the result into the notes.

Common starting note values, still chosen per song: a quarter or a dotted eighth for a vocal throw, a short slap for thickness. If the throw blurs the next word, shorten the feedback or the note value. The groove decides.

**Reverb follows how full the arrangement is.** A sparse song can take a longer decay and a wider image, because the space is part of the emotion. A starting decay there is often about 1.5–3 seconds, or a whole number of bars from the timing table, whichever ends in a musical gap. A dense song wants a shorter plate or a small room, often about 0.4–1.2 seconds, plus pre-delay, so the hit stays punchy and the wash does not cover the vocal. Pre-delay is a short note from the timing table (often a 1/32 or a 1/16), not a random millisecond. If the reference is nearly dry, start drier than these ranges.

**Duck the tails.** When the vocal (or the lead) is present, pull the wet reverb and delay down. Let the tail bloom in the pauses. Time the release so it breathes with the phrase. If the genre wants an obvious wash on the words, the brief will say so. Otherwise the words win.

## 4. Creative effects the artist asked for

These take priority. Build every line in the brief's creative-effects list, on the track it names or on the whole mix. A whole-song move (the entire record fading in, a sweep, a drop) goes on the mix bus, across the bars named. Doing it only on the vocal is a different effect.

The usual requests:

- Reverse reverb into a word or a hit. The swell ends as the sound starts.
- Echo throws on a word or a hit, then they stop. Tempo-synced, with the repeat count the brief asked for.
- A filtered, distorted fade-in that gets louder and clearer. Filter opening, distortion falling, and volume rising all move across the same bars. This can be one vocal or the entire song.
- Sweeps, risers, drops, tape stops, transitions, and beat switches, landed on the downbeat the brief names.

How to build each one is in `music/effects-guide.md`. If a named plugin cannot run on the Linux machine, build the same effect with the tools in `music/daw-setup.md` and write both names in the notes. Do not drop the effect, move it, or replace it with a different idea.

## 5. Low end, width, and the mix bus

The low end of this song is not the low end of the last one.

**Decide who owns the sub before you boost it.** On some records the kick is the click and the bass is the note. On others the 808 is both the pitch and the hit, and the kick is a short tick on top. Sidechain the bass from the kick when they occupy the same moment and the brief wants the kick to speak. Leave them stacked when the genre wants one combined thud. Confirm on a phone speaker, where the sub disappears and only the midrange of the bass remains.

**Keep the low end solid.** A starting point is to keep kick and bass mono below the crossover, often somewhere from 80 to 120 Hz. Move that point until the sub is stable in mono and the notes still read on a small speaker. Center the parts that should stay center, usually vocal, kick, bass, and snare, unless the brief wants one of them wide.

**Width comes from the arrangement.** Pan support parts. Leave the lead in its place. A widener is a last touch, checked in mono so nothing important vanishes. A chorus gets wider than a verse only when this song wants that lift.

**Bus processing is glue, after the balance exists.** Drum, music, and vocal buses can take a little compression or saturation once the faders tell the truth. The mix bus is not where you repair a vocal that was never ridden or a bass that was never EQ'd. Parallel compression adds weight under a dry path. It does not replace the dry path.

## 6. Master for this record

Every master is for one record. Master when the mix is ready. Order is a starting shape, not a law: corrective EQ, gentle compression, any tonal EQ, saturation only if the song wants it, limiter last. Fix balance problems in the mix.

**Loudness ranges are starting targets, not finish lines.** Pick a neighborhood from the genre and the feeling, then move it until this master sits with its own reference.

| Feel of the record | Starting integrated LUFS |
| --- | --- |
| Acoustic, jazz, ambient, or anything that should stay dynamic | about -14 to -16 |
| Modern pop, hip-hop, R&B | about -10 to -12 |
| Club, EDM, trap, when the reference is actually that dense | about -7 to -9 |

**True peak starting ceiling: -1.0 to -0.5 dBTP.** Stay inside that until the reference and the destination say otherwise. Louder masters and lossy encoding often want more headroom, closer to -1 dBTP or below. The platform ranges in `music/checklist.md` tell you what streaming and radio will do on playback. Matching a club reference at -8 LUFS does not mean the stream will play at -8. Write the measured LUFS, the true peak, and the target you compared them with.

## 7. Translation

Listen on earbuds, a phone speaker, in a car, and, when the brief names a club or a system like one, there too. Also check studio monitors. The definition of done in `music/README.md` requires the earbuds, phone, car, and monitors.

- Earbuds: vocal harshness, sibilance, and whether the lead is actually in front.
- Phone speaker: almost no bass. Does the song still read in the mids?
- Car: low end boom or a hole, vocal against noise.
- Club or a full-range system: sub, kick, and whether effects that felt subtle on headphones are now huge.

Write a line per system in `mix-notes.md`. Fix what fails in more than one place. Leave what is part of the sound, and say why.

## 8. Explain the pass, then wait for sign-off

For each version, leave an A/B the artist can follow: what you changed in EQ, compression, and space, and why this song needed it. Offer real revision choices in plain language, such as more upfront, wetter or drier, brighter, or more punch. One choice at a time is easier to judge than five at once.

In that note, name the decision, not a plugin dump:

- The vocal move, and what it did to this singer (closer, smoother, still breathing).
- The low-end move, and whether kick or bass owns the sub on this song.
- The space move, with the delay in note value and milliseconds.
- The loudness you measured, the reference you compared, and whether you stopped short of the reference on purpose.
- Any creative effect, where it lands, and whether it is on one track or the whole mix.

Return a WAV of the mix or master and an MP3 preview, logged in `mix-notes.md`, as `music/daw-setup.md` describes.

Nothing is finished until the user signs off on the final master. The checklist is in `music/README.md`, and the signature lives in that song's `mix-notes.md`. A work-in-progress export is not that signature. Until the sign-off is written, keep listening, and keep deciding for this song.

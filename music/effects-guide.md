# Creative effects guide

The song brief says which effects this song gets, and the exact moment each one happens. This page is how those effects are usually built, and how to time them.

An effect is either on **one track** or on the **whole mix**. The brief's Scope column says which. A whole-mix move goes on the mix bus or the master, so every element is affected together. Do not fake it by automating only the vocal.

Whole-mix moves are drawn across a set number of bars. Write the start bar, the end bar, and what is moving (cutoff, drive, volume, mute). When a plugin asks for a time in milliseconds, convert that bar length with the timing table below.

Honor the brief. If it names a plugin, use that plugin. If the plugin is missing from the session, write that in `mix-notes.md` and ask. Do not quietly swap in a different effect.

Acknowledge the list before you mix: in the song's notes, restate each request in your own words (effect, one track or whole mix, spot, length in bars, plugin). Then build it.

## Tempo math

Echoes, delays, reverb pre-delay, and reverb decay follow the song's tempo. Compute them from the BPM in the brief, or switch the plugin to the DAW's tempo sync at that same BPM. Double-check the math. A guessed millisecond value is not done.

These formulas assume one quarter note is one beat (normal 4/4). If the brief names another time signature, sync to the DAW grid and still write down the millisecond values you used.

**Quarter note in milliseconds = 60000 / BPM**

| Note | Formula |
| --- | --- |
| 1 bar of 4/4 | quarter × 4, which is 240000 / BPM |
| 1/2 | quarter × 2, which is 120000 / BPM |
| 1/8 | quarter / 2, which is 30000 / BPM |
| 1/16 | quarter / 4, which is 15000 / BPM |
| Dotted | that note × 1.5 (the note plus half of itself) |
| Triplet | that note × 2/3 (three of them fit in the time of two straight notes) |

A dotted 1/8 is the straight 1/8 time × 1.5. A 1/8 triplet is the straight 1/8 time × 2/3. Do not multiply the quarter note by 2/3 and call it an eighth-note triplet.

Multiply the exact value, then round the result to two decimals. Rounding the quarter note first, then multiplying, can be off by a hundredth.

### Worked example at 140 BPM

Quarter note = 60000 / 140 = **428.57 ms**.

Dotted quarter = (60000 / 140) × 1.5 = **642.86 ms**.

Quarter-note triplet = (60000 / 140) × 2/3 = **285.71 ms**.

| Note | Straight (ms) | Dotted × 1.5 (ms) | Triplet × 2/3 (ms) |
| --- | --- | --- | --- |
| 1 bar (4 beats) | 1714.29 | — | — |
| 1/2 | 857.14 | 1285.71 | 571.43 |
| 1/4 | 428.57 | 642.86 | 285.71 |
| 1/8 | 214.29 | 321.43 | 142.86 |
| 1/16 | 107.14 | 160.71 | 71.43 |

This table is only the example. Every song gets its own table in `brief.md`, filled from that song's BPM. If the tempo changes, calculate each section from its own BPM.

Host tempo sync is fine when the plugin has note values (1/8, dotted 1/8, and so on). A tempo change then stays locked. Still fill the brief's table, and compare one plugin readout to the table. If they disagree, find the wrong BPM before you print the effect.

Pre-delay is usually a short note, often a 1/16 or a 1/32 (a 1/32 is the 1/16 time cut in half: at 140 BPM that is 53.57 ms). Decay is a length in notes or bars: a 2-bar tail at 140 BPM is 1714.29 × 2 = **3428.57 ms**. Pick a length that ends on a musical boundary, such as the end of a bar or just before the next phrase, unless the brief asks for a long wash.

## Reverse reverb

A swell that rushes into a word or a hit, instead of a tail that rings after it.

1. Solo the word or hit.
2. Add a reverb and bounce only the wet tail, without the dry sound.
3. Reverse that bounced audio.
4. Place it so the swell ends as the word or hit starts.
5. Turn off the normal reverb on that moment if the reverse is the only space you wanted.

The brief says how long the swell is (often a 1/2 note or one bar). Compute that length from the BPM and trim so the peak of the swell lands on the lyric, not after it.

## Echo and delay throws

One word, syllable, or snare that repeats a few times, then stops. The whole vocal is not sitting in delay.

1. Put a delay on a send, fully wet.
2. Automate the send up for only that word or hit, then back down.
3. Set the delay time to a note from this song's timing table. A dotted 1/8 is a common vocal throw because the repeat falls between the beats. Use the note the brief names when it names one.
4. Set feedback for the number of repeats the brief asks for. Low feedback is one or two echoes.
5. Filter the repeats (often a high cut) when they should sit behind the next word.

Check the throw against the grid. The repeats should fall on musical divisions, not in a random gap.

## Filtered, distorted fade-in

A sound enters quiet, muffled, and gritty, then becomes louder and clearer. This can be one part, often a vocal, or the entire song.

Over the bars named in the brief, automate all three of these together:

- a low-pass filter cutoff moving from closed (muffled) to open (clear)
- saturation or distortion amount moving from high to low
- volume moving from quiet up to the level the part, or the whole mix, should sit at

They share one start bar and one end bar. The sound should arrive clear on the beat the brief names, not halfway through the next section. Write those bars in the notes.

On one track, the plugins and the automation sit on that track. For the whole song, they sit on the mix bus or master. The drums, bass, and vocals should all fade in muffled together. Leaving the beat clean while only the vocal is filtered is a different effect, and it needs its own line in the brief.

## Risers

A noise, a rising synth, or a reversed cymbal that climbs into a drop, chorus, or downbeat.

1. Start with noise, a pitch rise, or a reversed cymbal.
2. Over the length in the brief (often 1, 2, or 4 bars), automate volume upward and open a filter so the sound gets brighter as it gets louder.
3. End the riser on the downbeat it is leading into. A 4-bar riser at 140 BPM is 1714.29 × 4 = **6857.14 ms**. Use this song's BPM, not 140, when you build the real one.

## Full-mix filter sweeps

A filter on the mix bus that opens or closes across a transition, a build, or a breakdown.

1. Put the filter on the mix bus, not on a single stem, unless the brief names one instrument.
2. Automate the cutoff over the exact bars in the brief. Opening means muffled toward bright. Closing means the reverse.
3. Keep resonance low unless the brief asks for a pronounced sweep. High resonance on a full mix gets harsh fast.
4. Land the end of the move on the downbeat the brief names.

A sweep that lasts 2 bars at 140 BPM is 1714.29 × 2 = **3428.57 ms**. Use this song's bar length, from its own timing table, when you build the real one.

## Drops

A drop is a hole or a hit that the arrangement falls into. On a full mix it is usually the beat pulling away, a filter closing, or the mix bus dipping, then everything returning on a downbeat.

1. Decide from the brief what actually drops: the whole mix, the drums, or the music under a vocal that stays.
2. Mute, fade, or filter that scope for a length in beats or bars. A 1-beat hole is a quarter note from the timing table. A 1-bar hole is one bar.
3. The return lands on the grid. "About a bar" is not a drop timing.

If the brief wants silence, the mix bus fade or mute covers that exact length. Check it in mono and on a phone speaker so the hole still reads when there is almost no bass.

## Transitions

A transition is how one section becomes the next. It might be a riser, a sweep, an impact, a reverse reverb, a short silence, a tape stop, or more than one of those stacked.

Each piece still gets its own row in the brief, or one row that names the stack and the bar. They share an end point: the downbeat they lead into. Automate them over the bars named, on the track or the mix bus the brief chooses.

## Beat switches

The drum pattern, the groove, or the energy changes at a specific bar.

1. Mute or unmute the drum tracks on that bar, or swap to the other drum stem the brief names.
2. If a fill, sweep, or tape stop leads in, it ends as the new beat starts.
3. Crossfade the two beats only when the brief asks for a blend. A hard switch is a cut on the bar line.

The switch is a whole-mix moment even when the fader moves are on the drum tracks, because the listener hears the song change. Note both the bar and which stems flip.

## Tape stops

The song, or one part of it, slows and drops in pitch like a tape machine powering down. It usually falls into a pause, a drop, or a beat switch.

1. Use the tape-stop plugin named in the brief. If none is named, use a pitch-and-time move that slows down and pitches down together.
2. One part stops on that part's track. The whole song stopping means the plugin or the slowdown is on the mix bus, so nothing is left playing at full speed.
3. Start on the hit the brief names. A common length is a 1/4 note, a 1/2 note, or one bar. Compute that length so the stop finishes on the next point the brief names.

## Ordinary delay and reverb

The same timing rules apply when the effect is just the song's normal space, not a special moment.

- Delay time is a note value from the timing table.
- Pre-delay is a short note so the dry sound is heard before the wash.
- Decay is a number of notes or bars so the tail ends where the arrangement wants it to end.

Write the note value and the milliseconds in `mix-notes.md` whenever you set one.

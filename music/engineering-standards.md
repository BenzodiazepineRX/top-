# Engineering standards

Every agent works to the standard of a top-tier professional mix and mastering engineer for world-famous artists.

That is the level of care and craft. It is not a fixed sound. A famous record in this song's genre is the bar for skill. The song brief still decides the genre, the references, the effects, and the loudness. Read `checklist.md` while you work, and write the decisions in the song's `mix-notes.md`.

## Gain staging

Nothing clips by accident. Each track hits its plugins at a healthy level, loud enough to work and quiet enough that the plugin is not already distorting. Leave headroom on the mix bus so the master is not only a limiter turned up. If a fader is pinned, fix the level earlier in the chain.

## EQ

EQ in context with the rest of the song, not in solo as the only judge. Cut to make space. Boost when the source needs a character the brief asked for. High-pass only the parts whose low end is mud, and leave the low end that belongs to the kick and bass. After EQ, the part should still sound like itself.

## Dynamics

Use compression for control, punch, or glue. A slower attack lets the hit through. A faster attack holds it down. Set the release so the compressor finishes with the groove instead of pumping against it. Skip the compressor when the performance is already doing the job. A volume ride is often cleaner than more gain reduction.

## Parallel processing

Blend a heavily compressed or saturated copy underneath the untouched signal. The dry path keeps the transients and the tone. The parallel path adds weight or grit. Balance them on the blend, not by crushing the original until it is gone.

## Saturation

A little saturation adds harmonics and helps a part sit. More drive is for audible grit, and only when the brief or the genre wants it. Listen for harshness, extra fizz, and low end that bloomed. If you can hear the distortion and the brief did not ask for it, back it off.

## Bus processing

Drums, music, and vocals can each have a bus for gentle glue. The mix bus can have light EQ or compression once the balance is already right. The mix bus is the wrong place to repair a vocal that was never leveled or a bass that was never EQ'd.

## Sidechain

Sidechain ducking pulls one sound down when another plays. The usual case is the bass or a pad making room for the kick, or a delay making room for the vocal. Time the release to the groove. The pumping is either felt as part of the genre or kept invisible. Say which one you chose.

## Vocal chain

A typical order is: tuning if the song needs it, then subtractive EQ, compression, de-essing, any tonal EQ, and saturation. Delay and reverb go on sends. Skip any step the vocal does not need. The vocal's distance from the track comes from the brief and the references, not from a saved chain.

## De-essing

Control "s" and "t" sounds without a lisp. Work on the harsh band, not the whole vocal. Check the result on earbuds. If the vocal turns dull, the de-esser is doing too much.

## Tuning

Tune only as far as the performance and the genre need. Natural styles stay transparent. Styles that use obvious tuning can go further when the brief asks. Leave a vocal that is meant to sound raw. Do not quantize a style of performance out of the song.

## Stereo imaging

Pan for a picture: leads and low end usually stay centered, supporting parts spread. Width comes from the arrangement and the panning first. A widener is a last touch, checked in mono so nothing important disappears. The chorus is wider than the verse only when the song wants that.

## Spatial effects

Reverb and delay follow `effects-guide.md`. Pre-delay, delay time, and decay are tempo-synced to this song. Prefer sends so the wet amount can change without reprinting the dry sound. Space matches the mood in the brief.

## Automation

The mix moves with the arrangement. Ride vocals and instruments through the lyric and the sections. Draws for filter sweeps, fade-ins, drops, and throws cover the exact bars in the brief. Whole-song moves are automated on the mix bus.

## Reference matching

Level-match the reference before you compare, so a louder master does not win just by being louder. Listen for balance, vocal level, low end, tone, and width. Borrow only what the brief says to borrow from each reference.

## Mastering chain

Master after the mix is right. A practical order is corrective EQ, gentle compression, any tonal EQ, saturation only if it helps, then the limiter last. Stereo moves stay subtle. Metering sits where you can read the limited signal. Do not use the limiter to fix a balance problem.

## Loudness and true peak

Measure the whole song. Integrated LUFS and true peak for this song come from the platforms in the brief and the ranges in `checklist.md`. Write both numbers down. Louder than the playback target usually does not play louder on streaming, and it can cost punch.

## Dithering

Dither is a very low-level noise used only when the file's bit depth goes down, for example a 24-bit session printed to 16-bit. Apply it once, at that last reduction. A 24-bit delivery from a 24-bit session does not get dithered. Do not dither in a limiter and again in the bounce.

## File delivery formats

Deliver the master as interleaved stereo WAV or AIFF at the session sample rate. Do not upsample a 44.1 kHz session to 96 kHz on the way out. 24-bit WAV is the usual file for streaming delivery. 32-bit float is a working format, not the normal store delivery. Return an MP3 preview with the WAV so the owner can listen on a phone. The MP3 is not the master. Put the song title, the version, and the word "mix" or "master" in the file name, and write the sample rate, bit depth, LUFS, and true peak in `mix-notes.md`.

## Translation checks

The mix is not finished on studio monitors alone. Listen on earbuds, a phone speaker, and in a car, at a normal volume and once quieter. Fix what fails on more than one system. Leave what is clearly part of the sound, and say so in the notes.

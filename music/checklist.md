# Mixing and mastering checklist

Answer these for the song in front of you. Read that song's `brief.md` first.

A "yes" is not always the goal. The goal is a decision you can explain from the genre, the reference tracks, and the arrangement. Write the decision in the song's `mix-notes.md`.

Two loudness words, in plain English:

- **LUFS** measures how loud the whole song feels, not just the tallest spike.
- **True peak (dBTP)** estimates the highest spike, including peaks that can appear after a file is encoded for streaming. Going over 0 dBTP can distort on playback.

## Gain staging

- Is any track, bus, or the mix bus clipping before you meant it to?
- Does each track have a usable level, so you are not pushing a fader to the top just to hear it?
- Is there comfortable headroom on the mix bus for mastering? A common habit is to keep mix-bus peaks several dB under 0 so the master is not only a limiter turned up. The right amount depends on how dense this song already is.
- Are you solving a level problem with gain, or covering a balance problem with a plugin?

## Balance

- At each section, what should the listener notice first, and is that actually in front?
- If the song has a chorus, drop, or breakdown, does the size of those sections match the arrangement?
- Are supporting parts supporting the lead, or covering the same space?
- How do the reference tracks balance the lead against the track, and where should this song differ?

## EQ

- What problem in the brief is EQ supposed to fix: mud, harshness, thinness, or a part that will not sit?
- Are you cutting or boosting because of this arrangement, rather than reusing the last song's curve?
- Does low end that belongs to the kick or bass stay out of parts that do not need it?
- After EQ, does the part still sound like itself?

## Compression

- Does this part need more control, more punch, or more glue, or is it already doing its job?
- Is the compression helping the genre, or making a dynamic song smaller than the brief asks for?
- Can you hear the compressor pumping or dulling the part? If you can, is that on purpose?
- Would a volume ride do this job with fewer side effects?

## Low end and the kick-bass relationship

- Can you tell the kick and the bass apart on monitors and on a small speaker?
- Do they occupy the same hits on purpose, or does one move out of the way (sidechain, arrangement, or EQ)?
- Which one owns the sub, and which one owns the note you can hear on a phone?
- Does the low end hold together in mono, without a big drop or a big bloom?
- How do the reference tracks treat kick versus bass, and what are you copying versus leaving?

## Vocals

Skip this section if the song has no vocal. Say that in the notes.

- Is the vocal as close, or as set back, as this style wants?
- Are the words clear without the vocal turning thin, harsh, or louder than the track?
- Do doubles, harmonies, and ad-libs match the brief, or are they leftovers from another song?
- Is sibilance ("s" and "t" sounds) under control without lisping?
- Does the vocal still sit in the track when the music gets loud?

## Space, reverb, and delay

- What kind of room does the mood in the brief call for: dry, close, wide, or far away?
- Is the reverb or delay supporting the part, or washing out the words and the groove?
- Are delay time, pre-delay, and decay taken from this song's timing table, or from host tempo sync at this song's BPM? A guessed millisecond value does not pass. Double-check the math in `effects-guide.md`.
- Are effects on a send, so you can change the wet amount without reprinting the whole sound?
- What space do the references use, and what should this song not copy?

## Creative effects

Read **Creative effects requests** in the brief. Build them the way `effects-guide.md` describes.

- Did you acknowledge every request in `mix-notes.md` (effect, one track or whole mix, spot, length in bars, plugin) before treating the mix as underway?
- Is each effect on the exact word, hit, bar, or mix-bus moment the owner named, for the length they named?
- If the request is the whole song, is it automated on the mix bus or master, across those bars, rather than only on the vocal?
- If a plugin was named, is it the one in the session? If it cannot run on the Linux computer, did you build the same effect another way and write both names in the notes?
- For a reverse reverb, does the swell finish as the word or hit starts?
- For a filtered, distorted fade-in, on a track or on the whole mix, are the filter opening, the distortion coming down, and the volume coming up all moving across the same bars?
- For a throw, riser, sweep, drop, transition, tape stop, or beat switch, does it land on the beat the brief names?

## Stereo width and mono compatibility

- Is the width coming from panning and the arrangement, or mostly from a widener?
- Are the parts that should stay solid (often vocal, kick, bass, and snare) still solid in the center?
- Does anything important disappear, thin out, or jump in level when you sum to mono?
- Is the chorus wider than the verse only if the song actually wants that?
- Do the sides still sound good, or are they harsh and phasey?

## Automation

- Does the energy follow the arrangement, including intros, drops, and endings?
- Are vocal and instrument rides written for this lyric and this section?
- Did you automate the specific problems named in the brief, such as a harsh word, a loud hit, or a chorus that sinks?
- Would a static plugin setting fight the song less than a move, or the other way around?

## Loudness and true peak

Measure the full song from start to finish. Write down integrated LUFS and maximum true peak for each master version.

These are **typical published targets**. They vary by platform, by genre, and over time. They are reference ranges, not pass/fail rules. A quiet ballad and a dense club track should not be forced to the same density just to match a number. Services turn loud masters down in playback. Louder than the target usually does not play louder, and it can cost punch.

| Where | Typical target | True peak | How to use it |
| --- | --- | --- | --- |
| Spotify | -14 LUFS integrated on the Normal setting. Listeners can choose Loud (-11 LUFS) or Quiet (-19 LUFS). | Below -1 dBTP. If the master is louder than -14 LUFS, Spotify asks for true peak below -2 dBTP. | Spotify's own mastering note suggests aiming the master at -14 LUFS and staying under -1 dBTP. Most listeners leave the app on Normal. |
| YouTube | About -14 LUFS. Louder uploads are turned down. | A commonly used ceiling is -1 dBTP. | Treat this as the usual cited reference, not a law. YouTube does not boost every quiet upload up to the line. |
| Apple Music | About -16 LUFS is the widely cited Sound Check playback level. Apple does not publish one required stereo LUFS number. | At or below -1 dBTP. Apple's published advice is to leave at least 1 dB of headroom. | Master for the song. Sound Check evens out playback and does not add limiting. |
| Amazon Music | About -14 LUFS. | At or below -1 dBTP is the safe shared ceiling. | Track-by-track normalization is the commonly cited behavior. |
| Tidal | About -14 LUFS. | At or below -1 dBTP is the safe shared ceiling. | Tidal is cited as normalizing by album, including when a song shows up in a playlist. |
| Deezer | About -15 LUFS. | At or below -1 dBTP is the safe shared ceiling. | Close to the other music services, not a reason for a separate crushed master. |
| AES streaming recommendation | About -16 LUFS for music. About -14 LUFS for the loudest song when a whole album is normalized. About -18 LUFS for speech. | -1 dBTP is the ceiling usually discussed with this. | This is the Audio Engineering Society's recommendation for how services level playback (document AESTD1008, as commonly summarized). It is not an order to master every song to one number. |
| European radio and TV (EBU R 128) | -23 LUFS for the programme. Some radio distribution paths sit about -20 to -16 LUFS. | Do not exceed -1 dBTP in production. | This is the European broadcast standard, including radio production. It is much quieter than a typical streaming pop master. The station can still process the audio on the way to FM. |
| US commercial radio | No single published LUFS target the way Spotify has one. | At or below -1 dBTP. | The station's processor sets the on-air loudness and tone. A clean, balanced master survives that better than a master that is already crushed. |

Questions for this song:

- Which platforms does the brief name? If it names more than one, which reference are you using, and why?
- What integrated LUFS and true peak did this version measure?
- After limiting, does the chorus still punch, and do the quiet parts still feel quiet on purpose?
- If this song belongs to an EP or album, should it be quieter or louder than the others, and did you keep that gap?
- Would pushing louder than the references above help the genre, or only the meter?

## Translation checks

Listen at a normal volume and once a bit quieter. Write a line for each system in `mix-notes.md`.

- **Earbuds** — Are the vocal, kick, and bass still clear? Is anything harsh in the top end?
- **Car** — Does the low end boom or vanish? Does the vocal stay in front of road noise?
- **Phone speaker** — With almost no bass, does the song still read? Are the mids crowded?
- **Studio monitors** — Does the mix you approved still match the brief, or did the small speakers reveal a problem to fix here?

After the checks:

- What failed on more than one system?
- What will you change, and what will you leave because it is part of the sound?

## Definition of done

A song is not finished until every item here is true. Then the owner signs the master under **Final sign-off** in `mix-notes.md`. A work-in-progress export does not clear this list.

- Are all requested creative effects in place, on the right track or on the mix bus, at the right spot, for the right length? If a named plugin could not run here, is the stand-in tool written in the notes?
- Are echoes, delays, pre-delay, and decay timed from this song's BPM, with the math double-checked?
- Do the translation checks on earbuds, phone speaker, car, and studio monitors pass, with the results written down?
- Do the measured integrated LUFS and true peak meet the targets chosen for this song's platforms?
- Was the master compared with the reference tracks, and are the differences on purpose?
- Has the owner signed off on the final master?

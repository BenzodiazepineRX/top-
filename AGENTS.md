# Rules for every agent in this workspace

This workspace mixes and masters the owner's (Kenshin's) songs. These rules apply to every agent:
Claude, Codex, Gemini, Cursor, Copilot, Grok Bot and any other.

## The standard comes first (strict, must follow)

**Read `.claude/skills/pro-mix-master/SKILL.md` in full before touching audio.** It is the owner's
Pro Mix & Master Standard. Its rules are strict and non-negotiable. Where anything below or in older
notes disagrees with it, the standard wins.

- The bar is radio-ready, stream-ready, major-label quality on every song. "Good enough", "pretty
  close" and "fine for a demo" never count as finished.
- Rule 0: every song is a new project. No presets. Every value comes from this song's own
  measurements, its reference and the owner's intent, and is logged with its reason in the song's
  `mix_config.json`. A previous song's settings are only a hypothesis to re-measure.
- Work in gates (0 intake and forensics, 1 vocal cleanup/tone/pocket, 2 space/delays/throws,
  3 balance/automation/mix bus, 4 master, 5 QC and delivery). Never one-shot.
- One measured fault, one precise move. Never stack cuts, compressors or de-essers.
- Never let the limiter do the mixing: at most 3-4 dB gain reduction on the loudest 1% of hits.
  True peak at or below -1.0 dBTP, or at or below -2.0 dBTP when louder than -14 LUFS, and under
  0 dBTP after MP3/AAC encoding.
- Nothing ships until QC passes three clean rounds in a row on the 24-bit WAV, the 16-bit WAV and
  the decoded MP3. Until the owner approves, everything is "draft, not final".
- Never claim to have listened. Never call a mix "perfect" or "radio-ready" if any check failed.

## Owner corrections (newer than older notes; these override them)

- **Echoes: there is no default.** Echoes are different on every song. Before applying any echo,
  ask the owner how he wants them on this song (which words, timing, repeats, levels, tone). The old
  "last word only" rule is wrong and must not be used.
- **Reference track: chosen per song.** "Top8 (Extended Network)" is not a default reference. Ask the
  owner which reference(s) to use for each song.
- **No fixed loudness or vocal-level numbers carry over between songs.** Loudness is picked per song
  by the limiter rule above; vocal levels come from the reference and the owner's ears.

## Before any processing

1. **Read the lessons notebook.** `deliveries/LEARNINGS.md` is the shared notebook every agent reads
   first and adds to after every song and every round of feedback. Older lessons in
   `music/LESSONS.md` are being merged into it; until that is done, read both, and where they
   disagree with the corrections above, the corrections win.
2. **Find out what is on every file, from the owner's ears.** Run
   `python3 music/tools/stem_intake.py --stems ... --out intake/`, send him the solo previews and the
   question sheet it writes, and wait. A file's name does not settle what it contains.
3. **Ask whether a cleaner export exists,** with the beat and each vocal as separate files and only the
   autotune on.
4. **Ask which effects he wants** on this song, how he wants the echoes, which reference to use, and
   which effects in his own version he wants kept.
5. **Take the beat grid from the hats and kick clicks** (`stem_intake.py --bpm`), and confirm the tempo
   by matching the drum pattern against itself several bars apart.

## Making a version

6. **Approved past songs are a starting hypothesis, not a preset.** An approved lead's tone, levels
   and loudness can guide where to look, but every value is re-measured and derived for this song and
   logged in `mix_config.json`.
7. **Measure before boosting or cutting.** Lift only what the vocal lacks, and cut only what it has in
   excess, exactly where measurement finds it. No saturation and no bright shelf unless a measurement
   or the owner asks for it.
8. **Echoes and delays follow the owner's instructions for this song,** computed from the verified BPM
   in exact ms and samples, tail-padded 3-5 s to decay below -60 dBFS, and ducked or skipped where they
   would collide with a dry vocal.
9. **One purpose per version.** Change what the last feedback named and nothing else, and log the
   before/after diff. Send a loudness-matched clip of the previous version followed by the new one,
   with the times to listen at and three to five questions he can answer in a few words.
10. **After a sign-off, stop.** If he asks for more, start from the approved file and change only what
    he names. Never build on a version he rejected. Version every render (_v1, _v2) and never overwrite.

## Keeping the record

11. **One `mix-notes.md`, one `mix_config.json` and one version sequence per song,** whichever agent is
    working. Newest entry at the top, with the owner's exact words.
12. **Say what was measured and what was heard.** A number is not approval, and a second agent's
    agreement is not approval either.
13. **When a song teaches something new, add it to `deliveries/LEARNINGS.md` in the same change.**
14. **No audio and no secrets in commits** unless the owner asks for the audio to be stored here.

## Talking with the owner

He reviews on a phone, usually on headphones, and is new to audio terms. Use plain words and explain a
term the first time. Say which file to play first and what to listen for. Resend files when asked.

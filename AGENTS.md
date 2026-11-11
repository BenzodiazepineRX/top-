# Rules for every agent in this workspace

This workspace mixes and masters the owner's songs. Read this page first, then `music/LESSONS.md`, then
the song's `brief.md` and `mix-notes.md`.

No agent here can hear. The owner's words about a version are the only verdict.

## Before any processing

1. **Read `music/LESSONS.md`.** It holds what every earlier song taught: what the owner has approved,
   what he rejects and why, the echo rules, and the measurement traps that each cost a version.
2. **Find out what is on every file, from the owner's ears.** Run
   `python3 music/tools/stem_intake.py --stems ... --out intake/`, send him the solo previews and the
   question sheet it writes, and wait. A file's name does not settle what it contains.
3. **Ask whether a cleaner export exists,** with the beat and each vocal as separate files and only the
   autotune on.
4. **Ask which effects he wants,** using the list in `music/LESSONS.md` of what he asks for on nearly
   every song, and which effects in his own version he wants kept.
5. **Take the beat grid from the hats and kick clicks** (`stem_intake.py --bpm`), and confirm the tempo
   by matching the drum pattern against itself several bars apart.

## Making a version

6. **Start from what is already approved.** Match the lead's tone toward an approved lead. Use the
   approved levels, loudness and layer order as the starting point. Write down which approval you used.
7. **Measure before boosting or cutting.** Lift only what the vocal lacks against the approved lead,
   and cut only what it has in excess. No saturation and no bright shelf unless a measurement or the
   owner asks for it.
8. **Follow the echo rules in `music/LESSONS.md`.** Last word only, whole word, on a main beat of the
   song's own grid, never stacked on an older echo.
9. **One purpose per version.** Change what the last feedback named and nothing else. Send a
   loudness-matched clip of the previous version followed by the new one, with the times to listen at
   and three to five questions he can answer in a few words.
10. **After a sign-off, stop.** If he asks for more, start from the approved file and change only what
    he names. Never build on a version he rejected.

## Keeping the record

11. **One `mix-notes.md` and one version sequence per song,** whichever agent is working. Newest entry
    at the top, with the owner's exact words.
12. **Say what was measured and what was heard.** A number is not approval, and a second agent's
    agreement is not approval either.
13. **When a song teaches something new, add it to `music/LESSONS.md` in the same change.**
14. **No audio and no secrets in commits** unless the owner asks for the audio to be stored here.

## Talking with the owner

He reviews on a phone, usually on headphones, and is new to audio terms. Use plain words and explain a
term the first time. Say which file to play first and what to listen for. Resend files when asked.

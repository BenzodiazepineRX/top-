# Lessons from every song so far

Read this before starting or revising any song. It gathers what each song's notes recorded, so that a
lesson paid for on one song is not paid for again on the next. Last updated 2026-11-11.

Sources: each song's `mix-notes.md` on its own branch (pull requests #2 to #9) and the Satan's Casino
session log in `music/songs/satans-casino/`. No agent here can hear. Every verdict below is the owner's.

Where this page and an older page disagree (`tools/workflow.md`, `../agents/music_engineer.md`), this
page is the newer evidence. A song's own brief still wins over all of them.

## Scoreboard

| Song | Versions made | Verdicts on record | What the extra versions went on |
|---|---|---|---|
| Pushing the Interstate | at least 26, plus a "final" | v2 "masterpiece". v3 "LOVED". v4 signed off on 2026-11-08. Nothing is written down for v18 onward | Twenty-two versions after the sign-off, nearly all on echo timing, the outro echoes and the stutters |
| Driftin' Away | 6 | v1 "nearly perfect". v6 not answered yet | Which layer sits over which; effects too quiet; one timing bug |
| Baccdoor | 4 | v1 and v2 harsh, scratchy, "ampy". v3 "Nearly PERFECT". v4 not answered yet | The lead's tone |
| Don't Need Closure | 2 | v2 "W" | Reverb and level of the adlibs |
| Old Motorola | 1 mix, then 7 fixes within an hour | none written down | How much echo; adlib level |
| Satan's Casino | 6 in one workspace, 6 in another | v2 (first workspace) "all wrong". v02 (second) rejected. None approved | A wrong guess about what each track was; harshness; echo placement. Both workspaces had incomplete files |
| Apart / Other Half | none yet | | Brief only |

The count fell from song to song because each later song reused something the owner had already
approved: an approved lead's tone, the loudness, the layer order, the echo rule. That is the method.
**Start every song from what is already approved, and say in the notes which approval you started from.**

## What the owner has approved

Use these as the starting point on a new song. They are one artist's taste on seven songs, not laws.

| What | Starting point | Where it was approved |
|---|---|---|
| Lead tone | Match toward an approved lead: the Driftin' Away lead, the Baccdoor v4 lead, or Pushing the Interstate v3 | Baccdoor matched 85% toward Driftin' Away and went from "scratchy" to "Nearly PERFECT". Don't Need Closure matched 90% toward Baccdoor v4 and got "W" |
| Lead level | About 0.5 dB under the beat, K-weighted, measured while singing | Driftin' Away v2 onward, Baccdoor v3, Don't Need Closure |
| Adlibs and background vocals | 6 to 6.5 dB under the leads, measured only where both sing, bar by bar | Don't Need Closure v2 ("W"). Old Motorola settled on the same figure after its fixes |
| A repeat of a line | About 4 dB under the line it repeats, never over it | Driftin' Away v5 |
| Layer order | Lead, then background vocals, then their repeats | The owner's rule, Driftin' Away v5 |
| Sections | Verse and later sections within about 1 dB of each other | Driftin' Away v2 to v6 |
| Master | -11.5 to -12.1 LUFS, true peak -0.7 to -1.2 dBTP | Every accepted version |
| Lead reverb | Plate, about a dotted half or one bar long, return about 17 dB under the lead | Driftin' Away v2; not raised again |
| Adlib reverb | Little or none added | Don't Need Closure v2 |

What the owner asks for on nearly every song: echo throws on the last words, "perfectly timed", filling
the gaps; reverse reverb into a drop or a word; a telephone voice; stutters into a word; a fade-out.
Ask about each of these in the brief instead of waiting for the request to arrive as a correction.

## What the owner rejects, and what caused it

| The owner's words | Songs | Cause found | What fixed it |
|---|---|---|---|
| "Scratchy", "ampy", "harsh", "amplifying", "grainy", "max treble" | Baccdoor v1 and v2; Satan's Casino v2 and v3 | A presence boost, saturation, firm compression and a bright shelf on phone recordings that were already bright. A stereo effect baked into the export. A vocal rebuilt from its quiet channel | Leads in mono. Tone matched toward an approved lead. Then a cut at 2.5 kHz and a small lift at 5.5 kHz for clear words |
| "Way too much reverb"; "slightly too much reverb"; "you added more reverb to the main vocals" | Don't Need Closure v1; Driftin' Away v1; Interstate v12 | Reverb added on top of reverb already in the file. Compression lifting that baked-in tail | Less return. No reverb added to adlibs. Tails turned down |
| "Way too much delay, it distracts the listener" | Interstate v12 | An echo on every word | Last word only |
| Echoes he could not hear | Interstate v11; Driftin' Away v1 to v5 | Echo level 13 to 32 dB under the word | First echo 3 to 12 dB under the word, then ask "more or less?" |
| Echoes "off", "late or early", "not perfectly timed" | Interstate v4 to v15 | See the echo rules below. A different cause was found on almost every version | |
| "The repeat is louder than the main"; adlibs too quiet; adlibs louder than the main | Driftin' Away v1 and v3; Satan's Casino v2 and v4 | A whole track moved up or down with no check of each phrase against the line it answers | Per-phrase levels with a written check |
| The song "going quiet" at points | Interstate v1 | The limiter pulling the mix down 5 to 7 dB on 808 hits | A lower loudness target, and control of the 808's peaks |
| Reverse swells and build-ups too quiet | Driftin' Away v2 | Swells 6 dB under the word | Swell peak level with the word |

Boosting is not always wrong. On Interstate the lead arrived dark and boxy, and a presence lift, an air
shelf and light saturation were part of the "masterpiece". On Baccdoor and Satan's Casino the same moves
were rejected. **Measure the vocal against an approved lead first, then lift only what is missing and
cut only what is in excess.**

## Echo rules

Echo timing has cost more versions than everything else combined. These rules are what survived.

1. **Echo the last word of a line, not the line.** Whole lines stack and never seem to fade
   (Interstate v12). One exception is on record: in Old Motorola, from 1:40 to 2:03, the owner wanted
   the delay to follow the whole vocal. Ask.
2. **Cut the word from its real start to its real end, with a short fade.** A fixed 0.30 s slice began
   mid-word and ended early (Interstate v4 to v15; Satan's Casino v02 in the second workspace).
3. **Keep each copy under one beat long.** Longer copies cover the next beat (Interstate v15, v17).
4. **Start the first echo after the word has finished, on a main beat** (Interstate v10 and v15).
5. **Take the grid from this song's drums, not from 0:00 of the file.** The grid began 38 ms into
   Driftin' Away, 17 ms into Baccdoor and 0.955 s into Don't Need Closure.
6. **Do not move single echoes onto single drum hits.** That was Interstate v7, and the owner rejected
   it. `tools/workflow.md` still recommends it under "Lock echoes to the drums"; that paragraph is out
   of date. Echoes on the main beats of a grid measured from the drums were accepted on three songs.
7. **Two to four repeats, each about 5 dB quieter and darker, then stop.** Eight slow half-note echoes
   on the last line of a song.
8. **Duck lightly and fast: 3 to 4 dB, release 80 to 120 ms.** Heavy, slow ducking made exact echoes
   surface 15 to 36 ms late (Interstate v5).
9. **Never lay new echoes over old ones.** Check every supplied file for echoes already printed in it.
   Interstate's effects stem held about 216 of them, and new layers on top could not fix what he heard.
   Rebuild from the stems or remove the old copy first.
10. **After the owner approves a version, change only what he names, starting from that approved file.**
    Interstate v9 to v15 were new mixes built on rejected versions, and each one moved further away.
11. **Check by measurement before sending:** correlate each word with its echo, and check cut points
    near the end of the song as well as the start.
12. **Stutters:** the owner's definition is the first part of the first syllable, repeated three or four
    times before the word. He later preferred longer cuts, at least an eighth note. Ask which.

## Traps that cost a version

| Trap | Where | What it did | The check |
|---|---|---|---|
| A tempo fit locked onto 128.71 instead of 129 BPM | Interstate v4 | The outro went off beat | Match the drum pattern against itself several bars apart |
| Bar lines taken from the kick's low end | Satan's Casino v6 | Every bar line 95 ms late; a sweep took 16.5 dB of bass off a downbeat | Use hats and kick clicks: `tools/stem_intake.py --bpm` |
| A time step of 2.494 ms treated as 2.5 ms | Driftin' Away v1 to v5 | Cuts drifted to 0.3 s late by 2:18; echoes were cut from word tails | Check cut points late in the song |
| `ms-bus` adds a +2 dB treble shelf when `--mid-shelf` is left out | Baccdoor v2 | A brighter mix than intended | Always pass `--mid-shelf 9500:0` unless a shelf is wanted |
| Waveform correlation on autotuned vocals | Baccdoor v1 | False offsets of -70 to +42 ms | Align pitch-shifted vocals by their envelope |
| Compression on a track that arrives with reverb | Don't Need Closure v1 | Tails rose from 20 dB to 6 dB under the words | Measure tails after any dynamics |
| A level ride measured over whole windows | Baccdoor v1 | Near-silent parts boosted 13 dB | Measure only where both layers sing; clamp the gain |
| A ducker keyed by overall level | Baccdoor v4 | Active 68% of the time, so it was a static cut | Key it by the band it protects; read the percent active |
| A panned track measured on one channel | Satan's Casino v5 | Level under-read by 8 dB | Measure the mono sum |
| A track's role taken from its name | Satan's Casino v1 and v2 | Two versions built on the wrong picture | Send solo previews and ask (`tools/stem_intake.py`) |
| A "moved" count from one detector | Interstate v14 | Half the echo copies were missed | Confirm coverage with a second, independent detector |
| Word times from a speech model on sung lines | Satan's Casino, second workspace | Low-confidence boundaries | Ask the owner for the lyric sheet; flag low scores |

## Sources: ask for the cleanest files first

- The same song can exist in a better form somewhere else. Satan's Casino was mixed in one workspace
  from an app bounce in which the beat and the lead vocal were one clipped track, while clean, separate
  beat and lead files sat in a folder the other workspace used. Ask: "Is there another export of this
  song, with the beat and each vocal as separate files?"
- Beats are often YouTube rips with nothing above 15.6 to 16.6 kHz. Do not boost the top. Ask for the
  producer's WAV, and note that a free beat usually needs a lease or credit before release.
- Vocal exports often carry effects from the recording app: a stereo effect (Baccdoor leads), a long
  reverb (Don't Need Closure adlibs), panning (Satan's Casino adlibs). Ask for an export with only the
  autotune on.

## How the workspace itself cost tries

- **Nothing has been merged.** All nine pull requests are open, and `main` holds only a starter script.
  An agent that starts from `main` sees no playbook, no toolkit and no song notes. A lesson written on
  one song's branch is invisible from every other branch.
- **Two agents numbered versions of the same song separately.** Interstate has two different v8 to v14.
  Use one version sequence per song and one `mix-notes.md`.
- **Later versions were built on rejected ones** instead of on the approved file.
- **Interstate v18 to v26 and the "final" have files but no notes,** so nobody can say what changed or
  which file the owner prefers.
- **The older pages tell agents to "listen".** Where they say listen, send the owner a loudness-matched
  comparison and wait for his words.

## Open items the owner can close in one message each

- Pushing the Interstate: which file is the keeper, v4, v17 or the "final"?
- Driftin' Away v6 and Baccdoor v4: approved, or what is left?
- Satan's Casino: see `songs/satans-casino/README.md`. The full set of stems now exists across the two
  workspaces, and no version built so far has used all three.

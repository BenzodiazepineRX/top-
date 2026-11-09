# Music workflow

Use this path for every song. The point is to decide what *this* song needs, then write those decisions down so the next agent can follow them.

The checklist in `checklist.md` is a list of questions, not a fixed chain of plugins. Before mixing, read `../agents/music_engineer.md`. It is the base playbook. The song brief still wins. Also read:

- `engineering-standards.md` — the level of craft expected on every song
- `effects-guide.md` — creative effects on one track or the whole mix, and how to turn BPM into delay times
- `daw-setup.md` — how agents mix on the Linux computer today, and the DAWs planned for later
- `tools/workflow.md` — the processing toolkit: the scripts that measure, mix, master and export the song

## Who does what

Anyone can help at any step. These are the usual jobs:

- **General assistant** — create the song folder, keep the brief filled in, and make sure notes are easy to read.
- **Producer / mix engineer** — balance, tone, space, loudness, and the reasons behind those choices.
- **Studio agent** — monitoring, listening level, and checks on real playback systems.
- **DAW agent** — runs the Linux session in REAPER, Ardour, or with ffmpeg, SoX, and Python. Takes the owner's stems and returns a WAV plus an MP3 preview. Later, on the owner's computer, this agent operates Pro Tools first, and also Logic Pro or FL Studio.

If a step is not your job, leave a short note and hand it to the agent who owns it. Do not guess and move on.

## Steps

### 1. Create a song folder from the template

Copy `music/songs/_template` to a new folder under `music/songs/`.

Name the folder after the song, in lowercase with hyphens, for example `music/songs/midnight-drive`.

Do not edit files inside `_template`. That folder stays blank so the next song starts clean.

### 2. Fill in the brief

Open the new folder's `brief.md` and fill in every section before mixing.

The brief is the source of truth for that song: genre, mood, tempo, key, reference tracks, stems, what already works, what is wrong, where it will be heard, creative effects, and the deadline.

Fill in the delay-timing table from this song's BPM. The formulas are in `effects-guide.md`. If the tempo changes mid-song, add a second table for the other BPM.

If a fact is unknown, write "unknown" and the question to ask. Do not leave a blank that the next agent might invent an answer for.

### 3. Mix

Read `brief.md`, then `../agents/music_engineer.md`, then work through `checklist.md`. The playbook is the starting craft. The brief is the plan for this song.

Answer the questions for this song. Genre, references, and arrangement decide the settings. Write the choices in `mix-notes.md` as you go, including what you tried and what you rejected.

Before you change the sound, acknowledge every line under **Creative effects requests**: effect, whether it is one track or the whole mix, exact spot, length in bars, and plugin. Then build those effects. `effects-guide.md` is the method. The owner's request wins over a habit from the last song.

### 4. Master

Master after the mix is ready to master. Fix mix problems in the mix. The master is for overall level, tone, and translation, not for repairing a balance that was never settled.

Use the loudness section of the checklist as a reference. Platforms and genres differ. Hit the feel the brief asks for, then measure loudness and true peak and write the numbers down.

### 5. Check on more than one system

Listen on the systems named in the brief. At minimum, check:

- earbuds
- a car
- a phone speaker
- studio monitors

Write what changed between them. A mix that only works on one pair of speakers is not finished.

### 6. Log versions

Every export gets an entry in `mix-notes.md`: the date, the version name, the WAV file name, the MP3 preview file name, what changed, why it changed, and what the listening check said. Details of that handoff are in `daw-setup.md`.

Keep older notes. They are how the next session knows what already failed.

A rough mix can still be exported for feedback before the steps below are all true. Label that version as a work in progress in `mix-notes.md`. It is not the finished song.

## Definition of done

No song is finished until it passes this full final check. The same list is in `checklist.md`. The owner signs the final master in that song's `mix-notes.md`.

- Every creative effect in the brief is in the session, on the track or on the mix bus the brief names, at the word, hit, or bar requested, for the length requested. Whole-song moves are automated across those bars. If the brief names a plugin that runs here, that plugin is the one in use. If it does not run on the Linux computer, the notes name the stand-in tool and the effect itself still matches the request.
- Echoes, delays, reverb pre-delay, and reverb decay are tempo-synced to this song's BPM. The timing table in the brief is filled in, and someone double-checked the math against `effects-guide.md` or the DAW's synced readout.
- Translation checks on earbuds, a phone speaker, a car, and studio monitors are written in the notes. Problems that showed up are fixed, or the notes say why they stay.
- Loudness and true peak meet the targets chosen for this song. Pick those targets from the platforms named in the brief, using the ranges in `checklist.md`. Write the measured LUFS and true peak next to the target.
- The master was played against the reference tracks in the brief. The notes say what matches, and what was left different on purpose.
- The owner signs off on the final master in the **Final sign-off** section of `mix-notes.md`.

Until that sign-off is written, the song is still in progress.

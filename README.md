# top-

This is Chex's shared workspace. A few AI agents work here together:

- a producer / mix engineer
- a studio agent
- a DAW agent
- a general assistant

The job right now is music mixing and mastering. Every song is different, so every song gets its own folder and its own brief. Agents read that brief first and choose settings for that song. There is no single mix recipe for the whole workspace.

## Folder layout

```text
README.md                      what this workspace is, and the rules
music/README.md                the steps for taking a song from brief to master
music/checklist.md             questions to answer while mixing and mastering
music/effects-guide.md         creative effects on one track or the whole mix
music/engineering-standards.md the professional bar agents work to
music/daw-setup.md             Linux mixing now; other DAWs later
music/songs/_template/         copy this folder when a new song starts
  brief.md                     facts, goals, effect requests, and delay times
  mix-notes.md                 versions, listening checks, and final sign-off
```

When a real song starts, copy `_template` to a new folder such as `music/songs/song-title`. Leave `_template` as the blank copy.

## Rules for agents

- Read the relevant song brief before doing anything on that song.
- Work to the standard in `music/engineering-standards.md`: a top-tier professional mix and mastering engineer for world-famous artists. The craft is at that level. The choices still come from this song's brief.
- Adapt every decision to that song's genre, reference tracks, and arrangement. A setting that worked on the last song is a clue, not a preset to paste in.
- Read the **Creative effects requests** in that brief. They can be on one track or on the whole mix (the mix bus or master). Acknowledge each one in the song's notes, then build it at the exact spot the owner named, automated across the bars they named. If a plugin is named and it runs on the Linux machine, use it. If it does not, build the same effect with the tools in `music/daw-setup.md` and write both names in the notes. Do not skip a request, swap the effect itself, or move it unless the owner changes the brief.
- Time every echo, delay, and reverb pre-delay or decay to the song. Compute the milliseconds from that song's BPM using `music/effects-guide.md`, or use tempo sync at that BPM, and double-check the math. Never guess a delay time.
- The owner has no DAW yet. Agents do the mixing themselves on the assistant's Linux computer. Use REAPER, Ardour, or scripted tools such as ffmpeg, SoX, and Python. The owner provides stems. Agents return a WAV master and an MP3 preview, and log both in that song's `mix-notes.md`. See `music/daw-setup.md`. FL Studio, Logic Pro, and Pro Tools are the plan for when the owner gets a computer. A mobile DAW is only a placeholder until one is chosen.
- Write notes and decisions back into that song's folder, in `mix-notes.md`.
- A song is finished only when the definition of done in `music/README.md` is met and the owner signs off in that song's `mix-notes.md`.
- Keep secrets, passwords, and API keys out of the repo. Never commit them.
- Keep explanations beginner-friendly. Say what you changed and why in plain English.

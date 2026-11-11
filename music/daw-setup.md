# DAW setup

The owner does not have a DAW yet. A mobile DAW may come later. A computer with FL Studio, Logic Pro, and Pro Tools may come after that. Those later plans are at the bottom of this page. They are not the way songs get mixed today.

## Right now: agents mix on Linux

Agents choose their own tools and do the mixing and mastering themselves on the assistant's Linux computer. The owner does not click through a session.

### Workflow

1. The owner provides the stems and a filled-in `brief.md` for that song.
2. Agents process the stems on the Linux computer.
3. Agents return two files for each version they want heard:
   - a **WAV** of the mix or master (this is the real deliverable)
   - an **MP3** preview, so the owner can listen on a phone
4. Agents log the version in that song's `mix-notes.md`: date, version name, both file names, what changed, and why.

Save the files in the song's folder. The WAV is the master or the mix. The MP3 is only a preview.

### Tools

Pick the tool that can do the job, and name it in the notes.

- **REAPER** or **Ardour** for a real session: tracks, buses, automation, and the bounce.
- **ffmpeg**, **SoX**, or a **Python audio library** when the move has to land on an exact sample. The ready-made toolkit for this lives in `music/tools/` (see `music/tools/workflow.md`). Use these for tempo-synced delays, reversed reverb tails, gain fades, and filter moves across a set number of bars.

Delay times still come from that song's BPM table in the brief. A script uses those milliseconds. Tempo sync inside REAPER or Ardour is fine when the session tempo is the song's BPM. Either way, double-check the math in `effects-guide.md`. Never guess a delay time.

### When the brief names a plugin

Use that plugin if it actually runs on the Linux machine. If it only exists in FL Studio, Logic, or Pro Tools, build the same effect with REAPER, Ardour, or a script. In the notes, write the plugin the owner asked for and the tool you used in its place. That list is what gets rebuilt when the owner's computer arrives. Do not drop the effect.

## Rule for agents

Do the mix. Return the WAV and the MP3. Log them in `mix-notes.md`.

For every version, the notes still need enough detail to repeat the work: the tool, the track or bus, the settings that matter, delay times as a note value and in milliseconds, and automation as a start bar, an end bar, and what moved.

## Future plan: the owner's computer

When the owner has a computer, agents take over that desktop and operate the DAW themselves. Pro Tools is the first choice on that computer. Logic Pro and FL Studio are in scope too.

The sections below are placeholders. Fill them in when that computer and the real sessions exist. Do not invent a studio convention and treat it as already decided.

## Pro Tools

First choice on the owner's future computer.

### Session organization conventions

To be filled in when the studio computer is set up.

- Track order and color:
- Bus names (drums, music, vocals, mix bus):
- Where the mix bus and the master live:
- How a new song is created from a blank session:

### Export / bounce settings

To be filled in when the studio computer is set up.

- Bounce source (mix bus or master):
- File type, sample rate, and bit depth:
- Offline or real-time, and why:
- Dither: only if this bounce lowers the bit depth

### Naming

To be filled in when the studio computer is set up.

- Session file name:
- Bounced mix and master file names:
- Where the bounce is saved in the song folder:

## Logic Pro

### Session organization conventions

To be filled in when the studio computer is set up.

- Track stacks and bus names:
- Where the stereo out or a dedicated mix bus is used:
- How a new song is created from a template, once a template exists:

### Export / bounce settings

To be filled in when the studio computer is set up.

- Bounce source:
- PCM format, sample rate, and bit depth:
- Normalize: leave off unless the brief says otherwise
- Dither: only if this bounce lowers the bit depth

### Naming

To be filled in when the studio computer is set up.

- Project file name:
- Bounced file names:
- Where the bounce is saved in the song folder:

## FL Studio

### Session organization conventions

To be filled in when the studio computer is set up.

- Playlist, mixer, and pattern habits for a song session:
- Mixer track names and the route to the master:
- How stems land on the mixer:

### Export / bounce settings

To be filled in when the studio computer is set up.

- Mode (full song, not a loop unless the brief asks for a loop):
- WAV bit depth, sample rate, and resampling quality:
- Tail: leave remainder so reverb and delay finish, unless the brief wants a hard end
- Dither: only if this export lowers the bit depth

### Naming

To be filled in when the studio computer is set up.

- Project file name:
- Exported file names:
- Where the export is saved in the song folder:

## Future plan: a mobile DAW

The owner may get a mobile DAW later. No app is chosen yet. Leave this blank until one is.

- **App:** not chosen
- **What it is for:** to be filled in
- **How stems and bounces move between the phone and this workspace:** to be filled in

### Session organization conventions

To be filled in when a mobile DAW is chosen.

### Export / bounce settings

To be filled in when a mobile DAW is chosen.

- WAV for the master, MP3 for the preview, unless the app cannot write a WAV. If it cannot, say so in the notes and still keep a WAV made on the Linux computer.

### Naming

To be filled in when a mobile DAW is chosen.

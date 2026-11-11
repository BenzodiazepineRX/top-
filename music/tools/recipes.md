# Processing recipes

Tested ffmpeg settings and supporting notes. Every filter line below ran successfully on ffmpeg 6.1. Treat numbers as starting points: measure, render, compare, adjust.

Contents
1. Ground rules and syntax traps
2. Repairs and tone moves on a stereo file
3. Mono low end without `ms-bus`
4. Loudness targets
5. Two-pass loudnorm (simple normalization only)
6. Stems from a finished song: separation and the null test

---

## 1. Ground rules and syntax traps

Make working copies in 32-bit float at the delivery sample rate, so processing never clips internally:

```bash
ffmpeg -i "song.mp3" -map a:0 -af aresample=44100:resampler=soxr -c:a pcm_f32le 01_working.wav
```

(Drop `:resampler=soxr` if ffmpeg reports it unavailable.)

- **Small moves on a stereo mix.** One EQ band on a finished song touches every instrument in that range; 1–3 dB is usually plenty. Bigger moves are a sign the problem needs stems.
- **One change, then check.** Render, run `analyze_audio.py`, compare.
- **`acompressor threshold` and `alimiter limit` are linear (0–1) by default** but accept dB with a suffix: `threshold=-18dB`, `limit=-1dB`.
- **`alimiter` auto-levels by default** (`level=true`), renormalizing the output. Always set `level=disabled`; `render_master.py` does.
- **`alimiter` limits sample peaks, not true peaks.** Oversample around it and verify with `ebur128=peak=true`; `render_master.py` does both.
- **`loudnorm` outputs 192 kHz** whatever the input. Follow it with `aresample=<rate>`.
- **`equalizer` with `t=q:w=1.0`** sets width as Q: higher is narrower.
- **`adynamicequalizer` auto threshold** takes words: `auto=on`.
- **ffmpeg high-pass filters are 2-pole at most** (12 dB/oct). For 18 dB/oct use `dsp_tools.py hpf --order 3`, or chain `highpass=f=90:poles=1,highpass=f=90:poles=2:t=q:w=1.0` (a first-order plus a Q=1 second-order section is a 3rd-order Butterworth).
- Labeled filtergraphs (`asplit[a][b];...`) work inside `-af` and `render_master.py --chain` as long as the whole graph has one input and one output.

## 2. Repairs and tone moves on a stereo file

| What you hear or measure | Try first | Watch out for |
|---|---|---|
| Rumble, DC offset, wasted headroom | `highpass=f=25:poles=2` | Above ~35 Hz thins kicks and 808s |
| Muddy, boxy low-mids | `equalizer=f=250:t=q:w=1.0:g=-2` (try 200–400 Hz) | Too much cut sounds thin |
| Boomy bass | `lowshelf=f=100:g=-1.5`, or a bell cut at the boom | Kick loses weight |
| Thin, lacks warmth | `lowshelf=f=120:g=1.5` | Mud returns |
| Harsh only in loud parts (2–5 kHz) | `adynamicequalizer=dfrequency=3500:dqfactor=1.5:tfrequency=3500:tqfactor=1.5:threshold=0.05:ratio=2:range=6:mode=cut:attack=10:release=150`, or `dsp_tools.py dyneq` | A static cut also dulls presence |
| Sibilance in a full mix | `deesser=i=0.3:m=0.5:f=0.6`, or `dsp_tools.py deess` | Also softens cymbals |
| Dull, no air | `highshelf=f=10000:g=1.5` | On lossy/AI audio it lifts artifacts too |
| Vocal buried (stereo only) | `equalizer=f=2500:t=q:w=1.2:g=1.5`; `stereotools=mlev=1.06` (≈ +0.5 dB center) | Center boost lifts kick, bass and snare too; stems are the real fix |
| Too wide, weak in mono | `stereotools=slev=0.9`; `dsp_tools.py ms-bus` | Over-narrowing flattens the mix |
| Uneven, needs glue | `acompressor=threshold=-20dB:ratio=1.5:attack=30:release=200:knee=4` (1–2 dB reduction) | Fast attack dulls drum punch |
| Clicks and pops | `adeclick=w=55:o=75` | Can soften transients |
| Clipped source | `adeclip=w=55:o=75` | Modest improvement only |
| Steady hiss | `afftdn=nr=6:nf=-60:tn=1` | Beyond ~6–10 dB it sounds watery |
| Mains hum | `bandreject=f=60:w=4:t=h` (50 Hz in Europe; add 120/180 for harmonics) | Also notches bass notes at that pitch |
| Abrupt ending | `afade=t=out:st=<start s>:d=<length s>` | Don't fade a real tail |
| Long silence at start | `silenceremove=start_periods=1:start_threshold=-60dB,afade=t=in:d=0.01` | Keep intentional breaths |

Translation checks you can render (label them simulations when reporting): mono is `pan=mono|c0=0.5*c0+0.5*c1`; a rough phone speaker is `pan=mono|c0=0.5*c0+0.5*c1,highpass=f=250:poles=2,lowpass=f=9000`.

## 3. Mono low end without `ms-bus`

`dsp_tools.py ms-bus` is preferred. Inside an ffmpeg chain, this Linkwitz-Riley crossover does the same job and sums back flat (checked on pink noise, within 0.01 dB from 40 Hz to 1 kHz):

```
asplit[a][b];[a]lowpass=f=90,lowpass=f=90,pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1[lo];[b]highpass=f=90,highpass=f=90[hi];[lo][hi]amix=inputs=2:normalize=0
```

## 4. Loudness targets

The toolkit default is −10.5 LUFS integrated with a −0.5 dBTP true-peak ceiling, because the owner asked for it. The song brief's loudness target wins when it names one. Context for those conversations:

- Streaming services turn loud songs down to a playback reference (commonly cited: around −14 LUFS for Spotify and YouTube, around −16 LUFS for Apple Music; check current figures if it matters). A louder master doesn't play louder there; it plays with less punch for the same volume.
- −0.5 dBTP is tighter than the more common −1 dBTP recommendation. Lossy encoders overshoot peaks, so `export_master.py` checks the MP3 and turns down only that copy if needed.
- Broadcast uses its own specifications (for example EBU R128 at −23 LUFS, ATSC A/85 at −24 LKFS). Get the broadcaster's spec before claiming compliance.
- An already-loud source (peak-to-loudness ratio under ~8 dB) should not be pushed through another hard limiter; tell the user.
- `render_master.py` warns when the limiter removes more than ~4 LU; past that, drums flatten and pumping appears.

## 5. Two-pass loudnorm (simple normalization only)

For quick level matching, not mastering. Pass 1 measures:

```bash
ffmpeg -hide_banner -i in.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -
```

Pass 2 feeds the measured values back, asks for static gain, and resamples back:

```bash
ffmpeg -i in.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true:print_format=json,aresample=44100" -c:a pcm_f32le out.wav
```

If the pass 2 printout says `"normalization_type": "dynamic"`, the target wasn't reachable with static gain under the ceiling; use `render_master.py` instead.

## 6. Stems from a finished song: separation and the null test

**Separation.** Demucs is a widely used open-source separator (`pip install demucs`, then `demucs --two-stems=vocals song.wav` writes `vocals.wav` and `no_vocals.wav` under `separated/`). It needs PyTorch and downloads model weights on first run, so it may be unavailable when the workspace can't reach those servers; if installation or the download fails, tell the user plainly and ask for original stems rather than trying other routes. Web separation services are an option only with the user's agreement after checking cost and privacy; never pay or start a trial without explicit authorization.

Treat separated stems as estimates: check for vocal bleed, watery or metallic textures and smeared drum hits, and keep the stem route only if the result beats plain stereo processing at matched loudness.

**Null test: do the stems add back up to the song?**

```bash
ffmpeg -i vocals.wav -i no_vocals.wav -i original.wav -filter_complex \
 "[0][1]amix=inputs=2:normalize=0[sum];[2]volume=-1[inv];[sum][inv]amix=inputs=2:normalize=0,ebur128" -f null -
```

A residual 30+ LU below the song's loudness means the stems reconstruct it well. A large residual can also come from a timing offset or phase shift (any filtering applied to stems breaks the null), so check alignment before concluding the stems are incomplete.

Once stems exist, process them with the main workflow (`workflow.md` steps 2–6).

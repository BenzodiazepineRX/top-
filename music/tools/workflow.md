# Song Mix & Master: the processing toolkit

This page is the "hands" of the workspace. `agents/music_engineer.md` and the song's `brief.md` decide **what** a song needs; the tools here **do** it on the Linux machine with measurable DSP, and print what they measured and changed so every step can be logged in `mix-notes.md`.

The song brief always wins. Every number below (EQ frequencies, compression ratios, the −10.5 LUFS / −0.5 dBTP master target) is a starting point used only when the brief does not name its own. Delay times come from the brief's BPM table; `tempo_key.py` prints the same table so the two can be checked against each other.

A rigorous, DSP-driven audio engineering workflow: precise gain staging, mathematically tempo-synced delays, dynamic frequency management and clean commercial loudness, for vocal stems, full stem sets or finished tracks.

## Core principles

1. **No blind preset clicking.** Never rely on clicking plugins or default presets in external web DAWs. Without real-time listening there is no way to know what a preset did to the song, so every decision here is measured instead.
2. **Exact DSP in the workspace.** Process the source files in the sandbox with exact formulas and spectral measurement. Every tool below prints what it measured and what it changed, so each step can be checked and reported truthfully.
3. **Protect the artist.** Preserve vocal identity, pitch and lyric clarity. Remove muddy resonances, harsh sibilance and un-synced delay clutter; add nothing the song doesn't need.
4. **Measurements are not ears.** You cannot hear audio. Report what the numbers show, give the user a loudness-matched A/B to listen to, and never claim to have listened, auditioned or tested on headphones, speakers or a car.
5. **Private and free unless told otherwise.** Keep the music private; never publish or share it, and never start a paid service, trial or purchase without the user's explicit authorization.

## Tools

All scripts live in `music/tools/`, need ffmpeg/ffprobe plus numpy (and scipy for `tempo_key.py` and `dsp_tools.py`), and accept `-h`. Intermediate files are 32-bit float WAV, so nothing clips between steps.

| Tool | Use |
|---|---|
| `analyze_audio.py FILE [--reference REF]` | Format, integrated/short-term LUFS, true peak, RMS, clipping, stereo/mono, silence, bandwidth, spectral band shares; `--reference` prints the differences (use the original to verify a master) |
| `tempo_key.py FILE [--bpm N]` | BPM (with half/double alternatives), key and runner-up, tuning, and the full delay-time table |
| `dsp_tools.py gain-stage` | Set a stem's working level by gated RMS; report vocal vs. beat |
| `dsp_tools.py hpf` | Butterworth high-pass (`--order 3` = 18 dB/oct) |
| `dsp_tools.py resonances` | Peak candidates in the boxy (200–350 Hz) and harsh (2–5 kHz) zones, flagged when they are just harmonics of sung notes |
| `dsp_tools.py dyneq` / `deess` | Split-band dynamic cut: band-pass envelope detection, cuts only when the band flares |
| `dsp_tools.py comp2` | Two-stage serial compression: fast peak tamer, then a smooth slow-release leveler |
| `dsp_tools.py delay` | Tempo-synced ping-pong delay return, ducked by the lead vocal; optional throws on chosen time ranges |
| `dsp_tools.py reverb` | Plate or hall return with exact pre-delay and decay |
| `dsp_tools.py saturate` | Oversampled odd/even harmonic saturation |
| `dsp_tools.py mix` | Sum stems and effect returns with gains, sample-aligned |
| `dsp_tools.py ms-bus` | Mono sub-bass (side high-pass) and a mid-only high shelf |
| `render_master.py` | Oversampled lookahead limiter to an exact LUFS target and true-peak ceiling |
| `export_master.py` | 24-bit TPDF-dithered WAV + 320 kbps MP3, each reopened and verified |
| `ab_match.py` | Loudness-matched A/B clip for the user's ears |

`music/tools/recipes.md` has tested ffmpeg settings for repairs on stereo files (EQ, clicks, hum, noise), syntax traps, loudness-target notes and the stem-separation route. Read it when a problem isn't covered below.

## Workflow

### 1. Receive and measure the audio

Ask for 24-bit or 32-bit float WAV stems when possible: lead vocal, backing vocals or adlibs, and the instrumental, all exported from the same start point. MP3 or AAC works too, but say plainly that lossy files have already lost detail that no processing restores. Keep every upload untouched and work on copies.

Check that the stems share a sample rate and length (`ffprobe`), then measure:

```bash
python3 music/tools/analyze_audio.py instrumental.wav lead_vocal.wav adlibs.wav
python3 music/tools/tempo_key.py instrumental.wav          # or the full mix
```

Run tempo detection on the instrumental or full mix, never on a vocal stem alone: a vocal's phrasing misleads beat tracking (in testing, a vocal stem from a 92 BPM song read as 74 BPM with "high" confidence). If the user or their project states the BPM or key, that wins; if confidence is not high, or half/double time matters for the feel, confirm the BPM with the user before rendering any delay.

Delay times come from the BPM, never from guesswork:
- Quarter note (1/4) = 60,000 / BPM ms
- Dotted eighth (1/8d) = 45,000 / BPM ms
- Half note (1/2) = 120,000 / BPM ms

`tempo_key.py` prints these and the rest of the table (eighths, triplets, sixteenths, 1/64 for pre-delay). Example at 92 BPM: 1/4 = 652.17 ms, 1/8d = 489.13 ms, 1/2 = 1304.35 ms.

If only a finished stereo song exists, the vocal-specific steps need stems: try separation (recipes, section 6) or ask for stems; if neither works, do the bus mastering (step 5) only and say what that cannot fix.

### 2. Vocal stem processing and gain staging

Process the lead vocal in this order, checking each printout before moving on:

```bash
T="python3 music/tools/dsp_tools.py"
$T gain-stage lead_vocal.wav v1.wav --target-rms -18 --against instrumental.wav
$T hpf v1.wav v2.wav --freq 90 --order 3
$T resonances v2.wav
# optional static cut for a fixed ring: run ONE of these two lines so v3.wav always exists
ffmpeg -i v2.wav -af "equalizer=f=280:t=q:w=4:g=-3" -c:a pcm_f32le v3.wav   # cut
# cp v2.wav v3.wav                                                          # bypass (no fixed ring found)
$T dyneq v3.wav v4.wav --freq 3500 --q 2
# optional broad presence lift: run ONE of these two lines so v5.wav always exists
ffmpeg -i v4.wav -af "equalizer=f=3200:t=q:w=1.0:g=2" -c:a pcm_f32le v5.wav  # lift
# cp v4.wav v5.wav                                                          # bypass (presence already fine)
$T deess v5.wav v6.wav --low 5500 --high 8500
$T comp2 v6.wav v7.wav
```

- **Gain staging.** Bring the vocal's active (gated) RMS to the working level of −18 dBFS (−14 is the upper end of the range). The compressor thresholds below are calibrated to that level, and it leaves headroom. `--against` reports where the vocal sits relative to the beat; the audible balance, with the vocal sitting clearly above the instrumental, is set in the mix (step 5) and confirmed by the user's ears.
- **High-pass.** 85–100 Hz at 18 dB/oct (`--order 3`) removes rumble and plosive thumps. `resonances` lists the most-sung notes: keep the cutoff below the lowest sung note's fundamental (a deep male voice may need 75–80 Hz).
- **Resonances.** `resonances` finds narrow peaks and labels them by zone. A candidate flagged as a harmonic of a sung note may just be the melody; cut only peaks that stay fixed and ring. Use a static notch for a constant ring (Q 4–8, cut about half the measured excess) and `dyneq` for harshness that only flares on loud notes. Add presence afterwards as a broad lift (2.5–4.5 kHz, Q about 1, +1.5 to +3 dB): cutting the narrow harsh spot first and lifting broadly after is what lets both instructions coexist.
- **De-essing.** Band-pass envelope detection across 5.5–8.5 kHz with an automatic threshold. Read the printout: it should reduce only the S, T and CH moments (usually under ~20% of singing time, 3–8 dB on those). If it reduces far more often, raise `--auto-pct` or set `--threshold`; if sibilance survives, lower them.
- **Compression.** Stage 1 is a fast peak tamer (1 ms attack, 50 ms release, 5:1, peak detection); stage 2 is a smooth leveler (15 ms attack, 350 ms release, 2.5:1, RMS detection, soft knee). ffmpeg's compressor has a fixed release, so stage 2 approximates opto behavior rather than modeling an opto cell's program-dependent release; say so if the user asks for "opto". Aim for about 3–6 dB average reduction and a smaller loud-vs-quiet spread. Makeup gain restores the −18 dBFS working level automatically.

Backing vocals get the same treatment, usually with a higher high-pass (150–250 Hz) and more de-essing, so they sit behind the lead.

### 3. Tempo-synced delay and ducked echo throws

Delays go on backing vocals or adlibs, or on chosen lead words as throws:

```bash
$T delay adlibs_processed.wav adlib_delay.wav --bpm 92 --note 1/8d --feedback 0.4 --duck-by v7.wav --duck-depth 10
$T delay v7.wav lead_throws.wav --bpm 92 --note 1/4 --throws "31.2-32.0,58.5-59.1" --duck-by v7.wav
```

Ducking is mandatory: always pass `--duck-by` with the processed lead vocal. The tool ducks the delay return, which carries every repeat coming out of the feedback loop, so the echoes drop while the lead sings and swell back in the gaps. This keeps lyrics intelligible and is the standard way ducked delays work. In testing, a ducked return sat 7.9 dB lower during singing and unchanged in the gaps, with repeats exactly on the 1/8d grid. Check that the printout's "fully ducked" percentage roughly matches how much of the song the lead sings.

Defaults: ping-pong stereo, a 300–6000 Hz loop filter so each repeat sits darker and further back, feedback 0.3–0.45, return −8 dB. Output is the wet return only; it is blended in the mix.

### 4. Spatial reverb and saturation

```bash
$T saturate v7.wav v8.wav --drive 6 --even 0.15 --mix 0.3
# at 92 BPM: pre-delay 1/64 = 40.76 ms, decay 1/2 note = 1.30435 s (both printed by tempo_key.py)
$T reverb v8.wav vocal_verb.wav --type plate --decay 1.30435 --predelay 40.76 --duck-by v8.wav --duck-depth 4
```

- **Saturation** comes first, on the dry vocal, so the reverb receives the warmed signal. The asymmetric curve adds both even (2nd) and odd (3rd) harmonics, 4x oversampled to avoid aliasing. Tested on a sine at full mix, the 2nd and 3rd harmonics measured about 29 and 35 dB below the fundamental; the default 0.3 blend puts them roughly 10 dB lower still, which is subtle by design.
- **Reverb.** Both reverb times come from the song's BPM, never a fixed number. Pre-delay keeps the vocal's attack upfront before the tail blooms: use the note value `tempo_key.py` prints (1/64, 1/128 and so on), which is the one inside 25–40 ms or, when none lands there, the closest one. Decay is a note value too: `tempo_key.py` prints the 1/2-note, dotted-half and 1-bar times; pick the one in the plate range (about 1.2–2.0 s, bright and dense, suits most vocals) or hall range (about 1.8–2.8 s, darker, for slower, bigger songs). The reverb is generated from a noise-based impulse response with per-band decay (highs fade faster); in testing, pre-delay landed at exactly 32.0 ms for a 32 ms setting and the measured RT60 matched the setting. Light ducking (3–4 dB) keeps the tail out of the words. Return about −12 to −18 dB.

### 5. Mix and stereo bus mastering

Resample every file to 44.1 kHz first if it isn't already (`ffmpeg -i in.wav -af aresample=44100:resampler=soxr -c:a pcm_f32le out.wav`), so the limiter works at the delivery rate; resampling after limiting nudged true peak from −0.5 to −0.4 dBTP in testing.

```bash
$T mix mix_v1.wav --track instrumental.wav:0 --track v8.wav:1 --track adlibs_processed.wav:-3 \
   --track adlib_delay.wav:0 --track lead_throws.wav:0 --track vocal_verb.wav:0
# every wet return rendered in steps 3-4 goes into the mix; leave lead_throws.wav out only if step 3 skipped throws
$T ms-bus mix_v1.wav mix_v1_ms.wav --side-hp 90 --mid-shelf 9500:2.0
python3 music/tools/render_master.py mix_v1_ms.wav master_v1.wav --target-lufs -10.5 --ceiling -0.5
```

- **Balance.** Start from the gain-staging numbers, with the lead a dB or two above where it measured against the beat, then refine with the user: lyrics should stay clear at low playback volume without the vocal sounding pasted on top.
- **Mono sub-bass.** "Keep the sub-bass mono" is done by high-passing the side channel at 90 Hz (24 dB/oct, zero-phase), so everything below 90 Hz is centered. That is what a "side low cut" means; low-passing the side would do the opposite.
- **Mid sheen.** A high shelf of +1.5 to +2.5 dB above 9.5 kHz on the mid channel only (zero-phase). Stay near +1.5 dB on lossy or AI-generated sources, where the top end carries artifacts.
- **Limiting.** The default target is −10.5 LUFS integrated with true peak capped at −0.5 dBTP, using a 4x-oversampled lookahead limiter; if the song brief or the owner names another target, use theirs. If `render_master.py` warns of heavy limiting (more than about 4 LU), tell the user and fix dynamics earlier or lower the target instead of forcing the number.

### 6. Export and verification

```bash
python3 music/tools/export_master.py master_v1.wav --name SongName_master_v1 --rate 44100
python3 music/tools/analyze_audio.py SongName_master_v1_24bit.wav --reference original_mix.wav
python3 music/tools/ab_match.py original_mix.wav SongName_master_v1_24bit.wav --snippet <chorus start> 15
```

- The export writes a 24-bit 44.1 kHz WAV (TPDF dither) and a 320 kbps MP3, reopens both, and checks duration, sample rate, channels, decoding, LUFS and true peak. MP3 encoding overshoots peaks: at a −0.5 dBTP master, the MP3 tested at +0.3 dBTP, so the script turns down only the MP3 copy until it fits under −0.1 dBTP. Mention this when it happens; the WAV stays at the target.
- `analyze_audio.py --reference` verifies RMS, peak, LUFS, stereo correlation and spectral power distribution against the original. Expect the master to be louder with a similar tonal shape; explain any band that moved more than about 2 dB.
- Send the A/B clip so the user can judge at matched loudness, plus the delivery files.

### Reporting to the user

Keep it plain and short, with the numbers that matter:
- **Song facts:** BPM, key, and the delay times actually used
- **What changed:** two to four bullets, each with its reason
- **Before → after:** LUFS, true peak, RMS, and anything fixed
- **Listen for:** two or three timestamps, plus the A/B clip
- **Limits:** what the source prevents (lossy cutoff, vocal baked into a stereo mix, separation artifacts)
- **Files:** what each delivered file is for

Explain a term the first time in a few words (LUFS: a loudness measurement; true peak: the highest point the waveform reaches once played back). Keep each version and its `.settings.json`, iterate on specific issues, and stop when further processing offers no clear benefit.

## AI-generated songs

Songs from AI generators are often lossy, with a high-frequency cutoff (the analysis shows it), shimmery or metallic highs, smeared transients and sometimes a phasey stereo image, and they often arrive already loud. Prefer cuts to boosts, keep the mid shelf modest, check mono and correlation, check the peak-to-loudness ratio before limiting hard, and ask for the generator's WAV or stem downloads when it offers them.

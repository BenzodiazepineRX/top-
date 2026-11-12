# Review report: Willing To Show You — v2

Generated 2026-11-10 by `music/tools/song_report.py`.

**Verdict:** ❌ Not ready: 4 problem(s) to fix before the owner listens.

42 passed · 9 to check · 4 failed

The tools measure the audio; they do not listen. Every item here still needs the owner's ears.

## Files

- **WAV master:** `Willing_To_Show_You_Master_v2_24bit.wav`
- **MP3:** `Willing_To_Show_You_Master_v2.mp3`
- **Effects log:** `v2.json`
- **Compared with:** `Original_sum.wav`

## Master

| | Check | Result | To make it near-perfect |
| --- | --- | --- | --- |
| ✅ | Integrated loudness | -10.6 LUFS (target -10.5) | — |
| ✅ | True peak (WAV) | -1.5 dBTP (ceiling -1.3) | — |
| ✅ | True peak (MP3) | -1.2 dBTP | — |
| ✅ | Clipping | 0 samples above full scale, 0 clip runs | — |
| ✅ | Punch (peak-to-loudness) | 9.1 dB | — |
| ❌ | Contrast between sections (loudness range) | 2.9 LU | sections sound flat: back off compression or limiting |
| ✅ | Limiter workload | 1.1 LU taken off the peaks | — |
| ⚠️ | Volume dips from the limiter (pumping) | 1 s with dips over 4.5 dB, 44 s over 3 dB, worst -4.9 dB, typical worst -2.8 dB; worst moments 0:56, 1:18, 1:21, 1:28, 2:00 | find what triggers the dips at those times and control it before the limiter |
| ✅ | Stereo / phase | correlation 0.981, mono fold -0.0 dB | — |
| ✅ | Mono playback (phone speaker) | -0.0 dB when folded to mono | — |
| ✅ | Ending | ends smoothly: largest sudden drop 11 dB, 0.6 s fade/tail | — |
| ⚠️ | DC offset | 0.0022 | high-pass the mix at 5-10 Hz |

## Tone and width vs the original

| | Check | Result | To make it near-perfect |
| --- | --- | --- | --- |
| ✅ | sub | -1.3 dB | — |
| ✅ | bass | +0.2 dB | — |
| ⚠️ | low-mid | +3.3 dB | the low-mid band moved +3.3 dB: confirm by ear it was intended |
| ⚠️ | mid | +3.3 dB | the mid band moved +3.3 dB: confirm by ear it was intended |
| ⚠️ | upper-mid | +4.8 dB | the upper-mid band moved +4.8 dB: confirm by ear it was intended |
| ⚠️ | high | +7.3 dB | the high band moved +7.3 dB: confirm by ear it was intended |
| ⚠️ | air | +6.6 dB | the air band moved +6.6 dB: confirm by ear it was intended |
| ℹ️ | Stereo correlation | 0.985 → 0.981 | — |

## Effects and plugins

| | Check | Result | To make it near-perfect |
| --- | --- | --- | --- |
| ✅ | Lead 1 — Active-level gain staging | dsp_tools.py gain-stage: target gated RMS -18 dBFS | — |
| ⚠️ | Lead 1 — Rumble high-pass | dsp_tools.py hpf: 85 Hz, order 2 | Lowest vocal fundamental and subjective chest/body preservation remain unverified |
| ✅ | Lead 1 — Centered dry image | FFmpeg extrastereo: side multiplier 0.35, clipping disabled | — |
| ✅ | Lead 1 — Provisional tonal EQ | FFmpeg: equalizer=f=350:t=q:w=1:g=-2 | — |
| ✅ | Lead 1 — Provisional tonal EQ | FFmpeg: equalizer=f=2600:t=q:w=0.7:g=2.2 | — |
| ✅ | Lead 1 — Provisional tonal EQ | FFmpeg: treble=g=1:f=6500 | — |
| ❌ | Lead 1 — Limited split-band de-essing | dsp_tools.py deess: 5500–8500 Hz; auto percentile 90; ratio 3; max 3 dB → active 47.6% of singing, avg 1.8 dB | de-esser works too often and dulls the voice: raise its threshold |
| ✅ | Lead 1 — Serial peak and phrase control | dsp_tools.py comp2: peak -12 dB/5:1/2 ms/60 ms; smooth -22 dB/2.5:1/10 ms/200 ms; automatic makeup → avg 4.5 dB reduction | — |
| ✅ | Lead 1 — Residual peak catcher | FFmpeg alimiter: -9 dBFS; 2 ms attack; 60 ms release; auto-level off; latency compensated | — |
| ✅ | Lead 2 — Active-level gain staging | dsp_tools.py gain-stage: target gated RMS -18 dBFS | — |
| ⚠️ | Lead 2 — Rumble high-pass | dsp_tools.py hpf: 85 Hz, order 2 | Lowest vocal fundamental and subjective chest/body preservation remain unverified |
| ✅ | Lead 2 — Centered dry image | FFmpeg extrastereo: side multiplier 0.35, clipping disabled | — |
| ✅ | Lead 2 — Provisional tonal EQ | FFmpeg: equalizer=f=350:t=q:w=1:g=-2 | — |
| ✅ | Lead 2 — Provisional tonal EQ | FFmpeg: equalizer=f=2600:t=q:w=0.7:g=2.2 | — |
| ✅ | Lead 2 — Provisional tonal EQ | FFmpeg: treble=g=1:f=6500 | — |
| ❌ | Lead 2 — Limited split-band de-essing | dsp_tools.py deess: 5500–8500 Hz; auto percentile 90; ratio 3; max 3 dB → active 45.6% of singing, avg 1.7 dB | de-esser works too often and dulls the voice: raise its threshold |
| ✅ | Lead 2 — Serial peak and phrase control | dsp_tools.py comp2: peak -12 dB/5:1/2 ms/60 ms; smooth -22 dB/2.5:1/10 ms/200 ms; automatic makeup → avg 4.5 dB reduction | — |
| ✅ | Lead 2 — Residual peak catcher | FFmpeg alimiter: -9 dBFS; 2 ms attack; 60 ms release; auto-level off; latency compensated | — |
| ✅ | Adlibs — Active-level gain staging | dsp_tools.py gain-stage: target gated RMS -18 dBFS | — |
| ✅ | Adlibs — Rumble high-pass | dsp_tools.py hpf: 150 Hz, order 2 | — |
| ✅ | Adlibs — Provisional tonal EQ | FFmpeg: equalizer=f=350:t=q:w=1:g=-2.5 | — |
| ✅ | Adlibs — Provisional tonal EQ | FFmpeg: equalizer=f=2400:t=q:w=0.8:g=1.5 | — |
| ❌ | Adlibs — Limited split-band de-essing | dsp_tools.py deess: 5500–8500 Hz; auto percentile 90; ratio 3; max 3 dB → active 42.6% of singing, avg 1.9 dB | de-esser works too often and dulls the voice: raise its threshold |
| ✅ | Adlibs — Serial peak and phrase control | dsp_tools.py comp2: peak -12 dB/5:1/2 ms/60 ms; smooth -22 dB/2.5:1/10 ms/200 ms; automatic makeup → avg 3.3 dB reduction | — |
| ✅ | Adlibs — Residual peak catcher | FFmpeg alimiter: -9 dBFS; 2 ms attack; 60 ms release; auto-level off; latency compensated | — |
| ✅ | Beat — Gentle subsonic cut | FFmpeg highpass: 25 Hz, one pole | — |
| ✅ | Beat — Instrumental balance | FFmpeg volume: -4 dB | — |
| ✅ | Lead bus — Equal lead balance | dsp_tools.py mix: both leads -2 dB; both start at zero | — |
| ✅ | Adlibs — Supporting balance | dsp_tools.py mix: -8 dB after working-level processing | — |
| ✅ | Lead bus — Quiet timed density delay | dsp_tools.py delay: 1/16; feedback .25; 3 repeats; 300–4200 Hz; return -27 dB; 3 dB duck; attack 5 ms/release 1/16 → 1/16 at 135 BPM should be 111.11 ms, used 111.11 ms, ducked: yes | — |
| ✅ | Adlibs — Quiet timed density delay | dsp_tools.py delay: 1/16; feedback .25; 3 repeats; 300–4200 Hz; return -31 dB; 3 dB duck; attack 5 ms/release 1/16 → 1/16 at 135 BPM should be 111.11 ms, used 111.11 ms, ducked: yes | — |
| ✅ | Lead bus — Short ducked plate | dsp_tools.py reverb: plate; pre-delay 1/64; nominal decay 1/4; width .7; return -27 dB; duck 3 dB → pre-delay 27.77777777777778 ms (nearest note 1/64 = 27.78 ms), decay 0.4444444444444444 s (nearest note 1/4 = 0.444 s) | — |
| ✅ | Mix bus — Headroom and edge fades | FFmpeg: -4.709003 dB; 3 ms opening / .8 s ending edge fade; exactly 6256560 frames | — |
| ✅ | Mix bus — Sub-side cleanup | dsp_tools.py ms-bus: 90 Hz side high-pass, zero phase; mid shelf bypassed | — |
| ✅ | Master — Oversampled master limiting | render_master.py: 4x; 5 ms attack/100 ms release; -10.5 LUFS target; -1.3 dBTP ceiling | — |
| ✅ | Delivery — 24-bit dither and MP3 encoding | export_master.py: 44.1 kHz/24-bit TPDF WAV; 320 kbps MP3, decoded ceiling -1 dBTP | — |

## Creative effects requests (from the brief)

| | Check | Result | To make it near-perfect |
| --- | --- | --- | --- |
| ℹ️ | Requests | none in the brief yet | — |

## Missing facts in the brief

- Artist: unknown; confirm with Chex for release metadata. Chex is the workspace owner.
- Key: unknown; A minor is a low-confidence detector candidate, C minor runner-up. No pitch correction or retuning is applied.
- Release services: unknown; ask Chex before final distribution export. No broadcast target assumed.
- Needed by: unknown; no date supplied.

## What's needed before this song is near-perfect

- ❌ Contrast between sections (loudness range): sections sound flat: back off compression or limiting
- ❌ Lead 1 — Limited split-band de-essing: de-esser works too often and dulls the voice: raise its threshold
- ❌ Lead 2 — Limited split-band de-essing: de-esser works too often and dulls the voice: raise its threshold
- ❌ Adlibs — Limited split-band de-essing: de-esser works too often and dulls the voice: raise its threshold
- ⚠️ Volume dips from the limiter (pumping): find what triggers the dips at those times and control it before the limiter
- ⚠️ DC offset: high-pass the mix at 5-10 Hz
- ⚠️ low-mid: the low-mid band moved +3.3 dB: confirm by ear it was intended
- ⚠️ mid: the mid band moved +3.3 dB: confirm by ear it was intended
- ⚠️ upper-mid: the upper-mid band moved +4.8 dB: confirm by ear it was intended
- ⚠️ high: the high band moved +7.3 dB: confirm by ear it was intended
- ⚠️ air: the air band moved +6.6 dB: confirm by ear it was intended
- ⚠️ Lead 1 — Rumble high-pass: Lowest vocal fundamental and subjective chest/body preservation remain unverified
- ⚠️ Lead 2 — Rumble high-pass: Lowest vocal fundamental and subjective chest/body preservation remain unverified
- ⚠️ Fill in the 4 missing fact(s) in the brief: choices like loudness, tone and effects depend on them
- 👂 All creative effects from the brief are in place, on the right track or mix bus, in the right spot, and the right length
- 👂 Echo, delay, pre-delay, and decay times match this song's BPM, and the math was checked
- 👂 Earbuds check passed
- 👂 Phone speaker check passed
- 👂 Car check passed
- 👂 Studio monitors check passed
- 👂 Loudness and true peak meet this song's targets
- 👂 Compared against the reference tracks in the brief
- 👂 Owner sign-off on the final master

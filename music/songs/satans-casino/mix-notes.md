# Satan's Casino — v02 notes

This is a review candidate. Nothing here was judged by ear. Peaks, gaps, and grid positions are measurements.

## What was asked

Build-ups into the beat stops that are actually there. Reverse reverb. A clear telephone part, with its own reverb, made from this vocal because there is no second stem. Delay throws that repeat and fade in the gaps, on the musical grid, including dotted eighths. The lead stays intelligible and the ending is left intact. No one-click master.

## Tempo and the four suggested times

The drums lock to **135.00 BPM** from sample 0. A quarter is 444.44 ms (19600 samples). Half-tempo 67.5 and the chapter tag 110 do not fit. 129 was not used.

The suggested energy returns were checked. All four land on **beat 2** of a bar, inside a section where the vocal is still up:

| Suggested | Nearest grid | Vocal RMS in a 0.16 s window |
| --- | --- | --- |
| 30.6 s | beat 69 at 30.667 s | -28.2 dB |
| 59.1 s | beat 133 at 59.111 s | -18.5 dB |
| 87.5 s | beat 197 at 87.556 s | -18.4 dB |
| 158.6 s | beat 357 at 158.667 s | -19.6 dB |

Those are not stops. No envelope was written there.

The stops that were used are the two measured hat dropouts: bar 40 at 71.111 s (highs fall from about -43 dB to -74 dB, and the vocal is in a gap) and bar 80 at 142.222 s (same hat dropout, vocal still in, so the riser is quieter). One bar of reversed hats rises into each downbeat and yields over a 64th note. The beat level rides up 0.8 dB and 0.6 dB into those bars, then back.

The quiet vocal hole is measured from 154.561 s to the return at 156.438 s. That matches the suggested 154.8–156.4 s window. Two dotted-eighth throws sit in the first part of the hole (154.667 s and 155.000 s). The reverse swell occupies 155.538–156.438 s and ends on the return.

## Balance

Beat -8 dB, vocal -6 dB, no normalization, no vocal boost, no EQ, no compressor, no de-esser, no limiter. Baseline peak -1.550 dBFS, true peak -1.544 dBTP, -20.22 LUFS. Candidate peak -1.540 dBFS, true peak -1.534 dBTP, -20.24 LUFS. Same length as the beat, 216.172721 s. Dry vocal correlation at lag 0 is 1.0.

## Baked effects in the vocal

Measured, not heard. Side energy is 22.0 dB below the mid. Envelope autocorrelation is 0.03 at an eighth, -0.02 at a dotted eighth, 0.23 at a quarter. The quarter value follows the delivery, not a slap copy. In the quiet hole the vocal falls from about -40 dB to -64 dB over 0.8 s. No printed delay or long stereo reverb was found, so nothing was stripped and nothing was stacked on top of a printed echo.

## Layers

Each bus is the full beat length, starting at sample 0.

- `beat_dry` — beat at -8 dB. Peak -8.10 dBFS.
- `vocal_dry` — vocal at -6 dB, original start, silence after the stem ends. Peak -6.10 dBFS.
- `beat_stop` — the two rides and risers. Peak -15.99 dBFS.
- `reverse_swells` — two swells, peak held at -18.0 dBFS.
- `telephone_bgv` — opening phrase at 1.778–4.237 s, and the closing fragment at 190.222–191.822 s, band-limited 380–3400 Hz. Peak -20.62 dBFS. Silent through 13.4–15.9 s.
- `telephone_reverb` — half-note decay, 27.78 ms predelay, on the phone bus only. Peak -26.84 dBFS.
- `lead_reverb` — dotted-half decay (1.333 s), 27.78 ms predelay, ducked 5 dB while the lead is up. Peak -25.29 dBFS.
- `delay_throws` — 16 copies. Peak -15.66 dBFS.

Throws use a dotted eighth when the syllable is about 0.20–0.34 s, an eighth only if it is shorter, and a quarter when the ending is longer (the final line). Each repeat is 5 dB lower and lowpassed at 4.2 kHz. A repeat that would reach the next phrase was left out rather than cut. The final line gets four quarter-note repeats, fading to -26 dB, and they finish before the telephone answer.

## Files

Render again with:

```bash
python3 music/songs/satans-casino/tools/render_v02.py
```

The event list, with source samples, destinations, and gains, is `effects/v02-events.json`. The check list is `reports/v02.md`.

## Not done

No listening, no earbuds, no car, no phone speaker. No streaming loudness target. No claim that the vocal is intelligible. This pass is for an independent DAW and EQ listen.

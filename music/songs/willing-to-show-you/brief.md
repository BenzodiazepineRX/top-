# Song brief

## Song

- **Title:** Willing To Show You
- **Artist:** unknown; confirm with Chex for release metadata. Chex is the workspace owner.
- **Genre / subgenre:** trap / Memphis-influenced rap, engineer inference from beat filename and requested reference.
- **Mood / vibe:** proposed close, assertive vocal over a bass-heavy beat; owner requested professional mix/master, without additional mood instructions.
- **BPM:** 135 (instrumental detector: high confidence, exactly 135.00; 67.5 half-time gives the same grid). Not owner-supplied.
- **Key:** unknown; A minor is a low-confidence detector candidate, C minor runner-up. No pitch correction or retuning is applied.

## Reference tracks

1. **Pooh Shiesty — FDO**
   - Owner supplied https://youtu.be/MPuK06zUIhc?is=lJcJyEkWWLxW_arZ and confirmed artist/title.
   - Proposed borrowing: close forward vocal, restrained ambience, bass impact.
   - Leave alone: the arrangement and timing of this performance. No reference-match claim: reference audio could not be retrieved (403), and no auditory comparison has occurred.

## Session

Four stereo 44.1 kHz / 16-bit WAV sources from the Dropbox folder “Willing To Show You.” The owner confirmed the folder/song and common timeline start, despite differing lengths. Keep start offsets at zero, pad the shorter stems without moving phrases.

- `source/LEAD 1.wav`: 130.704558 s, alternating primary lead.
- `source/LEAD 2.wav`: 127.135465 s, alternating primary lead; not a backing double.
- `source/BACKGROUNDADLIBS.wav`: 78.225329 s, support.
- `source/Y2Mateis__FREE_Big_Scarr_x_Pooh_Shiesty_Type_Beat__Catch_A_OppPjA305Y70LA160k1659790065786.wav`: 141.872109 s stereo beat. Individual kick/808/instrument stems are unavailable.
- Source hashes: `provenance/sources.json`; originals stay unchanged and audio remains ignored by Git.
- Original shared source: the owner's Dropbox folder in the conversation. The private download capability is not copied into Git.

## What's working

- Preserve all takes, syllable placement and alternating-lead arrangement; both leads already have closely matched active RMS (about -22.3 dBFS).
- Preserve the beat's bass-led character; original LRA about 2 LU by the workspace EBU R128 measurement and low-frequency correlation is high.
- These are measured/proposed preservation choices, not listening judgments.

## Problem areas

- Source vocal active RMS is about 8 dB below the beat's overall RMS; improve relative vocal level and control isolated transients without peak-normalizing the alternating leads differently.
- Lead 2 reaches full scale briefly near 44.1643 and 58.2343 s; adlibs near 60.0039 s. Full-scale samples are measured; audible damage is unverified.
- The earlier local v1 used free-time slap/early-reflection settings before repository access. Replace that wet path in v2 with calculated, ducked timing. Retain the mild tonal proposal and equal priority of the two leads; rebuild dynamics with the toolkit and use a slightly more beat-forward provisional balance for owner comparison.
- Vocal fundamentals and exact vocal tonal problems remain unverified without listening; the inherited mild EQ is a first-pass choice, not a proven resonance repair.

## Creative effects requests

None specified by the owner in this conversation. No requested plugin, structural sweep, tape stop, beat switch, tuning or word throw is invented.

| Effect | Scope (one track or whole mix) | Where it happens | How long (bars) | Plugin, if one is required | Notes |
| --- | --- | --- | --- | --- | --- |
| None specified | — | — | — | — | Quiet ambience below is the engineer's proposal, not an artist request. |

Engineer-proposed v2 ambience: 1/16-note quiet lead/adlib density delays, ducked under the combined lead; short plate with 1/64-note pre-delay and 1/4-note nominal decay. No prominent line-end throw is introduced. The source-relative voice timing is retained rather than quantized.

## Delay timing for this song

- **BPM used:** 135
- **Time signature:** 4/4 working assumption for timing, not owner-confirmed.
- Formula: quarter = 60000 / 135; dotted = ×1.5; triplet = ×2/3.

| Note | Straight (ms) | Dotted (ms) | Triplet (ms) |
| --- | --- | --- | --- |
| 1 bar | 1777.78 | 2666.67 | 1185.19 |
| 1/2 | 888.89 | 1333.33 | 592.59 |
| 1/4 | 444.44 | 666.67 | 296.30 |
| 1/8 | 222.22 | 333.33 | 148.15 |
| 1/16 | 111.11 | 166.67 | 74.07 |
| 1/32 | 55.56 | 83.33 | 37.04 |
| 1/64 | 27.78 | 41.67 | 18.52 |

Used: slap 1/16 = 111.111111 ms (nearest sample); plate pre-delay 1/64 = 27.777778 ms, nominal RT60 1/4 = 0.444444 s. Detector results are in `measurements/tempo-key.json`. High-frequency reverb bands decay faster by design; the nominal setting is tempo-derived.

## Where it will be heard

- **Release services:** unknown; ask Chex before final distribution export. No broadcast target assumed.
- Working delivery: 44.1 kHz / 24-bit stereo WAV plus 320 kbps MP3.
- Provisional target: -11.5 LUFS integrated, WAV/decoded MP3 no higher than -1.0 dBTP; master limiter ceiling set -1.3 dBTP for extra encoding margin. This is the engineer's starting choice, not a measured FDO match or platform mandate.
- Earbuds, phone, car and studio-monitor checks remain pending with the owner; numerical mono checks are not listening tests.

## Deadline

- **Needed by:** unknown; no date supplied.
- **What this pass should deliver:** reviewed work-in-progress v2, private local WAV/MP3, matched A/B, reproducible settings, effects log and report in the workspace. No final sign-off is implied.

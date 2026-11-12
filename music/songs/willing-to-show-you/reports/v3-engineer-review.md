# Engineering review — v3

**Decision:** ready for the owner's revised listening review, with one explicitly accepted song-specific range exception and two inherited vocal-body warnings. No final approval or auditory reference comparison is claimed.

The owner rejected v2 because its main vocals were entirely too loud. V3 uses the exact same processed takes and corrects dry lead level and lead-only wet returns by -4 dB. Both alternating primary takes receive the same adjustment. Their measured active levels already differ by only 0.07 dB; separate phrase gain changes or extra compression were not justified. Beat and adlib routing is retained. The waveform, duration, phrase placements, de-essing and tonal processing are unchanged upstream of the new blend and master.

## Generic report exception

`v3.md` is the unchanged output of the shared automatic report: 53 passes, 2 checks and 1 failed generic range rule. That red row requires LRA >= 3 LU for every song. This song's source stereo beat measures 2.0 LU under the same EBU R128 method. After reducing the dominant lead as the owner explicitly requested, premaster LRA is 2.8 LU and master LRA 2.1 LU. The limiter removes about 0.8 LU, with no second over 4.5 dB of attenuation. Changing the arrangement or restoring the rejected loud lead merely to increase the automatic range number would work against this revision's brief. The playbook directs that the song and its brief take precedence over generic targets. The engineer therefore accepts the range exception for this review render and preserves the raw failed row for transparency. No global checker threshold has been changed or hidden.

## Remaining checks

The two high-pass/body warnings stay open: lowest vocal fundamentals and subjective body preservation remain unverified. Their settings are inherited unchanged; no new body-removing EQ was introduced in response to a level complaint. Actual listening on the owner's systems, the FDO comparison, release details and final sign-off remain pending.

## Delivery

- `exports/Willing_To_Show_You_Master_v3_24bit.wav`: 44.1 kHz stereo / 24-bit; about -11.6 LUFS, -1.5 dBTP.
- `exports/Willing_To_Show_You_Master_v3.mp3`: 320 kbps, about -11.6 LUFS, -1.4 dBTP.
- `exports/Willing_To_Show_You_v2_then_v3_AB.mp3`: v2 passage 0:42–0:57, 0.8 s pause, then the same passage in v3, loudness matched. A uniform -1.5 dB preview encoding gain preserves relative matching.
- `measurements/v3-delivery-verification.json`: actual output hashes, frame counts and mix reconstruction check. Original source and cached processing hashes are unchanged.

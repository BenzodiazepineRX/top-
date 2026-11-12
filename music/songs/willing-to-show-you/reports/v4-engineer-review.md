# Engineering review — v4 quieter, softer vocals

**Status:** owner listening review, with the existing source-range exception explicitly accepted. V3 was rejected for voice level and tone; this version makes both changes. Subjective removal of boxiness and final balance are not inferred from measurements.

## Owner feedback and response

“It’s still loud and sounds kinda ‘boxy’ like treble turned up alot or something.”

The earlier lead chain contained a broad +2.2 dB presence lift at 2.6 kHz and a +1 dB treble shelf at 6.5 kHz. V4 rebuilds the leads from the validated pre-EQ working-level caches, so these boosts are removed before dynamics, rather than being EQ'd on top of the already processed v3. New tone: 75 Hz order2 high-pass; 350 Hz Q1/-3 dB broad adjustment; -1 dB shelf at5.5 kHz; no positive EQ boosts. The source's low-mid peaks are harmonic-spaced near366/485/614/732/851 Hz. They support a broad tonal proposal, not a diagnosis of room ringing or a verified fundamental; no deep surgical notch is applied.

Both leads are another3.5 dB below v3 on the SAME frozen active50ms windows, with that correction applied AFTER automatic makeup and peak control. This prevents normalization from undoing the requested quieter level. Their difference remains about0.075 dB. Adlibs and their return are lowered2.5 dB to remain support after the main reduction. Main delay/plate are rebuilt from the new tone, with -30 dB returns and400 Hz wet high-pass, preserving135 BPM note timings. Overall master target is also1 dB lower at -12.5 LUFS. No phrase or source start is moved.

## Measured result and limits

Independent same-window normalized dry-lead measurements, beyond the common3.5 dB level reduction:

- Lead1:2–4.5 kHz -1.407 dB;5.5–10 kHz -1.813 dB.
- Lead2:2–4.5 kHz -1.464 dB;5.5–10 kHz -1.635 dB.
- Normalized300–650 Hz broad-band shares move only-0.088/-0.012 dB. Do not describe this as proof that all boxiness is removed. The absolute low-mid vocal level is lower, the350 Hz curve is gentler in level, and the upper tone is softer; the owner judges the remaining recorded character.

Full-mix normalized band shares versus v3: low-mid about-2.1 dB, mid-2.2, upper-mid-2.1, high-3.3, air-2.6 dB. The beat retains its original processing/routing. Common master level has changed, so absolute waveform comparisons must be loudness-matched.

Both delivered files independently decode to6,256,560 frames at44.1 kHz stereo, without decoder errors/full-scale samples: WAV24-bit and320 kbpsMP3 each measure-12.5 LUFS/-1.5 dBTP. Exact output hashes and a separate tone/level review are in measurements/.

## Report exception

The unmodified `v4.md` automatic report flags its generic minimum3 LU section-contrast rule. The source beat measures2.0 LU, v4 premaster2.2 LU and master2.0 LU; master limiting costs only0.2 LU. The playbook's brief-first rule and the owner's repeated request for quieter, more even vocals take precedence over inventing arrangement dynamics or raising the rejected vocal to satisfy a generic meter threshold. This is an explicit source/style exception, retained visibly in the raw report. No clipping, timing or peak failure is waived. Review counts and raw failed rows are not represented as all-passing.

Reference audition, real playback-system checks and owner sign-off remain pending. Older versions are preserved. The matched comparison contains v3 at0:42–0:57 first,0.8-second gap, then v4 over the same passage; a common preview attenuation preserves the match.

# Baccdoor build scripts

Run from a work folder that holds the stems as 01_Beat.wav, 02_Main1.wav, 03_Main2.wav, 04_BG.wav, 05_BGBG1.wav
(set `BACC_WORK` to it, or run inside it):

1. `map.py` - tempo, grid, the beat bar by bar, the vocal lines (writes map.json)
2. `pitch_layers.py` - how in tune each vocal is against the key, and how the layers relate
3. `prep_vocals.py` - retune each stem to the beat's tuning (re-aligned to the sample), gain stage, high-pass
4. `check_retune.py` - the pitch moved by the planned cents and the timing did not move
5. `build_bacc.py v4` (or v1-v3) - chains, layer order, echo throws, reverbs, progression, mix bus, master, export.
   v3 also: mono leads, tone match, the telephone background vocals at the first lead lines, and the fade-out
6. `verify_bacc.py v4` - echo timing, layer order (and the telephone background), gaps, mono (exits 1 on a failure)
7. `harsh.py` - harshness (2-5 kHz), fizz (5-12 kHz) and grit at every step of the lead chain, against Driftin' Away
8. `hnr.py` - harmonics-to-noise ratio (how clean the voice is) at each step of the lead chain

`match_eq.py` is the v3 tone match: it measures a vocal's long-term tone against a reference (the owner's Driftin'
Away lead) and applies part of the difference as a linear-phase EQ. The curves v3 used are saved here
(`match_m1.json`, `match_m2.json`, `match_bg.json`, `match_bb.json`), and `build_bacc.py` re-applies them, so a
rebuild does not need the Driftin' Away files.

`low_ctl.py` and `beat_peaks.py` are the two beat-peak experiments tried for v1 and not used (see mix-notes.md).
`degrain.py` (lowering the noise between the harmonics) was tried for v3 and not used: it raised the voice's
harmonics-to-noise ratio by only 0.3-0.4 dB, because at this low a voice (A2, 110 Hz) the harmonics sit too close
together to separate from the grain cleanly.

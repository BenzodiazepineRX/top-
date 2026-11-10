# Baccdoor build scripts

Run from a work folder that holds the stems as 01_Beat.wav, 02_Main1.wav, 03_Main2.wav, 04_BG.wav, 05_BGBG1.wav
(set `BACC_WORK` to it, or run inside it):

1. `map.py` - tempo, grid, the beat bar by bar, the vocal lines (writes map.json)
2. `pitch_layers.py` - how in tune each vocal is against the key, and how the layers relate
3. `prep_vocals.py` - retune each stem to the beat's tuning (re-aligned to the sample), gain stage, high-pass
4. `check_retune.py` - the pitch moved by the planned cents and the timing did not move
5. `build_bacc.py v1` - chains, layer order, echo throws, reverbs, progression, mix bus, master, export
6. `verify_bacc.py v1` - echo timing, layer order, gaps, mono (exits 1 on a failure)

`low_ctl.py` and `beat_peaks.py` are the two beat-peak experiments tried for v1 and not used (see mix-notes.md).

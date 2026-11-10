# Don't Need Closure: song tools

Scripts that built and checked this song's mixes. They read the stems from a work folder (`CLOSURE_WORK`, default the
current folder) with these names: `01_Beat.wav`, `02_Lead1.wav`, `03_Lead2.wav`, `04_Adlib1.wav`, `05_Adlib2.wav`.
The shared toolkit is `music/tools`.

Order:

1. `map.py` - tempo (126.000 BPM), the drum grid, the downbeat, sections, every vocal phrase -> `map.json`
2. `pitch_layers.py` - how in tune the vocals are and how the layers relate (this song is mostly rapped: not retuned)
3. gain staging and high-pass by hand (see `effects/v1.json`): `dsp_tools.py gain-stage` then `hpf` -> `l1_2.wav`,
   `l2_2.wav`, `a1_2.wav`, `a2_2.wav`
4. `build_closure.py v2` (or v1) - chains, phrase rider, adlib rides, echo throws, reverse-reverb swells and risers,
   reverbs, the beat carve, mix bus, master, export
5. `verify_closure.py v2` - echo timing, swell and riser timing, lead level per phrase, adlibs against the leads,
   adlib reverb tails, gaps, mono (exits 1 on a failure)
6. `tone_check.py v2` - how the leads and adlibs sit over the beat, band by band

Helpers: `closure_lib.py` (grid, echoes, loudness, rides, peak catcher, `tails_down`), `match_eq.py` (tone match in
octave-wide bands; the curves v1 used are saved here as `match_l1.json`, `match_l2.json`, `match_a1.json`,
`match_a2.json`, and the build re-applies them, so a rebuild does not need the Baccdoor files), `dereverb.py` (v2: less
of the reverb baked into the adlib tracks), `tail_check.py` (reverb tail level at clean word endings).

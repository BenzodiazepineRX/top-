#!/bin/sh
# Driftin' Away v1 vocal chains. Run in the work folder that holds 01_Beat.wav, 02_Lead.wav, 03_Background.wav, 04_Adlibs.wav.
set -e
T="python3 -I $(dirname "$0")/../../../tools/dsp_tools.py"
FF="ffmpeg -nostdin -v error -y"
# lead: 90 Hz high-pass (lowest sung note Bb2 117 Hz), no static notches (the peaks are harmonics of the tuned Eb3)
$T gain-stage 02_Lead.wav l_1.wav --target-rms -18 --against 01_Beat.wav
$T hpf l_1.wav l_2.wav --freq 90 --order 3
$T dyneq l_2.wav l_4.wav --freq 2500 --q 2 --auto-pct 97
$FF -i l_4.wav -af "equalizer=f=3500:t=q:w=1.0:g=1.5" -c:a pcm_f32le l_5.wav
$T deess l_5.wav l_6.wav --low 5500 --high 8500 --auto-pct 97
$T comp2 l_6.wav l_7.wav
$T saturate l_7.wav l_8.wav --drive 6 --even 0.15 --mix 0.3
# background vocal: behind the beat (thinner, softer top)
$T gain-stage 03_Background.wav b_1.wav --target-rms -18 --against 01_Beat.wav
$T hpf b_1.wav b_2.wav --freq 130 --order 3
$T dyneq b_2.wav b_4.wav --freq 2490 --q 2 --auto-pct 97
$FF -i b_4.wav -af "equalizer=f=3000:t=q:w=1.0:g=-1.5,highshelf=f=7000:g=-2" -c:a pcm_f32le b_5.wav
$T deess b_5.wav b_6.wav --low 5000 --high 8000 --auto-pct 97
$T comp2 b_6.wav b_7.wav
# adlibs
$T gain-stage 04_Adlibs.wav a_1.wav --target-rms -18 --against 01_Beat.wav
$T hpf a_1.wav a_2.wav --freq 150 --order 3
$T dyneq a_2.wav a_4.wav --freq 3000 --q 2 --auto-pct 97
$T deess a_4.wav a_6.wav --low 5500 --high 8500 --auto-pct 97
$T comp2 a_6.wav a_7.wav
# v2: the adlib responses levelled to one another (writes a_8.wav), then
#   ADLIB_SRC=a_8.wav python3 build_fx.py && python3 build_mix.py v2
python3 -I "$(dirname "$0")/level_adlibs.py"
# v3: FX_VERSION=v3 ADLIB_SRC=a_8.wav python3 build_fx.py && python3 build_mix.py v3
# v4: python3 build_mix.py v4 && python3 check_repeats.py   (every repeat must measure 0.0 dB or less vs its main line)
# v5: python3 build_mix.py v5 && python3 check_repeats.py   (every repeat 4 dB under the background vocal line it repeats)
# v6: python3 level_adlibs.py && FX_VERSION=v6 ADLIB_SRC=a_8.wav python3 build_fx.py && python3 build_mix.py v6 && python3 check_repeats.py v6 && python3 verify_v1.py v6

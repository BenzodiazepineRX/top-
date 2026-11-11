# Satans Casino v6: FX cue sheet

**Grid as used in v6, and wrong by 95 ms:** 135 BPM, 4/4, bar 1 beat 1 = 0.118 s. The real bar line in these files is at 0.0205 s (see ../README.md). Bar and beat labels below are therefore about 0.2 beat late; the times in seconds are what was rendered. Bar = 1.777778 s. bar.beat is 1-based.

| # | FX | Source | bar.beat | Start s | End s | Target / window | Settings | Note |
|---|---|---|---|---|---|---|---|---|
| 1 | filter sweep (COMPOSITE: beat + main vocal) | track 1 | 8.1.00 -> 10.1.00 | 12.562 | 16.118 | lands at T=16.118 | lowpass 1000->18000 Hz log, 2nd-order Butterworth (12 dB/oct, Q 0.707), 50% gain comp (max +4 dB), 10 ms crossfades in and at T | A: low-pass opens 1000 -> 18000 Hz over 2 bars |
| 2 | reverse reverb swell (half bar 888.889 ms) | first word of upcoming adlib phrase (reversed, 100% wet hall 2.4 s, 200-6000 Hz) | 10.4.67 -> 11.2.67 | 17.751 | 18.64 | lands at T=18.640 | fade-in 150 ms, fade-out 20 ms ending at T, peak -12 dB vs word peak | first adlib entrance (pickup into bar 11, after beat drop bar 10); rendered loudest point 18.614s |
| 3 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 11.3.48-11.4.27 | 19.0 | 19.35 | send 19.000-19.350 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 11 |
| 4 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 13.3.49-13.4.35 | 22.56 | 22.94 | send 22.560-22.940 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 13 |
| 5 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 15.3.48-15.4.13 | 26.11 | 26.4 | send 26.110-26.400 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 15 |
| 6 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 18.3.50-18.3.74 | 31.45 | 31.56 | send 31.450-31.560 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 18 |
| 7 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 19.3.48-19.3.88 | 33.22 | 33.4 | send 33.220-33.400 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 19 |
| 8 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 20.4.25-21.1.26 | 35.34 | 35.79 | send 35.340-35.790 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 20 |
| 9 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 23.3.50-23.3.97 | 40.34 | 40.55 | send 40.340-40.550 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 23 |
| 10 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 29.3.48-29.3.66 | 51.0 | 51.08 | send 51.000-51.080 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 29 |
| 11 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 34.4.25-35.1.26 | 60.23 | 60.68 | send 60.230-60.680 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 34 |
| 12 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 36.4.24-37.1.25 | 63.78 | 64.23 | send 63.780-64.230 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 36 |
| 13 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 37.4.24-38.1.26 | 65.56 | 66.01 | send 65.560-66.010 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 37 |
| 14 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 38.4.25-39.1.26 | 67.34 | 67.79 | send 67.340-67.790 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 38 |
| 15 | echo throw 1/2 (888.889 ms) | adlib (track 2) | 40.4.24-41.1.25 | 70.89 | 71.34 | send 70.890-71.340 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last bar 40 before breakdown/outro |
| 16 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 42.4.25-43.1.26 | 74.45 | 74.9 | send 74.450-74.900 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 42 |
| 17 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 44.4.26-45.1.27 | 78.01 | 78.46 | send 78.010-78.460 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 44 |
| 18 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 45.4.24-46.1.25 | 79.78 | 80.23 | send 79.780-80.230 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 45 |
| 19 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 46.4.24-47.1.26 | 81.56 | 82.01 | send 81.560-82.010 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 46 |
| 20 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 48.4.25-49.1.27 | 85.12 | 85.57 | send 85.120-85.570 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 48 |
| 21 | filter sweep (COMPOSITE: beat + main vocal) | track 1 | 49.1.00 -> 50.1.00 | 85.451 | 87.229 | lands at T=87.229 | highpass 30->400 Hz log, 2nd-order Butterworth (12 dB/oct, Q 0.707), 50% gain comp (max +4 dB), 10 ms crossfades in and at T | B: high-pass rises 30 -> 400 Hz over 1 bar, lows restored at T |
| 22 | reverse reverb swell (one bar 1777.778 ms) | first word of upcoming adlib phrase (reversed, 100% wet hall 2.4 s, 200-6000 Hz) | 49.1.54 -> 50.1.54 | 85.692 | 87.47 | lands at T=87.470 | fade-in 150 ms, fade-out 20 ms ending at T, peak -12 dB vs word peak | adlib entrance after breakdown, beat return bar 50; rendered loudest point 87.442s |
| 23 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 50.3.57-50.4.58 | 88.37 | 88.82 | send 88.370-88.820 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 50 |
| 24 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 52.3.82-52.4.84 | 92.04 | 92.49 | send 92.040-92.490 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 52 |
| 25 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 54.3.52-54.4.53 | 95.46 | 95.91 | send 95.460-95.910 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 54 |
| 26 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 56.3.96-56.4.97 | 99.21 | 99.66 | send 99.210-99.660 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 56 |
| 27 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 58.3.88-58.4.89 | 102.73 | 103.18 | send 102.730-103.180 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 58 |
| 28 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 60.3.48-60.4.47 | 106.11 | 106.55 | send 106.110-106.550 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 60 |
| 29 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 62.3.49-62.4.01 | 109.67 | 109.9 | send 109.670-109.900 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 62 |
| 30 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 65.3.48-65.3.75 | 115.0 | 115.12 | send 115.000-115.120 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 65 |
| 31 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 66.4.10-67.1.11 | 117.05 | 117.5 | send 117.050-117.500 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 66 |
| 32 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 67.3.49-67.3.76 | 118.56 | 118.68 | send 118.560-118.680 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 67 |
| 33 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 68.3.50-68.3.95 | 120.34 | 120.54 | send 120.340-120.540 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 68 |
| 34 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 70.3.49-70.4.27 | 123.89 | 124.24 | send 123.890-124.240 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 70 |
| 35 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 76.3.49-76.3.67 | 134.56 | 134.64 | send 134.560-134.640 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 76 |
| 36 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 78.3.48-78.4.40 | 138.11 | 138.52 | send 138.110-138.520 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 78 |
| 37 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 79.4.25-80.1.26 | 140.23 | 140.68 | send 140.230-140.680 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 79 |
| 38 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 81.4.24-82.1.25 | 143.78 | 144.23 | send 143.780-144.230 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 81 |
| 39 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 83.4.25-84.1.26 | 147.34 | 147.79 | send 147.340-147.790 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 83 |
| 40 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 84.4.25-85.1.27 | 149.12 | 149.57 | send 149.120-149.570 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 84 |
| 41 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 85.4.24-86.1.25 | 150.89 | 151.34 | send 150.890-151.340 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 85 |
| 42 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 87.4.25-88.1.26 | 154.45 | 154.9 | send 154.450-154.900 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 87 |
| 43 | filter sweep (COMPOSITE: beat + main vocal) | track 1 | 88.1.00 -> 90.1.00 | 154.785 | 158.34 | lands at T=158.340 | lowpass 800->18000 Hz log, 2nd-order Butterworth (12 dB/oct, Q 0.707), 50% gain comp (max +4 dB), 10 ms crossfades in and at T | C: low-pass opens 800 -> 18000 Hz over 2 bars |
| 44 | reverse reverb swell (one bar 1777.778 ms) | first word of upcoming adlib phrase (reversed, 100% wet hall 2.4 s, 200-6000 Hz) | 89.2.78 -> 90.2.78 | 157.352 | 159.13 | lands at T=159.130 | fade-in 150 ms, fade-out 20 ms ending at T, peak -12 dB vs word peak | adlib entrance after breakdown, beat return bar 90; rendered loudest point 159.092s |
| 45 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 90.3.50-90.3.72 | 159.45 | 159.55 | send 159.450-159.550 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 90 |
| 46 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 92.3.55-92.4.56 | 163.03 | 163.48 | send 163.030-163.480 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 92 |
| 47 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 94.3.49-94.4.46 | 166.56 | 166.99 | send 166.560-166.990 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 94 |
| 48 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 96.3.84-96.4.85 | 170.27 | 170.72 | send 170.270-170.720 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 96 |
| 49 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 98.3.56-98.4.57 | 173.7 | 174.15 | send 173.700-174.150 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 98 |
| 50 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 100.3.57-100.4.58 | 177.26 | 177.71 | send 177.260-177.710 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 100 |
| 51 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 101.3.57-101.4.59 | 179.04 | 179.49 | send 179.040-179.490 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 101 |
| 52 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 103.3.54-103.4.55 | 182.58 | 183.03 | send 182.580-183.030 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 103 |
| 53 | reverse reverb swell (half bar 888.889 ms) | first word of upcoming adlib phrase (reversed, 100% wet hall 2.4 s, 200-6000 Hz) | 105.1.73 -> 105.3.73 | 185.331 | 186.22 | lands at T=186.220 | fade-in 150 ms, fade-out 20 ms ending at T, peak -12 dB vs word peak | adlib re-entry after longest other silence (3.19 s); rendered loudest point 186.167s |
| 54 | echo throw 1/4 (444.444 ms) | adlib (track 2) | 105.4.25-106.1.26 | 186.45 | 186.9 | send 186.450-186.900 | fb 0.30, 200-5000 Hz loop, duck 6 dB, return -6 dB | last word(s) of bar 105 |

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
beat = os.path.join(HERE, "sources", "Satans casino beat.wav")
vocal = os.path.join(HERE, "sources", "Satans casino lead vocals.wav")
out_dir = os.path.join(HERE, "v01")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "Satans_Casino_v01_balance.wav")
subprocess.run(
    [
        "ffmpeg", "-v", "error", "-y",
        "-i", beat,
        "-i", vocal,
        "-filter_complex",
        "[0:a]volume=-8dB[b];[1:a]volume=-6dB[v];[b][v]amix=inputs=2:duration=longest:normalize=0:dropout_transition=0[m]",
        "-map", "[m]",
        "-c:a", "pcm_s24le",
        out,
    ],
    check=True,
)

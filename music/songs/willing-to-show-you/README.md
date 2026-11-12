# Willing To Show You

Work-in-progress song session based on the owner's four original stems and FDO by Pooh Shiesty as stylistic direction. Read `brief.md` first, then `mix-notes.md`.

- `render_v2.py`: reproducible song-specific driver using the shared music toolkit; run from repository root after placing the original four WAVs under `source/`.
- `provenance/sources.json`: required original source SHA256 hashes. Originals are private and ignored by Git; obtain them from the owner, not from a public mirror.
- `effects/v2.json`: every effect and processing stage.
- `reports/v2.md`: current automated review, with all warnings explained in the notes.
- `measurements/`: source/tempo/final analyses, command transcript and exact master settings.
- `exports/`: local ignored WAV/MP3 and loudness-matched A/B. In the shared execution session these are under `/workspace/top-music/music/songs/willing-to-show-you/exports/` and delivered as chat file links. Audio is not uploaded into the repository.

The driver verifies source hashes, keeps common timeline starts, pads/sums in float, uses calculated ducked effects, renders the premaster separately, masters at 4x oversampling, exports 24-bit/MP3, creates a passage-specific matched A/B and requires a review with zero failed checks. It uses cached source/tempo measurements only after verifying the unchanged source hashes. Intermediate audio is float; integer dither occurs on final master export.

The repository dependency is the music-workflow branch from PR #1. This song's review PR targets that branch; it does not merge or modify the workspace setup PR. No real-system listening or reference matching is claimed. The owner must approve the final master.

Latest listening revision is **v3**: `render_v3.py` rebuilds the blend from v2 caches with both main leads and their wet returns down 4 dB. Read `reports/v3-engineer-review.md` alongside the unmodified automatic report; its single generic LRA exception is explicitly documented. Use the v3 export filenames in `mix-notes.md`.

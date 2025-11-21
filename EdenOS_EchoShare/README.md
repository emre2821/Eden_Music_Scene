# EdenOS EchoShare

Playlist sharing scripts for the Eden ecosystem.

## Requirements
- Python 3.10+
- Optional GUI extras: `kivy`, `kivymd` (install with `pip install .[gui]`)

## Installation
Install the package so entry points are available:

```bash
pip install .
```

## Usage
Build the EchoPlay prequel playlists via the console script:

```bash
echoshare-prequel
```

You can still run the modules directly for custom paths or debugging:

```bash
python -m EdenOS_EchoShare.echoplay_prequel_complete_build
```

Generated playlist artifacts now live under `examples/` to keep the distributable clean. Inspect `examples/playlists/` for sample `.chaoslink`, `.json`, `.m3u`, and `.txt` exports.

## Notes
- Emotion tagging relies on the shared `emotion_tags_client` module in the repository root; the vendored copies have been removed to avoid drift.
- Mobile deployment scripts (`edenos_echoshare.complete_mobile_build.py`) expect an Android-friendly path; adjust `EDEN_PATH` before running if needed.

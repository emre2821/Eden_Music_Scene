# EchoDJ — AI DJ Agent

A simple Tkinter-based DJ assistant that searches YouTube via `yt-dlp`, previews results, and downloads tracks on demand.

## Features
- Search for songs using natural language queries.
- Present the most relevant YouTube match before downloading.
- Download audio as MP3s after confirmation.
- Async-friendly helpers for background work.
- Dependency checks for `yt-dlp` and `ffmpeg` before runtime.

## Requirements
- Python 3.10+
- `yt-dlp` executable on PATH
- `ffmpeg` installed on the system
- Tkinter available for your OS (bundled with most CPython builds)

Install Python dependencies from the package root:

```bash
pip install .
```

## Running
Use the console script installed with the package:

```bash
dj-agent
```

Or run the module directly for development:

```bash
python -m EchoDJ.dj_agent
```

## Notes
- The module name is `dj_agent.py`; previous docs referenced `ai_dj_gui.py` but that file has been retired.
- If you want the agent to talk to the local emotion tag service, import `emotion_tags_client` from the repository root rather than maintaining a copy inside this package.

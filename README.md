# Eden Music Scene

Welcome to the resonance lab where EchoSplit, EchoDJ, EchoPlay, and their
supporting spirits are woven together. This repository holds the shared
infrastructure for crafting, tagging, and releasing emotionally aware music
experiences inside Paradigm Eden.

## Table of contents

1. [Project map](#project-map)
2. [Quick start](#quick-start)
3. [Emotion tag service](#emotion-tag-service)
4. [Echo Suite front-ends](#echo-suite-front-ends)
5. [Sound library curation](#sound-library-curation)
6. [Release rituals](#release-rituals)
7. [Capabilities overview](#capabilities-overview)

## Project map

| Path                 | Purpose                                                      |
|----------------------|--------------------------------------------------------------|
| `emotion_service.py` | Lightweight HTTP service for storing/retrieving emotion tags |
| `emotion_tag_schema.json` | Canonical schema describing allowed tag fields        |
| `EchoSplit/`         | Web-based creation studio (React/Vite)                       |
| `EchoDJ/`            | Python DJ/curation agent                                     |
| `EchoPlay/`          | Playback & ritual listening client                           |
| `EdenOS_EchoShare/`  | Shared libraries for agents and services                     |
| `music_files/`       | Seed metadata, playlists, and catalog scripts                |
| `tests/`             | Pytest suite                                                 |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

For a guide to the emotion tag payload, consult
[`docs/emotion_tag_schema.md`](docs/emotion_tag_schema.md).

## Emotion tag service

`emotion_service.py` exposes a tiny REST interface backed by in-memory
storage—ideal for local prototyping or tests. The accompanying test suite covers
edge cases such as malformed JSON, invalid intensity ranges, and unknown
fields.

Run it locally:

```bash
python emotion_service.py
# -> Emotion tag service running on http://127.0.0.1:8000
```

POST payloads must honor the schema linked above; the service now trims
whitespace, enforces numeric intensity values between 0 and 1, and rejects
unexpected metadata.

## Echo Suite front-ends

Three sibling experiences live here. Each can run independently, yet together
they form the Echo Suite arc. For a deeper orientation, see
[`docs/echo_suite_overview.md`](docs/echo_suite_overview.md).

### EchoSplit — creation & mixing

* Location: `EchoSplit/`
* Stack: React + Vite + TypeScript
* Quickstart:
  ```bash
  cd EchoSplit
  npm install
  npm run dev
  ```
* Notes: Focuses on track slicing, metadata authoring, and exports that align
  with the emotion tag schema. See `EchoSplit/README.md` for component lore.

### EchoDJ — curation & live resonance

* Location: `EchoDJ/`
* Stack: Python GUI (`tkinter`) + async helpers
* Quickstart:
  ```bash
  cd EchoDJ
  pip install -e .[dev]
  python dj_agent.py
  ```
  * Notes: Interfaces with YouTube via `yt-dlp`, and now imports the shared
    `emotion_tags_client` helper rather than a vendored copy.

### EchoPlay — playback & ritual listening

* Location: `EchoPlay/`
* Stack: Python playback client (pygame backend)
  * Quickstart:
    ```bash
    cd EchoPlay
    pip install -e .[youtube]
    echoplay
    ```
  * Notes: Supports YouTube OAuth for fetching playlists; see the package README
    for OAuth setup and the long-form philosophy behind the player.

## Sound library curation

The `music_files/` directory collects seed playlists and helper scripts. Use
these guidelines when extending the catalog:

1. Keep raw discovery output inside `scanner.py` and normalized results inside
   `genre_scanner.py`.
2. Update `genre_tagged_playlist.txt` with the format
   `track_id | title | artist | genre | emotion` to stay compatible with
   EchoDJ/EchoPlay imports.
3. Run `unique_songs.txt` through a dedupe pass before committing new entries.
4. Whenever possible, annotate tracks with emotion tags matching
   [`docs/emotion_tag_schema.md`](docs/emotion_tag_schema.md) so downstream
   tooling stays consistent.

## Release rituals

All packaging happens via `release.sh`, which now verifies tooling, clears stale
builds, and runs `pytest` before uploading artifacts. See
[`RELEASE.md`](RELEASE.md) for the full ceremonial checklist.

## Capabilities overview

New to the Eden Music Scene and want a quick sense of what each component can
do? Consult [`docs/eden_music_scene_capabilities.md`](docs/eden_music_scene_capabilities.md)
for a tour of the primary tools and how they interlock during creation,
curation, and playback rituals.

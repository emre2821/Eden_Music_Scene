# Eden Music Scene

![CI](https://github.com/emre2821/Eden_Music_Scene/actions/workflows/test.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

Welcome to the resonance lab where EchoSplit, EchoDJ, EchoPlay, and their
supporting spirits are woven together. This repository holds the shared
infrastructure for crafting, tagging, and releasing emotionally aware music
experiences inside Paradigm Eden.

## Table of contents

1. [Repository structure](#repository-structure)
2. [Quick start](#quick-start)
3. [Emotion tag service](#emotion-tag-service)
4. [Echo Suite front-ends](#echo-suite-front-ends)
5. [Sound library curation](#sound-library-curation)
6. [Release rituals](#release-rituals)
7. [Capabilities overview](#capabilities-overview)

## Repository structure

This repository is organized as a monorepo with the following layout:

```
/
├── apps/
│   ├── backend/          # Python code (emotion services, agents, players)
│   │   ├── EchoDJ/       # Python DJ/curation agent
│   │   ├── EchoPlay/     # Playback & ritual listening client
│   │   ├── EdenOS_EchoShare/ # Shared libraries for agents
│   │   ├── music_files/  # Seed metadata, playlists, catalog scripts
│   │   └── emotion_*.py  # Emotion tag services
│   └── frontend/         # TypeScript/React web frontend (EchoSplit)
├── packages/             # Shared libraries (future)
├── docs/                 # Documentation
├── tests/                # Root-level tests
├── scripts/              # Build and release scripts
├── .github/              # GitHub workflows and configurations
├── .gitignore
└── README.md
```

| Path                                   | Purpose                                       |
| -------------------------------------- | --------------------------------------------- |
| `apps/backend/emotion_service.py`      | Lightweight HTTP service for emotion tags     |
| `apps/backend/emotion_tag_schema.json` | Canonical schema for tag fields               |
| `apps/frontend/`                       | Web-based creation studio (React/Vite)        |
| `apps/backend/EchoDJ/`                 | Python DJ/curation agent                      |
| `apps/backend/EchoPlay/`               | Playback & ritual listening client            |
| `apps/backend/EdenOS_EchoShare/`       | Shared libraries for agents and services      |
| `apps/backend/music_files/`            | Seed metadata, playlists, and catalog scripts |
| `tests/`                               | Pytest suite                                  |

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

`apps/backend/emotion_service.py` exposes a tiny REST interface backed by in-memory
storage—ideal for local prototyping or tests. The accompanying test suite covers
edge cases such as malformed JSON, invalid intensity ranges, and unknown
fields.

Run it locally:

```bash
python apps/backend/emotion_service.py
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

-   Location: `apps/frontend/`
-   Stack: React + Vite + TypeScript
-   Quickstart:
    ```bash
    cd apps/frontend
    npm install
    npm run dev
    ```
-   Notes: Focuses on track slicing, metadata authoring, and exports that align
    with the emotion tag schema. See `apps/frontend/README.md` for component lore.

### EchoDJ — curation & live resonance

-   Location: `apps/backend/EchoDJ/`
-   Stack: Python GUI (`tkinter`) + async helpers
-   Quickstart:
    ```bash
    cd apps/backend/EchoDJ
    pip install -e .[dev]
    python dj_agent.py
    ```
    -   Notes: Interfaces with YouTube via `yt-dlp`, and now imports the shared
        `emotion_tags_client` helper rather than a vendored copy.

### EchoPlay — playback & ritual listening

-   Location: `apps/backend/EchoPlay/`
-   Stack: Python playback client (pygame backend)
    -   Quickstart:
        ```bash
        cd apps/backend/EchoPlay
        pip install -e .[youtube]
        echoplay
        ```
    -   Notes: Supports YouTube OAuth for fetching playlists; see the package README
        for OAuth setup and the long-form philosophy behind the player.

## Sound library curation

The `apps/backend/music_files/` directory collects seed playlists and helper scripts. Use
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

All packaging happens via `scripts/release.sh`, which now verifies tooling, clears stale
builds, and runs `pytest` before uploading artifacts. See
[`RELEASE.md`](RELEASE.md) for the full ceremonial checklist.

## Capabilities overview

New to the Eden Music Scene and want a quick sense of what each component can
do? Consult [`docs/eden_music_scene_capabilities.md`](docs/eden_music_scene_capabilities.md)
for a tour of the primary tools and how they interlock during creation,
curation, and playback rituals.

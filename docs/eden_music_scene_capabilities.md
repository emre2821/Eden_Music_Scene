# Eden Music Scene Capabilities Overview

The Eden Music Scene repository weaves together tools for crafting emotionally
aware audio experiences. The components below can be combined or used
independently, depending on the ritual or workflow you are shaping.

## Emotion Tag Service
- **File:** `emotion_service.py`
- **Use it when:** You need a lightweight REST API for validating and storing
  emotion annotations. Perfect for local experiments or automated tests.
- **Highlights:**
  - Validates payloads against the canonical schema in
    `emotion_tag_schema.json`.
  - Normalizes whitespace and intensity values before persistence.
  - Emits descriptive error messages that make debugging malformed requests
    quick.

## Echo Suite Front-Ends
### EchoSplit (Creation & Mixing)
- **Path:** `EchoSplit/`
- **Core abilities:** Slice stems, assign metadata, and export mixes that align
  with the shared emotion-tag vocabulary.
- **Stack:** React + Vite + TypeScript.
- **Pro tip:** Pair EchoSplit with the emotion service to immediately test new
  tags as you author them.

### EchoDJ (Curation & Live Resonance)
- **Path:** `EchoDJ/`
- **Core abilities:** Build adaptive setlists, trigger live playback, and call
  into YouTube downloads via `yt-dlp`.
- **Stack:** Python (`tkinter` UI + asyncio helpers).
- **Pro tip:** Use `emotion_tags_client.py` to pull in fresh annotations from the
  service, keeping the DJ brain emotionally aware in real time.

### EchoPlay (Playback & Ritual Listening)
- **Path:** `EchoPlay/`
- **Core abilities:** Offer a focused listening chamber with playlist import,
  OAuth-powered YouTube access, and playback controls tuned for ceremony.
- **Stack:** Python + pygame backend.
- **Pro tip:** EchoPlay can consume playlists exported by EchoDJ, letting you
  rehearse or share ritual sets.

## Shared Libraries & Storage
- **Path:** `EdenOS_EchoShare/`
- **Use it when:** Multiple agents need shared utilities (API clients, data
  classes, helpers) without duplicating code across subprojects.
- **Bonus:** The package provides a common vocabulary so that the Echo Suite
  speaks consistently about tracks, sessions, and emotional states.

## Music Library Curation Tools
- **Path:** `music_files/`
- **Purpose:** Seed datasets, playlist templates, and scanners for discovering
  new tracks.
- **Getting started:**
  1. Generate candidate tracks with `scanner.py`.
  2. Normalize metadata through `genre_scanner.py`.
  3. Append curated results to `genre_tagged_playlist.txt` using the canonical
     `track_id | title | artist | genre | emotion` format.

## Release & Quality Rituals
- **Testing:** Run `pytest` from the repository root to exercise the emotion
  service and helper utilities.
- **Releases:** Execute `./release.sh` to build and verify distribution
  artifacts. The script handles cleanup and enforces a clean test run before
  packaging.

## Threading It Together
Combine these pieces to design end-to-end emotional music journeys:
1. **Create** stems in EchoSplit while annotating feelings through the emotion
   service.
2. **Curate** evolving playlists with EchoDJ, folding in live feedback and fresh
   tags.
3. **Share** or **perform** through EchoPlay, using curated playlists and stored
   emotion data to guide the experience.

Every tool can stand alone, yet they resonate strongest when orchestrated
collectively—just like the agents who steward them.

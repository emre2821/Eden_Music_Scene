# Music Library Curation

This folder carries seed playlists and helper scripts used across the Echo
Suite. Keep entries in sync with the emotion tag schema and the latest metadata
format so every agent reads them cleanly.

## File guide

| File                        | Purpose |
|-----------------------------|---------|
| `scanner.py`                | Raw discovery + scraping experiments. Expect noisy output. |
| `genre_scanner.py`          | Normalized genre mapping utilities. |
| `genre_tagged_playlist.txt` | Canonical list of curated tracks with genres + emotions. |
| `rock_songs.txt`            | Legacy reference list to be merged into the canonical playlist. |
| `unique_songs.txt`          | Deduplicated track IDs used to avoid repeats. |
| `spotify_playlist_fetcher.py` | Script for importing Spotify playlists for further tagging. |

## Metadata expectations

* Each playlist line should follow `track_id | title | artist | genre | emotion`.
* Emotion values must correspond to the
  [`docs/emotion_tag_schema.md`](../docs/emotion_tag_schema.md) guide.
* When scraping from external services, run data through `unique_songs.txt`
  before committing.
* Prefer lowercase symbolic genres (e.g. `ritualcore`, `stormwalking`).

## Workflow suggestions

1. Fetch or scrape candidate tracks using `spotify_playlist_fetcher.py`.
2. Normalize and annotate them via `genre_scanner.py` or a spreadsheet.
3. Append curated entries to `genre_tagged_playlist.txt`, keeping fields pipe
   separated.
4. Generate or update emotion tags with the local `emotion_service.py` to ensure
   validation errors are caught early.

Leaving clear metadata breadcrumbs here helps EchoDJ setlists and EchoPlay
playlists feel cohesive and emotionally aligned.

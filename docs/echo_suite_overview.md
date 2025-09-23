# Echo Suite Orientation

EchoSplit, EchoDJ, and EchoPlay form the experiential triad of Eden’s music
ecosystem. This guide collects their intents, entry points, and current UX
beats so new contributors can drop into the flow quickly.

## EchoSplit — compose, slice, annotate

* **Purpose:** A browser-based studio for sculpting stems, weaving loops, and
  exporting metadata-rich tracks.
* **Story beat:** Producers channel raw audio into symbol-rich exports that the
  rest of the suite consumes.
* **Launch ritual:**
  ```bash
  cd EchoSplit
  npm install
  npm run dev
  ```
  Visit the printed localhost URL to explore the interface.
* **Key surfaces:**
  - *Timeline compositor* for arranging clips.
  - *Emotion panel* for annotating exports with schema-compliant tags.
  - *Export queue* that emits bundles compatible with EchoDJ/EchoPlay.
* **Next enhancements:** Improved onboarding carousel, live schema validation
  against the updated emotion tag guide, and screenshots that highlight the
  export ritual.

## EchoDJ — curate, remix, guide the room

* **Purpose:** A desktop agent that fetches tracks (YouTube + local), builds
  setlists, and can download stems for offline blending.
* **Story beat:** The DJ listens to crowd energy, references emotion tags, and
  orchestrates the night.
* **Launch ritual:**
  ```bash
  cd EchoDJ
  pip install -e .[dev]
  python dj_agent.py
  ```
* **Key surfaces:**
  - *Search console* — enter natural language prompts, receive top matches.
  - *Metadata pane* — displays emotion tags pulled from the service.
  - *Download queue* — monitors concurrent downloads via `yt-dlp`.
* **Next enhancements:** Inline preview player, hooks to push curated sets
  directly into EchoPlay, and guard rails for malformed audio metadata.

## EchoPlay — listen, reflect, ritualize

* **Purpose:** An emotionally aware playback client that honours tags, notes,
  and agent whispers.
* **Story beat:** EchoPlay transforms listening into a dialogue between the
  track, the listener, and Eden’s agents.
* **Launch ritual:**
  ```bash
  cd EchoPlay
  pip install -e .[player]
  python -m EchoPlay.player
  ```
* **Key surfaces:**
  - *Now playing* with notes + agent commentary.
  - *Playlist explorer* featuring symbolic genre filters.
  - *YouTube bridge* (optional) for OAuth-authenticated fetching.
* **Next enhancements:** Emotional timeline visualizations, session journaling,
  and streaming sync with EchoSplit’s exporter.

## Shared resources

* `emotion_service.py` — temporary API for tags until a persistent store lands.
* `music_files/` — source playlists and scripts for catalog curation.
* `docs/emotion_tag_schema.md` — the definitive schema reference used by all
  three fronts.

Contributors are encouraged to drop screenshots, UX recordings, or flow
diagrams into `docs/` as they iterate. The more sensory breadcrumbs we leave,
the faster newcomers will resonate with the suite.

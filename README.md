# Eden Music Scene

Eden's experimental suite of music tools: online/local streaming, DJ automation, and more.

## Subprojects

| Module | Status | Description |
| ------ | ------ | ----------- |
| **EchoDJ** | beta | Python DJ agent that searches and downloads tracks via `yt-dlp`. |
| **EchoPlay** | planning | Emotion-aware playback engine; early prototypes only. |
| **EchoSplit** | prototype | Web + Python toolkit for splitting and mixing audio with AI. |
| **EdenOS_EchoShare** | prototype | Playlist sharing scripts for EdenOS deployments. |

## Common Prerequisites

Most projects use **Python 3.10+** or **Node.js 18+**. Some modules require `yt-dlp` and `ffmpeg` for media download/conversion.

### Installing Python

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt update && sudo apt install python3 python3-pip
  ```
- **macOS (Homebrew):**
  ```bash
  brew install python
  ```
- **Windows:** Install from [python.org](https://www.python.org/downloads/) and enable "Add to PATH".

### Installing Node.js

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt update && sudo apt install nodejs npm
  ```
- **macOS (Homebrew):**
  ```bash
  brew install node
  ```
- **Windows:** Download the installer from [nodejs.org](https://nodejs.org/) which includes `npm`.

### Installing ffmpeg

- **Linux (Debian/Ubuntu):** `sudo apt install ffmpeg`
- **macOS (Homebrew):** `brew install ffmpeg`
- **Windows:** Download binaries from [ffmpeg.org](https://ffmpeg.org/) and add the `bin` folder to your PATH.

### Installing yt-dlp

`yt-dlp` is a Python package:

```bash
pip install yt-dlp
```

## Modules

### EchoDJ

- **Dependencies:** Python 3, `yt-dlp`, `ffmpeg`.
- **Install:**
  1. Ensure Python 3 is installed.
  2. `pip install yt-dlp`
  3. Install `ffmpeg` using the notes above.
- **Run:**
  ```bash
  python EchoDJ/dj_agent.py
  ```
- **Usage:** Enter a song query, review the recommendation, then download if desired.

### EchoPlay

- **Status:** Early concept; only OAuth prototype exists.
- **Dependencies:** Python 3, `pygame`, `pydub` (planned), `google-auth-oauthlib` for the YouTube OAuth example.
- **Install:**
  1. Install Python 3.
  2. Install packages:
     ```bash
     pip install pygame pydub google-auth-oauthlib
     ```
  3. (Optional) place your Google client secret in `secrets/`.
- **Run example:**
  ```bash
  python EchoPlay/youtube/youtube_oauth_desktop.py
  ```
  This confirms Google API access; the full player UI is still under construction.

### EchoSplit

- **Dependencies:** Node.js 18+, `npm`, Python 3 packages from `requirements.txt`.
- **Install:**
  1. `cd EchoSplit`
  2. Install Node modules:
     ```bash
     npm install
     ```
  3. (Optional) set up Python environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```
  4. Copy `.env.local` and set `GEMINI_API_KEY`.
- **Run:**
  ```bash
  npm run dev
  ```
  Visit `http://localhost:5173` to interact.
- **Usage:** Upload a track and experiment with AI-based splitting and remixing.

### EdenOS_EchoShare

- **Dependencies:** Python 3.
- **Install/Run:**
  1. `cd EdenOS_EchoShare`
  2. Run the build script:
     ```bash
     python edenos_echoshare.complete_mobile_build.py
     ```
- **Usage:** Generates `.txt`, `.json`, and `.chaoslink` playlist files under the path configured inside the script.

---

Contributions are welcome; each module is at a different stage of experimentation and growth.

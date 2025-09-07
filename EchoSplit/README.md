# EchoSplit

Web-based audio splitting toolkit.

## Installation

### Dependencies

- Node.js 18+
- `npm`
- Python 3 (optional for local audio processing)
  - packages listed in `requirements.txt` (`numpy`, `librosa`, `spleeter`, etc.)

### Steps

1. Install Node.js (see root README for platform-specific commands).
2. Navigate into the module:
   ```bash
   cd EchoSplit
   ```
3. Install Node dependencies:
   ```bash
   npm install
   ```
4. (Optional) set up Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. Create `.env.local` and set `GEMINI_API_KEY` to your Gemini API key.

## Usage

Start the development server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser. Upload a track and experiment with AI-based stem splitting and remixing.

### Command-line stem separation

A lightweight CLI is available for running Spleeter locally. It accepts one or
more input audio files and writes the separated stems to the desired folder.

Separate a single track using the default output directory (`outputs/stems`):

```bash
python cli.py path/to/song.mp3
```

Provide multiple files and a custom destination:

```bash
python cli.py input.mp3 another.wav --output my_stems
```

### Demo scripts

The `04_src` directory contains several small Python demos:

- `04_src/00_core/echosplit_player.py` plays a single track. Supply the path
  via `--audio-file` or the `ECHO_AUDIO_FILE` environment variable.
- `04_src/00_core/spleeter_runner.py` wraps Spleeter. Provide an input file with
  `--input`/`ECHO_INPUT` and choose an output folder with
  `--output-dir`/`ECHO_OUTPUT_DIR`.
- `04_src/02_logic/test_analysis.py` analyzes one or more tracks. Pass paths via
  `--tracks` (or comma-separated `ECHO_TRACKS`) and set the render directory with
  `--render-dir`/`ECHO_RENDER_DIR`.

Each script validates that the supplied paths exist before processing.


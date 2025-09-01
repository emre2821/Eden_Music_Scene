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

A lightweight CLI is available for running Spleeter locally. It accepts one
or more input audio files and lets you choose the stem configuration:

```bash
python cli.py input.mp3 another.wav --stems 4 --output outputs/stems
```

`--stems` may be `2`, `4`, or `5`, matching Spleeter's available models.

### Demo player

A small demo player is included for quick audio playback using `pygame`:

```bash
python 04_src/00_core/echosplit_player.py --audio-file path/to/song.mp3
```

Alternatively set the `ECHO_AUDIO_FILE` environment variable instead of using
the flag. The script validates that the provided path exists before playback.


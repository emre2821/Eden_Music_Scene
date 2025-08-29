# Eden_Music_Scene

a cluster of music programs including a online and local streaming, new and unique DAW program, and more to come!

## Usage

### Analyze an audio file

Run the analysis module and supply a path to an audio file either with a CLI flag or the `AUDIO_PATH` environment variable. The script validates the file before loading it.

```bash
python EchoSplit/04_src/02_logic/analysis.py --audio EchoSplit/04_src/02_logic/samples/echoes_of_eden_1.mp3

# or
AUDIO_PATH=EchoSplit/04_src/02_logic/samples/echoes_of_eden_1.mp3 python EchoSplit/04_src/02_logic/analysis.py
```

### Full EchoSplit pipeline

The main entrypoint also accepts an audio path via flag or environment variable and requires a lyrics file:

```bash
python EchoSplit/04_src/00_core/main.py --audio path/to/audio.mp3 --lyrics path/to/lyrics.txt

# or
AUDIO_PATH=path/to/audio.mp3 python EchoSplit/04_src/00_core/main.py --lyrics path/to/lyrics.txt
```

# /src/main.py
# EchoSplit execution entrypoint — designed from Grok's vision.
# Orchestrates emotional decoding, resonance modeling, DAW editing, and CHAOS metadata output.

import json
import os

from daw.editor import Editor
from daw.engine import Engine
from daw.timeline import Timeline
from daw.ui import UI
from logic.adaptive_interface import InterfaceAdapter
from logic.emotion_decoder import EmotionDecoder
from logic.production import Production
from logic.resonance import Resonance
from logic.sovereign_stamp import SovereignStamp


def process_audio(audio_path: str, lyrics_path: str):
    # Load input
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.exists(lyrics_path):
        raise FileNotFoundError(f"Lyrics file not found: {lyrics_path}")

    with open(lyrics_path, "r", encoding="utf-8") as f:
        lyrics = f.read()

    # Emotional decoding
    decoder = EmotionDecoder()
    emotional_meta = decoder.generate_emotional_metadata(lyrics, audio_path)

    # Resonance analysis
    try:
        resonator = Resonance()
        resonant_pairs = resonator.find_resonant_pairings(emotional_meta)
        emotional_meta["resonant_pairs"] = resonant_pairs
    except Exception as e:
        emotional_meta["resonant_pairs"] = f"Resonance error: {e}"

    # Interface adaptation
    interface = InterfaceAdapter()
    interface.react(emotional_meta)

    # Sovereign theming
    theming = SovereignStamp()
    theming.render(emotional_meta)

    # DAW: track, timeline, engine
    editor = Editor()
    timeline = Timeline()
    engine = Engine()
    ui = UI()

    track = editor.import_track(audio_path)
    timeline.add_track(track)
    engine.load_track(track)
    ui.preview_project(editor)

    # Output metadata
    output_path = "outputs/exports/resonance_output.chaosmeta.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(emotional_meta, f, indent=2)

    # Optional: audio layering/export (not yet active)
    production = Production()
    try:
        layered_output = "outputs/exports/layered_mix.wav"
        production.layer_tracks([audio_path], layered_output)
        print(f"🎵 Layered audio exported to {layered_output}")
    except Exception as ex:
        print(f"[warn] Audio layering skipped: {ex}")

    print(f"✅ Full EchoSplit DAW+Emotional analysis complete: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run EchoSplit analysis")
    parser.add_argument(
        "--audio",
        default=os.getenv("AUDIO_PATH"),
        help="Path to the audio file. Can also be set via AUDIO_PATH environment variable.",
    )
    parser.add_argument("--lyrics", required=True, help="Path to the lyrics file.")

    args = parser.parse_args()

    audio_path = args.audio
    if not audio_path:
        parser.error(
            "Audio path must be provided via --audio flag or AUDIO_PATH environment variable."
        )

    lyrics_path = args.lyrics

    process_audio(audio_path, lyrics_path)


if __name__ == "__main__":
    main()

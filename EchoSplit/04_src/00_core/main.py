# /src/main.py
# EchoSplit execution entrypoint — designed from Grok's vision.
# Orchestrates emotional decoding, resonance modeling, DAW editing, and CHAOS metadata output.

import sys
import os
import json

from logic.emotion_decoder import EmotionDecoder
from logic.resonance import Resonance
from logic.player import Player
from logic import analysis
from logic.adaptive_interface import InterfaceAdapter
from logic.sovereign_stamp import SovereignStamp
from logic.production import Production
from logic import musical_decoder

from daw.editor import Editor
from daw.timeline import Timeline
from daw.engine import Engine
from daw.ui import UI

def process_audio(audio_path: str, lyrics_path: str):
    # Load input
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.exists(lyrics_path):
        raise FileNotFoundError(f"Lyrics file not found: {lyrics_path}")

    with open(lyrics_path, 'r', encoding='utf-8') as f:
        lyrics = f.read()

    # Emotional decoding
    decoder = EmotionDecoder()
    emotional_meta = decoder.generate_emotional_metadata(lyrics, audio_path)

    # Resonance analysis
    try:
        resonator = Resonance()
        resonant_pairs = resonator.find_resonant_pairings(emotional_meta)
        emotional_meta['resonant_pairs'] = resonant_pairs
    except Exception as e:
        emotional_meta['resonant_pairs'] = f"Resonance error: {e}"

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
    with open(output_path, 'w', encoding='utf-8') as f:
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
    if len(sys.argv) < 3:
        print("Usage: python main.py <audio_path> <lyrics_path>")
        return

    audio_path = sys.argv[1]
    lyrics_path = sys.argv[2]
    process_audio(audio_path, lyrics_path)

if __name__ == "__main__":
    main()

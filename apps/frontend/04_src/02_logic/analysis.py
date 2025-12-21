# /src/logic/analysis.py
# The mind of EchoSplit: analyzing tempo and genre with precision.
# Built to uncover the pulse and soul of music.

import argparse
import os

import librosa
import numpy as np


def analyze_tempo(audio_path):
    """
    Analyze the tempo (BPM) of an audio file.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        float: Tempo in beats per minute (BPM).
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    y, sr = librosa.load(audio_path)
    tempo = librosa.beat.tempo(y=y, sr=sr)
    if isinstance(tempo, (list, np.ndarray)):
        tempo = float(tempo[0])
    return float(tempo)


def analyze_genre(audio_path):
    """
    Classify the genre of an audio file (simplified example).

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        str: Detected genre (placeholder for a trained model).
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Placeholder: In a real implementation, use a pre-trained model
    # This example uses simple feature-based rules for demonstration
    y, sr = librosa.load(audio_path)
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    if spectral_centroid > 2000:
        return "Rock"
    elif spectral_centroid > 1000:
        return "Pop"
    else:
        return "Classical"


def main():
    parser = argparse.ArgumentParser(
        description="Analyze tempo and genre of an audio file"
    )
    parser.add_argument(
        "--audio",
        default=os.getenv("AUDIO_PATH"),
        help="Path to the audio file. Can also be set via AUDIO_PATH environment variable.",
    )
    args = parser.parse_args()

    audio_path = args.audio
    if not audio_path:
        parser.error(
            "Audio path must be provided via --audio flag or AUDIO_PATH environment variable."
        )

    if not os.path.exists(audio_path):
        parser.error(f"Audio file not found: {audio_path}")

    tempo = analyze_tempo(audio_path)
    genre = analyze_genre(audio_path)

    print(f"Tempo: {tempo}")
    print(f"Genre: {genre}")


if __name__ == "__main__":
    main()

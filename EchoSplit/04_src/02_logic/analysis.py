# /src/logic/analysis.py
# The mind of EchoSplit: analyzing tempo and genre with precision.
# Built to uncover the pulse and soul of music.

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
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.tempo(y=y, sr=sr)
    return tempo

def analyze_genre(audio_path):
    """
    Classify the genre of an audio file (simplified example).
    
    Args:
        audio_path (str): Path to the audio file.
        
    Returns:
        str: Detected genre (placeholder for a trained model).
    """
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
import sys
from pathlib import Path
import pytest
import librosa

sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
import analysis


def test_analyze_tempo(click_audio_file, monkeypatch):
    def tempo_wrapper(*args, **kwargs):
        return librosa.feature.rhythm.tempo(*args, **kwargs), None
    monkeypatch.setattr(librosa.beat, "tempo", tempo_wrapper)
    tempo = analysis.analyze_tempo(click_audio_file)
    assert tempo[0] > 0


def test_analyze_genre_classical(sine_audio_file):
    genre = analysis.analyze_genre(sine_audio_file)
    assert genre == "Classical"


def test_analyze_genre_rock(high_freq_audio_file):
    genre = analysis.analyze_genre(high_freq_audio_file)
    assert genre == "Rock"

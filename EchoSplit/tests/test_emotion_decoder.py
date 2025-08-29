
import sys
from pathlib import Path
import pytest
import librosa

sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
from emotion_decoder import EmotionDecoder


def test_decode_lyrical_emotions():
    decoder = EmotionDecoder()
    emotions = decoder.decode_lyrical_emotions("hope and light in dreams")
    assert "spark" in emotions
    assert emotions["spark"] > 0


def test_decode_audio_emotions(click_audio_file, monkeypatch):
    monkeypatch.setattr(librosa.feature, "chroma", librosa.feature.chroma_stft, raising=False)
    decoder = EmotionDecoder()
    emotions = decoder.decode_audio_emotions(click_audio_file)
    assert "burned chord" in emotions


def test_fuse_emotional_analysis(click_audio_file, monkeypatch):
    monkeypatch.setattr(librosa.feature, "chroma", librosa.feature.chroma_stft, raising=False)
    decoder = EmotionDecoder()
    result = decoder.fuse_emotional_analysis("hope and light", click_audio_file)
    assert "spark" in result
    assert result["spark"] > 0

import importlib
import sys
import types
from pathlib import Path


def load_decoder(monkeypatch):
    monkeypatch.setitem(sys.modules, "librosa", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "numpy", types.SimpleNamespace())
    sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
    if "emotion_decoder" in sys.modules:
        del sys.modules["emotion_decoder"]
    return importlib.import_module("emotion_decoder").EmotionDecoder()


def test_decode_lyrical_emotions(monkeypatch):
    decoder = load_decoder(monkeypatch)
    emotions = decoder.decode_lyrical_emotions("hope and light in dreams")
    assert "spark" in emotions and emotions["spark"] > 0


def test_fuse_emotional_analysis(monkeypatch, audio_clip_path):
    decoder = load_decoder(monkeypatch)
    monkeypatch.setattr(decoder, "decode_audio_emotions", lambda path: {"spark": 0.5})
    result = decoder.fuse_emotional_analysis("hope and light", audio_clip_path)
    assert result["spark"] > 0

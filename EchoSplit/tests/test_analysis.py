import importlib
import sys
import types
from pathlib import Path


def load_analysis(monkeypatch, spectral_value=500):
    """Import the analysis module with a stubbed librosa."""
    fake_librosa = types.SimpleNamespace()
    fake_librosa.load = lambda path: ([0.0], 22050)

    class FakeBeat:
        @staticmethod
        def tempo(y=None, sr=None):
            return [120]

    fake_librosa.beat = FakeBeat()

    class FakeFeature:
        @staticmethod
        def spectral_centroid(y=None, sr=None):
            return [spectral_value]

    fake_librosa.feature = FakeFeature()

    monkeypatch.setitem(sys.modules, "librosa", fake_librosa)
    fake_numpy = types.SimpleNamespace(ndarray=list, mean=lambda x: sum(x) / len(x))
    monkeypatch.setitem(sys.modules, "numpy", fake_numpy)
    sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
    if "analysis" in sys.modules:
        del sys.modules["analysis"]
    return importlib.import_module("analysis")


def test_analyze_tempo(monkeypatch, audio_clip_path):
    analysis = load_analysis(monkeypatch)
    tempo = analysis.analyze_tempo(audio_clip_path)
    assert tempo == 120.0


def test_analyze_genre_classical(monkeypatch, audio_clip_path):
    analysis = load_analysis(monkeypatch, spectral_value=500)
    assert analysis.analyze_genre(audio_clip_path) == "Classical"


def test_analyze_genre_rock(monkeypatch, audio_clip_path):
    analysis = load_analysis(monkeypatch, spectral_value=2500)
    assert analysis.analyze_genre(audio_clip_path) == "Rock"

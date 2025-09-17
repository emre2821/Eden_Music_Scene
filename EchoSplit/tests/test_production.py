import importlib
import sys
import types
from pathlib import Path


def load_production(monkeypatch):
    class DummySegment:
        def overlay(self, other):
            return self

        def export(self, out_path, format="wav"):
            Path(out_path).write_bytes(b"data")

    def from_file(path):
        return DummySegment()

    dummy_pydub = types.SimpleNamespace(
        AudioSegment=types.SimpleNamespace(from_file=from_file)
    )
    monkeypatch.setitem(sys.modules, "pydub", dummy_pydub)
    sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
    if "production" in sys.modules:
        del sys.modules["production"]
    return importlib.import_module("production")


def test_layer_tracks(tmp_path, audio_clip_path, monkeypatch):
    production = load_production(monkeypatch)
    output = tmp_path / "mix.wav"
    production.Production().layer_tracks(
        [audio_clip_path, audio_clip_path], str(output)
    )
    assert output.exists()

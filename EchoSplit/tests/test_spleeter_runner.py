
from pathlib import Path
import pytest

spleeter = pytest.importorskip("spleeter")
spleeter_runner = importlib.import_module("EchoSplit.04_src.00_core.spleeter_runner")


class DummySeparator:
    def __init__(self, *args, **kwargs):
        pass


def test_separate_vocals(tmp_path, audio_clip_path, monkeypatch):
    monkeypatch.setattr(spleeter_runner, "Separator", DummySeparator)
    out_dir = tmp_path / "stems"
    spleeter_runner.separate_vocals(audio_clip_path, str(out_dir))
    assert (out_dir / "vocals.wav").exists()
    assert (out_dir / "accompaniment.wav").exists()


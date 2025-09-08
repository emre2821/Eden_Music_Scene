import importlib
import sys
import types
from pathlib import Path


def load_spleeter_runner(monkeypatch):
    class DummySeparator:
        def __init__(self, *args, **kwargs):
            pass

        def separate_to_file(self, input_path, output_dir):
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            (Path(output_dir) / "vocals.wav").write_bytes(b"v")
            (Path(output_dir) / "accompaniment.wav").write_bytes(b"a")

    spleeter_pkg = types.SimpleNamespace(
        separator=types.SimpleNamespace(Separator=DummySeparator)
    )
    monkeypatch.setitem(sys.modules, "spleeter", spleeter_pkg)
    monkeypatch.setitem(sys.modules, "spleeter.separator", spleeter_pkg.separator)
    return importlib.import_module("EchoSplit.04_src.00_core.spleeter_runner")


def test_separate_vocals(tmp_path, audio_clip_path, monkeypatch):
    runner = load_spleeter_runner(monkeypatch)
    out_dir = tmp_path / "stems"
    runner.separate_vocals(audio_clip_path, str(out_dir))
    vocals = out_dir / "vocals.wav"
    accompaniment = out_dir / "accompaniment.wav"
    assert vocals.exists() and accompaniment.exists()
    assert vocals.stat().st_size > 0
    assert accompaniment.stat().st_size > 0

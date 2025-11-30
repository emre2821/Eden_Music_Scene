import importlib
from pathlib import Path

import pytest


spleeter = pytest.importorskip("spleeter")
spleeter_runner = importlib.import_module("apps.frontend.04_src.00_core.spleeter_runner")



def test_separate_vocals(tmp_path, audio_clip_path, monkeypatch):
    monkeypatch.setattr(spleeter_runner, "Separator", DummySeparator)
    out_dir = tmp_path / "stems"

import importlib.util
from pathlib import Path


def test_map_spectral_to_emotion():
    module_path = Path(__file__).resolve().parents[1] / "04_src" / "02_logic" / "emotion_map.py"
    spec = importlib.util.spec_from_file_location("emotion_map", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.map_spectral_to_emotion([], 44100)
    assert result["energy"] == 0.7
    assert "soothing" in result["tags"]


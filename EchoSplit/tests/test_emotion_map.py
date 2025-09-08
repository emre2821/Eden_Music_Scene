import importlib


def test_map_spectral_to_emotion():
    emotion_map = importlib.import_module("EchoSplit.04_src.02_logic.emotion_map")
    result = emotion_map.map_spectral_to_emotion([0.1], 22050)
    assert result["energy"] == 0.7
    assert result["brightness"] == 0.6
    assert "soothing" in result["tags"]

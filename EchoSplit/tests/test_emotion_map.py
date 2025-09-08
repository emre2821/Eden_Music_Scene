import importlib


emotion_map = importlib.import_module("EchoSplit.04_src.02_logic.emotion_map")


def test_map_spectral_to_emotion():
    result = emotion_map.map_spectral_to_emotion([0.1, 0.2], 44100)
    assert "tags" in result


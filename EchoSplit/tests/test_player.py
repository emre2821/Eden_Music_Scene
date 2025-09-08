import importlib
import pytest


pygame = pytest.importorskip("pygame")
player_module = importlib.import_module("EchoSplit.04_src.02_logic.player")


def test_player_controls(monkeypatch):
    monkeypatch.setattr(pygame.mixer, "init", lambda: None)
    monkeypatch.setattr(pygame.mixer.music, "load", lambda path: None)
    monkeypatch.setattr(pygame.mixer.music, "play", lambda: None)
    monkeypatch.setattr(pygame.mixer.music, "pause", lambda: None)
    monkeypatch.setattr(pygame.mixer.music, "stop", lambda: None)
    monkeypatch.setattr(pygame.mixer.music, "set_volume", lambda v: None)

    player = player_module.Player()
    player.load("song.wav")
    player.play()
    player.pause()
    player.stop()
    player.set_volume(0.5)


import importlib
import pygame

player_mod = importlib.import_module("EchoSplit.04_src.02_logic.player")


def test_player_controls(monkeypatch):
    class DummyMusic:
        def __init__(self):
            self.loaded = None
            self.played = False
            self.paused = False
            self.stopped = False
            self.volume = None

        def load(self, file_path):
            self.loaded = file_path

        def play(self):
            self.played = True

        def pause(self):
            self.paused = True

        def stop(self):
            self.stopped = True

        def set_volume(self, volume):
            self.volume = volume

    dummy_music = DummyMusic()

    class DummyMixer:
        def init(self):
            pass

        music = dummy_music

    monkeypatch.setattr(pygame, "mixer", DummyMixer())

    player = player_mod.Player()
    player.load("song.wav")
    player.play()
    player.pause()
    player.stop()
    player.set_volume(0.5)

    assert dummy_music.loaded == "song.wav"
    assert dummy_music.played
    assert dummy_music.paused
    assert dummy_music.stopped
    assert dummy_music.volume == 0.5

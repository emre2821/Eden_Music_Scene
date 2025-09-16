import importlib
import sys
import types


def load_player(monkeypatch):
    fake_music = types.SimpleNamespace()
    fake_music.load = lambda fp: setattr(fake_music, "loaded", fp)
    fake_music.play = lambda: setattr(fake_music, "played", True)
    fake_music.pause = lambda: setattr(fake_music, "paused", True)
    fake_music.stop = lambda: setattr(fake_music, "stopped", True)
    fake_music.set_volume = lambda v: setattr(fake_music, "volume", v)

    fake_mixer = types.SimpleNamespace(init=lambda: None, music=fake_music)
    fake_pygame = types.SimpleNamespace(mixer=fake_mixer)
    monkeypatch.setitem(sys.modules, "pygame", fake_pygame)

    module = importlib.import_module("EchoSplit.04_src.02_logic.player")
    return module, fake_music


def test_player_controls(monkeypatch, audio_clip_path):
    module, fake_music = load_player(monkeypatch)
    p = module.Player()
    p.load(audio_clip_path)
    p.play()
    p.pause()
    p.set_volume(0.2)
    p.stop()
    assert fake_music.loaded == audio_clip_path
    assert fake_music.played is True
    assert fake_music.paused is True
    assert fake_music.volume == 0.2
    assert fake_music.stopped is True

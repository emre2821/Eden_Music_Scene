import importlib.util
import sys
import types
from pathlib import Path


def load_player(monkeypatch):
    calls = []

    def record(name, arg=None):
        calls.append((name, arg))

    fake_music = types.SimpleNamespace(
        load=lambda path: record("load", path),
        play=lambda: record("play"),
        pause=lambda: record("pause"),
        stop=lambda: record("stop"),
        set_volume=lambda vol: record("set_volume", vol),
    )
    fake_pygame = types.SimpleNamespace(
        mixer=types.SimpleNamespace(init=lambda: record("init"), music=fake_music)
    )
    monkeypatch.setitem(sys.modules, "pygame", fake_pygame)
    module_path = Path(__file__).resolve().parents[1] / "04_src" / "02_logic" / "player.py"
    spec = importlib.util.spec_from_file_location("player", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Player(), calls


def test_player_controls(monkeypatch):
    player, calls = load_player(monkeypatch)
    player.load("song.wav")
    player.play()
    player.pause()
    player.stop()
    player.set_volume(0.5)
    assert calls == [
        ("init", None),
        ("load", "song.wav"),
        ("play", None),
        ("pause", None),
        ("stop", None),
        ("set_volume", 0.5),
    ]


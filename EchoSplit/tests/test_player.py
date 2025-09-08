import sys
import types
from pathlib import Path


def test_player_methods(monkeypatch, audio_clip_path):
    dummy_music = types.SimpleNamespace(
        load=lambda path: None,
        play=lambda: None,
        pause=lambda: None,
        stop=lambda: None,
        set_volume=lambda volume: None,
    )
    dummy_pygame = types.SimpleNamespace(
        mixer=types.SimpleNamespace(init=lambda: None, music=dummy_music)
    )
    monkeypatch.setitem(sys.modules, "pygame", dummy_pygame)
    sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
    if "player" in sys.modules:
        del sys.modules["player"]
    import player

    p = player.Player()
    p.load(audio_clip_path)
    p.play()
    p.pause()
    p.stop()
    p.set_volume(0.5)


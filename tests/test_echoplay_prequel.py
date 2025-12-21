import importlib
import sys
import types
from unittest.mock import Mock

MODULE_PATH = "apps.backend.EdenOS_EchoShare.echoplay_prequel_complete_build"


def _install_gui_stubs(monkeypatch):
    class DummyBase:
        def __init__(self, *args, **kwargs):
            pass

    class DummyDialog(DummyBase):
        def open(self):
            pass

    class DummyListItem(DummyBase):
        def add_widget(self, *args, **kwargs):
            pass

    dummy_clock_module = types.SimpleNamespace(
        Clock=types.SimpleNamespace(schedule_once=lambda func, delay=0: func(None))
    )
    dummy_app_module = types.SimpleNamespace(MDApp=type("MDApp", (), {}))
    dummy_button_module = types.SimpleNamespace(
        MDIconButton=DummyBase, MDRaisedButton=DummyBase
    )
    dummy_dialog_module = types.SimpleNamespace(MDDialog=DummyDialog)
    dummy_list_module = types.SimpleNamespace(ThreeLineListItem=DummyListItem)
    dummy_screen_module = types.SimpleNamespace(MDScreen=DummyBase)

    monkeypatch.setitem(sys.modules, "kivy.clock", dummy_clock_module)
    monkeypatch.setitem(sys.modules, "kivymd.app", dummy_app_module)
    monkeypatch.setitem(sys.modules, "kivymd.uix.button", dummy_button_module)
    monkeypatch.setitem(sys.modules, "kivymd.uix.dialog", dummy_dialog_module)
    monkeypatch.setitem(sys.modules, "kivymd.uix.list", dummy_list_module)
    monkeypatch.setitem(sys.modules, "kivymd.uix.screen", dummy_screen_module)


def load_module(monkeypatch):
    _install_gui_stubs(monkeypatch)
    module = importlib.import_module(MODULE_PATH)
    monkeypatch.setattr(module, "AI_AVAILABLE", True)
    return module


def test_generate_playlist_uses_ai_when_loaded(monkeypatch, capsys):
    module = load_module(monkeypatch)
    cli = module.PlaylistCLI()
    mock_curator = Mock()
    mock_curator.is_loaded.return_value = True
    expected_playlist = [
        {
            "artist": "Echo Star",
            "title": "Nebula Drift",
            "genre": "Synth",
            "reason": "AI",
        }
    ]
    mock_curator.generate_playlist_with_ai.return_value = expected_playlist
    cli.ai_curator = mock_curator

    inputs = iter(["Dreamwave", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    cli.generate_playlist_cli()

    mock_curator.generate_playlist_with_ai.assert_called_once_with("Dreamwave", 2)
    assert mock_curator.generate_playlist_with_ai.call_count == 1
    assert cli.current_playlist == expected_playlist
    output = capsys.readouterr().out
    assert "AI model not loaded yet; using rule-based generator." not in output
    assert "AI features unavailable; using bundled rule-based generator." not in output


def test_generate_playlist_ai_curator_missing_is_loaded(monkeypatch, capsys):
    module = load_module(monkeypatch)
    cli = module.PlaylistCLI()
    mock_curator = Mock()
    # Remove is_loaded attribute
    if hasattr(mock_curator, "is_loaded"):
        del mock_curator.is_loaded
    cli.ai_curator = mock_curator

    inputs = iter(["Dreamwave", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    cli.generate_playlist_cli()

    # Should fallback to rule-based generator
    output = capsys.readouterr().out
    assert "using rule-based generator" in output


def test_generate_playlist_ai_curator_is_loaded_not_callable(monkeypatch, capsys):
    module = load_module(monkeypatch)
    cli = module.PlaylistCLI()
    mock_curator = Mock()
    # Set is_loaded to a non-callable value
    mock_curator.is_loaded = True
    cli.ai_curator = mock_curator

    inputs = iter(["Dreamwave", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    cli.generate_playlist_cli()

    # Should fallback to rule-based generator
    output = capsys.readouterr().out
    assert "using rule-based generator" in output


def test_generate_playlist_falls_back_when_model_not_loaded(monkeypatch, capsys):
    module = load_module(monkeypatch)
    cli = module.PlaylistCLI()
    mock_curator = Mock()
    mock_curator.is_loaded.return_value = False
    cli.ai_curator = mock_curator

    expected_playlist = [
        {
            "artist": "Rule Weaver",
            "title": "Fallback Song",
            "genre": "Ambient",
            "reason": "Rule-based",
        }
    ]

    class DummyGenerator:
        def generate_from_topic(self, topic, count):
            self.args = (topic, count)
            return expected_playlist

    generator_instance = DummyGenerator()
    dummy_module = types.SimpleNamespace(MusicTopicGenerator=lambda: generator_instance)
    monkeypatch.setitem(sys.modules, "apps.backend.music_topic_gen", dummy_module)

    inputs = iter(["Starlight", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    cli.generate_playlist_cli()

    mock_curator.generate_playlist_with_ai.assert_not_called()
    assert generator_instance.args == ("Starlight", 1)
    assert cli.current_playlist == expected_playlist
    output = capsys.readouterr().out
    assert "AI model not loaded yet; using rule-based generator." in output


def test_cli_fallback_succeeds_when_ai_unavailable(monkeypatch, capsys):
    module = load_module(monkeypatch)
    module.AI_AVAILABLE = False
    cli = module.PlaylistCLI()

    inputs = iter(["Chill study", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    cli.generate_playlist_cli()

    output = capsys.readouterr().out
    assert "AI features unavailable; using bundled rule-based generator." in output
    assert "Midnight Reverie" in output
    assert len(cli.current_playlist) == 2

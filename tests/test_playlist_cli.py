from unittest.mock import MagicMock

from apps.backend.EdenOS_EchoShare import echoplay_prequel_complete_build as build


def _make_song(title: str) -> dict:
    return {"artist": "Test Artist", "title": title, "genre": "Test", "reason": "Because"}


def test_generate_playlist_uses_ai_when_loaded(monkeypatch):
    cli = build.PlaylistCLI()
    ai_mock = MagicMock()
    ai_mock.is_loaded.return_value = True
    ai_mock.generate_playlist_with_ai.return_value = [_make_song("AI Song")]
    cli.ai_curator = ai_mock

    monkeypatch.setattr(build, "AI_AVAILABLE", True)
    monkeypatch.setattr(cli, "_get_topic_generator", MagicMock())

    songs = cli.generate_playlist("vibes", 1)

    assert songs == [_make_song("AI Song")]
    ai_mock.generate_playlist_with_ai.assert_called_once_with("vibes", 1)
    cli._get_topic_generator.assert_not_called()


def test_generate_playlist_falls_back_when_model_not_loaded(monkeypatch):
    cli = build.PlaylistCLI()
    ai_mock = MagicMock()
    ai_mock.is_loaded.return_value = False
    cli.ai_curator = ai_mock

    fallback = MagicMock()
    fallback.generate_from_topic.return_value = [_make_song("Fallback Song")]

    monkeypatch.setattr(build, "AI_AVAILABLE", True)
    monkeypatch.setattr(cli, "_get_topic_generator", MagicMock(return_value=fallback))

    songs = cli.generate_playlist("energy", 1)

    assert songs == [_make_song("Fallback Song")]
    fallback.generate_from_topic.assert_called_once_with("energy", 1)
    ai_mock.generate_playlist_with_ai.assert_not_called()


def test_generate_playlist_cli_rejects_negative_count(monkeypatch, capsys):
    cli = build.PlaylistCLI()
    inputs = iter(["calm", "-5"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))
    playlist = [_make_song("Resilient Song")]
    cli.generate_playlist = MagicMock(return_value=playlist)

    cli.generate_playlist_cli()

    captured = capsys.readouterr().out
    assert "Song count must be positive" in captured
    cli.generate_playlist.assert_called_once_with("calm", 20)

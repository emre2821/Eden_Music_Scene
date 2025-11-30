from apps.backend.EdenOS_EchoShare import echoplay_prequel_complete_build as cli_module


def test_cli_fallback_without_ai(monkeypatch):
    monkeypatch.setattr(cli_module, "AI_AVAILABLE", False, raising=False)
    cli = cli_module.PlaylistCLI()

    songs = cli.generate_playlist("lofi study beats", 4)

    assert len(songs) == 4
    for song in songs:
        assert {"title", "artist", "genre", "reason"} <= song.keys()
        assert "Fits the 'lofi study beats' vibe." in song["reason"]

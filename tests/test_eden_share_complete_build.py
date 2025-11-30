import os
import runpy


def test_playlist_created(tmp_path, monkeypatch):
    monkeypatch.setenv("EDEN_ECHOSHARE_PLAYLIST_BASE_DIR", str(tmp_path))

    runpy.run_path("apps/backend/EdenOS_EchoShare/eden_share.complete_build.py", run_name="__main__")

    playlist_path = tmp_path / "you_wanna_fuckin_dance.m3u"
    assert playlist_path.exists(), "Playlist file was not created"

    contents = playlist_path.read_text(encoding="utf-8")
    assert contents.startswith("#EXTM3U\n")
    assert "#EXTINF:-1" in contents


def test_playlist_respects_home_env(tmp_path, monkeypatch):
    monkeypatch.delenv("EDEN_ECHOSHARE_PLAYLIST_BASE_DIR", raising=False)

    new_home = tmp_path / "new_home"
    monkeypatch.setenv("HOME", str(new_home))

    result = runpy.run_path(
        "apps/backend/EdenOS_EchoShare/eden_share.complete_build.py", run_name="__main__"
    )

    default_base_dir = result["DEFAULT_BASE_DIR"]
    playlist_name = result["PLAYLIST_NAME"]
    expanded_dir = default_base_dir.expanduser()
    playlist_path = expanded_dir / playlist_name

    assert playlist_path.exists(), "Playlist file was not created in expanded home"

import os
import runpy


def test_playlist_created(tmp_path, monkeypatch):
    monkeypatch.setenv("EDEN_ECHOSHARE_PLAYLIST_BASE_DIR", str(tmp_path))

    runpy.run_path("EdenOS_EchoShare/eden_share.complete_build.py", run_name="__main__")

    playlist_path = tmp_path / "you_wanna_fuckin_dance.m3u"
    assert playlist_path.exists(), "Playlist file was not created"

    contents = playlist_path.read_text(encoding="utf-8")
    assert contents.startswith("#EXTM3U\n")
    assert "#EXTINF:-1" in contents

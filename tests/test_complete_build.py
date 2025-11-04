from pathlib import Path
import os
import runpy

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "EdenOS_EchoShare" / "eden_share.complete_build.py"
EXPECTED_BASE = "~/EdenOS_Mobile/5_deployments/projects/EdenOS_EchoShare/playlists"
PLAYLIST_NAME = "you_wanna_fuckin_dance.m3u"


def test_complete_build_creates_playlist(tmp_path, monkeypatch):
    """Ensure the complete build script writes its playlist file."""

    target_dir = tmp_path / "playlists"
    original_expanduser = os.path.expanduser

    def fake_expanduser(path):
        return str(target_dir) if path == EXPECTED_BASE else original_expanduser(path)

    monkeypatch.setattr(os.path, "expanduser", fake_expanduser)

    runpy.run_path(str(SCRIPT_PATH))

    playlist_path = target_dir / PLAYLIST_NAME
    assert playlist_path.exists()
    assert playlist_path.read_text(encoding="utf-8").startswith("#EXTM3U\n")

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent.parent / "EdenOS_EchoShare" / "edenos_echoshare.complete_mobile_build.py"
spec = importlib.util.spec_from_file_location("echoshare_mobile", MODULE_PATH)
mobile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mobile)


def test_write_json_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(mobile, "EDEN_PATH", tmp_path)
    data = mobile.write_json()
    json_path = tmp_path / f"{mobile.PLAYLIST_NAME}.json"
    assert json_path.exists()
    assert len(data["songs"]) == len(mobile.SONGS)


def test_write_chaoslink_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(mobile, "EDEN_PATH", tmp_path)
    payload = {"playlist_title": "Test", "created": "2024", "songs": [], "tags": []}
    mobile.write_chaoslink(payload)
    chaos_path = tmp_path / f"{mobile.PLAYLIST_NAME}.chaoslink"
    assert chaos_path.exists()

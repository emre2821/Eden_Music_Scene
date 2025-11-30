import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from apps.backend.EchoPlay.storage import JSONStore


def test_save_and_load_playlist(tmp_path):
    store_path = tmp_path / "store.json"
    store = JSONStore(str(store_path))
    playlist = ["a.mp3", "b.mp3"]
    store.save_playlist(playlist)

    new_store = JSONStore(str(store_path))
    assert new_store.get_playlist() == playlist


def test_record_play_and_crud(tmp_path):
    store_path = tmp_path / "store.json"
    store = JSONStore(str(store_path))

    store.add_track("a.mp3")
    store.record_play("a.mp3")
    store.record_play("a.mp3")
    info = store.get_track("a.mp3")
    assert info["play_count"] == 2

    store.remove_track("a.mp3")
    assert store.get_track("a.mp3") is None
    assert store.get_playlist() == []


def test_load_recovers_from_corrupt_file(tmp_path):
    store_path = tmp_path / "store.json"
    store_path.write_text("{not valid json", encoding="utf-8")

    store = JSONStore(str(store_path))

    assert store.get_playlist() == []
    assert store.get_track("anything") is None
    # Ensure the corrupted file is replaced with valid JSON structure.
    saved_data = json.loads(store_path.read_text(encoding="utf-8"))
    assert saved_data == {"tracks": {}, "playlist": []}


def test_load_resets_when_json_is_not_dict(tmp_path):
    store_path = tmp_path / "store.json"
    store_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

    store = JSONStore(str(store_path))

    assert store.get_playlist() == []
    assert store.get_track("anything") is None
    saved_data = json.loads(store_path.read_text(encoding="utf-8"))
    assert saved_data == {"tracks": {}, "playlist": []}


def test_load_normalizes_missing_keys(tmp_path):
    store_path = tmp_path / "store.json"
    store_path.write_text(json.dumps({"playlist": ["x.mp3"]}), encoding="utf-8")

    store = JSONStore(str(store_path))

    assert store.get_playlist() == ["x.mp3"]
    store.record_play("x.mp3")
    assert store.get_track("x.mp3") == {"title": "x.mp3", "play_count": 1}

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from EchoPlay.storage import JSONStore


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

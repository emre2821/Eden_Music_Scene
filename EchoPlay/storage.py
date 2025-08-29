import json
import os
from typing import Any, Dict, List, Optional


class JSONStore:
    """Simple JSON-backed store for track and playlist data."""

    def __init__(self, filename: str = "playlist_data.json") -> None:
        self.path = os.path.join(os.path.dirname(__file__), filename)
        self.data: Dict[str, Any] = {"tracks": {}, "playlist": []}
        self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        return self.data

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def save_playlist(self, playlist: List[str]) -> None:
        self.data["playlist"] = list(playlist)
        for track in playlist:
            self.data["tracks"].setdefault(
                track, {"title": os.path.basename(track), "play_count": 0}
            )
        self.save()

    def record_play(self, track: str) -> None:
        info = self.data["tracks"].setdefault(
            track, {"title": os.path.basename(track), "play_count": 0}
        )
        info["play_count"] = info.get("play_count", 0) + 1
        self.save()

    def add_track(self, track: str) -> None:
        if track not in self.data["playlist"]:
            self.data["playlist"].append(track)
        self.data["tracks"].setdefault(
            track, {"title": os.path.basename(track), "play_count": 0}
        )
        self.save()

    def remove_track(self, track: str) -> None:
        if track in self.data["playlist"]:
            self.data["playlist"].remove(track)
        self.data["tracks"].pop(track, None)
        self.save()

    def get_playlist(self) -> List[str]:
        return list(self.data.get("playlist", []))

    def get_track(self, track: str) -> Optional[Dict[str, Any]]:
        return self.data["tracks"].get(track)

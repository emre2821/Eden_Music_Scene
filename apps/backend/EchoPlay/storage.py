import os  # Required for path operations and directory creation
import json
from typing import Any, Dict, List, Optional


class JSONStore:
    """Simple JSON-backed store for track and playlist data."""

    def __init__(self, filename: str = "playlist_data.json") -> None:
        self.path = os.path.join(os.path.dirname(__file__), filename)
        self.data: Dict[str, Any] = {"tracks": {}, "playlist": []}
        self._ensure_parent_dir()
        self.load()

    def _ensure_parent_dir(self) -> None:
        parent_dir = os.path.dirname(self.path) or "."
        os.makedirs(parent_dir, exist_ok=True)

    def _default_state(self) -> Dict[str, Any]:
        return {"tracks": {}, "playlist": []}

    def _normalize_data(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure persisted data always has the expected structure."""

        tracks = raw.get("tracks") if isinstance(raw.get("tracks"), dict) else {}
        playlist = (
            list(raw.get("playlist")) if isinstance(raw.get("playlist"), list) else []
        )
        return {"tracks": tracks, "playlist": playlist}

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                # Corrupt or unreadable files should not crash the store; reset safely.
                self.data = self._default_state()
                self.save()
                return self.data

            if isinstance(raw_data, dict):
                normalized = self._normalize_data(raw_data)
                if normalized != raw_data:
                    self.data = normalized
                    self.save()
                else:
                    self.data = normalized
                return self.data

            # Parsed JSON is valid but not a dictionary; reset to default and persist
            self.data = self._default_state()
            self.save()
            return self.data

        self.data = self._default_state()
        return self.data

    def save(self) -> None:
        self._ensure_parent_dir()
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

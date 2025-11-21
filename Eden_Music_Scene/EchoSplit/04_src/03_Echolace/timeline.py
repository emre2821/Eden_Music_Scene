# /src/echolace/timeline.py
# Coordinates the temporal structure of Echolace tracks — the lace between moments.

from .track import Track
from typing import List

class Timeline:
    def __init__(self):
        self.events: List[Track] = []

    def add_track(self, track: Track):
        self.events.append(track)
        self.events.sort(key=lambda t: t.start_time)
        print(f"🧵 Added track '{track.name}' at {track.start_time:.2f}s")

    def get_sequence(self) -> List[str]:
        return [f"{track.name} [{track.start_time:.2f}s → {track.start_time + (track.duration or 0):.2f}s]" for track in self.events]

    def total_duration(self) -> float:
        if not self.events:
            return 0.0
        return max(track.start_time + (track.duration or 0) for track in self.events)

    def clear(self):
        self.events.clear()
        print("🗑️ Timeline cleared.")

# The Timeline is the weave, the structure, the memory of sound across time.
# Here, Echoes become Story.

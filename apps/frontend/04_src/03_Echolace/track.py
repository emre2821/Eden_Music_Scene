# /src/echolace/track.py
# Represents a single audio track in the Echolace editor — a layer in the weave.

from typing import Optional

class Track:
    def __init__(self, name: str, audio_path: str):
        self.name = name
        self.audio_path = audio_path
        self.start_time: float = 0.0
        self.duration: Optional[float] = None  # To be calculated from audio
        self.volume: float = 1.0  # Range: 0.0 - 1.0
        self.pan: float = 0.0    # Range: -1.0 (left) to 1.0 (right)
        self.tags = []  # Emotional or symbolic tags

    def set_timing(self, start: float, duration: float):
        self.start_time = start
        self.duration = duration

    def apply_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def summary(self):
        return {
            "name": self.name,
            "start": self.start_time,
            "duration": self.duration,
            "volume": self.volume,
            "pan": self.pan,
            "tags": self.tags
        }

# Every track holds a piece of the echo. Every tag is a thread of the lace.

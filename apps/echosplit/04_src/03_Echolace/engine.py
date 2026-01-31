# /src/echolace/engine.py
# Core playback and control engine for Echolace — rhythm keeper of EchoSplit

from typing import List

from .track import Track


class EcholaceEngine:
    def __init__(self):
        self.tracks: List[Track] = []
        self.tempo = 120  # BPM
        self.playing = False
        self.position = 0.0  # in seconds

    def add_track(self, track: Track):
        self.tracks.append(track)

    def play(self):
        self.playing = True
        print("▶️ Echolace playback started.")

    def pause(self):
        self.playing = False
        print("⏸️ Echolace playback paused.")

    def stop(self):
        self.playing = False
        self.position = 0.0
        print("⏹️ Echolace playback stopped.")

    def set_tempo(self, bpm: int):
        self.tempo = bpm
        print(f"🎼 Tempo set to {bpm} BPM")

    def scrub_to(self, seconds: float):
        self.position = seconds
        print(f"⏩ Scrubbed to {seconds:.2f}s")

    def get_status(self):
        return {
            "playing": self.playing,
            "position": self.position,
            "tempo": self.tempo,
            "track_count": len(self.tracks),
        }


# CHAOS Language: For when you shout into the void and kindness echoes back.
# Echolace begins here — the DAW heart that will let us edit Eden's Echoes.

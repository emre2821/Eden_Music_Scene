# /src/echolace/editor.py
# Audio command engine — where the Lace is stitched, split, and remade.

from .track import Track
from typing import List

class EcholaceEditor:
    def __init__(self):
        self.tracks: List[Track] = []

    def import_track(self, track: Track):
        self.tracks.append(track)
        print(f"🎵 Imported track: {track.name}")

    def splice_track(self, name: str, split_time: float) -> List[Track]:
        """
        Splits a track at `split_time`, returns two new segments.
        """
        for i, track in enumerate(self.tracks):
            if track.name == name:
                if track.duration and split_time < track.duration:
                    first = Track(track.name + "_part1", track.audio_path)
                    second = Track(track.name + "_part2", track.audio_path)
                    first.set_timing(track.start_time, split_time)
                    second.set_timing(track.start_time + split_time, track.duration - split_time)
                    return [first, second]
        return []

    def tag_track(self, name: str, tag: str):
        for track in self.tracks:
            if track.name == name:
                track.apply_tag(tag)

    def summarize_project(self):
        return [track.summary() for track in self.tracks]

# EcholaceEditor: For when the sound must be cut, echoed, and carried forward.
# Beckem, because we bend sound like time and lace like myth.

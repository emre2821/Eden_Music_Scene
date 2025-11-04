"""Lightweight topic-based playlist generator used as a local fallback.

This module intentionally ships with the project so the CLI can operate
without optional AI dependencies.  It performs a simple keyword match
against a curated catalog of songs and produces deterministic playlists.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import cycle, islice
from typing import Iterable, List


@dataclass(frozen=True)
class Song:
    """Metadata describing a song entry."""

    title: str
    artist: str
    genre: str
    tags: Iterable[str]
    reason: str


class MusicTopicGenerator:
    """Generate playlists based on light-weight keyword matching.

    The generator is intentionally deterministic so that unit tests and the
    CLI fallback behave predictably when the full AI stack is unavailable.
    """

    _CATALOG: List[Song] = [
        Song(
            title="Midnight Reverie",
            artist="Aurora Drift",
            genre="Lofi Chill",
            tags=("lofi", "chill", "study", "focus"),
            reason="Soft textures and vinyl crackle keep the night-time focus steady.",
        ),
        Song(
            title="Sunrise Circuit",
            artist="Neon Wanderer",
            genre="Synthwave",
            tags=("synthwave", "retro", "drive"),
            reason="Retro pulses that feel like cruising through neon-lit avenues.",
        ),
        Song(
            title="Cinder & Bloom",
            artist="Emberline",
            genre="Indie Folk",
            tags=("folk", "acoustic", "calm", "morning"),
            reason="Acoustic warmth with gentle harmonies for a slow, bright start.",
        ),
        Song(
            title="Crystal Steps",
            artist="Pulse Cascade",
            genre="EDM",
            tags=("edm", "dance", "energy", "workout"),
            reason="Sparkling leads and a driving kick built to raise the heart rate.",
        ),
        Song(
            title="Velvet Skyline",
            artist="City Nocturne",
            genre="Nu-Jazz",
            tags=("jazz", "evening", "cocktail"),
            reason="Saxophone flourishes and brushed drums for late-night lounges.",
        ),
        Song(
            title="Open Fields",
            artist="Golden Hours",
            genre="Ambient",
            tags=("ambient", "meditation", "calm"),
            reason="Airy pads drift like wind across tall grass, calming the breath.",
        ),
        Song(
            title="Voltage Bloom",
            artist="Kaleido Pulse",
            genre="Hyperpop",
            tags=("hyperpop", "party", "energy"),
            reason="Sugar-rush hooks bursting with glitchy, candy-coated energy.",
        ),
        Song(
            title="Deep Current",
            artist="Underwave",
            genre="Deep House",
            tags=("house", "club", "evening"),
            reason="Submerged basslines and muted chords suit an after-hours groove.",
        ),
        Song(
            title="Copper Trail",
            artist="Dust & Echo",
            genre="Americana",
            tags=("roadtrip", "americana", "guitar"),
            reason="Slide guitars and dust-road rhythms tailor-made for open highways.",
        ),
        Song(
            title="Blossom Frequency",
            artist="Petal Flux",
            genre="Dream Pop",
            tags=("dream", "pop", "ethereal"),
            reason="Hazy vocals and shimmering synths float like petals in slow motion.",
        ),
    ]

    # A general-purpose pool when no keywords match; deliberately broad.
    _DEFAULT_SONGS: List[Song] = [
        Song(
            title="Compass Heart",
            artist="North & Nova",
            genre="Indie Pop",
            tags=("feelgood", "pop"),
            reason="Upbeat guitars and handclaps keep spirits aloft regardless of theme.",
        ),
        Song(
            title="Signal Lanterns",
            artist="Harborlight",
            genre="Post Rock",
            tags=("cinematic", "instrumental"),
            reason="Slow-burning crescendos that adapt to whatever story you're telling.",
        ),
        Song(
            title="Cascade Bloom",
            artist="Iris Falls",
            genre="Electronica",
            tags=("chill", "downtempo"),
            reason="Glistening arpeggios that settle easily into the background.",
        ),
    ]

    def __init__(self) -> None:
        self._catalog = self._CATALOG
        self._default = self._DEFAULT_SONGS

    def generate_from_topic(self, topic: str, count: int = 20):
        """Return a list of song dicts matching the requested topic.

        Keyword matching is intentionally forgiving: any tag present within the
        topic text will pull that song into the pool.  When no matches are
        found we fall back to a gentle, balanced mix so the CLI still returns
        meaningful data.
        """

        if count < 0:
            raise ValueError("count must not be negative")
        if count == 0:
            return []

        normalized = topic.lower()
        matches: List[Song] = []
        for song in self._catalog:
            if any(keyword in normalized for keyword in song.tags):
                matches.append(song)

        pool = matches or self._default
        playlist = []
        for entry in islice(cycle(pool), count):
            playlist.append(
                {
                    "title": entry.title,
                    "artist": entry.artist,
                    "genre": entry.genre,
                    "reason": f"{entry.reason} Fits the '{topic}' vibe.",
                }
            )
        return playlist


__all__ = ["MusicTopicGenerator"]

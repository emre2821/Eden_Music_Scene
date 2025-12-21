# /src/logic/production.py
# The crafting space of EchoSplit: tools to layer and shape music.
# Designed for clarity and future expansion.

import os

from pydub import AudioSegment


class Production:
    def layer_tracks(self, track_paths, output_path):
        """
        Layer multiple audio tracks into a single mix.

        Args:
            track_paths (list): List of paths to audio files.
            output_path (str): Path to save the mixed audio.
        """
        if not track_paths:
            raise ValueError("No tracks provided for layering.")

        # Load the first track as the base
        mixed = AudioSegment.from_file(track_paths[0])

        # Overlay additional tracks
        for track_path in track_paths[1:]:
            next_track = AudioSegment.from_file(track_path)
            mixed = mixed.overlay(next_track)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export the mixed track
        mixed.export(output_path, format="wav")

# /src/logic/player.py
# The rhythm of EchoSplit: a music player that brings sound to life.
# Built with simplicity and care for seamless playback.

import pygame


class Player:
    def __init__(self):
        """Initialize the Pygame mixer for audio playback."""
        pygame.mixer.init()

    def load(self, file_path):
        """Load an audio file for playback."""
        pygame.mixer.music.load(file_path)

    def play(self):
        """Start or resume playback."""
        pygame.mixer.music.play()

    def pause(self):
        """Pause the current playback."""
        pygame.mixer.music.pause()

    def stop(self):
        """Stop playback entirely."""
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        """Set the playback volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(volume)

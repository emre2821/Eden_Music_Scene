import os
import tkinter as tk
from tkinter import filedialog

import pygame


class EchoPlayer:
    """Minimal Tkinter-based music player using pygame for playback."""

    def __init__(self) -> None:
        pygame.mixer.init()
        self.root = tk.Tk()
        self.root.title("EchoPlay")

        self.playlist: list[str] = []
        self.current_index: int = 0
        self.paused: bool = False

        self.now_playing = tk.StringVar()
        self.now_playing.set("No track loaded")
        tk.Label(self.root, textvariable=self.now_playing).pack(pady=10)

        controls = tk.Frame(self.root)
        controls.pack(pady=5)
        tk.Button(controls, text="Load Playlist", command=self.load_playlist).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Play", command=self.play).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Next", command=self.next_track).pack(side=tk.LEFT, padx=5)

    def load_playlist(self) -> None:
        """Open a file dialog to choose audio files for the playlist."""
        files = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")],
        )
        if files:
            self.playlist = list(files)
            self.current_index = 0
            self.play()

    def play(self) -> None:
        """Play the current track or resume if paused."""
        if not self.playlist:
            return

        track = self.playlist[self.current_index]
        if self.paused and pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.paused = False

        self.now_playing.set(f"Now Playing: {os.path.basename(track)}")

    def pause(self) -> None:
        """Pause playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True

    def next_track(self) -> None:
        """Advance to the next track in the playlist."""
        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.paused = False
        self.play()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = EchoPlayer()
    app.run()

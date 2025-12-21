"""Minimal Tkinter music player for local files."""

import os
import tkinter as tk
from tkinter import filedialog

import pygame


class EchoPlayer:
    """Simple Tkinter music player backed by pygame."""

    def __init__(self) -> None:
        pygame.mixer.init()
        self.root = tk.Tk()
        self.root.title("EchoPlay")

        self.current_track: str | None = None
        self.paused: bool = False

        self.now_playing = tk.StringVar(value="Now Playing: none")
        tk.Label(self.root, textvariable=self.now_playing).pack(pady=10)

        controls = tk.Frame(self.root)
        controls.pack(pady=5)
        tk.Button(controls, text="Open File", command=self.open_file).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(controls, text="Play", command=self.play).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)

    def open_file(self) -> None:
        """Select an audio file to play."""
        file = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")],
        )
        if file:
            self.current_track = file
            self.paused = False
            self.now_playing.set(f"Ready: {os.path.basename(file)}")

    def play(self) -> None:
        """Play or resume the selected track."""
        if not self.current_track:
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.load(self.current_track)
            pygame.mixer.music.play()
        self.now_playing.set(f"Now Playing: {os.path.basename(self.current_track)}")

    def pause(self) -> None:
        """Pause playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            if self.current_track:
                self.now_playing.set(f"Paused: {os.path.basename(self.current_track)}")

    def stop(self) -> None:
        """Stop playback."""
        pygame.mixer.music.stop()
        self.paused = False
        self.now_playing.set("Now Playing: none")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    EchoPlayer().run()


def main() -> None:
    """Entry point for console scripts."""

    EchoPlayer().run()

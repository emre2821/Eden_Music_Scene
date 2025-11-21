"""Simple demo player for EchoSplit audio files.

The audio file to play is provided either via the ``--audio-file`` CLI flag
or the ``ECHO_AUDIO_FILE`` environment variable. The script validates that the
file exists before attempting playback.
"""

import argparse
import asyncio
import os
import platform
from pathlib import Path

import pygame

FPS = 60


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the demo player."""

    parser = argparse.ArgumentParser(description="EchoSplit demo audio player")
    parser.add_argument(
        "--audio-file",
        "-f",
        default=os.environ.get("ECHO_AUDIO_FILE"),
        help="Path to the audio file to play. Can also be set via ECHO_AUDIO_FILE.",
    )
    return parser.parse_args()


def setup(audio_path: str) -> None:
    """Initialize pygame and load the requested audio file."""

    file_path = Path(audio_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    pygame.mixer.init()
    pygame.mixer.music.load(str(file_path))
    pygame.mixer.music.play()


def update_loop() -> None:
    """Handle basic playback events."""

    if not pygame.mixer.music.get_busy():
        print("Playback finished.")
        # Could loop or load next track here


async def main() -> None:
    args = parse_args()
    if not args.audio_file:
        raise SystemExit(
            "Provide an audio file with --audio-file or the ECHO_AUDIO_FILE env variable"
        )

    setup(args.audio_file)

    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)


if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())

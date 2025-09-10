import math
import struct
import wave
from pathlib import Path

import pytest


@pytest.fixture
def audio_clip_path(tmp_path: Path) -> Path:
    """Create a short dummy WAV file and return its path."""
    sample_rate = 44100
    frequency = 440.0
    duration_seconds = 1
    n_samples = int(sample_rate * duration_seconds)
    file_path = tmp_path / "clip.wav"

    with wave.open(str(file_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wav_file.writeframes(struct.pack("<h", value))

    return file_path

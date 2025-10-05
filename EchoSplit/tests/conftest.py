import math
import struct
import wave
from pathlib import Path

import pytest


@pytest.fixture
def audio_clip_path(tmp_path: Path) -> str:
    """Create a temporary sine-wave audio clip for tests."""
    sample_rate = 44100
    duration_seconds = 1
    frequency = 440
    amplitude = 0.5

    output_path = tmp_path / "test_clip.wav"

    frame_count = sample_rate * duration_seconds
    # Convert floating point amplitude to 16-bit PCM samples.
    frames = [
        int(amplitude * 32767 * math.sin(2 * math.pi * frequency * (i / sample_rate)))
        for i in range(frame_count)
    ]

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(struct.pack("<h", frame) for frame in frames))

    return str(output_path)

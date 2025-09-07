import math
import struct
import wave

import pytest


@pytest.fixture
def audio_clip_path(tmp_path):
    """Generate a small sine-wave clip for audio tests and return its path."""
    sample_rate = 8000
    duration = 0.5  # seconds
    frequency = 440.0
    path = tmp_path / "test_clip.wav"
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(int(sample_rate * duration)):
            value = int(32767.0 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wf.writeframes(struct.pack("<h", value))
    return str(path)

import math
import struct
import wave

import pytest


@pytest.fixture
def audio_clip_path(tmp_path):
    """Create a temporary sine-wave audio clip and return its file path."""
    sample_rate = 44100
    duration = 0.5  # seconds
    frequency = 440.0
    path = tmp_path / "test_clip.wav"
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            frames.append(struct.pack("<h", value))
        wf.writeframes(b"".join(frames))
    return str(path)

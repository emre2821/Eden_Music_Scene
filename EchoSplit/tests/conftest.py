import math
import struct
import wave
from pathlib import Path

import pytest


@pytest.fixture
def audio_clip_path(tmp_path):
    """Generate a short sine-wave clip and return its path."""
    sample_rate = 44100
    duration = 0.1  # seconds
    freq = 440.0
    clip_path = tmp_path / "test_clip.wav"
    with wave.open(str(clip_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(int(sample_rate * duration)):
            sample = int(32767 * math.sin(2 * math.pi * freq * i / sample_rate))
            wf.writeframes(struct.pack("<h", sample))
    return str(clip_path)

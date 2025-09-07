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
    num_frames = int(sample_rate * duration)
    path = tmp_path / "test_clip.wav"
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
    return str(path)

import math
import struct
import wave
from pathlib import Path

import pytest


@pytest.fixture
def audio_clip_path(tmp_path):

import pytest
import numpy as np
import soundfile as sf
import librosa

@pytest.fixture
def sine_audio_file(tmp_path):
    sr = 22050
    t = np.linspace(0, 1, sr, False)
    y = 0.5 * np.sin(2 * np.pi * 440 * t)
    file_path = tmp_path / "sine.wav"
    sf.write(file_path, y, sr)
    return str(file_path)

@pytest.fixture
def click_audio_file(tmp_path):
    sr = 22050
    y = librosa.clicks(times=np.arange(0, 1, 0.5), sr=sr, length=sr)
    file_path = tmp_path / "click.wav"
    sf.write(file_path, y, sr)
    return str(file_path)

@pytest.fixture
def high_freq_audio_file(tmp_path):
    sr = 22050
    t = np.linspace(0, 1, sr, False)
    y = 0.5 * np.sin(2 * np.pi * 4000 * t)
    file_path = tmp_path / "high.wav"
    sf.write(file_path, y, sr)
    return str(file_path)

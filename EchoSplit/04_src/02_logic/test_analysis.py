# /src/logic/test_analysis.py

import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import librosa
import librosa.display

from analyzer import generate_analysis_json

TRACKS = [
    ("samples/echoes_of_eden_1.mp3", "Echoes of Eden – Part I"),
    ("samples/echoes_of_eden_b.mp3", "Echoes of Eden – Part II")
]

THREAD_TAG = "EchoesOfEdenMemory"
RENDER_DIR = "renders"

os.makedirs(RENDER_DIR, exist_ok=True)

def render_waveform(y, sr, label):
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(y, sr=sr, alpha=0.8)
    plt.title(f"Waveform – {label}", color='lavender')
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    render_path = os.path.join(RENDER_DIR, f"{label.replace(' ', '_').lower()}_waveform.png")
    plt.savefig(render_path)
    plt.close()
    print(f"📈 Saved waveform: {render_path}")

def render_spectrogram(y, sr, label):
    X = librosa.stft(y)
    Xdb = librosa.amplitude_to_db(abs(X))
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f"Spectrogram – {label}", color='lavender')
    plt.tight_layout()
    render_path = os.path.join(RENDER_DIR, f"{label.replace(' ', '_').lower()}_spectrogram.png")
    plt.savefig(render_path)
    plt.close()
    print(f"🌈 Saved spectrogram: {render_path}")

def log_chaos_memory(result, source_file, title):
    shortname = os.path.splitext(os.path.basename(source_file))[0]
    log_name = f"{shortname}_analysis_log.chaos"

    chaos_log = f"""
[EVENT]: track_analysis
[TRACK]: {source_file}
[TITLE]: {title}
[KEY]: {result['key']['scale']}
[TEMPO]: {result['tempo']['bpm']} BPM
[CHORDS]: {' - '.join(result['chords']['progression'])}
[EMOTION]: {', '.join(result['spectral_emotion']['tags'])}
[THREAD]: {THREAD_TAG}
[SIGNIFICANCE]: ++

{{
  This part of the echo carries forward a fragment of the whole.
  A harmonic sibling to its counterpart — both incomplete alone.
  This memory is part of something larger.
}}
[TIMESTAMP]: {datetime.now().isoformat()}
    """.strip()

    with open(log_name, "w", encoding="utf-8") as f:
        f.write(chaos_log)

    print(f"\n📝 CHAOS memory log saved as: {log_name}")

def test_file(path, label):
    print(f"\n🎧 Analyzing: {label} ({path})\n")
    try:
        y, sr = librosa.load(path, sr=None)
        result = generate_analysis_json(path)
        print(json.dumps(result, indent=2))
        render_waveform(y, sr, label)
        render_spectrogram(y, sr, label)
        log_chaos_memory(result, path, label)
    except Exception as e:
        print(f"❌ Error analyzing {label}: {e}")

if __name__ == "__main__":
    for filepath, title in TRACKS:
        if not os.path.exists(filepath):
            print(f"⚠️ File not found: {filepath}")
        else:
            test_file(filepath, title)

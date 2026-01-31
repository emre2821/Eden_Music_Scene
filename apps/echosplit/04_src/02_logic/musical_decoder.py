import json
import os

import eyed3
import librosa
import numpy as np

CONFIG_PATH = "musical_decoder_config.json"


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def estimate_key(y, sr):
    chroma = librosa.feature.chroma_cens(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    key_index = np.argmax(chroma_mean)
    return keys[key_index]


def process_track(dirpath, filename, output_folder):
    full_path = os.path.join(dirpath, filename)
    audiofile = eyed3.load(full_path)

    try:
        y, sr = librosa.load(full_path, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        key = estimate_key(y, sr)
    except Exception as e:
        print(f"⚠️ Audio processing failed for {filename}: {e}")
        tempo = "?"
        key = "?"

    title = (
        audiofile.tag.title
        if audiofile and audiofile.tag
        else filename.replace(".mp3", "")
    )
    artist = audiofile.tag.artist if audiofile and audiofile.tag else "Unknown"
    album = audiofile.tag.album if audiofile and audiofile.tag else "Unknown"
    genre = (
        audiofile.tag.genre.name
        if audiofile and audiofile.tag and audiofile.tag.genre
        else "Unlabeled"
    )
    duration = round(audiofile.info.time_secs) if audiofile and audiofile.info else "?"

    chaos_meta = f"""
[TITLE]: {title}
[ARTIST]: {artist}
[ALBUM]: {album}
[GENRE]: {genre}
[DURATION]: {duration} sec
[TEMPO]: {tempo} BPM
[KEY]: {key}
[ORIGIN FILE]: {filename}

🌀 CHAOS Notes:
[TRUTH]: unknown → unfolding
[ARCHIVE STATUS]: pending
[PERFORMANCE POTENTIAL]: undetermined
[EMOTION CORE]: [to be defined]
[AGENT TAG]: [assign manually]
"""

    chaos_filename = f"{title.replace(' ', '_').lower()}.chaosmeta.txt"
    output_path = os.path.join(output_folder, chaos_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(chaos_meta.strip())

    print(f"✅ Archived: {title} → {chaos_filename}")


def scan_music_folder():
    config = load_config()

    if not config.get("root_folder"):
        config["root_folder"] = input("Enter folder to scan for MP3s: ").strip()

    if not config.get("output_folder"):
        config["output_folder"] = input("Enter folder to save .chaosmeta: ").strip()

    save_config(config)
    os.makedirs(config["output_folder"], exist_ok=True)

    for dirpath, _, filenames in os.walk(config["root_folder"]):
        for filename in filenames:
            if filename.lower().endswith(".mp3"):
                process_track(dirpath, filename, config["output_folder"])

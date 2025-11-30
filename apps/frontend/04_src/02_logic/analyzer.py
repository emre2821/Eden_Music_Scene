import librosa
import numpy as np
import madmom

GENRE_LABELS = [
    "ambient", "classical", "electronic", "folk", "funk", "hiphop", "jazz",
    "lofi", "metal", "pop", "punk", "rock", "synthwave",
    "Fonk",  # Folk Punk – custom
    "Emo-Punk-Easy Listening"  # tribute genre
]

def predict_genre(y, sr):
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    energy = np.mean(librosa.feature.rms(y=y))
    brightness = spectral_centroid / 1000

    # Very basic mock genre classifier (replace with ML model later)
    if brightness < 1 and tempo < 90:
        genre = "ambient"
    elif tempo > 160 and energy > 0.2:
        genre = "punk"
    elif tempo < 100 and brightness > 2.5:
        genre = "lofi"
    elif 90 < tempo < 130 and 1 < brightness < 2:
        genre = "pop"
    else:
        genre = np.random.choice(GENRE_LABELS)

    confidence = np.clip((energy + brightness) / 2, 0, 1)
    return {"predicted": genre, "confidence": round(float(confidence), 2)}

def generate_analysis_json(filepath):
    y, sr = librosa.load(filepath, sr=None)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    key_index = chroma_mean.argmax()
    key_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = key_list[key_index]

    chords = ["C", "G", "Am", "F"]  # placeholder
    energy = float(np.mean(librosa.feature.rms(y=y)))
    brightness = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))) / 1000
    tags = []
    if energy < 0.02:
        tags.append("gentle")
    elif energy > 0.2:
        tags.append("intense")
    if brightness < 1:
        tags.append("dark")
    elif brightness > 3:
        tags.append("bright")

    genre_info = predict_genre(y, sr)

    return {
        "tempo": {"bpm": round(float(tempo), 2)},
        "key": {"scale": f"{key}_major"},
        "chords": {"progression": chords},
        "spectral_emotion": {
            "energy": round(energy, 2),
            "brightness": round(brightness, 2),
            "tags": tags
        },
        "genre": genre_info
    }

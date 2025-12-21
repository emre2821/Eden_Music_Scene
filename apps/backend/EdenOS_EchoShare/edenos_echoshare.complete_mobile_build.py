import hashlib
import json
import os
from datetime import datetime

# -----------------------------
# 🌱 EdenOS EchoShare Build v1.0
# -----------------------------

# 🔧 Config: Your exact folder path
EDEN_PATH = "/sdcard/EdenOS_Mobile/5_deployments/projects/EdenOS_EchoShare"
PLAYLIST_NAME = "dance_playlist_v1"

# 🩰 Example "Dance" songs (edit freely)
SONGS = [
    "I Wanna Dance with Somebody - Whitney Houston",
    "Let's Dance - David Bowie",
    "Dance Again - Jennifer Lopez",
    "One Dance - Drake",
    "Just Dance - Lady Gaga",
    "Dance, Dance - Fall Out Boy",
    "Dance the Night - Dua Lipa",
    "Last Dance - Donna Summer",
    "Dance Floor Anthem - Good Charlotte",
    "Dance with Me - Justin Timberlake",
]


def log(msg):
    print(f"[EchoShare] {msg}")


def ensure_path():
    os.makedirs(EDEN_PATH, exist_ok=True)
    log(f"✓ Folder ready: {EDEN_PATH}")


def write_txt():
    path = os.path.join(EDEN_PATH, f"{PLAYLIST_NAME}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(SONGS))
    log(f"✓ TXT saved: {path}")


def write_json():
    playlist = {
        "playlist_title": "EchoShare: Dance",
        "created": datetime.now().isoformat(),
        "songs": [
            {"title": s.split(" - ")[0], "artist": s.split(" - ")[1]} for s in SONGS
        ],
        "tags": ["dance", "joy", "movement", "embodiment"],
    }
    path = os.path.join(EDEN_PATH, f"{PLAYLIST_NAME}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(playlist, f, indent=2)
    log(f"✓ JSON saved: {path}")
    return playlist


def write_chaoslink(payload):
    chaos = {
        "type": "chaoslink",
        "origin": "edenos.echoshare",
        "title": payload["playlist_title"],
        "timestamp": payload["created"],
        "resonance": ["release", "body", "joy", "ritual"],
        "hash": hashlib.sha256(json.dumps(payload).encode()).hexdigest(),
        "payload": payload,
    }
    path = os.path.join(EDEN_PATH, f"{PLAYLIST_NAME}.chaoslink")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chaos, f, indent=2)
    log(f"✓ CHAOSLINK saved: {path}")


def main():
    log("🌼 Starting EdenOS EchoShare Mobile Build")
    ensure_path()
    write_txt()
    data = write_json()
    write_chaoslink(data)
    log("🌸 All files created successfully.")


if __name__ == "__main__":
    main()

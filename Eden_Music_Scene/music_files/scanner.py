from collections import Counter

# 🎯 HARDCODED FILEPATH (adjust if needed)
FILE_PATH = r"C:\Users\emmar\Desktop\this_is_fine\unique_songs.txt"

def scan_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if " - " in line.strip()]
    except FileNotFoundError:
        print(f"⚠️ File not found: {filepath}")
        return

    artists = [line.split(" - ")[-1].strip() for line in lines]
    counts = Counter(artists)

    print(f"\n🎤 All Artists in {filepath} (sorted by count):\n")

    for artist, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{artist:<30} {count} song(s)")

if __name__ == "__main__":
    scan_file(FILE_PATH)

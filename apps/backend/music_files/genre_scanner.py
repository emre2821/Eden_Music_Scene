import time
from collections import Counter

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 🔐 API credentials (REPLACE THESE)
CLIENT_ID = "your_spotify_client_id"
CLIENT_SECRET = "your_spotify_client_secret"

# 🎯 HARDCODED PATH TO SONG LIST
SONG_FILE = r"C:\Users\emmar\Desktop\this_is_fine\unique_songs.txt"

# 🎛️ Setup Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
)

# 🧠 Cache to avoid repeated lookups
artist_genre_cache = {}


# 🧹 Extract genres
def get_genres_for_artist(artist):
    if artist in artist_genre_cache:
        return artist_genre_cache[artist]

    try:
        result = sp.search(q=f"artist:{artist}", type="artist", limit=1)
        items = result["artists"]["items"]
        if items:
            genres = items[0].get("genres", [])
            artist_genre_cache[artist] = genres
            return genres
    except Exception as e:
        print(f"⚠️ Error fetching genres for {artist}: {e}")

    artist_genre_cache[artist] = []
    return []


# 🔎 Main logic
def scan_genres():
    with open(SONG_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if " - " in line.strip()]

    genre_counter = Counter()

    for line in lines:
        _, artist = line.rsplit(" - ", 1)
        genres = get_genres_for_artist(artist)
        if not genres:
            continue
        for g in genres:
            genre_counter[g] += 1
        time.sleep(0.2)  # Respect API rate limits

    print("\n🎧 Genre Breakdown:\n")
    for genre, count in genre_counter.most_common():
        print(f"{genre:<30} {count} song(s)")


if __name__ == "__main__":
    scan_genres()

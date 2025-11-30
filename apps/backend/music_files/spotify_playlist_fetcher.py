import spotipy
from spotipy.oauth2 import SpotifyOAuth
from difflib import SequenceMatcher

# 🔐 Your API credentials
CLIENT_ID = "8d58172354784d65b5629db83e0dc68f"
CLIENT_SECRET = "fa3edd3c887f47bdb4743af67578a128"
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'playlist-read-private playlist-read-collaborative'

# 🪪 Your playlist ID (copy it from Spotify's URL)
PLAYLIST_ID = '4967gIQuEXiGBznSzYJw3N'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# 🧼 Normalize
def normalize(song):
    return song.strip().replace("–", "-").lower()

# 🤖 Fuzzy match only if artist is the same
def is_similar(a, b):
    try:
        title_a, artist_a = normalize(a).split(" - ", 1)
        title_b, artist_b = normalize(b).split(" - ", 1)
    except ValueError:
        return False
    if artist_a != artist_b:
        return False
    return 0.88 < SequenceMatcher(None, title_a, title_b).ratio() < 0.97

# 🎶 Grab tracks from the one playlist
def get_tracks():
    tracks = []
    results = sp.playlist_items(PLAYLIST_ID, limit=100)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return [
        f"{item['track']['name'].strip()} - {item['track']['artists'][0]['name'].strip()}"
        for item in tracks if item.get('track')
    ]

# 🧠 Dedupe logic
def get_unique_songs():
    seen = []
    known_duplicates = {}
    print(f"📥 Scanning playlist...")

    for song in get_tracks():
        add = True
        for s in seen:
            if normalize(song) == normalize(s):
                add = False
                break
            elif is_similar(song, s):
                key = tuple(sorted([song, s]))
                if key in known_duplicates:
                    if known_duplicates[key] == 'same':
                        add = False
                        break
                else:
                    print(f"\n🌀 Potential duplicate:")
                    print(f"1️⃣ {s}")
                    print(f"2️⃣ {song}")
                    choice = input("Same song? (y/n): ").strip().lower()
                    if choice == 'y':
                        known_duplicates[key] = 'same'
                        add = False
                        break
                    else:
                        known_duplicates[key] = 'different'
        if add:
            seen.append(song)

    return sorted(seen)

# 🚀 Run it
if __name__ == "__main__":
    unique_songs = get_unique_songs()
    print(f"\n🎧 Final unique song count: {len(unique_songs)}")
    for s in unique_songs:
        print(s)

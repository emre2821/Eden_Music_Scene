import os
from pathlib import Path


BASE_DIR_ENV_VAR = "EDEN_ECHOSHARE_PLAYLIST_BASE_DIR"
DEFAULT_BASE_DIR = Path("~/EdenOS_Mobile/5_deployments/projects/EdenOS_EchoShare/playlists").expanduser()
PLAYLIST_NAME = "you_wanna_fuckin_dance.m3u"


# List of songs
SONGS = [
    "Maniac – Michael Sembello",
    "Boogie Shoes – KC & the Sunshine Band",
    "The Humpty Dance – Digital Underground",
    "Just Dance – Lady Gaga",
    "Dancing on My Own – Calum Scott",
    "Watch Me (Whip / Nae Nae) – Silentó",
    "You Should Be Dancing – Bee Gees",
    "Dance the Night – Dua Lipa",
    "Dancing With Myself – Billy Idol",
    "Dance with the Devil – Breaking Benjamin",
    "Gloria – Laura Branigan",
    "The Twist – Chubby Checker",
    "Dance Monkey – Tones and I",
    "Teach Me How to Dougie – Cali Swag District",
    "Let’s Twist Again – Chubby Checker",
    "Tootsie Roll – 69 Boyz",
    "Let’s Dance – David Bowie",
    "Flashdance (What a Feeling) – Irene Cara",
    "Electric Slide – Marcia Griffiths",
    "Dancing on the Ceiling – Lionel Richie",
    "The Safety Dance – Men Without Hats",
    "Twist and Shout – The Beatles",
    "I Wanna Dance with Somebody – Whitney Houston",
    "Macarena – Los Del Rio",
    "Everybody Dance Now – C+C Music Factory",
    "Dance, Dance – Fall Out Boy",
    "Take Me Out (Dance Remix) – Franz Ferdinand",
    "Venus – Bananarama",
    "Dance With Me – Justin Timberlake",
    "Footloose – Kenny Loggins",
    "I Don’t Feel Like Dancin’ – Scissor Sisters",
    "Levitating – Dua Lipa ft. DaBaby",
    "She Works Hard for the Money – Donna Summer",
    "Dancing with a Stranger – Sam Smith & Normani",
    "Physical – Dua Lipa",
    "Rhythm Is a Dancer – SNAP!",
    "Move Your Feet – Junior Senior",
    "Can’t Get You Out of My Head – Kylie Minogue",
    "Get Up (I Feel Like Being a) Sex Machine – James Brown",
    "Hand Jive – Grease Soundtrack",
]


def build_playlist(base_dir: Path | None = None) -> Path:
    """Create the EchoShare playlist and return its path."""

    resolved_base_dir = Path(
        base_dir
        or os.environ.get(BASE_DIR_ENV_VAR, DEFAULT_BASE_DIR)
    ).expanduser()
    playlist_path = resolved_base_dir / PLAYLIST_NAME

    resolved_base_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Ensured playlist directory exists at {resolved_base_dir}")

    with playlist_path.open("w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        for track in SONGS:
            file.write(f"#EXTINF:-1,{track}\n{track}\n")

    print(f"✅ Playlist saved to {playlist_path}")
    return playlist_path


if __name__ == "__main__":
    build_playlist()

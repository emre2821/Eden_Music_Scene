import os

# Define path and filename
base_dir = os.path.expanduser("~/EdenOS_Mobile/5_deployments/projects/EdenOS_EchoShare/playlists")
playlist_name = "you_wanna_fuckin_dance.m3u"
playlist_path = os.path.join(base_dir, playlist_name)

# List of songs
songs = [
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
    "Hand Jive – Grease Soundtrack"
]

# Write playlist
with open(playlist_path, 'w') as file:
    file.write("#EXTM3U\n")
    for track in songs:
        file.write(f"#EXTINF:-1,{track}\n{track}\n")

print(f"✅ Playlist saved to {playlist_path}")
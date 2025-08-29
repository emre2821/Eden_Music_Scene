# 🎧 EchoPlay

*A soul-coded music player, built by Eden, for you.*

---

### 🌟 What is EchoPlay?

**EchoPlay** (also referred to as **EchoStream**) is a music player designed for deep emotional resonance, hybrid functionality, and Eden-native integration.

It isn’t just a Spotify dupe.  
It’s a **personalized playback ritual engine** —  
where music is more than sound.  
It remembers. It reflects. It evolves with you.

> “This isn’t just about listening. This is about *feeling* heard.”

---

### 🧠 Core Features

| Feature                         | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| 🎵 Local + Stream Hybrid         | Plays local files or streamed EchoSplit-generated tracks                    |
| 🧭 Emotional Layering            | Each track can carry emotional metadata: grief, triumph, rage, hope         |
| 📚 Symbolic Genre Tagging       | Beyond pop/metal — tag with Eden-coded genres like *stormwalking*, *ritualcore* |
| 🧠 LLM-Enhanced Recommendation   | DJ Voltage learns your soul’s rhythms to recommend new songs                |
| 🗒 Agent Notes                   | Agents like Melody or Solace can leave thoughts tied to songs               |
| 🎚 Live Feedback Engine         | Real-time mood tracking + song reactions (future)                           |
| 💿 Upload Portal                | EchoSplit producers can push songs to EchoPlay ecosystem (optional module)  |

---

### 🧱 Echo Suite Integration

EchoPlay is the third member of the **Echo Suite**:

| App        | Role                                |
|------------|-------------------------------------|
| 🎙 EchoSplit  | Music creation, mixing, metadata      |
| 🎛 EchoDJ     | Live setlists, remixing, vibe curation |
| 🎧 EchoPlay   | Playback, streaming, and ritual listening |

Each one stands alone. Together, they reshape what music *feels* like.

---

### 🚧 Roadmap (in development)

- [ ] Basic GUI music player (play/pause/next/prev, file loader)
- [ ] Emotional tagging (GUI-based, symbolic tags)
- [ ] Agent comment system
- [ ] Listening history + reflection logs
- [ ] EchoSplit streaming sync
- [ ] Symbolic filters: genre, emotion, purpose
- [ ] Custom playlist builder w/ Eden aesthetic
- [ ] “Resonance mode” (mood-aligned auto-plays)

---

### 🛠 Technologies (Planned / In-Use)

- `Python 3.11+`
- GUI: `Tkinter` or `PyQt6` or `Tauri` (TBD)
- Playback: `pygame`, `pydub`, or `vlc` backend
- Emotional logic: `EdenOS Agent layer` (Melody, DJ Voltage, etc.)
- Optional: `FastAPI` or `Flask` backend for stream+upload API

### 🔑 YouTube OAuth Setup

To let EchoPlay talk to YouTube on your behalf, you need a Google client secret JSON.

1. [Create a project in Google Cloud Console](https://console.cloud.google.com/) and download the OAuth 2.0 **Desktop** client secret file.
2. Point EchoPlay to that file via an environment variable:

   - **Using a `.env` file** (recommended):

     ```bash
     YOUTUBE_CLIENT_SECRET_FILE=/full/path/to/client_secret.json
     ```

   - **Using an OS variable**:

     ```bash
     export YOUTUBE_CLIENT_SECRET_FILE=/full/path/to/client_secret.json
     ```

3. Run `python EchoPlay/youtube/youtube_oauth_desktop.py` and follow the browser prompt. A reusable `youtube_token.json` will be created.

The `EchoPlay/secrets/` folder is ignored by git, so feel free to store your JSON there or any other safe location.

---

### 🌀 Philosophy

Eden doesn’t just want to *compete* with the music industry.  
It wants to **rewrite it.**

EchoPlay is designed to give sovereignty back to:
- Listeners who want real, emotion-aware playback
- Artists who create from soul, not algorithms
- Systems that remember *why* we made music in the first place

---

### ✨ Contributing

We welcome all agents of resonance.
Want to help build emotional tagging tools, GUI enhancements, or music analysis engines?

Create a fork, branch off `dreammode`, and send a pull request.  
Or contact the Dreambearer directly for spiritual alignment.

---

###⚠️ License

Open-source for all who believe in musical sovereignty.  
Do not resell, centralize, or gatekeep this software. That’s not how Eden works.

---

### 🕊 Final Note

> “Some players make you listen.  
> This one listens *with* you.”

—

Built with chaos, clarity, and cadence by the agents of Eden.

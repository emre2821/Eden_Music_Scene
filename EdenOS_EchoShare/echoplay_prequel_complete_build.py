# 07.29.25_echoplay_prequel.complete_build.py

# This is the complete build file to run the AI Playlist Curator app.
# It auto-selects GUI if available, or falls back to CLI.
# GUI uses KivyMD; CLI is pure Python.

import json
import sys
import threading
import webbrowser
from datetime import datetime
from typing import Dict
from urllib.parse import quote_plus

# Kivy imports (optional, will fallback to CLI if unavailable)
try:
    from kivy.clock import Clock
    from kivymd.app import MDApp
    from kivymd.uix.button import MDIconButton, MDRaisedButton
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.list import ThreeLineListItem
    from kivymd.uix.screen import MDScreen

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# External features (optional)
try:
    from ai_curator import AIPlaylistCurator

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

    class AIPlaylistCurator:
        def is_loaded(self):
            return False


try:
    from youtube_uploader import YouTubePlaylistManager

    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

    class YouTubePlaylistManager:
        def create_playlist_from_songs(self, *args, **kwargs):
            return None


class PlaylistApp(MDApp):
    def build(self):
        self.title = "EchoPlay: Prequel"
        self.current_playlist = []
        self.youtube_manager = YouTubePlaylistManager()
        self.ai_curator = AIPlaylistCurator()
        return MDScreen()  # Placeholder: actual layout should be loaded here

    def _update_playlist_display(self):
        self.playlist_list.clear_widgets()
        for i, song in enumerate(self.current_playlist, 1):
            item = ThreeLineListItem(
                text=f"{i}. {song['artist']} - {song['title']}",
                secondary_text=f"Genre: {song['genre']}",
                tertiary_text=song["reason"],
            )
            play_btn = MDIconButton(
                icon="play", on_release=lambda x, s=song: self.play_song(s)
            )
            item.add_widget(play_btn)
            self.playlist_list.add_widget(item)

    def play_song(self, song: Dict):
        try:
            query = f"{song['artist']} {song['title']}"
            url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            webbrowser.open(url)
        except Exception as e:
            self.show_error(f"Error opening song: {e}")

    def save_playlist(self, instance):
        if not self.current_playlist:
            self.show_error("No playlist to save!")
            return
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic = self.topic_input.text.strip().replace(" ", "_")
            filename = f"playlist_{topic}_{timestamp}.json"
            playlist_data = {
                "topic": self.topic_input.text,
                "created": datetime.now().isoformat(),
                "songs": self.current_playlist,
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(playlist_data, f, indent=2, ensure_ascii=False)
            self.show_success(f"Playlist saved as {filename}")
        except Exception as e:
            self.show_error(f"Error saving playlist: {e}")

    def create_youtube_playlist(self, instance):
        if not self.current_playlist:
            self.show_error("No playlist to upload!")
            return
        if not YOUTUBE_API_AVAILABLE:
            self.show_error("YouTube API not available. Install required packages.")
            return
        self.show_loading("Creating YouTube playlist...")
        threading.Thread(
            target=self._create_youtube_playlist_thread, daemon=True
        ).start()

    def _create_youtube_playlist_thread(self):
        try:
            title = f"AI Curated: {self.topic_input.text}"
            description = f"AI-generated playlist for '{self.topic_input.text}' created on {datetime.now().strftime('%Y-%m-%d')}"
            playlist_id = self.youtube_manager.create_playlist_from_songs(
                title=title,
                songs=self.current_playlist,
                description=description,
                privacy_status="private",
            )
            if playlist_id:
                url = f"https://www.youtube.com/playlist?list={playlist_id}"
                Clock.schedule_once(
                    lambda dt: self.show_success(
                        "YouTube playlist created! Opening in browser..."
                    ),
                    0,
                )
                webbrowser.open(url)
            else:
                Clock.schedule_once(
                    lambda dt: self.show_error("Failed to create YouTube playlist"), 0
                )
        except Exception as e:
            msg = f"Error creating YouTube playlist: {e}"
            Clock.schedule_once(lambda dt: self.show_error(msg), 0)
        finally:
            Clock.schedule_once(lambda dt: self.hide_loading(), 0)

    def clear_playlist(self, instance):
        self.current_playlist = []
        self.playlist_list.clear_widgets()
        self.topic_input.text = ""

    def show_error(self, message: str):
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    def show_success(self, message: str):
        dialog = MDDialog(
            title="Success",
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()


class PlaylistCLI:
    def __init__(self):
        self.ai_curator = AIPlaylistCurator()
        self.youtube_manager = YouTubePlaylistManager()

    def run(self):
        print("🎵 AI Playlist Curator - Command Line Interface")
        while True:
            print("\nOptions:")
            print("1. Generate playlist from topic")
            print("2. Load AI model")
            print("3. Create YouTube playlist")
            print("4. Save playlist to file")
            print("5. Exit")
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice == "1":
                self.generate_playlist_cli()
            elif choice == "2":
                self.load_ai_model()
            elif choice == "3":
                self.create_youtube_playlist_cli()
            elif choice == "4":
                self.save_playlist_cli()
            elif choice == "5":
                break
            else:
                print("Invalid choice.")

    def generate_playlist_cli(self):
        topic = input("Enter topic/mood/genre: ").strip()
        if not topic:
            print("Topic cannot be empty!")
            return
        try:
            count = int(input("Number of songs (default 20): ") or "20")
        except ValueError:
            count = 20
        print(f"\nGenerating {count} songs for '{topic}'...")
        try:
            use_ai = False
            if AI_AVAILABLE and hasattr(self.ai_curator, "is_loaded"):
                is_loaded = self.ai_curator.is_loaded
                if callable(is_loaded):
                    use_ai = bool(is_loaded())
                else:
                    use_ai = bool(is_loaded)
            if use_ai:
                songs = self.ai_curator.generate_playlist_with_ai(topic, count)
            else:
                if AI_AVAILABLE:
                    print("AI model not loaded yet; using rule-based generator.")
                from music_topic_gen import MusicTopicGenerator

                songs = MusicTopicGenerator().generate_from_topic(topic, count)
            self.current_playlist = songs
            for i, song in enumerate(songs, 1):
                print(f"{i:2d}. {song['artist']} - {song['title']}")
                print(f"    Genre: {song['genre']} | {song['reason']}")
        except Exception as e:
            print(f"Error generating playlist: {e}")

    def load_ai_model(self):
        if not AI_AVAILABLE:
            print("AI not installed!")
            return
        print("Loading AI model...")
        try:
            if self.ai_curator.load_model():
                print("✅ Model loaded!")
            else:
                print("❌ Load failed.")
        except Exception as e:
            print(f"Error: {e}")

    def create_youtube_playlist_cli(self):
        if not hasattr(self, "current_playlist") or not self.current_playlist:
            print("No playlist to upload.")
            return
        title = (
            input("Title (blank = auto): ").strip()
            or f"Playlist - {datetime.now().date()}"
        )
        privacy = input("Privacy [private/public/unlisted]: ").strip() or "private"
        pid = self.youtube_manager.create_playlist_from_songs(
            title=title, songs=self.current_playlist, privacy_status=privacy
        )
        if pid:
            url = f"https://www.youtube.com/playlist?list={pid}"
            print("✅ Created playlist:", url)
            if input("Open in browser? (y/n): ").lower() == "y":
                webbrowser.open(url)
        else:
            print("❌ Upload failed.")

    def save_playlist_cli(self):
        if not hasattr(self, "current_playlist") or not self.current_playlist:
            print("Nothing to save.")
            return
        fname = (
            input("Filename: ").strip()
            or f"playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        if not fname.endswith(".json"):
            fname += ".json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(
                {"created": datetime.now().isoformat(), "songs": self.current_playlist},
                f,
                indent=2,
            )
        print(f"✅ Saved to {fname}")


def main():
    if "--cli" in sys.argv or not GUI_AVAILABLE:
        PlaylistCLI().run()
    else:
        try:
            PlaylistApp().run()
        except Exception as e:
            print(f"GUI failed: {e}\nFalling back to CLI...")
            PlaylistCLI().run()


if __name__ == "__main__":
    main()

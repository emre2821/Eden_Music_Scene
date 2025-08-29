# ai_dj_gui.py

import json
import os
import subprocess
import threading  # For non-blocking operations
import tkinter as tk
from tkinter import messagebox, scrolledtext


class AIDJApp:
    def __init__(self, master):
        self.master = master
        master.title("AI DJ Agent")
        master.geometry("700x500")  # Set a default window size
        master.resizable(True, True)  # Allow resizing

        self.current_video_info = None  # To store info of the video found

        # --- Frame for Search Input ---
        self.search_frame = tk.Frame(master, padx=10, pady=10)
        self.search_frame.pack(fill=tk.X)

        self.query_label = tk.Label(
            self.search_frame, text="Song Query (e.g., 'Bohemian Rhapsody Queen'):"
        )
        self.query_label.pack(anchor=tk.W)

        self.query_entry = tk.Entry(self.search_frame, width=60)
        self.query_entry.pack(fill=tk.X, pady=5)
        self.query_entry.bind(
            "<Return>", self.search_music_from_event
        )  # Allow pressing Enter

        self.search_button = tk.Button(
            self.search_frame, text="Search & Recommend", command=self.search_music
        )
        self.search_button.pack(pady=5)

        # --- Frame for Results Display ---
        self.results_frame = tk.LabelFrame(
            master, text="Search Results", padx=10, pady=10
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, wrap=tk.WORD, width=80, height=10
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)  # Make it read-only initially

        # --- Frame for Actions (Download, etc.) ---
        self.action_frame = tk.Frame(master, padx=10, pady=5)
        self.action_frame.pack(fill=tk.X)

        self.download_button = tk.Button(
            self.action_frame,
            text="Download Selected",
            command=self.prompt_download,
            state=tk.DISABLED,
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

        # --- Status Bar ---
        self.status_bar = tk.Label(
            master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Default download path - can be made configurable later
        self.download_directory = os.path.join(
            os.path.expanduser("~"), "Downloaded_AI_Music"
        )
        self.ensure_download_directory_exists(self.download_directory)

    def update_results_text(self, text):
        """Helper to update the read-only results text area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)

    def update_status(self, message):
        """Helper to update the status bar."""
        self.status_bar.config(text=message)

    def ensure_download_directory_exists(self, path):
        """Creates the download directory if it doesn't exist."""
        try:
            os.makedirs(path, exist_ok=True)
            self.update_status(f"Download directory set to: {path}")
        except Exception as e:
            self.update_status(f"Error creating download directory {path}: {e}")
            messagebox.showerror(
                "Directory Error", f"Could not create download directory: {e}"
            )

    def search_music_from_event(self, event):
        """Wrapper for search_music to handle event binding (e.g., Enter key)."""
        self.search_music()

    def search_music(self):
        """Initiates the music search in a separate thread."""
        query = self.query_entry.get().strip()
        if not query:
            self.update_status("Please enter a song query.")
            return

        self.update_status(f"Searching for: '{query}'...")
        self.update_results_text("Searching...\nPlease wait...")
        self.search_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        self.current_video_info = None  # Clear previous info

        # Run search in a separate thread to keep GUI responsive
        threading.Thread(target=self._perform_search, args=(query,)).start()

    def _perform_search(self, query):
        """Performs the actual yt-dlp search."""
        search_command = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            "--default-search",
            "ytsearch",
            query,
        ]

        try:
            result = subprocess.run(
                search_command,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            lines = result.stdout.strip().split("\n")

            if not lines or not lines[0]:
                self.master.after(
                    0,
                    lambda: self.update_results_text(
                        f"No results found for '{query}'.\nTry a different query."
                    ),
                )
                self.master.after(
                    0, lambda: self.update_status(f"No results found for '{query}'.")
                )
                return

            try:
                # Parse the first result (most relevant)
                video_info = json.loads(lines[0])
                self.current_video_info = video_info  # Store for download

                title = video_info.get("title", "Unknown Title")
                uploader = video_info.get("uploader", "Unknown Artist")
                webpage_url = video_info.get("webpage_url", "N/A")

                display_text = (
                    f"AI DJ found:\n"
                    f"Title: '{title}'\n"
                    f"Artist: '{uploader}'\n"
                    f"Source URL: {webpage_url}\n\n"
                    f"Click 'Download Selected' to download this track."
                )
                self.master.after(0, lambda: self.update_results_text(display_text))
                self.master.after(
                    0, lambda: self.update_status(f"Found: '{title}' by '{uploader}'")
                )
                self.master.after(
                    0, lambda: self.download_button.config(state=tk.NORMAL)
                )

            except json.JSONDecodeError as e:
                msg = f"Error parsing search result JSON: {e}\nRaw output:\n{lines[0][:500]}..."
                self.master.after(0, lambda: self.update_results_text(msg))
                self.master.after(
                    0, lambda: self.update_status("Error parsing search result.")
                )

        except subprocess.CalledProcessError as e:
            error_message = f"Error during search:\n{e.stderr}\nPlease ensure yt-dlp and ffmpeg are correctly installed and in your system's PATH."
            self.master.after(0, lambda: self.update_results_text(error_message))
            self.master.after(0, lambda: self.update_status("Search failed."))
            messagebox.showerror("Search Error", error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred during search: {e}"
            self.master.after(0, lambda: self.update_results_text(error_message))
            self.master.after(0, lambda: self.update_status("Search failed."))
            messagebox.showerror("Error", error_message)
        finally:
            self.master.after(0, lambda: self.search_button.config(state=tk.NORMAL))

    def prompt_download(self):
        """Prompts user for download confirmation and starts download in a new thread."""
        if not self.current_video_info:
            messagebox.showinfo("No Selection", "Please search for a song first.")
            return

        title = self.current_video_info.get("title", "Unknown Title")
        uploader = self.current_video_info.get("uploader", "Unknown Artist")

        # Use tkinter's messagebox for permission
        if messagebox.askyesno(
            "Download Confirmation",
            f"Do you want to download '{title}' by '{uploader}'?",
        ):
            self.update_status(f"Starting download for '{title}'...")
            self.download_button.config(state=tk.DISABLED)
            # Run download in a separate thread
            threading.Thread(
                target=self._perform_download, args=(self.current_video_info,)
            ).start()
        else:
            self.update_status("Download cancelled by user.")

    def _perform_download(self, video_info):
        """Performs the actual yt-dlp download."""
        webpage_url = video_info.get("webpage_url")
        title = video_info.get("title", "Unknown Title")
        uploader = video_info.get("uploader", "Unknown Artist")

        if not webpage_url:
            self.master.after(
                0, lambda: self.update_status("Error: No URL available for download.")
            )
            messagebox.showerror("Download Error", "No URL available for download.")
            return

        # Sanitize filename to prevent issues with OS paths
        # Replace forbidden characters with underscores, and limit length if needed
        # This is a basic sanitization. For robust solutions, consider 'slugify' libraries.
        sanitized_title = "".join(
            c if c.isalnum() or c in (" ", "-", "_", ".") else "_" for c in title
        ).strip()
        sanitized_uploader = "".join(
            c if c.isalnum() or c in (" ", "-", "_", ".") else "_" for c in uploader
        ).strip()

        output_filename_template = os.path.join(
            self.download_directory,
            f"{sanitized_title} by {sanitized_uploader}.%(ext)s",
        )

        download_command = [
            "yt-dlp",
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            "-o",
            output_filename_template,
            webpage_url,
        ]

        try:
            # subprocess.run(..., text=True) is problematic with large output or non-UTF8.
            # For progress, you'd typically run with check=False and read stdout incrementally.
            # For simplicity in this single-file GUI, we'll just run it and check the result.
            self.master.after(
                0,
                lambda: self.update_status(
                    f"Downloading '{title}'... (This may take a moment)"
                ),
            )
            subprocess.run(
                download_command,
                capture_output=True,
                check=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # You can parse process.stdout for progress if needed, but it's complex for single-file GUI.
            self.master.after(
                0,
                lambda: self.update_status(
                    f"Successfully downloaded '{title}' to '{self.download_directory}'"
                ),
            )
            self.master.after(
                0,
                lambda: messagebox.showinfo(
                    "Download Complete", f"'{title}' downloaded successfully!"
                ),
            )
        except subprocess.CalledProcessError as e:
            error_message = f"Error during download:\n{e.stderr}\nMake sure yt-dlp and ffmpeg are installed and accessible."
            self.master.after(0, lambda: self.update_status("Download failed."))
            self.master.after(
                0, lambda: messagebox.showerror("Download Error", error_message)
            )
        except Exception as e:
            error_message = f"An unexpected error occurred during download: {e}"
            self.master.after(0, lambda: self.update_status("Download failed."))
            self.master.after(0, lambda: messagebox.showerror("Error", error_message))
        finally:
            self.master.after(
                0, lambda: self.download_button.config(state=tk.NORMAL)
            )  # Re-enable download button


def main() -> None:
    """Launch the AI DJ GUI."""
    root = tk.Tk()
    AIDJApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

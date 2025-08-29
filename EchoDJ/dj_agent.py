# ai_dj_gui.py

import asyncio
import json
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox


def build_yt_dlp_search_command(query: str) -> list[str]:
    """Construct the yt-dlp command for searching."""
    return [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--default-search",
        "ytsearch",
        query,
    ]


def build_yt_dlp_download_command(output_template: str, url: str) -> list[str]:
    """Construct the yt-dlp command for downloading audio."""
    return [
        "yt-dlp",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--newline",
        "-o",
        output_template,
        url,
    ]


class AIDJApp:
    def __init__(self, master):
        self.master = master
        master.title("AI DJ Agent")
        master.geometry("700x600")
        master.resizable(True, True)

        self.current_video_info = None
        self.download_tasks = set()

        # --- Frame for Search Input ---
        self.search_frame = tk.Frame(master, padx=10, pady=10)
        self.search_frame.pack(fill=tk.X)

        self.query_label = tk.Label(
            self.search_frame, text="Song Query (e.g., 'Bohemian Rhapsody Queen'):"
        )
        self.query_label.pack(anchor=tk.W)

        self.query_entry = tk.Entry(self.search_frame, width=60)
        self.query_entry.pack(fill=tk.X, pady=5)
        self.query_entry.bind("<Return>", self.search_music_from_event)

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
        self.results_text.config(state=tk.DISABLED)

        # --- Frame for Actions ---
        self.action_frame = tk.Frame(master, padx=10, pady=5)
        self.action_frame.pack(fill=tk.X)

        self.download_button = tk.Button(
            self.action_frame,
            text="Download Selected",
            command=self.prompt_download,
            state=tk.DISABLED,
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

        # --- Frame for Download Progress ---
        self.progress_frame = tk.LabelFrame(
            master, text="Download Progress", padx=10, pady=10
        )
        self.progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.progress_list = tk.Listbox(self.progress_frame, height=6)
        self.progress_list.pack(fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Default download path
        self.download_directory = os.path.join(
            os.path.expanduser("~"), "Downloaded_AI_Music"
        )
        self.ensure_download_directory_exists(self.download_directory)

    # -------------------- Helper Methods --------------------
    def update_results_text(self, text: str) -> None:
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)

    def update_status(self, message: str) -> None:
        self.status_bar.config(text=message)

    def ensure_download_directory_exists(self, path: str) -> None:
        try:
            os.makedirs(path, exist_ok=True)
            self.update_status(f"Download directory set to: {path}")
        except Exception as e:
            self.update_status(f"Error creating download directory {path}: {e}")
            messagebox.showerror("Directory Error", f"Could not create download directory: {e}")

    def search_music_from_event(self, event):
        self.search_music()

    # -------------------- Search Logic --------------------
    def search_music(self) -> None:
        query = self.query_entry.get().strip()
        if not query:
            self.update_status("Please enter a song query.")
            return

        self.update_status(f"Searching for: '{query}'...")
        self.update_results_text("Searching...\nPlease wait...")
        self.search_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        self.current_video_info = None

        asyncio.create_task(self._perform_search(query))

    async def _perform_search(self, query: str) -> None:
        search_command = build_yt_dlp_search_command(query)
        try:
            proc = await asyncio.create_subprocess_exec(
                *search_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                error_message = (
                    f"Error during search:\n{stderr.decode('utf-8', 'replace')}\n"
                    "Please ensure yt-dlp and ffmpeg are correctly installed and in your system's PATH."
                )
                self.update_results_text(error_message)
                self.update_status("Search failed.")
                messagebox.showerror("Search Error", error_message)
                return

            lines = stdout.decode("utf-8", errors="replace").strip().split("\n")
            if not lines or not lines[0]:
                self.update_results_text(
                    f"No results found for '{query}'.\nTry a different query."
                )
                self.update_status(f"No results found for '{query}'.")
                return

            try:
                video_info = json.loads(lines[0])
                self.current_video_info = video_info

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
                self.update_results_text(display_text)
                self.update_status(f"Found: '{title}' by '{uploader}'")
                self.download_button.config(state=tk.NORMAL)
            except json.JSONDecodeError as e:
                self.update_results_text(
                    f"Error parsing search result JSON: {e}\nRaw output:\n{lines[0][:500]}..."
                )
                self.update_status("Error parsing search result.")
        except Exception as e:
            error_message = f"An unexpected error occurred during search: {e}"
            self.update_results_text(error_message)
            self.update_status("Search failed.")
            messagebox.showerror("Error", error_message)
        finally:
            self.search_button.config(state=tk.NORMAL)

    # -------------------- Download Logic --------------------
    def prompt_download(self) -> None:
        if not self.current_video_info:
            messagebox.showinfo("No Selection", "Please search for a song first.")
            return

        title = self.current_video_info.get("title", "Unknown Title")
        uploader = self.current_video_info.get("uploader", "Unknown Artist")

        if messagebox.askyesno(
            "Download Confirmation",
            f"Do you want to download '{title}' by '{uploader}'?",
        ):
            self.update_status(f"Starting download for '{title}'...")
            self.start_download_task(self.current_video_info)
        else:
            self.update_status("Download cancelled by user.")

    def start_download_task(self, video_info: dict) -> None:
        title = video_info.get("title", "Unknown Title")
        index = self.progress_list.size()
        self.progress_list.insert(tk.END, f"{title}: starting...")

        task = asyncio.create_task(self._perform_download(video_info, index))
        self.download_tasks.add(task)
        task.add_done_callback(lambda t, idx=index: self._on_download_done(t, idx))
        self.update_status(f"{len(self.download_tasks)} download(s) in progress")

    def _on_download_done(self, task: asyncio.Task, index: int) -> None:
        self.download_tasks.discard(task)
        if self.download_tasks:
            self.update_status(f"{len(self.download_tasks)} download(s) in progress")
        else:
            self.update_status("Ready")

    def update_progress_entry(self, index: int, text: str) -> None:
        self.progress_list.delete(index)
        self.progress_list.insert(index, text)

    async def _perform_download(self, video_info: dict, index: int) -> None:
        webpage_url = video_info.get("webpage_url")
        title = video_info.get("title", "Unknown Title")
        uploader = video_info.get("uploader", "Unknown Artist")

        if not webpage_url:
            self.update_progress_entry(index, f"{title}: no URL available")
            messagebox.showerror("Download Error", "No URL available for download.")
            return

        sanitized_title = "".join(
            c if c.isalnum() or c in (" ", "-", "_", ".") else "_"
            for c in title
        ).strip()
        sanitized_uploader = "".join(
            c if c.isalnum() or c in (" ", "-", "_", ".") else "_"
            for c in uploader
        ).strip()
        output_template = os.path.join(
            self.download_directory, f"{sanitized_title} by {sanitized_uploader}.%(ext)s"
        )

        download_command = build_yt_dlp_download_command(
            output_template, webpage_url
        )

        try:
            proc = await asyncio.create_subprocess_exec(
                *download_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").strip()
                if decoded:
                    if "[download]" in decoded and "%" in decoded:
                        progress = decoded.split("[download]")[-1].strip()
                        self.update_progress_entry(index, f"{title}: {progress}")
            await proc.wait()
            if proc.returncode == 0:
                self.update_progress_entry(index, f"{title}: completed")
                messagebox.showinfo(
                    "Download Complete", f"'{title}' downloaded successfully!"
                )
            else:
                self.update_progress_entry(index, f"{title}: failed")
                messagebox.showerror(
                    "Download Error", f"Download failed for '{title}'."
                )
        except Exception as e:
            self.update_progress_entry(index, f"{title}: error {e}")
            messagebox.showerror(
                "Error", f"An unexpected error occurred during download: {e}"
            )

    # -------------------- Tkinter Loop --------------------
    async def run(self) -> None:
        try:
            while True:
                self.master.update()
                await asyncio.sleep(0.01)
        except tk.TclError:
            pass


async def main() -> None:
    root = tk.Tk()
    app = AIDJApp(root)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())


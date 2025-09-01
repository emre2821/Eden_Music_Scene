"""Simple AI DJ application using Tkinter and ``yt-dlp``.

This module exposes :class:`AIDJApp`, a minimal GUI that searches for
tracks on YouTube using ``yt-dlp``.  The search results are shown in a
``tk.Listbox`` and the user can choose one result to download.  The
download functionality is intentionally lightweight – it only appends a
message to the progress list.  The focus of the implementation is the
search logic and the ability to select an item from the populated list.

The tests for this kata exercise only interact with
``ensure_download_directory_exists``.  Nevertheless the surrounding code
is provided so that the module can be imported without errors and the GUI
can be explored manually if desired.
"""

from __future__ import annotations

import asyncio
import json
import os
import tkinter as tk
from tkinter import messagebox


def check_dependencies() -> bool:
    """Ensure ``yt-dlp`` and ``ffmpeg`` are available on the system."""

    missing = [dep for dep in ("yt-dlp", "ffmpeg") if shutil.which(dep) is None]
    if missing:
        messagebox.showerror(
            "Missing Dependencies",
            f"Required tools not found: {', '.join(missing)}",
        )
        return False
    return True


def build_yt_dlp_search_command(query: str) -> list[str]:
    """Return a ``yt-dlp`` command that searches YouTube for ``query``.

    The command uses ``ytsearch`` with a limit of five results and emits
    JSON lines for each result.
    """

    return ["yt-dlp", "-j", f"ytsearch5:{query}"]


class AIDJApp:
    """Tiny Tk-based interface for searching and downloading music."""

    def __init__(self, master: tk.Misc) -> None:
        self.master = master
        if not check_dependencies():
            raise RuntimeError("Missing required external tools.")
        master.title("AI DJ Agent")

        # --- Search widgets -------------------------------------------------
        self.search_frame = tk.Frame(master, padx=10, pady=10)
        self.search_frame.pack(fill=tk.X)

        self.query_entry = tk.Entry(self.search_frame, width=60)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.search_button = tk.Button(
            self.search_frame, text="Search", command=self.search_music
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        # --- Results list ---------------------------------------------------
        self.results_frame = tk.LabelFrame(
            master, text="Search Results", padx=10, pady=10
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.results_list = tk.Listbox(self.results_frame, height=10)
        self.results_list.pack(fill=tk.BOTH, expand=True)
        self.results_list.bind("<<ListboxSelect>>", self._on_result_select)

        # --- Actions --------------------------------------------------------
        self.action_frame = tk.Frame(master, padx=10, pady=5)
        self.action_frame.pack(fill=tk.X)

        self.download_button = tk.Button(
            self.action_frame,
            text="Download Selected",
            command=self.prompt_download,
            state=tk.DISABLED,
        )
        self.download_button.pack(side=tk.LEFT)

        # --- Download progress ---------------------------------------------
        self.progress_frame = tk.LabelFrame(
            master, text="Download Progress", padx=10, pady=10
        )
        self.progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.progress_list = tk.Listbox(self.progress_frame, height=6)
        self.progress_list.pack(fill=tk.BOTH, expand=True)

        # --- Status bar -----------------------------------------------------
        self.status_bar = tk.Label(
            master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Prepare download directory
        self.download_directory = os.path.join(
            os.path.expanduser("~"), "Downloaded_AI_Music"
        )
        self.ensure_download_directory_exists(self.download_directory)

        # State
        self.current_results: list[dict] = []
        self.current_video_info: dict | None = None

    # ------------------------------------------------------------------
    # Helper methods
    def update_status(self, message: str) -> None:
        self.status_bar.config(text=message)

    def ensure_download_directory_exists(self, path: os.PathLike[str] | str) -> None:
        """Create ``path`` if it doesn't already exist.

        The method is tiny but is used by the unit tests to ensure that
        the directory creation logic works as expected.
        """

        try:
            os.makedirs(path, exist_ok=True)
            self.update_status(f"Download directory set to: {path}")
        except Exception as exc:  # pragma: no cover - exceptional path
            self.update_status(f"Error creating download directory {path}: {exc}")
            messagebox.showerror(
                "Directory Error", f"Could not create download directory: {exc}"
            )

    # ------------------------------------------------------------------
    # Search logic
    def search_music(self) -> None:
        """Kick off a search based on the query entry's contents."""

        query = self.query_entry.get().strip()
        if not query:
            self.update_status("Please enter a song query.")
            return

        self.update_status(f"Searching for: '{query}'...")
        # Run the async search synchronously for simplicity.  The GUI is
        # small enough that the blocking call is acceptable here.
        asyncio.run(self._perform_search(query))

    async def _perform_search(self, query: str) -> None:
        """Execute ``yt-dlp`` and populate the results list.

        The ``yt-dlp`` command returns one JSON object per line.  All
        lines are parsed and stored so that the user can choose which one
        to download.
        """

        search_command = build_yt_dlp_search_command(query)

        proc = await asyncio.create_subprocess_exec(
            *search_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            self.update_status("Search failed.")
            messagebox.showerror("Search Error", stderr.decode())
            return

        # Parse all JSON lines from yt-dlp output
        self.current_results = []
        for line in stdout.decode().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                info = json.loads(line)
                self.current_results.append(info)
            except json.JSONDecodeError:  # pragma: no cover - defensive
                continue

        # Populate the listbox with ``title – uploader`` pairs
        self.results_list.delete(0, tk.END)
        for info in self.current_results:
            title = info.get("title", "Unknown Title")
            uploader = info.get("uploader", "Unknown Artist")
            self.results_list.insert(tk.END, f"{title} – {uploader}")

        self.current_video_info = None
        self.download_button.config(state=tk.DISABLED)
        if self.current_results:
            self.update_status(
                f"Found {len(self.current_results)} result(s). Select one to download."
            )
        else:
            self.update_status("No results found.")

    # ------------------------------------------------------------------
    # Selection and download logic
    def _on_result_select(self, event: tk.Event) -> None:
        """Handle the user selecting an item in the results list."""

        selection = self.results_list.curselection()
        if not selection:
            self.current_video_info = None
            self.download_button.config(state=tk.DISABLED)
            return

        index = selection[0]
        self.current_video_info = self.current_results[index]
        self.download_button.config(state=tk.NORMAL)

    def prompt_download(self) -> None:
        """Download the currently highlighted item in the results list."""

        selection = self.results_list.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a track to download.")
            return

        index = selection[0]
        info = self.current_results[index]
        title = info.get("title", "Unknown Title")
        uploader = info.get("uploader", "Unknown Artist")

        if not messagebox.askyesno(
            "Download Confirmation",
            f"Do you want to download '{title}' by '{uploader}'?",
        ):
            return

        self.update_status(f"Starting download for '{title}'...")

        url = info.get("webpage_url")
        if url:
            download_cmd = [
                "yt-dlp",
                "-o",
                os.path.join(self.download_directory, "%(title)s.%(ext)s"),
                url,
            ]
            proc = subprocess.run(
                download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if proc.returncode != 0:  # pragma: no cover - depends on network
                messagebox.showerror("Download Error", proc.stderr.decode())
                self.update_status("Download failed.")
                return

        self.progress_list.insert(tk.END, f"Downloaded: {title} – {uploader}")
        self.update_status("Download complete.")


__all__ = ["AIDJApp", "build_yt_dlp_search_command"]

# ai_dj_gui.py




class AIDJApp:
    def __init__(self, master):
        self.master = master
        master.title("AI DJ Agent")

        # --- Frame for Search Input ---
        self.search_frame = tk.Frame(master, padx=10, pady=10)
        self.search_frame.pack(fill=tk.X)

        self.query_label = tk.Label(
            self.search_frame, text="Song Query (e.g., 'Bohemian Rhapsody Queen'):"
        )
        self.query_label.pack(anchor=tk.W)

        self.query_entry = tk.Entry(self.search_frame, width=60)
        self.query_entry.pack(fill=tk.X, pady=5)

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
        self.status_bar = tk.Label(
            master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


        self.download_directory = os.path.join(
            os.path.expanduser("~"), "Downloaded_AI_Music"
        )
        self.ensure_download_directory_exists(self.download_directory)


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
            messagebox.showerror(
                "Directory Error", f"Could not create download directory: {e}"
            )

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


    async def _perform_search(self, query: str) -> None:
        search_command = build_yt_dlp_search_command(query)
        try:

                return

            try:
                video_info = json.loads(lines[0])


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

        webpage_url = video_info.get("webpage_url")
        title = video_info.get("title", "Unknown Title")
        uploader = video_info.get("uploader", "Unknown Artist")

        if not webpage_url:


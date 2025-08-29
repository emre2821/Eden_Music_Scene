# AI DJ Agent (GUI)

This is a single-file Python application that acts as a simple AI DJ agent with a graphical user interface. It allows you to search for music by title and artist, displays the most relevant search result from YouTube (via `yt-dlp`), and gives you the option to download the audio as an MP3.

## Features

* Search for songs using a query (e.g., "Bohemian Rhapsody Queen").
* Displays the title, artist, and source URL of the found track.
* Prompts for user permission before downloading.
* Downloads the audio as a high-quality MP3 file.
* Uses `tkinter` for a simple graphical interface.
* Handles searches and downloads concurrently using `asyncio`.
* Displays progress for multiple downloads at once.

## Prerequisites

Before running this application, you need to have the following installed on your system:

1.  **Python 3**: This application is written in Python 3.
    * [Download Python](https://www.python.org/downloads/)

2.  **`yt-dlp`**: A command-line program to download videos and audio from many websites.
    * **Installation (using pip):**
        ```bash
        pip install yt-dlp
        ```
    * **Or, follow official instructions:** [https://github.com/yt-dlp/yt-dlp#installation](https://github.com/yt-dlp/yt-dlp#installation)

3.  **`ffmpeg`**: A complete, cross-platform solution to record, convert and stream audio and video. `yt-dlp` uses `ffmpeg` for audio conversion to MP3.
    * **Linux (Debian/Ubuntu):**
        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```
    * **macOS (using Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    * **Windows:**
        1.  Download the `ffmpeg` binaries from their official website: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
        2.  Extract the downloaded archive.
        3.  Add the path to the `bin` folder (e.g., `C:\path\to\ffmpeg\bin`) to your system's Environment Variables (PATH). A quick search for "edit environment variables" in Windows will help.

## How to Run

1.  **Save the file:** Save the provided Python code as `ai_dj_gui.py` in a directory of your choice.
2.  **Open your terminal or command prompt.**
3.  **Navigate to the directory** where you saved `ai_dj_gui.py`.
    ```bash
    cd /path/to/your/directory
    ```
4.  **Run the script:**
    ```bash
    python ai_dj_gui.py
    ```

## Usage

1.  Enter your desired song query (e.g., "hotel california eagles") into the text field.
2.  Click the "Search & Recommend" button (or press Enter in the query field).
3.  The application will display the most relevant search result.
4.  Review the result. If it's the correct song, click the "Download Selected" button.
5.  A confirmation dialog will appear. Click "Yes" to proceed with the download.
6.  The downloaded MP3 file will be saved in a `Downloaded_AI_Music` folder in your user's home directory (e.g., `C:\Users\YourUser\Downloaded_AI_Music` on Windows, or `/home/YourUser/Downloaded_AI_Music` on Linux).

## Notes

* Filenames are basic-sanitized to avoid common issues with illegal characters in file paths.
* This version focuses on core search and download. Future enhancements could include integration with music libraries (Navidrome/Jellyfin APIs) and a more advanced recommendation engine.
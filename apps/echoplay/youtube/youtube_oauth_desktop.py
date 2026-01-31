"""Desktop OAuth flow for YouTube with helpful environment checks."""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - optional dependency
    pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_FILE = Path(__file__).with_name("youtube_token.json")


def _get_client_secret_file() -> str:
    """Return path to client secret file or raise an EnvironmentError."""

    try:
        return os.environ["YOUTUBE_CLIENT_SECRET_FILE"]
    except KeyError as exc:  # pragma: no cover - simple env lookup
        raise EnvironmentError("YOUTUBE_CLIENT_SECRET_FILE not set") from exc


try:
    CLIENT_SECRET_FILE = _get_client_secret_file()
except EnvironmentError:
    message = (
        "❌ Missing YOUTUBE_CLIENT_SECRET_FILE.\n"
        "Set the environment variable or add it to your .env file before running this script."
    )
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing YouTube Client Secret", message)
        root.destroy()
    except Exception:
        print(message)
    sys.exit(1)


# 🔐 Scopes: grant permissions to manage your YouTube account
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def get_credentials() -> Credentials:
    """Load existing credentials or perform OAuth flow, refreshing tokens when needed."""

    creds: Credentials | None = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8090)

        with TOKEN_FILE.open("w") as token_file:
            token_file.write(creds.to_json())

    return creds


def main() -> None:
    """Authenticate and print the user's channel name."""

    credentials = get_credentials()
    youtube = build("youtube", "v3", credentials=credentials)
    response = youtube.channels().list(part="snippet", mine=True).execute()
    channel_name = response["items"][0]["snippet"]["title"]
    print(f"\n✅ OAuth Success! You are logged in as: {channel_name}")


if __name__ == "__main__":  # pragma: no cover - manual execution entrypoint
    main()

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


# ✅ Path to your client_secret file supplied via env var
CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE")
TOKEN_FILE = "youtube_token.json"

if not CLIENT_SECRET_FILE:
    raise RuntimeError(
        "Missing YOUTUBE_CLIENT_SECRET_FILE environment variable.\n"
        "Set it to the full path of your OAuth client secret JSON file."
    )

if not os.path.exists(CLIENT_SECRET_FILE):
    raise FileNotFoundError(
        f"Could not find client secret file at {CLIENT_SECRET_FILE}. "
        "Check the path or update YOUTUBE_CLIENT_SECRET_FILE."
    )

# 🔐 Scopes: grant permissions to manage your YouTube account
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]


def get_credentials() -> Credentials:
    """Load existing credentials or perform OAuth flow, refreshing tokens when needed."""
    creds: Credentials | None = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8090)

        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds


credentials = get_credentials()

# 🎬 Connect to YouTube API
youtube = build('youtube', 'v3', credentials=credentials)

# ✅ Test auth by printing your channel name
response = youtube.channels().list(part='snippet', mine=True).execute()
channel_name = response['items'][0]['snippet']['title']
print(f"\n✅ OAuth Success! You are logged in as: {channel_name}")

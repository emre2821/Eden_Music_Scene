import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError as e:
    print(f"Warning: python-dotenv not installed: {e}. Environment variables must be set manually.")
except Exception as e:
    print(f"Warning: Failed to load .env file: {e}")

# ✅ Path to your client_secret file via environment variable
CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE")
if not CLIENT_SECRET_FILE:
    raise EnvironmentError("YOUTUBE_CLIENT_SECRET_FILE environment variable not set.")

# 🔐 Scopes: grant permissions to manage your YouTube account
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]

# 🚪 Start OAuth 2.0 Flow (opens browser for login)
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
credentials = flow.run_local_server(port=8090)

# 💾 Save token to reuse later (so you don’t have to log in every time)
with open('youtube_token.json', 'w') as token_file:
    token_file.write(credentials.to_json())

# 🎬 Connect to YouTube API
youtube = build('youtube', 'v3', credentials=credentials)

# ✅ Test auth by printing your channel name
response = youtube.channels().list(part='snippet', mine=True).execute()
channel_name = response['items'][0]['snippet']['title']
print(f"\n✅ OAuth Success! You are logged in as: {channel_name}")


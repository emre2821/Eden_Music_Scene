import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ✅ Pull client secret file path from environment
CLIENT_SECRET_FILE = os.environ.get("ECHO_PLAY_CLIENT_SECRET_FILE")
if not CLIENT_SECRET_FILE:
    raise RuntimeError(
        "Set the ECHO_PLAY_CLIENT_SECRET_FILE environment variable to your OAuth client secret JSON"
    )

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


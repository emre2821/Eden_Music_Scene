import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ✅ Full raw string path to your client_secret file
CLIENT_SECRET_FILE = r'C:\Users\emmar\Desktop\Eden_Music\EchoPlay\secrets\client_secret_7610264765-0he942nuoiul0orkohed5bf774j5m3mr.apps.googleusercontent.com.json'  # <-- update this if needed

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

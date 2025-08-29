# OAuth Token Lifecycle

This guide explains how YouTube OAuth tokens are handled in EchoPlay and how to revoke them when needed.

## Environment Setup
- Set the environment variable `YOUTUBE_CLIENT_SECRET_FILE` to the full path of your Google client secret JSON file.
- Tokens are stored locally in `youtube_token.json` in this directory.

## Lifecycle
1. **First Run** – If no `youtube_token.json` exists, a browser window opens for Google login. The resulting token is saved for reuse.
2. **Refresh** – Each run checks the saved token. If it is expired but has a refresh token, the script refreshes it automatically and writes the updated credentials back to `youtube_token.json`.
3. **Failure** – If the token cannot be refreshed (for example, it was revoked), the browser-based OAuth flow runs again.

## Revocation
- **Local** – Delete `youtube_token.json` to force a new login on the next run.
- **Google Account** – Visit [Google Security Settings](https://myaccount.google.com/permissions) and remove the app’s access, or call:
  ```bash
  curl -d -X POST \
    "https://oauth2.googleapis.com/revoke?token=YOUR_REFRESH_TOKEN"
  ```
  Replace `YOUR_REFRESH_TOKEN` with the value from `youtube_token.json`.

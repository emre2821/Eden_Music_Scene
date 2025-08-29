# EdenOS EchoShare

Playlist sharing scripts for the Eden ecosystem.

## Dependencies

- Python 3.10+

## Installation & Usage

1. Install Python 3 (see root README for platform-specific instructions).
2. Navigate into the module:
   ```bash
   cd EdenOS_EchoShare
   ```
3. Run the build script:
   ```bash
   python edenos_echoshare.complete_mobile_build.py
   ```
   The script writes `.txt`, `.json`, and `.chaoslink` playlist files to the path defined at the top of the file (`EDEN_PATH`).

### Example

After running the script, check the configured `EDEN_PATH` (default `/sdcard/EdenOS_Mobile/5_deployments/projects/EdenOS_EchoShare`) for the generated playlist files. Edit the `SONGS` list in the script to customize your playlist.

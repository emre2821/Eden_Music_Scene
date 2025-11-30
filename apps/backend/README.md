# Backend Services

This directory contains the Python-based backend services and tools for the Eden Music Scene.

## Structure

- **EchoDJ/** - DJ/curation agent with tkinter GUI
- **EchoPlay/** - Playback client with pygame backend
- **EdenOS_EchoShare/** - Shared libraries for agents and services
- **music_files/** - Seed metadata, playlists, and catalog scripts

## Core Services

- `emotion_service.py` - REST API for emotion tags
- `emotion_storage.py` - In-memory storage for tags
- `emotion_tags_client.py` - Client library for tag API
- `emotion_tag_schema.json` - Canonical schema for tag fields

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the emotion service
python emotion_service.py
```

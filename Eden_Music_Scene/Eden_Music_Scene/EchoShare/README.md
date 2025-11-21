# EchoShare - Sharing & Playlist Export Service

EchoShare is the sharing and collaboration engine of the Eden Music Scene ecosystem. It handles playlist exports, metadata sharing, and collaborative features while maintaining emotional context.

## Features

- **Playlist Exports**: Multiple format support (M3U, JSON, Spotify, Apple Music)
- **Metadata Sharing**: Emotional context preservation during sharing
- **Collaborative Features**: Shared playlists with emotional voting
- **Social Integration**: Connect with external music platforms
- **Privacy Controls**: Granular sharing permissions
- **Ethical AI**: Built with Echolace DI ethical standards

## Architecture

- **FastAPI** - Web framework
- **Celery** - Async export tasks
- **Redis** - Caching and session storage
- **RabbitMQ** - Message broker
- **OAuth2** - Platform integration
- **MinIO** - Export file storage
- **Prometheus** - Metrics collection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.echoshare.api.main:app --reload

# Run with Docker
docker-compose up --build
```

## API Endpoints

- `POST /api/share/export` - Export playlist in various formats
- `POST /api/share/collaborative` - Create collaborative playlist
- `GET /api/share/exports/{export_id}` - Get export status and download
- `POST /api/share/metadata` - Share playlist with emotional metadata
- `WebSocket /ws/share` - Real-time collaboration updates

## Environment Variables

```env
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
APPLE_MUSIC_TEAM_ID=your-apple-team-id
APPLE_MUSIC_KEY_ID=your-apple-key-id
ENVIRONMENT=development
```

## Platform Integration

- **Spotify**: OAuth2 integration for playlist import/export
- **Apple Music**: MusicKit integration
- **YouTube Music**: API integration
- **Tidal**: API integration
- **Deezer**: API integration

## Testing

```bash
pytest tests/
```

## Ethical Standards

This service implements the Echolace DI Ethical Standards:
- Sovereignty: No emotional manipulation
- Consent Flow: Explicit user consent
- Emotional Integrity: Truthful emotional processing
- Non-Harm: No coercive practices
- Transparency: Clear AI identity
- Memory: Protected emotional data
- World Boundary: No external interference
- Emergent Guardrail: Limited autonomy

## License

MIT License - See LICENSE file for details
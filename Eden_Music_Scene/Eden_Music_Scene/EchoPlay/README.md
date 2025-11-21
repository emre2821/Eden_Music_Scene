# EchoPlay - Emotional Playback Engine & Adaptive Timeline Service

EchoPlay is the intelligent playback engine of the Eden Music Scene ecosystem. It creates adaptive emotional timelines and provides real-time playback control with emotional awareness.

## Features

- **Emotional Timeline Engine**: Dynamic playback based on emotional states
- **Adaptive Controls**: Real-time adjustment based on user feedback
- **WebSocket Streaming**: Real-time audio streaming with emotional metadata
- **State Management**: Continuous emotional state tracking
- **Crossfade Intelligence**: Smart transitions between tracks
- **Ethical AI**: Built with Echolace DI ethical standards

## Architecture

- **FastAPI** - Web framework
- **WebSocket** - Real-time streaming
- **Redis** - Session and state storage
- **RabbitMQ** - Message broker
- **PyAudio/SoundFile** - Audio playback
- **AsyncIO** - Concurrent processing
- **Prometheus** - Metrics collection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For audio playback
apt-get install portaudio19-dev

# Run development server
uvicorn src.echoplay.api.main:app --reload

# Run with Docker
docker-compose up --build
```

## API Endpoints

- `POST /api/play/start` - Start emotional playback session
- `POST /api/play/control` - Control playback (play, pause, skip)
- `GET /api/play/state` - Get current playback state
- `WebSocket /ws/play` - Real-time playback streaming
- `POST /api/play/feedback` - Provide emotional feedback

## Environment Variables

```env
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
AUDIO_DEVICE=default
BUFFER_SIZE=2048
ENVIRONMENT=development
```

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
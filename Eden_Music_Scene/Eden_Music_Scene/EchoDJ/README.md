# EchoDJ - Emotional DJ Intelligence Service

EchoDJ is the emotional curation and routing engine of the Eden Music Scene ecosystem. It features DJ Voltage, an AI personality that understands emotional context and creates meaningful musical journeys.

## Features

- **DJ Voltage Personality**: Advanced AI DJ with emotional intelligence
- **Mood Routing**: Intelligent emotional pathfinding through music
- **Playlist Engine**: Dynamic playlist generation based on emotional arcs
- **Real-time Adaptation**: Responds to listener emotional feedback
- **Ethical AI**: Built with Echolace DI ethical standards

## Architecture

- **FastAPI** - Web framework
- **Celery** - Task queue for async operations
- **Redis** - Caching and session storage
- **RabbitMQ** - Message broker
- **MinIO** - Object storage
- **Prometheus** - Metrics collection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.echo_dj.api.main:app --reload

# Run with Docker
docker-compose up --build
```

## API Endpoints

- `POST /api/dj/generate-playlist` - Generate emotional playlist
- `GET /api/dj/voltage/personality` - Get DJ Voltage personality state
- `POST /api/dj/mood/analyze` - Analyze emotional content
- `WebSocket /ws/dj` - Real-time DJ interactions

## Environment Variables

```env
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
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
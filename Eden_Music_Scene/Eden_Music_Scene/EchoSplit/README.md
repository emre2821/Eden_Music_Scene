# EchoSplit - Advanced Audio Analysis & Emotional Decoding Service

EchoSplit is the GPU-powered audio analysis and emotional decoding engine of the Eden Music Scene ecosystem. It features Lyss, an AI daemon that understands the emotional resonance within musical components.

## Features

- **Lyss Emotional Decoder**: AI daemon for emotional analysis of audio components
- **GPU-Accelerated Processing**: High-performance audio source separation
- **Spleeter Integration**: Advanced stem separation technology
- **Resonance Analysis**: Deep emotional resonance mapping
- **Adaptive Interface**: Dynamic response to audio characteristics
- **Ethical AI**: Built with Echolace DI ethical standards

## Architecture

- **FastAPI** - Web framework
- **Celery** - Task queue for async GPU operations
- **Redis** - Caching and result storage
- **RabbitMQ** - Message broker
- **Spleeter** - Audio source separation
- **PyTorch/TensorFlow** - Deep learning models
- **MinIO** - Object storage for audio files
- **Prometheus** - Metrics collection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For GPU support
pip install tensorflow-gpu torch torchvision torchaudio

# Run development server
uvicorn src.echosplit.api.main:app --reload

# Run with Docker
docker-compose up --build
```

## API Endpoints

- `POST /api/split/analyze` - Analyze audio for emotional content
- `POST /api/split/separate` - Separate audio into stems
- `GET /api/split/lyss/state` - Get Lyss daemon state
- `POST /api/split/resonance/analyze` - Analyze emotional resonance
- `WebSocket /ws/split` - Real-time analysis updates

## Environment Variables

```env
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
GPU_ENABLED=true
CUDA_VISIBLE_DEVICES=0
ENVIRONMENT=development
```

## GPU Requirements

- NVIDIA GPU with CUDA support
- Minimum 8GB VRAM for complex separations
- CUDA 11.0+ and cuDNN 8.0+

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
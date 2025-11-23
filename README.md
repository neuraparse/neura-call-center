# 🤖 Neura Call Center

Modern, platform-agnostic AI-powered call center solution built with cutting-edge technologies.

## ✨ Features

- 🌍 **Multi-Cloud & On-Premise** - Deploy anywhere (AWS, GCP, Azure, or your own servers)
- 🔌 **Provider Agnostic** - Switch between providers without code changes
- 🚀 **Modern Stack** - FastAPI, LangGraph, PostgreSQL, Valkey
- 💰 **Cost Optimized** - ~70% cheaper than Azure-only solutions
- 🎯 **Production Ready** - Monitoring, observability, and scalability built-in
- 🔒 **Secure** - Enterprise-grade security and compliance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEPHONY LAYER                          │
│  Twilio / Vonage / Bandwidth / Telnyx (Configurable)       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   API GATEWAY (FastAPI)                      │
│  - WebSocket (real-time audio streaming)                    │
│  - REST API (call management, webhooks)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
│ STT Service  │ │ LLM     │ │ TTS Service │
│ (Multi)      │ │ Agent   │ │ (Multi)     │
└───────┬──────┘ └──┬──────┘ └──┬──────────┘
        │           │            │
        └───────────┼────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼──────┐ ┌─▼────────┐ ┌▼──────────┐
│ PostgreSQL   │ │ Valkey   │ │ RabbitMQ  │
│ + pgvector   │ │ (Cache)  │ │ (Queue)   │
└──────────────┘ └──────────┘ └───────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/bayrameker/neura-call-center.git
cd neura-call-center

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 3. Development Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start development server
uvicorn apps.api.main:app --reload --port 8080
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Configuration Guide](docs/configuration.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Provider Setup](docs/providers.md)

## 🔧 Configuration

All configuration is done via environment variables. See [.env.example](.env.example) for all options.

### Supported Providers

| Service | Providers |
|---------|-----------|
| **STT** | Deepgram, Whisper (local), AssemblyAI, Azure Speech |
| **TTS** | ElevenLabs, OpenAI, Azure TTS, Coqui (local) |
| **LLM** | OpenAI, Anthropic, Azure OpenAI, Ollama (local) |
| **Telephony** | Twilio, Vonage, Bandwidth, Telnyx |
| **Vector DB** | pgvector, Qdrant, Weaviate |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test
pytest tests/test_stt.py -v
```

## 📊 Monitoring

- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **LLM Observability**: Langfuse
- **Error Tracking**: Sentry

## 💰 Cost Comparison

| Service | Azure Only | Neura (Optimized) | Savings |
|---------|-----------|-------------------|---------|
| Monthly (1000 calls) | $720 | $215 | 70% |

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by [Microsoft Call Center AI](https://github.com/microsoft/call-center-ai) but built for the modern, multi-cloud era.


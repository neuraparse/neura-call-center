# 🤖 Neura Call Center

Modern, platform-agnostic AI-powered call center solution built with cutting-edge technologies. A complete rewrite of Microsoft's call-center-ai project with multi-cloud support and provider flexibility.

## ✨ Features

- 🌍 **Multi-Cloud & On-Premise** - Deploy anywhere (AWS, GCP, Azure, or your own servers)
- 🔌 **Provider Agnostic** - Switch between providers without code changes
- 🚀 **Modern Stack** - FastAPI, LangGraph, PostgreSQL 17, Valkey, RabbitMQ
- 💰 **Cost Optimized** - ~70% cheaper than Azure-only solutions
- 🎯 **Production Ready** - Monitoring, observability, and scalability built-in
- 🔒 **Secure** - Enterprise-grade security with rate limiting and API key management
- 🔄 **Real-time Streaming** - WebSocket support for live audio streaming
- 🧪 **Well Tested** - Comprehensive test suite with pytest

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
- PostgreSQL 17+ with pgvector extension (or use Docker)
- API Keys (OpenAI, Deepgram, ElevenLabs, Twilio)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/neuraparse/neura-call-center.git
cd neura-call-center

# Run the setup script (recommended)
bash scripts/setup.sh

# OR manually:
# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Start with Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL, Valkey, RabbitMQ, API, Prometheus, Grafana, Tempo)
docker-compose up -d

# Check logs
docker-compose logs -f api

# Access services:
# - API: http://localhost:8080
# - API Docs: http://localhost:8080/docs
# - Grafana: http://localhost:3002 (admin/admin)
# - Prometheus: http://localhost:9090
# - RabbitMQ Management: http://localhost:15672 (admin/admin)
```

### 3. Development Setup (Local)

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Start only database services
docker-compose up -d postgres valkey rabbitmq

# Run database migrations
alembic upgrade head

# Start development server
uvicorn apps.api.main:app --reload --port 8080

# Or use Makefile
make dev      # Install dev dependencies
make migrate  # Run migrations
make run      # Start server
```

## 📚 Documentation

- [Project Summary](PROJECT_SUMMARY.md) - Complete project overview and status
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [API Documentation](http://localhost:8080/docs) - Interactive OpenAPI docs (when running)

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
pytest --cov=apps --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_health_check -v

# Using Makefile
make test      # Run all tests
make test-cov  # Run with coverage report
```

## 📊 Monitoring & Observability

The project includes a complete observability stack:

- **Metrics**: Prometheus + Grafana (pre-configured dashboards)
- **Distributed Tracing**: Grafana Tempo + OpenTelemetry
- **Logging**: Structured logging with structlog
- **LLM Observability**: Langfuse integration (optional)
- **Error Tracking**: Sentry integration (optional)

Access monitoring dashboards:
- Grafana: http://localhost:3002 (admin/admin)
- Prometheus: http://localhost:9090
- Tempo: http://localhost:3200

## 💰 Cost Comparison

Estimated monthly costs for 1000 calls (~30 hours):

| Component | Azure (Microsoft) | Neura (Optimized) | Savings |
|-----------|------------------|-------------------|---------|
| STT | Azure Speech ($30) | Deepgram ($9) or Whisper (free) | 70-100% |
| TTS | Azure TTS ($16) | ElevenLabs ($11) or OpenAI ($15) | 6-31% |
| LLM | Azure OpenAI ($60) | OpenAI/Anthropic ($60) or Ollama (free) | 0-100% |
| Database | Cosmos DB ($200) | PostgreSQL ($20) | 90% |
| Infrastructure | Azure ($150) | Any cloud ($50) | 67% |
| **Total** | **~$456** | **~$155** | **~66%** |

*Note: Costs vary based on usage, provider selection, and deployment options. Self-hosted options (Whisper, Ollama) can reduce costs to near zero.*

## 🛠️ Development

```bash
# Format code
make format

# Run linting
make lint

# Type checking
mypy apps

# Clean up
make clean

# Database shell
make db-shell

# Create new migration
make migrate-create
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Docker Compose (production)
- Kubernetes
- AWS, GCP, Azure
- On-premise servers

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by [Microsoft Call Center AI](https://github.com/microsoft/call-center-ai) but built for the modern, multi-cloud era with provider flexibility and cost optimization.

## 📞 Support

- 📧 Email: support@neuraparse.com
- 🐛 Issues: [GitHub Issues](https://github.com/neuraparse/neura-call-center/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/neuraparse/neura-call-center/discussions)


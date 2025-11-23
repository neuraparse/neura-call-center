# Neura Call Center

**Enterprise-grade AI-powered call center platform with multi-cloud support and provider flexibility.**

Neura Call Center is a modern, production-ready solution for building intelligent voice applications. Built as a complete rewrite of Microsoft's call-center-ai project, it eliminates vendor lock-in by supporting multiple cloud providers and on-premise deployments while reducing operational costs by up to 70%.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## Table of Contents

- [Why Neura Call Center?](#why-neura-call-center)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Cost Analysis](#cost-analysis)
- [Contributing](#contributing)
- [License](#license)

---

## Why Neura Call Center?

### The Problem

Traditional call center solutions suffer from:
- **Vendor Lock-in**: Tied to a single cloud provider (Azure, AWS, etc.)
- **High Costs**: Expensive proprietary services and licensing
- **Limited Flexibility**: Difficult to switch between AI/telephony providers
- **Complex Integration**: Fragmented tools and services

### The Solution

Neura Call Center provides:
- **Provider Agnostic Architecture**: Switch between STT, TTS, LLM, and telephony providers via configuration
- **Multi-Cloud Support**: Deploy on AWS, GCP, Azure, or your own infrastructure
- **Cost Optimization**: 66-70% cost reduction compared to Azure-only solutions
- **Modern Technology Stack**: Built with FastAPI, LangGraph, PostgreSQL 17, and industry-standard tools
- **Production Ready**: Complete observability, monitoring, and security features out of the box

---

## Key Features

### Core Capabilities

**Multi-Provider Support**
- Seamlessly switch between AI service providers without code changes
- Automatic fallback mechanisms for high availability
- Support for self-hosted alternatives (Whisper, Ollama, Coqui)

**Real-Time Communication**
- WebSocket-based audio streaming for low-latency interactions
- Bidirectional streaming for STT and TTS
- Twilio Media Streams integration for telephony

**Intelligent Conversation Management**
- LangGraph-powered conversational AI agents
- Context-aware dialogue management
- Tool calling for CRM and database operations
- Multi-language support (English, Turkish, French, German, Spanish)

**Enterprise Security**
- API key authentication and management
- Rate limiting and DDoS protection
- CORS configuration
- Secure credential management

**Production-Grade Infrastructure**
- PostgreSQL 17 with pgvector for vector embeddings
- Valkey (Redis fork) for high-performance caching
- RabbitMQ for reliable message queuing
- Alembic for database migrations
- Docker Compose for easy deployment

**Comprehensive Observability**
- Prometheus metrics collection
- Grafana dashboards for visualization
- Distributed tracing with Grafana Tempo and OpenTelemetry
- Structured logging with structlog
- Optional Sentry integration for error tracking
- Optional Langfuse integration for LLM observability

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TELEPHONY LAYER                              │
│  Twilio / Vonage / Bandwidth / Telnyx (Provider Agnostic)          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ SIP/WebRTC/Media Streams
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                           │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │   WebSocket    │  │  REST API    │  │   Webhook Handlers     │  │
│  │ Audio Streaming│  │ Management   │  │  Twilio/Vonage/etc     │  │
│  └────────────────┘  └──────────────┘  └────────────────────────┘  │
│                                                                      │
│  Middleware: Auth | Rate Limiting | CORS | Security                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
┌───────────────▼────┐  ┌──────▼──────┐  ┌───▼──────────────┐
│   STT Providers    │  │  LLM Agent  │  │  TTS Providers   │
│                    │  │             │  │                  │
│ • Deepgram         │  │ LangGraph   │  │ • ElevenLabs     │
│ • Whisper (local)  │  │ + LangChain │  │ • OpenAI TTS     │
│ • AssemblyAI       │  │             │  │ • Azure TTS      │
│ • Azure Speech     │  │ Tool Calls  │  │ • Coqui (local)  │
│                    │  │             │  │                  │
│ Factory + Fallback │  │ Streaming   │  │ Factory + Cache  │
└───────────────┬────┘  └──────┬──────┘  └───┬──────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
┌───────────────▼────┐  ┌──────▼──────┐  ┌───▼──────────────┐
│   PostgreSQL 17    │  │   Valkey    │  │    RabbitMQ      │
│                    │  │             │  │                  │
│ • Call Records     │  │ • Sessions  │  │ • Async Tasks    │
│ • Conversations    │  │ • Cache     │  │ • Event Queue    │
│ • Messages         │  │ • Rate Limit│  │ • Webhooks       │
│ • Claims/Tickets   │  │             │  │                  │
│ • pgvector (RAG)   │  │ Redis Proto │  │ AMQP Protocol    │
└────────────────────┘  └─────────────┘  └──────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
┌───────────────▼────┐  ┌──────▼──────┐  ┌───▼──────────────┐
│    Prometheus      │  │   Grafana   │  │  Grafana Tempo   │
│                    │  │             │  │                  │
│ Metrics Collection │  │ Dashboards  │  │ Distributed      │
│ Time Series DB     │  │ Alerts      │  │ Tracing          │
└────────────────────┘  └─────────────┘  └──────────────────┘
```

### Request Flow

1. **Incoming Call**: Telephony provider (Twilio) receives call and sends webhook to API
2. **WebSocket Connection**: API establishes WebSocket connection for audio streaming
3. **Audio Processing**:
   - Audio chunks sent to STT provider (Deepgram/Whisper)
   - Transcribed text sent to LLM agent (LangGraph)
   - Agent generates response using context and tools
   - Response sent to TTS provider (ElevenLabs/OpenAI)
   - Audio chunks streamed back to caller
4. **Data Persistence**: Call metadata, conversation history, and analytics stored in PostgreSQL
5. **Observability**: Metrics, traces, and logs collected throughout the pipeline

### Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **API Gateway** | HTTP/WebSocket endpoints, routing, middleware | FastAPI, Uvicorn |
| **STT Service** | Speech-to-text transcription with streaming | Deepgram, Whisper, AssemblyAI |
| **LLM Agent** | Conversational AI, context management, tool calling | LangGraph, LangChain, OpenAI/Anthropic |
| **TTS Service** | Text-to-speech synthesis with streaming | ElevenLabs, OpenAI, Azure |
| **Database** | Persistent storage, vector search | PostgreSQL 17 + pgvector |
| **Cache** | Session management, rate limiting | Valkey (Redis) |
| **Message Queue** | Async task processing, event handling | RabbitMQ |
| **Monitoring** | Metrics, tracing, logging | Prometheus, Grafana, Tempo, OpenTelemetry |

---

## Technology Stack

### Backend & API
- **FastAPI** (0.115+) - Modern async web framework
- **Uvicorn** - ASGI server with WebSocket support
- **Pydantic** (2.9+) - Data validation and settings management
- **Python** 3.11+ - Type hints, async/await

### AI & Machine Learning
- **LangGraph** (0.2+) - Stateful agent orchestration
- **LangChain** (0.3+) - LLM application framework
- **OpenAI** - GPT-4o, GPT-4-turbo, Whisper, TTS
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus
- **Deepgram** - Real-time speech recognition
- **ElevenLabs** - High-quality voice synthesis

### Data & Storage
- **PostgreSQL 17** - Primary database with JSONB support
- **pgvector** - Vector similarity search for RAG
- **Valkey** (6.0+) - Redis-compatible cache (Redis fork)
- **RabbitMQ** (3.13+) - Message broker
- **Alembic** - Database migration tool
- **SQLAlchemy** (2.0+) - Async ORM

### Telephony
- **Twilio** - Voice, SMS, Media Streams
- **Vonage** (planned) - Voice API
- **Bandwidth** (planned) - Voice API
- **Telnyx** (planned) - Voice API

### Monitoring & Observability
- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards
- **Grafana Tempo** - Distributed tracing backend
- **OpenTelemetry** - Instrumentation framework
- **structlog** - Structured logging
- **Sentry** (optional) - Error tracking
- **Langfuse** (optional) - LLM observability

### Development & Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage
- **httpx** - Async HTTP client for testing
- **Faker** - Test data generation
- **Ruff** - Fast Python linter and formatter
- **mypy** - Static type checker
- **pre-commit** - Git hooks

### DevOps & Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Kubernetes** (planned) - Container orchestration
- **Terraform** (planned) - Infrastructure as code

---

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**
- **Docker** (20.10+) and **Docker Compose** (v2.0+)
- **Git**

You'll also need API keys from the following providers (at minimum):
- **OpenAI** - For LLM (GPT-4o) - [Get API Key](https://platform.openai.com/api-keys)
- **Deepgram** - For STT - [Get API Key](https://console.deepgram.com/)
- **ElevenLabs** - For TTS - [Get API Key](https://elevenlabs.io/)
- **Twilio** - For telephony - [Get Credentials](https://www.twilio.com/console)

### Option 1: Automated Setup (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/neuraparse/neura-call-center.git
cd neura-call-center

# Run the automated setup script
bash scripts/setup.sh
```

The script will:
1. Check for Docker and Docker Compose
2. Create `.env` file from template
3. Start all services (PostgreSQL, Valkey, RabbitMQ, API, monitoring stack)
4. Run database migrations
5. Display service URLs and credentials

**Important**: Edit `.env` file and add your API keys before the services start.

### Option 2: Manual Setup

If you prefer manual control:

```bash
# Clone the repository
git clone https://github.com/neuraparse/neura-call-center.git
cd neura-call-center

# Create environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Required environment variables:
```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o

# Speech-to-Text
DEEPGRAM_API_KEY=...
STT_PRIMARY_PROVIDER=deepgram

# Text-to-Speech
ELEVENLABS_API_KEY=...
TTS_PRIMARY_PROVIDER=elevenlabs

# Telephony
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
```

Start all services:
```bash
# Start all services in detached mode
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Run database migrations
docker-compose exec api alembic upgrade head

# Check API logs
docker-compose logs -f api
```

### Option 3: Local Development Setup

For active development without Docker for the API:

```bash
# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with development tools
pip install -e ".[dev]"

# Start only infrastructure services
docker-compose up -d postgres valkey rabbitmq

# Run database migrations
alembic upgrade head

# Start development server with hot reload
uvicorn apps.api.main:app --reload --port 8080 --log-level debug

# Or use Makefile shortcuts
make dev      # Install dev dependencies
make migrate  # Run migrations
make run      # Start server
```

### Verify Installation

Once services are running, verify the installation:

```bash
# Check API health
curl http://localhost:8080/health

# Expected response:
# {"status":"healthy","version":"0.1.0","timestamp":"..."}

# Access interactive API documentation
open http://localhost:8080/docs
```

### Access Services

After successful setup, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8080 | - |
| **API Documentation** | http://localhost:8080/docs | - |
| **Grafana** | http://localhost:3002 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **RabbitMQ Management** | http://localhost:15672 | admin / admin |
| **Tempo** | http://localhost:3200 | - |

### Next Steps

1. **Test the API**: Use the interactive docs at `/docs` to test endpoints
2. **Configure Providers**: Customize provider settings in `.env`
3. **Set up Webhooks**: Configure Twilio webhooks to point to your API
4. **Explore Examples**: Check the `examples/` directory for usage examples
5. **Read Documentation**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for detailed information

---

## Configuration

Neura Call Center is designed to be highly configurable through environment variables. All configuration is centralized in the `.env` file.

### Configuration Files

- **`.env.example`** - Template with all available options and documentation
- **`.env`** - Your local configuration (created from `.env.example`, not committed to git)
- **`apps/core/config.py`** - Configuration schema and validation using Pydantic

### Core Configuration Sections

#### Application Settings
```bash
APP_NAME=neura-call-center
APP_ENV=development  # development, staging, production
APP_DEBUG=true
APP_LOG_LEVEL=INFO   # DEBUG, INFO, WARNING, ERROR, CRITICAL
APP_HOST=0.0.0.0
APP_PORT=8080
```

#### Database Configuration
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/neura_call_center
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_ECHO=false  # Set to true for SQL query logging
```

#### Cache Configuration (Valkey/Redis)
```bash
CACHE_URL=redis://localhost:6379/0
CACHE_TTL=3600
CACHE_ENABLED=true
```

#### LLM Provider Configuration
```bash
# Primary provider: openai, anthropic, azure-openai, ollama
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_STREAMING=true

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=  # Optional

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Azure OpenAI (optional)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

#### Speech-to-Text (STT) Configuration
```bash
# Primary provider: deepgram, whisper, assemblyai, azure
STT_PRIMARY_PROVIDER=deepgram
STT_FALLBACK_PROVIDERS=["whisper"]

# Deepgram
DEEPGRAM_API_KEY=...

# Whisper (local/self-hosted)
WHISPER_MODEL=base  # tiny, base, small, medium, large
WHISPER_DEVICE=cpu  # cpu, cuda

# AssemblyAI
ASSEMBLYAI_API_KEY=...

# Azure Speech
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=eastus
```

#### Text-to-Speech (TTS) Configuration
```bash
# Primary provider: elevenlabs, openai, azure
TTS_PRIMARY_PROVIDER=elevenlabs
TTS_FALLBACK_PROVIDERS=["openai"]

# ElevenLabs
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel

# OpenAI TTS
OPENAI_TTS_MODEL=tts-1-hd
OPENAI_TTS_VOICE=alloy  # alloy, echo, fable, onyx, nova, shimmer

# Azure TTS
AZURE_TTS_VOICE=en-US-JennyNeural
```

#### Telephony Configuration
```bash
# Primary provider: twilio, vonage, bandwidth, telnyx
TELEPHONY_PROVIDER=twilio

# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://your-domain.com/webhooks/twilio
```

#### Security Configuration
```bash
SECRET_KEY=your-secret-key-change-this-in-production
API_KEY_HEADER=X-API-Key
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
CORS_ENABLED=true
```

#### Monitoring Configuration
```bash
# Sentry (Error Tracking)
SENTRY_DSN=...
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1

# OpenTelemetry (Tracing)
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# Langfuse (LLM Observability)
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Supported Providers

The platform supports multiple providers for each service, allowing you to choose based on your requirements:

#### Speech-to-Text (STT)

| Provider | Type | Latency | Cost | Best For |
|----------|------|---------|------|----------|
| **Deepgram** | Cloud | Very Low | $0.0043/min | Production, real-time |
| **Whisper** | Self-hosted | Medium | Free | Privacy, cost savings |
| **AssemblyAI** | Cloud | Low | $0.00025/sec | Accuracy, features |
| **Azure Speech** | Cloud | Low | $1/hour | Azure ecosystem |

#### Text-to-Speech (TTS)

| Provider | Type | Quality | Cost | Best For |
|----------|------|---------|------|----------|
| **ElevenLabs** | Cloud | Excellent | $0.30/1K chars | Natural voices |
| **OpenAI** | Cloud | Very Good | $15/1M chars | Integration, speed |
| **Azure TTS** | Cloud | Good | $16/1M chars | Azure ecosystem |
| **Coqui** | Self-hosted | Good | Free | Privacy, customization |

#### Large Language Models (LLM)

| Provider | Models | Cost | Best For |
|----------|--------|------|----------|
| **OpenAI** | GPT-4o, GPT-4-turbo | $5-10/1M tokens | General purpose |
| **Anthropic** | Claude 3.5 Sonnet, Opus | $3-15/1M tokens | Complex reasoning |
| **Azure OpenAI** | GPT-4, GPT-3.5 | Similar to OpenAI | Enterprise, compliance |
| **Ollama** | Llama 3, Mistral, etc. | Free | Self-hosted, privacy |

#### Telephony

| Provider | Coverage | Features | Best For |
|----------|----------|----------|----------|
| **Twilio** | Global | Full-featured | Production, reliability |
| **Vonage** | Global | Enterprise | Large scale |
| **Bandwidth** | US/Canada | Cost-effective | North America |
| **Telnyx** | Global | Developer-friendly | Flexibility |

#### Vector Databases

| Provider | Type | Best For |
|----------|------|----------|
| **pgvector** | PostgreSQL extension | Simplicity, existing PostgreSQL |
| **Qdrant** | Dedicated vector DB | High performance, scale |
| **Weaviate** | Dedicated vector DB | Advanced features |

### Provider Switching

Switch providers by simply changing environment variables:

```bash
# Switch from Deepgram to Whisper
STT_PRIMARY_PROVIDER=whisper

# Switch from ElevenLabs to OpenAI
TTS_PRIMARY_PROVIDER=openai

# Switch from OpenAI to Anthropic
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
```

No code changes required! The factory pattern handles provider instantiation automatically.

### Configuration Best Practices

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use different configs per environment** - `.env.development`, `.env.production`
3. **Set fallback providers** - Ensure high availability
4. **Monitor costs** - Different providers have different pricing
5. **Test provider switches** - Verify functionality before production changes
6. **Use secrets management** - For production, use AWS Secrets Manager, Azure Key Vault, etc.

---

## Development

### Development Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes

# 3. Format code
make format

# 4. Run linting
make lint

# 5. Run type checking
mypy apps

# 6. Run tests
make test

# 7. Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### Code Quality Tools

#### Ruff (Linting & Formatting)

Ruff is an extremely fast Python linter and formatter:

```bash
# Check for linting issues
ruff check apps tests

# Auto-fix issues
ruff check --fix apps tests

# Format code
ruff format apps tests

# Or use Makefile
make lint    # Run linting
make format  # Format code
```

Configuration in `pyproject.toml`:
- Line length: 100
- Target: Python 3.11+
- Enabled rules: pycodestyle, pyflakes, isort, flake8-bugbear, comprehensions, pyupgrade

#### MyPy (Type Checking)

Static type checking for Python:

```bash
# Type check the entire codebase
mypy apps

# Type check specific module
mypy apps/api/main.py

# Generate HTML report
mypy apps --html-report ./mypy-report
```

Configuration in `pyproject.toml`:
- Strict mode enabled
- Disallow untyped definitions
- Warn on unused configs

#### Pre-commit Hooks

Set up pre-commit hooks to automatically check code before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Database Migrations

Using Alembic for database schema management:

```bash
# Create a new migration
make migrate-create
# Or manually:
alembic revision --autogenerate -m "Add new column to calls table"

# Apply migrations
make migrate
# Or manually:
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Database Management

```bash
# Access PostgreSQL shell
make db-shell
# Or manually:
docker-compose exec postgres psql -U postgres -d neura_call_center

# Backup database
docker-compose exec postgres pg_dump -U postgres neura_call_center > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres neura_call_center < backup.sql

# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

### Useful Make Commands

```bash
make help          # Show all available commands
make install       # Install production dependencies
make dev           # Install development dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make clean         # Clean up generated files
make docker-up     # Start Docker services
make docker-down   # Stop Docker services
make docker-logs   # View Docker logs
make docker-build  # Build Docker images
make migrate       # Run database migrations
make migrate-create # Create new migration
make db-shell      # Open database shell
make run           # Run development server
make run-prod      # Run production server
```

### Project Structure

```
neura-call-center/
├── apps/                       # Application code
│   ├── api/                   # FastAPI application
│   │   ├── main.py           # Application entry point
│   │   ├── middleware/       # Custom middleware
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── rate_limit.py # Rate limiting
│   │   │   └── security.py   # Security headers
│   │   └── routers/          # API routes
│   │       ├── calls.py      # Call management
│   │       ├── health.py     # Health checks
│   │       ├── streaming.py  # WebSocket streaming
│   │       └── webhooks.py   # Telephony webhooks
│   ├── agents/               # LangGraph agents
│   │   └── call_agent.py    # Main call handling agent
│   ├── core/                 # Core utilities
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database setup
│   │   └── logging.py       # Logging configuration
│   ├── models/               # Database models
│   │   ├── base.py          # Base model class
│   │   ├── call.py          # Call model
│   │   ├── conversation.py  # Conversation & Message
│   │   └── claim.py         # Claim/Ticket model
│   └── providers/            # Provider abstraction
│       ├── stt/             # Speech-to-Text
│       │   ├── base.py      # Base interface
│       │   ├── factory.py   # Provider factory
│       │   ├── deepgram.py  # Deepgram implementation
│       │   └── whisper.py   # Whisper implementation
│       ├── tts/             # Text-to-Speech
│       │   ├── base.py      # Base interface
│       │   ├── factory.py   # Provider factory
│       │   ├── elevenlabs.py # ElevenLabs implementation
│       │   └── openai.py    # OpenAI implementation
│       └── telephony/       # Telephony providers
│           ├── base.py      # Base interface
│           ├── factory.py   # Provider factory
│           └── twilio.py    # Twilio implementation
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── agents/              # Agent tests
│   ├── providers/           # Provider tests
│   ├── test_api.py          # API tests
│   └── test_websocket.py    # WebSocket tests
├── alembic/                  # Database migrations
│   ├── versions/            # Migration files
│   └── env.py              # Alembic configuration
├── infrastructure/           # Infrastructure configs
│   ├── grafana/            # Grafana dashboards
│   ├── prometheus/         # Prometheus config
│   └── tempo/              # Tempo config
├── scripts/                  # Utility scripts
│   ├── setup.sh            # Setup script
│   └── test.sh             # Test script
├── examples/                 # Usage examples
│   ├── agent_example.py    # Agent usage
│   ├── stt_example.py      # STT usage
│   ├── tts_example.py      # TTS usage
│   └── websocket_client.py # WebSocket client
├── docker-compose.yml        # Docker orchestration
├── Dockerfile               # Container image
├── pyproject.toml           # Python project config
├── alembic.ini              # Alembic config
├── Makefile                 # Development commands
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── PROJECT_SUMMARY.md      # Project overview
├── CONTRIBUTING.md         # Contribution guide
└── DEPLOYMENT.md           # Deployment guide
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=apps --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_api.py::TestHealthEndpoints -v

# Run specific test function
pytest tests/test_api.py::test_health_check -v

# Run tests matching a pattern
pytest -k "test_health" -v

# Run tests with specific markers
pytest -m "integration" -v

# Using Makefile
make test      # Run all tests
make test-cov  # Run with coverage report
```

### Test Structure

Tests are organized by component:

```
tests/
├── conftest.py              # Shared fixtures
├── agents/
│   └── test_call_agent.py  # Agent tests
├── providers/
│   ├── test_stt.py         # STT provider tests
│   ├── test_tts.py         # TTS provider tests
│   └── test_telephony.py   # Telephony tests
├── test_api.py             # API endpoint tests
└── test_websocket.py       # WebSocket tests
```

### Writing Tests

Example test structure:

```python
import pytest
from httpx import AsyncClient
from apps.api.main import app

@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_call(db_session):
    """Test call creation."""
    # Test implementation
    pass
```

### Test Coverage

View coverage report:

```bash
# Generate HTML coverage report
pytest --cov=apps --cov-report=html

# Open in browser
open htmlcov/index.html
```

Current coverage targets:
- Overall: >80%
- Core modules: >90%
- Providers: >85%

### Integration Tests

Integration tests require running services:

```bash
# Start test services
docker-compose up -d postgres valkey rabbitmq

# Run integration tests
pytest -m integration

# Stop services
docker-compose down
```

### Mocking External Services

Use pytest-mock for mocking external API calls:

```python
@pytest.mark.asyncio
async def test_deepgram_stt(mocker):
    """Test Deepgram STT with mocked API."""
    mock_response = {"results": {"channels": [{"alternatives": [{"transcript": "Hello"}]}]}}
    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

    # Test implementation
```

---

## Deployment

Neura Call Center can be deployed in various environments. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Deployment Options

#### 1. Docker Compose (Recommended for Small-Medium Scale)

Production-ready Docker Compose setup:

```bash
# Use production environment file
cp .env.example .env.production
nano .env.production  # Configure for production

# Start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose up -d --scale api=3
```

**Pros**: Simple, cost-effective, good for single-server deployments
**Cons**: Limited scalability, single point of failure

#### 2. Kubernetes (Recommended for Large Scale)

Deploy on any Kubernetes cluster (EKS, GKE, AKS, self-hosted):

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/k8s/

# Or use Helm
helm install neura-call-center ./infrastructure/helm/
```

**Pros**: High availability, auto-scaling, cloud-agnostic
**Cons**: More complex setup and management

#### 3. Cloud-Specific Deployments

**AWS**
- ECS/Fargate for containers
- RDS for PostgreSQL
- ElastiCache for Redis
- Application Load Balancer

**Google Cloud Platform**
- Cloud Run for containers
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Load Balancing

**Azure**
- Container Instances or AKS
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Application Gateway

#### 4. On-Premise

Deploy on your own infrastructure:
- Docker Swarm or Kubernetes
- Self-managed PostgreSQL cluster
- Self-managed Redis cluster
- Hardware load balancer or HAProxy

### Production Checklist

Before deploying to production:

- [ ] Change all default passwords and secrets
- [ ] Configure SSL/TLS certificates
- [ ] Set up domain and DNS
- [ ] Configure firewall rules
- [ ] Enable monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure backup strategy
- [ ] Test disaster recovery procedures
- [ ] Set up CI/CD pipeline
- [ ] Configure rate limiting
- [ ] Enable CORS for allowed origins only
- [ ] Set up Sentry for error tracking
- [ ] Configure Twilio webhooks with production URL
- [ ] Test with production API keys
- [ ] Load test the system
- [ ] Document runbooks for common issues

### Environment-Specific Configuration

**Development**
```bash
APP_ENV=development
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
DATABASE_ECHO=true
```

**Staging**
```bash
APP_ENV=staging
APP_DEBUG=false
APP_LOG_LEVEL=INFO
DATABASE_ECHO=false
```

**Production**
```bash
APP_ENV=production
APP_DEBUG=false
APP_LOG_LEVEL=WARNING
DATABASE_ECHO=false
SENTRY_ENABLED=true
OTEL_ENABLED=true
```

### Scaling Considerations

**Horizontal Scaling**
- API: Scale to multiple instances behind load balancer
- Workers: Scale background job processors
- Database: Use read replicas for read-heavy workloads

**Vertical Scaling**
- Increase CPU/memory for compute-intensive tasks
- Optimize database queries and indexes
- Use connection pooling

**Caching Strategy**
- Cache LLM responses for common queries
- Cache TTS audio for repeated phrases
- Use Redis for session management

---

## Monitoring & Observability

### Overview

Neura Call Center includes a comprehensive observability stack for monitoring system health, performance, and debugging issues.

### Metrics (Prometheus + Grafana)

**Prometheus** collects and stores metrics:
- API request rates and latencies
- Database query performance
- Cache hit/miss rates
- Provider API call metrics
- System resource usage (CPU, memory, disk)

**Grafana** visualizes metrics with pre-built dashboards:
- System Overview Dashboard
- API Performance Dashboard
- Database Metrics Dashboard
- Provider Health Dashboard
- Cost Tracking Dashboard

Access Grafana:
```
URL: http://localhost:3002
Username: admin
Password: admin
```

### Distributed Tracing (Grafana Tempo + OpenTelemetry)

**OpenTelemetry** instruments the application:
- Automatic instrumentation for FastAPI, SQLAlchemy, Redis, httpx
- Custom spans for business logic
- Trace context propagation across services

**Grafana Tempo** stores and queries traces:
- End-to-end request tracing
- Service dependency mapping
- Performance bottleneck identification
- Error correlation

Access Tempo:
```
URL: http://localhost:3200
Query via Grafana: Data Sources > Tempo
```

Example trace flow:
```
Incoming Call → API Gateway → STT Provider → LLM Agent → TTS Provider → Response
     100ms         50ms          200ms         500ms        150ms        50ms
```

### Structured Logging (structlog)

All logs are structured JSON for easy parsing and analysis:

```json
{
  "event": "call_started",
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "call_id": "call_123",
  "phone_number": "+1234567890",
  "provider": "twilio"
}
```

Log levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical issues requiring immediate attention

### Error Tracking (Sentry)

Optional Sentry integration for error monitoring:

```bash
# Enable in .env
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

Features:
- Automatic error capture and grouping
- Stack traces with source code context
- Release tracking
- Performance monitoring
- User feedback collection

### LLM Observability (Langfuse)

Optional Langfuse integration for LLM monitoring:

```bash
# Enable in .env
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

Features:
- LLM call tracing and debugging
- Token usage tracking
- Cost analysis
- Prompt versioning
- User feedback collection

### Custom Metrics

Add custom metrics to your code:

```python
from prometheus_client import Counter, Histogram

# Counter for tracking events
call_counter = Counter('calls_total', 'Total number of calls', ['status'])
call_counter.labels(status='completed').inc()

# Histogram for tracking durations
call_duration = Histogram('call_duration_seconds', 'Call duration')
with call_duration.time():
    # Your code here
    pass
```

### Alerting

Set up alerts in Grafana for critical conditions:

- API error rate > 5%
- Database connection pool exhausted
- High latency (p95 > 2s)
- Provider API failures
- Disk space < 10%
- Memory usage > 90%

### Health Checks

Multiple health check endpoints:

```bash
# Basic health check
curl http://localhost:8080/health

# Readiness check (includes dependencies)
curl http://localhost:8080/health/ready

# Liveness check
curl http://localhost:8080/health/live
```

### Log Aggregation

For production, consider centralized logging:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki** (Grafana Loki)
- **CloudWatch Logs** (AWS)
- **Cloud Logging** (GCP)
- **Azure Monitor** (Azure)

### Monitoring Best Practices

1. **Set up alerts** for critical metrics
2. **Monitor costs** across all providers
3. **Track SLAs** (uptime, latency, error rate)
4. **Review dashboards** regularly
5. **Analyze traces** for performance optimization
6. **Monitor provider health** and switch if needed
7. **Set up on-call rotation** for production issues
8. **Document runbooks** for common issues

---

## Cost Analysis

### Monthly Cost Comparison

Based on 1000 calls per month (~30 hours of conversation):

#### Azure-Only Solution (Microsoft Call Center AI)

| Component | Service | Usage | Cost |
|-----------|---------|-------|------|
| **STT** | Azure Speech | 30 hours | $30.00 |
| **TTS** | Azure TTS | ~100K characters | $16.00 |
| **LLM** | Azure OpenAI (GPT-4) | ~3M tokens | $60.00 |
| **Database** | Cosmos DB | 10GB + RU/s | $200.00 |
| **Storage** | Azure Blob Storage | 50GB | $10.00 |
| **Compute** | Azure App Service | Standard tier | $75.00 |
| **Networking** | Azure Load Balancer | Data transfer | $25.00 |
| **Monitoring** | Azure Monitor | Logs + metrics | $40.00 |
| **Total** | | | **$456.00** |

#### Neura Call Center (Optimized Configuration)

| Component | Service | Usage | Cost |
|-----------|---------|-------|------|
| **STT** | Deepgram | 30 hours | $9.00 |
| **TTS** | ElevenLabs | ~100K characters | $11.00 |
| **LLM** | OpenAI (GPT-4o) | ~3M tokens | $45.00 |
| **Database** | PostgreSQL (managed) | 10GB | $20.00 |
| **Cache** | Redis (managed) | 1GB | $10.00 |
| **Compute** | VPS/Cloud VM | 4 vCPU, 8GB RAM | $40.00 |
| **Monitoring** | Self-hosted (Prometheus/Grafana) | - | $0.00 |
| **Queue** | RabbitMQ (self-hosted) | - | $0.00 |
| **Total** | | | **$135.00** |

**Savings: $321/month (70%)**

#### Neura Call Center (Maximum Cost Optimization)

| Component | Service | Usage | Cost |
|-----------|---------|-------|------|
| **STT** | Whisper (self-hosted) | 30 hours | $0.00 |
| **TTS** | OpenAI TTS | ~100K characters | $15.00 |
| **LLM** | Ollama (self-hosted Llama 3) | ~3M tokens | $0.00 |
| **Database** | PostgreSQL (self-hosted) | 10GB | $0.00 |
| **Cache** | Valkey (self-hosted) | 1GB | $0.00 |
| **Compute** | VPS/Dedicated Server | 8 vCPU, 16GB RAM | $80.00 |
| **Monitoring** | Self-hosted | - | $0.00 |
| **Queue** | RabbitMQ (self-hosted) | - | $0.00 |
| **Total** | | | **$95.00** |

**Savings: $361/month (79%)**

### Cost Breakdown by Provider

#### Speech-to-Text (30 hours/month)

| Provider | Cost | Notes |
|----------|------|-------|
| Azure Speech | $30.00 | $1.00/hour |
| Deepgram | $9.00 | $0.30/hour |
| AssemblyAI | $7.50 | $0.25/hour |
| Whisper (self-hosted) | $0.00 | Requires GPU for real-time |

#### Text-to-Speech (100K characters/month)

| Provider | Cost | Notes |
|----------|------|-------|
| Azure TTS | $16.00 | $16/1M characters |
| ElevenLabs | $11.00 | $11/1M characters |
| OpenAI TTS | $15.00 | $15/1M characters |
| Coqui (self-hosted) | $0.00 | Lower quality |

#### Large Language Models (3M tokens/month)

| Provider | Model | Cost | Notes |
|----------|-------|------|-------|
| Azure OpenAI | GPT-4 | $60.00 | $10/1M input, $30/1M output |
| OpenAI | GPT-4o | $45.00 | $7.50/1M input, $22.50/1M output |
| Anthropic | Claude 3.5 Sonnet | $45.00 | $3/1M input, $15/1M output |
| Ollama | Llama 3 70B | $0.00 | Self-hosted, requires GPU |

### Scaling Cost Projections

| Monthly Calls | Azure Solution | Neura (Optimized) | Neura (Max Savings) | Savings |
|---------------|----------------|-------------------|---------------------|---------|
| 100 | $150 | $50 | $30 | 67-80% |
| 500 | $300 | $90 | $60 | 70-80% |
| 1,000 | $456 | $135 | $95 | 70-79% |
| 5,000 | $2,100 | $650 | $450 | 69-79% |
| 10,000 | $4,200 | $1,300 | $900 | 69-79% |

### Cost Optimization Strategies

1. **Use Self-Hosted Models**
   - Whisper for STT (free, requires GPU)
   - Ollama for LLM (free, requires GPU)
   - Coqui for TTS (free, lower quality)

2. **Choose Cost-Effective Providers**
   - Deepgram over Azure Speech (70% savings)
   - ElevenLabs over Azure TTS (31% savings)
   - GPT-4o over GPT-4 (25% savings)

3. **Implement Caching**
   - Cache common TTS responses
   - Cache LLM responses for FAQs
   - Use Redis for session management

4. **Optimize LLM Usage**
   - Use smaller models for simple tasks
   - Implement prompt caching
   - Reduce token usage with better prompts

5. **Use Spot/Preemptible Instances**
   - 60-80% savings on compute
   - Suitable for non-critical workloads

6. **Monitor and Optimize**
   - Track costs per call
   - Identify expensive operations
   - Switch providers based on usage patterns

### Hidden Costs to Consider

**Azure Solution**
- Vendor lock-in (migration costs)
- Limited provider choice
- Forced upgrades and pricing changes
- Complex pricing models

**Neura Call Center**
- Initial setup time
- Learning curve
- Self-hosting maintenance (if applicable)
- Provider management

### ROI Calculation

For a business handling 5,000 calls/month:

**Annual Savings**: ($2,100 - $650) × 12 = **$17,400/year**

**Break-even**: Even with 40 hours of setup/migration time at $100/hour, you break even in the first month.

---

## Contributing

We welcome contributions from the community! Whether it's bug fixes, new features, documentation improvements, or provider integrations, your help is appreciated.

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/neuraparse/neura-call-center.git
   cd neura-call-center
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style (Ruff formatting)
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests and linting**
   ```bash
   make format  # Format code
   make lint    # Check linting
   make test    # Run tests
   mypy apps    # Type checking
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test changes
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance tasks

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Contribution Ideas

**High Priority**
- Add new provider implementations (AssemblyAI, Azure Speech, Vonage, etc.)
- Improve LangGraph agent capabilities
- Add more comprehensive tests
- Create Kubernetes deployment manifests
- Build Grafana dashboards

**Medium Priority**
- Add support for more languages
- Implement call recording management
- Add sentiment analysis
- Create example applications
- Improve documentation

**Good First Issues**
- Fix typos in documentation
- Add code comments
- Improve error messages
- Add unit tests
- Update dependencies

### Development Guidelines

**Code Style**
- Use type hints for all functions
- Follow PEP 8 (enforced by Ruff)
- Write docstrings for public APIs
- Keep functions small and focused

**Testing**
- Write tests for new features
- Maintain >80% code coverage
- Use pytest fixtures for common setup
- Mock external API calls

**Documentation**
- Update README.md for user-facing changes
- Update PROJECT_SUMMARY.md for architecture changes
- Add docstrings to new functions/classes
- Include examples for new features

**Commit Messages**
- Use conventional commits format
- Keep first line under 72 characters
- Provide detailed description if needed
- Reference issues/PRs when applicable

### Code Review Process

1. All PRs require at least one approval
2. CI/CD checks must pass (tests, linting, type checking)
3. Code coverage should not decrease
4. Documentation must be updated
5. Breaking changes require discussion

### Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Documentation

### Available Documentation

- **[README.md](README.md)** - This file, quick start and overview
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Detailed project status and roadmap
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[API Documentation](http://localhost:8080/docs)** - Interactive OpenAPI docs (when running)

### Additional Resources

- **Examples**: See `examples/` directory for usage examples
- **Tests**: See `tests/` directory for test examples
- **Configuration**: See `.env.example` for all configuration options

---

## Roadmap

### Current Status (v0.1.0)

- ✅ Core infrastructure and API
- ✅ Provider abstraction layer (STT, TTS, Telephony)
- ✅ Database models and migrations
- ✅ Docker Compose setup
- ✅ Monitoring and observability stack
- ✅ Basic tests and documentation

### Upcoming (v0.2.0)

- 🚧 LangGraph agent implementation
- 🚧 WebSocket audio streaming
- 🚧 Twilio Media Streams integration
- 🚧 Call recording management
- 🚧 Additional provider implementations

### Future (v0.3.0+)

- 📋 Kubernetes deployment
- 📋 Multi-language support
- 📋 Advanced analytics dashboard
- 📋 Sentiment analysis
- 📋 Custom agent workflows
- 📋 Voice biometrics
- 📋 Real-time translation

See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for detailed roadmap.

---

## FAQ

### General Questions

**Q: What makes Neura Call Center different from other solutions?**
A: Provider flexibility, multi-cloud support, cost optimization, and modern technology stack. No vendor lock-in.

**Q: Can I use this in production?**
A: Yes, the core infrastructure is production-ready. However, some features (LangGraph agent, WebSocket streaming) are still in development.

**Q: What's the minimum cost to run this?**
A: With self-hosted options (Whisper, Ollama), you can run it for ~$80-100/month on a VPS. With cloud providers, expect ~$135-200/month for 1000 calls.

**Q: Do I need to use all the providers?**
A: No, you can choose any combination. The factory pattern allows easy switching between providers.

### Technical Questions

**Q: Can I run this without Docker?**
A: Yes, but Docker is recommended for easier setup. You'll need to manually install PostgreSQL, Redis, and RabbitMQ.

**Q: What Python version is required?**
A: Python 3.11 or higher is required for modern type hints and async features.

**Q: Can I use this with my existing database?**
A: Yes, but you'll need to run Alembic migrations to create the required tables.

**Q: How do I add a new provider?**
A: Implement the base interface (e.g., `BaseSTTProvider`) and register it in the factory. See existing providers for examples.

**Q: Is this compatible with Azure/AWS/GCP?**
A: Yes, it's cloud-agnostic. You can deploy on any cloud or on-premise.

### Provider Questions

**Q: Which STT provider is best?**
A: Deepgram for production (low latency, good accuracy), Whisper for self-hosted/privacy.

**Q: Which TTS provider sounds most natural?**
A: ElevenLabs has the most natural voices, but OpenAI TTS is also very good and more cost-effective.

**Q: Can I use multiple LLM providers simultaneously?**
A: Not currently, but you can switch providers via configuration without code changes.

**Q: Do I need Twilio for telephony?**
A: Twilio is currently the only fully implemented provider, but the architecture supports others (Vonage, Bandwidth, Telnyx).

---

## License

MIT License

Copyright (c) 2025 Neuraparse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Acknowledgments

This project was inspired by [Microsoft Call Center AI](https://github.com/microsoft/call-center-ai) but completely rewritten to eliminate Azure dependency and provide multi-cloud support with provider flexibility.

**Special Thanks To:**
- Microsoft for the original call-center-ai concept
- The FastAPI team for an amazing framework
- LangChain/LangGraph teams for AI orchestration tools
- All the open-source contributors whose libraries make this possible

---

## Support & Community

### Get Help

- **Documentation**: Start with this README and [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **GitHub Issues**: [Report bugs or request features](https://github.com/neuraparse/neura-call-center/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/neuraparse/neura-call-center/discussions)
- **Email**: support@neuraparse.com

### Stay Updated

- **Star the repo** to get notifications of new releases
- **Watch the repo** for updates and discussions
- **Follow us** on social media (coming soon)

### Commercial Support

For enterprise support, custom development, or consulting:
- Email: enterprise@neuraparse.com
- We offer: Training, custom integrations, SLA support, deployment assistance

---

## Project Status

**Current Version**: 0.1.0 (Alpha)

**Stability**: Core infrastructure is stable, but some features are still in development.

**Production Readiness**:
- ✅ API and database layer
- ✅ Provider abstraction
- ✅ Monitoring and observability
- 🚧 LangGraph agent (in progress)
- 🚧 WebSocket streaming (in progress)

**Last Updated**: November 2025

---

**Built with ❤️ by the Neuraparse team**


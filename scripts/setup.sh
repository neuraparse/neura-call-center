#!/bin/bash

# Neura Call Center Setup Script
# This script helps you set up the development environment

set -e

echo "🚀 Neura Call Center - Setup Script"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys:"
    echo "   - OpenAI API Key (for LLM)"
    echo "   - Deepgram API Key (for STT)"
    echo "   - ElevenLabs API Key (for TTS)"
    echo "   - Twilio credentials (for telephony)"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🗄️  Running database migrations..."
docker-compose exec -T api alembic upgrade head || {
    echo "⚠️  Migration failed. This is normal on first run."
    echo "   Waiting a bit more for database to be ready..."
    sleep 10
    docker-compose exec -T api alembic upgrade head
}

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Services are running:"
echo "   - API:        http://localhost:8080"
echo "   - API Docs:   http://localhost:8080/docs"
echo "   - Grafana:    http://localhost:3000 (admin/admin)"
echo "   - Prometheus: http://localhost:9090"
echo "   - RabbitMQ:   http://localhost:15672 (admin/admin)"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:        docker-compose logs -f"
echo "   - Stop services:    docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Run tests:        make test"
echo ""
echo "🎉 Happy coding!"


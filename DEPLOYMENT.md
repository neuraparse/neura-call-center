# 🚀 Deployment Guide

This guide covers deploying Neura Call Center to various environments.

## 📋 Prerequisites

- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 16+ with pgvector extension
- Redis/Valkey for caching
- API keys for your chosen providers

## 🐳 Docker Deployment (Recommended)

### Local/Development

```bash
# 1. Clone and setup
git clone <repo-url>
cd neura-call-center
cp .env.example .env

# 2. Edit .env with your credentials
nano .env

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Check health
curl http://localhost:8080/health
```

### Production

```bash
# 1. Build production image
docker-compose -f docker-compose.prod.yml build

# 2. Start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## ☁️ Cloud Deployments

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Setup RDS PostgreSQL**
   ```bash
   # Create RDS instance with PostgreSQL 16
   # Enable pgvector extension
   ```

2. **Setup ElastiCache (Redis)**
   ```bash
   # Create Redis cluster
   ```

3. **Deploy to ECS**
   ```bash
   # Build and push image to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t neura-call-center .
   docker tag neura-call-center:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/neura-call-center:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/neura-call-center:latest

   # Create ECS task definition and service
   ```

#### Using EKS (Kubernetes)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### GCP Deployment

#### Using Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/neura-call-center
gcloud run deploy neura-call-center \
  --image gcr.io/PROJECT_ID/neura-call-center \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Using GKE (Kubernetes)

```bash
# Create GKE cluster
gcloud container clusters create neura-cluster --num-nodes=3

# Deploy
kubectl apply -f k8s/
```

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name neura-rg --location eastus

# Create container instance
az container create \
  --resource-group neura-rg \
  --name neura-call-center \
  --image <your-registry>/neura-call-center:latest \
  --dns-name-label neura-call-center \
  --ports 8080
```

#### Using AKS (Kubernetes)

```bash
# Create AKS cluster
az aks create --resource-group neura-rg --name neura-cluster --node-count 3

# Deploy
kubectl apply -f k8s/
```

## 🔧 Environment Variables

### Required Variables

```bash
# Application
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8080

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Cache
CACHE_URL=redis://host:6379/0

# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# STT Provider (choose one)
DEEPGRAM_API_KEY=...
# or use Whisper (no key needed)

# TTS Provider (choose one)
ELEVENLABS_API_KEY=...
# or
OPENAI_API_KEY=sk-...

# Telephony Provider (choose one)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
```

## 📊 Monitoring

### Prometheus & Grafana

```bash
# Access Grafana
http://your-domain:3000

# Default credentials
Username: admin
Password: admin
```

### Health Checks

```bash
# Basic health
curl http://your-domain/health

# Readiness (includes DB check)
curl http://your-domain/health/ready

# Liveness
curl http://your-domain/health/live
```

## 🔒 Security Checklist

- [ ] Change default passwords (Grafana, RabbitMQ)
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Rotate API keys regularly
- [ ] Enable database encryption
- [ ] Set up VPC/private networks
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates

## 🔄 CI/CD

### GitHub Actions Example

See `.github/workflows/deploy.yml` for automated deployment pipeline.

### GitLab CI Example

See `.gitlab-ci.yml` for GitLab deployment pipeline.

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale API instances
docker-compose up -d --scale api=3

# Or in Kubernetes
kubectl scale deployment neura-api --replicas=3
```

### Database Scaling

- Use read replicas for read-heavy workloads
- Enable connection pooling (already configured in SQLAlchemy)
- Consider sharding for very large datasets

### Caching Strategy

- Redis/Valkey for session storage
- Cache frequently accessed data
- Use TTL appropriately

## 🆘 Troubleshooting

### Database Connection Issues

```bash
# Check database connectivity
docker-compose exec api python -c "from apps.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Provider Issues

```bash
# Check provider health
curl http://your-domain/api/v1/providers/health
```

### Logs

```bash
# View API logs
docker-compose logs -f api

# View all logs
docker-compose logs -f
```

## 📞 Support

For deployment issues, please open an issue on GitHub or contact the team.


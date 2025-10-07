# Setup and Deployment Guide

This guide provides detailed instructions for setting up and deploying the POS Display Pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Maintenance](#maintenance)

## Prerequisites

### Required Software

- **Python 3.11 or higher**
  ```bash
  python --version  # Should be 3.11+
  ```

- **Docker** (version 20.10+)
  ```bash
  docker --version
  ```

- **Docker Compose** (version 2.0+)
  ```bash
  docker-compose --version
  ```

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB+ free space
- **OS**: Linux, macOS, or Windows with WSL2

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd pipeline
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### 4. Set Up Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

### 5. Create Required Directories

```bash
# Using Makefile
make setup-dirs

# Or manually
mkdir -p storage/videos storage/models storage/temp logs
```

### 6. Start RabbitMQ

```bash
# Using Docker
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management

# Wait for RabbitMQ to be ready (about 10-15 seconds)
docker logs rabbitmq
```

### 7. Start Services

Open 4 terminal windows and run:

**Terminal 1 - API Service:**
```bash
source venv/bin/activate
python -m api.app
```

**Terminal 2 - Video Generator:**
```bash
source venv/bin/activate
python -m video_generator.service
```

**Terminal 3 - Model Converter:**
```bash
source venv/bin/activate
python -m model_converter.service
```

**Terminal 4 - Orchestrator:**
```bash
source venv/bin/activate
python -m orchestrator.service
```

### 8. Verify Development Setup

```bash
# Check API health
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","timestamp":"...","components":{"api":"healthy","queue":"healthy"}}
```

## Docker Deployment

### Quick Start

```bash
# Build all images
make docker-build

# Start all services
make docker-up

# View logs
make docker-logs
```

### Step-by-Step

#### 1. Build Docker Images

```bash
docker-compose build

# Or build specific service
docker-compose build api
docker-compose build video_generator
```

#### 2. Start Services

```bash
# Start in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up
```

#### 3. Check Service Status

```bash
# View running containers
docker-compose ps

# Expected output:
# NAME                     STATUS
# pipeline_api             Up
# pipeline_video_generator Up
# pipeline_model_converter Up
# pipeline_orchestrator    Up
# pipeline_rabbitmq        Up
```

#### 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f video_generator
```

#### 5. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Compose Configuration

The `docker-compose.yml` includes:

- **RabbitMQ**: Message queue with management UI
- **API**: REST API service (port 8000)
- **Video Generator**: Video generation service
- **Model Converter**: 3D model conversion service
- **Orchestrator**: Pipeline orchestration service

All services are connected via a Docker network and share volumes for storage.

## Production Deployment

### 1. Environment Configuration

Create production environment file:

```bash
cp .env.example .env.production
```

Edit `.env.production`:

```bash
# Production settings
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secure-api-key-here

QUEUE_HOST=rabbitmq
QUEUE_PORT=5672
QUEUE_USERNAME=pipeline_user
QUEUE_PASSWORD=secure_password_here

LOG_LEVEL=INFO
JSON_LOGS=true

MAX_CONCURRENT_JOBS=5
JOB_TIMEOUT_SECONDS=900
```

### 2. Security Hardening

**a. Set API Key:**
```bash
# Generate secure API key
openssl rand -hex 32

# Add to .env.production
API_KEY=<generated-key>
```

**b. Update Queue Credentials:**
```bash
# In .env.production
QUEUE_USERNAME=pipeline_prod
QUEUE_PASSWORD=<secure-password>
```

**c. Update docker-compose.yml:**
```yaml
rabbitmq:
  environment:
    RABBITMQ_DEFAULT_USER: pipeline_prod
    RABBITMQ_DEFAULT_PASS: <secure-password>
```

### 3. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. Persistent Storage

Configure volumes for persistence:

```yaml
volumes:
  rabbitmq_data:
    driver: local
  storage_data:
    driver: local
  logs_data:
    driver: local

services:
  rabbitmq:
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
```

### 5. Reverse Proxy (Nginx)

Create `nginx.conf`:

```nginx
upstream api_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. SSL/TLS Configuration

```bash
# Using Let's Encrypt
certbot --nginx -d your-domain.com
```

### 7. Monitoring Setup

Add monitoring stack (optional):

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

## Configuration

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | 0.0.0.0 | API host address |
| `API_PORT` | 8000 | API port |
| `API_KEY` | None | API authentication key |
| `QUEUE_HOST` | localhost | RabbitMQ host |
| `QUEUE_PORT` | 5672 | RabbitMQ port |
| `VIDEO_DURATION` | 30 | Video duration in seconds |
| `VIDEO_FRAME_RATE` | 30 | Video frame rate |
| `VIDEO_WIDTH` | 512 | Video width in pixels |
| `VIDEO_HEIGHT` | 512 | Video height in pixels |
| `POINT_CLOUD_DENSITY` | 1000 | Point cloud density |
| `LOG_LEVEL` | INFO | Logging level |
| `MAX_CONCURRENT_JOBS` | 3 | Max concurrent jobs |
| `JOB_TIMEOUT_SECONDS` | 600 | Job timeout |

### Queue Configuration

RabbitMQ queues used:
- `pipeline_input`: Initial text input
- `model_conversion_input`: Video to model conversion
- `pipeline_completed`: Completed pipelines

## Verification

### 1. Health Checks

```bash
# API health
curl http://localhost:8000/health

# RabbitMQ health
curl http://localhost:15672/api/health/checks/alarms \
  -u guest:guest
```

### 2. Test Pipeline

```bash
# Submit test request
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test display with LED lights and modern design"
  }'

# Save the request_id from response
```

### 3. Monitor Execution

```bash
# Watch logs
docker-compose logs -f api video_generator model_converter

# Check storage
ls -la storage/videos/
ls -la storage/models/
```

### 4. Run Tests

```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Maintenance

### Backup

```bash
# Backup storage
tar -czf backup-storage-$(date +%Y%m%d).tar.gz storage/

# Backup configuration
tar -czf backup-config-$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

### Log Rotation

```bash
# Add to crontab
0 0 * * * find /path/to/logs -name "*.log" -mtime +7 -delete
```

### Cleanup

```bash
# Clean old files
make clean

# Clean Docker
docker system prune -a

# Clean specific storage
rm -rf storage/temp/*
find storage/videos -mtime +30 -delete
find storage/models -mtime +30 -delete
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Monitoring

```bash
# Check service health
docker-compose ps

# View resource usage
docker stats

# Check disk usage
du -sh storage/*
df -h
```

## Troubleshooting

See README.md for common issues and solutions.

### Get Support

```bash
# View detailed logs
docker-compose logs --tail=100 <service-name>

# Check service status
docker-compose exec <service-name> ps aux

# Enter service container
docker-compose exec <service-name> bash
```
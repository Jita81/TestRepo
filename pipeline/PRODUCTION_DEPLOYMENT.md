# Production Deployment Guide
## POS to 3D Pipeline - Enhanced Version 2.0

This guide covers deploying the enhanced production-ready version of the pipeline with enterprise features.

---

## 🚀 Quick Start with Docker

### Option 1: Full Stack (Recommended)

Deploy the complete stack with all services:

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f pipeline-api
```

**Services included**:
- Pipeline API (port 8000)
- RabbitMQ (port 5672, management on 15672)
- MinIO object storage (port 9000, console on 9001)
- Redis cache (port 6379)
- Prometheus (port 9090)
- Grafana (port 3000)

### Option 2: API Only

Run just the API service:

```bash
# Build image
docker build -t pipeline-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/storage:/app/storage \
  --name pipeline-api \
  pipeline-api:latest
```

---

## 📦 Manual Installation

### Prerequisites

- Python 3.9+
- RabbitMQ (optional)
- MinIO or S3 (optional)
- Redis (optional)

### Installation Steps

```bash
# 1. Clone and navigate
cd pipeline/

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements-production.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Run the API
python app_enhanced.py
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following:

```bash
# Application
LOG_LEVEL=INFO
ENVIRONMENT=production

# RabbitMQ (optional)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=pipeline
RABBITMQ_PASS=your_secure_password

# MinIO/S3 (optional)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=your_secure_password
MINIO_SECURE=false

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Pipeline Configuration
MAX_CONCURRENT_JOBS=5
DEFAULT_VIDEO_DURATION=30
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  pipeline-api:
    environment:
      - LOG_LEVEL=INFO
      # Add your custom environment variables
```

---

## 🔧 Production Features

### 1. Message Queue (RabbitMQ)

**Purpose**: Asynchronous job processing, load distribution

**Usage**:
```python
# Request async processing
POST /api/v1/process
{
  "text": "Your POS description",
  "use_async": true,
  "priority": 5  # 0-9, higher = more priority
}
```

**Management UI**: http://localhost:15672
- Username: pipeline
- Password: pipeline_secret

### 2. Object Storage (MinIO)

**Purpose**: Cloud-native storage for videos and models

**Usage**:
```python
# Upload results to storage
POST /api/v1/process
{
  "text": "Your POS description",
  "upload_to_storage": true
}
```

**Console UI**: http://localhost:9001
- Username: minioadmin
- Password: minioadmin

### 3. Circuit Breaker

**Purpose**: Prevent cascading failures, improve resilience

**Features**:
- Automatic failure detection
- Graceful degradation
- Self-healing

**Monitoring**:
```bash
# Check circuit breaker status
curl http://localhost:8000/api/v1/circuit-breakers
```

### 4. Metrics & Monitoring

**Prometheus Metrics**: http://localhost:9090

**Grafana Dashboards**: http://localhost:3000
- Username: admin
- Password: admin

**Available Metrics**:
- `pipeline_requests_total` - Total requests
- `pipeline_processing_duration_seconds` - Processing time
- `pipeline_errors_total` - Error count
- `pipeline_videos_generated_total` - Videos created
- `pipeline_models_generated_total` - Models created
- `pipeline_queue_size` - Queue depth

### 5. Retry Mechanism

**Purpose**: Handle transient failures automatically

**Configuration**:
- Max attempts: 3
- Initial delay: 2 seconds
- Exponential backoff with jitter
- Automatic retry on network errors

---

## 📊 API Endpoints

### Health Check

```bash
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2025-10-06T12:00:00Z",
  "version": "2.0.0",
  "components": {
    "api": "healthy",
    "message_queue": "healthy",
    "object_storage": "healthy"
  }
}
```

### Process Request

```bash
POST /api/v1/process
Content-Type: application/json

{
  "text": "A vibrant display stand...",
  "priority": 5,
  "use_async": false,
  "upload_to_storage": false
}

Response:
{
  "job_id": "job_1234567890",
  "status": "processing",
  "message": "Request accepted",
  "estimated_time_seconds": 120
}
```

### Get Status

```bash
GET /api/v1/status/{job_id}

Response:
{
  "job_id": "job_1234567890",
  "status": "completed",
  "progress": 100,
  "result": {
    "video_path": "/app/storage/output/video.mp4",
    "model_path": "/app/storage/output/model.stl"
  }
}
```

### Metrics

```bash
GET /metrics

Response: Prometheus text format
```

### Circuit Breaker Stats

```bash
GET /api/v1/circuit-breakers

Response:
{
  "pipeline": {
    "state": "closed",
    "failure_count": 0,
    "failure_threshold": 5
  }
}
```

---

## 🔒 Security

### Production Checklist

- [ ] Change default passwords (RabbitMQ, MinIO, Grafana)
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS origins
- [ ] Set up authentication/authorization
- [ ] Enable firewall rules
- [ ] Use secrets management (e.g., Vault)
- [ ] Enable audit logging
- [ ] Set resource limits
- [ ] Configure backups

### Recommended Settings

```yaml
# docker-compose.yml
services:
  pipeline-api:
    environment:
      - CORS_ORIGINS=https://yourdomain.com
      - ENABLE_HTTPS=true
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale workers
docker-compose up -d --scale pipeline-worker=4

# Verify
docker-compose ps
```

### Load Balancing

Use Nginx or HAProxy:

```nginx
upstream pipeline {
    least_conn;
    server pipeline-api-1:8000;
    server pipeline-api-2:8000;
    server pipeline-api-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://pipeline;
    }
}
```

---

## 🔍 Monitoring & Alerting

### Prometheus Alerts

Create `alerts.yml`:

```yaml
groups:
  - name: pipeline_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(pipeline_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: LongProcessingTime
        expr: pipeline_processing_duration_seconds > 300
        annotations:
          summary: "Processing taking too long"
```

### Grafana Dashboards

Import provided dashboards:
1. Open Grafana (http://localhost:3000)
2. Import dashboard JSON from `monitoring/grafana/dashboards/`
3. View metrics in real-time

---

## 🐛 Troubleshooting

### Check Logs

```bash
# API logs
docker-compose logs -f pipeline-api

# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rabbitmq
```

### Common Issues

**Issue**: RabbitMQ connection failed
```bash
# Check if RabbitMQ is running
docker-compose ps rabbitmq

# Restart service
docker-compose restart rabbitmq
```

**Issue**: Out of disk space
```bash
# Check disk usage
df -h

# Clean old files
docker system prune -a
```

**Issue**: High memory usage
```bash
# Check container stats
docker stats

# Restart services
docker-compose restart
```

---

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Backup

```bash
# Backup storage
tar -czf backup-$(date +%Y%m%d).tar.gz storage/

# Backup database/volumes
docker-compose down
tar -czf volumes-backup-$(date +%Y%m%d).tar.gz \
  $(docker volume inspect pipeline_minio-data -f '{{.Mountpoint}}')
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **RabbitMQ Management**: http://localhost:15672
- **MinIO Console**: http://localhost:9001

---

## 💡 Best Practices

1. **Always use environment variables** for sensitive data
2. **Monitor metrics regularly** via Grafana
3. **Set up alerts** for critical failures
4. **Backup regularly** (storage, volumes, configuration)
5. **Test disaster recovery** procedures
6. **Keep dependencies updated** for security
7. **Use resource limits** to prevent resource exhaustion
8. **Enable audit logging** for compliance
9. **Implement proper authentication** for production
10. **Use HTTPS/TLS** for all external communication

---

**Production Deployment Complete!** 🎉

For support, check the main README or create an issue in the repository.

# POS Display Pipeline - End-to-End Prototype

A complete pipeline for generating 3D models from POS (Point of Sale) display text descriptions. This system takes a text description as input, generates a video representation, and converts it to a 3D model in STL format.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Overview

This prototype implements a microservices-based pipeline that:

1. **Accepts** text descriptions of marketing POS displays via REST API
2. **Generates** a 30-second video output using text-to-video processing
3. **Converts** the video to a 3D model in STL format
4. **Executes** end-to-end without manual intervention
5. **Uses** open-source models and frameworks
6. **Includes** comprehensive error handling and logging
7. **Provides** automated testing at each stage

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐      ┌──────────────────┐
│   API       │─────▶│  RabbitMQ    │─────▶│ Video Generator │─────▶│ Model Converter  │
│   Service   │      │  Queue       │      │   Service       │      │    Service       │
└─────────────┘      └──────────────┘      └─────────────────┘      └──────────────────┘
      │                     │                        │                         │
      │                     ▼                        ▼                         ▼
      │              ┌──────────────┐         ┌──────────┐            ┌──────────┐
      └─────────────▶│ Orchestrator │         │  Video   │            │   STL    │
                     │   Service    │         │  Storage │            │  Output  │
                     └──────────────┘         └──────────┘            └──────────┘
```

### Components

- **API Service**: FastAPI-based REST API for accepting text input
- **Video Generator**: Converts text descriptions to video (30 seconds, MP4 format)
- **Model Converter**: Converts video frames to 3D mesh models (STL format)
- **Orchestrator**: Monitors pipeline progress and manages state
- **Message Queue**: RabbitMQ for asynchronous inter-service communication

## Features

✅ **REST API** with OpenAPI documentation  
✅ **Asynchronous processing** via message queues  
✅ **Microservices architecture** with Docker support  
✅ **Comprehensive logging** with structured logs  
✅ **Error handling** with retry mechanisms  
✅ **Automated tests** (unit and integration)  
✅ **Docker Compose** for easy deployment  
✅ **Health checks** for all services  
✅ **Configuration management** via environment variables  

## Requirements

### System Requirements
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- 4GB+ RAM
- 10GB+ disk space

### Python Dependencies
See `requirements.txt` for full list. Key dependencies:
- FastAPI & Uvicorn (API framework)
- OpenCV (video processing)
- numpy-stl (3D model generation)
- Pika (RabbitMQ client)
- Structlog (structured logging)

## Installation

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pipeline
   ```

2. **Build Docker images**
   ```bash
   make docker-build
   # or
   docker-compose build
   ```

3. **Start all services**
   ```bash
   make docker-up
   # or
   docker-compose up -d
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   ```

### Option 2: Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

3. **Create required directories**
   ```bash
   make setup-dirs
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start RabbitMQ**
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management
   ```

6. **Start services** (in separate terminals)
   ```bash
   # Terminal 1 - API
   make run-api
   
   # Terminal 2 - Video Generator
   make run-video
   
   # Terminal 3 - Model Converter
   make run-model
   
   # Terminal 4 - Orchestrator
   make run-orchestrator
   ```

## Quick Start

### Using Docker Compose

1. **Start the pipeline**
   ```bash
   docker-compose up -d
   ```

2. **Submit a generation request**
   ```bash
   curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "A modern retail display for energy drinks with LED backlighting and metallic finish",
       "metadata": {"customer_id": "demo001"}
     }'
   ```

3. **Check the response**
   ```json
   {
     "request_id": "req_abc123def456",
     "status": "pending",
     "message": "Pipeline initiated successfully",
     "created_at": "2025-10-07T12:00:00Z"
   }
   ```

4. **Monitor progress**
   ```bash
   # View logs
   docker-compose logs -f
   
   # Check generated files
   ls -la storage/videos/
   ls -la storage/models/
   ```

## Usage

### API Endpoints

#### POST `/generate`
Submit a text description for processing.

**Request:**
```json
{
  "description": "A sleek point-of-sale display featuring premium chocolate bars with warm LED lighting",
  "metadata": {
    "customer_id": "cust_12345",
    "project": "retail_displays_q4"
  }
}
```

**Response:**
```json
{
  "request_id": "req_a1b2c3d4e5f6",
  "status": "pending",
  "message": "Pipeline initiated successfully",
  "created_at": "2025-10-07T12:00:00.000Z"
}
```

#### GET `/status/{request_id}`
Check the status of a pipeline request.

**Response:**
```json
{
  "request_id": "req_a1b2c3d4e5f6",
  "status": "processing",
  "message": "Status tracking information"
}
```

#### GET `/health`
Check API and component health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T12:00:00.000Z",
  "components": {
    "api": "healthy",
    "queue": "healthy"
  }
}
```

### Interactive API Documentation

Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### RabbitMQ Management

Access RabbitMQ management interface:
- **URL**: http://localhost:15672
- **Username**: guest
- **Password**: guest

## API Documentation

### Input Validation

The API validates all input:
- Description must be 10-1000 characters
- No special characters: `<`, `>`, `{`, `}`, null bytes
- Whitespace is automatically trimmed

### Error Responses

```json
{
  "detail": "Error message",
  "stage": "validation",
  "errors": [...]
}
```

## Testing

### Run All Tests
```bash
make test
# or
pytest
```

### Run with Coverage
```bash
make test-coverage
# or
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Specific Tests
```bash
# Unit tests only
pytest tests/test_models.py

# Integration tests
pytest tests/test_integration.py -m integration

# Specific test
pytest tests/test_api.py::TestHealthEndpoint::test_health_check
```

### Test Structure
```
tests/
├── conftest.py              # Pytest fixtures
├── test_models.py           # Data model tests
├── test_api.py              # API endpoint tests
├── test_video_generator.py  # Video generation tests
├── test_model_converter.py  # 3D conversion tests
└── test_integration.py      # End-to-end tests
```

## Configuration

### Environment Variables

All configuration is managed via environment variables. See `.env.example` for all options.

Key settings:

```bash
# API
API_HOST=0.0.0.0
API_PORT=8000

# Queue
QUEUE_HOST=localhost
QUEUE_PORT=5672

# Video Generation
VIDEO_DURATION=30
VIDEO_FRAME_RATE=30
VIDEO_WIDTH=512
VIDEO_HEIGHT=512

# Storage
VIDEO_STORAGE_PATH=storage/videos
MODEL_STORAGE_PATH=storage/models

# Logging
LOG_LEVEL=INFO
JSON_LOGS=true
```

### Docker Compose Configuration

Modify `docker-compose.yml` to adjust:
- Port mappings
- Resource limits
- Environment variables
- Volume mounts

## Troubleshooting

### Common Issues

**Queue Connection Failed**
```
Error: Failed to connect to queue after 3 attempts
```
Solution: Ensure RabbitMQ is running
```bash
docker-compose up -d rabbitmq
```

**Storage Permission Denied**
```
Error: Permission denied: 'storage/videos'
```
Solution: Create directories with correct permissions
```bash
make setup-dirs
chmod -R 755 storage/
```

**Video Generation Timeout**
```
Error: Video generation timeout
```
Solution: Increase timeout in configuration
```bash
JOB_TIMEOUT_SECONDS=1200  # 20 minutes
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f video_generator

# Local logs
tail -f logs/pipeline.log
```

### Reset Everything

```bash
# Stop and remove containers
docker-compose down -v

# Clean storage
make clean

# Rebuild and restart
make docker-build
make docker-up
```

## Development

### Project Structure

```
pipeline/
├── api/                    # API service
│   ├── __init__.py
│   └── app.py
├── video_generator/        # Video generation service
│   ├── __init__.py
│   └── service.py
├── model_converter/        # 3D conversion service
│   ├── __init__.py
│   └── service.py
├── orchestrator/           # Orchestration service
│   ├── __init__.py
│   └── service.py
├── common/                 # Shared utilities
│   ├── __init__.py
│   ├── models.py
│   ├── queue_client.py
│   ├── logging_config.py
│   ├── exceptions.py
│   └── config.py
├── tests/                  # Test suite
├── config/                 # Configuration files
├── storage/                # Output storage
│   ├── videos/
│   ├── models/
│   └── temp/
├── docker-compose.yml      # Docker Compose config
├── Dockerfile.*            # Service Dockerfiles
├── requirements.txt        # Python dependencies
├── pytest.ini             # Test configuration
├── Makefile               # Development commands
└── README.md              # This file
```

### Adding New Features

1. **Create feature branch**
2. **Implement changes**
3. **Add tests**
4. **Update documentation**
5. **Run tests**: `make test`
6. **Submit pull request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document all public functions
- Keep functions focused and small
- Write comprehensive docstrings

## API Examples

### Using cURL

```bash
# Submit request
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Modern display with LED lights"}'

# Check health
curl http://localhost:8000/health

# Check status
curl http://localhost:8000/status/req_abc123
```

### Using Python

```python
import requests

# Submit generation request
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "description": "Elegant wine display with wooden shelves",
        "metadata": {"customer": "retail_store_001"}
    }
)

data = response.json()
request_id = data["request_id"]
print(f"Request ID: {request_id}")

# Check status
status = requests.get(f"http://localhost:8000/status/{request_id}")
print(status.json())
```

## Production Considerations

This is a **prototype implementation**. For production use, consider:

- ✅ Add authentication and authorization
- ✅ Implement request rate limiting
- ✅ Add request/response validation middleware
- ✅ Set up monitoring and alerting (Prometheus, Grafana)
- ✅ Implement distributed tracing
- ✅ Add caching layer (Redis)
- ✅ Use production-grade message broker configuration
- ✅ Implement proper backup and recovery
- ✅ Add load balancing
- ✅ Set up CI/CD pipeline
- ✅ Implement proper secrets management
- ✅ Add comprehensive error recovery
- ✅ Scale services based on load

## License

[Your License Here]

## Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review logs for error details

## Changelog

### v1.0.0 - Prototype Release
- Initial end-to-end pipeline implementation
- Text-to-video generation
- Video-to-3D model conversion
- Microservices architecture
- Docker Compose deployment
- Comprehensive test suite
- API documentation
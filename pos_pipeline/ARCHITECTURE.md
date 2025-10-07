# POS Pipeline - Architecture Documentation

## System Overview

The POS Display Pipeline is a microservices-based system that transforms text descriptions into 3D models through video generation. The architecture follows clean separation of concerns with modular, testable components.

## Architecture Principles

1. **Modularity**: Each service is independent and can be tested/deployed separately
2. **Asynchronous Processing**: Long-running tasks execute in background
3. **Clear Contracts**: Well-defined interfaces between services
4. **Error Resilience**: Comprehensive error handling at each stage
5. **Observability**: Extensive logging and status tracking

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                    (HTTP REST Client)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                      (FastAPI)                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ - Authentication (API Key)                           │  │
│  │ - Request Validation                                 │  │
│  │ - Response Formatting                                │  │
│  │ - Error Handling                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Internal API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Pipeline Orchestrator                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ - Job Queue Management                               │  │
│  │ - Stage Coordination                                 │  │
│  │ - Progress Tracking                                  │  │
│  │ - Timeout Management                                 │  │
│  │ - Error Recovery                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────┬──────────────────┬────────────────────┬────────────────┘
     │                  │                    │
     │ Stage 1          │ Stage 2           │ Stage 3
     ▼                  ▼                    ▼
┌──────────┐      ┌──────────┐        ┌──────────┐
│  Text    │      │  Video   │        │   3D     │
│Processor │──────│Generator │────────│Converter │
└──────────┘      └──────────┘        └──────────┘
     │                  │                    │
     │                  │                    │
     └──────────────────┴────────────────────┘
                        │
                        ▼
            ┌────────────────────┐
            │   Storage Layer    │
            │  - Videos (MP4)    │
            │  - Models (STL)    │
            │  - Metadata        │
            └────────────────────┘
```

## Component Details

### 1. API Gateway (`services/api_gateway`)

**Responsibility**: External interface for the pipeline

**Key Features**:
- RESTful API endpoints
- API key authentication
- Request/response validation
- CORS configuration
- Error formatting

**Endpoints**:
- `POST /pipeline/process` - Submit job
- `GET /pipeline/status/{job_id}` - Check status
- `GET /pipeline/result/{job_id}` - Get results
- `GET /health` - Health check

**Technologies**:
- FastAPI (web framework)
- Pydantic (validation)
- Uvicorn (ASGI server)

### 2. Pipeline Orchestrator (`services/orchestrator`)

**Responsibility**: Coordinate pipeline execution

**Key Features**:
- Job queue management
- Stage sequencing
- Progress tracking
- Timeout enforcement
- Error handling and recovery

**Workflow**:
1. Accept job from API Gateway
2. Generate unique job ID
3. Execute stages sequentially:
   - Text Processing
   - Video Generation
   - 3D Model Conversion
4. Track status throughout
5. Store final results

**State Management**:
- In-memory for prototype (production would use Redis/DB)
- Job status tracking
- Result caching

### 3. Text Processor (`services/text_processor`)

**Responsibility**: Validate and preprocess input text

**Processing Steps**:
1. Input validation
   - Length checks
   - Content validation
   - Character encoding
2. Sanitization
   - Remove harmful characters
   - Clean HTML/scripts
   - Normalize whitespace
3. Metadata extraction
   - Keyword extraction
   - Token counting

**Output**:
- Processed text
- Token count
- Keywords
- Processing metadata

### 4. Video Generator (`services/video_generator`)

**Responsibility**: Generate video from text

**Processing Steps**:
1. Text analysis
2. Video generation (placeholder in prototype)
3. Format validation
4. Quality checks

**Output Format**:
- Format: MP4
- Duration: 30+ seconds
- Resolution: 512x512
- FPS: 24

**Note**: In production, this would integrate with AI models like:
- Stable Video Diffusion
- ModelScope Text-to-Video
- Other text-to-video models

### 5. 3D Model Converter (`services/model_converter`)

**Responsibility**: Convert video to 3D model

**Processing Steps**:
1. Frame extraction (key frames)
2. Point cloud generation
3. Mesh creation (Delaunay triangulation)
4. STL export

**Algorithms**:
- Edge detection (Canny)
- Convex hull generation
- Mesh simplification

**Output Format**:
- Format: STL
- Includes: Vertices, faces, normals

## Data Flow

### Pipeline Execution Flow

```
1. Client Request
   ↓
2. API Gateway
   - Validate request
   - Authenticate
   ↓
3. Orchestrator
   - Create job
   - Queue processing
   ↓
4. Text Processing
   - Validate text
   - Sanitize
   - Extract metadata
   ↓
5. Video Generation
   - Generate video
   - Save to storage
   ↓
6. 3D Conversion
   - Extract frames
   - Create mesh
   - Export STL
   ↓
7. Complete
   - Store results
   - Update status
   ↓
8. Client retrieves results
```

### Data Models

#### PipelineInput
```python
{
    "text": str,              # Input description
    "metadata": dict          # Optional metadata
}
```

#### PipelineOutput
```python
{
    "job_id": str,
    "status": str,
    "video_url": str,
    "model_url": str,
    "processing_time": float,
    "stages": {
        "text_processing": {...},
        "video_generation": {...},
        "model_conversion": {...}
    }
}
```

#### ProcessingStatus
```python
{
    "job_id": str,
    "stage": str,
    "progress": float,
    "message": str,
    "created_at": datetime,
    "updated_at": datetime,
    "error": str | None
}
```

## Error Handling Strategy

### Error Types

1. **ValidationError**: Invalid input data
2. **TextProcessingError**: Text processing failures
3. **VideoGenerationError**: Video creation failures
4. **ModelConversionError**: 3D conversion failures
5. **StorageError**: File system issues
6. **TimeoutError**: Processing timeouts
7. **ResourceLimitError**: Resource constraints

### Error Handling Flow

```
Try:
    Execute stage
Catch PipelineException:
    - Log error details
    - Update job status
    - Store error info
    - Mark as recoverable/non-recoverable
    - Return error response
```

### Recovery Strategies

- **Validation errors**: Immediate failure, user correction needed
- **Processing errors**: Retry with exponential backoff (future)
- **Storage errors**: Check disk space, retry
- **Timeout errors**: Configurable timeouts per stage

## Logging Architecture

### Log Levels

- **DEBUG**: Detailed diagnostic info
- **INFO**: General operational events
- **WARNING**: Unusual but handled situations
- **ERROR**: Error events requiring attention

### Log Destinations

1. **Console**: Real-time monitoring
2. **File** (`pipeline.log`): Persistent text logs
3. **JSON** (`pipeline.json.log`): Structured logs
4. **Error** (`errors.log`): Error-only logs

### Log Format

```json
{
    "timestamp": "2025-10-07T10:00:00Z",
    "level": "INFO",
    "service": "orchestrator",
    "job_id": "550e8400-...",
    "stage": "video_generation",
    "message": "Video generation completed",
    "duration": 95.2,
    "details": {...}
}
```

## Storage Architecture

### Directory Structure

```
storage/
├── videos/
│   └── {job_id}.mp4
└── models/
    └── {job_id}.stl
```

### Storage Management

- **Cleanup**: Manual/scheduled cleanup (future: automatic)
- **Limits**: Configurable size limits
- **Access**: Static file serving via FastAPI

## Security Considerations

### Authentication

- API Key authentication via headers
- Configurable API key in environment

### Input Validation

- Text length limits
- Character sanitization
- HTML/script tag removal
- Unicode validation

### File Security

- Path validation (no directory traversal)
- File size limits
- Format validation
- Sanitized filenames

## Scalability Considerations

### Current Limitations (Prototype)

- In-memory job tracking
- Single instance processing
- Sequential job execution

### Future Enhancements

1. **Distributed Processing**
   - Message queue (RabbitMQ/Kafka)
   - Worker pool
   - Load balancing

2. **State Management**
   - Redis for job tracking
   - PostgreSQL for persistent data
   - Distributed caching

3. **Horizontal Scaling**
   - Container orchestration (Kubernetes)
   - Auto-scaling workers
   - Service mesh

4. **Performance**
   - GPU acceleration
   - Batch processing
   - Result caching

## Testing Strategy

### Test Levels

1. **Unit Tests**
   - Individual service functions
   - Validation logic
   - Error handling

2. **Integration Tests**
   - End-to-end pipeline
   - Service interactions
   - Data flow

3. **API Tests**
   - Endpoint behavior
   - Authentication
   - Error responses

### Test Coverage

- Target: >80% code coverage
- Focus: Critical paths, error handling
- Mock: External dependencies

## Monitoring & Observability

### Metrics (Future)

- Jobs processed
- Processing times
- Error rates
- Resource usage

### Health Checks

- API endpoint: `/health`
- Service availability
- Dependency checks

## Configuration Management

### Environment Variables

All configuration via `.env` file:
- API settings
- Processing limits
- Timeouts
- Storage paths
- Logging levels

### Configuration Hierarchy

1. Environment variables (highest priority)
2. `.env` file
3. Default values in `settings.py`

## Deployment Options

### 1. Local Development

```bash
python -m uvicorn services.api_gateway.main:app
```

### 2. Docker Container

```bash
docker build -t pos-pipeline .
docker run -p 8000:8000 pos-pipeline
```

### 3. Docker Compose

```bash
docker-compose up -d
```

### 4. Production (Future)

- Kubernetes deployment
- Load balancer
- Auto-scaling
- Monitoring stack

## API Contract Versioning

### Current Version: 1.0.0

- Stable API contracts
- Backward compatibility maintained
- Version in API responses

### Future Versioning

- URL-based: `/v2/pipeline/process`
- Header-based: `API-Version: 2.0`

## Dependencies

### Core Dependencies

- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **OpenCV**: Video processing
- **Trimesh**: 3D mesh operations
- **NumPy**: Numerical operations

### Optional Dependencies

- **RabbitMQ**: Message queue (future)
- **Redis**: Caching (future)
- **PostgreSQL**: Persistence (future)

## Performance Characteristics

### Typical Processing Times

- Text Processing: 1-3 seconds
- Video Generation: 60-120 seconds
- 3D Conversion: 20-40 seconds
- **Total**: 2-3 minutes

### Resource Usage

- CPU: 50-80% during processing
- Memory: 2-4 GB
- Disk: ~100 MB per job
- Network: Minimal

## Known Limitations

1. **Video Generation**: Uses placeholder algorithm
2. **3D Quality**: Basic mesh generation
3. **Concurrency**: Limited parallel processing
4. **Persistence**: In-memory state
5. **Scaling**: Single instance only

## Future Roadmap

### Phase 2: Production Models

- Integrate real AI models
- Improve 3D quality
- Advanced validation

### Phase 3: Scale

- Distributed processing
- Database integration
- Advanced monitoring

### Phase 4: Features

- Batch processing
- Webhooks
- UI dashboard
- Quality metrics
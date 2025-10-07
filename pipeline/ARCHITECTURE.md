# Architecture Documentation

## System Overview

The POS Display Pipeline is a microservices-based system that transforms text descriptions into 3D models through a multi-stage processing pipeline.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Client Applications                            │
│                     (cURL, Python, JavaScript, etc.)                    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                │ HTTP/REST
                                │
                    ┌───────────▼──────────┐
                    │                      │
                    │    API Gateway       │
                    │   (FastAPI/8000)     │
                    │                      │
                    └───────────┬──────────┘
                                │
                                │ Publishes to Queue
                                │
                    ┌───────────▼──────────┐
                    │                      │
                    │    RabbitMQ Queue    │
                    │   (Message Broker)   │
                    │                      │
                    └─────┬────────┬───────┘
                          │        │
           ┌──────────────┘        └──────────────┐
           │                                      │
           │ pipeline_input                       │ model_conversion_input
           │                                      │
┌──────────▼───────────┐              ┌──────────▼────────────┐
│                      │              │                       │
│  Video Generator     │              │  Model Converter      │
│     Service          │─────────────▶│      Service          │
│                      │  Queue Msg   │                       │
└──────────┬───────────┘              └──────────┬────────────┘
           │                                     │
           │ Stores Video                        │ Stores STL
           │                                     │
    ┌──────▼──────┐                      ┌──────▼──────┐
    │             │                      │             │
    │   Video     │                      │   Model     │
    │  Storage    │                      │  Storage    │
    │             │                      │             │
    └─────────────┘                      └──────┬──────┘
                                                │
                                                │ Completion Event
                                                │
                                    ┌───────────▼──────────┐
                                    │                      │
                                    │   Orchestrator       │
                                    │     Service          │
                                    │  (State Manager)     │
                                    │                      │
                                    └──────────────────────┘
```

## Component Details

### 1. API Service

**Technology**: FastAPI + Uvicorn  
**Port**: 8000  
**Responsibility**: HTTP request handling and validation

#### Key Features:
- REST API endpoints
- Input validation with Pydantic
- API key authentication (optional)
- Health checks
- CORS support
- OpenAPI/Swagger documentation
- Async request handling

#### Endpoints:
- `POST /generate` - Submit pipeline request
- `GET /status/{request_id}` - Check request status
- `GET /health` - Health check
- `GET /docs` - Interactive API docs
- `GET /redoc` - Alternative API docs

#### Data Flow:
```
1. Receive HTTP POST request
2. Validate input with Pydantic models
3. Generate unique request ID
4. Create PipelineMessage
5. Publish to RabbitMQ
6. Return 202 Accepted response
```

### 2. Message Queue (RabbitMQ)

**Technology**: RabbitMQ 3.12  
**Ports**: 5672 (AMQP), 15672 (Management UI)  
**Responsibility**: Asynchronous message routing

#### Queues:
- `pipeline_input` - Initial text processing
- `model_conversion_input` - Video to 3D conversion
- `pipeline_completed` - Completion notifications

#### Features:
- Message persistence
- Acknowledgment handling
- Retry mechanisms
- Dead letter queues (future)
- Priority queuing (future)

### 3. Video Generator Service

**Technology**: Python + OpenCV  
**Responsibility**: Text-to-video generation

#### Current Implementation:
- Generates animated gradient videos (prototype)
- 30 seconds duration
- 30 FPS frame rate
- 512x512 resolution
- MP4 format (H.264)

#### Production Ready:
- Integration point for actual text-to-video models
- Support for models like:
  - Stable Video Diffusion
  - ModelScope Text-to-Video
  - CogVideo
  - Custom trained models

#### Processing Flow:
```
1. Consume message from pipeline_input queue
2. Parse text description
3. Generate video frames
4. Encode to MP4
5. Store in video storage
6. Create VideoMetadata
7. Publish to model_conversion_input queue
```

### 4. Model Converter Service

**Technology**: Python + OpenCV + numpy-stl + scipy  
**Responsibility**: Video-to-3D model conversion

#### Current Implementation:
- Frame extraction from video
- Point cloud generation
- Convex hull mesh creation
- STL export

#### Processing Steps:
```
1. Extract frames from video (every 10th frame)
2. Generate point cloud from frames:
   - Use pixel intensity as depth approximation
   - Sample N points per frame
   - Normalize coordinates
3. Create 3D mesh:
   - Compute convex hull
   - Generate triangular faces
   - Export to STL format
4. Store model and metadata
5. Publish completion event
```

#### Production Enhancements:
- Depth estimation models (MiDaS, DPT)
- Multi-view reconstruction
- COLMAP integration
- NeRF-based reconstruction
- Mesh optimization and simplification

### 5. Orchestrator Service

**Technology**: Python  
**Responsibility**: Pipeline state management

#### Functions:
- Monitor pipeline progress
- Track request states
- Handle timeouts
- Manage retries
- Cleanup old data
- Provide status information

#### State Management:
```python
PipelineResult {
    request_id: str
    status: PipelineStatus
    video_metadata: Optional[VideoMetadata]
    model_metadata: Optional[ModelMetadata]
    processing_time: float
    timestamps: {created, started, completed}
}
```

## Data Models

### TextInput
```python
{
    description: str (10-1000 chars)
    metadata: dict (optional)
}
```

### PipelineMessage
```python
{
    request_id: str
    stage: PipelineStage
    payload: dict
    timestamp: datetime
    status: PipelineStatus
    error_message: Optional[str]
    retry_count: int
}
```

### VideoMetadata
```python
{
    video_path: str
    duration: float
    frame_rate: int
    resolution: (width, height)
    size_bytes: int
    generated_at: datetime
}
```

### ModelMetadata
```python
{
    model_path: str
    format: str
    vertex_count: int
    face_count: int
    size_bytes: int
    generated_at: datetime
}
```

## Communication Patterns

### 1. Request-Response (API)
```
Client -> HTTP POST -> API -> HTTP 202 Response -> Client
```

### 2. Publish-Subscribe (Queue)
```
Service A -> Publish Message -> Queue -> Consume -> Service B
```

### 3. Event-Driven (Orchestrator)
```
Service -> Complete -> Publish Event -> Orchestrator -> Update State
```

## Error Handling Strategy

### Levels:
1. **Input Validation**: Pydantic models at API level
2. **Service Errors**: Try-catch with logging
3. **Queue Errors**: Message acknowledgment + requeue
4. **Timeout Handling**: Orchestrator monitors
5. **Resource Errors**: Pre-flight checks

### Error Flow:
```
Error Occurs
    ├─> Log error with context
    ├─> Update pipeline state
    ├─> Increment retry counter
    └─> Requeue (if retries available)
         or
        Mark as failed
```

## Scalability Considerations

### Horizontal Scaling:
- **API Service**: Multiple instances behind load balancer
- **Video Generator**: Worker pool (limited by GPU)
- **Model Converter**: Worker pool (CPU-bound)
- **Queue**: RabbitMQ cluster

### Vertical Scaling:
- Increase container resources
- Optimize video processing
- GPU acceleration for ML models

### Bottlenecks:
1. Video generation (GPU-intensive)
2. 3D conversion (CPU + memory intensive)
3. Storage I/O

## Security Architecture

### API Layer:
- Optional API key authentication
- Request rate limiting (future)
- Input sanitization
- CORS configuration

### Service Layer:
- No external ports except API
- Internal network communication
- Environment variable configuration
- Secrets management (future)

### Storage:
- Isolated volumes
- File permission controls
- Cleanup policies

## Monitoring & Observability

### Logging:
- Structured JSON logs
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request ID tracing
- Component-specific loggers

### Metrics (Future):
- Request rate
- Processing time
- Queue depth
- Success/failure rates
- Resource utilization

### Health Checks:
- API service health
- Queue connectivity
- Storage availability
- Service readiness

## Deployment Architecture

### Docker Compose:
```yaml
Services:
  - rabbitmq (message queue)
  - api (web service)
  - video_generator (worker)
  - model_converter (worker)
  - orchestrator (monitor)

Networks:
  - pipeline_network (bridge)

Volumes:
  - storage (persistent)
  - logs (persistent)
```

### Production Deployment:
- Kubernetes orchestration
- Helm charts
- Service mesh (Istio/Linkerd)
- Ingress controller
- Auto-scaling policies
- Health probes

## Future Enhancements

### Phase 2:
- [ ] State persistence (PostgreSQL/Redis)
- [ ] Enhanced status tracking
- [ ] Webhook notifications
- [ ] Result retrieval API
- [ ] Batch processing

### Phase 3:
- [ ] Production-grade ML models
- [ ] GPU acceleration
- [ ] Advanced 3D reconstruction
- [ ] Quality metrics
- [ ] Model optimization

### Phase 4:
- [ ] Web UI for monitoring
- [ ] Real-time progress updates (WebSocket)
- [ ] Multi-tenant support
- [ ] Analytics dashboard
- [ ] Cost optimization

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Framework | FastAPI | REST API |
| Web Server | Uvicorn | ASGI server |
| Message Queue | RabbitMQ | Async messaging |
| Video Processing | OpenCV | Frame manipulation |
| 3D Processing | numpy-stl, scipy | Mesh generation |
| Logging | Structlog | Structured logs |
| Testing | Pytest | Unit/integration tests |
| Containerization | Docker | Service isolation |
| Orchestration | Docker Compose | Multi-service deploy |
| Data Validation | Pydantic | Schema validation |

## Performance Characteristics

### Expected Latencies:
- API response: < 100ms
- Video generation: 30-120 seconds
- 3D conversion: 10-30 seconds
- Total pipeline: 1-3 minutes

### Resource Usage:
- API: ~100MB RAM
- Video Generator: ~500MB-2GB RAM
- Model Converter: ~200MB-1GB RAM
- RabbitMQ: ~100-200MB RAM

### Throughput:
- Prototype: 1-3 concurrent requests
- Production: 10-50 concurrent requests (with scaling)
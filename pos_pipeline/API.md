# POS Pipeline - API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/health` and root) require API key authentication via header:

```
X-API-Key: your-api-key-here
```

## Endpoints

### 1. Health Check

Check if the API is running and healthy.

**Endpoint**: `GET /health`

**Authentication**: Not required

**Response**: 200 OK
```json
{
  "status": "healthy",
  "service": "POS Display Pipeline",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 2. Root Endpoint

Get basic API information.

**Endpoint**: `GET /`

**Authentication**: Not required

**Response**: 200 OK
```json
{
  "service": "POS Display Pipeline",
  "version": "1.0.0",
  "status": "running"
}
```

---

### 3. Submit Pipeline Job

Submit a text description for processing through the pipeline.

**Endpoint**: `POST /pipeline/process`

**Authentication**: Required (X-API-Key header)

**Request Body**:
```json
{
  "text": "string (1-1024 characters, required)",
  "metadata": {
    "key": "value (optional)"
  }
}
```

**Response**: 202 Accepted
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Job submitted successfully",
  "status_url": "/pipeline/status/550e8400-e29b-41d4-a716-446655440000",
  "result_url": "/pipeline/result/550e8400-e29b-41d4-a716-446655440000"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/pipeline/process \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "text": "A modern red and white POS display stand for electronics",
    "metadata": {
      "category": "electronics",
      "brand": "TechCo"
    }
  }'
```

**Validation Rules**:
- Text must be 1-1024 characters
- Text must contain at least 3 words
- Text cannot be empty or whitespace only

**Error Responses**:

**400 Bad Request** - Invalid input
```json
{
  "detail": {
    "error": "Text exceeds maximum length of 1024 characters",
    "stage": "text_processing",
    "details": {
      "length": 1500,
      "max_length": 1024
    }
  }
}
```

**403 Forbidden** - Invalid API key
```json
{
  "detail": "Invalid API key"
}
```

**422 Unprocessable Entity** - Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 4. Get Job Status

Get the current processing status of a job.

**Endpoint**: `GET /pipeline/status/{job_id}`

**Authentication**: Required (X-API-Key header)

**Path Parameters**:
- `job_id` (string): Unique job identifier

**Response**: 200 OK
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "stage": "video_generation",
  "progress": 45.0,
  "message": "Generating video from text",
  "created_at": "2025-10-07T10:00:00.000Z",
  "updated_at": "2025-10-07T10:01:30.000Z",
  "error": null
}
```

**Possible Stages**:
- `queued` - Job is queued for processing
- `text_processing` - Processing input text
- `video_generation` - Generating video
- `model_conversion` - Converting to 3D model
- `completed` - Processing complete
- `failed` - Processing failed

**Example**:
```bash
curl http://localhost:8000/pipeline/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: dev-key-change-in-production"
```

**Error Responses**:

**404 Not Found** - Job not found
```json
{
  "detail": "Job 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

### 5. Get Job Result

Get the final result of a completed job.

**Endpoint**: `GET /pipeline/result/{job_id}`

**Authentication**: Required (X-API-Key header)

**Path Parameters**:
- `job_id` (string): Unique job identifier

**Response**: 200 OK (when completed)
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "video_url": "/storage/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
  "model_url": "/storage/models/550e8400-e29b-41d4-a716-446655440000.stl",
  "video_path": "/workspace/pos_pipeline/storage/videos/550e8400.mp4",
  "model_path": "/workspace/pos_pipeline/storage/models/550e8400.stl",
  "processing_time": 125.5,
  "stages": {
    "text_processing": {
      "processing_time": 2.3,
      "token_count": 12,
      "keywords": ["modern", "red", "white", "display", "electronics"]
    },
    "video_generation": {
      "processing_time": 95.2,
      "duration": 30,
      "file_size_mb": 15.3,
      "resolution": [512, 512]
    },
    "model_conversion": {
      "processing_time": 28.0,
      "vertex_count": 450,
      "face_count": 896,
      "file_size_mb": 1.2
    }
  },
  "created_at": "2025-10-07T10:00:00.000Z",
  "completed_at": "2025-10-07T10:02:05.500Z"
}
```

**Example**:
```bash
curl http://localhost:8000/pipeline/result/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: dev-key-change-in-production"
```

**Error Responses**:

**202 Accepted** - Job still processing
```json
{
  "detail": {
    "message": "Job is still processing",
    "stage": "video_generation",
    "progress": 45.0
  }
}
```

**404 Not Found** - Job not found
```json
{
  "detail": "Job 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

## Complete Workflow Example

### Step 1: Submit Job

```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/pipeline/process \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "text": "Modern blue POS display for beverages"
  }')

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"
```

### Step 2: Poll Status

```bash
while true; do
  STATUS=$(curl -s http://localhost:8000/pipeline/status/$JOB_ID \
    -H "X-API-Key: dev-key-change-in-production")
  
  STAGE=$(echo $STATUS | jq -r '.stage')
  PROGRESS=$(echo $STATUS | jq -r '.progress')
  
  echo "Stage: $STAGE, Progress: $PROGRESS%"
  
  if [ "$STAGE" = "completed" ]; then
    break
  fi
  
  sleep 5
done
```

### Step 3: Get Results

```bash
curl -s http://localhost:8000/pipeline/result/$JOB_ID \
  -H "X-API-Key: dev-key-change-in-production" | jq .
```

---

## Rate Limits

Current prototype has no rate limiting. Production deployment should implement:
- Rate limiting per API key
- Concurrent job limits
- Queue size limits

---

## Error Codes Summary

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Request successful |
| 202 | Accepted | Job submitted/still processing |
| 400 | Bad Request | Invalid input data |
| 403 | Forbidden | Invalid API key |
| 404 | Not Found | Job ID doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |

---

## Data Models

### PipelineInput

```typescript
{
  text: string;           // Required, 1-1024 characters
  metadata?: {            // Optional
    [key: string]: any;
  };
}
```

### PipelineOutput

```typescript
{
  job_id: string;
  status: "completed" | "failed";
  video_url: string | null;
  model_url: string | null;
  video_path: string | null;
  model_path: string | null;
  processing_time: number;
  stages: {
    text_processing: StageDetails;
    video_generation: StageDetails;
    model_conversion: StageDetails;
  };
  created_at: string;     // ISO 8601 timestamp
  completed_at: string | null;
}
```

### ProcessingStatus

```typescript
{
  job_id: string;
  stage: "queued" | "text_processing" | "video_generation" | "model_conversion" | "completed" | "failed";
  progress: number;       // 0-100
  message: string;
  created_at: string;     // ISO 8601 timestamp
  updated_at: string;     // ISO 8601 timestamp
  error: string | null;
}
```

---

## Client Libraries

### Python

See `examples/example_usage.py` for a complete Python client implementation.

Quick example:
```python
import requests

response = requests.post(
    "http://localhost:8000/pipeline/process",
    json={"text": "Modern POS display"},
    headers={"X-API-Key": "your-key"}
)
job_id = response.json()["job_id"]
```

### JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8000/pipeline/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-key'
  },
  body: JSON.stringify({
    text: 'Modern POS display',
    metadata: { category: 'electronics' }
  })
});

const { job_id } = await response.json();
```

### curl

```bash
curl -X POST http://localhost:8000/pipeline/process \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"text": "Modern POS display"}'
```

---

## Interactive Documentation

The API provides interactive documentation via Swagger UI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly
- View request/response schemas
- See example payloads

---

## Webhooks (Future)

Future versions will support webhook notifications:

```json
{
  "webhook_url": "https://your-server.com/webhook",
  "events": ["completed", "failed"]
}
```

---

## Versioning

Current API version: **1.0.0**

Version is included in all responses and can be checked via the root endpoint.

Future versions will maintain backward compatibility or use URL-based versioning:
- `/v1/pipeline/process`
- `/v2/pipeline/process`

---

## Support

For API issues or questions:
- Check the main README.md
- Review example code in `examples/`
- Consult ARCHITECTURE.md for design details
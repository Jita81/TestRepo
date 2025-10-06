# POS to 3D Pipeline - End-to-End Prototype

Transform marketing Point-of-Sale (POS) text descriptions into 3D models through automated video generation.

## 🎯 Overview

This prototype pipeline demonstrates a complete end-to-end workflow:

1. **Text Processing**: Validates and enhances marketing POS descriptions
2. **Video Generation**: Creates visual representation (30+ second video)
3. **3D Model Conversion**: Converts video to STL format 3D model

## ✨ Features

- ✅ **Complete Pipeline**: Text → Video → 3D Model
- ✅ **RESTful API**: FastAPI-based endpoints
- ✅ **Async Processing**: Non-blocking background task execution
- ✅ **Status Tracking**: Real-time pipeline execution monitoring
- ✅ **Comprehensive Testing**: Unit and integration tests
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Open Source**: Uses only open-source models and libraries

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone or navigate to the pipeline directory**:
   ```bash
   cd pipeline
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if you want to customize settings
   ```

4. **Create required directories**:
   ```bash
   mkdir -p storage/{input,output,temp} logs
   ```

### Running the Application

Start the API server:

```bash
python app.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## 📚 API Usage

### 1. Process Text to 3D Model

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A vibrant red and blue rotating display stand featuring energy drink products with bold modern graphics"
  }'
```

Response:
```json
{
  "execution_id": "exec_abc123def456",
  "status": "queued",
  "message": "Pipeline execution started",
  "status_url": "/api/v1/status/exec_abc123def456"
}
```

### 2. Check Execution Status

```bash
curl "http://localhost:8000/api/v1/status/exec_abc123def456"
```

Response:
```json
{
  "execution_id": "exec_abc123def456",
  "status": "running",
  "progress": 66,
  "current_stage": "VideoGenerator",
  "stages": [...],
  "errors": []
}
```

### 3. Get Results

```bash
curl "http://localhost:8000/api/v1/result/exec_abc123def456"
```

### 4. Download Generated Files

```bash
# Download video
curl "http://localhost:8000/api/v1/download/video/pos_video_20251006_120000.mp4" \
  --output video.mp4

# Download 3D model
curl "http://localhost:8000/api/v1/download/model/pos_model_20251006_120000.stl" \
  --output model.stl
```

## 🏗️ Architecture

### Pipeline Stages

```
┌─────────────────┐
│  Text Input     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Processor  │  - Validates input
│                 │  - Extracts keywords
│                 │  - Identifies visual elements
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Video Generator │  - Creates 30s+ video
│                 │  - Renders visual elements
│                 │  - Applies animations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Converter │  - Extracts depth from video
│                 │  - Generates 3D mesh
│                 │  - Exports to STL format
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3D Model Output│
└─────────────────┘
```

### Directory Structure

```
pipeline/
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── pytest.ini            # Test configuration
├── README.md             # This file
├── config/
│   └── config.yaml       # Pipeline configuration
├── src/
│   ├── core/             # Core pipeline components
│   │   ├── base.py       # Base classes
│   │   ├── orchestrator.py
│   │   └── status_tracker.py
│   ├── stages/           # Pipeline stages
│   │   ├── text_processor.py
│   │   ├── video_generator.py
│   │   └── model_converter.py
│   └── utils/            # Utility modules
│       ├── config_manager.py
│       ├── logger.py
│       ├── validators.py
│       └── file_handler.py
├── tests/
│   ├── unit/             # Unit tests
│   │   ├── test_text_processor.py
│   │   ├── test_video_generator.py
│   │   ├── test_model_converter.py
│   │   └── test_orchestrator.py
│   └── integration/      # Integration tests
│       ├── test_end_to_end.py
│       └── test_api.py
├── storage/
│   ├── input/            # Input files
│   ├── output/           # Generated outputs
│   └── temp/             # Temporary files
└── logs/                 # Application logs
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_text_processor.py

# With coverage
pytest --cov=src --cov-report=html
```

## 🔧 Configuration

### Configuration File

Edit `config/config.yaml` to customize:

- Storage paths
- Video generation settings (duration, FPS, resolution)
- 3D model quality
- Logging levels
- API settings

### Environment Variables

Set these in `.env` file or system environment:

- `STORAGE_BASE_PATH`: Base path for storage
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `API_HOST`: API server host
- `API_PORT`: API server port
- `PIPELINE_MAX_CONCURRENT`: Max concurrent pipeline executions

## 📊 Pipeline Stages Details

### 1. Text Processor

**Input**: Marketing POS description text

**Processing**:
- Validates text length and content
- Normalizes whitespace and formatting
- Extracts keywords using NLP techniques
- Identifies visual elements (colors, objects, actions)
- Enhances text for better video generation

**Output**: Processed text with extracted metadata

### 2. Video Generator

**Input**: Processed text and visual elements

**Processing**:
- Generates video frames based on description
- Creates animations and transitions
- Applies colors and visual elements
- Renders text overlays
- Composes final video at specified FPS

**Output**: MP4 video file (30+ seconds)

**Note**: Prototype uses procedural rendering. Production would use models like ModelScope, CogVideo, or Stable Video Diffusion.

### 3. Model Converter

**Input**: Generated video file

**Processing**:
- Extracts key frames from video
- Generates depth maps using edge detection
- Creates 3D mesh from depth information
- Triangulates surface
- Exports to binary STL format

**Output**: STL file for 3D printing/viewing

**Note**: Prototype uses depth estimation. Production would use NeRF, 3D Gaussian Splatting, or similar.

## 🛠️ Development

### Adding New Pipeline Stages

1. Create new stage class inheriting from `PipelineStage`
2. Implement required methods: `validate()` and `process()`
3. Add stage to orchestrator in `app.py`
4. Write tests in `tests/unit/`

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📈 Performance

### Prototype Specifications

- **Text Processing**: < 1 second
- **Video Generation**: 30-60 seconds (for 30s video)
- **Model Conversion**: 10-30 seconds
- **Total Pipeline**: ~1-2 minutes per execution

### Optimization Opportunities

For production deployment:

- Use ML-based text-to-video models (ModelScope, CogVideo)
- Implement GPU acceleration
- Use advanced video-to-3D models (NeRF, 3DGS)
- Add result caching
- Implement request queuing with Celery/RQ
- Deploy with load balancing

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Video file not found"
- **Solution**: Check storage directory permissions and paths

**Issue**: "Module not found"
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: "Pipeline execution failed"
- **Solution**: Check logs in `logs/pipeline.log` for detailed error messages

### Logs

Check application logs:
```bash
tail -f logs/pipeline.log
```

## 🔒 Security

- Input validation on all text inputs
- Path traversal protection for file operations
- File type validation
- Size limits on uploads and generated files
- No code execution from user input

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🎓 Future Enhancements

- [ ] Integrate production ML models (text-to-video, video-to-3D)
- [ ] Add texture mapping to 3D models
- [ ] Support multiple output formats (OBJ, FBX, GLTF)
- [ ] Implement result caching
- [ ] Add user authentication
- [ ] Create web UI for visualization
- [ ] Support batch processing
- [ ] Add quality metrics and validation
- [ ] GPU acceleration support
- [ ] Cloud deployment templates

## 📞 Support

For issues and questions:
- Check logs in `logs/pipeline.log`
- Review API documentation at `/docs`
- Run tests to verify setup: `pytest`

---

**Built with ❤️ using FastAPI, OpenCV, and Python**

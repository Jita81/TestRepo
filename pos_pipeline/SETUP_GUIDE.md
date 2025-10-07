# POS Pipeline - Setup Guide

This guide will help you set up and run the POS Display Pipeline system within 2 hours.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] pip package manager
- [ ] Git (for version control)
- [ ] 2GB+ free disk space
- [ ] Internet connection (for downloading dependencies)
- [ ] Optional: Docker & Docker Compose

## Setup Steps

### Step 1: Verify Python Installation (5 minutes)

```bash
# Check Python version
python --version  # Should be 3.11 or higher

# Check pip
pip --version
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/)

### Step 2: Navigate to Project Directory (2 minutes)

```bash
cd /workspace/pos_pipeline
```

### Step 3: Create Virtual Environment (5 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
```

### Step 4: Install Dependencies (15 minutes)

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - FastAPI and Uvicorn (API framework)
# - Pydantic (data validation)
# - OpenCV and MoviePy (video processing)
# - Trimesh (3D model processing)
# - Pytest (testing)
# - And other required packages
```

**Note**: Installation may take 10-15 minutes depending on your internet speed.

### Step 5: Configure Environment (5 minutes)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred text editor
# Minimum required changes:
# - Set a secure API_KEY (replace the default)
nano .env  # or vim .env, or code .env
```

**Important settings to review:**
```bash
API_KEY=your-secure-api-key-here  # CHANGE THIS!
LOG_LEVEL=INFO
DEBUG=False
```

### Step 6: Create Required Directories (2 minutes)

```bash
# Create storage and log directories
mkdir -p logs
mkdir -p storage/videos
mkdir -p storage/models

# Verify directories were created
ls -la
```

### Step 7: Verify Installation (10 minutes)

```bash
# Test imports
python -c "import fastapi; import cv2; import trimesh; print('All imports successful!')"

# If successful, you should see: "All imports successful!"
```

### Step 8: Run Tests (15 minutes)

```bash
# Run test suite to verify everything works
pytest -v

# Expected output: All tests should pass
# This may take 10-15 minutes on first run
```

### Step 9: Start the Application (5 minutes)

```bash
# Start the API server
python -m uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal window open while the server is running.

### Step 10: Test the API (20 minutes)

Open a **new terminal window** and test the endpoints:

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "POS Display Pipeline",
  "version": "1.0.0"
}
```

#### Test 2: Submit Pipeline Job
```bash
curl -X POST http://localhost:8000/pipeline/process \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "text": "A modern red and white POS display stand for electronics products",
    "metadata": {"category": "electronics", "brand": "TechCo"}
  }'
```

Expected response:
```json
{
  "job_id": "some-uuid-here",
  "message": "Job submitted successfully",
  "status_url": "/pipeline/status/...",
  "result_url": "/pipeline/result/..."
}
```

**Save the job_id from the response!**

#### Test 3: Check Job Status
```bash
# Replace {job_id} with the actual job ID from previous step
curl http://localhost:8000/pipeline/status/{job_id} \
  -H "X-API-Key: dev-key-change-in-production"
```

#### Test 4: Wait and Get Results

Wait 2-3 minutes for processing to complete, then:

```bash
# Replace {job_id} with your actual job ID
curl http://localhost:8000/pipeline/result/{job_id} \
  -H "X-API-Key: dev-key-change-in-production"
```

Expected response:
```json
{
  "job_id": "...",
  "status": "completed",
  "video_url": "/storage/videos/....mp4",
  "model_url": "/storage/models/....stl",
  "processing_time": 125.5,
  "stages": {...}
}
```

#### Test 5: Verify Output Files
```bash
# Check generated files
ls -lh storage/videos/
ls -lh storage/models/

# You should see:
# - .mp4 video file (~10-50 MB)
# - .stl model file (~100 KB - 5 MB)
```

### Step 11: View API Documentation (5 minutes)

Open your web browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can test all endpoints interactively from the Swagger UI.

## Alternative: Docker Setup (Faster!)

If you have Docker installed, you can skip steps 3-7:

```bash
# Navigate to project directory
cd /workspace/pos_pipeline

# Build and run with Docker Compose
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f api

# Test the API (same as Step 10 above)
curl http://localhost:8000/health
```

## Troubleshooting

### Issue: Import errors during installation

**Solution:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python -m uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8001

# Or find and kill the process using port 8000
lsof -i :8000  # Find process ID
kill -9 <PID>  # Kill the process
```

### Issue: Permission denied for storage directories

**Solution:**
```bash
chmod -R 755 storage/
chmod -R 755 logs/
```

### Issue: Tests fail

**Solution:**
```bash
# Make sure you're in the project directory
cd /workspace/pos_pipeline

# Set PYTHONPATH
export PYTHONPATH=/workspace/pos_pipeline:$PYTHONPATH

# Run tests again
pytest -v
```

### Issue: Video generation takes too long

**Note:** This is normal for the prototype. Video generation can take 1-2 minutes.
You can monitor progress:
```bash
# Check logs
tail -f logs/pipeline.log

# Or check job status via API
curl http://localhost:8000/pipeline/status/{job_id} \
  -H "X-API-Key: dev-key-change-in-production"
```

## Verification Checklist

After setup, verify:

- [ ] API server starts without errors
- [ ] Health check endpoint returns "healthy"
- [ ] Can submit a pipeline job successfully
- [ ] Job status can be retrieved
- [ ] Processing completes within 3 minutes
- [ ] Video file (.mp4) is generated
- [ ] 3D model file (.stl) is generated
- [ ] API documentation is accessible
- [ ] Tests pass successfully

## Next Steps

Now that your setup is complete:

1. **Read the README.md** for detailed usage instructions
2. **Explore the API** using Swagger UI at http://localhost:8000/docs
3. **Review the code** to understand the architecture
4. **Customize settings** in the .env file
5. **Integrate with your application** using the REST API

## Estimated Total Time

- **Without Docker**: 60-90 minutes
- **With Docker**: 30-45 minutes

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs in `logs/pipeline.log`
3. Verify all dependencies are installed
4. Ensure Python version is 3.11+
5. Check that all required directories exist

## Congratulations!

You've successfully set up the POS Display Pipeline! 🎉

The system is now ready to process text descriptions and generate 3D models.
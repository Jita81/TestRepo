# Quick Start Guide
## POS to 3D Pipeline - Get Running in 5 Minutes

---

## 🚀 Option 1: Full Stack (Recommended)

### Start Everything

```bash
cd /workspace/pipeline
docker-compose up -d
```

### Check Status

```bash
docker-compose ps
```

### Access Services

- **API**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (pipeline/pipeline_secret)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Process Your First POS Stand

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A vibrant cardboard tower display stand for premium potato chips. 180cm tall with hexagonal base, five rotating tiers in bold red and yellow colors.",
    "use_async": true,
    "priority": 5
  }'
```

### Check Job Status

```bash
# Replace JOB_ID with the ID from previous response
curl http://localhost:8000/api/v1/status/JOB_ID
```

### View Results

Results are in: `/workspace/pipeline/storage/output/`

---

## 🏃 Option 2: Quick Test (No Docker)

### Install Dependencies

```bash
cd /workspace/pipeline
pip3 install --user fastapi uvicorn numpy opencv-python pyyaml python-dotenv
```

### Run API

```bash
python3 app.py
```

### Test

Visit http://localhost:8000/docs and try the API!

---

## 📊 Monitoring

### View Metrics

```bash
curl http://localhost:8000/metrics
```

### View Circuit Breaker Status

```bash
curl http://localhost:8000/api/v1/circuit-breakers
```

### View Logs

```bash
docker-compose logs -f pipeline-api
```

---

## 🔧 Scaling

### Scale Workers

```bash
docker-compose up -d --scale pipeline-worker=5
```

### Scale API

```bash
docker-compose up -d --scale pipeline-api=3
```

---

## 🛑 Stop Everything

```bash
docker-compose down
```

---

## 📚 More Information

- **Full Documentation**: See `PRODUCTION_DEPLOYMENT.md`
- **System Overview**: See `ENHANCED_SYSTEM_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs

---

**That's it! You're ready to process POS stands at scale!** 🎉

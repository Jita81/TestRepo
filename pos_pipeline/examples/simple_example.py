"""
Simple example of using the POS Pipeline API.

This demonstrates the minimal code needed to use the pipeline.
"""
import requests
import time

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "dev-key-change-in-production"
HEADERS = {"X-API-Key": API_KEY}

# Step 1: Submit a job
print("Submitting pipeline job...")
response = requests.post(
    f"{API_URL}/pipeline/process",
    json={
        "text": "A modern red and white POS display stand for electronics",
        "metadata": {"category": "electronics"}
    },
    headers=HEADERS
)

job_data = response.json()
job_id = job_data["job_id"]
print(f"Job submitted! ID: {job_id}")

# Step 2: Wait for completion
print("Waiting for processing to complete...")
max_attempts = 60
attempt = 0

while attempt < max_attempts:
    # Check status
    status_response = requests.get(
        f"{API_URL}/pipeline/status/{job_id}",
        headers=HEADERS
    )
    status = status_response.json()
    
    print(f"Status: {status['stage']} ({status['progress']:.0f}%)")
    
    # Check if completed
    if status['stage'] == 'completed':
        break
    
    if status['stage'] == 'failed':
        print(f"Job failed: {status.get('error')}")
        exit(1)
    
    time.sleep(5)
    attempt += 1

# Step 3: Get results
print("\nGetting results...")
result_response = requests.get(
    f"{API_URL}/pipeline/result/{job_id}",
    headers=HEADERS
)

result = result_response.json()

# Step 4: Display results
print("\n" + "="*50)
print("Pipeline Completed Successfully!")
print("="*50)
print(f"Video URL: {result['video_url']}")
print(f"Model URL: {result['model_url']}")
print(f"Total processing time: {result['processing_time']:.2f} seconds")
print("\nStage breakdown:")
for stage, data in result['stages'].items():
    print(f"  {stage}: {data['processing_time']:.2f}s")
print("="*50)
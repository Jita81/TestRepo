#!/bin/bash
# Script to test the POS Pipeline end-to-end

set -e

API_URL="${API_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-dev-key-change-in-production}"

echo "Testing POS Pipeline at $API_URL"
echo "=================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "-------------------"
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
echo "Response: $HEALTH_RESPONSE"
echo ""

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi

echo ""

# Test 2: Submit Pipeline Job
echo "Test 2: Submit Pipeline Job"
echo "---------------------------"
SUBMIT_RESPONSE=$(curl -s -X POST "$API_URL/pipeline/process" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
        "text": "A modern red and white POS display stand for electronics products",
        "metadata": {"category": "electronics", "test": true}
    }')

echo "Response: $SUBMIT_RESPONSE"
echo ""

JOB_ID=$(echo "$SUBMIT_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "✗ Failed to get job ID"
    exit 1
fi

echo "✓ Job submitted successfully"
echo "Job ID: $JOB_ID"
echo ""

# Test 3: Check Status
echo "Test 3: Check Job Status"
echo "-----------------------"
STATUS_RESPONSE=$(curl -s "$API_URL/pipeline/status/$JOB_ID" \
    -H "X-API-Key: $API_KEY")

echo "Response: $STATUS_RESPONSE"
echo ""

if echo "$STATUS_RESPONSE" | grep -q "$JOB_ID"; then
    echo "✓ Status check passed"
else
    echo "✗ Status check failed"
    exit 1
fi

echo ""

# Test 4: Wait for Completion
echo "Test 4: Wait for Job Completion"
echo "-------------------------------"
echo "Waiting for job to complete (max 3 minutes)..."

MAX_ATTEMPTS=90
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    RESULT_RESPONSE=$(curl -s "$API_URL/pipeline/result/$JOB_ID" \
        -H "X-API-Key: $API_KEY")
    
    if echo "$RESULT_RESPONSE" | grep -q '"status":"completed"'; then
        echo ""
        echo "✓ Job completed successfully!"
        echo "Result: $RESULT_RESPONSE"
        echo ""
        
        # Extract URLs
        VIDEO_URL=$(echo "$RESULT_RESPONSE" | grep -o '"video_url":"[^"]*"' | cut -d'"' -f4)
        MODEL_URL=$(echo "$RESULT_RESPONSE" | grep -o '"model_url":"[^"]*"' | cut -d'"' -f4)
        
        echo "Generated Files:"
        echo "  Video: $VIDEO_URL"
        echo "  Model: $MODEL_URL"
        echo ""
        
        break
    elif echo "$RESULT_RESPONSE" | grep -q '"status":"failed"'; then
        echo ""
        echo "✗ Job failed"
        echo "Result: $RESULT_RESPONSE"
        exit 1
    fi
    
    echo -n "."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo ""
    echo "✗ Job did not complete within timeout"
    exit 1
fi

echo ""
echo "=================================="
echo "All tests passed! ✓"
echo "=================================="
# API Usage Examples

This document provides comprehensive examples for interacting with the POS Display Pipeline API.

## Table of Contents

1. [cURL Examples](#curl-examples)
2. [Python Examples](#python-examples)
3. [JavaScript Examples](#javascript-examples)
4. [Response Examples](#response-examples)
5. [Error Handling](#error-handling)

## cURL Examples

### Basic Request

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A modern retail display for energy drinks with LED backlighting"
  }'
```

### Request with Metadata

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Premium chocolate display with wooden shelves and warm lighting",
    "metadata": {
      "customer_id": "cust_12345",
      "project": "retail_q4_2025",
      "category": "confectionery"
    }
  }'
```

### Request with API Key

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "description": "Sleek beverage cooler with transparent doors and LED strips"
  }'
```

### Check Health

```bash
curl http://localhost:8000/health
```

### Check Request Status

```bash
curl http://localhost:8000/status/req_abc123def456
```

### Pretty Print JSON Response

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Modern wine display with temperature control"
  }' | jq '.'
```

### Save Response to File

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Cosmetics display with mirror and LED lighting"
  }' -o response.json
```

## Python Examples

### Basic Request

```python
import requests

url = "http://localhost:8000/generate"
data = {
    "description": "A modern retail display for energy drinks with LED backlighting"
}

response = requests.post(url, json=data)
print(response.json())
```

### Complete Example with Error Handling

```python
import requests
import time
from typing import Optional, Dict

class PipelineClient:
    """Client for POS Display Pipeline API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def generate(self, description: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Submit a generation request.
        
        Args:
            description: Text description of POS display
            metadata: Optional metadata dictionary
            
        Returns:
            Response dictionary with request_id and status
        """
        url = f"{self.base_url}/generate"
        data = {"description": description}
        if metadata:
            data["metadata"] = metadata
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            raise
    
    def check_status(self, request_id: str) -> Dict:
        """Check status of a request."""
        url = f"{self.base_url}/status/{request_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def check_health(self) -> Dict:
        """Check API health."""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        return response.json()


# Usage
if __name__ == "__main__":
    # Initialize client
    client = PipelineClient()
    
    # Check health
    health = client.check_health()
    print(f"API Health: {health['status']}")
    
    # Submit generation request
    result = client.generate(
        description="Modern wine display with wooden shelves and ambient lighting",
        metadata={
            "customer_id": "cust_001",
            "project": "retail_displays"
        }
    )
    
    print(f"Request ID: {result['request_id']}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    # Check status
    status = client.check_status(result['request_id'])
    print(f"Current Status: {status}")
```

### Async Python Example

```python
import aiohttp
import asyncio
from typing import Dict

async def submit_request(session: aiohttp.ClientSession, description: str) -> Dict:
    """Submit a generation request asynchronously."""
    url = "http://localhost:8000/generate"
    data = {"description": description}
    
    async with session.post(url, json=data) as response:
        return await response.json()

async def main():
    """Submit multiple requests concurrently."""
    descriptions = [
        "Modern energy drink display with LED backlighting",
        "Premium chocolate display with wooden shelves",
        "Sleek beverage cooler with glass doors",
        "Cosmetics display with mirror and spotlights"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [submit_request(session, desc) for desc in descriptions]
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            print(f"Request {i+1}: {result['request_id']}")

# Run
asyncio.run(main())
```

## JavaScript Examples

### Using Fetch API

```javascript
// Basic request
async function generateModel(description) {
    const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            description: description
        })
    });
    
    const data = await response.json();
    return data;
}

// Usage
generateModel('Modern wine display with LED lighting')
    .then(result => {
        console.log('Request ID:', result.request_id);
        console.log('Status:', result.status);
    })
    .catch(error => console.error('Error:', error));
```

### Complete Client Class

```javascript
class PipelineClient {
    constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        return headers;
    }
    
    async generate(description, metadata = null) {
        const url = `${this.baseUrl}/generate`;
        const body = { description };
        if (metadata) {
            body.metadata = metadata;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: this._getHeaders(),
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async checkStatus(requestId) {
        const url = `${this.baseUrl}/status/${requestId}`;
        const response = await fetch(url, {
            headers: this._getHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async checkHealth() {
        const url = `${this.baseUrl}/health`;
        const response = await fetch(url);
        return await response.json();
    }
}

// Usage
const client = new PipelineClient();

client.generate(
    'Premium chocolate display with elegant design',
    { customer_id: 'cust_001', project: 'retail_q4' }
)
.then(result => {
    console.log('Request submitted:', result.request_id);
    return client.checkStatus(result.request_id);
})
.then(status => {
    console.log('Status:', status);
})
.catch(error => {
    console.error('Error:', error);
});
```

### Using Axios

```javascript
const axios = require('axios');

const client = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add API key if needed
// client.defaults.headers.common['X-API-Key'] = 'your-api-key';

// Submit request
async function submitRequest() {
    try {
        const response = await client.post('/generate', {
            description: 'Modern retail display with LED backlighting',
            metadata: {
                customer_id: 'cust_123'
            }
        });
        
        console.log('Request ID:', response.data.request_id);
        console.log('Status:', response.data.status);
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Check status
async function checkStatus(requestId) {
    try {
        const response = await client.get(`/status/${requestId}`);
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
submitRequest()
    .then(result => checkStatus(result.request_id))
    .then(status => console.log('Current status:', status));
```

## Response Examples

### Successful Generation Request

```json
{
    "request_id": "req_a1b2c3d4e5f6",
    "status": "pending",
    "message": "Pipeline initiated successfully",
    "created_at": "2025-10-07T12:00:00.000Z"
}
```

### Health Check Response

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

### Status Check Response

```json
{
    "request_id": "req_a1b2c3d4e5f6",
    "status": "processing",
    "message": "Status tracking will be implemented with state storage"
}
```

## Error Handling

### Validation Error (422)

```json
{
    "detail": [
        {
            "loc": ["body", "description"],
            "msg": "ensure this value has at least 10 characters",
            "type": "value_error.any_str.min_length"
        }
    ]
}
```

### Invalid Input (400)

```json
{
    "detail": "Invalid characters detected in description",
    "stage": "validation"
}
```

### Service Unavailable (503)

```json
{
    "detail": "Queue service is not available"
}
```

### Python Error Handling

```python
try:
    result = client.generate("Test description")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 422:
        print("Validation error:", e.response.json())
    elif e.response.status_code == 503:
        print("Service unavailable")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### JavaScript Error Handling

```javascript
try {
    const result = await client.generate('Test description');
    console.log(result);
} catch (error) {
    if (error.response) {
        // Server responded with error status
        console.error('Status:', error.response.status);
        console.error('Data:', error.response.data);
    } else if (error.request) {
        // Request made but no response
        console.error('No response received');
    } else {
        // Error setting up request
        console.error('Error:', error.message);
    }
}
```

## Best Practices

1. **Always validate input** before sending to API
2. **Handle errors gracefully** with appropriate retry logic
3. **Store request IDs** for tracking and debugging
4. **Use timeouts** for long-running operations
5. **Implement rate limiting** to avoid overwhelming the service
6. **Log all API interactions** for debugging
7. **Use environment variables** for API URLs and keys
8. **Implement exponential backoff** for retries

## Rate Limiting Example

```python
import time
from functools import wraps

def rate_limit(max_calls: int, period: int):
    """Rate limiting decorator."""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls
            calls[:] = [call for call in calls if call > now - period]
            
            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                time.sleep(sleep_time)
            
            calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, period=60)  # 10 calls per minute
def submit_request(description):
    return client.generate(description)
```
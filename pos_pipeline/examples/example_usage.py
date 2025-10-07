"""
Example usage of the POS Pipeline API.

This script demonstrates how to use the pipeline programmatically.
"""
import asyncio
import time
import httpx
from typing import Optional


class PipelineClient:
    """Client for interacting with the POS Pipeline API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "dev-key-change-in-production"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}
    
    async def submit_job(self, text: str, metadata: Optional[dict] = None) -> str:
        """
        Submit a pipeline job.
        
        Args:
            text: Text description of POS display
            metadata: Optional metadata
            
        Returns:
            Job ID for tracking
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pipeline/process",
                json={"text": text, "metadata": metadata or {}},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data["job_id"]
    
    async def get_status(self, job_id: str) -> dict:
        """
        Get job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Status information
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pipeline/status/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_result(self, job_id: str) -> dict:
        """
        Get job result.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Pipeline output with URLs
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pipeline/result/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def wait_for_completion(self, job_id: str, max_wait: int = 300, interval: int = 5) -> dict:
        """
        Wait for job to complete.
        
        Args:
            job_id: Job identifier
            max_wait: Maximum wait time in seconds
            interval: Check interval in seconds
            
        Returns:
            Final result
            
        Raises:
            TimeoutError: If job doesn't complete within max_wait
            Exception: If job fails
        """
        elapsed = 0
        
        while elapsed < max_wait:
            status = await self.get_status(job_id)
            
            if status["stage"] == "completed":
                return await self.get_result(job_id)
            
            if status["stage"] == "failed":
                raise Exception(f"Job failed: {status.get('error', 'Unknown error')}")
            
            print(f"Status: {status['stage']} - {status['progress']}% - {status['message']}")
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        raise TimeoutError(f"Job did not complete within {max_wait} seconds")


async def example_basic_usage():
    """Example: Basic pipeline usage."""
    print("Example 1: Basic Pipeline Usage")
    print("=" * 50)
    
    # Create client
    client = PipelineClient()
    
    # Submit job
    text = "A modern red and white POS display stand for electronics products"
    print(f"Submitting job with text: {text}")
    job_id = await client.submit_job(text)
    print(f"Job submitted! ID: {job_id}")
    print()
    
    # Wait for completion
    print("Waiting for processing...")
    result = await client.wait_for_completion(job_id)
    
    # Display results
    print("\nJob completed!")
    print(f"Video URL: {result['video_url']}")
    print(f"Model URL: {result['model_url']}")
    print(f"Processing time: {result['processing_time']:.2f}s")
    print()


async def example_with_metadata():
    """Example: Pipeline with metadata."""
    print("Example 2: Pipeline with Metadata")
    print("=" * 50)
    
    client = PipelineClient()
    
    # Submit job with metadata
    text = "Blue and silver POS display for cosmetics with LED lighting"
    metadata = {
        "category": "cosmetics",
        "brand": "LuxuryBeauty",
        "target_audience": "premium",
        "features": ["LED", "rotating"]
    }
    
    print(f"Text: {text}")
    print(f"Metadata: {metadata}")
    
    job_id = await client.submit_job(text, metadata)
    print(f"Job ID: {job_id}")
    
    # Poll status manually
    print("\nPolling status every 10 seconds...")
    while True:
        status = await client.get_status(job_id)
        print(f"  {status['stage']}: {status['progress']:.1f}% - {status['message']}")
        
        if status['stage'] == 'completed':
            break
        if status['stage'] == 'failed':
            print(f"  Error: {status.get('error')}")
            break
        
        await asyncio.sleep(10)
    
    # Get final result
    if status['stage'] == 'completed':
        result = await client.get_result(job_id)
        print("\nStage Details:")
        for stage_name, stage_data in result['stages'].items():
            print(f"  {stage_name}: {stage_data}")
    print()


async def example_multiple_jobs():
    """Example: Multiple concurrent jobs."""
    print("Example 3: Multiple Concurrent Jobs")
    print("=" * 50)
    
    client = PipelineClient()
    
    # Submit multiple jobs
    jobs = [
        "Red POS display for beverages",
        "Green POS stand for organic products",
        "Black POS display for tech accessories"
    ]
    
    print("Submitting 3 jobs concurrently...")
    job_ids = []
    for text in jobs:
        job_id = await client.submit_job(text)
        job_ids.append(job_id)
        print(f"  Submitted: {job_id[:8]}... - {text}")
    
    print(f"\nWaiting for all jobs to complete...")
    
    # Wait for all jobs
    results = await asyncio.gather(*[
        client.wait_for_completion(job_id)
        for job_id in job_ids
    ])
    
    # Display results
    print("\nAll jobs completed!")
    for i, result in enumerate(results):
        print(f"\nJob {i+1}:")
        print(f"  Video: {result['video_url']}")
        print(f"  Model: {result['model_url']}")
        print(f"  Time: {result['processing_time']:.2f}s")
    print()


async def example_error_handling():
    """Example: Error handling."""
    print("Example 4: Error Handling")
    print("=" * 50)
    
    client = PipelineClient()
    
    # Try with invalid text (too short)
    try:
        print("Attempting to submit invalid text (too short)...")
        job_id = await client.submit_job("abc")
        await client.wait_for_completion(job_id)
    except httpx.HTTPStatusError as e:
        print(f"✓ Validation error caught: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
    
    print()
    
    # Try with invalid API key
    try:
        print("Attempting with invalid API key...")
        bad_client = PipelineClient(api_key="invalid-key")
        job_id = await bad_client.submit_job("Valid text for testing")
    except httpx.HTTPStatusError as e:
        print(f"✓ Authentication error caught: {e.response.status_code}")
    
    print()


async def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("POS Pipeline API - Usage Examples")
    print("=" * 50 + "\n")
    
    # Run examples
    try:
        # Example 1: Basic usage
        await example_basic_usage()
        
        # Example 2: With metadata
        await example_with_metadata()
        
        # Example 3: Multiple jobs
        await example_multiple_jobs()
        
        # Example 4: Error handling
        await example_error_handling()
        
        print("=" * 50)
        print("All examples completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure the API server is running on http://localhost:8000")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
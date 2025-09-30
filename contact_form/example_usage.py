"""
Example usage of the Contact Form API

This script demonstrates how to use the contact form API programmatically.
"""

import asyncio
import httpx
from typing import Dict, Any


class ContactFormClient:
    """Client for interacting with the Contact Form API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def submit_contact_form(
        self,
        name: str,
        email: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Submit a contact form.
        
        Args:
            name: User's full name
            email: User's email address
            message: Message content
            
        Returns:
            API response dictionary
            
        Raises:
            httpx.HTTPError: If request fails
        """
        payload = {
            "name": name,
            "email": email,
            "message": message
        }
        
        response = await self.client.post("/api/contact", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check API health.
        
        Returns:
            Health status dictionary
        """
        response = await self.client.get("/api/health")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def example_successful_submission():
    """Example: Submit a valid contact form."""
    print("\n=== Example 1: Successful Submission ===")
    
    client = ContactFormClient()
    
    try:
        result = await client.submit_contact_form(
            name="John Doe",
            email="john.doe@example.com",
            message="Hello! I would like to inquire about your services."
        )
        
        print(f"✅ Success!")
        print(f"   Submission ID: {result['submission_id']}")
        print(f"   Message: {result['message']}")
        print(f"   Timestamp: {result['timestamp']}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ Error: {e.response.status_code}")
        print(f"   {e.response.json()}")
    
    finally:
        await client.close()


async def example_validation_error():
    """Example: Handle validation errors."""
    print("\n=== Example 2: Validation Error (Short Name) ===")
    
    client = ContactFormClient()
    
    try:
        result = await client.submit_contact_form(
            name="J",  # Too short!
            email="john@example.com",
            message="This is a valid message."
        )
        
        print(f"✅ Success: {result}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ Validation Error (Expected)")
        print(f"   Status: {e.response.status_code}")
        error_data = e.response.json()
        if 'detail' in error_data:
            print(f"   Details: {error_data['detail']}")
    
    finally:
        await client.close()


async def example_invalid_email():
    """Example: Handle invalid email."""
    print("\n=== Example 3: Invalid Email ===")
    
    client = ContactFormClient()
    
    try:
        result = await client.submit_contact_form(
            name="John Doe",
            email="not-an-email",  # Invalid format!
            message="This is a valid message."
        )
        
        print(f"✅ Success: {result}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ Validation Error (Expected)")
        print(f"   Status: {e.response.status_code}")
        error_data = e.response.json()
        if 'detail' in error_data:
            for error in error_data['detail']:
                print(f"   - {error.get('msg', error)}")
    
    finally:
        await client.close()


async def example_health_check():
    """Example: Check API health."""
    print("\n=== Example 4: Health Check ===")
    
    client = ContactFormClient()
    
    try:
        health = await client.check_health()
        print(f"✅ API is {health['status']}")
        print(f"   Timestamp: {health['timestamp']}")
        
    except httpx.HTTPError as e:
        print(f"❌ Health check failed: {e}")
    
    finally:
        await client.close()


async def example_multiple_submissions():
    """Example: Submit multiple forms."""
    print("\n=== Example 5: Multiple Submissions ===")
    
    client = ContactFormClient()
    
    submissions = [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "message": "I'm interested in your product catalog."
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "message": "Can you provide more information about pricing?"
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "message": "I would like to schedule a demo of your platform."
        }
    ]
    
    try:
        for i, submission in enumerate(submissions, 1):
            result = await client.submit_contact_form(**submission)
            print(f"✅ Submission {i}: {result['submission_id']}")
        
        print(f"\nAll {len(submissions)} submissions completed successfully!")
        
    except httpx.HTTPError as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.close()


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Contact Form API - Usage Examples")
    print("=" * 60)
    
    print("\nMake sure the API server is running:")
    print("  uvicorn contact_form.api:app --reload")
    print("\n" + "=" * 60)
    
    # Run all examples
    await example_health_check()
    await example_successful_submission()
    await example_validation_error()
    await example_invalid_email()
    await example_multiple_submissions()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
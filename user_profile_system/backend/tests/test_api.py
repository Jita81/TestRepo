"""API endpoint tests."""

import pytest
from io import BytesIO
from PIL import Image


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client, test_user_data):
    """Test user registration."""
    response = client.post("/api/register", json=test_user_data)
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email."""
    client.post("/api/register", json=test_user_data)
    response = client.post("/api/register", json=test_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login(client, test_user_data):
    """Test user login."""
    client.post("/api/register", json=test_user_data)
    
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client, test_user_data):
    """Test login with invalid credentials."""
    client.post("/api/register", json=test_user_data)
    
    login_data = {
        "email": test_user_data["email"],
        "password": "WrongPassword123"
    }
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 401


def test_get_current_user_profile(authenticated_client):
    """Test getting current user's profile."""
    client, token = authenticated_client
    
    response = client.get("/api/users/me/profile")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert data["name"] == "Test User"


def test_get_user_profile_unauthorized(client):
    """Test getting profile without authentication."""
    response = client.get("/api/users/me/profile")
    assert response.status_code == 403


def test_update_profile(authenticated_client, test_user_data):
    """Test updating user profile."""
    client, token = authenticated_client
    
    # Get current profile
    profile_response = client.get("/api/users/me/profile")
    user_id = profile_response.json()["id"]
    
    # Update profile
    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com"
    }
    response = client.put(f"/api/users/{user_id}/profile", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"
    
    # Verify update
    profile_response = client.get("/api/users/me/profile")
    assert profile_response.json()["name"] == "Updated Name"
    assert profile_response.json()["email"] == "updated@example.com"


def test_update_profile_invalid_name(authenticated_client):
    """Test updating profile with invalid name."""
    client, token = authenticated_client
    
    profile_response = client.get("/api/users/me/profile")
    user_id = profile_response.json()["id"]
    
    update_data = {"name": "A"}  # Too short
    response = client.put(f"/api/users/{user_id}/profile", json=update_data)
    assert response.status_code == 422


def test_update_profile_invalid_email(authenticated_client):
    """Test updating profile with invalid email."""
    client, token = authenticated_client
    
    profile_response = client.get("/api/users/me/profile")
    user_id = profile_response.json()["id"]
    
    update_data = {"email": "invalid-email"}
    response = client.put(f"/api/users/{user_id}/profile", json=update_data)
    assert response.status_code == 422


def test_update_profile_unauthorized(authenticated_client):
    """Test updating another user's profile."""
    client, token = authenticated_client
    
    other_user_id = "different-user-id"
    update_data = {"name": "Hacker"}
    response = client.put(f"/api/users/{other_user_id}/profile", json=update_data)
    assert response.status_code == 403


def create_test_image():
    """Create a test image file."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_upload_profile_picture(authenticated_client):
    """Test uploading profile picture."""
    client, token = authenticated_client
    
    profile_response = client.get("/api/users/me/profile")
    user_id = profile_response.json()["id"]
    
    img_bytes = create_test_image()
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    
    response = client.patch(f"/api/users/{user_id}/profile/picture", files=files)
    assert response.status_code == 200
    assert "profile_picture" in response.json()["data"]


def test_upload_invalid_image_type(authenticated_client):
    """Test uploading invalid file type."""
    client, token = authenticated_client
    
    profile_response = client.get("/api/users/me/profile")
    user_id = profile_response.json()["id"]
    
    files = {"file": ("test.txt", BytesIO(b"not an image"), "text/plain")}
    response = client.patch(f"/api/users/{user_id}/profile/picture", files=files)
    assert response.status_code == 400


def test_update_settings(authenticated_client):
    """Test updating user settings."""
    client, token = authenticated_client
    
    profile_response = client.get("/api/users/me/profile")
    user_id = profile_response.json()["id"]
    
    update_data = {
        "settings": {
            "emailNotifications": False,
            "privacyLevel": "private",
            "theme": "dark"
        }
    }
    response = client.put(f"/api/users/{user_id}/profile", json=update_data)
    assert response.status_code == 200
    
    # Verify settings
    profile_response = client.get("/api/users/me/profile")
    settings = profile_response.json()["settings"]
    assert settings["emailNotifications"] == False
    assert settings["privacyLevel"] == "private"
    assert settings["theme"] == "dark"
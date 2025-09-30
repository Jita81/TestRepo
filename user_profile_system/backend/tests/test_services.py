"""Service layer tests."""

import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate, ProfileUpdateDTO, UserSettings
from fastapi import HTTPException


def test_create_user(db_session):
    """Test user creation."""
    service = UserService(db_session)
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="TestPass123"
    )
    
    user = service.create_user(user_data)
    assert user.id is not None
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.hashed_password != "TestPass123"  # Should be hashed


def test_create_user_duplicate_email(db_session):
    """Test creating user with duplicate email."""
    service = UserService(db_session)
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="TestPass123"
    )
    
    service.create_user(user_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_user(user_data)
    assert exc_info.value.status_code == 400


def test_get_user_by_id(db_session):
    """Test getting user by ID."""
    service = UserService(db_session)
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="TestPass123"
    )
    
    created_user = service.create_user(user_data)
    retrieved_user = service.get_user_by_id(created_user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


def test_get_user_by_email(db_session):
    """Test getting user by email."""
    service = UserService(db_session)
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="TestPass123"
    )
    
    service.create_user(user_data)
    retrieved_user = service.get_user_by_email("test@example.com")
    
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"


def test_update_profile(db_session):
    """Test updating user profile."""
    service = UserService(db_session)
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="TestPass123"
    )
    
    user = service.create_user(user_data)
    
    update_data = ProfileUpdateDTO(
        name="Updated Name",
        email="updated@example.com"
    )
    
    updated_user = service.update_profile(user.id, update_data)
    assert updated_user.name == "Updated Name"
    assert updated_user.email == "updated@example.com"


def test_update_profile_nonexistent_user(db_session):
    """Test updating nonexistent user."""
    service = UserService(db_session)
    update_data = ProfileUpdateDTO(name="Test")
    
    with pytest.raises(HTTPException) as exc_info:
        service.update_profile("nonexistent-id", update_data)
    assert exc_info.value.status_code == 404


def test_check_authorization(db_session):
    """Test authorization check."""
    service = UserService(db_session)
    
    assert service.check_authorization("user1", "user1") == True
    assert service.check_authorization("user1", "user2") == False
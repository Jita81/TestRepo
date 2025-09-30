"""Security utilities tests."""

import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    sanitize_html,
    sanitize_input
)
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("WrongPassword", hashed) == False


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    data = {"sub": "user123"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    
    decoded = decode_token(token)
    assert decoded["sub"] == "user123"
    assert "exp" in decoded


def test_sanitize_html():
    """Test HTML sanitization."""
    dirty_html = '<script>alert("XSS")</script><p>Hello</p>'
    clean_html = sanitize_html(dirty_html)
    
    assert '<script>' not in clean_html
    assert '<p>Hello</p>' in clean_html


def test_sanitize_input():
    """Test input sanitization."""
    dirty_input = '<script>alert("XSS")</script>Hello'
    clean_input = sanitize_input(dirty_input)
    
    assert '<script>' not in clean_input
    assert 'Hello' in clean_input
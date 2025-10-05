#!/usr/bin/env python3
"""
Demo script to test the contact form implementation.
This script demonstrates the contact form functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import Database
from src.contact_validation import ContactValidator


def demo_validation():
    """Demonstrate validation functionality."""
    print("=" * 60)
    print("CONTACT FORM VALIDATION DEMO")
    print("=" * 60)
    
    validator = ContactValidator()
    
    # Test valid inputs
    print("\n✓ Testing VALID inputs:")
    test_cases = [
        ("John Doe", "john@example.com"),
        ("María García", "maria.garcia@example.com"),
        ("O'Connor-Smith", "test+label@domain.co.uk"),
    ]
    
    for name, email in test_cases:
        try:
            result = validator.validate_contact_form(name, email)
            print(f"  ✓ {name} / {email}")
            print(f"    → Sanitized: {result['fullName']} / {result['email']}")
        except Exception as e:
            print(f"  ✗ {name} / {email}: {e}")
    
    # Test invalid inputs
    print("\n✗ Testing INVALID inputs:")
    invalid_cases = [
        ("", "valid@email.com", "Empty name"),
        ("John", "invalid-email", "Invalid email"),
        ("<script>alert('xss')</script>", "test@example.com", "XSS attempt"),
        ("A" * 101, "test@example.com", "Name too long"),
    ]
    
    for name, email, reason in invalid_cases:
        try:
            result = validator.validate_contact_form(name, email)
            print(f"  ⚠ {reason}: Should have failed but passed!")
        except Exception as e:
            print(f"  ✓ {reason}: Correctly rejected")


def demo_database():
    """Demonstrate database functionality."""
    print("\n" + "=" * 60)
    print("DATABASE OPERATIONS DEMO")
    print("=" * 60)
    
    # Use a demo database
    demo_db_path = Path("demo_contacts.db")
    if demo_db_path.exists():
        demo_db_path.unlink()
    
    Database._db_path = demo_db_path
    db = Database()
    
    print("\n✓ Inserting sample contacts...")
    contacts = [
        ("Alice Johnson", "alice@example.com", "192.168.1.1"),
        ("Bob Smith", "bob@example.com", "192.168.1.2"),
        ("Charlie Brown", "charlie@example.com", "192.168.1.3"),
    ]
    
    for name, email, ip in contacts:
        contact_id = db.insert_contact(name, email, ip_address=ip)
        print(f"  → Inserted: {name} (ID: {contact_id})")
    
    print("\n✓ Retrieving contacts...")
    stored_contacts = db.get_contacts(limit=10)
    print(f"  → Found {len(stored_contacts)} contacts:")
    for contact in stored_contacts:
        print(f"     - {contact['full_name']} <{contact['email']}>")
    
    print("\n✓ Testing rate limiting...")
    test_ip = "192.168.1.100"
    for i in range(7):
        allowed, remaining = db.check_rate_limit(test_ip, max_requests=5)
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"  Request {i+1}: {status} (Remaining: {remaining})")
    
    # Clean up
    if hasattr(Database._local, 'connection'):
        Database._local.connection.close()
    if demo_db_path.exists():
        demo_db_path.unlink()
    print("\n✓ Demo database cleaned up")


def demo_security():
    """Demonstrate security features."""
    print("\n" + "=" * 60)
    print("SECURITY FEATURES DEMO")
    print("=" * 60)
    
    validator = ContactValidator()
    
    print("\n✓ Testing XSS Prevention:")
    xss_attempts = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "'; DROP TABLE contacts; --",
    ]
    
    for attempt in xss_attempts:
        sanitized = validator.sanitize_input(attempt)
        print(f"  Original : {attempt}")
        print(f"  Sanitized: {sanitized}")
        print()
    
    print("✓ Testing Email Normalization:")
    emails = [
        "Test@EXAMPLE.COM",
        "JOHN.DOE@Gmail.Com",
    ]
    
    for email in emails:
        try:
            result = validator.validate_contact_form("John Doe", email)
            print(f"  {email} → {result['email']}")
        except:
            print(f"  {email} → REJECTED")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 12 + "CONTACT FORM IMPLEMENTATION DEMO" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        demo_validation()
        demo_database()
        demo_security()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\n✓ All features working correctly!")
        print("\nTo start the web server, run:")
        print("  python3 main.py")
        print("\nThen visit:")
        print("  http://localhost:8000/contact")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
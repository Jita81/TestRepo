"""
Database configuration and models for the contact form.
Implements secure database operations with connection pooling.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict
import threading
from pathlib import Path


class Database:
    """Thread-safe database manager with connection pooling."""
    
    _local = threading.local()
    _db_path = Path("contacts.db")
    
    def __init__(self):
        """Initialize database and create schema if it doesn't exist."""
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create database schema with proper indexes."""
        schema = """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(254) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_contacts_email 
            ON contacts(email);
        
        CREATE INDEX IF NOT EXISTS idx_contacts_created_at 
            ON contacts(created_at);
        
        -- Rate limiting table
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address VARCHAR(45) NOT NULL,
            request_count INTEGER DEFAULT 1,
            window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ip_address)
        );
        
        CREATE INDEX IF NOT EXISTS idx_rate_limits_ip 
            ON rate_limits(ip_address);
        """
        
        with self.get_connection() as conn:
            conn.executescript(schema)
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        Get a thread-local database connection.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self._db_path,
                check_same_thread=False,
                timeout=10.0
            )
            self._local.connection.row_factory = sqlite3.Row
        
        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            raise e
    
    def insert_contact(
        self,
        full_name: str,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> int:
        """
        Insert a new contact into the database.
        
        Args:
            full_name: Contact's full name (max 100 chars)
            email: Contact's email address (max 254 chars)
            ip_address: Optional IP address for tracking
            user_agent: Optional user agent string
        
        Returns:
            int: ID of the inserted record
        
        Raises:
            sqlite3.Error: If database operation fails
        """
        query = """
        INSERT INTO contacts (full_name, email, ip_address, user_agent)
        VALUES (?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (full_name, email, ip_address, user_agent))
            conn.commit()
            return cursor.lastrowid
    
    def get_contacts(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Retrieve contacts from the database.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            List of contact dictionaries
        """
        query = """
        SELECT id, full_name, email, created_at, ip_address
        FROM contacts
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
    
    def check_rate_limit(
        self,
        ip_address: str,
        max_requests: int = 5,
        window_minutes: int = 15
    ) -> tuple[bool, int]:
        """
        Check if an IP address has exceeded rate limits.
        
        Args:
            ip_address: IP address to check
            max_requests: Maximum requests allowed in window
            window_minutes: Time window in minutes
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        with self.get_connection() as conn:
            # Clean up old entries
            cleanup_query = """
            DELETE FROM rate_limits
            WHERE datetime(window_start, '+' || ? || ' minutes') < datetime('now')
            """
            conn.execute(cleanup_query, (window_minutes,))
            
            # Check current rate limit
            check_query = """
            SELECT request_count, window_start
            FROM rate_limits
            WHERE ip_address = ?
            AND datetime(window_start, '+' || ? || ' minutes') >= datetime('now')
            """
            
            cursor = conn.execute(check_query, (ip_address, window_minutes))
            row = cursor.fetchone()
            
            if row is None:
                # First request in window
                insert_query = """
                INSERT OR REPLACE INTO rate_limits (ip_address, request_count, window_start)
                VALUES (?, 1, datetime('now'))
                """
                conn.execute(insert_query, (ip_address,))
                conn.commit()
                return True, max_requests - 1
            
            request_count = row[0]
            
            if request_count >= max_requests:
                return False, 0
            
            # Increment request count
            update_query = """
            UPDATE rate_limits
            SET request_count = request_count + 1
            WHERE ip_address = ?
            """
            conn.execute(update_query, (ip_address,))
            conn.commit()
            
            return True, max_requests - request_count - 1


# Global database instance
db = Database()
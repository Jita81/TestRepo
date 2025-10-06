#!/usr/bin/env python3
"""
Simple HTTP Server for Responsive Authentication Interface

This script starts a local web server to serve the authentication interface.
Perfect for development and testing.

⚠️  SECURITY WARNING: This server is for DEVELOPMENT ONLY
   - Not suitable for production use
   - No authentication or authorization
   - Basic rate limiting only
   - For production, use a proper web server (nginx, Apache, etc.)

Usage:
    python server.py [port] [--allowed-origins ORIGINS]

Default port: 8000

Examples:
    python server.py
    python server.py 3000
    python server.py 8000 --allowed-origins http://localhost:3000,http://localhost:8080
"""

import http.server
import socketserver
import os
import sys
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

# Configuration
DEFAULT_PORT = 8000
DIRECTORY = Path(__file__).parent

# Rate limiting configuration (for development server security)
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 100  # requests per IP per window
MAX_REQUESTS_PER_SECOND = 10  # requests per IP per second


class RateLimiter:
    """Simple token bucket rate limiter for development server"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked = {}
    
    def is_allowed(self, ip_address):
        """Check if request from IP is allowed"""
        now = datetime.now()
        
        # Check if IP is temporarily blocked
        if ip_address in self.blocked:
            if now < self.blocked[ip_address]:
                return False, "Rate limit exceeded. Try again later."
            else:
                del self.blocked[ip_address]
        
        # Clean old requests
        self.requests[ip_address] = [
            req_time for req_time in self.requests[ip_address]
            if now - req_time < timedelta(seconds=RATE_LIMIT_WINDOW)
        ]
        
        # Check rate limits
        recent_requests = self.requests[ip_address]
        
        # Check per-second limit
        last_second = [
            req_time for req_time in recent_requests
            if now - req_time < timedelta(seconds=1)
        ]
        if len(last_second) >= MAX_REQUESTS_PER_SECOND:
            self.blocked[ip_address] = now + timedelta(seconds=10)
            return False, "Too many requests per second. Blocked for 10 seconds."
        
        # Check per-window limit
        if len(recent_requests) >= MAX_REQUESTS_PER_WINDOW:
            self.blocked[ip_address] = now + timedelta(seconds=60)
            return False, f"Too many requests. Blocked for 60 seconds."
        
        # Allow request and record it
        self.requests[ip_address].append(now)
        return True, None


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with security features for development"""
    
    # Class-level rate limiter shared across all requests
    rate_limiter = RateLimiter()
    allowed_origins = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def do_GET(self):
        """Handle GET requests with rate limiting"""
        if not self.check_rate_limit():
            return
        super().do_GET()
    
    def do_POST(self):
        """Handle POST requests with rate limiting"""
        if not self.check_rate_limit():
            return
        super().do_POST()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        if not self.check_rate_limit():
            return
        self.send_response(200)
        self.end_headers()
    
    def check_rate_limit(self):
        """Check rate limit for current request"""
        client_ip = self.client_address[0]
        allowed, message = self.rate_limiter.is_allowed(client_ip)
        
        if not allowed:
            self.send_error(429, f"Too Many Requests: {message}")
            self.log_message(f"Rate limit exceeded for {client_ip}: {message}")
            return False
        
        return True
    
    def end_headers(self):
        """Add security headers"""
        # CORS configuration - restricted to allowed origins
        origin = self.headers.get('Origin', '')
        
        if self.allowed_origins:
            # Production-like: Only allow specific origins
            if origin in self.allowed_origins:
                self.send_header('Access-Control-Allow-Origin', origin)
            else:
                # For development, allow localhost origins only
                if origin.startswith('http://localhost') or origin.startswith('http://127.0.0.1'):
                    self.send_header('Access-Control-Allow-Origin', origin)
        else:
            # Default: Allow localhost only (safer than '*')
            if origin.startswith('http://localhost') or origin.startswith('http://127.0.0.1'):
                self.send_header('Access-Control-Allow-Origin', origin)
            elif not origin:
                # Same-origin requests (direct browser access)
                self.send_header('Access-Control-Allow-Origin', 'http://localhost:8000')
        
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        
        # Security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        
        # Content Security Policy for development
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Allow inline scripts for demos
            "style-src 'self' 'unsafe-inline'; "   # Allow inline styles
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self'"
        )
        self.send_header('Content-Security-Policy', csp)
        
        # Development server identification
        self.send_header('X-Server-Type', 'Development')
        
        super().end_headers()
    
    def log_message(self, format, *args):
        """Custom log format with timestamp and client IP"""
        client_ip = self.client_address[0]
        timestamp = self.log_date_time_string()
        sys.stdout.write(f"[{timestamp}] {client_ip} - {format % args}\n")


def find_free_port(start_port=DEFAULT_PORT, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socketserver.TCPServer(("", port), None) as s:
                return port
        except OSError:
            continue
    return None


def main():
    """Start the web server"""
    # Parse command line arguments
    port = DEFAULT_PORT
    allowed_origins = []
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--allowed-origins':
            if i + 1 < len(sys.argv):
                allowed_origins = [origin.strip() for origin in sys.argv[i + 1].split(',')]
                i += 2
            else:
                print("Error: --allowed-origins requires a comma-separated list of origins")
                print(f"Usage: python {sys.argv[0]} [port] [--allowed-origins ORIGINS]")
                sys.exit(1)
        elif arg == '--help' or arg == '-h':
            print(__doc__)
            sys.exit(0)
        else:
            try:
                port = int(arg)
                i += 1
            except ValueError:
                print(f"Error: Invalid argument '{arg}'")
                print(f"Usage: python {sys.argv[0]} [port] [--allowed-origins ORIGINS]")
                sys.exit(1)
    
    # Set allowed origins on handler class
    AuthHandler.allowed_origins = allowed_origins
    
    # Find free port if specified port is busy
    free_port = find_free_port(port)
    if free_port is None:
        print(f"Error: Could not find a free port starting from {port}")
        sys.exit(1)
    
    if free_port != port:
        print(f"Warning: Port {port} is busy, using port {free_port} instead")
        port = free_port
    
    # Create server
    try:
        with socketserver.TCPServer(("127.0.0.1", port), AuthHandler) as httpd:
            print("\n" + "="*60)
            print("🚀 Responsive Authentication Interface Server")
            print("="*60)
            print(f"\n⚠️  DEVELOPMENT SERVER - NOT FOR PRODUCTION USE")
            print(f"\n✅ Server running at: http://localhost:{port}/")
            print(f"\n🔒 Security Features (Development):")
            print(f"   • Rate limiting: {MAX_REQUESTS_PER_WINDOW} requests per {RATE_LIMIT_WINDOW}s")
            print(f"   • Burst protection: {MAX_REQUESTS_PER_SECOND} requests per second")
            print(f"   • CORS: localhost origins only")
            if allowed_origins:
                print(f"   • Additional origins: {', '.join(allowed_origins)}")
            print(f"   • Security headers enabled")
            print(f"   • CSP enabled")
            print(f"\n📄 Available pages:")
            print(f"   • Home:         http://localhost:{port}/templates/index.html")
            print(f"   • Login:        http://localhost:{port}/templates/login.html")
            print(f"   • Register:     http://localhost:{port}/templates/register.html")
            print(f"   • Dashboard:    http://localhost:{port}/templates/dashboard.html")
            print(f"   • Test Suite:   http://localhost:{port}/tests/test_responsive.html")
            print(f"\n💡 Tips:")
            print(f"   • Press Ctrl+C to stop the server")
            print(f"   • Test on mobile: Use your device's browser with your computer's IP")
            print(f"   • Use browser DevTools to simulate different devices")
            print(f"\n⚠️  For production deployment:")
            print(f"   • Use a proper web server (nginx, Apache, Caddy)")
            print(f"   • Implement proper authentication & authorization")
            print(f"   • Use HTTPS/TLS")
            print(f"   • Configure production-grade rate limiting")
            print(f"   • Set up proper logging and monitoring")
            print("\n" + "="*60 + "\n")
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

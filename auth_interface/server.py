#!/usr/bin/env python3
"""
Simple HTTP Server for Responsive Authentication Interface

This script starts a local web server to serve the authentication interface.
Perfect for development and testing.

Usage:
    python server.py [port]

Default port: 8000
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
DEFAULT_PORT = 8000
DIRECTORY = Path(__file__).parent


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and directory handling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        """Add custom headers"""
        # Enable CORS for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        
        super().end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


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
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid port number '{sys.argv[1]}'")
            print(f"Usage: python {sys.argv[0]} [port]")
            sys.exit(1)
    else:
        port = DEFAULT_PORT
    
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
        with socketserver.TCPServer(("", port), AuthHandler) as httpd:
            print("\n" + "="*60)
            print("🚀 Responsive Authentication Interface Server")
            print("="*60)
            print(f"\n✅ Server running at: http://localhost:{port}/")
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

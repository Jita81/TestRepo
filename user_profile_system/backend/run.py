"""Script to run the backend server."""

import uvicorn
from app.db.database import init_db

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    
    # Run the server
    print("Starting server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
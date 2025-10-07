from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import os
import json
from pathlib import Path

app = FastAPI(title="Generated App")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main application interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run")
async def run_application():
    """Run the underlying application."""
    try:
        # Try to run the main application
        result = subprocess.run(
            ["python", "main.py"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/status")
async def get_status():
    """Get application status."""
    return {"status": "running", "message": "Application is ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

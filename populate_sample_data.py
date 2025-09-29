"""
Helper script to populate sample data for dashboard demonstration.
This can be imported and called to add sample conversions.
"""

from datetime import datetime, timedelta
import uuid
import random

def get_sample_conversions():
    """Generate sample conversion data for dashboard demonstration."""
    sample_repos = [
        {
            "github_url": "https://github.com/octocat/Hello-World",
            "repo_name": "Hello-World",
            "platform": "web",
            "status": "success"
        },
        {
            "github_url": "https://github.com/tiangolo/fastapi",
            "repo_name": "fastapi",
            "platform": "docker",
            "status": "success"
        },
        {
            "github_url": "https://github.com/pallets/flask",
            "repo_name": "flask",
            "platform": "executable",
            "status": "success"
        },
        {
            "github_url": "https://github.com/django/django",
            "repo_name": "django",
            "platform": "web",
            "status": "failed"
        },
        {
            "github_url": "https://github.com/torvalds/linux",
            "repo_name": "linux",
            "platform": "docker",
            "status": "failed"
        },
        {
            "github_url": "https://github.com/microsoft/vscode",
            "repo_name": "vscode",
            "platform": "executable",
            "status": "processing"
        },
        {
            "github_url": "https://github.com/facebook/react",
            "repo_name": "react",
            "platform": "web",
            "status": "success"
        },
        {
            "github_url": "https://github.com/vuejs/vue",
            "repo_name": "vue",
            "platform": "docker",
            "status": "success"
        }
    ]
    
    conversions = []
    
    for i, repo in enumerate(sample_repos):
        conversion_id = str(uuid.uuid4())
        
        # Create dates with decreasing timestamps
        date = datetime.now() - timedelta(hours=i*2, minutes=random.randint(0, 59))
        
        conversion = {
            "id": conversion_id,
            "github_url": repo["github_url"],
            "repo_name": repo["repo_name"],
            "platform": repo["platform"],
            "status": repo["status"],
            "date": date.isoformat(),
            "app_name": f"{repo['repo_name']}_app",
            "download_url": f"/download/{repo['repo_name']}_app" if repo["status"] == "success" else None,
            "error_message": "Build failed: Missing dependencies" if repo["status"] == "failed" else None
        }
        
        conversions.append(conversion)
    
    return conversions

def populate_sample_data(conversions_storage):
    """Populate the conversions storage with sample data."""
    sample_data = get_sample_conversions()
    conversions_storage.extend(sample_data)
    return len(sample_data)
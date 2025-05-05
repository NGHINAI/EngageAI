from celery import Celery
from .db import SessionLocal
from .models import PlatformIntegration, MonitoringProfile
from datetime import datetime, timedelta
import httpx
import os

app = Celery("engageai", broker="redis://localhost:6379/0")

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@app.task
def check_for_new_posts():
    """Periodic task to check for new posts on monitored platforms"""
    db = SessionLocal()
    try:
        # Get active monitoring profiles
        profiles = db.query(MonitoringProfile).filter(MonitoringProfile.is_active == True).all()
        
        for profile in profiles:
            # Get corresponding platform integration
            integration = db.query(PlatformIntegration)\n                .filter(PlatformIntegration.id == profile.integration_id)\n                .filter(PlatformIntegration.is_active == True)\n                .first()
            
            if integration:
                if integration.platform == "linkedin":
                    _check_linkedin_posts(db, integration, profile)
    finally:
        db.close()

def _check_linkedin_posts(db, integration, profile):
    """Check for new LinkedIn posts matching monitoring criteria"""
    posts_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {"Authorization": f"Bearer {integration.access_token}"}
    params = {"keywords": profile.keywords}
    
    try:
        response = httpx.get(posts_url, headers=headers, params=params)
        if response.status_code == 200:
            posts = response.json().get("elements", [])
            for post in posts:
                # Process new posts and generate comments
                _process_linkedin_post(db, integration, profile, post)
    except Exception as e:
        print(f"Error checking LinkedIn posts: {e}")
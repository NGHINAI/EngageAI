from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import httpx

from ..db import get_db
from ..models import PlatformIntegration
from ..schemas import MonitoringProfileCreate, MonitoringProfile

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

@router.post("/profiles", response_model=MonitoringProfile)
def create_monitoring_profile(profile: MonitoringProfileCreate, db: Session = Depends(get_db)):
    # Create a new monitoring profile in database
    db_profile = MonitoringProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/profiles", response_model=List[MonitoringProfile])
def get_monitoring_profiles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Get all monitoring profiles
    profiles = db.query(MonitoringProfile).offset(skip).limit(limit).all()
    return profiles

@router.get("/linkedin/posts")
async def get_linkedin_posts(integration_id: int, db: Session = Depends(get_db)):
    # Get LinkedIn integration from database
    integration = db.query(PlatformIntegration).filter(PlatformIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Get recent posts from LinkedIn API
    posts_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {"Authorization": f"Bearer {integration.access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(posts_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get posts")
        
        return response.json()

@router.post("/linkedin/comment")
async def create_linkedin_comment(
    post_id: str, 
    comment: str, 
    integration_id: int, 
    db: Session = Depends(get_db)
):
    # Get LinkedIn integration from database
    integration = db.query(PlatformIntegration).filter(PlatformIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Post comment to LinkedIn
    comment_url = f"https://api.linkedin.com/v2/socialActions/{post_id}/comments"
    headers = {"Authorization": f"Bearer {integration.access_token}"}
    data = {"actor": "urn:li:person:{integration.user_id}", "message": {"text": comment}}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(comment_url, json=data, headers=headers)
        if response.status_code != 201:
            raise HTTPException(status_code=400, detail="Failed to post comment")
        
        return {"status": "success", "comment_id": response.json().get("id")}
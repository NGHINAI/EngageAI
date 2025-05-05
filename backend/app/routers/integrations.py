from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import httpx
import os

from ..db import get_db
from ..models import PlatformIntegration
from ..schemas import PlatformIntegrationCreate

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/linkedin/callback")
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

@router.get("/linkedin/connect")
def connect_linkedin():
    # Generate LinkedIn OAuth URL
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": "random_state_string",
        "scope": "r_liteprofile r_emailaddress w_member_social"
    }
    auth_url = f"{LINKEDIN_AUTH_URL}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
    return RedirectResponse(url=auth_url)

@router.get("/linkedin/callback")
async def linkedin_callback(code: str, state: str, db: Session = Depends(get_db)):
    # Exchange code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(LINKEDIN_TOKEN_URL, data=token_data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_response = response.json()
        expires_in = token_response.get("expires_in", 5184000)  # Default 60 days
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Save integration to database
        integration = PlatformIntegrationCreate(
            platform="linkedin",
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token"),
            expires_at=expires_at,
            is_active=True
        )
        db_integration = PlatformIntegration(**integration.dict())
        db.add(db_integration)
        db.commit()
        db.refresh(db_integration)
        
        return {"status": "success", "integration_id": db_integration.id}

@router.get("/linkedin/profile")
async def get_linkedin_profile(integration_id: int, db: Session = Depends(get_db)):
    # Get integration from database
    integration = db.query(PlatformIntegration).filter(PlatformIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Get profile data from LinkedIn API
    profile_url = "https://api.linkedin.com/v2/me"
    headers = {"Authorization": f"Bearer {integration.access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(profile_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get profile data")
        
        return response.json()
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PlatformIntegrationBase(BaseModel):
    platform: str
    is_active: bool

class PlatformIntegrationCreate(PlatformIntegrationBase):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

class PlatformIntegration(PlatformIntegrationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
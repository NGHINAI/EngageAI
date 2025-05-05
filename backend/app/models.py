from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .db import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PlatformIntegration(Base):
    __tablename__ = 'platform_integrations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform = Column(String(20), nullable=False)  # 'linkedin', 'reddit', 'twitter'
    access_token = Column(String(512), nullable=False)
    refresh_token = Column(String(512), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
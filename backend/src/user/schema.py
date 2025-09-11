from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class User(Document):
    """User document schema for MongoDB using Beanie."""
    
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    email: str = Field(..., description="User's email address")
    profile_url: Optional[str] = Field(None, description="URL to user's profile picture")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when user was created")
    
    class Settings:
        name = "users"  # MongoDB collection name
        
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "profile_url": "https://example.com/profile.jpg",
                "created_at": "2025-09-11T10:30:00"
            }
        }


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    email: str = Field(..., description="User's email address")
    profile_url: Optional[str] = Field(None, description="URL to user's profile picture")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's last name")
    email: Optional[str] = Field(None, description="User's email address")
    profile_url: Optional[str] = Field(None, description="URL to user's profile picture")


class UserResponse(BaseModel):
    """Schema for user response."""
    
    id: str = Field(..., description="User's unique identifier")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    email: str = Field(..., description="User's email address")
    profile_url: Optional[str] = Field(None, description="URL to user's profile picture")
    created_at: datetime = Field(..., description="Timestamp when user was created")
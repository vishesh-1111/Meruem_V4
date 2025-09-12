from beanie import Document, Link, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from pymongo import IndexModel
from src.user.schema import User


class WorkspaceMember(BaseModel):
    user_id: Link[User]
    is_admin: bool = Field(default=False)


class Workspace(Document):
    name: str = Field(..., description="Name of the workspace")
    members: List[WorkspaceMember] = Field(default_factory=list, description="List of workspace members")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when workspace was created")
    created_by: Link[User] = Field(..., description="User who created the workspace")

    
    class Settings:
        name = "workspaces"
        indexes = [
            IndexModel(
                [("created_by", 1), ("name", 1)], 
                unique=True,
                name="unique_admin_workspace_name"
            )
        ]
        
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Workspace",
                "members": [
                    {
                        "user_id": "60d5f4832f8fb814c56fa181",
                        "is_admin": True
                    }
                ],
                "created_by": "60d5f4832f8fb814c56fa181"
            }
        }


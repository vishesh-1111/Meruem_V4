from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel
from src.user.schema import User
from src.workspace.schema import Workspace
from src.connections.schema import Connection


class Chat(Document):
    """Chat document"""
    name: str = Field(..., description="Name of the chat")
    created_by: Link[User] = Field(..., description="User who created the chat")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when chat was created")
    workspace_id: Link[Workspace] = Field(..., description="Workspace this chat belongs to")
    connection_id: Link[Connection] = Field(..., description="Database connection used for this chat")

    class Settings:
        name = "chats"
        indexes = [
            # Index for efficient querying by workspace
            IndexModel(
                [("workspace_id", 1), ("created_at", -1)], 
                name="workspace_chats_by_date"
            ),
            # Index for efficient querying by connection
            IndexModel(
                [("connection_id", 1), ("created_at", -1)], 
                name="connection_chats_by_date"
            ),
            # Index for efficient querying by creator
            IndexModel(
                [("created_by", 1), ("created_at", -1)], 
                name="user_chats_by_date"
            ),
            # Ensure unique chat names within a workspace
            IndexModel(
                [("workspace_id", 1), ("name", 1)], 
                unique=True,
                name="unique_chat_name_per_workspace"
            )
        ]
        
    class Config:
        json_schema_extra = {
            "example": {
                "name": "General Discussion",
                "created_by": "60d5f4832f8fb814c56fa181",
                "workspace_id": "68b954f1146c5b9a3c56c1b7",
                "connection_id": "60d5f4832f8fb814c56fa182"
            }
        }
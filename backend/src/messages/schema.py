from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from typing import Dict, Any
from enum import Enum
from pymongo import IndexModel
from src.chats.schema import Chat


class MessageRole(str, Enum):
    """Enum for message roles"""
    ASSISTANT = "assistant"
    USER = "user"


class Message(Document):
    """Message document"""
    chat_id: Link[Chat] = Field(..., description="Chat this message belongs to")
    role: MessageRole = Field(..., description="Role of the message sender (assistant or user)")
    content: Dict[str, Any] = Field(..., description="Flexible content dictionary containing message data")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when message was created")

    class Settings:
        name = "messages"
        indexes = [
            # Index for efficient querying by chat and creation time
            IndexModel(
                [("chat_id", 1), ("created_at", 1)], 
                name="chat_messages_by_date"
            ),
            # Index for efficient querying by role within a chat
            IndexModel(
                [("chat_id", 1), ("role", 1), ("created_at", 1)], 
                name="chat_messages_by_role_and_date"
            )
        ]
        
    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "60d5f4832f8fb814c56fa181",
                "role": "user",
                "content": {
                    "text": "Hello, can you help me with this query?",
                    "metadata": {
                        "client": "web",
                        "timestamp": "2025-09-19T10:30:00"
                    }
                },
                "created_at": "2025-09-19T10:30:00"
            }
        }

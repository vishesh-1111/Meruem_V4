from pydantic import BaseModel
from datetime import datetime


# Request models
class CreateChatRequest(BaseModel):
    name: str


# Response models
class ChatResponse(BaseModel):
    id: str
    name: str
    created_by: str
    createdAt: datetime
    workspace_id: str
    connection_id: str
    
    class Config:
        from_attributes = True

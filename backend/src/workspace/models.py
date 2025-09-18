from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

from .schema import WorkspaceMember


# Request models
class CreateWorkspaceRequest(BaseModel):
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Workspace name must be between 2 and 100 characters"
    )
    
    @validator('name')
    def validate_name(cls, v):
        if v is None:
            raise ValueError('Workspace name is required')
        
        # Strip whitespace
        v = v.strip()
        
        if not v:
            raise ValueError('Workspace name cannot be empty or contain only whitespace')
        
        # Additional validation for special characters if needed
        if len(v) < 2:
            raise ValueError('Workspace name must be at least 2 characters long')
        
        if len(v) > 100:
            raise ValueError('Workspace name cannot exceed 100 characters')
        
        return v


class AddMemberRequest(BaseModel):
    email: str


class UpdateWorkspaceRequest(BaseModel):
    name: str


# Response models
class WorkspaceResponse(BaseModel):
    id: str
    name: str
    members: List[WorkspaceMember]
    created_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True


class UserDataResponse(BaseModel):
    first_name: str
    last_name: str
    profile_url: str = None
    email :str
    
    class Config:
        from_attributes = True


class WorkspaceDataResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True


class ConnectionDataResponse(BaseModel):
    connection_name: str
    connection_driver: str
    connection_id: str
    
    class Config:
        from_attributes = True


class ChatDataResponse(BaseModel):
    chat_name: str
    chat_id: str
    
    class Config:
        from_attributes = True


class WorkspaceDataFullResponse(BaseModel):
    user: UserDataResponse
    workspaces: List[WorkspaceDataResponse]
    connections: List[ConnectionDataResponse]
    chats: List[ChatDataResponse]
    
    class Config:
        from_attributes = True


class NewWorkspaceDataResponse(BaseModel):
    currentWorkspace: WorkspaceDataResponse
    user: UserDataResponse
    workspaces: List[WorkspaceDataResponse]
    
    class Config:
        from_attributes = True

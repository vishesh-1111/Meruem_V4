from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from src.user.schema import User
from src.auth.current_user import current_active_user
from .schema import Workspace, WorkspaceMember


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


router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.post("/create", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: CreateWorkspaceRequest,
    current_user: User = Depends(current_active_user)
):
    
    print(current_user)
    """
    Create a new workspace.
    
    - **name**: Name of the workspace
    
    The current user is automatically added as an admin member and set as the creator.
    """
    try:
        # Validate workspace data is present
        if workspace_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace data is required"
            )
        
        # Validate name is present and not empty
        if not hasattr(workspace_data, 'name'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace name is required"
            )
        
        if not workspace_data.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace name cannot be empty"
            )
        
        # Validate name format and length
        workspace_name = workspace_data.name.strip()
        if not workspace_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace name cannot be empty or contain only whitespace"
            )
        
        if len(workspace_name) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace name must be at least 2 characters long"
            )
        
        if len(workspace_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace name cannot exceed 100 characters"
            )
        
        # Validate current user
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user: User ID is missing"
            )
        
        # Add current user as admin
        print(current_user.id)
        current_user_member = WorkspaceMember(
            user_id=current_user.id,
            is_admin=True
        )
        
        # Create workspace

        print(workspace_name,current_user_member,current_user.id)
        workspace = Workspace(
            name=workspace_name,
            members=[current_user_member],
            created_by=current_user.id,
            created_at=datetime.now()
        )
        
        # Save to database
        await workspace.insert()
        
        # Return response
        return WorkspaceResponse(
            id=str(workspace.id),
            name=workspace.name,
            members=workspace.members,
            created_at=workspace.created_at,
            created_by=str(workspace.created_by.ref.id)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have a workspace named '{workspace_data.name if workspace_data and hasattr(workspace_data, 'name') else 'Unknown'}'. Please choose a different name."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except AttributeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace: {str(e)}"
        )


@router.post("/{workspace_id}/add-member", response_model=WorkspaceResponse)
async def add_member_to_workspace(
    workspace_id: str,
    member_data: AddMemberRequest,
    current_user: User = Depends(current_active_user)
):
    """
    Add a member to a workspace.
    
    - **workspace_id**: ID of the workspace
    - **email**: Email of the user to add as a member
    
    Only admin members can add new members. New members are added as non-admin by default.
    """
    try:
        # Convert workspace_id to ObjectId
        workspace_object_id = PydanticObjectId(workspace_id)
        
        # Get the workspace and check if current user is a member
        workspace = await Workspace.find_one(
            Workspace.id == workspace_object_id,
            Workspace.members.user_id.id == current_user.id
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you are not a member of this workspace"
            )
        
        # Check if current user is an admin
        current_user_member = None
        for member in workspace.members:
            if member.user_id.ref.id == current_user.id:
                current_user_member = member
                break
        
        if not current_user_member or not current_user_member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can add members"
            )
        
        # Find user by email
        user_to_add = await User.find_one(User.email == member_data.email)
        if not user_to_add:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{member_data.email}' not found"
            )
        
        # Check if user is already a member
        for member in workspace.members:
            if member.user_id.ref.id == user_to_add.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User '{member_data.email}' is already a member of this workspace"
                )
        
        # Add user as non-admin member
        new_member = WorkspaceMember(
            user_id=user_to_add.id,
            is_admin=False
        )
        workspace.members.append(new_member)
        
        # Save the updated workspace
        await workspace.save()
        
        # Return response
        return WorkspaceResponse(
            id=str(workspace.id),
            name=workspace.name,
            members=workspace.members,
            created_at=workspace.created_at,
            created_by=str(workspace.created_by.ref.id)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid workspace ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add member to workspace: {str(e)}"
        )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_data: UpdateWorkspaceRequest,
    current_user: User = Depends(current_active_user)
):
    """
    Update a workspace name.
    
    - **workspace_id**: ID of the workspace to update
    - **name**: New name for the workspace
    
    Only admin members can update the workspace name.
    """
    try:
        # Convert workspace_id to ObjectId
        workspace_object_id = PydanticObjectId(workspace_id)
        
        # Get the workspace and check if current user is a member
        workspace = await Workspace.find_one(
            Workspace.id == workspace_object_id,
            Workspace.members.user_id.id == current_user.id
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you are not a member of this workspace"
            )
        
        # Check if current user is an admin
        current_user_member = None
        for member in workspace.members:
            if member.user_id.ref.id == current_user.id:
                current_user_member = member
                break
        
        if not current_user_member or not current_user_member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can update the workspace"
            )
        
        # Update the workspace name
        workspace.name = workspace_data.name
        
        # Save the updated workspace
        await workspace.save()
        
        # Return response
        return WorkspaceResponse(
            id=str(workspace.id),
            name=workspace.name,
            members=workspace.members,
            created_at=workspace.created_at,
            created_by=str(workspace.created_by.ref.id)
        )
        
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have a workspace named '{workspace_data.name}'. Please choose a different name."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid workspace ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workspace: {str(e)}"
        )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Delete a workspace.
    
    - **workspace_id**: ID of the workspace to delete
    
    Only admin members can delete the workspace.
    """
    try:
        # Convert workspace_id to ObjectId
        workspace_object_id = PydanticObjectId(workspace_id)
        
        # Get the workspace and check if current user is a member
        workspace = await Workspace.find_one(
            Workspace.id == workspace_object_id,
            Workspace.members.user_id.id == current_user.id
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you are not a member of this workspace"
            )
        
        # Check if current user is an admin
        current_user_member = None
        for member in workspace.members:
            if member.user_id.ref.id == current_user.id:
                current_user_member = member
                break
        
        if not current_user_member or not current_user_member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can delete the workspace"
            )
        
        # Delete the workspace
        await workspace.delete()
        
        # Return 204 No Content status (successful deletion)
        return
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid workspace ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workspace: {str(e)}"
        )    
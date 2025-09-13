from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from src.user.schema import User
from src.user.services import check_user_exists
from ..auth.services import get_current_user, current_active_user
from .schema import Workspace, WorkspaceMember
from .models import CreateWorkspaceRequest, AddMemberRequest, UpdateWorkspaceRequest, WorkspaceResponse
from .services import get_user_role_in_workspace, check_user_already_member, UserRole


router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.post("/create", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: CreateWorkspaceRequest,
    request: Request
):
    
    current_user_id = get_current_user(request)
    """
    Create a new workspace.
    
    - **name**: Name of the workspace
    
    The current user is automatically added as an admin member and set as the creator.
    """
    try:
        workspace_name = workspace_data.name.strip()
        
        current_user_member = WorkspaceMember(
            user_id=PydanticObjectId(current_user_id),
            is_admin=True
        )
        
        # Create workspace

        print(workspace_name,current_user_member,current_user_id)
        workspace = Workspace(
            name=workspace_name,
            members=[current_user_member],
            created_by=PydanticObjectId(current_user_id),
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
        # Check if current user is an admin in this workspace
        current_user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
        if current_user_role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can add members"
            )
        
        # Check if user to add exists and is registered
        user_to_add = await check_user_exists(member_data.email)
        
        # Check if user is already a member
        is_already_member = await check_user_already_member(workspace_id, str(user_to_add.id))
        if is_already_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{member_data.email}' is already a member of this workspace"
            )
        
        # Get the workspace to add the member
        workspace_object_id = PydanticObjectId(workspace_id)
        workspace = await Workspace.find_one(Workspace.id == workspace_object_id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
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
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
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
        # Check if current user is an admin in this workspace
        current_user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
        if current_user_role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can update the workspace"
            )
        
        # Get the workspace to update
        workspace_object_id = PydanticObjectId(workspace_id)
        workspace = await Workspace.find_one(Workspace.id == workspace_object_id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
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
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
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
        # Check if current user is an admin in this workspace
        current_user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
        if current_user_role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace admins can delete the workspace"
            )
        
        # Get the workspace to delete
        workspace_object_id = PydanticObjectId(workspace_id)
        workspace = await Workspace.find_one(Workspace.id == workspace_object_id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Delete the workspace
        await workspace.delete()
        
        # Return 204 No Content status (successful deletion)
        return
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workspace: {str(e)}"
        )    
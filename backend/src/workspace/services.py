from fastapi import HTTPException, status
from beanie import PydanticObjectId
from typing import Optional, Literal
from enum import Enum

from .schema import Workspace
from src.user.schema import User


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


async def get_user_role_in_workspace(workspace_id: str, user_id: str) -> UserRole:
    """
    Get the role of a user in a workspace.
    
    Args:
        workspace_id: The workspace ID
        user_id: The user ID to check
        
    Returns:
        UserRole: The role of the user (admin or member)
        
    Raises:
        HTTPException: 
            - 400: Invalid workspace ID format
            - 404: Workspace not found or user not found in workspace
            - 500: Internal server error
    """
    try:
        # Convert workspace_id to ObjectId
        workspace_object_id = PydanticObjectId(workspace_id)
        user_object_id = PydanticObjectId(user_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {str(e)}"
        )
    
    try:
        # Find the workspace
        workspace = await Workspace.find_one(Workspace.id == workspace_object_id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user is a member of the workspace
        for member in workspace.members:
            if member.user_id.ref.id == user_object_id:
                return UserRole.ADMIN if member.is_admin else UserRole.MEMBER
        
        # User not found in workspace
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this workspace"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user role in workspace: {str(e)}"
        )


async def check_user_already_member(workspace_id: str, user_id: str) -> bool:
    """
    Check if a user is already a member of a workspace.
    
    Args:
        workspace_id: The workspace ID
        user_id: The user ID to check
        
    Returns:
        bool: True if user is already a member, False otherwise
        
    Raises:
        HTTPException:
            - 400: Invalid ID format
            - 404: Workspace not found
            - 500: Internal server error
    """
    try:
        # Convert IDs to ObjectId
        workspace_object_id = PydanticObjectId(workspace_id)
        user_object_id = PydanticObjectId(user_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {str(e)}"
        )
    
    try:
        # Find the workspace
        workspace = await Workspace.find_one(Workspace.id == workspace_object_id)
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user is already a member
        for member in workspace.members:
            if member.user_id.ref.id == user_object_id:
                return True
        
        return False
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check user membership: {str(e)}"
        )

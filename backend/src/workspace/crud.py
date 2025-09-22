from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime
from .schema import Workspace, WorkspaceMember


async def create_workspace_for_user(user_id: str, workspace_name: str) -> Workspace:
    """
    Create a new workspace for a user.
    Args:
        user_id (str): The ID of the user who owns the workspace
        workspace_name (str): The name of the workspace
    Returns:
        Workspace: The created workspace document
    Raises:
        ValueError: If the user_id is not a valid ObjectId
        Exception: If workspace creation fails
    """
    try:
        print("calling create workspace")
        # Convert user_id string to PydanticObjectId
        user_object_id = PydanticObjectId(user_id)
        
        # Create workspace member with admin privileges for the creator
        creator_member = WorkspaceMember(
            user_id=user_object_id,
            is_admin=True
        )
        
        # Create workspace following the schema
        workspace = Workspace(
            name=workspace_name,
            members=[creator_member],
            created_by=user_object_id,
            created_at=datetime.now()
        )
        
        # Save to database
        await workspace.insert()
        print(workspace)
        return workspace
        
    except Exception as e:
        # Handle invalid ObjectId format
        if "Invalid ObjectId" in str(e):
            raise ValueError(f"Invalid user ID format: {user_id}")
        # Re-raise other exceptions
        raise e


async def get_workspace_by_id(workspace_id: str) -> Optional[Workspace]:
    """
    Retrieve a workspace by its ID.
    
    Args:
        workspace_id (str): The ID of the workspace to retrieve
        
    Returns:
        Optional[Workspace]: The workspace document if found, None otherwise
        
    Raises:
        ValueError: If the workspace_id is not a valid ObjectId
    """
    try:
        # Convert string ID to PydanticObjectId
        object_id = PydanticObjectId(workspace_id)
        
        # Find the workspace by ID
        workspace = await Workspace.get(object_id)
        
        return workspace
        
    except Exception as e:
        # Handle invalid ObjectId format
        if "Invalid ObjectId" in str(e):
            raise ValueError(f"Invalid workspace ID format: {workspace_id}")
        raise e

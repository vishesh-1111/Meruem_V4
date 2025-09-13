from typing import Optional
from beanie import PydanticObjectId
from .schema import Workspace


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

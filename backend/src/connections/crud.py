from typing import Optional
from beanie import PydanticObjectId
from .schema import Connection


async def get_connection_by_id(connection_id: str) -> Optional[Connection]:
    """
    Retrieve a connection by its ID.
    
    Args:
        connection_id (str): The ID of the connection to retrieve
        
    Returns:
        Optional[Connection]: The connection document if found, None otherwise
        
    Raises:
        ValueError: If the connection_id is not a valid ObjectId
    """
    try:
        # Convert string ID to PydanticObjectId
        object_id = PydanticObjectId(connection_id)
        
        # Find the connection by ID
        connection = await Connection.get(object_id)
        
        return connection
        
    except Exception as e:
        # Handle invalid ObjectId format
        if "Invalid ObjectId" in str(e):
            raise ValueError(f"Invalid connection ID format: {connection_id}")
        raise e

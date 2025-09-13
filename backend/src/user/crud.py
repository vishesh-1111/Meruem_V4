from typing import Optional
from beanie import PydanticObjectId
from .schema import User


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Retrieve a user by their ID.
    
    Args:
        user_id (str): The ID of the user to retrieve
        
    Returns:
        Optional[User]: The user document if found, None otherwise
        
    Raises:
        ValueError: If the user_id is not a valid ObjectId
    """
    try:
        # Convert string ID to PydanticObjectId
        object_id = PydanticObjectId(user_id)
        
        # Find the user by ID
        user = await User.get(object_id)
        
        return user
        
    except Exception as e:
        # Handle invalid ObjectId format
        if "Invalid ObjectId" in str(e):
            raise ValueError(f"Invalid user ID format: {user_id}")
        raise e


async def get_user_by_email(email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.
    
    Args:
        email (str): The email address of the user to retrieve
        
    Returns:
        Optional[User]: The user document if found, None otherwise
        
    Raises:
        ValueError: If the email is empty or None
    """
    if not email or not email.strip():
        raise ValueError("Email cannot be empty or None")
    
    # Find the user by email (case-insensitive search)
    user = await User.find_one(User.email == email.strip().lower())
    
    return user

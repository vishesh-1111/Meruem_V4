from fastapi import HTTPException, status
from .schema import User


async def check_user_exists(email: str) -> User:
    """
    Check if a user exists by email.
    
    Args:
        email: The email of the user to check
        
    Returns:
        User: The user object if found
        
    Raises:
        HTTPException:
            - 404: User not found
            - 500: Internal server error
    """
    try:
        user = await User.find_one(User.email == email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check user existence: {str(e)}"
        )

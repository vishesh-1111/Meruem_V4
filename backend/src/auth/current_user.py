import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Request, HTTPException, Depends
from beanie import PydanticObjectId
from ..user.schema import User
from config import get_settings


SECRET_KEY = get_settings().JWT_SECRET
ALGORITHM = "HS256"
print("............................",SECRET_KEY)
def get_current_user(request: Request):
    """Extract user ID from JWT token in Authorization header (Bearer) or cookies."""
    # Check if JWT secret is configured
    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT secret not configured"
        )
    
    token = None
    
    # First, try to get token from Authorization header (Bearer token)
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    # If no Bearer token, fall back to checking cookies
    if not token:
        token = request.cookies.get("meruem-access-token")
    
    # If still no token found, raise error
    if not token:
        raise HTTPException(status_code=401, detail="Unauthenticated: Token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or tampered token")

    return user_id

async def current_active_user(request: Request) -> User:
    """FastAPI dependency to get the current authenticated user from database."""
    user_id = get_current_user(request)
    
    try:
        # Convert string to ObjectId and find user
        user_object_id = PydanticObjectId(user_id)
        user = await User.get(user_object_id)
        
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="User not found"
            )
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid user ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch user: {str(e)}"
        )

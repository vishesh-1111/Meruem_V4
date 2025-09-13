import jwt
import httpx
import urllib.parse
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Request, HTTPException, Depends
from beanie import PydanticObjectId
from datetime import datetime, timedelta, timezone
from ..user.schema import User
from config import get_settings
from .config import get_google_oauth_config


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


def create_jwt_token(payload: dict, lifespan: int = 2) -> str:
    """
    Create a JWT token with the given payload and lifespan.
    
    Args:
        payload (dict): The payload to include in the token (should contain user_id, user_email)
        lifespan (int): Token lifespan in hours (default: 2 hours)
    
    Returns:
        str: The encoded JWT token
        
    Raises:
        HTTPException: If JWT secret is not configured or token generation fails
    """
    # Check if JWT secret is configured
    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT secret not configured"
        )
    
    # Calculate expiry time
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=lifespan)
    
    # Add expiry to payload
    token_payload = payload.copy()
    token_payload["exp"] = int(expiry_time.timestamp())
    
    # Generate JWT token
    try:
        token = jwt.encode(
            token_payload, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate access token: {str(e)}"
        )


async def fetch_google_user_profile(access_token: str) -> dict:
    """
    Fetch user profile information from Google using the access token.
    
    Args:
        access_token (str): The Google OAuth access token
        
    Returns:
        dict: User profile data containing given_name, family_name, email, picture
        
    Raises:
        HTTPException: If profile fetching fails
    """
    profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        profile_response = await client.get(profile_url, headers=headers)
        
        if profile_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get user profile: {profile_response.text}"
            )
        
        profile_data = profile_response.json()
        
        # Extract user information
        given_name = profile_data.get("given_name", "")
        family_name = profile_data.get("family_name", "")
        email = profile_data.get("email", "")
        picture = profile_data.get("picture", "")

        print("profile_data", profile_data)
        
        if not given_name or not family_name or not email:
            raise HTTPException(
                status_code=400,
                detail="Missing required user information from Google profile"
            )
        
        return {
            "given_name": given_name,
            "family_name": family_name,
            "email": email,
            "picture": picture
        }


async def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> str:
    """
    Exchange Google OAuth authorization code for access token.
    
    Args:
        code (str): The authorization code from Google OAuth callback
        client_id (str): Google OAuth client ID
        client_secret (str): Google OAuth client secret
        redirect_uri (str): The redirect URI used in OAuth flow
        
    Returns:
        str: The access token from Google
        
    Raises:
        HTTPException: If token exchange fails
    """
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        # Get access token
        token_response = await client.post(token_url, data=token_data)
        print("token_response", token_response)
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to exchange code for token: {token_response.text}"
            )
        
        token_info = token_response.json()
        access_token = token_info.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="No access token received from Google"
            )
        
        return access_token


async def get_access_token_from_code(code: str) -> str:
    """
    Get Google OAuth access token from authorization code.
    This function handles OAuth configuration retrieval and token exchange.
    
    Args:
        code (str): The authorization code from Google OAuth callback
        
    Returns:
        str: The access token from Google
        
    Raises:
        HTTPException: If OAuth configuration is missing or token exchange fails
    """
    # Get Google OAuth configuration
    oauth_config = get_google_oauth_config()
    client_id = oauth_config["client_id"]
    client_secret = oauth_config["client_secret"]
    redirect_uri = oauth_config["redirect_uri"]
    
    # Validate required configuration
    if not all([client_id, client_secret, redirect_uri]):
        raise HTTPException(
            status_code=500, 
            detail="Missing Google OAuth configuration"
        )
    
    # Exchange authorization code for access token
    access_token = await exchange_code_for_token(
        code=code,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )
    
    return access_token


def generate_google_oauth_url() -> str:
    """
    Generate Google OAuth URL for authentication.
    Returns the OAuth URL that users should be redirected to for authentication.
    
    Returns:
        str: The Google OAuth URL
        
    Raises:
        HTTPException: If OAuth configuration is missing or URL generation fails
    """
    # Get Google OAuth configuration
    oauth_config = get_google_oauth_config()
    client_id = oauth_config["client_id"]
    redirect_uri = oauth_config["redirect_uri"]
    
    # Validate required environment variables
    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth client ID not configured"
        )
    
    if not redirect_uri:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth redirect URI not configured"
        )
    
    # Build OAuth URL
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "access_type": "online",
        "prompt": "consent",
        "scope": "openid email profile"
    }
    
    try:
        oauth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        return oauth_url
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )

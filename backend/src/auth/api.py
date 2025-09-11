from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import os
import urllib.parse
import httpx
from datetime import datetime, timedelta
import jwt
from beanie import PydanticObjectId
from ..user.schema import User, UserCreate

router = APIRouter(prefix="/auth")


class GoogleCallbackRequest(BaseModel):
    code: str


@router.get("/google")
async def get_google_oauth_url():
    """
    Generate Google OAuth URL for authentication.
    Returns the OAuth URL that users should be redirected to for authentication.
    """
    try:
        # Get environment variables
        client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
        
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate OAuth URL: {str(e)}"
            )
        
        return JSONResponse(content={"url": oauth_url})
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during OAuth URL generation: {str(e)}"
        )


@router.post("/google/callback")
async def google_oauth_callback(request: GoogleCallbackRequest):
    """
    Handle Google OAuth callback with authorization code.
    Exchange code for access token and create/get user.
    """
    try:
        # Get environment variables
        client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
        
        if not all([client_id, client_secret, redirect_uri]):
            raise HTTPException(
                status_code=500, 
                detail="Missing Google OAuth configuration"
            )
        
        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": request.code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(token_url, data=token_data)
            
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
            
            # Get user profile from Google
            profile_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            
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
            
            if not given_name or not family_name or not email:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required user information from Google profile"
                )
            
            # Check if user already exists by email
            existing_user = await User.find_one(User.email == email)
            
            if existing_user:
                user = existing_user
            else:
                # Create new user
                user_data = UserCreate(
                    first_name=given_name,
                    last_name=family_name,
                    email=email,
                    profile_url=picture if picture else None
                )
                
                # Save user to database
                user = User(
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    email=user_data.email,
                    profile_url=user_data.profile_url
                )
                
                await user.insert()
            
            # Generate JWT token with 2-hour expiration
            jwt_secret = os.getenv("JWT_SECRET")
            if not jwt_secret:
                raise HTTPException(
                    status_code=500,
                    detail="JWT secret not configured"
                )
            
            # Calculate expiry time (2 hours from now)
            expiry_time = datetime.utcnow() + timedelta(hours=2)
            
            # Token payload with specified fields
            token_payload = {
                "user_id": str(user.id),
                "user_email": user.email,
                "exp": int(expiry_time.timestamp())  # iat as expiry time as requested
            }
            
            # Generate JWT token
            try:
                meruem_access_token = jwt.encode(
                    token_payload, 
                    jwt_secret, 
                    algorithm="HS256"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate access token: {str(e)}"
                )
            
            # Create response with cookie
            response_content = {
                "message": "User authenticated successfully",
                "meruem_access_token": meruem_access_token,
                "token_expires_in": 7200,  # 2 hours in seconds
                "user": {
                    "id": str(user.id),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "profile_url": user.profile_url
                },
                "google_profile": {
                    "email": email,
                    "given_name": given_name,
                    "family_name": family_name
                }
            }
            response = JSONResponse(content=response_content)
            # response = RedirectResponse(url="http://localhost:3000", status_code=302)
            response.set_cookie(
                key="meruem_access_token",
                value=meruem_access_token,
                max_age=7200,  # 2 hours
                httponly=False,
                secure=True,  # True in production with HTTPS
                samesite="none"
            )
            return response
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during OAuth callback: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """
    Handle user logout by redirecting to localhost:3000.
    Since JWT tokens are stateless, token invalidation happens on the client side.
    """
    try:
        # For JWT tokens, logout is typically handled on the client side
        # by removing the token from storage (localStorage, cookies, etc.)
        
        # Redirect to localhost:3000 after logout
        return RedirectResponse(
            url="http://localhost:3000",
            status_code=302
        )
        
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during logout: {str(e)}"
        )
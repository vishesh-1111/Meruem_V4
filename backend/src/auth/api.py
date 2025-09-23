from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import os
import httpx
from beanie import PydanticObjectId
from ..user.schema import User, UserCreate
from config import get_settings
from .config import get_google_oauth_config
from .services import create_jwt_token, fetch_google_user_profile, exchange_code_for_token, generate_google_oauth_url, get_access_token_from_code
from ..workspace.crud import create_workspace_for_user
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
        oauth_url = generate_google_oauth_url()
        return JSONResponse(content={"url": oauth_url})
        
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
        # Get access token from authorization code using service
        access_token = await get_access_token_from_code(request.code)
        
        # Get user profile from Google using service
        profile_data = await fetch_google_user_profile(access_token)
        
        # Extract user information
        given_name = profile_data["given_name"]
        family_name = profile_data["family_name"]
        email = profile_data["email"]
        picture = profile_data["picture"]
        
        # Check if user already exists by email
        existing_user = await User.find_one(User.email == email)

        # print('existing_user',existing_user)
        
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
            # Create default workspace for the new user
            workspace_name = f"{given_name}'s workspace"
            print("calling workspace creation")
            await create_workspace_for_user(str(user.id), workspace_name)
        
        # Generate JWT token with 2-hour expiration using service
        token_payload = {
            "user_id": str(user.id),
            "user_email": user.email
        }
        
        # Generate JWT token using service function
        meruem_access_token = create_jwt_token(token_payload, lifespan=2)
        
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
        # print(response)
        # response = RedirectResponse(url="http://localhost:3000", status_code=302)
        response.set_cookie(
            key="meruem_access_token",
            value=meruem_access_token,
            max_age=7200,  # 2 hours
            httponly=True,
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


@router.get("/logout")
async def logout():
    """
    Handle user logout by redirecting to localhost:3000.
    Since JWT tokens are stateless, token invalidation happens on the client side.
    """
    try:
     response = RedirectResponse(url="http://localhost:3000", status_code=302)
     response.delete_cookie(key="meruem_access_token", domain="localhost", path="/")
     return response

        
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during logout: {str(e)}"
        )
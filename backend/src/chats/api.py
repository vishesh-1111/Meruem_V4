from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from src.user.schema import User
from src.auth.current_user import current_active_user
from src.workspace.schema import Workspace
from src.connections.schema import Connection
from .schema import Chat
from fastapi import Response


# Request models
class CreateChatRequest(BaseModel):
    name: str


# Response models
class ChatResponse(BaseModel):
    id: str
    name: str
    created_by: str
    created_at: datetime
    workspace_id: str
    connection_id: str
    
    class Config:
        from_attributes = True


router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/create/{workspace_id}/{connection_id}", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    workspace_id: str,
    connection_id: str,
    chat_data: CreateChatRequest,
    current_user: User = Depends(current_active_user)
):
    """
    Create a new chat in a workspace with a specific connection.
    
    - **workspace_id**: ID of the workspace where the chat will be created
    - **connection_id**: ID of the database connection to use for this chat
    - **name**: Name of the chat
    
    The current user is automatically set as the creator.
    """
    try:
        # Validate workspace exists and user has access
        workspace = await Workspace.get(PydanticObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user has access to this workspace
        user_has_access = any(
            str(member.user_id.ref.id) == str(current_user.id) for member in workspace.members
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )
        
        # Validate connection exists and belongs to the workspace
        connection = await Connection.get(PydanticObjectId(connection_id))
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )
        
        # Check if connection belongs to the workspace
        if str(connection.workspaceId.ref.id) != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Connection does not belong to this workspace"
            )
        
        # Create chat
        chat = Chat(
            name=chat_data.name,
            created_by=current_user.id,
            workspace_id=workspace.id,
            connection_id=connection.id
        )
        
        # Save to database
        await chat.insert()
        
        # Return response
        return ChatResponse(
            id=str(chat.id),
            name=chat.name,
            created_by=str(chat.created_by.ref.id),
            created_at=chat.created_at,
            workspace_id=str(chat.workspace_id.ref.id),
            connection_id=str(chat.connection_id.ref.id)
        )
        
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A chat with this name already exists in this workspace"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the chat: {str(e)}"
        )


@router.get("/workspace/{workspace_id}", response_model=List[ChatResponse])
async def get_workspace_chats(
    workspace_id: str,
    response: Response, 
    current_user: User = Depends(current_active_user)
):
    """
    Get all chats in a workspace.
    
    - **workspace_id**: ID of the workspace to get chats from
    """
    try:
        # Validate workspace exists and user has access
        workspace = await Workspace.get(PydanticObjectId(workspace_id))
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user has access to this workspace
        user_has_access = any(
            str(member.user_id.ref.id) == str(current_user.id) for member in workspace.members
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )
        
        # Get all chats in the workspace, sorted by creation date (newest first)
        chats = await Chat.find(
            # Chat.workspace_id.ref.id == PydanticObjectId(workspace_id)
        ).sort(-Chat.created_at).to_list()
        
        # Convert to response format
        chat_responses = []
        for chat in chats:
            chat_responses.append(ChatResponse(
                id=str(chat.id),
                name=chat.name,
                created_by=str(chat.created_by.ref.id),
                created_at=chat.created_at,
                workspace_id=str(chat.workspace_id.ref.id),
                connection_id=str(chat.connection_id.ref.id)
            ))
        
        
        return chat_responses
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching chats: {str(e)}"
        )


@router.get("/connection/{connection_id}", response_model=List[ChatResponse])
async def get_connection_chats(
    connection_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get all chats for a specific connection.
    
    - **connection_id**: ID of the connection to get chats from
    """
    try:
        # Validate connection exists
        connection = await Connection.get(PydanticObjectId(connection_id))
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )
        
        # Get the workspace to check user access
        workspace = await Workspace.get(connection.workspaceId.ref.id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user has access to this workspace
        user_has_access = any(
            str(member.user_id.ref.id) == str(current_user.id) for member in workspace.members
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this connection"
            )
        
        # Get all chats for the connection, sorted by creation date (newest first)
        chats = await Chat.find(
            Chat.connection_id.ref.id == PydanticObjectId(connection_id)
        ).sort(-Chat.created_at).to_list()
        
        # Convert to response format
        chat_responses = []
        for chat in chats:
            chat_responses.append(ChatResponse(
                id=str(chat.id),
                name=chat.name,
                created_by=str(chat.created_by.ref.id),
                created_at=chat.created_at,
                workspace_id=str(chat.workspace_id.ref.id),
                connection_id=str(chat.connection_id.ref.id)
            ))
        
        return chat_responses
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching chats: {str(e)}"
        )


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get a specific chat by ID.
    
    - **chat_id**: ID of the chat to retrieve
    """
    try:
        # Get the chat
        chat = await Chat.get(PydanticObjectId(chat_id))
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Get the workspace to check user access
        workspace = await Workspace.get(chat.workspace_id.ref.id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user has access to this workspace
        user_has_access = any(
            str(member.user_id.ref.id) == str(current_user.id) for member in workspace.members
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this chat"
            )
        
        # Return chat
        return ChatResponse(
            id=str(chat.id),
            name=chat.name,
            created_by=str(chat.created_by.ref.id),
            created_at=chat.created_at,
            workspace_id=str(chat.workspace_id.ref.id),
            connection_id=str(chat.connection_id.ref.id)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the chat: {str(e)}"
        )
    
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Delete a chat by ID.
    
    The chat can only be deleted if:
    1) It was created by the user who wants to delete it, OR
    2) The user who wants to delete the chat is an admin of the workspace the chat belongs to
    
    - **chat_id**: ID of the chat to delete
    """
    try:
        # Get the chat
        chat = await Chat.get(PydanticObjectId(chat_id))
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Get the workspace to check admin permissions
        workspace = await Workspace.get(chat.workspace_id.ref.id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Check if user has permission to delete this chat
        can_delete = False
        
        # Condition 1: User created the chat
        if str(chat.created_by.ref.id) == str(current_user.id):
            can_delete = True
        else:
            # Condition 2: User is admin of the workspace
            for member in workspace.members:
                if str(member.user_id.ref.id) == str(current_user.id) and member.is_admin:
                    can_delete = True
                    break
        
        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this chat. Only the chat creator or workspace admins can delete chats."
            )
        
        # Delete the chat
        await chat.delete()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the chat: {str(e)}"
        )    
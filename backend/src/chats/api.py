from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from src.user.schema import User
from ..auth.services import current_active_user
from src.workspace.schema import Workspace
from src.workspace.services import get_user_role_in_workspace, UserRole
from src.connections.schema import Connection
from .schema import Chat
from .models import CreateChatRequest, ChatResponse
from fastapi import Response,Request


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
        # Check if user has access to this workspace using service function
        user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
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
            workspace_id=PydanticObjectId(workspace_id),
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


@router.get("/workspace/{workspace_id}")
async def get_workspace_chats(
    workspace_id: str,
    response: Response, 
    request: Request,
    current_user: User = Depends(current_active_user)
):
    """
    Get all chats in a workspace.
    
    - **workspace_id**: ID of the workspace to get chats from
    """
    try:

        print(request.query_params)
        # Check if user has access to this workspace using service function
        user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
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
                createdAt=chat.created_at,
                workspace_id=str(chat.workspace_id.ref.id),
                connection_id=str(chat.connection_id.ref.id)
            ))
        
        
        return {
            "chats": chat_responses,
            "hasMore": False
        }
        
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
        
        # Check if user has access to the workspace that owns this connection
        workspace_id = str(connection.workspaceId.ref.id)
        user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
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
        
        # Check if user has access to the workspace that owns this chat
        workspace_id = str(chat.workspace_id.ref.id)
        user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
        
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
        
        # Check if user has permission to delete this chat
        can_delete = False
        
        # Condition 1: User created the chat
        if str(chat.created_by.ref.id) == str(current_user.id):
            can_delete = True
        else:
            # Condition 2: User is admin of the workspace
            try:
                workspace_id = str(chat.workspace_id.ref.id)
                user_role = await get_user_role_in_workspace(workspace_id, str(current_user.id))
                if user_role == UserRole.ADMIN:
                    can_delete = True
            except HTTPException:
                # User doesn't have access to workspace
                pass
        
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
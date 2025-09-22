from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from src.user.schema import User
from ..auth.services import current_active_user
from src.chats.schema import Chat
from .schema import Message, MessageRole
from fastapi import Response, Request


router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/create/{chat_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: str,
    role: MessageRole,
    content: dict,
    current_user: User = Depends(current_active_user)
):
    """
    Create a new message in a chat.
    
    - **chat_id**: ID of the chat where the message will be created
    - **role**: Role of the message sender (assistant or user)
    - **content**: Message content as a flexible dictionary
    """
    try:
        # Verify that the chat exists
        chat = await Chat.get(PydanticObjectId(chat_id))
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Create the message
        message = Message(
            chat_id=chat.id,
            role=role,
            content=content
        )
        
        await message.insert()
        
        return {
            "id": str(message.id),
            "chat_id": str(message.chat_id.ref.id),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chat ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )


@router.get("/chat/{chat_id}", response_model=List[dict])
async def get_chat_messages(
    chat_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get all messages for a specific chat.
    
    - **chat_id**: ID of the chat to retrieve messages from
    """
    try:
        # Verify that the chat exists
        chat = await Chat.get(PydanticObjectId(chat_id))
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Get messages for the chat, ordered by creation time
        messages = await Message.find(
            Message.chat_id == chat.id
        ).sort(+Message.created_at).to_list()
        
        return [
            {
                "id": str(message.id),
                "chat_id": str(message.chat_id.ref.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
            for message in messages
        ]
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chat ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )


@router.get("/{message_id}", response_model=dict)
async def get_message(
    message_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get a specific message by ID.
    
    - **message_id**: ID of the message to retrieve
    """
    try:
        message = await Message.get(PydanticObjectId(message_id))
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return {
            "id": str(message.id),
            "chat_id": str(message.chat_id.ref.id),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving message: {str(e)}"
        )


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Delete a specific message by ID.
    
    - **message_id**: ID of the message to delete
    """
    try:
        message = await Message.get(PydanticObjectId(message_id))
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        await message.delete()
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        )

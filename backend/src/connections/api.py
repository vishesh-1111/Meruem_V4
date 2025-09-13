from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List
import mysql.connector
from mysql.connector import Error
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from urllib.parse import urlparse
from .handlers.mysql import parse_mysql_connection_string,get_mysql_schema
from src.user.schema import User
from ..auth.services import current_active_user
from src.workspace.schema import Workspace
from .schema import (
    Connection, 
    ConnectionCreate, 
    ConnectionResponse, 
)

router = APIRouter(prefix="/connections", tags=["connections"])



@router.post("/{workspace_id}/create", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    workspace_id: str,
    connection_data: ConnectionCreate,
    current_user: User = Depends(current_active_user)
):
    """
    Create a new database connection.
    
    This endpoint:
    1. Validates the connection string
    2. Tests the connection to the MySQL database
    3. Fetches the database schema
    4. Creates a new connection document
    
    - **name**: Display name for the connection
    - **config**: MySQL configuration including connection string
    - **workspace_id**: ID of the workspace this connection belongs to (query parameter)
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
        print("workspace",workspace)
        user_has_access = any(
            str(member.user_id.ref.id) == str(current_user.id) for member in workspace.members
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )
        
        # Parse and validate connection string
        connection_params = parse_mysql_connection_string(connection_data.config.connectionString)
        
        # Test connection and fetch schema
        db_schema = get_mysql_schema(connection_params)
        
        # Create connection document
        connection = Connection(
            name=connection_data.name,
            driver="mysql",
            config=connection_data.config,
            dbSchema=db_schema,
            createdBy=current_user,
            workspaceId=workspace
        )
        
        try:
            await connection.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A connection with this configuration already exists in this workspace"
            )
        
        # Return response
        return ConnectionResponse(
            id=str(connection.id),
            name=connection.name,
            driver=connection.driver,
            workspaceId=str(workspace.id),
            createdAt=connection.createdAt,
            hasSchema=len(connection.dbSchema) > 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connection: {str(e)}"
        )


@router.get("/workspace/{workspace_id}", response_model=List[ConnectionResponse])
async def get_workspace_connections(
    workspace_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get all connections for a specific workspace.
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
        
        # Get all connections for this workspace
        connections = await Connection.find(
            Connection.workspaceId.id == PydanticObjectId(workspace_id)
        ).to_list()
        
        return [
            ConnectionResponse(
                id=str(conn.id),
                name=conn.name,
                driver=conn.driver,
                workspaceId=str(conn.workspaceId.ref.id),
                createdAt=conn.createdAt,
                hasSchema=len(conn.dbSchema) > 0
            )
            for conn in connections
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch connections: {str(e)}"
        )


@router.get("/{connection_id}/schema")
async def get_connection_schema(
    connection_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get the database schema for a specific connection.
    """
    try:
        # Get connection
        connection = await Connection.get(PydanticObjectId(connection_id))
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )
        
        # Check if user has access to this workspace
        workspace = await connection.workspaceId.fetch()
        user_has_access = any(
            str(member.user_id.id) == str(current_user.id) for member in workspace.members
        )
        if not user_has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this connection"
            )
        
        return connection.dbSchema
        
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schema: {str(e)}"
        )
    
from beanie import Document, Link
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import IndexModel
from src.user.schema import User
from src.workspace.schema import Workspace


class ColumnSchema(BaseModel):
    """Schema for database table columns"""
    name: str
    type: str
    isPrimary: bool = False
    referenceTable: Optional[str] = None
    referenceColumn: Optional[str] = None


class TableSchema(BaseModel):
    """Schema for database tables"""
    name: str
    database_schema: str  # Renamed from 'schema' to avoid shadowing BaseModel attribute
    columns: List[ColumnSchema]


class MySQLConfig(BaseModel):
    """Configuration for MySQL connections"""
    connectionString: str


class Connection(Document):
    """Database connection document"""
    name: str
    driver: str = "mysql"
    config: MySQLConfig
    dbSchema: Dict[str, TableSchema] = Field(default_factory=dict)
    createdBy: Link[User]
    workspaceId: Link[Workspace]
    createdAt: datetime = Field(default_factory=datetime.now)

    class Settings:
     name = "connections"
     indexes = [
        # Prevent same workspace from having two connections with the same name
        IndexModel(
            [("workspaceId", 1), ("name", 1)], 
            unique=True,
            name="unique_connection_name_per_workspace"
        ),
        # Prevent same workspace from having two connections with the same config
        IndexModel(
            [("workspaceId", 1), ("config", 1)], 
            unique=True,
            name="unique_connection_config_per_workspace"
        )
    ]


    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production MySQL",
                "driver": "mysql",
                "config": {
                    "connectionString": "mysql://user:password@localhost:3306/classicmodels"
                },
                "dbSchema": {
                    "classicmodels.customers": {
                        "name": "customers",
                        "database_schema": "classicmodels",
                        "columns": [
                            {
                                "name": "customerNumber",
                                "type": "int",
                                "isPrimary": True,
                                "referenceTable": None,
                                "referenceColumn": None
                            },
                            {
                                "name": "customerName",
                                "type": "varchar",
                                "isPrimary": False,
                                "referenceTable": None,
                                "referenceColumn": None
                            }
                        ]
                    },
                    "classicmodels.products": {
                        "name": "products",
                        "database_schema": "classicmodels",
                        "columns": [
                            {
                                "name": "productCode",
                                "type": "varchar",
                                "isPrimary": True,
                                "referenceTable": None,
                                "referenceColumn": None
                            },
                            {
                                "name": "productLine",
                                "type": "varchar",
                                "isPrimary": False,
                                "referenceTable": "productlines",
                                "referenceColumn": "productLine"
                            }
                        ]
                    }
                },
                "workspaceId": "workspace_123"
            }
        }


class ConnectionCreate(BaseModel):
    """Schema for creating a new connection"""
    name: str
    config: MySQLConfig


class ConnectionResponse(BaseModel):
    """Schema for connection response"""
    id: str
    name: str
    driver: str
    workspaceId: str  # Return as string for API response
    createdAt: datetime
    hasSchema: bool

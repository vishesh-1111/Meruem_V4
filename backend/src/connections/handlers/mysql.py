from typing import Dict
from urllib.parse import urlparse
from fastapi import  HTTPException, status
import mysql.connector
from ..schema import (
    Connection, 
    ConnectionCreate, 
    ConnectionResponse, 
    TableSchema,
    ColumnSchema
)




def parse_mysql_connection_string(connection_string: str) -> Dict[str, str]:
    """
    Parse MySQL connection string and extract connection parameters.
    Supports formats like: mysql://user:password@host:port/database?ssl-mode=REQUIRED
    """
    try:
        parsed = urlparse(connection_string)
        
        if parsed.scheme != 'mysql':
            raise ValueError("Connection string must start with 'mysql://'")
        
        # Parse query parameters for SSL and other options
        query_params = {}
        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
        
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'ssl_mode': query_params.get('ssl-mode', 'PREFERRED'),
            'query_params': query_params
        }
    except Exception as e:
        raise ValueError(f"Invalid connection string format: {str(e)}")
    



def get_mysql_schema(connection_params: Dict[str, str]) -> Dict[str, TableSchema]:
    """
    Connect to MySQL database and fetch schema information.
    Returns a dictionary mapping table names to their schema.
    """
    connection = None
    cursor = None
    
    try:
        # Establish connection
        connection_config = {
            'host': connection_params['host'],
            'port': connection_params['port'],
            'user': connection_params['user'],
            'password': connection_params['password'],
            'database': connection_params['database'],
            'autocommit': True
        }
        
        # Handle SSL configuration for cloud databases
        if 'ssl_mode' in connection_params:
            ssl_mode = connection_params['ssl_mode'].upper()
            if ssl_mode in ['REQUIRED', 'VERIFY_CA', 'VERIFY_IDENTITY']:
                connection_config['ssl_disabled'] = False
            elif ssl_mode == 'DISABLED':
                connection_config['ssl_disabled'] = True
        
        connection = mysql.connector.connect(**connection_config)
        
        if not connection.is_connected():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to MySQL database"
            )
        
        cursor = connection.cursor()
        database_name = connection_params['database']
        
        print(f"✅ Connected to database: {database_name}")
        
        # Get all tables in the database
        cursor.execute(f"SHOW TABLES FROM `{database_name}`")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables: {tables}")
        
        if not tables:
            print("⚠️  No tables found in the database")
            return {}
        
        schema_dict = {}
        
        for table_name in tables:
            print(f"🔍 Processing table: {table_name}")
            
            # Get column information for each table
            cursor.execute(f"""
                SELECT 
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.COLUMN_KEY,
                    c.EXTRA,
                    kcu.REFERENCED_TABLE_NAME,
                    kcu.REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS c
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    ON c.TABLE_SCHEMA = kcu.TABLE_SCHEMA 
                    AND c.TABLE_NAME = kcu.TABLE_NAME 
                    AND c.COLUMN_NAME = kcu.COLUMN_NAME
                    AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                WHERE c.TABLE_SCHEMA = %s AND c.TABLE_NAME = %s
                ORDER BY c.ORDINAL_POSITION
            """, (database_name, table_name))
            
            columns_data = cursor.fetchall()
            print(f"  📊 Found {len(columns_data)} columns")
            
            columns = []
            
            for col_data in columns_data:
                column_name, data_type, is_nullable, column_key, extra, ref_table, ref_column = col_data
                
                # Determine if column is primary key
                is_primary = column_key == 'PRI'
                
                # Map MySQL data types to simpler types
                simple_type = map_mysql_type(data_type)
                
                column_schema = ColumnSchema(
                    name=column_name,
                    type=simple_type,
                    isPrimary=is_primary,
                    referenceTable=ref_table,
                    referenceColumn=ref_column
                )
                columns.append(column_schema)
                print(f"    🔸 {column_name} ({simple_type}) {'[PK]' if is_primary else ''}")
            
            # Create table schema
            table_schema = TableSchema(
                name=table_name,
                database_schema=database_name,
                columns=columns
            )
            
            # Use format: schema.table_name as key
            schema_key = f"{database_name}.{table_name}"
            schema_dict[schema_key] = table_schema
        
        print(f"✅ Schema extraction completed. Found {len(schema_dict)} tables.")
        return schema_dict
        
    except mysql.connector.Error as e:
        error_msg = f"MySQL Error: {str(e)}"
        if e.errno == 1045:  # Access denied
            error_msg = "Access denied. Please check your username and password."
        elif e.errno == 2003:  # Can't connect to server
            error_msg = "Can't connect to MySQL server. Please check host and port."
        elif e.errno == 1049:  # Unknown database
            error_msg = "Unknown database. Please check the database name."
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()    


def map_mysql_type(mysql_type: str) -> str:
    """
    Map MySQL data types to simplified types.
    """
    mysql_type = mysql_type.lower()
    
    # Integer types
    if mysql_type in ['tinyint', 'smallint', 'mediumint', 'int', 'integer', 'bigint']:
        return 'int'
    
    # Decimal types
    if mysql_type in ['decimal', 'numeric', 'float', 'double', 'real']:
        return 'decimal'
    
    # String types
    if mysql_type in ['char', 'varchar', 'text', 'tinytext', 'mediumtext', 'longtext']:
        return 'varchar'
    
    # Date/Time types
    if mysql_type in ['date', 'time', 'datetime', 'timestamp', 'year']:
        return 'datetime'
    
    # Binary types
    if mysql_type in ['binary', 'varbinary', 'blob', 'tinyblob', 'mediumblob', 'longblob']:
        return 'binary'
    
    # Boolean
    if mysql_type == 'boolean' or mysql_type == 'bool':
        return 'boolean'
    
    # JSON
    if mysql_type == 'json':
        return 'json'
    
    # Default to varchar for unknown types
    return 'varchar'            
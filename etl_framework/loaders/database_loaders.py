"""
Database data loaders.
"""
import pandas as pd
from typing import Any, Dict, List, Optional

from ..core.base import Loader
from ..core.exceptions import LoadError


class SQLLoader(Loader):
    """Load data to SQL databases."""
    
    def __init__(self, name: str, connection_string: str, table_name: str, 
                 if_exists: str = "append", method: str = "pandas"):
        super().__init__(name)
        self.connection_string = connection_string
        self.table_name = table_name
        self.if_exists = if_exists  # 'fail', 'replace', 'append'
        self.method = method
        
    def validate_config(self) -> bool:
        """Validate SQL loader configuration."""
        if not self.connection_string:
            raise LoadError("Connection string is required")
        if not self.table_name:
            raise LoadError("Table name is required")
        return True
        
    def _get_connection(self):
        """Get database connection."""
        try:
            from sqlalchemy import create_engine
            engine = create_engine(self.connection_string)
            return engine
        except ImportError:
            raise LoadError("SQLAlchemy is required for SQL loading")
        except Exception as e:
            raise LoadError(f"Failed to connect to database: {str(e)}")
    
    def load(self, data: List[Dict[str, Any]]) -> bool:
        """Load data to SQL database."""
        self.validate_config()
        
        if not isinstance(data, list):
            raise LoadError("SQLLoader expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            engine = self._get_connection()
            
            df.to_sql(
                name=self.table_name,
                con=engine,
                if_exists=self.if_exists,
                index=False,
                method=self.method
            )
            
            self.logger.info(f"Successfully loaded {len(data)} records to SQL table: {self.table_name}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to SQL database: {str(e)}")


class NoSQLLoader(Loader):
    """Load data to NoSQL databases (MongoDB, etc.)."""
    
    def __init__(self, name: str, connection_config: Dict[str, Any], 
                 collection: str, operation: str = "insert"):
        super().__init__(name)
        self.connection_config = connection_config
        self.collection = collection
        self.operation = operation.lower()  # 'insert', 'upsert', 'replace'
        
    def validate_config(self) -> bool:
        """Validate NoSQL loader configuration."""
        if not self.connection_config:
            raise LoadError("Connection configuration is required")
        if not self.collection:
            raise LoadError("Collection name is required")
        return True
        
    def _get_mongodb_client(self):
        """Get MongoDB client."""
        try:
            from pymongo import MongoClient
            
            host = self.connection_config.get('host', 'localhost')
            port = self.connection_config.get('port', 27017)
            username = self.connection_config.get('username')
            password = self.connection_config.get('password')
            database = self.connection_config.get('database')
            
            if username and password:
                client = MongoClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password
                )
            else:
                client = MongoClient(host=host, port=port)
            
            return client[database] if database else client
        except ImportError:
            raise LoadError("pymongo is required for MongoDB loading")
        except Exception as e:
            raise LoadError(f"Failed to connect to MongoDB: {str(e)}")
    
    def load(self, data: List[Dict[str, Any]]) -> bool:
        """Load data to NoSQL database."""
        self.validate_config()
        
        if not isinstance(data, list):
            raise LoadError("NoSQLLoader expects list of dictionaries")
        
        db_type = self.connection_config.get('type', 'mongodb').lower()
        
        if db_type == 'mongodb':
            return self._load_to_mongodb(data)
        else:
            raise LoadError(f"Unsupported NoSQL database type: {db_type}")
    
    def _load_to_mongodb(self, data: List[Dict[str, Any]]) -> bool:
        """Load data to MongoDB."""
        try:
            db = self._get_mongodb_client()
            collection = db[self.collection]
            
            if self.operation == "insert":
                if len(data) == 1:
                    collection.insert_one(data[0])
                else:
                    collection.insert_many(data)
            elif self.operation == "replace":
                # Clear collection and insert new data
                collection.delete_many({})
                if data:
                    collection.insert_many(data)
            elif self.operation == "upsert":
                # Upsert requires a key field to identify documents
                key_field = self.connection_config.get('upsert_key', '_id')
                for doc in data:
                    if key_field in doc:
                        collection.replace_one(
                            {key_field: doc[key_field]},
                            doc,
                            upsert=True
                        )
                    else:
                        collection.insert_one(doc)
            else:
                raise LoadError(f"Unknown MongoDB operation: {self.operation}")
            
            self.logger.info(f"Successfully loaded {len(data)} records to MongoDB collection: {self.collection}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to MongoDB: {str(e)}")
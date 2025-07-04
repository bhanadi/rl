"""
Database data extractors.
"""
from typing import Any, Dict, List, Optional, Union
import logging

from ..core.base import Extractor
from ..core.exceptions import ExtractionError


class SQLExtractor(Extractor):
    """Extract data from SQL databases."""
    
    def __init__(self, name: str, connection_string: str, query: str, params: Optional[Dict] = None):
        super().__init__(name)
        self.connection_string = connection_string
        self.query = query
        self.params = params or {}
        self._connection = None
        
    def validate_config(self) -> bool:
        """Validate SQL extractor configuration."""
        if not self.connection_string:
            raise ExtractionError("Connection string is required")
        if not self.query:
            raise ExtractionError("SQL query is required")
        return True
        
    def _get_connection(self):
        """Get database connection (implement based on your database)."""
        # This is a template - implement based on your specific database
        # Examples:
        # - For PostgreSQL: psycopg2.connect(self.connection_string)
        # - For MySQL: mysql.connector.connect(...)
        # - For SQLite: sqlite3.connect(...)
        # - For SQLAlchemy: create_engine(self.connection_string).connect()
        
        try:
            import pandas as pd
            from sqlalchemy import create_engine
            
            engine = create_engine(self.connection_string)
            return engine.connect()
        except ImportError:
            raise ExtractionError("SQLAlchemy and pandas are required for SQL extraction")
        except Exception as e:
            raise ExtractionError(f"Failed to connect to database: {str(e)}")
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from SQL database."""
        self.validate_config()
        
        try:
            import pandas as pd
            
            with self._get_connection() as conn:
                df = pd.read_sql(self.query, conn, params=self.params)
                return df.to_dict('records')
        except ImportError:
            raise ExtractionError("pandas is required for SQL extraction")
        except Exception as e:
            raise ExtractionError(f"Failed to extract from SQL database: {str(e)}")


class NoSQLExtractor(Extractor):
    """Extract data from NoSQL databases (MongoDB, etc.)."""
    
    def __init__(self, name: str, connection_config: Dict[str, Any], 
                 collection: str, query: Optional[Dict] = None):
        super().__init__(name)
        self.connection_config = connection_config
        self.collection = collection
        self.query = query or {}
        
    def validate_config(self) -> bool:
        """Validate NoSQL extractor configuration."""
        if not self.connection_config:
            raise ExtractionError("Connection configuration is required")
        if not self.collection:
            raise ExtractionError("Collection name is required")
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
            raise ExtractionError("pymongo is required for MongoDB extraction")
        except Exception as e:
            raise ExtractionError(f"Failed to connect to MongoDB: {str(e)}")
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from NoSQL database."""
        self.validate_config()
        
        db_type = self.connection_config.get('type', 'mongodb').lower()
        
        if db_type == 'mongodb':
            return self._extract_from_mongodb()
        else:
            raise ExtractionError(f"Unsupported NoSQL database type: {db_type}")
    
    def _extract_from_mongodb(self) -> List[Dict[str, Any]]:
        """Extract data from MongoDB."""
        try:
            db = self._get_mongodb_client()
            collection = db[self.collection]
            
            cursor = collection.find(self.query)
            
            # Convert ObjectId to string for JSON serialization
            result = []
            for doc in cursor:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                result.append(doc)
            
            return result
        except Exception as e:
            raise ExtractionError(f"Failed to extract from MongoDB: {str(e)}")


class RedisExtractor(Extractor):
    """Extract data from Redis."""
    
    def __init__(self, name: str, connection_config: Dict[str, Any], 
                 keys_pattern: str = "*", data_type: str = "string"):
        super().__init__(name)
        self.connection_config = connection_config
        self.keys_pattern = keys_pattern
        self.data_type = data_type.lower()
        
    def validate_config(self) -> bool:
        """Validate Redis extractor configuration."""
        if not self.connection_config:
            raise ExtractionError("Connection configuration is required")
        return True
        
    def _get_redis_client(self):
        """Get Redis client."""
        try:
            import redis
            
            return redis.Redis(
                host=self.connection_config.get('host', 'localhost'),
                port=self.connection_config.get('port', 6379),
                password=self.connection_config.get('password'),
                db=self.connection_config.get('db', 0),
                decode_responses=True
            )
        except ImportError:
            raise ExtractionError("redis package is required for Redis extraction")
        except Exception as e:
            raise ExtractionError(f"Failed to connect to Redis: {str(e)}")
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from Redis."""
        self.validate_config()
        
        try:
            client = self._get_redis_client()
            keys = client.keys(self.keys_pattern)
            
            result = []
            for key in keys:
                if self.data_type == "string":
                    value = client.get(key)
                elif self.data_type == "hash":
                    value = client.hgetall(key)
                elif self.data_type == "list":
                    value = client.lrange(key, 0, -1)
                elif self.data_type == "set":
                    value = list(client.smembers(key))
                else:
                    value = client.get(key)
                
                result.append({
                    'key': key,
                    'value': value,
                    'type': self.data_type
                })
            
            return result
        except Exception as e:
            raise ExtractionError(f"Failed to extract from Redis: {str(e)}")
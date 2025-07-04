"""
Cloud storage data loaders.
"""
import json
import pandas as pd
from typing import Any, Dict, List, Optional
from io import StringIO, BytesIO

from ..core.base import Loader
from ..core.exceptions import LoadError


class S3Loader(Loader):
    """Load data to AWS S3."""
    
    def __init__(self, name: str, bucket: str, key: str, 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: str = "us-east-1",
                 file_format: str = "json"):
        super().__init__(name)
        self.bucket = bucket
        self.key = key
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.file_format = file_format.lower()
        
    def validate_config(self) -> bool:
        """Validate S3 loader configuration."""
        if not self.bucket:
            raise LoadError("S3 bucket is required")
        if not self.key:
            raise LoadError("S3 key is required")
        return True
        
    def _get_s3_client(self):
        """Get S3 client."""
        try:
            import boto3
            
            if self.aws_access_key_id and self.aws_secret_access_key:
                client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.region_name
                )
            else:
                # Use default credentials (IAM role, env vars, etc.)
                client = boto3.client('s3', region_name=self.region_name)
            
            return client
        except ImportError:
            raise LoadError("boto3 is required for S3 loading")
        except Exception as e:
            raise LoadError(f"Failed to create S3 client: {str(e)}")
    
    def load(self, data: Any) -> bool:
        """Load data to S3."""
        self.validate_config()
        
        try:
            s3_client = self._get_s3_client()
            
            # Convert data to appropriate format
            if self.file_format == "json":
                content = json.dumps(data, indent=2, default=str)
                content_type = "application/json"
            elif self.file_format == "csv":
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    content = df.to_csv(index=False)
                else:
                    raise LoadError("CSV format requires list of dictionaries")
                content_type = "text/csv"
            elif self.file_format == "parquet":
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    buffer = BytesIO()
                    df.to_parquet(buffer, index=False)
                    content = buffer.getvalue()
                else:
                    raise LoadError("Parquet format requires list of dictionaries")
                content_type = "application/octet-stream"
            else:
                # Plain text
                content = str(data)
                content_type = "text/plain"
            
            # Upload to S3
            if isinstance(content, str):
                s3_client.put_object(
                    Bucket=self.bucket,
                    Key=self.key,
                    Body=content.encode('utf-8'),
                    ContentType=content_type
                )
            else:
                s3_client.put_object(
                    Bucket=self.bucket,
                    Key=self.key,
                    Body=content,
                    ContentType=content_type
                )
            
            record_count = len(data) if isinstance(data, list) else 1
            self.logger.info(f"Successfully loaded {record_count} records to S3: s3://{self.bucket}/{self.key}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to S3: {str(e)}")


class AzureBlobLoader(Loader):
    """Load data to Azure Blob Storage."""
    
    def __init__(self, name: str, account_name: str, container_name: str, 
                 blob_name: str, account_key: Optional[str] = None,
                 connection_string: Optional[str] = None,
                 file_format: str = "json"):
        super().__init__(name)
        self.account_name = account_name
        self.container_name = container_name
        self.blob_name = blob_name
        self.account_key = account_key
        self.connection_string = connection_string
        self.file_format = file_format.lower()
        
    def validate_config(self) -> bool:
        """Validate Azure Blob loader configuration."""
        if not self.account_name:
            raise LoadError("Azure storage account name is required")
        if not self.container_name:
            raise LoadError("Azure container name is required")
        if not self.blob_name:
            raise LoadError("Azure blob name is required")
        if not self.connection_string and not self.account_key:
            raise LoadError("Either connection string or account key is required")
        return True
        
    def _get_blob_client(self):
        """Get Azure Blob client."""
        try:
            from azure.storage.blob import BlobServiceClient
            
            if self.connection_string:
                blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            else:
                account_url = f"https://{self.account_name}.blob.core.windows.net"
                blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=self.account_key
                )
            
            return blob_service_client.get_blob_client(
                container=self.container_name,
                blob=self.blob_name
            )
        except ImportError:
            raise LoadError("azure-storage-blob is required for Azure Blob loading")
        except Exception as e:
            raise LoadError(f"Failed to create Azure Blob client: {str(e)}")
    
    def load(self, data: Any) -> bool:
        """Load data to Azure Blob Storage."""
        self.validate_config()
        
        try:
            blob_client = self._get_blob_client()
            
            # Convert data to appropriate format
            if self.file_format == "json":
                content = json.dumps(data, indent=2, default=str)
                content_type = "application/json"
            elif self.file_format == "csv":
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    content = df.to_csv(index=False)
                else:
                    raise LoadError("CSV format requires list of dictionaries")
                content_type = "text/csv"
            elif self.file_format == "parquet":
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    buffer = BytesIO()
                    df.to_parquet(buffer, index=False)
                    content = buffer.getvalue()
                else:
                    raise LoadError("Parquet format requires list of dictionaries")
                content_type = "application/octet-stream"
            else:
                # Plain text
                content = str(data)
                content_type = "text/plain"
            
            # Upload to Azure Blob
            if isinstance(content, str):
                blob_client.upload_blob(
                    content.encode('utf-8'),
                    overwrite=True,
                    content_settings={'content_type': content_type}
                )
            else:
                blob_client.upload_blob(
                    content,
                    overwrite=True,
                    content_settings={'content_type': content_type}
                )
            
            record_count = len(data) if isinstance(data, list) else 1
            self.logger.info(f"Successfully loaded {record_count} records to Azure Blob: {self.blob_name}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to Azure Blob: {str(e)}")
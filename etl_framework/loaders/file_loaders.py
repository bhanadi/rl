"""
File-based data loaders.
"""
import json
import pandas as pd
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..core.base import Loader
from ..core.exceptions import LoadError


class CSVLoader(Loader):
    """Load data to CSV files."""
    
    def __init__(self, name: str, file_path: str, mode: str = "w", **csv_kwargs):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.mode = mode
        self.csv_kwargs = csv_kwargs
        
    def validate_config(self) -> bool:
        """Validate CSV loader configuration."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        return True
        
    def load(self, data: List[Dict[str, Any]]) -> bool:
        """Load data to CSV file."""
        self.validate_config()
        
        if not isinstance(data, list):
            raise LoadError("CSVLoader expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Set default CSV parameters
            csv_params = {
                'index': False,
                'mode': self.mode,
                **self.csv_kwargs
            }
            
            # Handle append mode
            if self.mode == 'a' and self.file_path.exists():
                csv_params['header'] = False
            
            df.to_csv(self.file_path, **csv_params)
            
            self.logger.info(f"Successfully loaded {len(data)} records to CSV: {self.file_path}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to CSV {self.file_path}: {str(e)}")


class JSONLoader(Loader):
    """Load data to JSON files."""
    
    def __init__(self, name: str, file_path: str, mode: str = "w", 
                 indent: Optional[int] = 2, ensure_ascii: bool = False):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.mode = mode
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        
    def validate_config(self) -> bool:
        """Validate JSON loader configuration."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        return True
        
    def load(self, data: Any) -> bool:
        """Load data to JSON file."""
        self.validate_config()
        
        try:
            if self.mode == 'a' and self.file_path.exists():
                # Append mode: load existing data and merge
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                if isinstance(existing_data, list) and isinstance(data, list):
                    combined_data = existing_data + data
                else:
                    combined_data = data
                
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, indent=self.indent, 
                             ensure_ascii=self.ensure_ascii, default=str)
            else:
                # Write mode
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=self.indent, 
                             ensure_ascii=self.ensure_ascii, default=str)
            
            record_count = len(data) if isinstance(data, list) else 1
            self.logger.info(f"Successfully loaded {record_count} records to JSON: {self.file_path}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to JSON {self.file_path}: {str(e)}")


class ExcelLoader(Loader):
    """Load data to Excel files."""
    
    def __init__(self, name: str, file_path: str, sheet_name: str = "Sheet1", 
                 mode: str = "w", **excel_kwargs):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.mode = mode
        self.excel_kwargs = excel_kwargs
        
    def validate_config(self) -> bool:
        """Validate Excel loader configuration."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        return True
        
    def load(self, data: List[Dict[str, Any]]) -> bool:
        """Load data to Excel file."""
        self.validate_config()
        
        if not isinstance(data, list):
            raise LoadError("ExcelLoader expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Set default Excel parameters
            excel_params = {
                'index': False,
                'sheet_name': self.sheet_name,
                **self.excel_kwargs
            }
            
            if self.mode == 'a' and self.file_path.exists():
                # Append mode: add to existing workbook
                with pd.ExcelWriter(self.file_path, mode='a', 
                                   if_sheet_exists='replace') as writer:
                    df.to_excel(writer, **excel_params)
            else:
                # Write mode: create new workbook
                with pd.ExcelWriter(self.file_path, mode='w') as writer:
                    df.to_excel(writer, **excel_params)
            
            self.logger.info(f"Successfully loaded {len(data)} records to Excel: {self.file_path}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to Excel {self.file_path}: {str(e)}")


class ParquetLoader(Loader):
    """Load data to Parquet files."""
    
    def __init__(self, name: str, file_path: str, **parquet_kwargs):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.parquet_kwargs = parquet_kwargs
        
    def validate_config(self) -> bool:
        """Validate Parquet loader configuration."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        return True
        
    def load(self, data: List[Dict[str, Any]]) -> bool:
        """Load data to Parquet file."""
        self.validate_config()
        
        if not isinstance(data, list):
            raise LoadError("ParquetLoader expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Set default Parquet parameters
            parquet_params = {
                'index': False,
                **self.parquet_kwargs
            }
            
            df.to_parquet(self.file_path, **parquet_params)
            
            self.logger.info(f"Successfully loaded {len(data)} records to Parquet: {self.file_path}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to Parquet {self.file_path}: {str(e)}")


class TextLoader(Loader):
    """Load data to text files."""
    
    def __init__(self, name: str, file_path: str, mode: str = "w", 
                 separator: str = "\n", encoding: str = "utf-8"):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.mode = mode
        self.separator = separator
        self.encoding = encoding
        
    def validate_config(self) -> bool:
        """Validate text loader configuration."""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        return True
        
    def load(self, data: List[str]) -> bool:
        """Load data to text file."""
        self.validate_config()
        
        if not isinstance(data, list):
            raise LoadError("TextLoader expects list of strings")
        
        try:
            with open(self.file_path, self.mode, encoding=self.encoding) as f:
                content = self.separator.join(str(item) for item in data)
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
            
            self.logger.info(f"Successfully loaded {len(data)} lines to text file: {self.file_path}")
            return True
            
        except Exception as e:
            raise LoadError(f"Failed to load to text file {self.file_path}: {str(e)}")
"""
File-based data extractors.
"""
import json
import csv
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..core.base import Extractor
from ..core.exceptions import ExtractionError


class CSVExtractor(Extractor):
    """Extract data from CSV files."""
    
    def __init__(self, name: str, file_path: str, **csv_kwargs):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.csv_kwargs = csv_kwargs
        
    def validate_config(self) -> bool:
        """Validate CSV extractor configuration."""
        if not self.file_path.exists():
            raise ExtractionError(f"CSV file not found: {self.file_path}")
        return True
        
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from CSV file."""
        self.validate_config()
        
        try:
            df = pd.read_csv(self.file_path, **self.csv_kwargs)
            return df.to_dict('records')
        except Exception as e:
            raise ExtractionError(f"Failed to extract from CSV {self.file_path}: {str(e)}")


class JSONExtractor(Extractor):
    """Extract data from JSON files."""
    
    def __init__(self, name: str, file_path: str, json_path: Optional[str] = None):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.json_path = json_path  # JSONPath for nested data extraction
        
    def validate_config(self) -> bool:
        """Validate JSON extractor configuration."""
        if not self.file_path.exists():
            raise ExtractionError(f"JSON file not found: {self.file_path}")
        return True
        
    def extract(self) -> Any:
        """Extract data from JSON file."""
        self.validate_config()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if self.json_path:
                # Simple JSONPath implementation
                return self._extract_by_path(data, self.json_path)
            
            return data
        except Exception as e:
            raise ExtractionError(f"Failed to extract from JSON {self.file_path}: {str(e)}")
    
    def _extract_by_path(self, data: Any, path: str) -> Any:
        """Extract data using a simple dot notation path."""
        current = data
        for part in path.split('.'):
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                current = current[index] if index < len(current) else None
            else:
                return None
        return current


class XMLExtractor(Extractor):
    """Extract data from XML files."""
    
    def __init__(self, name: str, file_path: str, xpath: Optional[str] = None):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.xpath = xpath
        
    def validate_config(self) -> bool:
        """Validate XML extractor configuration."""
        if not self.file_path.exists():
            raise ExtractionError(f"XML file not found: {self.file_path}")
        return True
        
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from XML file."""
        self.validate_config()
        
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            
            if self.xpath:
                elements = root.findall(self.xpath)
            else:
                elements = list(root)
            
            result = []
            for element in elements:
                item = self._element_to_dict(element)
                result.append(item)
                
            return result
        except Exception as e:
            raise ExtractionError(f"Failed to extract from XML {self.file_path}: {str(e)}")
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._element_to_dict(child)
            tag = child.tag
            
            if tag in result:
                # Handle multiple elements with same tag
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_data)
            else:
                result[tag] = child_data
        
        return result


class ExcelExtractor(Extractor):
    """Extract data from Excel files."""
    
    def __init__(self, name: str, file_path: str, sheet_name: Optional[str] = None, **excel_kwargs):
        super().__init__(name)
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.excel_kwargs = excel_kwargs
        
    def validate_config(self) -> bool:
        """Validate Excel extractor configuration."""
        if not self.file_path.exists():
            raise ExtractionError(f"Excel file not found: {self.file_path}")
        return True
        
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from Excel file."""
        self.validate_config()
        
        try:
            df = pd.read_excel(
                self.file_path, 
                sheet_name=self.sheet_name,
                **self.excel_kwargs
            )
            return df.to_dict('records')
        except Exception as e:
            raise ExtractionError(f"Failed to extract from Excel {self.file_path}: {str(e)}")
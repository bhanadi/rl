"""
Base classes for ETL framework components.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging


class BaseETLComponent(ABC):
    """Base class for all ETL components."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
    def validate_config(self) -> bool:
        """Validate component configuration."""
        return True
        
    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the component logic."""
        pass


class Extractor(BaseETLComponent):
    """Base class for data extraction components."""
    
    @abstractmethod
    def extract(self) -> Any:
        """Extract data from source."""
        pass
    
    def execute(self, data: Any = None) -> Any:
        """Execute extraction logic."""
        self.logger.info(f"Starting extraction: {self.name}")
        try:
            result = self.extract()
            self.logger.info(f"Extraction completed: {self.name}")
            return result
        except Exception as e:
            self.logger.error(f"Extraction failed: {self.name} - {str(e)}")
            raise


class Transformer(BaseETLComponent):
    """Base class for data transformation components."""
    
    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform the input data."""
        pass
    
    def execute(self, data: Any) -> Any:
        """Execute transformation logic."""
        self.logger.info(f"Starting transformation: {self.name}")
        try:
            result = self.transform(data)
            self.logger.info(f"Transformation completed: {self.name}")
            return result
        except Exception as e:
            self.logger.error(f"Transformation failed: {self.name} - {str(e)}")
            raise


class Loader(BaseETLComponent):
    """Base class for data loading components."""
    
    @abstractmethod
    def load(self, data: Any) -> bool:
        """Load data to destination."""
        pass
    
    def execute(self, data: Any) -> Any:
        """Execute loading logic."""
        self.logger.info(f"Starting load: {self.name}")
        try:
            result = self.load(data)
            self.logger.info(f"Load completed: {self.name}")
            return result
        except Exception as e:
            self.logger.error(f"Load failed: {self.name} - {str(e)}")
            raise


class Validator(BaseETLComponent):
    """Base class for data validation components."""
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate the data."""
        pass
    
    def execute(self, data: Any) -> Any:
        """Execute validation logic."""
        self.logger.info(f"Starting validation: {self.name}")
        try:
            is_valid = self.validate(data)
            if is_valid:
                self.logger.info(f"Validation passed: {self.name}")
                return data
            else:
                raise ValueError(f"Validation failed: {self.name}")
        except Exception as e:
            self.logger.error(f"Validation error: {self.name} - {str(e)}")
            raise
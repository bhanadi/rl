"""
Custom exceptions for ETL framework.
"""


class ETLError(Exception):
    """Base exception for ETL operations."""
    pass


class ExtractionError(ETLError):
    """Exception raised during data extraction."""
    pass


class TransformationError(ETLError):
    """Exception raised during data transformation."""
    pass


class LoadError(ETLError):
    """Exception raised during data loading."""
    pass


class ValidationError(ETLError):
    """Exception raised during data validation."""
    pass


class ConfigurationError(ETLError):
    """Exception raised for configuration issues."""
    pass


class PipelineError(ETLError):
    """Exception raised during pipeline execution."""
    pass
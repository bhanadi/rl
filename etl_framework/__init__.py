"""
ETL Framework - A comprehensive Python framework for building ETL pipelines.

This framework provides:
- Modular ETL components (Extractors, Transformers, Loaders, Validators)
- Pipeline orchestration and management
- Configuration management
- Logging and monitoring
- Data validation and quality checks
- Support for multiple data sources and destinations
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core imports
from .core import (
    BaseETLComponent,
    Extractor, 
    Transformer, 
    Loader, 
    Validator,
    Pipeline,
    PipelineBuilder,
    ETLError,
    ExtractionError,
    TransformationError,
    LoadError,
    ValidationError
)

# Extractors
from .extractors import (
    CSVExtractor,
    JSONExtractor,
    XMLExtractor,
    SQLExtractor,
    NoSQLExtractor,
    APIExtractor,
    WebScrapingExtractor
)

# Transformers
from .transformers import (
    FilterTransformer,
    ColumnSelectTransformer,
    DataTypeTransformer,
    AggregateTransformer,
    JoinTransformer,
    NullValueTransformer,
    DuplicateRemovalTransformer,
    TextCleaningTransformer,
    DateNormalizationTransformer,
    CustomFunctionTransformer
)

# Loaders
from .loaders import (
    CSVLoader,
    JSONLoader,
    ExcelLoader,
    SQLLoader,
    NoSQLLoader,
    S3Loader,
    AzureBlobLoader
)

# Validators
from .validators import (
    SchemaValidator,
    DataQualityValidator,
    BusinessRuleValidator,
    StatisticalValidator
)

# Utilities
from .utils import (
    ConfigManager,
    setup_logging,
    data_profiler,
    memory_usage,
    execution_timer,
    retry_on_failure
)

__all__ = [
    # Core components
    'BaseETLComponent',
    'Extractor',
    'Transformer', 
    'Loader',
    'Validator',
    'Pipeline',
    'PipelineBuilder',
    
    # Exceptions
    'ETLError',
    'ExtractionError',
    'TransformationError',
    'LoadError', 
    'ValidationError',
    
    # Extractors
    'CSVExtractor',
    'JSONExtractor',
    'XMLExtractor', 
    'SQLExtractor',
    'NoSQLExtractor',
    'APIExtractor',
    'WebScrapingExtractor',
    
    # Transformers
    'FilterTransformer',
    'ColumnSelectTransformer',
    'DataTypeTransformer',
    'AggregateTransformer',
    'JoinTransformer',
    'NullValueTransformer',
    'DuplicateRemovalTransformer',
    'TextCleaningTransformer',
    'DateNormalizationTransformer',
    'CustomFunctionTransformer',
    
    # Loaders
    'CSVLoader',
    'JSONLoader',
    'ExcelLoader',
    'SQLLoader',
    'NoSQLLoader', 
    'S3Loader',
    'AzureBlobLoader',
    
    # Validators
    'SchemaValidator',
    'DataQualityValidator',
    'BusinessRuleValidator',
    'StatisticalValidator',
    
    # Utilities
    'ConfigManager',
    'setup_logging',
    'data_profiler',
    'memory_usage',
    'execution_timer',
    'retry_on_failure'
]
"""
ETL Pipeline orchestration classes.
"""
from typing import Any, List, Dict, Optional, Callable
import logging
from datetime import datetime
import time

from .base import BaseETLComponent, Extractor, Transformer, Loader, Validator
from .exceptions import PipelineError, ConfigurationError


class PipelineMetrics:
    """Class to track pipeline execution metrics."""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration: Optional[float] = None
        self.success: bool = False
        self.errors: List[str] = []
        self.records_processed: int = 0
        
    def start(self):
        """Mark pipeline start."""
        self.start_time = datetime.now()
        
    def stop(self, success: bool = True):
        """Mark pipeline end."""
        self.end_time = datetime.now()
        self.success = success
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    def add_error(self, error: str):
        """Add an error to the metrics."""
        self.errors.append(error)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'success': self.success,
            'records_processed': self.records_processed,
            'errors': self.errors
        }


class Pipeline:
    """Main ETL Pipeline class."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.extractors: List[Extractor] = []
        self.transformers: List[Transformer] = []
        self.loaders: List[Loader] = []
        self.validators: List[Validator] = []
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
        self.error_handlers: List[Callable] = []
        self.logger = logging.getLogger(f"etl.pipeline.{name}")
        self.metrics = PipelineMetrics()
        
    def add_extractor(self, extractor: Extractor) -> 'Pipeline':
        """Add an extractor to the pipeline."""
        if not isinstance(extractor, Extractor):
            raise ConfigurationError(f"Expected Extractor, got {type(extractor)}")
        self.extractors.append(extractor)
        return self
        
    def add_transformer(self, transformer: Transformer) -> 'Pipeline':
        """Add a transformer to the pipeline."""
        if not isinstance(transformer, Transformer):
            raise ConfigurationError(f"Expected Transformer, got {type(transformer)}")
        self.transformers.append(transformer)
        return self
        
    def add_loader(self, loader: Loader) -> 'Pipeline':
        """Add a loader to the pipeline."""
        if not isinstance(loader, Loader):
            raise ConfigurationError(f"Expected Loader, got {type(loader)}")
        self.loaders.append(loader)
        return self
        
    def add_validator(self, validator: Validator) -> 'Pipeline':
        """Add a validator to the pipeline."""
        if not isinstance(validator, Validator):
            raise ConfigurationError(f"Expected Validator, got {type(validator)}")
        self.validators.append(validator)
        return self
        
    def add_pre_hook(self, hook: Callable) -> 'Pipeline':
        """Add a pre-execution hook."""
        self.pre_hooks.append(hook)
        return self
        
    def add_post_hook(self, hook: Callable) -> 'Pipeline':
        """Add a post-execution hook."""
        self.post_hooks.append(hook)
        return self
        
    def add_error_handler(self, handler: Callable) -> 'Pipeline':
        """Add an error handler."""
        self.error_handlers.append(handler)
        return self
        
    def validate_pipeline(self) -> bool:
        """Validate pipeline configuration."""
        if not self.extractors:
            raise ConfigurationError("Pipeline must have at least one extractor")
        if not self.loaders:
            raise ConfigurationError("Pipeline must have at least one loader")
        return True
        
    def _execute_hooks(self, hooks: List[Callable], *args, **kwargs):
        """Execute a list of hooks."""
        for hook in hooks:
            try:
                hook(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Hook execution failed: {str(e)}")
                
    def _handle_error(self, error: Exception, context: str):
        """Handle pipeline errors."""
        error_msg = f"{context}: {str(error)}"
        self.metrics.add_error(error_msg)
        self.logger.error(error_msg)
        
        for handler in self.error_handlers:
            try:
                handler(error, context)
            except Exception as e:
                self.logger.error(f"Error handler failed: {str(e)}")
                
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the complete ETL pipeline."""
        self.logger.info(f"Starting pipeline: {self.name}")
        self.metrics.start()
        
        try:
            # Validate pipeline
            self.validate_pipeline()
            
            # Execute pre-hooks
            self._execute_hooks(self.pre_hooks, pipeline=self, **kwargs)
            
            # Extract data
            data = None
            for extractor in self.extractors:
                try:
                    extracted = extractor.execute()
                    if data is None:
                        data = extracted
                    else:
                        # Merge or combine data from multiple extractors
                        if isinstance(data, list) and isinstance(extracted, list):
                            data.extend(extracted)
                        elif isinstance(data, dict) and isinstance(extracted, dict):
                            data.update(extracted)
                        else:
                            data = [data, extracted] if not isinstance(data, list) else data + [extracted]
                except Exception as e:
                    self._handle_error(e, f"Extraction ({extractor.name})")
                    raise PipelineError(f"Extraction failed: {extractor.name}") from e
            
            # Validate extracted data
            for validator in self.validators:
                try:
                    data = validator.execute(data)
                except Exception as e:
                    self._handle_error(e, f"Validation ({validator.name})")
                    raise PipelineError(f"Validation failed: {validator.name}") from e
            
            # Transform data
            for transformer in self.transformers:
                try:
                    data = transformer.execute(data)
                except Exception as e:
                    self._handle_error(e, f"Transformation ({transformer.name})")
                    raise PipelineError(f"Transformation failed: {transformer.name}") from e
            
            # Load data
            for loader in self.loaders:
                try:
                    loader.execute(data)
                except Exception as e:
                    self._handle_error(e, f"Loading ({loader.name})")
                    raise PipelineError(f"Loading failed: {loader.name}") from e
            
            # Update metrics
            if isinstance(data, (list, tuple)):
                self.metrics.records_processed = len(data)
            elif isinstance(data, dict):
                self.metrics.records_processed = len(data.get('records', []))
            else:
                self.metrics.records_processed = 1 if data is not None else 0
            
            # Execute post-hooks
            self._execute_hooks(self.post_hooks, pipeline=self, data=data, **kwargs)
            
            self.metrics.stop(success=True)
            self.logger.info(f"Pipeline completed successfully: {self.name}")
            
            return {
                'success': True,
                'metrics': self.metrics.to_dict(),
                'message': f"Pipeline {self.name} completed successfully"
            }
            
        except Exception as e:
            self.metrics.stop(success=False)
            self.logger.error(f"Pipeline failed: {self.name} - {str(e)}")
            
            return {
                'success': False,
                'metrics': self.metrics.to_dict(),
                'error': str(e),
                'message': f"Pipeline {self.name} failed"
            }


class PipelineBuilder:
    """Builder class for creating ETL pipelines."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.pipeline = Pipeline(name, description)
        
    def extract_from(self, extractor: Extractor) -> 'PipelineBuilder':
        """Add an extractor to the pipeline."""
        self.pipeline.add_extractor(extractor)
        return self
        
    def transform_with(self, transformer: Transformer) -> 'PipelineBuilder':
        """Add a transformer to the pipeline."""
        self.pipeline.add_transformer(transformer)
        return self
        
    def load_to(self, loader: Loader) -> 'PipelineBuilder':
        """Add a loader to the pipeline."""
        self.pipeline.add_loader(loader)
        return self
        
    def validate_with(self, validator: Validator) -> 'PipelineBuilder':
        """Add a validator to the pipeline."""
        self.pipeline.add_validator(validator)
        return self
        
    def with_pre_hook(self, hook: Callable) -> 'PipelineBuilder':
        """Add a pre-execution hook."""
        self.pipeline.add_pre_hook(hook)
        return self
        
    def with_post_hook(self, hook: Callable) -> 'PipelineBuilder':
        """Add a post-execution hook."""
        self.pipeline.add_post_hook(hook)
        return self
        
    def with_error_handler(self, handler: Callable) -> 'PipelineBuilder':
        """Add an error handler."""
        self.pipeline.add_error_handler(handler)
        return self
        
    def build(self) -> Pipeline:
        """Build and return the configured pipeline."""
        return self.pipeline
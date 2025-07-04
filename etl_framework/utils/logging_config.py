"""
Logging configuration utilities.
"""
import logging
import logging.handlers
import sys
from typing import Dict, Any, Optional
from pathlib import Path


def setup_logging(config: Optional[Dict[str, Any]] = None, log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration for ETL framework."""
    
    # Default configuration
    default_config = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'handlers': {
            'console': {
                'type': 'console',
                'level': 'INFO'
            }
        }
    }
    
    # Merge with provided config
    if config:
        _deep_merge(default_config, config)
    
    logging_config = default_config
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set logging level
    level = getattr(logging, logging_config['level'].upper())
    root_logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(logging_config['format'])
    
    # Set up handlers
    for handler_name, handler_config in logging_config['handlers'].items():
        handler = _create_handler(handler_config, log_file)
        if handler:
            handler.setFormatter(formatter)
            
            # Set handler level
            handler_level = getattr(logging, handler_config.get('level', 'INFO').upper())
            handler.setLevel(handler_level)
            
            root_logger.addHandler(handler)
    
    # Create ETL framework logger
    etl_logger = logging.getLogger('etl_framework')
    
    return etl_logger


def _create_handler(config: Dict[str, Any], log_file: Optional[str] = None) -> Optional[logging.Handler]:
    """Create a logging handler based on configuration."""
    handler_type = config.get('type', 'console').lower()
    
    if handler_type == 'console':
        handler = logging.StreamHandler(sys.stdout)
    elif handler_type == 'file':
        log_path = log_file or config.get('filename', 'etl_framework.log')
        log_path = Path(log_path)
        
        # Create log directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        max_bytes = config.get('max_bytes', 10 * 1024 * 1024)  # 10MB default
        backup_count = config.get('backup_count', 5)
        
        handler = logging.handlers.RotatingFileHandler(
            log_path, 
            maxBytes=max_bytes, 
            backupCount=backup_count
        )
    elif handler_type == 'syslog':
        handler = logging.handlers.SysLogHandler()
    elif handler_type == 'null':
        handler = logging.NullHandler()
    else:
        print(f"Warning: Unknown handler type '{handler_type}', skipping")
        return None
    
    return handler


def _deep_merge(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """Recursively merge dictionaries."""
    for key, value in update_dict.items():
        if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
            _deep_merge(base_dict[key], value)
        else:
            base_dict[key] = value


class ETLLogger:
    """Custom logger for ETL operations with context."""
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = ' | '.join([f"{k}={v}" for k, v in self.context.items()])
            return f"[{context_str}] {message}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(self._format_message(message), **kwargs)
    
    def set_context(self, **context):
        """Update logger context."""
        self.context.update(context)
    
    def clear_context(self):
        """Clear logger context."""
        self.context.clear()
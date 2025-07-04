"""
Configuration management utilities.
"""
import json
import yaml
import os
from typing import Any, Dict, Optional, List
from pathlib import Path


class ConfigManager:
    """Manage ETL pipeline configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else None
        self.config_data: Dict[str, Any] = {}
        
        if self.config_path and self.config_path.exists():
            self.load_config()
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file."""
        if config_path:
            self.config_path = Path(config_path)
        
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() in ['.yml', '.yaml']:
                    self.config_data = yaml.safe_load(f)
                elif self.config_path.suffix.lower() == '.json':
                    self.config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {self.config_path.suffix}")
            
            # Process environment variable substitutions
            self.config_data = self._substitute_env_vars(self.config_data)
            
            return self.config_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {str(e)}")
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file."""
        if config_path:
            self.config_path = Path(config_path)
        
        if not self.config_path:
            raise ValueError("No configuration path specified")
        
        # Create parent directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.safe_dump(self.config_data, f, default_flow_style=False, indent=2)
                elif self.config_path.suffix.lower() == '.json':
                    json.dump(self.config_data, f, indent=2)
                else:
                    raise ValueError(f"Unsupported config file format: {self.config_path.suffix}")
                    
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        current = self.config_data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        current = self.config_data
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration with dictionary."""
        self._deep_update(self.config_data, config_dict)
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """Substitute environment variables in configuration."""
        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Look for ${VAR_NAME} or ${VAR_NAME:default_value} patterns
            import re
            pattern = r'\$\{([^}]+)\}'
            
            def replace_var(match):
                var_expr = match.group(1)
                if ':' in var_expr:
                    var_name, default_value = var_expr.split(':', 1)
                    return os.environ.get(var_name.strip(), default_value.strip())
                else:
                    return os.environ.get(var_expr.strip(), match.group(0))
            
            return re.sub(pattern, replace_var, obj)
        else:
            return obj
    
    def get_database_config(self, db_name: str) -> Dict[str, Any]:
        """Get database configuration by name."""
        return self.get(f'databases.{db_name}', {})
    
    def get_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        """Get pipeline configuration by name."""
        return self.get(f'pipelines.{pipeline_name}', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'handlers': {
                'console': {
                    'type': 'console',
                    'level': 'INFO'
                }
            }
        })
    
    def validate_config(self, schema: Dict[str, Any]) -> bool:
        """Validate configuration against schema."""
        # This is a basic implementation
        # You might want to use a library like jsonschema for more complex validation
        
        def validate_recursive(data: Any, schema_part: Any, path: str = "") -> List[str]:
            errors = []
            
            if isinstance(schema_part, dict):
                if 'type' in schema_part:
                    expected_type = schema_part['type']
                    if expected_type == 'dict' and not isinstance(data, dict):
                        errors.append(f"{path}: Expected dict, got {type(data).__name__}")
                    elif expected_type == 'list' and not isinstance(data, list):
                        errors.append(f"{path}: Expected list, got {type(data).__name__}")
                    elif expected_type == 'str' and not isinstance(data, str):
                        errors.append(f"{path}: Expected string, got {type(data).__name__}")
                    elif expected_type == 'int' and not isinstance(data, int):
                        errors.append(f"{path}: Expected integer, got {type(data).__name__}")
                    elif expected_type == 'float' and not isinstance(data, (int, float)):
                        errors.append(f"{path}: Expected number, got {type(data).__name__}")
                
                if 'required' in schema_part and isinstance(data, dict):
                    for required_key in schema_part['required']:
                        if required_key not in data:
                            errors.append(f"{path}: Missing required key '{required_key}'")
                
                if 'properties' in schema_part and isinstance(data, dict):
                    for key, sub_schema in schema_part['properties'].items():
                        if key in data:
                            sub_path = f"{path}.{key}" if path else key
                            errors.extend(validate_recursive(data[key], sub_schema, sub_path))
            
            return errors
        
        validation_errors = validate_recursive(self.config_data, schema)
        
        if validation_errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(validation_errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config_data.copy()
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.config_data, indent=2, default=str)
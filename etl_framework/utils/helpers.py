"""
Helper utilities for ETL operations.
"""
import time
import psutil
import pandas as pd
from typing import Any, Dict, List, Callable, Optional
from functools import wraps
import logging


def data_profiler(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a data profile report."""
    if not isinstance(data, list) or not data:
        return {
            'record_count': 0,
            'columns': {},
            'summary': 'No data to profile'
        }
    
    try:
        df = pd.DataFrame(data)
        
        profile = {
            'record_count': len(df),
            'column_count': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'columns': {},
            'data_quality': {
                'duplicate_rows': df.duplicated().sum(),
                'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100
            }
        }
        
        # Profile each column
        for column in df.columns:
            col_profile = {
                'data_type': str(df[column].dtype),
                'non_null_count': df[column].notna().sum(),
                'null_count': df[column].isnull().sum(),
                'null_percentage': (df[column].isnull().sum() / len(df)) * 100,
                'unique_count': df[column].nunique(),
                'unique_percentage': (df[column].nunique() / len(df)) * 100
            }
            
            # Add type-specific statistics
            if pd.api.types.is_numeric_dtype(df[column]):
                col_profile.update({
                    'min': df[column].min(),
                    'max': df[column].max(),
                    'mean': df[column].mean(),
                    'median': df[column].median(),
                    'std': df[column].std(),
                    'quantiles': {
                        '25%': df[column].quantile(0.25),
                        '75%': df[column].quantile(0.75)
                    }
                })
            elif pd.api.types.is_string_dtype(df[column]):
                col_profile.update({
                    'min_length': df[column].str.len().min(),
                    'max_length': df[column].str.len().max(),
                    'avg_length': df[column].str.len().mean(),
                    'most_common': df[column].value_counts().head(5).to_dict()
                })
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                col_profile.update({
                    'min_date': df[column].min(),
                    'max_date': df[column].max(),
                    'date_range_days': (df[column].max() - df[column].min()).days
                })
            
            profile['columns'][column] = col_profile
        
        return profile
        
    except Exception as e:
        return {
            'error': f"Failed to profile data: {str(e)}",
            'record_count': len(data) if data else 0
        }


def memory_usage() -> Dict[str, float]:
    """Get current memory usage statistics."""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'total_mb': psutil.virtual_memory().total / 1024 / 1024
        }
    except Exception as e:
        return {'error': f"Failed to get memory usage: {str(e)}"}


def execution_timer(func: Optional[Callable] = None, *, logger: Optional[logging.Logger] = None):
    """Decorator to time function execution."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                
                message = f"{f.__name__} executed in {execution_time:.4f} seconds"
                if logger:
                    logger.info(message)
                else:
                    print(message)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                message = f"{f.__name__} failed after {execution_time:.4f} seconds: {str(e)}"
                if logger:
                    logger.error(message)
                else:
                    print(message)
                raise
                
        return wrapper
    
    if func is None:
        # Decorator called with arguments
        return decorator
    else:
        # Decorator called without arguments
        return decorator(func)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    exponential_backoff: bool = True,
                    exceptions: tuple = (Exception,),
                    logger: Optional[logging.Logger] = None):
    """Decorator to retry function execution on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        message = f"{func.__name__} succeeded on attempt {attempt + 1}"
                        if logger:
                            logger.info(message)
                        else:
                            print(message)
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        message = f"{func.__name__} failed on attempt {attempt + 1}, retrying in {current_delay}s: {str(e)}"
                        if logger:
                            logger.warning(message)
                        else:
                            print(message)
                        
                        time.sleep(current_delay)
                        
                        if exponential_backoff:
                            current_delay *= 2
                    else:
                        message = f"{func.__name__} failed after {max_retries + 1} attempts: {str(e)}"
                        if logger:
                            logger.error(message)
                        else:
                            print(message)
            
            # If we get here, all retries failed
            raise last_exception
            
        return wrapper
    
    return decorator


class ProgressTracker:
    """Track progress of ETL operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        
    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        self._print_progress()
    
    def _print_progress(self):
        """Print current progress."""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed_time = time.time() - self.start_time
            
            if self.current > 0:
                eta = (elapsed_time / self.current) * (self.total - self.current)
                eta_str = f"ETA: {eta:.1f}s"
            else:
                eta_str = "ETA: --"
            
            progress_bar = "█" * int(percentage // 2) + "░" * (50 - int(percentage // 2))
            
            print(f"\r{self.description}: [{progress_bar}] {percentage:.1f}% ({self.current}/{self.total}) | {eta_str}", end="")
            
            if self.current >= self.total:
                print()  # New line when complete
    
    def finish(self):
        """Mark progress as complete."""
        self.current = self.total
        self._print_progress()


def validate_data_types(data: List[Dict[str, Any]], expected_types: Dict[str, type]) -> List[str]:
    """Validate data types in a dataset."""
    if not data:
        return []
    
    errors = []
    
    for i, record in enumerate(data):
        for field, expected_type in expected_types.items():
            if field in record:
                value = record[field]
                if value is not None and not isinstance(value, expected_type):
                    errors.append(f"Record {i}: Field '{field}' expected {expected_type.__name__}, got {type(value).__name__}")
            else:
                errors.append(f"Record {i}: Missing required field '{field}'")
    
    return errors


def chunk_data(data: List[Any], chunk_size: int):
    """Split data into chunks of specified size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def compare_datasets(data1: List[Dict[str, Any]], data2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare two datasets and return differences."""
    if not data1 and not data2:
        return {'identical': True, 'differences': []}
    
    try:
        df1 = pd.DataFrame(data1) if data1 else pd.DataFrame()
        df2 = pd.DataFrame(data2) if data2 else pd.DataFrame()
        
        comparison = {
            'identical': False,
            'record_count_diff': len(df2) - len(df1),
            'column_differences': {
                'added': list(set(df2.columns) - set(df1.columns)),
                'removed': list(set(df1.columns) - set(df2.columns)),
                'common': list(set(df1.columns) & set(df2.columns))
            },
            'data_differences': []
        }
        
        # Check if datasets are identical
        if df1.equals(df2):
            comparison['identical'] = True
            return comparison
        
        # Compare common columns
        for column in comparison['column_differences']['common']:
            if not df1[column].equals(df2[column]):
                diff_count = (df1[column] != df2[column]).sum() if len(df1) == len(df2) else 'N/A (different lengths)'
                comparison['data_differences'].append({
                    'column': column,
                    'differences': diff_count
                })
        
        return comparison
        
    except Exception as e:
        return {'error': f"Failed to compare datasets: {str(e)}"}


def sanitize_column_names(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sanitize column names to be database-friendly."""
    if not data:
        return data
    
    # Create mapping of old to new column names
    sample_record = data[0]
    column_mapping = {}
    
    for old_name in sample_record.keys():
        # Remove special characters and replace spaces with underscores
        new_name = ''.join(c if c.isalnum() else '_' for c in old_name)
        new_name = new_name.lower().strip('_')
        
        # Ensure name doesn't start with number
        if new_name and new_name[0].isdigit():
            new_name = f"col_{new_name}"
        
        # Handle empty names
        if not new_name:
            new_name = "unnamed_column"
        
        column_mapping[old_name] = new_name
    
    # Apply mapping to all records
    sanitized_data = []
    for record in data:
        sanitized_record = {column_mapping[k]: v for k, v in record.items()}
        sanitized_data.append(sanitized_record)
    
    return sanitized_data
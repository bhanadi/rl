"""
Data cleaning transformation components.
"""
import pandas as pd
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..core.base import Transformer
from ..core.exceptions import TransformationError


class NullValueTransformer(Transformer):
    """Handle null/missing values in data."""
    
    def __init__(self, name: str, strategy: str = "drop", fill_value: Any = None, 
                 columns: Optional[List[str]] = None):
        super().__init__(name)
        self.strategy = strategy.lower()
        self.fill_value = fill_value
        self.columns = columns
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle null values according to strategy."""
        if not isinstance(data, list):
            raise TransformationError("NullValueTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Select columns to process
            target_columns = self.columns if self.columns else df.columns
            
            if self.strategy == "drop":
                # Drop rows with null values
                df = df.dropna(subset=target_columns)
            elif self.strategy == "fill":
                # Fill null values with specified value
                fill_dict = {col: self.fill_value for col in target_columns}
                df = df.fillna(fill_dict)
            elif self.strategy == "forward_fill":
                # Forward fill
                df[target_columns] = df[target_columns].fillna(method='ffill')
            elif self.strategy == "backward_fill":
                # Backward fill
                df[target_columns] = df[target_columns].fillna(method='bfill')
            elif self.strategy == "mean":
                # Fill with mean (numeric columns only)
                for col in target_columns:
                    if df[col].dtype in ['int64', 'float64']:
                        df[col] = df[col].fillna(df[col].mean())
            elif self.strategy == "median":
                # Fill with median (numeric columns only)
                for col in target_columns:
                    if df[col].dtype in ['int64', 'float64']:
                        df[col] = df[col].fillna(df[col].median())
            elif self.strategy == "mode":
                # Fill with mode
                for col in target_columns:
                    mode_value = df[col].mode()
                    if len(mode_value) > 0:
                        df[col] = df[col].fillna(mode_value.iloc[0])
            else:
                raise TransformationError(f"Unknown null handling strategy: {self.strategy}")
            
            return df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to handle null values: {str(e)}")


class DuplicateRemovalTransformer(Transformer):
    """Remove duplicate records from data."""
    
    def __init__(self, name: str, subset: Optional[List[str]] = None, keep: str = "first"):
        super().__init__(name)
        self.subset = subset
        self.keep = keep
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate records."""
        if not isinstance(data, list):
            raise TransformationError("DuplicateRemovalTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Remove duplicates
            df_dedup = df.drop_duplicates(subset=self.subset, keep=self.keep)
            
            return df_dedup.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to remove duplicates: {str(e)}")


class TextCleaningTransformer(Transformer):
    """Clean and normalize text data."""
    
    def __init__(self, name: str, columns: List[str], operations: List[str]):
        super().__init__(name)
        self.columns = columns
        self.operations = operations
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean text data according to specified operations."""
        if not isinstance(data, list):
            raise TransformationError("TextCleaningTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            for column in self.columns:
                if column not in df.columns:
                    continue
                    
                # Convert to string
                df[column] = df[column].astype(str)
                
                for operation in self.operations:
                    if operation == "lowercase":
                        df[column] = df[column].str.lower()
                    elif operation == "uppercase":
                        df[column] = df[column].str.upper()
                    elif operation == "strip":
                        df[column] = df[column].str.strip()
                    elif operation == "remove_whitespace":
                        df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
                    elif operation == "remove_punctuation":
                        df[column] = df[column].str.replace(r'[^\w\s]', '', regex=True)
                    elif operation == "remove_digits":
                        df[column] = df[column].str.replace(r'\d+', '', regex=True)
                    elif operation == "remove_special_chars":
                        df[column] = df[column].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
                    elif operation == "normalize_spaces":
                        df[column] = df[column].str.replace(r'\s+', ' ', regex=True).str.strip()
            
            return df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to clean text: {str(e)}")


class DateNormalizationTransformer(Transformer):
    """Normalize date formats."""
    
    def __init__(self, name: str, date_columns: List[str], 
                 input_format: Optional[str] = None, output_format: str = "%Y-%m-%d"):
        super().__init__(name)
        self.date_columns = date_columns
        self.input_format = input_format
        self.output_format = output_format
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize date formats."""
        if not isinstance(data, list):
            raise TransformationError("DateNormalizationTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            for column in self.date_columns:
                if column not in df.columns:
                    continue
                
                # Convert to datetime
                if self.input_format:
                    df[column] = pd.to_datetime(df[column], format=self.input_format, errors='coerce')
                else:
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                
                # Format output
                df[column] = df[column].dt.strftime(self.output_format)
            
            return df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to normalize dates: {str(e)}")


class OutlierRemovalTransformer(Transformer):
    """Remove outliers from numeric data."""
    
    def __init__(self, name: str, columns: List[str], method: str = "iqr", threshold: float = 1.5):
        super().__init__(name)
        self.columns = columns
        self.method = method.lower()
        self.threshold = threshold
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove outliers based on specified method."""
        if not isinstance(data, list):
            raise TransformationError("OutlierRemovalTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            mask = pd.Series([True] * len(df))
            
            for column in self.columns:
                if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
                    continue
                
                if self.method == "iqr":
                    # Interquartile Range method
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - self.threshold * IQR
                    upper_bound = Q3 + self.threshold * IQR
                    
                    column_mask = (df[column] >= lower_bound) & (df[column] <= upper_bound)
                    
                elif self.method == "zscore":
                    # Z-score method
                    mean = df[column].mean()
                    std = df[column].std()
                    z_scores = abs((df[column] - mean) / std)
                    column_mask = z_scores <= self.threshold
                    
                else:
                    raise TransformationError(f"Unknown outlier removal method: {self.method}")
                
                mask = mask & column_mask
            
            filtered_df = df[mask]
            return filtered_df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to remove outliers: {str(e)}")


class DataValidationTransformer(Transformer):
    """Validate data against rules and remove invalid records."""
    
    def __init__(self, name: str, validation_rules: Dict[str, Dict[str, Any]], 
                 action: str = "drop"):
        super().__init__(name)
        self.validation_rules = validation_rules
        self.action = action.lower()
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate data and handle invalid records."""
        if not isinstance(data, list):
            raise TransformationError("DataValidationTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            mask = pd.Series([True] * len(df))
            
            for column, rules in self.validation_rules.items():
                if column not in df.columns:
                    continue
                
                column_mask = pd.Series([True] * len(df))
                
                for rule_type, rule_value in rules.items():
                    if rule_type == "min_length" and pd.api.types.is_string_dtype(df[column]):
                        column_mask = column_mask & (df[column].str.len() >= rule_value)
                    elif rule_type == "max_length" and pd.api.types.is_string_dtype(df[column]):
                        column_mask = column_mask & (df[column].str.len() <= rule_value)
                    elif rule_type == "min_value" and pd.api.types.is_numeric_dtype(df[column]):
                        column_mask = column_mask & (df[column] >= rule_value)
                    elif rule_type == "max_value" and pd.api.types.is_numeric_dtype(df[column]):
                        column_mask = column_mask & (df[column] <= rule_value)
                    elif rule_type == "regex_pattern":
                        column_mask = column_mask & df[column].str.match(rule_value, na=False)
                    elif rule_type == "not_null":
                        if rule_value:
                            column_mask = column_mask & df[column].notna()
                    elif rule_type == "allowed_values":
                        column_mask = column_mask & df[column].isin(rule_value)
                
                mask = mask & column_mask
            
            if self.action == "drop":
                valid_df = df[mask]
                return valid_df.to_dict('records')
            elif self.action == "flag":
                df['_validation_failed'] = ~mask
                return df.to_dict('records')
            else:
                raise TransformationError(f"Unknown validation action: {self.action}")
            
        except Exception as e:
            raise TransformationError(f"Failed to validate data: {str(e)}")
"""
Common data transformation components.
"""
import pandas as pd
from typing import Any, Dict, List, Optional, Callable, Union
import logging

from ..core.base import Transformer
from ..core.exceptions import TransformationError


class FilterTransformer(Transformer):
    """Filter data based on conditions."""
    
    def __init__(self, name: str, conditions: Union[Dict, Callable], operation: str = "and"):
        super().__init__(name)
        self.conditions = conditions
        self.operation = operation.lower()
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter data based on conditions."""
        if not isinstance(data, list):
            raise TransformationError("FilterTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            if callable(self.conditions):
                # Custom function filter
                mask = df.apply(self.conditions, axis=1)
            elif isinstance(self.conditions, dict):
                # Dictionary-based conditions
                mask = pd.Series([True] * len(df))
                
                for column, condition in self.conditions.items():
                    if column not in df.columns:
                        continue
                        
                    if isinstance(condition, dict):
                        col_mask = self._apply_condition(df[column], condition)
                    else:
                        col_mask = df[column] == condition
                    
                    if self.operation == "and":
                        mask = mask & col_mask
                    elif self.operation == "or":
                        mask = mask | col_mask
            else:
                raise TransformationError("Conditions must be a dictionary or callable")
            
            filtered_df = df[mask]
            return filtered_df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to filter data: {str(e)}")
    
    def _apply_condition(self, series: pd.Series, condition: Dict) -> pd.Series:
        """Apply a single condition to a pandas Series."""
        if 'eq' in condition:
            return series == condition['eq']
        elif 'ne' in condition:
            return series != condition['ne']
        elif 'gt' in condition:
            return series > condition['gt']
        elif 'ge' in condition:
            return series >= condition['ge']
        elif 'lt' in condition:
            return series < condition['lt']
        elif 'le' in condition:
            return series <= condition['le']
        elif 'in' in condition:
            return series.isin(condition['in'])
        elif 'not_in' in condition:
            return ~series.isin(condition['not_in'])
        elif 'contains' in condition:
            return series.str.contains(condition['contains'], na=False)
        elif 'startswith' in condition:
            return series.str.startswith(condition['startswith'], na=False)
        elif 'endswith' in condition:
            return series.str.endswith(condition['endswith'], na=False)
        else:
            return pd.Series([True] * len(series))


class ColumnSelectTransformer(Transformer):
    """Select specific columns from data."""
    
    def __init__(self, name: str, columns: List[str], exclude: bool = False):
        super().__init__(name)
        self.columns = columns
        self.exclude = exclude
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select or exclude specified columns."""
        if not isinstance(data, list):
            raise TransformationError("ColumnSelectTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            if self.exclude:
                # Exclude specified columns
                selected_columns = [col for col in df.columns if col not in self.columns]
            else:
                # Include only specified columns
                selected_columns = [col for col in self.columns if col in df.columns]
            
            if not selected_columns:
                raise TransformationError("No valid columns selected")
            
            result_df = df[selected_columns]
            return result_df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to select columns: {str(e)}")


class DataTypeTransformer(Transformer):
    """Convert data types of columns."""
    
    def __init__(self, name: str, type_mapping: Dict[str, str]):
        super().__init__(name)
        self.type_mapping = type_mapping
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert data types according to mapping."""
        if not isinstance(data, list):
            raise TransformationError("DataTypeTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            for column, dtype in self.type_mapping.items():
                if column in df.columns:
                    if dtype.lower() == 'datetime':
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                    elif dtype.lower() == 'numeric':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif dtype.lower() == 'string':
                        df[column] = df[column].astype(str)
                    elif dtype.lower() == 'boolean':
                        df[column] = df[column].astype(bool)
                    elif dtype.lower() == 'category':
                        df[column] = df[column].astype('category')
                    else:
                        df[column] = df[column].astype(dtype)
            
            return df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to convert data types: {str(e)}")


class AggregateTransformer(Transformer):
    """Aggregate data by grouping columns."""
    
    def __init__(self, name: str, group_by: List[str], aggregations: Dict[str, Union[str, List[str]]]):
        super().__init__(name)
        self.group_by = group_by
        self.aggregations = aggregations
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate data based on grouping and aggregation rules."""
        if not isinstance(data, list):
            raise TransformationError("AggregateTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Check if group_by columns exist
            missing_cols = [col for col in self.group_by if col not in df.columns]
            if missing_cols:
                raise TransformationError(f"Group by columns not found: {missing_cols}")
            
            # Perform aggregation
            agg_df = df.groupby(self.group_by).agg(self.aggregations).reset_index()
            
            # Flatten column names if multi-level
            if isinstance(agg_df.columns, pd.MultiIndex):
                agg_df.columns = ['_'.join(col).strip() if col[1] else col[0] 
                                 for col in agg_df.columns.values]
            
            return agg_df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to aggregate data: {str(e)}")


class JoinTransformer(Transformer):
    """Join data with another dataset."""
    
    def __init__(self, name: str, right_data: List[Dict[str, Any]], 
                 on: Union[str, List[str]], how: str = "inner"):
        super().__init__(name)
        self.right_data = right_data
        self.on = on
        self.how = how.lower()
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Join left data with right data."""
        if not isinstance(data, list):
            raise TransformationError("JoinTransformer expects list of dictionaries")
        
        try:
            left_df = pd.DataFrame(data)
            right_df = pd.DataFrame(self.right_data)
            
            # Perform join
            result_df = left_df.merge(right_df, on=self.on, how=self.how)
            
            return result_df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to join data: {str(e)}")


class RenameColumnsTransformer(Transformer):
    """Rename columns in the data."""
    
    def __init__(self, name: str, column_mapping: Dict[str, str]):
        super().__init__(name)
        self.column_mapping = column_mapping
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rename columns according to mapping."""
        if not isinstance(data, list):
            raise TransformationError("RenameColumnsTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            df = df.rename(columns=self.column_mapping)
            return df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to rename columns: {str(e)}")


class AddColumnTransformer(Transformer):
    """Add new columns to the data."""
    
    def __init__(self, name: str, new_columns: Dict[str, Union[Any, Callable]]):
        super().__init__(name)
        self.new_columns = new_columns
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add new columns to the data."""
        if not isinstance(data, list):
            raise TransformationError("AddColumnTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            for column_name, value_or_func in self.new_columns.items():
                if callable(value_or_func):
                    # Apply function to create column
                    df[column_name] = df.apply(value_or_func, axis=1)
                else:
                    # Use static value
                    df[column_name] = value_or_func
            
            return df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to add columns: {str(e)}")


class SortTransformer(Transformer):
    """Sort data by specified columns."""
    
    def __init__(self, name: str, sort_by: Union[str, List[str]], ascending: Union[bool, List[bool]] = True):
        super().__init__(name)
        self.sort_by = sort_by
        self.ascending = ascending
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by specified columns."""
        if not isinstance(data, list):
            raise TransformationError("SortTransformer expects list of dictionaries")
        
        try:
            df = pd.DataFrame(data)
            
            # Sort data
            sorted_df = df.sort_values(by=self.sort_by, ascending=self.ascending)
            
            return sorted_df.to_dict('records')
            
        except Exception as e:
            raise TransformationError(f"Failed to sort data: {str(e)}")
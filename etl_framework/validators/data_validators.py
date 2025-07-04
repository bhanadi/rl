"""
Data validation components.
"""
import pandas as pd
import re
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime

from ..core.base import Validator
from ..core.exceptions import ValidationError


class SchemaValidator(Validator):
    """Validate data against a defined schema."""
    
    def __init__(self, name: str, schema: Dict[str, Dict[str, Any]], strict: bool = True):
        super().__init__(name)
        self.schema = schema
        self.strict = strict
        
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """Validate data against schema."""
        if not isinstance(data, list):
            raise ValidationError("SchemaValidator expects list of dictionaries")
        
        if not data:
            return True
        
        try:
            df = pd.DataFrame(data)
            errors = []
            
            # Check required columns
            schema_columns = set(self.schema.keys())
            data_columns = set(df.columns)
            
            if self.strict:
                # In strict mode, data must have exactly the schema columns
                missing_columns = schema_columns - data_columns
                extra_columns = data_columns - schema_columns
                
                if missing_columns:
                    errors.append(f"Missing required columns: {missing_columns}")
                if extra_columns:
                    errors.append(f"Unexpected columns: {extra_columns}")
            else:
                # In non-strict mode, just check that required columns exist
                missing_columns = schema_columns - data_columns
                if missing_columns:
                    errors.append(f"Missing required columns: {missing_columns}")
            
            # Validate column types and constraints
            for column, constraints in self.schema.items():
                if column not in df.columns:
                    continue
                
                column_errors = self._validate_column(df[column], column, constraints)
                errors.extend(column_errors)
            
            if errors:
                raise ValidationError(f"Schema validation failed: {'; '.join(errors)}")
            
            return True
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Schema validation error: {str(e)}")
    
    def _validate_column(self, series: pd.Series, column_name: str, constraints: Dict[str, Any]) -> List[str]:
        """Validate a single column against constraints."""
        errors = []
        
        # Check data type
        if 'type' in constraints:
            expected_type = constraints['type'].lower()
            if expected_type == 'string' and not pd.api.types.is_string_dtype(series):
                errors.append(f"Column '{column_name}' should be string type")
            elif expected_type == 'integer' and not pd.api.types.is_integer_dtype(series):
                errors.append(f"Column '{column_name}' should be integer type")
            elif expected_type == 'float' and not pd.api.types.is_numeric_dtype(series):
                errors.append(f"Column '{column_name}' should be numeric type")
            elif expected_type == 'datetime' and not pd.api.types.is_datetime64_any_dtype(series):
                errors.append(f"Column '{column_name}' should be datetime type")
        
        # Check nullable constraint
        if 'nullable' in constraints and not constraints['nullable']:
            null_count = series.isnull().sum()
            if null_count > 0:
                errors.append(f"Column '{column_name}' has {null_count} null values but should not be nullable")
        
        # Check unique constraint
        if 'unique' in constraints and constraints['unique']:
            duplicate_count = series.duplicated().sum()
            if duplicate_count > 0:
                errors.append(f"Column '{column_name}' has {duplicate_count} duplicate values but should be unique")
        
        # Check min/max values for numeric columns
        if pd.api.types.is_numeric_dtype(series):
            if 'min_value' in constraints:
                min_violations = (series < constraints['min_value']).sum()
                if min_violations > 0:
                    errors.append(f"Column '{column_name}' has {min_violations} values below minimum {constraints['min_value']}")
            
            if 'max_value' in constraints:
                max_violations = (series > constraints['max_value']).sum()
                if max_violations > 0:
                    errors.append(f"Column '{column_name}' has {max_violations} values above maximum {constraints['max_value']}")
        
        # Check string length constraints
        if pd.api.types.is_string_dtype(series):
            if 'min_length' in constraints:
                min_length_violations = (series.str.len() < constraints['min_length']).sum()
                if min_length_violations > 0:
                    errors.append(f"Column '{column_name}' has {min_length_violations} values shorter than minimum length {constraints['min_length']}")
            
            if 'max_length' in constraints:
                max_length_violations = (series.str.len() > constraints['max_length']).sum()
                if max_length_violations > 0:
                    errors.append(f"Column '{column_name}' has {max_length_violations} values longer than maximum length {constraints['max_length']}")
        
        # Check allowed values
        if 'allowed_values' in constraints:
            invalid_values = ~series.isin(constraints['allowed_values'])
            invalid_count = invalid_values.sum()
            if invalid_count > 0:
                errors.append(f"Column '{column_name}' has {invalid_count} values not in allowed list")
        
        # Check regex pattern
        if 'pattern' in constraints and pd.api.types.is_string_dtype(series):
            pattern_violations = ~series.str.match(constraints['pattern'], na=False)
            violation_count = pattern_violations.sum()
            if violation_count > 0:
                errors.append(f"Column '{column_name}' has {violation_count} values not matching pattern")
        
        return errors


class DataQualityValidator(Validator):
    """Validate data quality metrics."""
    
    def __init__(self, name: str, quality_rules: Dict[str, Any]):
        super().__init__(name)
        self.quality_rules = quality_rules
        
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """Validate data quality."""
        if not isinstance(data, list):
            raise ValidationError("DataQualityValidator expects list of dictionaries")
        
        if not data:
            return True
        
        try:
            df = pd.DataFrame(data)
            errors = []
            
            # Check minimum record count
            if 'min_records' in self.quality_rules:
                min_records = self.quality_rules['min_records']
                if len(df) < min_records:
                    errors.append(f"Dataset has {len(df)} records but minimum required is {min_records}")
            
            # Check maximum null percentage
            if 'max_null_percentage' in self.quality_rules:
                max_null_pct = self.quality_rules['max_null_percentage']
                for column in df.columns:
                    null_pct = (df[column].isnull().sum() / len(df)) * 100
                    if null_pct > max_null_pct:
                        errors.append(f"Column '{column}' has {null_pct:.2f}% null values, exceeding maximum {max_null_pct}%")
            
            # Check duplicate percentage
            if 'max_duplicate_percentage' in self.quality_rules:
                max_dup_pct = self.quality_rules['max_duplicate_percentage']
                duplicate_pct = (df.duplicated().sum() / len(df)) * 100
                if duplicate_pct > max_dup_pct:
                    errors.append(f"Dataset has {duplicate_pct:.2f}% duplicate records, exceeding maximum {max_dup_pct}%")
            
            # Check column completeness
            if 'required_columns' in self.quality_rules:
                required_columns = set(self.quality_rules['required_columns'])
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    errors.append(f"Missing required columns: {missing_columns}")
            
            # Check data freshness (if timestamp column exists)
            if 'max_age_hours' in self.quality_rules and 'timestamp_column' in self.quality_rules:
                timestamp_col = self.quality_rules['timestamp_column']
                max_age_hours = self.quality_rules['max_age_hours']
                
                if timestamp_col in df.columns:
                    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
                    max_timestamp = df[timestamp_col].max()
                    if pd.notna(max_timestamp):
                        age_hours = (datetime.now() - max_timestamp).total_seconds() / 3600
                        if age_hours > max_age_hours:
                            errors.append(f"Data is {age_hours:.2f} hours old, exceeding maximum {max_age_hours} hours")
            
            if errors:
                raise ValidationError(f"Data quality validation failed: {'; '.join(errors)}")
            
            return True
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Data quality validation error: {str(e)}")


class BusinessRuleValidator(Validator):
    """Validate business rules."""
    
    def __init__(self, name: str, rules: List[Dict[str, Any]]):
        super().__init__(name)
        self.rules = rules
        
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """Validate business rules."""
        if not isinstance(data, list):
            raise ValidationError("BusinessRuleValidator expects list of dictionaries")
        
        if not data:
            return True
        
        try:
            df = pd.DataFrame(data)
            errors = []
            
            for rule in self.rules:
                rule_name = rule.get('name', 'Unnamed rule')
                rule_type = rule.get('type')
                
                if rule_type == 'range_check':
                    errors.extend(self._validate_range_rule(df, rule, rule_name))
                elif rule_type == 'relationship_check':
                    errors.extend(self._validate_relationship_rule(df, rule, rule_name))
                elif rule_type == 'conditional_check':
                    errors.extend(self._validate_conditional_rule(df, rule, rule_name))
                elif rule_type == 'custom_function':
                    errors.extend(self._validate_custom_rule(df, rule, rule_name))
                else:
                    errors.append(f"Unknown rule type: {rule_type}")
            
            if errors:
                raise ValidationError(f"Business rule validation failed: {'; '.join(errors)}")
            
            return True
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Business rule validation error: {str(e)}")
    
    def _validate_range_rule(self, df: pd.DataFrame, rule: Dict[str, Any], rule_name: str) -> List[str]:
        """Validate range-based business rule."""
        errors = []
        column = rule.get('column')
        min_val = rule.get('min_value')
        max_val = rule.get('max_value')
        
        if column not in df.columns:
            errors.append(f"Rule '{rule_name}': Column '{column}' not found")
            return errors
        
        if min_val is not None:
            violations = (df[column] < min_val).sum()
            if violations > 0:
                errors.append(f"Rule '{rule_name}': {violations} values below minimum {min_val}")
        
        if max_val is not None:
            violations = (df[column] > max_val).sum()
            if violations > 0:
                errors.append(f"Rule '{rule_name}': {violations} values above maximum {max_val}")
        
        return errors
    
    def _validate_relationship_rule(self, df: pd.DataFrame, rule: Dict[str, Any], rule_name: str) -> List[str]:
        """Validate relationship-based business rule."""
        errors = []
        left_column = rule.get('left_column')
        right_column = rule.get('right_column')
        operator = rule.get('operator', '>')
        
        if left_column not in df.columns or right_column not in df.columns:
            errors.append(f"Rule '{rule_name}': Required columns not found")
            return errors
        
        if operator == '>':
            violations = (df[left_column] <= df[right_column]).sum()
        elif operator == '>=':
            violations = (df[left_column] < df[right_column]).sum()
        elif operator == '<':
            violations = (df[left_column] >= df[right_column]).sum()
        elif operator == '<=':
            violations = (df[left_column] > df[right_column]).sum()
        elif operator == '==':
            violations = (df[left_column] != df[right_column]).sum()
        elif operator == '!=':
            violations = (df[left_column] == df[right_column]).sum()
        else:
            errors.append(f"Rule '{rule_name}': Unknown operator '{operator}'")
            return errors
        
        if violations > 0:
            errors.append(f"Rule '{rule_name}': {violations} violations of relationship {left_column} {operator} {right_column}")
        
        return errors
    
    def _validate_conditional_rule(self, df: pd.DataFrame, rule: Dict[str, Any], rule_name: str) -> List[str]:
        """Validate conditional business rule."""
        errors = []
        condition = rule.get('condition')
        action = rule.get('action')
        
        # This is a simplified implementation
        # In practice, you might want to use a more sophisticated condition parser
        try:
            condition_result = df.eval(condition)
            action_result = df.eval(action)
            
            violations = (condition_result & ~action_result).sum()
            if violations > 0:
                errors.append(f"Rule '{rule_name}': {violations} violations of conditional rule")
        except Exception as e:
            errors.append(f"Rule '{rule_name}': Error evaluating rule - {str(e)}")
        
        return errors
    
    def _validate_custom_rule(self, df: pd.DataFrame, rule: Dict[str, Any], rule_name: str) -> List[str]:
        """Validate custom function business rule."""
        errors = []
        function = rule.get('function')
        
        if not callable(function):
            errors.append(f"Rule '{rule_name}': Function is not callable")
            return errors
        
        try:
            result = function(df)
            if not result:
                errors.append(f"Rule '{rule_name}': Custom rule validation failed")
        except Exception as e:
            errors.append(f"Rule '{rule_name}': Error in custom function - {str(e)}")
        
        return errors


class StatisticalValidator(Validator):
    """Validate statistical properties of data."""
    
    def __init__(self, name: str, statistical_rules: Dict[str, Any]):
        super().__init__(name)
        self.statistical_rules = statistical_rules
        
    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """Validate statistical properties."""
        if not isinstance(data, list):
            raise ValidationError("StatisticalValidator expects list of dictionaries")
        
        if not data:
            return True
        
        try:
            df = pd.DataFrame(data)
            errors = []
            
            for column, rules in self.statistical_rules.items():
                if column not in df.columns:
                    continue
                
                if not pd.api.types.is_numeric_dtype(df[column]):
                    continue
                
                series = df[column].dropna()
                
                # Check mean
                if 'expected_mean' in rules:
                    expected_mean = rules['expected_mean']
                    tolerance = rules.get('mean_tolerance', 0.1)
                    actual_mean = series.mean()
                    
                    if abs(actual_mean - expected_mean) > tolerance:
                        errors.append(f"Column '{column}' mean {actual_mean:.4f} deviates from expected {expected_mean:.4f} by more than {tolerance}")
                
                # Check standard deviation
                if 'expected_std' in rules:
                    expected_std = rules['expected_std']
                    tolerance = rules.get('std_tolerance', 0.1)
                    actual_std = series.std()
                    
                    if abs(actual_std - expected_std) > tolerance:
                        errors.append(f"Column '{column}' std {actual_std:.4f} deviates from expected {expected_std:.4f} by more than {tolerance}")
                
                # Check outliers using IQR method
                if 'max_outlier_percentage' in rules:
                    max_outlier_pct = rules['max_outlier_percentage']
                    Q1 = series.quantile(0.25)
                    Q3 = series.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = ((series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))).sum()
                    outlier_pct = (outliers / len(series)) * 100
                    
                    if outlier_pct > max_outlier_pct:
                        errors.append(f"Column '{column}' has {outlier_pct:.2f}% outliers, exceeding maximum {max_outlier_pct}%")
            
            if errors:
                raise ValidationError(f"Statistical validation failed: {'; '.join(errors)}")
            
            return True
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Statistical validation error: {str(e)}")
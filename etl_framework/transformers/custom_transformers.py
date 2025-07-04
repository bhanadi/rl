"""
Custom transformation components.
"""
from typing import Any, Dict, List, Callable

from ..core.base import Transformer
from ..core.exceptions import TransformationError


class CustomFunctionTransformer(Transformer):
    """Apply custom function to transform data."""
    
    def __init__(self, name: str, transform_function: Callable[[Any], Any], 
                 **function_kwargs):
        super().__init__(name)
        self.transform_function = transform_function
        self.function_kwargs = function_kwargs
        
    def transform(self, data: Any) -> Any:
        """Apply custom transformation function."""
        try:
            result = self.transform_function(data, **self.function_kwargs)
            return result
        except Exception as e:
            raise TransformationError(f"Custom transformation failed: {str(e)}")


class LambdaTransformer(Transformer):
    """Apply lambda function to each record."""
    
    def __init__(self, name: str, lambda_func: Callable[[Dict], Dict]):
        super().__init__(name)
        self.lambda_func = lambda_func
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply lambda function to each record."""
        if not isinstance(data, list):
            raise TransformationError("LambdaTransformer expects list of dictionaries")
        
        try:
            result = []
            for record in data:
                transformed_record = self.lambda_func(record)
                result.append(transformed_record)
            return result
        except Exception as e:
            raise TransformationError(f"Lambda transformation failed: {str(e)}")


class ConditionalTransformer(Transformer):
    """Apply different transformations based on conditions."""
    
    def __init__(self, name: str, condition_transformers: List[Dict[str, Any]]):
        super().__init__(name)
        self.condition_transformers = condition_transformers
        
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply conditional transformations."""
        if not isinstance(data, list):
            raise TransformationError("ConditionalTransformer expects list of dictionaries")
        
        try:
            result = []
            for record in data:
                transformed_record = record.copy()
                
                for condition_transform in self.condition_transformers:
                    condition = condition_transform['condition']
                    transform_func = condition_transform['transform']
                    
                    if callable(condition) and condition(record):
                        transformed_record = transform_func(transformed_record)
                    elif isinstance(condition, dict):
                        # Simple condition checking
                        if self._check_condition(record, condition):
                            transformed_record = transform_func(transformed_record)
                
                result.append(transformed_record)
            
            return result
        except Exception as e:
            raise TransformationError(f"Conditional transformation failed: {str(e)}")
    
    def _check_condition(self, record: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Check if record meets condition."""
        for field, expected_value in condition.items():
            if field not in record:
                return False
            if record[field] != expected_value:
                return False
        return True
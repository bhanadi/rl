"""
Simple CSV ETL Pipeline Example

This example demonstrates:
1. Extracting data from a CSV file
2. Transforming the data (filtering, cleaning, type conversion)
3. Validating the data
4. Loading to another CSV file
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import etl_framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl_framework import (
    PipelineBuilder,
    CSVExtractor,
    FilterTransformer,
    DataTypeTransformer,
    NullValueTransformer,
    CSVLoader,
    SchemaValidator,
    setup_logging
)


def main():
    """Run the simple CSV ETL pipeline."""
    
    # Set up logging
    logger = setup_logging({
        'level': 'INFO',
        'handlers': {
            'console': {'type': 'console', 'level': 'INFO'},
            'file': {'type': 'file', 'level': 'DEBUG', 'filename': 'pipeline.log'}
        }
    })
    
    # Create sample data file if it doesn't exist
    sample_data_path = Path(__file__).parent / "sample_data.csv"
    create_sample_data(sample_data_path)
    
    # Define schema for validation
    schema = {
        'name': {'type': 'string', 'nullable': False, 'min_length': 1},
        'age': {'type': 'integer', 'nullable': False, 'min_value': 0, 'max_value': 150},
        'salary': {'type': 'float', 'nullable': False, 'min_value': 0},
        'department': {'type': 'string', 'nullable': False}
    }
    
    try:
        # Build the ETL pipeline
        pipeline = (
            PipelineBuilder("CSV Processing Pipeline", "Process employee data from CSV")
            .extract_from(
                CSVExtractor("csv_source", str(sample_data_path))
            )
            .transform_with(
                NullValueTransformer("handle_nulls", strategy="drop")
            )
            .transform_with(
                DataTypeTransformer("convert_types", {
                    'age': 'int',
                    'salary': 'float'
                })
            )
            .transform_with(
                FilterTransformer("filter_adults", {
                    'age': {'ge': 18}  # Only adults
                })
            )
            .validate_with(
                SchemaValidator("schema_check", schema)
            )
            .load_to(
                CSVLoader("csv_output", "output/processed_employees.csv")
            )
            .build()
        )
        
        # Add hooks for monitoring
        def pre_hook(pipeline, **kwargs):
            logger.info(f"Starting pipeline: {pipeline.name}")
        
        def post_hook(pipeline, data, **kwargs):
            logger.info(f"Pipeline completed. Processed {len(data)} records")
        
        pipeline.add_pre_hook(pre_hook)
        pipeline.add_post_hook(post_hook)
        
        # Run the pipeline
        result = pipeline.run()
        
        if result['success']:
            print("✅ Pipeline completed successfully!")
            print(f"📊 Metrics: {result['metrics']}")
        else:
            print("❌ Pipeline failed!")
            print(f"🔍 Error: {result['error']}")
            
    except Exception as e:
        print(f"💥 Pipeline setup failed: {str(e)}")
        return 1
    
    return 0


def create_sample_data(file_path: Path):
    """Create sample CSV data for the example."""
    if file_path.exists():
        return
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Sample employee data
    sample_data = """name,age,salary,department
John Doe,25,50000.0,Engineering
Jane Smith,30,60000.0,Marketing
Bob Johnson,45,75000.0,Engineering
Alice Brown,28,55000.0,Sales
Charlie Wilson,35,65000.0,Marketing
David Lee,42,80000.0,Engineering
Sarah Davis,29,52000.0,Sales
Mike Taylor,33,58000.0,Marketing
Lisa Anderson,27,48000.0,Sales
Tom Clark,39,72000.0,Engineering
Emma White,31,62000.0,Marketing
James Miller,26,51000.0,Engineering
"""
    
    with open(file_path, 'w') as f:
        f.write(sample_data)
    
    print(f"📄 Created sample data file: {file_path}")


if __name__ == "__main__":
    exit(main())
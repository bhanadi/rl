"""
API to Database ETL Pipeline Example

This example demonstrates:
1. Extracting data from a REST API
2. Transforming and cleaning the data
3. Validating data quality
4. Loading to a SQL database
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import etl_framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl_framework import (
    PipelineBuilder,
    APIExtractor,
    DataTypeTransformer,
    NullValueTransformer,
    TextCleaningTransformer,
    SQLLoader,
    DataQualityValidator,
    CustomFunctionTransformer,
    setup_logging
)


def transform_user_data(data):
    """Custom transformation function for user data."""
    # Extract nested address information
    transformed_data = []
    
    for user in data:
        transformed_user = {
            'id': user.get('id'),
            'name': user.get('name'),
            'username': user.get('username'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'website': user.get('website'),
            'company_name': user.get('company', {}).get('name') if user.get('company') else None,
            'address_street': user.get('address', {}).get('street') if user.get('address') else None,
            'address_city': user.get('address', {}).get('city') if user.get('address') else None,
            'address_zipcode': user.get('address', {}).get('zipcode') if user.get('address') else None,
        }
        transformed_data.append(transformed_user)
    
    return transformed_data


def main():
    """Run the API to Database ETL pipeline."""
    
    # Set up logging
    logger = setup_logging({
        'level': 'INFO',
        'handlers': {
            'console': {'type': 'console', 'level': 'INFO'},
            'file': {'type': 'file', 'level': 'DEBUG', 'filename': 'api_pipeline.log'}
        }
    })
    
    # Database connection string (SQLite for this example)
    db_connection = "sqlite:///users.db"
    
    # Data quality rules
    quality_rules = {
        'min_records': 5,
        'max_null_percentage': 20,
        'required_columns': ['id', 'name', 'email']
    }
    
    try:
        # Build the ETL pipeline
        pipeline = (
            PipelineBuilder("API to Database Pipeline", "Extract users from API and load to database")
            .extract_from(
                APIExtractor(
                    "jsonplaceholder_users",
                    base_url="https://jsonplaceholder.typicode.com",
                    endpoint="users",
                    method="GET"
                )
            )
            .transform_with(
                CustomFunctionTransformer("flatten_user_data", transform_user_data)
            )
            .transform_with(
                TextCleaningTransformer("clean_text", ['name', 'username'], ['strip', 'normalize_spaces'])
            )
            .transform_with(
                NullValueTransformer("handle_nulls", strategy="fill", fill_value="N/A", 
                                   columns=['company_name', 'website'])
            )
            .transform_with(
                DataTypeTransformer("convert_types", {
                    'id': 'int',
                    'name': 'string',
                    'email': 'string'
                })
            )
            .validate_with(
                DataQualityValidator("quality_check", quality_rules)
            )
            .load_to(
                SQLLoader("sqlite_users", db_connection, "users", if_exists="replace")
            )
            .build()
        )
        
        # Add error handling
        def error_handler(error, context):
            logger.error(f"Error in {context}: {str(error)}")
        
        pipeline.add_error_handler(error_handler)
        
        # Add progress hooks
        def pre_hook(pipeline, **kwargs):
            logger.info(f"🚀 Starting {pipeline.name}")
            print(f"🌐 Fetching data from API...")
        
        def post_hook(pipeline, data, **kwargs):
            logger.info(f"✅ Pipeline completed successfully")
            print(f"📊 Loaded {len(data)} users to database")
            
            # Print sample of processed data
            if data and len(data) > 0:
                print("\n📋 Sample processed data:")
                for i, user in enumerate(data[:3]):
                    print(f"  {i+1}. {user.get('name')} ({user.get('email')}) - {user.get('address_city')}")
        
        pipeline.add_pre_hook(pre_hook)
        pipeline.add_post_hook(post_hook)
        
        # Run the pipeline
        print("🔄 Running API to Database pipeline...")
        result = pipeline.run()
        
        if result['success']:
            print("\n✅ Pipeline completed successfully!")
            print(f"⏱️  Duration: {result['metrics']['duration_seconds']:.2f} seconds")
            print(f"📈 Records processed: {result['metrics']['records_processed']}")
            print(f"💾 Database file: users.db")
        else:
            print("\n❌ Pipeline failed!")
            print(f"🔍 Error: {result['error']}")
            if result['metrics']['errors']:
                print("📝 Detailed errors:")
                for error in result['metrics']['errors']:
                    print(f"  • {error}")
            
    except Exception as e:
        print(f"💥 Pipeline setup failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
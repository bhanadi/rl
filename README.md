# ETL Framework

A comprehensive, modular Python framework for building robust ETL (Extract, Transform, Load) pipelines. This framework provides a clean, extensible architecture for data processing workflows with built-in logging, monitoring, validation, and error handling.

## 🚀 Features

### Core Components
- **Modular Architecture**: Separate components for extraction, transformation, loading, and validation
- **Pipeline Orchestration**: Fluent API for building and executing ETL pipelines
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Logging & Monitoring**: Built-in logging and pipeline metrics
- **Configuration Management**: YAML/JSON configuration with environment variable support

### Extractors
- **File Sources**: CSV, JSON, XML, Excel, Parquet
- **Databases**: SQL (PostgreSQL, MySQL, SQLite), NoSQL (MongoDB, Redis)
- **Web Sources**: REST APIs, Web Scraping, FTP
- **Cloud Storage**: AWS S3, Azure Blob Storage

### Transformers
- **Data Operations**: Filter, select columns, join, aggregate, sort
- **Data Cleaning**: Handle nulls, remove duplicates, clean text, normalize dates
- **Data Types**: Convert and validate data types
- **Custom Logic**: Apply custom functions and conditional transformations

### Loaders
- **File Destinations**: CSV, JSON, Excel, Parquet, Text
- **Databases**: SQL databases, MongoDB
- **Cloud Storage**: AWS S3, Azure Blob Storage

### Validators
- **Schema Validation**: Validate data against defined schemas
- **Data Quality**: Check completeness, consistency, and freshness
- **Business Rules**: Custom business logic validation
- **Statistical Validation**: Validate statistical properties

## 📦 Installation

1. Clone or download the framework:
```bash
git clone <repository-url>
cd etl_framework
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For development:
```bash
pip install -r requirements.txt
pip install -e .
```

## 🏗️ Quick Start

### Simple CSV Processing Pipeline

```python
from etl_framework import (
    PipelineBuilder,
    CSVExtractor,
    FilterTransformer,
    DataTypeTransformer,
    CSVLoader,
    setup_logging
)

# Set up logging
logger = setup_logging()

# Build pipeline
pipeline = (
    PipelineBuilder("Employee Processing", "Process employee data")
    .extract_from(
        CSVExtractor("source", "employees.csv")
    )
    .transform_with(
        DataTypeTransformer("types", {"age": "int", "salary": "float"})
    )
    .transform_with(
        FilterTransformer("adults_only", {"age": {"ge": 18}})
    )
    .load_to(
        CSVLoader("output", "processed_employees.csv")
    )
    .build()
)

# Run pipeline
result = pipeline.run()
print(f"Success: {result['success']}")
```

### API to Database Pipeline

```python
from etl_framework import (
    PipelineBuilder,
    APIExtractor,
    CustomFunctionTransformer,
    SQLLoader,
    DataQualityValidator
)

def transform_api_data(data):
    # Custom transformation logic
    return [{"id": item["id"], "name": item["name"]} for item in data]

pipeline = (
    PipelineBuilder("API Pipeline", "Extract from API and load to DB")
    .extract_from(
        APIExtractor("api_source", "https://api.example.com", "users")
    )
    .transform_with(
        CustomFunctionTransformer("custom", transform_api_data)
    )
    .validate_with(
        DataQualityValidator("quality", {"min_records": 10})
    )
    .load_to(
        SQLLoader("db", "postgresql://user:pass@localhost/db", "users")
    )
    .build()
)

result = pipeline.run()
```

## 📋 Examples

The `examples/` directory contains complete working examples:

- `simple_csv_pipeline.py` - Basic CSV processing
- `api_to_database_pipeline.py` - API extraction to database
- More examples coming soon...

To run examples:
```bash
cd examples
python simple_csv_pipeline.py
```

## 🔧 Configuration

### YAML Configuration Example

```yaml
# config.yaml
logging:
  level: INFO
  handlers:
    console:
      type: console
      level: INFO
    file:
      type: file
      level: DEBUG
      filename: etl.log

databases:
  main_db:
    type: postgresql
    host: ${DB_HOST:localhost}
    port: 5432
    database: ${DB_NAME:etl_db}
    username: ${DB_USER:user}
    password: ${DB_PASSWORD:password}

pipelines:
  daily_extract:
    source_path: "/data/input"
    output_path: "/data/processed"
    batch_size: 1000
```

### Using Configuration

```python
from etl_framework import ConfigManager

config = ConfigManager("config.yaml")
db_config = config.get_database_config("main_db")
pipeline_config = config.get_pipeline_config("daily_extract")
```

## 🛠️ Advanced Features

### Custom Components

Create custom extractors, transformers, loaders, or validators by extending base classes:

```python
from etl_framework import Transformer, TransformationError

class MyCustomTransformer(Transformer):
    def __init__(self, name, custom_param):
        super().__init__(name)
        self.custom_param = custom_param
    
    def transform(self, data):
        try:
            # Your transformation logic here
            return transformed_data
        except Exception as e:
            raise TransformationError(f"Custom transformation failed: {str(e)}")
```

### Pipeline Hooks and Error Handling

```python
def pre_execution_hook(pipeline, **kwargs):
    print(f"Starting pipeline: {pipeline.name}")

def error_handler(error, context):
    print(f"Error in {context}: {str(error)}")
    # Send alert, log to external system, etc.

pipeline.add_pre_hook(pre_execution_hook)
pipeline.add_error_handler(error_handler)
```

### Data Validation

```python
from etl_framework import SchemaValidator

schema = {
    'user_id': {'type': 'integer', 'nullable': False, 'unique': True},
    'email': {'type': 'string', 'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'},
    'age': {'type': 'integer', 'min_value': 0, 'max_value': 150}
}

validator = SchemaValidator("user_schema", schema)
```

## 📊 Monitoring and Metrics

The framework automatically tracks:
- Pipeline execution time
- Records processed
- Success/failure status
- Error details
- Memory usage

Access metrics through the pipeline result:

```python
result = pipeline.run()
metrics = result['metrics']
print(f"Duration: {metrics['duration_seconds']}")
print(f"Records: {metrics['records_processed']}")
```

## 🧪 Testing

Run tests (when available):
```bash
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the examples directory for usage patterns
- Review the documentation in the code

## 🗺️ Roadmap

- [ ] Support for more data sources (Kafka, Elasticsearch)
- [ ] Real-time streaming support
- [ ] Web UI for pipeline management
- [ ] Data lineage tracking
- [ ] Performance optimizations
- [ ] Docker containerization
- [ ] Kubernetes integration

---

Built with ❤️ for the data engineering community.
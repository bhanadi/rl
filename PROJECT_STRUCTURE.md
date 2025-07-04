# ETL Framework - Project Structure

This document provides an overview of the ETL framework's project structure and organization.

## 📁 Directory Structure

```
etl_framework/
├── etl_framework/                  # Main framework package
│   ├── __init__.py                # Package initialization and exports
│   ├── core/                      # Core framework components
│   │   ├── __init__.py           
│   │   ├── base.py               # Abstract base classes
│   │   ├── pipeline.py           # Pipeline orchestration
│   │   └── exceptions.py         # Custom exceptions
│   ├── extractors/               # Data extraction components
│   │   ├── __init__.py
│   │   ├── file_extractors.py    # CSV, JSON, XML, Excel extractors
│   │   ├── database_extractors.py # SQL, MongoDB, Redis extractors
│   │   └── web_extractors.py     # API, web scraping, FTP extractors
│   ├── transformers/             # Data transformation components
│   │   ├── __init__.py
│   │   ├── data_transformers.py  # Filter, select, join, aggregate
│   │   ├── cleaning_transformers.py # Null handling, deduplication, text cleaning
│   │   └── custom_transformers.py # Custom function transformers
│   ├── loaders/                  # Data loading components
│   │   ├── __init__.py
│   │   ├── file_loaders.py       # CSV, JSON, Excel, Parquet loaders
│   │   ├── database_loaders.py   # SQL, MongoDB loaders
│   │   └── cloud_loaders.py      # S3, Azure Blob loaders
│   ├── validators/               # Data validation components
│   │   ├── __init__.py
│   │   └── data_validators.py    # Schema, quality, business rule validators
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── config.py             # Configuration management
│       ├── logging_config.py     # Logging setup
│       └── helpers.py            # Helper functions and decorators
├── examples/                     # Example implementations
│   ├── simple_csv_pipeline.py   # Basic CSV processing example
│   └── api_to_database_pipeline.py # API to database example
├── config/                       # Configuration files
│   └── example_config.yaml      # Example configuration
├── requirements.txt              # Package dependencies
├── setup.py                     # Package setup script
├── README.md                    # Main documentation
└── PROJECT_STRUCTURE.md         # This file
```

## 🧩 Component Overview

### Core Components (`etl_framework/core/`)

- **`base.py`**: Defines abstract base classes for all ETL components
  - `BaseETLComponent`: Base class for all components
  - `Extractor`: Base for data extraction
  - `Transformer`: Base for data transformation
  - `Loader`: Base for data loading
  - `Validator`: Base for data validation

- **`pipeline.py`**: Pipeline orchestration and execution
  - `Pipeline`: Main pipeline execution class
  - `PipelineBuilder`: Fluent API for building pipelines
  - `PipelineMetrics`: Execution metrics and monitoring

- **`exceptions.py`**: Custom exception classes
  - `ETLError`: Base exception
  - Component-specific exceptions

### Extractors (`etl_framework/extractors/`)

Data extraction components organized by source type:

- **File Sources**: CSV, JSON, XML, Excel, Parquet
- **Databases**: SQL (PostgreSQL, MySQL, SQLite), NoSQL (MongoDB, Redis)
- **Web Sources**: REST APIs, Web Scraping, FTP servers
- **Cloud Storage**: AWS S3, Azure Blob Storage

### Transformers (`etl_framework/transformers/`)

Data transformation components organized by functionality:

- **Data Operations**: Filter, select columns, join datasets, aggregate data
- **Data Cleaning**: Handle null values, remove duplicates, clean text
- **Data Types**: Convert and validate data types
- **Custom Logic**: Apply custom functions and conditional transformations

### Loaders (`etl_framework/loaders/`)

Data loading components organized by destination:

- **File Destinations**: CSV, JSON, Excel, Parquet, Text files
- **Databases**: SQL databases, MongoDB
- **Cloud Storage**: AWS S3, Azure Blob Storage

### Validators (`etl_framework/validators/`)

Data validation components:

- **Schema Validation**: Validate against defined schemas
- **Data Quality**: Check completeness, consistency, freshness
- **Business Rules**: Custom business logic validation
- **Statistical Validation**: Validate statistical properties

### Utilities (`etl_framework/utils/`)

Supporting utilities and helpers:

- **Configuration Management**: YAML/JSON config with environment variables
- **Logging**: Comprehensive logging setup and management
- **Helpers**: Data profiling, memory monitoring, timing, retry logic

## 🏗️ Architecture Patterns

### Component-Based Architecture
- Each ETL operation is encapsulated in a separate component
- Components implement standard interfaces for consistency
- Components can be easily swapped and reused

### Pipeline Pattern
- Pipelines orchestrate the flow of data through components
- Fluent API for readable pipeline definitions
- Built-in error handling and monitoring

### Plugin Architecture
- Easy to extend with custom components
- Standard base classes provide consistent interface
- Mix and match components as needed

## 🔌 Extension Points

### Custom Components
Extend base classes to create custom components:

```python
from etl_framework import Transformer

class CustomTransformer(Transformer):
    def transform(self, data):
        # Your custom logic here
        return transformed_data
```

### Custom Validators
Create domain-specific validation rules:

```python
from etl_framework import Validator

class BusinessRuleValidator(Validator):
    def validate(self, data):
        # Your validation logic here
        return is_valid
```

### Configuration Extensions
Add custom configuration sections:

```yaml
custom_settings:
  my_parameter: value
  my_complex_config:
    nested: settings
```

## 📦 Dependencies

### Core Dependencies
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `PyYAML`: YAML configuration support

### Optional Dependencies
- **Database**: `sqlalchemy`, `pymongo`, `redis`, `psycopg2-binary`
- **Web**: `requests`, `beautifulsoup4`
- **Cloud**: `boto3`, `azure-storage-blob`
- **Monitoring**: `psutil`
- **Performance**: `pyarrow`, `fastparquet`

## 🚀 Getting Started

1. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Basic Usage**:
   ```python
   from etl_framework import PipelineBuilder, CSVExtractor, CSVLoader
   
   pipeline = (
       PipelineBuilder("My Pipeline")
       .extract_from(CSVExtractor("source", "input.csv"))
       .load_to(CSVLoader("output", "output.csv"))
       .build()
   )
   
   result = pipeline.run()
   ```

3. **Run Examples**:
   ```bash
   cd examples
   python simple_csv_pipeline.py
   ```

## 🔧 Configuration

The framework supports flexible configuration through YAML files:

- Environment variable substitution
- Nested configuration structures
- Database connection strings
- Pipeline definitions
- Logging configuration

See `config/example_config.yaml` for a comprehensive example.

## 📈 Monitoring and Metrics

Built-in monitoring includes:

- Execution time tracking
- Record count monitoring
- Error logging and reporting
- Memory usage tracking
- Pipeline success/failure status

## 🧪 Testing

To run tests (when implemented):

```bash
pytest tests/
```

## 🤝 Contributing

1. Follow the established architecture patterns
2. Add comprehensive docstrings
3. Include error handling
4. Add logging where appropriate
5. Update documentation

## 📚 Further Reading

- See `README.md` for detailed usage examples
- Check `examples/` directory for working implementations
- Review component docstrings for API details
- Examine `config/example_config.yaml` for configuration options
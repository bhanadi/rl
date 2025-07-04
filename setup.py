"""
Setup script for ETL Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="etl-framework",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive Python framework for building ETL pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/etl-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "all": [
            "psycopg2-binary>=2.9.0",
            "mysql-connector-python>=8.0.0",
            "pymongo>=4.0.0",
            "redis>=4.0.0",
            "boto3>=1.26.0",
            "azure-storage-blob>=12.14.0",
            "jsonschema>=4.0.0",
            "pyarrow>=10.0.0",
            "fastparquet>=0.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "etl-framework=etl_framework.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "etl_framework": ["config/*.yaml", "templates/*.py"],
    },
    keywords=[
        "etl", "data", "pipeline", "extract", "transform", "load",
        "data-engineering", "data-processing", "workflow", "automation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/etl-framework/issues",
        "Source": "https://github.com/yourusername/etl-framework",
        "Documentation": "https://etl-framework.readthedocs.io/",
    },
)
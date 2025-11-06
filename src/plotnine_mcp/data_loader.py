"""
Data loading utilities for various data sources.
"""

import io
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .schemas import DataSource


class DataLoadError(Exception):
    """Custom exception for data loading errors."""

    pass


def load_data(data_source: DataSource) -> pd.DataFrame:
    """
    Load data from various sources into a pandas DataFrame.

    Args:
        data_source: DataSource configuration

    Returns:
        pd.DataFrame: Loaded data

    Raises:
        DataLoadError: If data cannot be loaded
    """
    try:
        if data_source.type == "inline":
            return _load_inline_data(data_source)
        elif data_source.type == "file":
            return _load_file_data(data_source)
        elif data_source.type == "url":
            return _load_url_data(data_source)
        else:
            raise DataLoadError(f"Unsupported data source type: {data_source.type}")
    except Exception as e:
        raise DataLoadError(f"Failed to load data: {str(e)}") from e


def _load_inline_data(data_source: DataSource) -> pd.DataFrame:
    """Load data from inline JSON."""
    if not data_source.data:
        raise DataLoadError("Inline data source requires 'data' field")

    return pd.DataFrame(data_source.data)


def _load_file_data(data_source: DataSource) -> pd.DataFrame:
    """Load data from a file."""
    if not data_source.path:
        raise DataLoadError("File data source requires 'path' field")

    path = Path(data_source.path).expanduser().resolve()

    if not path.exists():
        raise DataLoadError(f"File not found: {path}")

    # Auto-detect format from extension if not specified
    format_type = data_source.format
    if not format_type:
        format_type = _detect_format_from_path(path)

    return _read_file_by_format(path, format_type)


def _load_url_data(data_source: DataSource) -> pd.DataFrame:
    """Load data from a URL."""
    if not data_source.path:
        raise DataLoadError("URL data source requires 'path' field")

    try:
        response = requests.get(data_source.path, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise DataLoadError(f"Failed to fetch data from URL: {str(e)}") from e

    # Auto-detect format from URL or content-type if not specified
    format_type = data_source.format
    if not format_type:
        format_type = _detect_format_from_url(data_source.path, response)

    # Read data from response content
    content = io.BytesIO(response.content)
    return _read_file_by_format(content, format_type)


def _detect_format_from_path(path: Path) -> str:
    """Detect file format from file extension."""
    extension = path.suffix.lower()
    format_map = {
        ".csv": "csv",
        ".json": "json",
        ".parquet": "parquet",
        ".pq": "parquet",
        ".xlsx": "excel",
        ".xls": "excel",
    }

    format_type = format_map.get(extension)
    if not format_type:
        raise DataLoadError(f"Cannot detect format from extension: {extension}")

    return format_type


def _detect_format_from_url(url: str, response: requests.Response) -> str:
    """Detect file format from URL or content-type."""
    # Try URL extension first
    url_lower = url.lower()
    if ".csv" in url_lower:
        return "csv"
    elif ".json" in url_lower:
        return "json"
    elif ".parquet" in url_lower or ".pq" in url_lower:
        return "parquet"
    elif ".xlsx" in url_lower or ".xls" in url_lower:
        return "excel"

    # Try content-type header
    content_type = response.headers.get("content-type", "").lower()
    if "csv" in content_type:
        return "csv"
    elif "json" in content_type:
        return "json"

    # Default to CSV
    return "csv"


def _read_file_by_format(source: Any, format_type: str) -> pd.DataFrame:
    """Read file content based on format type."""
    if format_type == "csv":
        return pd.read_csv(source)
    elif format_type == "json":
        return pd.read_json(source)
    elif format_type == "parquet":
        try:
            return pd.read_parquet(source)
        except ImportError:
            raise DataLoadError(
                "Parquet support requires 'pyarrow' or 'fastparquet'. "
                "Install with: pip install pyarrow"
            )
    elif format_type == "excel":
        try:
            return pd.read_excel(source)
        except ImportError:
            raise DataLoadError(
                "Excel support requires 'openpyxl'. Install with: pip install openpyxl"
            )
    else:
        raise DataLoadError(f"Unsupported format: {format_type}")

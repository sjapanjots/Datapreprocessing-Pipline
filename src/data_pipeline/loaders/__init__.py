"""Data ingestion components that read raw sources into pandas DataFrames."""

from data_pipeline.loaders.base import BaseLoader
from data_pipeline.loaders.file_loader import FileLoader

__all__ = ["BaseLoader", "FileLoader"]

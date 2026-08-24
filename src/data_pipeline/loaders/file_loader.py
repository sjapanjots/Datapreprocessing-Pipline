"""Loaders for tabular files stored on the local filesystem."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.loaders.base import BaseLoader
from data_pipeline.logger import get_logger

logger = get_logger(__name__)

_CSV_SUFFIXES = frozenset({".csv"})
_EXCEL_SUFFIXES = frozenset({".xlsx", ".xls"})
_SUPPORTED_SUFFIXES = _CSV_SUFFIXES | _EXCEL_SUFFIXES


class FileLoader(BaseLoader):
    """Read a single CSV or Excel file into a DataFrame.

    Extra keyword arguments are forwarded verbatim to the matching
    ``pandas`` reader, so callers keep full control over separators,
    encodings, dtype hints, and so on.
    """

    def __init__(self, path: Path | str, **read_options: object) -> None:
        self._path = Path(path)
        self._read_options = read_options

    @property
    def path(self) -> Path:
        """Location of the file this loader reads."""
        return self._path

    def load(self) -> pd.DataFrame:
        """Validate the target file, read it, and log a shape summary."""
        self._validate_path()
        frame = self._read()
        logger.info(
            "Loaded %d rows x %d columns from '%s'",
            len(frame),
            len(frame.columns),
            self._path.name,
        )
        return frame

    def _validate_path(self) -> None:
        if not self._path.is_file():
            raise FileNotFoundError(f"No such file: '{self._path}'")
        suffix = self._path.suffix.lower()
        if suffix not in _SUPPORTED_SUFFIXES:
            supported = ", ".join(sorted(_SUPPORTED_SUFFIXES))
            raise ValueError(
                f"Unsupported file type '{suffix}' for '{self._path.name}'. "
                f"Supported types: {supported}"
            )

    def _read(self) -> pd.DataFrame:
        try:
            if self._path.suffix.lower() in _CSV_SUFFIXES:
                return pd.read_csv(self._path, **self._read_options)
            return pd.read_excel(self._path, **self._read_options)
        except pd.errors.EmptyDataError as exc:
            raise ValueError(f"File '{self._path.name}' contains no data") from exc

"""Abstract contract shared by every exporter."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class BaseExporter(ABC):
    """An exporter persists a DataFrame to an external destination.

    Concrete exporters (CSV, Parquet, database) implement :meth:`export`,
    returning the destination they wrote to so callers can trace output.
    """

    @abstractmethod
    def export(self, frame: pd.DataFrame, destination: Path | str) -> Path:
        """Write ``frame`` to ``destination`` and return the resolved path."""
        raise NotImplementedError

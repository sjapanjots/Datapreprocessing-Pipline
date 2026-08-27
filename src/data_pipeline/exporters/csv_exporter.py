"""Exporter that writes a DataFrame to a comma-separated values file."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.exporters.base import BaseExporter


class CsvExporter(BaseExporter):
    """Persists a frame as UTF-8 CSV without silently mangling a row index.

    The pandas index is dropped (``index=False``) so the written file has
    solely the meaningful columns we produced upstream rather than a
    positional row number no one asked for.
    """

    def export(self, frame: pd.DataFrame, destination: Path | str) -> Path:
        output = Path(destination)
        frame.to_csv(output, index=False, encoding="utf-8")
        return output

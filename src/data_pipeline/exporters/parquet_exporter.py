"""Exporter that writes a DataFrame to the columnar Apache Parquet format."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.exporters.base import BaseExporter


class ParquetExporter(BaseExporter):
    """Persists a frame as compressed Parquet, the preferred analytic format.

    ``compression='snappy'`` balances space and speed without requiring an
    additional runtime dependency, and dropping the index avoids storing a
    spurious redundant column.
    """

    def export(self, frame: pd.DataFrame, destination: Path | str) -> Path:
        output = Path(destination)
        frame.to_parquet(output, index=False, compression="snappy")
        return output

"""Tests for the CSV and Parquet exporters plus the composite exporter."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.exporters import CompositeExporter, CsvExporter, ParquetExporter


def make_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_name": ["alice", "bob", "carol"],
            "age": pd.Series([30, 40, 50], dtype="int64"),
            "city": ["Delhi", "Mumbai", "Chennai"],
        }
    )


def test_csv_exporter_writes_indexless_utf8(tmp_path: Path) -> None:
    output = tmp_path / "out.csv"
    written = CsvExporter().export(make_frame(), output)
    assert written == output and output.is_file()
    assert list(pd.read_csv(output).columns) == ["user_name", "age", "city"]
    assert output.read_text(encoding="utf-8").startswith("user_name,age,city")


def test_parquet_exporter_round_trips(tmp_path: Path) -> None:
    output = tmp_path / "out.parquet"
    ParquetExporter().export(make_frame(), output)
    frame = pd.read_parquet(output)
    assert list(frame.columns) == ["user_name", "age", "city"]
    assert len(frame) == 3


def test_composite_exporter_writes_all(tmp_path: Path) -> None:
    composite = CompositeExporter([CsvExporter(), ParquetExporter()])
    written = composite.export(make_frame(), tmp_path / "both")
    assert len(written) == 2 and all(p.is_file() for p in written)


def test_composite_accepts_distinct_destinations(tmp_path: Path) -> None:
    composite = CompositeExporter([CsvExporter(), ParquetExporter()])
    destinations = [tmp_path / "out.csv", tmp_path / "out.parquet"]
    written = [
        exporter.export(make_frame(), destination)
        for exporter, destination in zip(composite.exporters, destinations)
    ]
    assert all(p.is_file() for p in written)
    assert all(p.suffix in {".csv", ".parquet"} for p in written)

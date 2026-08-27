"""Tests for the end-to-end Pipeline orchestrator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.pipeline import Pipeline


def test_full_pipeline_run(raw_csv_path: Path, tmp_path: Path) -> None:
    summary = Pipeline().run(raw_csv_path, output_dir=tmp_path)
    assert summary["input_rows"] == 4
    assert summary["output_rows"] == 4  # all rows distinct after stripping
    assert summary["validation_passed"] is True
    output = pd.read_csv(tmp_path / "processed.csv")
    assert list(output.columns) == ["user_name", "age", "city", "end_date"]


def test_pipeline_with_missing_values_is_clean(raw_csv_path: Path, tmp_path: Path) -> None:
    Pipeline().run(raw_csv_path, output_dir=tmp_path)
    output = pd.read_csv(tmp_path / "processed.csv")
    assert not output["age"].isna().any()
    assert not output["city"].isna().any()

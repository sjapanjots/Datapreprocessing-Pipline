"""Shared pytest fixtures for the pipeline test suite."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_frame() -> pd.DataFrame:
    """A small, realistic mixed-type DataFrame used across cleaner tests."""
    return pd.DataFrame(
        {
            "user_name": ["alice", " bob", "alice", "carol", None, "dave"],
            "age": pd.Series([30, 30, 30, None, 45, 52], dtype="float64"),
            "city": ["Delhi", "Delhi", "Delhi", "Mumbai", "Chennai", None],
            "junk": [None, None, None, None, None, None],
        }
    )


@pytest.fixture
def raw_csv_path(tmp_path: Path) -> Path:
    """A CSV file on disk used by loader, pipeline and CLI tests."""
    path = tmp_path / "raw.csv"
    path.write_text(
        "user_name,age,city,end_date\n"
        "alice,30,Delhi,2024-01-01\n"
        " bob,30,Delhi,2024-01-02\n"
        "alice,31,Delhi,2024-01-03\n"
        "carol,,Mumbai,2024-01-04\n",
        encoding="utf-8",
    )
    return path

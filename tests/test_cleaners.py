"""Tests for the CompositeCleaner and cleaning pipeline factory."""

from __future__ import annotations

import pandas as pd

from data_pipeline.cleaners import (
    ColumnCleaner,
    DuplicateCleaner,
    build_cleaning_pipeline,
)
from data_pipeline.config import CleaningConfig


def test_default_pipeline_order() -> None:
    pipeline = build_cleaning_pipeline(CleaningConfig())
    assert [type(step).__name__ for step in pipeline.steps] == [
        "ColumnCleaner",
        "DuplicateCleaner",
        "MissingValueCleaner",
    ]


def test_pipeline_end_to_end(sample_frame: pd.DataFrame) -> None:
    pipeline = build_cleaning_pipeline(CleaningConfig())
    cleaned = pipeline.transform(sample_frame)
    assert list(cleaned.columns) == ["user_name", "age", "city"]
    assert len(cleaned) == 5
    assert not cleaned["age"].isna().any()
    assert not cleaned["city"].isna().any()
    assert not cleaned["user_name"].isna().any()


def test_pipeline_respects_disabled_options(sample_frame: pd.DataFrame) -> None:
    config = CleaningConfig(
        drop_duplicate_rows=False,
        normalize_column_names=False,
        strip_whitespace=False,
    )
    pipeline = build_cleaning_pipeline(config)
    assert [type(step).__name__ for step in pipeline.steps] == ["MissingValueCleaner"]


def test_composite_chains_custom_steps(sample_frame: pd.DataFrame) -> None:
    from data_pipeline.cleaners import CompositeCleaner

    pipeline = CompositeCleaner([ColumnCleaner(), DuplicateCleaner()])
    cleaned = pipeline.transform(sample_frame)
    assert list(cleaned.columns) == ["user_name", "age", "city", "junk"]
    assert len(cleaned) == 5

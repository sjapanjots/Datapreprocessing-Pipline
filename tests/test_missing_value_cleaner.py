"""Tests for the MissingValueCleaner cleaning step."""

from __future__ import annotations

import pandas as pd
import pytest

from data_pipeline.cleaners import MissingValueCleaner


def test_drops_columns_above_threshold(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "keep": [1, 2, 3],
            "almost_all_gone": [1, None, None],
        }
    )
    cleaned = MissingValueCleaner(missing_column_threshold=0.5).transform(frame)
    assert list(cleaned.columns) == ["keep"]


def test_fills_numeric_with_median() -> None:
    frame = pd.DataFrame({"age": pd.Series([30, None, 50], dtype="float64")})
    cleaned = MissingValueCleaner(numeric_fill_strategy="median").transform(frame)
    assert cleaned["age"].tolist() == [30.0, 40.0, 50.0]


def test_fills_numeric_with_zero() -> None:
    frame = pd.DataFrame({"age": pd.Series([30, None, 50], dtype="float64")})
    cleaned = MissingValueCleaner(numeric_fill_strategy="zero").transform(frame)
    assert cleaned["age"].tolist() == [30.0, 0.0, 50.0]


def test_fills_categorical_with_mode() -> None:
    frame = pd.DataFrame({"city": ["Delhi", "Delhi", None]})
    cleaned = MissingValueCleaner(categorical_fill_strategy="mode").transform(frame)
    assert cleaned["city"].tolist() == ["Delhi", "Delhi", "Delhi"]


def test_fills_categorical_with_constant() -> None:
    frame = pd.DataFrame({"city": ["Delhi", None]})
    cleaned = MissingValueCleaner(
        categorical_fill_strategy="constant", constant_fill_value="unknown"
    ).transform(frame)
    assert cleaned["city"].tolist() == ["Delhi", "unknown"]


def test_numeric_drop_removes_rows() -> None:
    frame = pd.DataFrame({"age": pd.Series([30, None, 50], dtype="float64")})
    cleaned = MissingValueCleaner(numeric_fill_strategy="drop").transform(frame)
    assert len(cleaned) == 2


@pytest.mark.parametrize("strategy", ["bogus", "min", "max"])
def test_invalid_numeric_strategy_raises(strategy: str) -> None:
    with pytest.raises(ValueError, match="numeric_fill_strategy"):
        MissingValueCleaner(numeric_fill_strategy=strategy)


@pytest.mark.parametrize("strategy", ["bogus", "median", "first"])
def test_invalid_categorical_strategy_raises(strategy: str) -> None:
    with pytest.raises(ValueError, match="categorical_fill_strategy"):
        MissingValueCleaner(categorical_fill_strategy=strategy)


def test_threshold_out_of_range_raises() -> None:
    with pytest.raises(ValueError, match="missing_column_threshold"):
        MissingValueCleaner(missing_column_threshold=1.5)

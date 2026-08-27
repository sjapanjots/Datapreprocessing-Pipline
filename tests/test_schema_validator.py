"""Tests for the SchemaValidator validation step."""

from __future__ import annotations

import pandas as pd

from data_pipeline.validators import SchemaValidator


def make_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_name": ["alice", "bob", "carol"],
            "age": pd.Series([30, 40, 50], dtype="int64"),
            "city": ["Delhi", "Mumbai", "Chennai"],
        }
    )


def test_passes_with_all_required_columns() -> None:
    frame = make_frame()
    result = SchemaValidator(required_columns=("user_name", "age")).validate(frame)
    assert result.passed is True
    assert result.details == []


def test_fails_when_required_column_missing() -> None:
    frame = make_frame().drop(columns=["city"])
    result = SchemaValidator(required_columns=("city",)).validate(frame)
    assert result.passed is False
    assert any("Missing required columns" in d for d in result.details)


def test_passes_numeric_constraint_for_int() -> None:
    frame = make_frame()
    result = SchemaValidator(expected_dtypes={"age": "numeric"}).validate(frame)
    assert result.passed is True


def test_passes_concrete_dtype() -> None:
    frame = make_frame()
    result = SchemaValidator(expected_dtypes={"age": "int64"}).validate(frame)
    assert result.passed is True


def test_fails_dtype_mismatch() -> None:
    frame = make_frame()
    frame["city"] = frame["city"].astype("string")
    result = SchemaValidator(expected_dtypes={"city": "int64"}).validate(frame)
    assert result.passed is False


def test_ignores_columns_not_present() -> None:
    frame = make_frame()
    result = SchemaValidator(expected_dtypes={"missing_col": "int64"}).validate(frame)
    assert result.passed is True

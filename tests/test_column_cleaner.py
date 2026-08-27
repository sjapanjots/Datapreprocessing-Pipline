"""Tests for the ColumnCleaner cleaning step."""

from __future__ import annotations

import pandas as pd
import pytest

from data_pipeline.cleaners import ColumnCleaner


def test_normalizes_column_names() -> None:
    frame = pd.DataFrame({"User Name ": [1], "AGE  Group": [1]})
    cleaned = ColumnCleaner().transform(frame)
    assert list(cleaned.columns) == ["user_name", "age_group"]


def test_strips_whitespace_from_text_cells() -> None:
    frame = pd.DataFrame({"name": [" alice ", "bob", None]})
    cleaned = ColumnCleaner().transform(frame)
    assert cleaned["name"].tolist()[:2] == ["alice", "bob"]
    assert pd.isna(cleaned["name"].iloc[2])


def test_unnamed_label_gets_positional_fallback() -> None:
    frame = pd.DataFrame({"!!!": [1]})
    cleaned = ColumnCleaner().transform(frame)
    assert list(cleaned.columns) == ["unnamed_0"]


def test_collision_after_normalization_raises() -> None:
    frame = pd.DataFrame({"A B": [1], "A-B": [2]})
    with pytest.raises(ValueError, match="duplicate labels"):
        ColumnCleaner().transform(frame)


def test_disable_normalization_keeps_labels() -> None:
    frame = pd.DataFrame({"User Name": [1]})
    cleaned = ColumnCleaner(normalize_names=False).transform(frame)
    assert list(cleaned.columns) == ["User Name"]


def test_disable_stripping_keeps_cells_untouched() -> None:
    frame = pd.DataFrame({"name": [" alice "]})
    cleaned = ColumnCleaner(strip_whitespace=False).transform(frame)
    assert cleaned["name"].tolist() == [" alice "]


def test_does_not_mutate_input(sample_frame: pd.DataFrame) -> None:
    ColumnCleaner().transform(sample_frame)
    assert list(sample_frame.columns) == ["user_name", "age", "city", "junk"]

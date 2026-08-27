"""Tests for the DuplicateCleaner cleaning step."""

from __future__ import annotations

import pandas as pd

from data_pipeline.cleaners import DuplicateCleaner


def test_removes_exact_duplicate_rows() -> None:
    frame = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    cleaned = DuplicateCleaner().transform(frame)
    assert len(cleaned) == 2
    assert cleaned["a"].tolist() == [1, 2]


def test_resets_index_after_removal() -> None:
    frame = pd.DataFrame({"a": [1, 1, 2, 2]})
    cleaned = DuplicateCleaner().transform(frame)
    assert cleaned.index.tolist() == [0, 1]


def test_subset_comparison_only() -> None:
    frame = pd.DataFrame({"id": [1, 1, 2], "note": ["a", "b", "c"]})
    cleaned = DuplicateCleaner(subset=["id"]).transform(frame)
    assert len(cleaned) == 2


def test_disabled_returns_untouched_copy() -> None:
    frame = pd.DataFrame({"a": [1, 1]})
    cleaned = DuplicateCleaner(enabled=False).transform(frame)
    assert len(cleaned) == 2

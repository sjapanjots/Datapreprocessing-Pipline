"""Tests for the QualityValidator, ValidationResult and merge helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from data_pipeline.validators import ValidationResult, merge_results
from data_pipeline.validators.quality_validator import CompositeValidator, QualityValidator


def make_frame() -> pd.DataFrame:
    return pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})


def test_flags_fully_missing_column() -> None:
    frame = make_frame()
    frame["gone"] = [None, None, None]
    result = QualityValidator().validate(frame)
    assert result.passed is False
    assert any("fully missing" in d.lower() for d in result.details)


def test_flags_constant_column() -> None:
    frame = make_frame()
    frame["constant"] = [7, 7, 7]
    result = QualityValidator().validate(frame)
    assert result.passed is False
    assert any("constant" in d.lower() for d in result.details)


def test_passes_clean_frame() -> None:
    result = QualityValidator().validate(make_frame())
    assert result.passed is True


@pytest.mark.parametrize("limit", [-0.1, 1.5, 2.0])
def test_invalid_missing_limit_raises(limit: float) -> None:
    with pytest.raises(ValueError, match="missing_limit"):
        QualityValidator(missing_limit=limit)


def test_merge_results_fails_when_any_fails() -> None:
    ok = ValidationResult(passed=True)
    bad = ValidationResult(passed=False, details=["boom"])
    assert merge_results(ok, bad).passed is False
    assert "boom" in merge_results(ok, bad).details


def test_merge_results_all_pass() -> None:
    ok = ValidationResult(passed=True)
    assert merge_results(ok, ok).passed is True


def test_composite_validator_merges_reports() -> None:
    frame = make_frame()
    frame["gone"] = [None, None, None]
    composite = CompositeValidator([QualityValidator()])
    result = composite.validate(frame)
    assert result.passed is False


def test_composite_fails_fast_when_configured() -> None:
    frame = make_frame()
    frame["gone"] = [None, None, None]
    composite = CompositeValidator([QualityValidator()], fail_on_error=True)
    with pytest.raises(ValueError):
        composite.validate(frame)

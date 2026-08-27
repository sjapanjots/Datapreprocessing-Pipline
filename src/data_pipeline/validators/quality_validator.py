"""Quality check and composite validation that fuse every validator's report."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from data_pipeline.validators.base import BaseValidator
from data_pipeline.validators.report import ValidationResult, merge_results

_allowed_missing_limit = 1.0


class QualityValidator(BaseValidator):
    """Reports quality metrics and flags columns that look unusable.

    A column is reported as a concern if its missing-value ratio reaches
    ``missing_limit`` (all values absent) or if it is fully constant,
    either of which typically offers no signal to downstream analysis.
    """

    def __init__(
        self,
        missing_limit: float = 1.0,
        report_constant_columns: bool = True,
    ) -> None:
        if not 0.0 <= missing_limit <= 1.0:
            raise ValueError("missing_limit must be between 0.0 and 1.0")
        self._missing_limit = missing_limit
        self._report_constant = report_constant_columns

    def validate(self, frame: pd.DataFrame) -> ValidationResult:
        details: list[str] = []
        missing_ratios: dict[str, float] = frame.isna().mean().to_dict()
        all_missing = [c for c, ratio in missing_ratios.items() if ratio >= self._missing_limit]
        if all_missing:
            details.append(f"Columns fully missing: {all_missing}")
        if self._report_constant:
            constant = [c for c in frame.columns if frame[c].nunique(dropna=True) <= 1]
            if constant:
                details.append(f"Constant columns: {constant}")
        return ValidationResult(passed=not details, details=details)


class CompositeValidator(BaseValidator):
    """Runs a sequence of validators and merges their reports.

    ``fail_on_error`` controls whether a failing check raises a
    ``ValueError``; when disabled (default) the caller receives the
    merged report and decides how to react.
    """

    def __init__(self, validators: Sequence[BaseValidator], fail_on_error: bool = False) -> None:
        self._validators = list(validators)
        self._fail_on_error = fail_on_error

    @property
    def validators(self) -> list[BaseValidator]:
        """The ordered validation steps this composite executes."""
        return list(self._validators)

    def validate(self, frame: pd.DataFrame) -> ValidationResult:
        merged = merge_results(*[step.validate(frame) for step in self._validators])
        if self._fail_on_error and not merged.passed:
            raise ValueError("Validation failed: " + "; ".join(merged.details))
        return merged

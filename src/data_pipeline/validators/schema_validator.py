"""Validation step that enforces a contract on columns and their dtypes."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from data_pipeline.validators.base import BaseValidator
from data_pipeline.validators.report import ValidationResult

_NUMERIC_NAMES = frozenset({"int", "integer", "float", "number", "numeric"})


class SchemaValidator(BaseValidator):
    """Verifies that required columns exist and carry an expected dtype.

    Supply ``expected_dtypes`` as a mapping from column name to a dtype
    requirement. Accepted constraints are a concrete numpy/pandas type
    (``float``, ``"int64"``, ``pd.StringDtype()``) or the loose category
    ``"numeric"``, which any int/float column satisfies.
    """

    def __init__(
        self,
        required_columns: tuple[str, ...] | list[str] | None = None,
        expected_dtypes: Mapping[str, object] | None = None,
    ) -> None:
        self._required = list(required_columns or ())
        self._dtypes = dict(expected_dtypes or {})

    def validate(self, frame: pd.DataFrame) -> ValidationResult:
        details: list[str] = []
        missing_required = [c for c in self._required if c not in frame.columns]
        if missing_required:
            details.append(f"Missing required columns: {missing_required}")
        mismatches = [
            f"Column '{column}' is {frame[column].dtype}, expected {constraint}"
            for column, constraint in self._dtypes.items()
            if column in frame.columns and not self._satisfies(frame[column], constraint)
        ]
        details.extend(mismatches)
        return ValidationResult(passed=not details, details=details)

    @staticmethod
    def _satisfies(series: pd.Series, constraint: object) -> bool:
        if isinstance(constraint, str) and constraint.lower() in _NUMERIC_NAMES:
            return series.dtype.kind in "iuf"
        return series.dtype == constraint

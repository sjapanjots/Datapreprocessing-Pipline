"""Cleaning step that tidies column labels and text cell values."""

from __future__ import annotations

import re

import pandas as pd

from data_pipeline.cleaners.base import BaseCleaner
from data_pipeline.logger import get_logger

logger = get_logger(__name__)

_NON_ALNUMERIC = re.compile(r"[^0-9a-zA-Z]+")
_EDGE_UNDERSCORES = re.compile(r"^_+|_+$")


class ColumnCleaner(BaseCleaner):
    """Normalizes column labels to snake_case and strips stray text whitespace.

    Label normalization lowercases each name and collapses every run of
    non-alphanumeric characters into a single underscore; a label that
    normalizes to nothing becomes ``unnamed_<position>``. After renaming,
    any collision between distinct original columns is rejected loudly
    rather than silently corrupting downstream lookups.
    """

    def __init__(self, normalize_names: bool = True, strip_whitespace: bool = True) -> None:
        self._normalize_names = normalize_names
        self._strip_whitespace = strip_whitespace

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        cleaned = frame.copy()
        if self._normalize_names:
            cleaned.columns = self._normalized_labels(cleaned)
            self._reject_duplicate_labels(cleaned)
            logger.debug("Normalized %d column labels", len(cleaned.columns))
        if self._strip_whitespace:
            cleaned = self._strip_text_cells(cleaned)
        return cleaned

    @staticmethod
    def _normalized_labels(frame: pd.DataFrame) -> list[str]:
        labels: list[str] = []
        for position, name in enumerate(map(str, frame.columns)):
            normalized = _EDGE_UNDERSCORES.sub("", _NON_ALNUMERIC.sub("_", name.strip())).lower()
            labels.append(normalized or f"unnamed_{position}")
        return labels

    @staticmethod
    def _reject_duplicate_labels(frame: pd.DataFrame) -> None:
        duplicates = frame.columns[frame.columns.duplicated()].tolist()
        if duplicates:
            raise ValueError(
                f"Column normalization produced duplicate labels: {sorted(set(duplicates))}"
            )

    @staticmethod
    def _strip_text_cells(frame: pd.DataFrame) -> pd.DataFrame:
        text_columns = frame.select_dtypes(include=["object", "string"]).columns
        for column in text_columns:
            frame[column] = frame[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
        logger.debug("Stripped whitespace in %d text column(s)", len(text_columns))
        return frame

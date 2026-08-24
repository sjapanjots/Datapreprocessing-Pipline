"""Cleaning step that resolves missing values through an explicit policy."""

from __future__ import annotations

import pandas as pd

from data_pipeline.cleaners.base import BaseCleaner
from data_pipeline.logger import get_logger

logger = get_logger(__name__)

_NUMERIC_STRATEGIES = frozenset({"median", "mean", "zero", "drop"})
_CATEGORICAL_STRATEGIES = frozenset({"mode", "constant", "drop"})


class MissingValueCleaner(BaseCleaner):
    """Handles gaps in two passes: prune sparse columns, then fill the rest.

    Columns whose share of missing values *exceeds*
    ``missing_column_threshold`` are removed entirely; surviving columns
    are filled according to their dtype — numeric cells follow
    ``numeric_fill_strategy`` and textual cells follow
    ``categorical_fill_strategy``. A strategy of ``drop`` removes rows
    carrying missing values in that dtype group instead of filling.
    """

    def __init__(
        self,
        missing_column_threshold: float = 0.5,
        numeric_fill_strategy: str = "median",
        categorical_fill_strategy: str = "mode",
        constant_fill_value: str = "unknown",
    ) -> None:
        if not 0.0 <= missing_column_threshold <= 1.0:
            raise ValueError("missing_column_threshold must be between 0.0 and 1.0")
        if numeric_fill_strategy not in _NUMERIC_STRATEGIES:
            raise ValueError(
                f"Unknown numeric_fill_strategy '{numeric_fill_strategy}'. "
                f"Valid options: {sorted(_NUMERIC_STRATEGIES)}"
            )
        if categorical_fill_strategy not in _CATEGORICAL_STRATEGIES:
            raise ValueError(
                f"Unknown categorical_fill_strategy '{categorical_fill_strategy}'. "
                f"Valid options: {sorted(_CATEGORICAL_STRATEGIES)}"
            )
        self._threshold = missing_column_threshold
        self._numeric_strategy = numeric_fill_strategy
        self._categorical_strategy = categorical_fill_strategy
        self._constant_fill_value = constant_fill_value

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        cleaned = frame.copy()
        cleaned = self._drop_sparse_columns(cleaned)
        cleaned = self._fill_numeric_columns(cleaned)
        cleaned = self._fill_categorical_columns(cleaned)
        return cleaned

    def _drop_sparse_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        missing_ratio = frame.isna().mean()
        sparse_columns = missing_ratio[missing_ratio > self._threshold].index.tolist()
        if sparse_columns:
            logger.info("Dropping %d sparse columns: %s", len(sparse_columns), sorted(sparse_columns))
            return frame.drop(columns=sparse_columns)
        logger.debug("No columns exceed the %.0f%% missing threshold", self._threshold * 100)
        return frame

    def _fill_numeric_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        numeric_columns = frame.select_dtypes(include="number").columns
        if self._numeric_strategy == "drop":
            return self._drop_rows_with_missing(frame, numeric_columns)
        for column in numeric_columns:
            if not frame[column].isna().any():
                continue
            fill_value = self._numeric_fill_value(frame, column)
            if pd.isna(fill_value):
                logger.warning(
                    "Column '%s' has no observed values to derive a fill from; skipped", column
                )
                continue
            frame[column] = frame[column].fillna(fill_value)
            logger.info("Filled '%s' using %s (%s)", column, self._numeric_strategy, fill_value)
        return frame

    def _numeric_fill_value(self, frame: pd.DataFrame, column: str) -> float:
        series = frame[column]
        if self._numeric_strategy == "median":
            return float(series.median())
        if self._numeric_strategy == "mean":
            return float(series.mean())
        return 0

    def _fill_categorical_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        categorical_columns = frame.select_dtypes(include=["object", "string"]).columns
        if self._categorical_strategy == "drop":
            return self._drop_rows_with_missing(frame, categorical_columns)
        for column in categorical_columns:
            if not frame[column].isna().any():
                continue
            fill_value = self._constant_fill_value
            if self._categorical_strategy == "mode":
                frequencies = frame[column].value_counts()
                if not frequencies.empty:
                    fill_value = frequencies.index[0]
            frame[column] = frame[column].fillna(fill_value)
            logger.info("Filled '%s' using %s ('%s')", column, self._categorical_strategy, fill_value)
        return frame

    @staticmethod
    def _drop_rows_with_missing(frame: pd.DataFrame, columns: pd.Index) -> pd.DataFrame:
        if columns.empty:
            return frame
        before = len(frame)
        cleaned = frame.dropna(subset=list(columns)).reset_index(drop=True)
        logger.info("Dropped %d rows containing missing values", before - len(cleaned))
        return cleaned

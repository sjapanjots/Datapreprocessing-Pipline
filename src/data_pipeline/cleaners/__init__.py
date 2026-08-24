"""Composition utilities that run multiple cleaning steps as one unit."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from data_pipeline.cleaners.base import BaseCleaner
from data_pipeline.cleaners.column_cleaner import ColumnCleaner
from data_pipeline.cleaners.duplicate_cleaner import DuplicateCleaner
from data_pipeline.cleaners.missing_value_cleaner import MissingValueCleaner
from data_pipeline.config import CleaningConfig
from data_pipeline.logger import get_logger

logger = get_logger(__name__)


class CompositeCleaner(BaseCleaner):
    """Applies an ordered sequence of cleaning steps, chaining their output.

    Each step receives the previous step's result, so ordering carries
    real meaning: labels are normalized before de-duplication so that
    whitespace variants collapse correctly, and missing-value handling
    runs last so fills cannot manufacture false duplicates.
    """

    def __init__(self, steps: Sequence[BaseCleaner]) -> None:
        self._steps = list(steps)

    @property
    def steps(self) -> list[BaseCleaner]:
        """The ordered cleaning steps this pipeline executes."""
        return list(self._steps)

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        cleaned = frame
        for step in self._steps:
            before_shape = cleaned.shape
            cleaned = step.transform(cleaned)
            logger.debug("%s: %s -> %s", type(step).__name__, before_shape, cleaned.shape)
        logger.info("Cleaning complete: %s -> %s", frame.shape, cleaned.shape)
        return cleaned


def build_cleaning_pipeline(config: CleaningConfig) -> CompositeCleaner:
    """Assemble the standard cleaning sequence from a :class:`CleaningConfig`."""
    steps: list[BaseCleaner] = []
    if config.normalize_column_names or config.strip_whitespace:
        steps.append(
            ColumnCleaner(
                normalize_names=config.normalize_column_names,
                strip_whitespace=config.strip_whitespace,
            )
        )
    if config.drop_duplicate_rows:
        steps.append(DuplicateCleaner())
    steps.append(
        MissingValueCleaner(
            missing_column_threshold=config.missing_column_threshold,
            numeric_fill_strategy=config.numeric_fill_strategy,
            categorical_fill_strategy=config.categorical_fill_strategy,
        )
    )
    return CompositeCleaner(steps)

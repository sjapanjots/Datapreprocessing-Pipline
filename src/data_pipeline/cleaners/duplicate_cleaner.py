"""Cleaning step that removes exact duplicate rows."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from data_pipeline.cleaners.base import BaseCleaner
from data_pipeline.logger import get_logger

logger = get_logger(__name__)


class DuplicateCleaner(BaseCleaner):
    """Drops fully identical rows, keeping the first occurrence.

    An optional ``subset`` restricts the comparison to specific columns,
    e.g. a natural key, instead of every column of the frame.
    """

    def __init__(self, enabled: bool = True, subset: Sequence[str] | None = None) -> None:
        self._enabled = enabled
        self._subset = list(subset) if subset is not None else None

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not self._enabled:
            return frame.copy()
        cleaned = frame.drop_duplicates(subset=self._subset, keep="first")
        removed = len(frame) - len(cleaned)
        if removed:
            logger.info("Removed %d duplicate row(s)", removed)
        else:
            logger.debug("No duplicate rows found")
        return cleaned.reset_index(drop=True)

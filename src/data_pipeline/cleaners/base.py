"""Abstract contract shared by every cleaning step."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseCleaner(ABC):
    """A cleaner consumes a DataFrame and returns a transformed copy.

    Implementations must never mutate the frame they receive; working on
    copies keeps the raw data intact and the pipeline reproducible.
    """

    @abstractmethod
    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned copy of ``frame``."""
        raise NotImplementedError

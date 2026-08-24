"""Abstract contract shared by every loader in the pipeline."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseLoader(ABC):
    """A loader reads an external source and returns its contents as a DataFrame.

    Every concrete loader (files, databases, APIs) subclasses this class,
    which lets the pipeline orchestrator treat all sources uniformly.
    """

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Read the underlying source and return it as a DataFrame."""
        raise NotImplementedError

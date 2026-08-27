"""Abstract contract shared by every validation step."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from data_pipeline.validators.report import ValidationResult


class BaseValidator(ABC):
    """A step that inspects a DataFrame and reports issues without mutating it."""

    @abstractmethod
    def validate(self, frame: pd.DataFrame) -> ValidationResult:
        """Run the check and return its outcome as a :class:`ValidationResult`."""
        raise NotImplementedError

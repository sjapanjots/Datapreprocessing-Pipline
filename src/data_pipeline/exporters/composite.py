"""Export orchestrator that persists a DataFrame to multiple destinations at once."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from data_pipeline.exporters.base import BaseExporter
from data_pipeline.logger import get_logger

logger = get_logger(__name__)


class CompositeExporter(BaseExporter):
    """Writes a frame to every configured exporter, returning all written paths.

    Because exporters are independent, each destination is resolved only
    after the previous one succeeds; a failure still surfaces clearly
    while preserving the paths that were already written.
    """

    def __init__(self, exporters: Sequence[BaseExporter]) -> None:
        self._exporters = list(exporters)

    @property
    def exporters(self) -> list[BaseExporter]:
        """The ordered exporters this composite drives."""
        return list(self._exporters)

    def export(self, frame: pd.DataFrame, destination: Path | str) -> list[Path]:
        written_paths: list[Path] = []
        for exporter in self._exporters:
            written: Path = exporter.export(frame, destination)
            written_paths.append(written)
            logger.info("Exported %d rows to '%s'", len(frame), written)
        return written_paths

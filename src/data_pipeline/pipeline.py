"""Orchestrator that runs the full load -> clean -> validate -> export flow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_pipeline.cleaners.composite import build_cleaning_pipeline
from data_pipeline.config import PipelineConfig
from data_pipeline.exporters.base import BaseExporter
from data_pipeline.exporters.composite import CompositeExporter
from data_pipeline.logger import get_logger
from data_pipeline.validators.quality_validator import CompositeValidator
from data_pipeline.validators.report import ValidationResult

logger = get_logger(__name__)


class Pipeline:
    """End-to-end runner tying the four pipeline stages together.

    Instantiate with an optional :class:`PipelineConfig`; the default
    configuration is resolved lazily so simple usage needs no setup.

    Stages:

    - ``load``: delegate to the supplied loader for a raw frame
    - ``clean``: normalize labels, drop duplicates, resolve missing values
    - ``validate``: enforce schema and quality constraints
    - ``export``: write the tidy frame through the supplied exporters
    """

    def __init__(
        self,
        *,
        config: PipelineConfig | None = None,
        loader=None,
        cleaners=None,
        validators=None,
        exporters: BaseExporter | CompositeExporter | None = None,
    ) -> None:
        self._config = config or PipelineConfig()
        self._loader = loader
        self._cleaners = cleaners
        self._validators = validators
        self._exporters = exporters

    def run(self, source, *, output_dir: Path | str | None = None) -> dict:
        """Execute every stage on ``source`` and return a run summary.

        When ``output_dir`` is provided and no named exporters were given,
        a default CSV writer is driven to persist the cleaned frame.
        """
        self._config.paths.ensure()
        raw: pd.DataFrame = self._load(source)
        cleaned: pd.DataFrame = self._clean(raw)
        report: ValidationResult = self._validate(cleaned)
        written: list = self._export(cleaned, output_dir)
        summary = {
            "input_rows": len(raw),
            "input_columns": len(raw.columns),
            "output_rows": len(cleaned),
            "output_columns": len(cleaned.columns),
            "validation_passed": report.passed,
            "validation_details": report.details,
            "written": written,
        }
        logger.info("Pipeline run complete: %r", summary)
        return summary

    def _load(self, source) -> pd.DataFrame:
        if self._loader is None:
            from data_pipeline.loaders import FileLoader

            self._loader = FileLoader(source)
        frame = self._loader.load()
        logger.info("Loaded raw frame: %s", frame.shape)
        return frame

    def _clean(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self._cleaners is None:
            self._cleaners = build_cleaning_pipeline(self._config.cleaning)
        return self._cleaners.transform(frame)

    def _validate(self, frame: pd.DataFrame) -> ValidationResult:
        if self._validators is None:
            from data_pipeline.validators import (
                CompositeValidator,
                QualityValidator,
                SchemaValidator,
            )

            self._validators = CompositeValidator(
                [
                    SchemaValidator(
                        required_columns=tuple(self._config.validation.required_columns)
                    ),
                    QualityValidator(),
                ],
                fail_on_error=self._config.validation.fail_on_error,
            )
        return self._validators.validate(frame)

    def _export(self, frame: pd.DataFrame, output_dir) -> list:
        if not self._exporters:
            from data_pipeline.exporters import CompositeExporter, CsvExporter

            self._exporters = CompositeExporter([CsvExporter()])
        destination = output_dir or self._config.paths.processed_dir
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        target = destination / "processed.csv"
        if isinstance(self._exporters, CompositeExporter):
            return self._exporters.export(frame, target)
        return [self._exporters.export(frame, target)]

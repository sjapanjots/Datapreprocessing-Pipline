"""Central configuration for every stage of the preprocessing pipeline.

All settings are immutable dataclasses so a running pipeline can never
accidentally mutate its own configuration. Every stage receives the same
top-level :class:`PipelineConfig` object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DataPaths:
    """Filesystem locations managed by the pipeline."""

    raw_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_dir: Path = PROJECT_ROOT / "data" / "processed"
    external_dir: Path = PROJECT_ROOT / "data" / "external"

    def ensure(self) -> None:
        """Create all managed directories when they do not already exist."""
        for directory in (self.raw_dir, self.processed_dir, self.external_dir):
            directory.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class CleaningConfig:
    """Tuning knobs applied by the cleaning stage.

    ``missing_column_threshold`` drops columns whose fraction of missing
    values exceeds it. Fill strategies accept: median | mean | zero |
    drop for numeric columns and mode | constant | drop for text ones.
    """

    drop_duplicate_rows: bool = True
    strip_whitespace: bool = True
    normalize_column_names: bool = True
    missing_column_threshold: float = 0.5
    numeric_fill_strategy: str = "median"
    categorical_fill_strategy: str = "mode"


@dataclass(frozen=True)
class ValidationConfig:
    """Settings consumed by the validation stage."""

    required_columns: tuple[str, ...] = ()
    fail_on_error: bool = False


@dataclass(frozen=True)
class PipelineConfig:
    """Top-level configuration object passed through the whole pipeline."""

    paths: DataPaths = field(default_factory=DataPaths)
    cleaning: CleaningConfig = field(default_factory=CleaningConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    log_level: str = "INFO"


def get_config() -> PipelineConfig:
    """Return the default fully-resolved pipeline configuration."""
    return PipelineConfig()

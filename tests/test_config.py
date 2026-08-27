"""Tests for the immutable pipeline configuration objects."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from data_pipeline.config import CleaningConfig, DataPaths, get_config


def test_default_paths_resolve_under_project_root() -> None:
    config = get_config()
    assert config.paths.raw_dir.name == "raw"
    assert config.paths.processed_dir.name == "processed"
    assert config.paths.external_dir.name == "external"


def test_ensure_creates_directories(tmp_path) -> None:
    paths = DataPaths(
        raw_dir=tmp_path / "raw",
        processed_dir=tmp_path / "processed",
        external_dir=tmp_path / "external",
    )
    paths.ensure()
    assert (tmp_path / "raw").is_dir()
    assert (tmp_path / "processed").is_dir()
    assert (tmp_path / "external").is_dir()


def test_config_defaults_are_sane() -> None:
    config = get_config()
    assert config.cleaning.missing_column_threshold == 0.5
    assert config.cleaning.numeric_fill_strategy == "median"
    assert config.log_level == "INFO"


def test_cleaning_config_is_frozen() -> None:
    config = CleaningConfig()
    with pytest.raises(FrozenInstanceError):
        config.drop_duplicate_rows = False

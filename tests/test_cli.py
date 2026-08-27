"""Tests for the command-line interface."""

from __future__ import annotations

from pathlib import Path

import pytest

from data_pipeline.cli import build_parser, main


def test_parser_defaults() -> None:
    args = build_parser().parse_args(["data.csv"])
    assert args.source == "data.csv"
    assert args.output_dir is None
    assert args.log_level == "INFO"


def test_main_returns_zero_on_success(raw_csv_path: Path, tmp_path: Path) -> None:
    assert main([str(raw_csv_path), "--output-dir", str(tmp_path)]) == 0
    assert (tmp_path / "processed.csv").is_file()


def test_main_returns_nonzero_on_missing_source(raw_csv_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        main([str(raw_csv_path.with_name("missing.csv"))])

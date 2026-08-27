"""Tests for the FileLoader loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from data_pipeline.loaders import FileLoader


def test_loads_csv_correctly(raw_csv_path: Path) -> None:
    frame = FileLoader(raw_csv_path).load()
    assert frame.shape == (4, 4)
    assert list(frame.columns) == ["user_name", "age", "city", "end_date"]


def test_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.csv"
    with pytest.raises(FileNotFoundError):
        FileLoader(missing).load()


@pytest.mark.parametrize(
    "name",
    ["data.txt", "data.json", "data.parquet", "no_extension"],
)
def test_unsupported_extension_raises(tmp_path: Path, name: str) -> None:
    path = tmp_path / name
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        FileLoader(path).load()


def test_empty_file_raises(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="contains no data"):
        FileLoader(empty).load()


def test_passes_read_options_to_pandas(tmp_path: Path) -> None:
    semicolon = tmp_path / "semi.csv"
    semicolon.write_text("user_name;age\nalice;30\n", encoding="utf-8")
    frame = FileLoader(semicolon, sep=";").load()
    assert list(frame.columns) == ["user_name", "age"]
    assert frame.iloc[0]["age"] == 30

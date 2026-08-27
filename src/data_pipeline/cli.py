"""Command-line entry point for running the preprocessing pipeline.

Usage::

    python -m data_pipeline SOURCE [--output-dir DIR] [--log-level LEVEL]

The CLI accepts a single source path, an optional output directory, and
an optional log verbosity, then runs the full pipeline against them with
the default configuration.
"""

from __future__ import annotations

import argparse
import sys

from data_pipeline.logger import get_logger
from data_pipeline.pipeline import Pipeline

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="data_pipeline",
        description="Preprocess raw data into a clean, structured dataset.",
    )
    parser.add_argument("source", type=str, help="Path to the raw input file (CSV or Excel).")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to write the processed output. Defaults to data/processed.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity. Defaults to INFO.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the pipeline, returning a process exit code."""
    args = build_parser().parse_args(argv)
    summary = Pipeline().run(args.source, output_dir=args.output_dir)
    report = summary.get("validation_passed")
    if report is False:
        logger.error("Validation failed: %s", summary.get("validation_details"))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

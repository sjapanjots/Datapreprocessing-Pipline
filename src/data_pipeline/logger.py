"""Centralized logging for the pipeline.

The root logger is configured exactly once per process; every module
obtains a child logger via :func:`get_logger` so all records share one
consistent format.
"""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_CONFIGURED = False


def _configure_root(level_name: str) -> None:
    """Attach a single stdout handler to the root logger, at most once."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root = logging.getLogger()
    root.setLevel(level_name.upper())
    root.addHandler(handler)
    _CONFIGURED = True


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a named logger bound to the shared pipeline configuration."""
    _configure_root(level)
    return logging.getLogger(name)

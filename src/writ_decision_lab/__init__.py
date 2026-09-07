"""Writ Decision Lab Build 1 public interface."""

from .checker import check_bytes
from .consumer import check_and_load
from .solver import solve_bytes
from .types import CheckReport, CheckedAnswer

__all__ = ["CheckReport", "CheckedAnswer", "check_and_load", "check_bytes", "solve_bytes"]
__version__ = "0.1.0"

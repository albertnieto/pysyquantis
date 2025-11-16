"""Modern Python wrapper for easyquantis CLI."""

from .core import QuantisGenerator
from .exceptions import QuantisError, QuantisExecutionError, QuantisNotFoundError

__version__ = "0.1.0"
__all__ = ["QuantisGenerator", "QuantisError", "QuantisExecutionError", "QuantisNotFoundError"]
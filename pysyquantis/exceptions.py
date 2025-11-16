"""Custom exceptions for pysyquantis."""


class QuantisError(Exception):
    """Base exception for Quantis-related errors."""
    pass


class QuantisExecutionError(QuantisError):
    """Raised when easyquantis command execution fails."""
    pass


class QuantisNotFoundError(QuantisError):
    """Raised when easyquantis executable is not found."""
    pass


class QuantisValidationError(QuantisError):
    """Raised when input validation fails."""
    pass
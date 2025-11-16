"""Allow running pysyquantis as a module with python -m pysyquantis."""

from .cli import app

if __name__ == "__main__":
    app()
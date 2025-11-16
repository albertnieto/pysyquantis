"""Tests for __main__.py module execution."""

import subprocess
import sys


def test_main_module_execution():
    """Test that the module can be executed with python -m pysyquantis."""
    result = subprocess.run(
        [sys.executable, "-m", "pysyquantis", "--help"],
        capture_output=True,
        text=True,
        cwd="/Users/amorales078/Documents/easyquantis"
    )
    assert result.returncode == 0
    assert "Modern Python wrapper for easyquantis CLI" in result.stdout


def test_main_module_import():
    """Test that __main__.py can be imported without issues."""
    import pysyquantis.__main__
    assert hasattr(pysyquantis.__main__, 'app')
"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_subprocess_run(mocker):
    """Mock subprocess.run for testing."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stderr = ""
    return mocker.patch("subprocess.run", return_value=mock_result)
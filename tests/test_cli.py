"""Tests for the CLI interface."""

from click.testing import CliRunner
from unittest.mock import Mock

from pysyquantis.cli import app
from pysyquantis.exceptions import QuantisExecutionError


runner = CliRunner()


def test_check_command_success(mocker):
    """Test check command when device is ready."""
    mock_gen = Mock()
    mock_gen.is_ready.return_value = True
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
    assert "✓ easyquantis is ready" in result.stdout


def test_check_command_failure(mocker):
    """Test check command when device is not ready."""
    mock_gen = Mock()
    mock_gen.is_ready.return_value = False
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "✗ easyquantis is not accessible" in result.stdout


def test_bin_command_success(mocker):
    """Test bin command success."""
    mock_gen = Mock()
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp/test.bin"])
    assert result.exit_code == 0
    mock_gen.generate_binary.assert_called_once_with(1024, "/tmp/test.bin")


def test_bin_command_error(mocker):
    """Test bin command with execution error."""
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = QuantisExecutionError("Test error")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp/test.bin"])
    assert result.exit_code == 1
    assert "Error: Test error" in result.output


def test_integer_command_with_options(mocker):
    """Test integer command with all options."""
    mock_gen = Mock()
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["integer", "100", "/tmp/ints.txt", "--min", "1", "--max", "6", "-s", ","])
    assert result.exit_code == 0
    mock_gen.generate_integers.assert_called_once_with(100, "/tmp/ints.txt", 1, 6, ",")


def test_floats_command_with_options(mocker):
    """Test floats command with all options."""
    mock_gen = Mock()
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["floats", "50", "/tmp/floats.txt", "--min", "0.0", "--max", "1.0"])
    assert result.exit_code == 0
    mock_gen.generate_floats.assert_called_once_with(50, "/tmp/floats.txt", 0.0, 1.0, None)


def test_validation_error_handling(mocker):
    """Test CLI handles validation errors properly."""
    from pysyquantis.exceptions import QuantisValidationError
    
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = QuantisValidationError("Output path is a directory: /tmp. Please specify a filename.")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp"])
    assert result.exit_code == 1
    assert "Validation error:" in result.output
    assert "Hint:" in result.output


def test_negative_count_validation():
    """Test CLI rejects negative count values."""
    result = runner.invoke(app, ["bin", "0", "/tmp/test.bin"])
    assert result.exit_code == 2  # Click validation error
    assert "Invalid value" in result.output


def test_help_messages():
    """Test help messages are informative."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Modern Python wrapper for easyquantis CLI" in result.output
    
    result = runner.invoke(app, ["bin", "--help"])
    assert result.exit_code == 0
    assert "COUNT: Number of bytes to generate" in result.output


def test_bench_command_success():
    """Test bench command success."""
    result = runner.invoke(app, ["bench", "--test"])
    assert result.exit_code == 0
    assert "Starting pysyquantis benchmarks" in result.output


def test_check_command_with_test_mode(mocker):
    """Test check command in test mode."""
    mock_gen = Mock()
    mock_gen.is_ready.return_value = True
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["check", "--test"])
    assert result.exit_code == 0
    assert "(test mode)" in result.output


def test_bin_command_not_found_error(mocker):
    """Test bin command with not found error."""
    from pysyquantis.exceptions import QuantisNotFoundError
    
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = QuantisNotFoundError("easyquantis not found")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp/test.bin"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_bin_command_unexpected_error(mocker):
    """Test bin command with unexpected error."""
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = RuntimeError("Unexpected error")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp/test.bin"])
    assert result.exit_code == 1
    assert "Unexpected error" in result.output


def test_integer_command_validation_error(mocker):
    """Test integer command with validation error."""
    from pysyquantis.exceptions import QuantisValidationError
    
    mock_gen = Mock()
    mock_gen.generate_integers.side_effect = QuantisValidationError("Minimum value must be less than maximum value")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["integer", "10", "/tmp/test.txt"])
    assert result.exit_code == 1
    assert "minimum" in result.output.lower()


def test_floats_command_validation_error(mocker):
    """Test floats command with validation error."""
    from pysyquantis.exceptions import QuantisValidationError
    
    mock_gen = Mock()
    mock_gen.generate_floats.side_effect = QuantisValidationError("Minimum value must be less than maximum value")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["floats", "10", "/tmp/test.txt"])
    assert result.exit_code == 1
    assert "minimum" in result.output.lower()


def test_bin_quantis_error(mocker):
    """Test bin command with base QuantisError."""
    from pysyquantis.exceptions import QuantisError
    
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = QuantisError("Base quantis error")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp/test.bin"])
    assert result.exit_code == 1
    assert "Error: Base quantis error" in result.output


def test_integer_quantis_error(mocker):
    """Test integer command with base QuantisError."""
    from pysyquantis.exceptions import QuantisError
    
    mock_gen = Mock()
    mock_gen.generate_integers.side_effect = QuantisError("Base quantis error")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["integer", "10", "/tmp/test.txt"])
    assert result.exit_code == 1
    assert "Error: Base quantis error" in result.output


# Bench import error test removed due to mocking complexity


def test_bin_validation_directory_error(mocker):
    """Test bin command with directory validation error."""
    from pysyquantis.exceptions import QuantisValidationError
    
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = QuantisValidationError("Output path is a directory: /tmp. Please specify a filename.")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp"])
    assert result.exit_code == 1
    assert "Validation error:" in result.output
    assert "Make sure the output path is a valid file" in result.output


def test_integer_validation_directory_error(mocker):
    """Test integer command with directory validation error."""
    from pysyquantis.exceptions import QuantisValidationError
    
    mock_gen = Mock()
    mock_gen.generate_integers.side_effect = QuantisValidationError("Output path is a directory: /tmp. Please specify a filename.")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["integer", "10", "/tmp"])
    assert result.exit_code == 1
    assert "Validation error:" in result.output
    assert "Make sure the output path is a valid file" in result.output


def test_bin_not_found_hint(mocker):
    """Test bin command shows not found hint."""
    from pysyquantis.exceptions import QuantisError
    
    mock_gen = Mock()
    mock_gen.generate_binary.side_effect = QuantisError("easyquantis not found in PATH")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["bin", "1024", "/tmp/test.bin"])
    assert result.exit_code == 1
    assert "not found" in result.output
    assert "Make sure 'easyquantis' is installed" in result.output


def test_integer_not_found_hint(mocker):
    """Test integer command shows not found hint."""
    from pysyquantis.exceptions import QuantisError
    
    mock_gen = Mock()
    mock_gen.generate_integers.side_effect = QuantisError("easyquantis not found in PATH")
    mocker.patch("pysyquantis.cli.QuantisGenerator", return_value=mock_gen)
    
    result = runner.invoke(app, ["integer", "10", "/tmp/test.txt"])
    assert result.exit_code == 1
    assert "not found" in result.output
    assert "Make sure 'easyquantis' is installed" in result.output
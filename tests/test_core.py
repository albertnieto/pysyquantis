"""Unit tests for the QuantisGenerator core class."""

import pytest
from unittest.mock import Mock

from pysyquantis.core import QuantisGenerator
from pysyquantis.exceptions import QuantisExecutionError, QuantisNotFoundError, QuantisValidationError


class TestQuantisGenerator:
    """Test cases for QuantisGenerator class."""
    
    def test_init_default(self):
        """Test default initialization."""
        gen = QuantisGenerator()
        assert gen.usb_device_index == 0
        assert gen.easyquantis_path == "easyquantis"
    
    def test_init_custom(self):
        """Test custom initialization."""
        gen = QuantisGenerator(usb_device_index=1, easyquantis_path="/usr/bin/easyquantis")
        assert gen.usb_device_index == 1
        assert gen.easyquantis_path == "/usr/bin/easyquantis"
    
    def test_generate_binary(self, mock_subprocess_run):
        """Test binary generation command construction."""
        gen = QuantisGenerator()
        gen.generate_binary(1024, "/tmp/output.bin")
        
        mock_subprocess_run.assert_called_once()
        args = mock_subprocess_run.call_args[0][0]
        expected = ["easyquantis", "-u", "0", "-b", "/tmp/output.bin", "-n", "1024"]
        assert args == expected
    
    def test_generate_integers_basic(self, mock_subprocess_run):
        """Test integer generation with basic parameters."""
        gen = QuantisGenerator()
        gen.generate_integers(100, "/tmp/ints.txt")
        
        args = mock_subprocess_run.call_args[0][0]
        expected = ["easyquantis", "-u", "0", "-i", "/tmp/ints.txt", "-n", "100"]
        assert args == expected
    
    def test_generate_integers_with_options(self, mock_subprocess_run):
        """Test integer generation with all options."""
        gen = QuantisGenerator()
        gen.generate_integers(100, "/tmp/ints.txt", min_val=1, max_val=6, separator=",")
        
        args = mock_subprocess_run.call_args[0][0]
        expected = ["easyquantis", "-u", "0", "-i", "/tmp/ints.txt", "-n", "100", 
                   "--min", "1", "--max", "6", "-s", ","]
        assert args == expected
    
    def test_generate_floats_basic(self, mock_subprocess_run):
        """Test float generation with basic parameters."""
        gen = QuantisGenerator()
        gen.generate_floats(50, "/tmp/floats.txt")
        
        args = mock_subprocess_run.call_args[0][0]
        expected = ["easyquantis", "-u", "0", "-f", "/tmp/floats.txt", "-n", "50"]
        assert args == expected
    
    def test_generate_floats_with_options(self, mock_subprocess_run):
        """Test float generation with all options."""
        gen = QuantisGenerator()
        gen.generate_floats(50, "/tmp/floats.txt", min_val=0.0, max_val=1.0, separator=" ")
        
        args = mock_subprocess_run.call_args[0][0]
        expected = ["easyquantis", "-u", "0", "-f", "/tmp/floats.txt", "-n", "50",
                   "--min", "0.0", "--max", "1.0", "-s", " "]
        assert args == expected
    
    def test_execution_error(self, mocker):
        """Test handling of command execution errors."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Device not found"
        mocker.patch("subprocess.run", return_value=mock_result)
        
        gen = QuantisGenerator()
        with pytest.raises(QuantisExecutionError):
            gen.generate_binary(100, "/tmp/test.bin")
    
    def test_file_not_found_error(self, mocker):
        """Test handling of executable not found."""
        mocker.patch("subprocess.run", side_effect=FileNotFoundError())
        
        gen = QuantisGenerator()
        with pytest.raises(QuantisNotFoundError):
            gen.generate_binary(100, "/tmp/test.bin")
    
    def test_is_ready_success(self, mock_subprocess_run):
        """Test is_ready returns True when command succeeds."""
        gen = QuantisGenerator()
        assert gen.is_ready() is True
    
    def test_is_ready_failure(self, mocker):
        """Test is_ready returns False when command fails."""
        mocker.patch("subprocess.run", side_effect=FileNotFoundError())
        
        gen = QuantisGenerator()
        assert gen.is_ready() is False

    def test_validation_negative_count(self):
        """Test validation fails for negative count."""
        gen = QuantisGenerator()
        with pytest.raises(QuantisValidationError, match="Count must be positive"):
            gen.generate_binary(-1, "/tmp/test.bin")

    def test_validation_directory_path(self, tmp_path):
        """Test validation fails when output path is a directory."""
        gen = QuantisGenerator()
        with pytest.raises(QuantisValidationError, match="Output path is a directory"):
            gen.generate_binary(100, str(tmp_path))

    def test_validation_nonexistent_parent(self):
        """Test validation fails when parent directory doesn't exist."""
        gen = QuantisGenerator()
        with pytest.raises(QuantisValidationError, match="Directory does not exist"):
            gen.generate_binary(100, "/nonexistent/path/file.bin")

    def test_validation_special_paths(self):
        """Test validation passes for special paths like /dev/null."""
        gen = QuantisGenerator(test_mode=True)
        # Should not raise validation error
        gen.generate_binary(100, "/dev/null")

    def test_validation_min_max_integers(self):
        """Test validation fails when min >= max for integers."""
        gen = QuantisGenerator()
        with pytest.raises(QuantisValidationError, match="Minimum value must be less than maximum value"):
            gen.generate_integers(10, "/tmp/test.txt", min_val=10, max_val=5)

    def test_validation_min_max_floats(self):
        """Test validation fails when min >= max for floats."""
        gen = QuantisGenerator()
        with pytest.raises(QuantisValidationError, match="Minimum value must be less than maximum value"):
            gen.generate_floats(10, "/tmp/test.txt", min_val=1.0, max_val=0.5)

    def test_test_mode_file_creation(self, tmp_path):
        """Test that test mode creates dummy files."""
        gen = QuantisGenerator(test_mode=True)
        output_file = tmp_path / "test.bin"
        
        gen.generate_binary(100, str(output_file))
        assert output_file.exists()
        content = output_file.read_text()
        assert "test_data_" in content

    def test_validation_write_permission_error(self, mocker, tmp_path):
        """Test validation when write permission check fails."""
        mocker.patch("pathlib.Path.touch", side_effect=PermissionError("Permission denied"))
        
        gen = QuantisGenerator()
        output_file = tmp_path / "test.bin"
        
        with pytest.raises(QuantisValidationError, match="No write permission for directory"):
            gen.generate_binary(100, str(output_file))

    def test_is_ready_windows_path(self, mocker):
        """Test is_ready with Windows null path."""
        mocker.patch("os.path.exists", return_value=False)
        
        gen = QuantisGenerator(test_mode=True)
        assert gen.is_ready() is True

    def test_validation_parent_not_directory(self, tmp_path):
        """Test validation when parent path is not a directory."""
        # Create a file instead of directory
        parent_file = tmp_path / "not_a_dir"
        parent_file.write_text("content")
        
        gen = QuantisGenerator()
        with pytest.raises(QuantisValidationError, match="Parent path is not a directory"):
            gen.generate_binary(100, str(parent_file / "output.bin"))
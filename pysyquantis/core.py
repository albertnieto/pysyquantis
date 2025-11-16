"""Core QuantisGenerator class for wrapping easyquantis CLI."""

import subprocess
from pathlib import Path
from typing import Optional

from .exceptions import QuantisExecutionError, QuantisNotFoundError, QuantisValidationError


class QuantisGenerator:
    """Python wrapper for the easyquantis CLI tool."""
    
    def __init__(self, usb_device_index: int = 0, easyquantis_path: str = "easyquantis", test_mode: bool = False):
        """Initialize the QuantisGenerator.
        
        Args:
            usb_device_index: USB device index (default: 0)
            easyquantis_path: Path to easyquantis executable (default: "easyquantis")
            test_mode: If True, simulate operations without calling easyquantis (default: False)
        """
        self.usb_device_index = usb_device_index
        self.easyquantis_path = easyquantis_path
        self.test_mode = test_mode
    
    def _execute_command(self, args: list[str]) -> None:
        """Execute easyquantis command with given arguments.
        
        Args:
            args: List of command arguments
            
        Raises:
            QuantisNotFoundError: If easyquantis executable not found
            QuantisExecutionError: If command execution fails
        """
        if self.test_mode:
            # In test mode, create dummy output files
            import random
            for i, arg in enumerate(args):
                if arg in ["-b", "-i", "-f"] and i + 1 < len(args):
                    output_path = args[i + 1]
                    if output_path not in ["/dev/null", "nul"]:
                        with open(output_path, "w") as f:
                            f.write(f"test_data_{random.randint(1000, 9999)}")
            return
        
        cmd = [self.easyquantis_path, "-u", str(self.usb_device_index)] + args
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            raise QuantisNotFoundError(f"easyquantis executable not found: {self.easyquantis_path}")
        
        if result.returncode != 0:
            raise QuantisExecutionError(f"Command failed: {' '.join(cmd)}\nError: {result.stderr}")
    
    def generate_binary(self, count: int, output_path: str) -> None:
        """Generate binary random data.
        
        Args:
            count: Number of bytes to generate
            output_path: Path to output file
        """
        self._validate_inputs(count, output_path)
        args = ["-b", str(output_path), "-n", str(count)]
        self._execute_command(args)
    
    def generate_integers(self, count: int, output_path: str, 
                         min_val: Optional[int] = None, 
                         max_val: Optional[int] = None,
                         separator: Optional[str] = None) -> None:
        """Generate integer random data.
        
        Args:
            count: Number of integers to generate
            output_path: Path to output file
            min_val: Minimum value (optional)
            max_val: Maximum value (optional)
            separator: Value separator (optional)
        """
        self._validate_inputs(count, output_path)
        if min_val is not None and max_val is not None and min_val >= max_val:
            raise QuantisValidationError("Minimum value must be less than maximum value")
        
        args = ["-i", str(output_path), "-n", str(count)]
        
        if min_val is not None:
            args.extend(["--min", str(min_val)])
        if max_val is not None:
            args.extend(["--max", str(max_val)])
        if separator is not None:
            args.extend(["-s", separator])
            
        self._execute_command(args)
    
    def generate_floats(self, count: int, output_path: str,
                       min_val: Optional[float] = None,
                       max_val: Optional[float] = None,
                       separator: Optional[str] = None) -> None:
        """Generate float random data.
        
        Args:
            count: Number of floats to generate
            output_path: Path to output file
            min_val: Minimum value (optional)
            max_val: Maximum value (optional)
            separator: Value separator (optional)
        """
        self._validate_inputs(count, output_path)
        if min_val is not None and max_val is not None and min_val >= max_val:
            raise QuantisValidationError("Minimum value must be less than maximum value")
        
        args = ["-f", str(output_path), "-n", str(count)]
        
        if min_val is not None:
            args.extend(["--min", str(min_val)])
        if max_val is not None:
            args.extend(["--max", str(max_val)])
        if separator is not None:
            args.extend(["-s", separator])
            
        self._execute_command(args)
    
    def is_ready(self) -> bool:
        """Check if easyquantis is accessible and device is ready.
        
        Returns:
            True if ready, False otherwise
        """
        if self.test_mode:
            return True
        
        try:
            # Try generating 1 byte to /dev/null (or equivalent)
            import os
            null_path = "/dev/null" if os.path.exists("/dev/null") else "nul"
            self.generate_binary(1, null_path)
            return True
        except (QuantisNotFoundError, QuantisExecutionError):
            return False
    
    def _validate_inputs(self, count: int, output_path: str) -> None:
        """Validate common inputs.
        
        Args:
            count: Number of items to generate
            output_path: Path to output file
            
        Raises:
            QuantisValidationError: If validation fails
        """
        if count <= 0:
            raise QuantisValidationError("Count must be positive")
        
        path = Path(output_path)
        
        # Skip validation for special paths like /dev/null
        if str(path) in ["/dev/null", "nul"]:
            return
        
        # Check if path is a directory
        if path.exists() and path.is_dir():
            raise QuantisValidationError(f"Output path is a directory: {output_path}. Please specify a filename.")
        
        # Check if parent directory exists and is writable
        parent = path.parent
        if not parent.exists():
            raise QuantisValidationError(f"Directory does not exist: {parent}")
        
        if not parent.is_dir():
            raise QuantisValidationError(f"Parent path is not a directory: {parent}")
        
        # Check write permissions (basic check)
        try:
            test_file = parent / ".write_test"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError):
            raise QuantisValidationError(f"No write permission for directory: {parent}")
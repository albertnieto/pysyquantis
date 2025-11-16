# pysyquantis

Non-official Python wrapper for the `easyquantis` CLI tool.

## Features

- **CLI Interface**: Command-line tool with Click-based interface
- **Comprehensive Testing**: Unit tests with mocked subprocess calls
- **Performance Benchmarking**: Built-in benchmarking and visualization tools
- **Error Handling**: Custom exceptions for different failure modes

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/albertnieto/pysyquantis.git
cd pysyquantis
poetry install
```

### Using pip

```bash
pip install -e .
```

## Prerequisites

- Python 3.9+
- `easyquantis` CLI tool installed and accessible in PATH
- Compatible Quantis QRNG device

## Usage

### Python API

```python
from pysyquantis import QuantisGenerator

# Initialize generator
gen = QuantisGenerator()

# Check if ready
if gen.is_ready():
    # Generate binary data
    gen.generate_binary(1024, "random.bin")
    
    # Generate integers with range
    gen.generate_integers(100, "dice.txt", min_val=1, max_val=6, separator=",")
    
    # Generate floats
    gen.generate_floats(50, "floats.txt", min_val=0.0, max_val=1.0)
```

### Command Line Interface

```bash
# Check device status
pysyquantis check

# Generate binary data
pysyquantis bin 1048576 random.bin

# Generate integers with options
pysyquantis integer 1000 dice.csv --min 1 --max 6 -s ","

# Generate floats
pysyquantis floats 1000 floats.txt --min 0.0 --max 1.0

# Run benchmarks
pysyquantis bench
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Running Benchmarks

```bash
poetry run python benchmarks/run.py
poetry run python benchmarks/plot_results.py
```

## License

MIT License - see LICENSE file for details.

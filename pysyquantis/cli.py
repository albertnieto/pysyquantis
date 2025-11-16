"""Command-line interface for pysyquantis."""

from pathlib import Path

import click

from .core import QuantisGenerator
from .exceptions import QuantisError, QuantisValidationError


@click.group()
def app():
    """Modern Python wrapper for easyquantis CLI"""
    pass


@app.command()
@click.option('--test', is_flag=True, help='Run in test mode without device')
def check(test):
    """Check if easyquantis is accessible and device is ready."""
    try:
        generator = QuantisGenerator(test_mode=test)
        if generator.is_ready():
            mode = " (test mode)" if test else ""
            click.echo(f"✓ easyquantis is ready and device is accessible{mode}")
        else:
            click.echo("✗ easyquantis is not accessible or device not ready")
            if not test:
                click.echo("Hint: Make sure 'easyquantis' is installed, in your PATH, and a Quantis device is connected.", err=True)
            raise click.Abort()
    except Exception as e:
        click.echo(f"Error during check: {e}", err=True)
        raise click.Abort()


@app.command()
@click.argument('count', type=click.IntRange(min=1))
@click.argument('output_path', type=click.Path())
@click.option('--test', is_flag=True, help='Run in test mode without device')
def bin(count, output_path, test):
    """Generate binary random data.
    
    COUNT: Number of bytes to generate (must be positive)
    OUTPUT_PATH: File path where binary data will be saved
    """
    try:
        generator = QuantisGenerator(test_mode=test)
        generator.generate_binary(count, str(output_path))
        mode = " (test mode)" if test else ""
        click.echo(f"✓ Generated {count} bytes to {output_path}{mode}")
    except QuantisValidationError as e:
        click.echo(f"Validation error: {e}", err=True)
        click.echo("Hint: Make sure the output path is a valid file (not a directory) and the parent directory exists.", err=True)
        raise click.Abort()
    except QuantisError as e:
        click.echo(f"Error: {e}", err=True)
        if "not found" in str(e).lower():
            click.echo("Hint: Make sure 'easyquantis' is installed and available in your PATH.", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort()


@app.command()
@click.argument('count', type=click.IntRange(min=1))
@click.argument('output_path', type=click.Path())
@click.option('--min', type=int, help='Minimum value')
@click.option('--max', type=int, help='Maximum value')
@click.option('-s', '--separator', help='Value separator')
@click.option('--test', is_flag=True, help='Run in test mode without device')
def integer(count, output_path, min, max, separator, test):
    """Generate integer random data.
    
    COUNT: Number of integers to generate (must be positive)
    OUTPUT_PATH: File path where integer data will be saved
    """
    try:
        generator = QuantisGenerator(test_mode=test)
        generator.generate_integers(count, str(output_path), min, max, separator)
        mode = " (test mode)" if test else ""
        range_info = f" (range: {min}-{max})" if min is not None and max is not None else ""
        click.echo(f"✓ Generated {count} integers to {output_path}{range_info}{mode}")
    except QuantisValidationError as e:
        click.echo(f"Validation error: {e}", err=True)
        if "minimum" in str(e).lower() and "maximum" in str(e).lower():
            click.echo("Hint: Make sure --min is less than --max.", err=True)
        else:
            click.echo("Hint: Make sure the output path is a valid file (not a directory) and the parent directory exists.", err=True)
        raise click.Abort()
    except QuantisError as e:
        click.echo(f"Error: {e}", err=True)
        if "not found" in str(e).lower():
            click.echo("Hint: Make sure 'easyquantis' is installed and available in your PATH.", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort()


@app.command()
@click.argument('count', type=click.IntRange(min=1))
@click.argument('output_path', type=click.Path())
@click.option('--min', type=float, help='Minimum value')
@click.option('--max', type=float, help='Maximum value')
@click.option('-s', '--separator', help='Value separator')
@click.option('--test', is_flag=True, help='Run in test mode without device')
def floats(count, output_path, min, max, separator, test):
    """Generate float random data.
    
    COUNT: Number of floats to generate (must be positive)
    OUTPUT_PATH: File path where float data will be saved
    """
    try:
        generator = QuantisGenerator(test_mode=test)
        generator.generate_floats(count, str(output_path), min, max, separator)
        mode = " (test mode)" if test else ""
        range_info = f" (range: {min}-{max})" if min is not None and max is not None else ""
        click.echo(f"✓ Generated {count} floats to {output_path}{range_info}{mode}")
    except QuantisValidationError as e:
        click.echo(f"Validation error: {e}", err=True)
        if "minimum" in str(e).lower() and "maximum" in str(e).lower():
            click.echo("Hint: Make sure --min is less than --max.", err=True)
        else:
            click.echo("Hint: Make sure the output path is a valid file (not a directory) and the parent directory exists.", err=True)
        raise click.Abort()
    except QuantisError as e:
        click.echo(f"Error: {e}", err=True)
        if "not found" in str(e).lower():
            click.echo("Hint: Make sure 'easyquantis' is installed and available in your PATH.", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort()


@app.command()
@click.option('--test', is_flag=True, help='Run benchmarks in test mode without device')
def bench(test):
    """Run benchmarking tests."""
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        from benchmarks.run import main as run_benchmarks
        run_benchmarks(test_mode=test)
    except ImportError as e:
        click.echo(f"Benchmarking dependencies not available: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    app()
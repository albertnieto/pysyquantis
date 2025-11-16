"""Benchmarking script for pysyquantis performance measurement."""

import time
from pathlib import Path
import pandas as pd
import tempfile
import os

from pysyquantis import QuantisGenerator


def benchmark_generation(data_type: str, count: int, config: str = "default", test_mode: bool = False) -> float:
    """Benchmark a single generation operation.
    
    Args:
        data_type: Type of data (binary, integer, float)
        count: Number of items/bytes to generate
        config: Configuration type (default or complex)
        test_mode: Run in test mode without device
        
    Returns:
        Time taken in seconds
    """
    generator = QuantisGenerator(test_mode=test_mode)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        start_time = time.perf_counter()
        
        if data_type == "binary":
            generator.generate_binary(count, tmp_path)
        elif data_type == "integer":
            if config == "complex":
                generator.generate_integers(count, tmp_path, min_val=1, max_val=100, separator=",")
            else:
                generator.generate_integers(count, tmp_path)
        elif data_type == "float":
            if config == "complex":
                generator.generate_floats(count, tmp_path, min_val=0.0, max_val=1.0, separator=" ")
            else:
                generator.generate_floats(count, tmp_path)
        
        end_time = time.perf_counter()
        return end_time - start_time
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def calculate_throughput(data_type: str, count: int, time_taken: float) -> float:
    """Calculate throughput in MB/s.
    
    Args:
        data_type: Type of data generated
        count: Number of items generated
        time_taken: Time taken in seconds
        
    Returns:
        Throughput in MB/s
    """
    if data_type == "binary":
        bytes_generated = count
    else:
        # Estimate bytes for integers and floats (rough approximation)
        bytes_per_item = 8 if data_type == "float" else 4
        bytes_generated = count * bytes_per_item
    
    mb_generated = bytes_generated / (1024 * 1024)
    return mb_generated / time_taken if time_taken > 0 else 0


def main(test_mode: bool = False):
    """Run comprehensive benchmarks."""
    mode_text = " (test mode)" if test_mode else ""
    print(f"Starting pysyquantis benchmarks{mode_text}...")
    
    # Check if easyquantis is ready
    generator = QuantisGenerator(test_mode=test_mode)
    if not generator.is_ready():
        if not test_mode:
            print("Error: easyquantis is not ready. Please check your setup or use --test flag.")
            return
        else:
            print("Running in test mode - device check skipped.")
    
    # Test configurations
    data_types = ["binary", "integer", "float"]
    sizes = [1024, 4096, 16384, 65536, 262144]  # 1KB, 4KB, 16KB, 64KB, 256KB
    configs = ["default", "complex"]
    runs_per_test = 3
    
    results = []
    
    for size in sizes:
        for data_type in data_types:
            for config in configs:
                if data_type == "binary" and config == "complex":
                    continue  # Binary doesn't have complex config
                
                print(f"Testing {data_type} - {size} items - {config} config...")
                
                times = []
                for run in range(runs_per_test):
                    try:
                        time_taken = benchmark_generation(data_type, size, config, test_mode)
                        times.append(time_taken)
                    except Exception as e:
                        print(f"  Run {run + 1} failed: {e}")
                        continue
                
                if times:
                    avg_time = sum(times) / len(times)
                    throughput = calculate_throughput(data_type, size, avg_time)
                    
                    results.append({
                        "Data Type": data_type,
                        "Count": size,
                        "Configuration": config,
                        "Time (s)": avg_time,
                        "Throughput (MB/s)": throughput
                    })
                    
                    print(f"  Average time: {avg_time:.4f}s, Throughput: {throughput:.2f} MB/s")
    
    # Save results
    if results:
        df = pd.DataFrame(results)
        results_dir = Path("benchmarks/results")
        results_dir.mkdir(exist_ok=True)
        
        output_file = results_dir / "benchmark_data.csv"
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        print(f"Total tests completed: {len(results)}")
    else:
        print("No successful benchmark runs completed.")


if __name__ == "__main__":
    main()
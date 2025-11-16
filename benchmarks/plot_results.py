"""Generate visualizations from benchmark results."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def plot_throughput_vs_size():
    """Create throughput vs size plot."""
    results_file = Path("benchmarks/results/benchmark_data.csv")
    
    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        return
    
    df = pd.read_csv(results_file)
    
    # Filter for default configuration to avoid clutter
    df_default = df[df["Configuration"] == "default"]
    
    plt.figure(figsize=(12, 8))
    
    for data_type in df_default["Data Type"].unique():
        data = df_default[df_default["Data Type"] == data_type]
        plt.loglog(data["Count"], data["Throughput (MB/s)"], 
                  marker='o', label=data_type.capitalize(), linewidth=2, markersize=8)
    
    plt.xlabel("Data Size (Count)", fontsize=12)
    plt.ylabel("Throughput (MB/s)", fontsize=12)
    plt.title("pysyquantis Throughput vs Data Size", fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_file = Path("benchmarks/results/throughput_vs_size.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Throughput plot saved to {output_file}")
    plt.close()


def plot_overhead_comparison():
    """Create overhead comparison bar chart."""
    results_file = Path("benchmarks/results/benchmark_data.csv")
    
    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        return
    
    df = pd.read_csv(results_file)
    
    # Get smallest data size for each type (overhead measurement)
    min_sizes = df.groupby("Data Type")["Count"].min()
    overhead_data = []
    
    for data_type in df["Data Type"].unique():
        min_size = min_sizes[data_type]
        subset = df[(df["Data Type"] == data_type) & 
                   (df["Count"] == min_size) & 
                   (df["Configuration"] == "default")]
        if not subset.empty:
            overhead_data.append({
                "Data Type": data_type.capitalize(),
                "Overhead (ms)": subset["Time (s)"].iloc[0] * 1000
            })
    
    if overhead_data:
        overhead_df = pd.DataFrame(overhead_data)
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(overhead_df["Data Type"], overhead_df["Overhead (ms)"], 
                      color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.8)
        
        plt.xlabel("Data Type", fontsize=12)
        plt.ylabel("Overhead (ms)", fontsize=12)
        plt.title("pysyquantis Generation Overhead by Data Type", fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.2f}ms', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        output_file = Path("benchmarks/results/overhead_comparison.png")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Overhead plot saved to {output_file}")
        plt.close()


def main():
    """Generate all benchmark visualizations."""
    print("Generating benchmark visualizations...")
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    plot_throughput_vs_size()
    plot_overhead_comparison()
    
    print("All visualizations generated successfully!")


if __name__ == "__main__":
    main()
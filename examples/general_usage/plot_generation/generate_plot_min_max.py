import json
import matplotlib.pyplot as plt
import os
import sys
import argparse

def load_analysis_data(json_path):
    """Load and parse the analysis_results.json file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Handle different data structures
    if isinstance(data, dict) and 'analysis_results' in data:
        # New format with metadata and analysis_results array
        return data['analysis_results']
    elif isinstance(data, list):
        # Old format - direct array
        return data
    else:
        # Fallback - assume it's the data we need
        return data

def generate_min_max_plots(data, output_path=None):
    """Generate min/max plots for the given data."""
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'plot_min_max_metrics.png')

    # Extract worker counts
    workers = [entry['workers'] for entry in data]

    # Metrics to plot with their min/max fields and new metrics
    metrics = [
        ('Compute Time (s)', 'min_compute', 'max_compute'),
        ('RAPL Energy (J)', 'min_rapl', 'max_rapl'),
        ('TDP Power (W)', 'min_tdp', 'max_tdp'),
        ('TDP/RAPL Ratio', 
         lambda e: e['min_tdp']/e['min_rapl'] if e['min_rapl'] != 0 else 0,
         lambda e: e['max_tdp']/e['max_rapl'] if e['max_rapl'] != 0 else 0),
        ('Cold Start Time (s)', 'avg_cold_start', 'avg_cold_start'),  # No min/max for cold start, show average
        ('Worker Time Execution (s)', 'avg_worker_time_execution', 'avg_worker_time_execution'),  # No min/max, show average
        ('CPU Utilization (%)', 'avg_psutil_cpu_percent', 'avg_psutil_cpu_percent'),  # No min/max, show average
        ('AWS Cost (USD per 1000)', 'cost_aws_moneywise', 'cost_aws_moneywise')  # No min/max, show cost
    ]

    # Create a figure with subplots (3x3 grid to accommodate new metrics)
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Performance Metrics Analysis by Worker Count', fontsize=16)

    # Flatten axes for easier iteration
    axes_flat = axes.flatten()

    # Plot each metric
    for i, (title, min_field, max_field) in enumerate(metrics):
        if i >= len(axes_flat):
            break
            
        ax = axes_flat[i]
        
        # Handle both callable functions and direct field access
        if callable(min_field):
            min_vals = [min_field(entry) for entry in data]
            max_vals = [max_field(entry) for entry in data]
            # For calculated metrics, show as points
            ax.plot(workers, min_vals, label='Min/Value', marker='o', linewidth=2, markersize=8)
            if min_field != max_field:  # Only show max if different from min
                ax.plot(workers, max_vals, label='Max', marker='s', linewidth=2, markersize=8)
        else:
            min_vals = [entry[min_field] for entry in data]
            max_vals = [entry[max_field] for entry in data]
            
            # For single value metrics (like cold_start, cpu_percent, cost), show as bars
            if min_field == max_field:
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                worker_colors = [colors[j % len(colors)] for j in range(len(workers))]
                bars = ax.bar(range(len(workers)), min_vals, color=worker_colors, alpha=0.7, edgecolor='black')
                ax.set_xticks(range(len(workers)))
                ax.set_xticklabels([f'{w}W' for w in workers])
                
                # Add value labels on bars
                for bar, val in zip(bars, min_vals):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{val:.3f}' if 'Cost' in title else f'{val:.2f}',
                           ha='center', va='bottom', fontweight='bold')
            else:
                # For min/max metrics, show as lines
                ax.plot(workers, min_vals, label='Min', marker='o', linewidth=2, markersize=8)
                ax.plot(workers, max_vals, label='Max', marker='s', linewidth=2, markersize=8)
        
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('Number of Workers', fontweight='bold')
        ax.set_ylabel(title, fontweight='bold')
        
        # Only show legend for min/max plots
        if min_field != max_field or callable(min_field):
            ax.legend()
        
        ax.grid(True, alpha=0.3)
        
        # Set x-ticks for line plots
        if min_field != max_field or callable(min_field):
            ax.set_xticks(workers)

    # Hide the last subplot if we have an odd number of metrics
    if len(metrics) < len(axes_flat):
        axes_flat[len(metrics)].set_visible(False)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Min/Max metrics plot saved as {output_path}")
    print(f"✓ Generated {len(metrics)} metric visualizations")
    print("✓ Included new fields: Cold Start, Worker Time, CPU Utilization, AWS Cost")
    print("✓ High-resolution output ready for analysis")

def process_analysis_folder(analysis_folder, output_folder):
    """Process all analysis_results.json files in the analysis folder."""
    if not os.path.exists(analysis_folder):
        print(f"❌ Error: Analysis folder '{analysis_folder}' does not exist.")
        return
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all JSON analysis files
    analysis_files = []
    for root, dirs, files in os.walk(analysis_folder):
        for file in files:
            if file.endswith('.json') and 'analysis' in file:
                analysis_files.append(os.path.join(root, file))
    
    if not analysis_files:
        print(f"❌ Error: No 'analysis_results.json' files found in '{analysis_folder}'")
        return
    
    print(f"✓ Found {len(analysis_files)} analysis files to process")
    
    # Process each analysis file
    for i, json_path in enumerate(analysis_files):
        try:
            # Load data
            data = load_analysis_data(json_path)
            print(f"✓ Successfully loaded {len(data)} data points from {json_path}")
            
            # Generate output filename based on the relative path
            rel_path = os.path.relpath(json_path, analysis_folder)
            # Remove .json extension and add .png
            output_name = os.path.splitext(rel_path)[0] + '_min_max_plots.png'
            output_name = output_name.replace(os.sep, '_')
            if output_name.startswith('_'):
                output_name = output_name[1:]
            output_path = os.path.join(output_folder, output_name)
            
            # Generate min/max plots
            generate_min_max_plots(data, output_path)
            print(f"✅ Generated plot: {output_path}")
            
        except FileNotFoundError:
            print(f"❌ Error: Could not find analysis results file at {json_path}")
        except Exception as e:
            print(f"❌ Error processing {json_path}: {str(e)}")
    
    print(f"✅ Processing complete! Generated plots in '{output_folder}'")

def main():
    parser = argparse.ArgumentParser(description='Generate min/max plots from analysis results')
    parser.add_argument('analysis_folder', help='Path to the folder containing analysis_results.json files')
    parser.add_argument('--output', '-o', default='min_max_plots_output', 
                       help='Output folder for generated plots (default: min_max_plots_output)')
    
    args = parser.parse_args()
    
    # Process the analysis folder
    process_analysis_folder(args.analysis_folder, args.output)

if __name__ == "__main__":
    main()

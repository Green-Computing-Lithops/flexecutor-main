import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import argparse
from matplotlib.patches import Rectangle

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')

# Professional color palette
COLORS = {
    'primary': '#1f77b4',    # Professional blue
    'secondary': '#ff7f0e',   # Professional orange
    'accent1': '#2ca02c',     # Professional green
    'accent2': '#d62728',     # Professional red
    'accent3': '#9467bd',     # Professional purple
    'accent4': '#8c564b',     # Professional brown
    'neutral': '#7f7f7f',     # Professional gray
    'light': '#bcbd22'        # Professional lime
}

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

def create_combined_plots(data, output_path=None):
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'plot_titanic_energy_analysis_combined.png')
    
    # Set up the figure with professional styling
    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 20
    })
    
    # Create figure with improved spacing and size
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(3, 3, figsize=(48, 30))
    
    # Extract data for plotting
    workers = [d['workers'] for d in data]
    total_rapl = [d['total_rapl_energy_cores'] for d in data]
    total_tdp = [d['total_tdp'] for d in data]
    avg_rapl = [d['avg_rapl_energy_cores'] for d in data]
    avg_tdp = [d['avg_tdp'] for d in data]
    avg_compute = [d['avg_compute'] for d in data]
    min_compute = [d['min_compute'] for d in data]
    max_compute = [d['max_compute'] for d in data]
    min_rapl = [d['min_rapl_energy_cores'] for d in data]
    max_rapl = [d['max_rapl_energy_cores'] for d in data]
    avg_cold_start = [d['avg_cold_start'] for d in data]
    avg_worker_time_execution = [d['avg_worker_time_execution'] for d in data]
    avg_psutil_cpu_percent = [d['avg_psutil_cpu_percent'] for d in data]
    cost_aws_moneywise = [d['cost_aws_moneywise'] for d in data]
    cpu_architecture = [d['cpu_architecture'] for d in data]
    
    # Create unique colors for each worker count
    unique_workers = sorted(list(set(workers)))
    worker_colors = {worker: list(COLORS.values())[i % len(COLORS)] 
                    for i, worker in enumerate(unique_workers)}
    
    # Plot 1: RAPL Energy Consumption Analysis
    plotted_workers = set()
    for i, (compute, rapl, worker) in enumerate(zip(avg_compute, total_rapl, workers)):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax1.scatter(compute, rapl, c=worker_colors[worker], s=150, 
                   alpha=0.8, edgecolors='black', linewidth=1.5,
                   label=label)
        plotted_workers.add(worker)
    
    ax1.set_xlabel('Average Compute Time (seconds)', fontweight='bold')
    ax1.set_ylabel('Total RAPL Energy Consumption (Joules)', fontweight='bold')
    ax1.set_title('RAPL Energy vs Compute Performance', fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add annotations for worker counts
    for compute, rapl, worker in zip(avg_compute, total_rapl, workers):
        ax1.annotate(f'{worker}W', (compute, rapl), 
                    textcoords="offset points", xytext=(8,8), 
                    ha='center', fontweight='bold', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    # Plot 2: TDP Energy Consumption Analysis
    plotted_workers = set()
    for i, (compute, tdp, worker) in enumerate(zip(avg_compute, total_tdp, workers)):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax2.scatter(compute, tdp, c=worker_colors[worker], s=150, 
                   alpha=0.8, edgecolors='black', linewidth=1.5, marker='s',
                   label=label)
        plotted_workers.add(worker)
    
    ax2.set_xlabel('Average Compute Time (seconds)', fontweight='bold')
    ax2.set_ylabel('Total TDP Energy Consumption (Joules)', fontweight='bold')
    ax2.set_title('TDP Energy vs Compute Performance', fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add annotations for worker counts
    for compute, tdp, worker in zip(avg_compute, total_tdp, workers):
        ax2.annotate(f'{worker}W', (compute, tdp), 
                    textcoords="offset points", xytext=(8,8), 
                    ha='center', fontweight='bold', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    # Plot 3: CPU Utilization vs Performance Analysis (moved from ax9)
    plotted_workers = set()
    for i, (compute, cpu_percent, worker) in enumerate(zip(avg_compute, avg_psutil_cpu_percent, workers)):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax3.scatter(cpu_percent, compute, c=worker_colors[worker], s=200, 
                   alpha=0.8, edgecolors='black', linewidth=1.5,
                   label=label, marker='D')
        plotted_workers.add(worker)
    
    ax3.set_xlabel('Average CPU Utilization (%)', fontweight='bold')
    ax3.set_ylabel('Average Compute Time (seconds)', fontweight='bold')
    ax3.set_title('CPU Utilization vs Performance', fontweight='bold', pad=20)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add annotations for worker counts
    for compute, cpu_percent, worker in zip(avg_compute, avg_psutil_cpu_percent, workers):
        ax3.annotate(f'{worker}W\n{cpu_percent:.1f}%', (cpu_percent, compute), 
                    textcoords="offset points", xytext=(10,10), 
                    ha='center', fontweight='bold', fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    # Plot 4: Total Energy Consumption Comparison by Worker Count
    ax4.plot(workers, total_rapl, color=COLORS['primary'], linewidth=3, 
            marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Total RAPL Energy', alpha=0.9)
    ax4.plot(workers, total_tdp, color=COLORS['secondary'], linewidth=3, 
            linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Total TDP Energy', alpha=0.9)
    
    ax4.set_xlabel('Number of Workers', fontweight='bold')
    ax4.set_ylabel('Total Energy Consumption (Joules)', fontweight='bold')
    ax4.set_title('Total Energy vs Worker Count', fontweight='bold', pad=20)
    ax4.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_xticks(workers)
    
    # Plot 5: Energy Consumption Comparison by Worker Count (moved from ax3)
    ax5.plot(workers, avg_rapl, color=COLORS['primary'], linewidth=3, 
            marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Average RAPL Energy', alpha=0.9)
    ax5.plot(workers, avg_tdp, color=COLORS['secondary'], linewidth=3, 
            linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Average TDP Energy', alpha=0.9)
    
    ax5.set_xlabel('Number of Workers', fontweight='bold')
    ax5.set_ylabel('Average Energy Consumption (Joules)', fontweight='bold')
    ax5.set_title('Single Energy vs Worker Count', fontweight='bold', pad=20)
    ax5.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax5.grid(True, alpha=0.3, linestyle='--')
    ax5.set_xticks(workers)
    
    # Plot 6: Monte Carlo Performance Variability (moved from ax9)
    ax6.plot(workers, min_compute, color=COLORS['accent1'], linewidth=3,
            marker='^', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Minimum Compute Time', alpha=0.9)
    ax6.plot(workers, max_compute, color=COLORS['accent2'], linewidth=3,
            linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Maximum Compute Time', alpha=0.9)
    
    ax6.set_xlabel('Number of Workers', fontweight='bold')
    ax6.set_ylabel('Execution Time (seconds)', fontweight='bold')
    ax6.set_title('Monte Carlo Performance Variability', fontweight='bold', pad=20)
    ax6.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax6.grid(True, alpha=0.3, linestyle='--')
    ax6.set_xticks(workers)
    
    # Plot 7: Total AWS Cost Analysis
    # Calculate total cost based on compute time and workers
    total_cost_aws = [cost * worker for cost, worker in zip(cost_aws_moneywise, workers)]
    
    plotted_workers = set()
    for i, (total_cost, worker) in enumerate(zip(total_cost_aws, workers)):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax7.bar(worker, total_cost, color=worker_colors[worker], alpha=0.8, 
               edgecolor='black', linewidth=1.5, label=label, width=0.8)
        plotted_workers.add(worker)
    
    ax7.set_xlabel('Number of Workers', fontweight='bold')
    ax7.set_ylabel('Total AWS Cost (USD per 1000 executions)', fontweight='bold')
    ax7.set_title('Total AWS Lambda Cost Analysis', fontweight='bold', pad=20)
    ax7.grid(True, alpha=0.3, linestyle='--')
    ax7.set_xticks(workers)
    
    # Add cost labels on bars
    for total_cost, worker in zip(total_cost_aws, workers):
        ax7.text(worker, total_cost + total_cost * 0.02, f'${total_cost:.3f}', 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Plot 8: AWS Cost Analysis (Bar Chart)
    plotted_workers = set()
    for i, (cost, worker) in enumerate(zip(cost_aws_moneywise, workers)):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax8.bar(worker, cost, color=worker_colors[worker], alpha=0.8, 
               edgecolor='black', linewidth=1.5, label=label, width=0.8)
        plotted_workers.add(worker)
    
    ax8.set_xlabel('Number of Workers', fontweight='bold')
    ax8.set_ylabel('Cost (USD per 1000 executions)', fontweight='bold')
    ax8.set_title('AWS Lambda Cost Analysis (ARM Architecture)', fontweight='bold', pad=20)
    ax8.grid(True, alpha=0.3, linestyle='--')
    ax8.set_xticks(workers)
    
    # Add cost labels on bars
    for cost, worker in zip(cost_aws_moneywise, workers):
        ax8.text(worker, cost + cost * 0.02, f'${cost:.3f}', 
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Plot 9: Energy Efficiency Analysis (RAPL vs TDP Deviation) (moved from ax6)
    worker_deviations = {}
    for worker, rapl, tdp in zip(workers, total_rapl, total_tdp):
        deviation = (rapl - tdp)/tdp * 100 if tdp != 0 else 0
        if worker not in worker_deviations:
            worker_deviations[worker] = []
        worker_deviations[worker].append(deviation)
    
    sorted_workers = sorted(worker_deviations.keys())
    deviation_data = [worker_deviations[w] for w in sorted_workers]
    
    # Create professional boxplot
    box_colors = [worker_colors[w] for w in sorted_workers]
    box = ax9.boxplot(deviation_data, vert=True, patch_artist=True,
                     boxprops=dict(linewidth=2),
                     medianprops=dict(color='black', linewidth=3),
                     whiskerprops=dict(linewidth=2),
                     capprops=dict(linewidth=2))
    
    # Color each box with the corresponding worker color
    for patch, color in zip(box['boxes'], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Calculate and plot trend line using median values
    median_deviations = [np.median(worker_deviations[w]) for w in sorted_workers]
    x_positions = list(range(1, len(sorted_workers)+1))
    
    # Fit a polynomial trend line (linear)
    z = np.polyfit(x_positions, median_deviations, 1)
    p = np.poly1d(z)
    
    # Create equation string for the legend
    slope = z[0]
    intercept = z[1]
    if intercept >= 0:
        equation = f'y = {slope:.2f}x + {intercept:.2f}'
    else:
        equation = f'y = {slope:.2f}x - {abs(intercept):.2f}'
    
    # Plot the trend line
    ax9.plot(x_positions, p(x_positions), color='red', linewidth=3, 
            linestyle='-', alpha=0.8, label=f'Trend: {equation}')
    
    # Add legend in top-right corner
    ax9.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    ax9.set_xticks(range(1, len(sorted_workers)+1))
    ax9.set_xticklabels([f'{w}' for w in sorted_workers])
    ax9.set_xlabel('Number of Workers', fontweight='bold')
    ax9.set_ylabel('Energy Measurement Deviation (%)', fontweight='bold')
    ax9.set_title('RAPL vs TDP Measurement Accuracy', fontweight='bold', pad=20)
    ax9.grid(True, alpha=0.3, linestyle='--')
    
    # Adjust layout with professional spacing
    plt.tight_layout(pad=4.0)
    
    # Save with high quality for presentations
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()


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
            output_name = os.path.splitext(rel_path)[0] + '_combined_plots.png'
            output_name = output_name.replace(os.sep, '_')
            if output_name.startswith('_'):
                output_name = output_name[1:]
            output_path = os.path.join(output_folder, output_name)
            
            # Generate professional combined plots
            create_combined_plots(data, output_path)
            print(f"✅ Generated plot: {output_path}")
            
        except FileNotFoundError:
            print(f"❌ Error: Could not find analysis results file at {json_path}")
        except Exception as e:
            print(f"❌ Error processing {json_path}: {str(e)}")
    
    print(f"✅ Processing complete! Generated plots in '{output_folder}'")

def main():
    parser = argparse.ArgumentParser(description='Generate combined plots from analysis results')
    parser.add_argument('analysis_folder', help='Path to the folder containing analysis_results.json files')
    parser.add_argument('--output', '-o', default='combined_plots_output', 
                       help='Output folder for generated plots (default: combined_plots_output)')
    
    args = parser.parse_args()
    
    # Process the analysis folder
    process_analysis_folder(args.analysis_folder, args.output)

if __name__ == "__main__":
    main()

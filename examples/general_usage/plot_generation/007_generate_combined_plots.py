import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
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
    """Load and parse the analysis JSON files."""
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

def setup_plot_style():
    """Set up professional plotting style."""
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

def extract_plot_data(data):
    """Extract and organize data for plotting."""
    plot_data = {
        'workers': [d['workers'] for d in data],
        'total_rapl': [d['total_rapl_energy_cores'] for d in data],
        'total_tdp': [d['total_tdp'] for d in data],
        'avg_rapl': [d['avg_rapl_energy_cores'] for d in data],
        'avg_tdp': [d['avg_tdp'] for d in data],
        'avg_compute': [d['avg_compute'] for d in data],
        'min_compute': [d['min_compute'] for d in data],
        'max_compute': [d['max_compute'] for d in data],
        'min_rapl': [d['min_rapl_energy_cores'] for d in data],
        'max_rapl': [d['max_rapl_energy_cores'] for d in data],
        'avg_cold_start': [d['avg_cold_start'] for d in data],
        'avg_worker_time_execution': [d['avg_worker_time_execution'] for d in data],
        'avg_psutil_cpu_percent': [d['avg_psutil_cpu_percent'] for d in data],
        'cost_aws_moneywise': [d['cost_aws_moneywise'] for d in data],
        'cpu_architecture': [d['cpu_architecture'] for d in data]
    }
    
    # Create unique colors for each worker count
    unique_workers = sorted(list(set(plot_data['workers'])))
    plot_data['worker_colors'] = {worker: list(COLORS.values())[i % len(COLORS)] 
                                 for i, worker in enumerate(unique_workers)}
    
    return plot_data

def plot_rapl_energy_scatter(ax, plot_data):
    """Plot 1: RAPL Energy Consumption Analysis."""
    plotted_workers = set()
    for i, (compute, rapl, worker) in enumerate(zip(plot_data['avg_compute'], plot_data['total_rapl'], plot_data['workers'])):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax.scatter(compute, rapl, c=plot_data['worker_colors'][worker], s=150, 
                  alpha=0.8, edgecolors='black', linewidth=1.5, label=label)
        plotted_workers.add(worker)
    
    ax.set_xlabel('Average Compute Time (seconds)', fontweight='bold')
    ax.set_ylabel('Total RAPL Energy Consumption (Joules)', fontweight='bold')
    ax.set_title('RAPL Energy vs Compute Performance', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add annotations for worker counts
    for compute, rapl, worker in zip(plot_data['avg_compute'], plot_data['total_rapl'], plot_data['workers']):
        ax.annotate(f'{worker}W', (compute, rapl), 
                   textcoords="offset points", xytext=(8,8), 
                   ha='center', fontweight='bold', fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))

def plot_tdp_energy_scatter(ax, plot_data):
    """Plot 2: TDP Energy Consumption Analysis."""
    plotted_workers = set()
    for i, (compute, tdp, worker) in enumerate(zip(plot_data['avg_compute'], plot_data['total_tdp'], plot_data['workers'])):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax.scatter(compute, tdp, c=plot_data['worker_colors'][worker], s=150, 
                  alpha=0.8, edgecolors='black', linewidth=1.5, marker='s', label=label)
        plotted_workers.add(worker)
    
    ax.set_xlabel('Average Compute Time (seconds)', fontweight='bold')
    ax.set_ylabel('Total TDP Energy Consumption (Joules)', fontweight='bold')
    ax.set_title('TDP Energy vs Compute Performance', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add annotations for worker counts
    for compute, tdp, worker in zip(plot_data['avg_compute'], plot_data['total_tdp'], plot_data['workers']):
        ax.annotate(f'{worker}W', (compute, tdp), 
                   textcoords="offset points", xytext=(8,8), 
                   ha='center', fontweight='bold', fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))

def plot_cpu_utilization_scatter(ax, plot_data):
    """Plot 3: CPU Utilization vs Performance Analysis."""
    plotted_workers = set()
    for i, (compute, cpu_percent, worker) in enumerate(zip(plot_data['avg_compute'], plot_data['avg_psutil_cpu_percent'], plot_data['workers'])):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax.scatter(cpu_percent, compute, c=plot_data['worker_colors'][worker], s=200, 
                  alpha=0.8, edgecolors='black', linewidth=1.5, label=label, marker='D')
        plotted_workers.add(worker)
    
    ax.set_xlabel('Average CPU Utilization (%)', fontweight='bold')
    ax.set_ylabel('Average Compute Time (seconds)', fontweight='bold')
    ax.set_title('CPU Utilization vs Performance', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Add annotations for worker counts
    for compute, cpu_percent, worker in zip(plot_data['avg_compute'], plot_data['avg_psutil_cpu_percent'], plot_data['workers']):
        ax.annotate(f'{worker}W\n{cpu_percent:.1f}%', (cpu_percent, compute), 
                   textcoords="offset points", xytext=(10,10), 
                   ha='center', fontweight='bold', fontsize=9,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

def plot_total_energy_lines(ax, plot_data):
    """Plot 4: Total Energy Consumption Comparison by Worker Count."""
    ax.plot(plot_data['workers'], plot_data['total_rapl'], color=COLORS['primary'], linewidth=3, 
           marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Total RAPL Energy', alpha=0.9)
    ax.plot(plot_data['workers'], plot_data['total_tdp'], color=COLORS['secondary'], linewidth=3, 
           linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Total TDP Energy', alpha=0.9)
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Total Energy Consumption (Joules)', fontweight='bold')
    ax.set_title('Total Energy vs Worker Count', fontweight='bold', pad=20)
    ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(plot_data['workers'])

def plot_average_energy_lines(ax, plot_data):
    """Plot 5: Energy Consumption Comparison by Worker Count."""
    ax.plot(plot_data['workers'], plot_data['avg_rapl'], color=COLORS['primary'], linewidth=3, 
           marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Average RAPL Energy', alpha=0.9)
    ax.plot(plot_data['workers'], plot_data['avg_tdp'], color=COLORS['secondary'], linewidth=3, 
           linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Average TDP Energy', alpha=0.9)
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Average Energy Consumption (Joules)', fontweight='bold')
    ax.set_title('Single Energy vs Worker Count', fontweight='bold', pad=20)
    ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(plot_data['workers'])

def plot_performance_variability(ax, plot_data):
    """Plot 6: Performance Variability."""
    ax.plot(plot_data['workers'], plot_data['min_compute'], color=COLORS['accent1'], linewidth=3,
           marker='^', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Minimum Compute Time', alpha=0.9)
    ax.plot(plot_data['workers'], plot_data['max_compute'], color=COLORS['accent2'], linewidth=3,
           linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Maximum Compute Time', alpha=0.9)
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
    ax.set_title('Performance Variability', fontweight='bold', pad=20)
    ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(plot_data['workers'])

def plot_total_aws_cost_bars(ax, plot_data):
    """Plot 7: Total AWS Cost Analysis."""
    # Calculate total cost based on compute time and workers
    total_cost_aws = [cost * worker for cost, worker in zip(plot_data['cost_aws_moneywise'], plot_data['workers'])]
    
    plotted_workers = set()
    for i, (total_cost, worker) in enumerate(zip(total_cost_aws, plot_data['workers'])):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax.bar(worker, total_cost, color=plot_data['worker_colors'][worker], alpha=0.8, 
              edgecolor='black', linewidth=1.5, label=label, width=0.8)
        plotted_workers.add(worker)
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Total AWS Cost (USD per 1000 executions)', fontweight='bold')
    ax.set_title('Total AWS Lambda Cost Analysis', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(plot_data['workers'])
    
    # Add cost labels on bars
    for total_cost, worker in zip(total_cost_aws, plot_data['workers']):
        ax.text(worker, total_cost + total_cost * 0.02, f'${total_cost:.3f}', 
               ha='center', va='bottom', fontweight='bold', fontsize=10)

def plot_aws_cost_bars(ax, plot_data):
    """Plot 8: AWS Cost Analysis (Bar Chart)."""
    plotted_workers = set()
    for i, (cost, worker) in enumerate(zip(plot_data['cost_aws_moneywise'], plot_data['workers'])):
        label = f'{worker} Workers' if worker not in plotted_workers else None
        ax.bar(worker, cost, color=plot_data['worker_colors'][worker], alpha=0.8, 
              edgecolor='black', linewidth=1.5, label=label, width=0.8)
        plotted_workers.add(worker)
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Cost (USD per 1000 executions)', fontweight='bold')
    ax.set_title('AWS Lambda Cost Analysis (ARM Architecture)', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(plot_data['workers'])
    
    # Add cost labels on bars
    for cost, worker in zip(plot_data['cost_aws_moneywise'], plot_data['workers']):
        ax.text(worker, cost + cost * 0.02, f'${cost:.3f}', 
               ha='center', va='bottom', fontweight='bold', fontsize=10)

def plot_energy_efficiency_boxplot(ax, plot_data):
    """Plot 9: Energy Efficiency Analysis (RAPL vs TDP Deviation)."""
    worker_deviations = {}
    for worker, rapl, tdp in zip(plot_data['workers'], plot_data['total_rapl'], plot_data['total_tdp']):
        deviation = (rapl - tdp)/tdp * 100 if tdp != 0 else 0
        if worker not in worker_deviations:
            worker_deviations[worker] = []
        worker_deviations[worker].append(deviation)
    
    sorted_workers = sorted(worker_deviations.keys())
    deviation_data = [worker_deviations[w] for w in sorted_workers]
    
    # Create professional boxplot
    box_colors = [plot_data['worker_colors'][w] for w in sorted_workers]
    box = ax.boxplot(deviation_data, vert=True, patch_artist=True,
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
    ax.plot(x_positions, p(x_positions), color='red', linewidth=3, 
           linestyle='-', alpha=0.8, label=f'Trend: {equation}')
    
    # Add legend in top-right corner
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    ax.set_xticks(range(1, len(sorted_workers)+1))
    ax.set_xticklabels([f'{w}' for w in sorted_workers])
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Energy Measurement Deviation (%)', fontweight='bold')
    ax.set_title('RAPL vs TDP Measurement Accuracy', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')

def create_combined_plots(data, output_path=None):
    """Create the full 3x3 combined plots using individual plot functions."""
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'plot_titanic_energy_analysis_combined.png')
    
    # Set up professional styling
    setup_plot_style()
    
    # Create figure with improved spacing and size
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(3, 3, figsize=(48, 30))
    
    # Extract and organize data
    plot_data = extract_plot_data(data)
    
    # Create all plots using the individual plot functions
    plot_rapl_energy_scatter(ax1, plot_data)
    plot_tdp_energy_scatter(ax2, plot_data)
    plot_cpu_utilization_scatter(ax3, plot_data)
    plot_total_energy_lines(ax4, plot_data)
    plot_average_energy_lines(ax5, plot_data)
    plot_performance_variability(ax6, plot_data)
    plot_total_aws_cost_bars(ax7, plot_data)
    plot_aws_cost_bars(ax8, plot_data)
    plot_energy_efficiency_boxplot(ax9, plot_data)
    
    # Adjust layout with professional spacing
    plt.tight_layout(pad=4.0)
    
    # Save with high quality for presentations
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()


def process_analysis_folder(analysis_folder, output_folder):
    """Process all 001_analyze_all_profiling_enhanced.json files in the analysis folder."""
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
        print(f"❌ Error: No '001_analyze_all_profiling_enhanced.json' files found in '{analysis_folder}'")
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

def process_analysis_folder_with_hypothesis_2(analysis_folder, output_folder):
    """Process all 001_analyze_all_profiling_enhanced.json files and generate hypothesis 2 plots."""
    if not os.path.exists(analysis_folder):
        print(f"❌ Error: Analysis folder '{analysis_folder}' does not exist.")
        return
    
    # Create hypothesis 2 output folder
    hypothesis_2_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '008_hypotesis_2')
    os.makedirs(hypothesis_2_folder, exist_ok=True)
    
    # Find all JSON analysis files
    analysis_files = []
    for root, dirs, files in os.walk(analysis_folder):
        for file in files:
            if file.endswith('.json') and 'analysis' in file:
                analysis_files.append(os.path.join(root, file))
    
    if not analysis_files:
        print(f"❌ Error: No '001_analyze_all_profiling_enhanced.json' files found in '{analysis_folder}'")
        return
    
    print(f"✓ Found {len(analysis_files)} analysis files to process for hypothesis 2")
    
    # Process each analysis file
    for i, json_path in enumerate(analysis_files):
        try:
            # Load data
            data = load_analysis_data(json_path)
            print(f"✓ Successfully loaded {len(data)} data points from {json_path}")
            
            # Generate output filename based on the relative path
            rel_path = os.path.relpath(json_path, analysis_folder)
            # Remove .json extension and add .png
            hypothesis_2_name = os.path.splitext(rel_path)[0] + '_hypothesis_2.png'
            hypothesis_2_name = hypothesis_2_name.replace(os.sep, '_')
            if hypothesis_2_name.startswith('_'):
                hypothesis_2_name = hypothesis_2_name[1:]
            hypothesis_2_path = os.path.join(hypothesis_2_folder, hypothesis_2_name)
            
            create_hypothesis_2_plots(data, hypothesis_2_path)
            print(f"✅ Generated hypothesis 2 plot: {hypothesis_2_path}")
            
        except FileNotFoundError:
            print(f"❌ Error: Could not find analysis results file at {json_path}")
        except Exception as e:
            print(f"❌ Error processing {json_path}: {str(e)}")
    
    print(f"✅ Hypothesis 2 processing complete! Generated plots in '{hypothesis_2_folder}'")


def plot_merged_energy_consumption(ax, plot_data):
    """Plot merged energy consumption: total and per worker TDP energy in one graph."""
    # Plot total TDP energy
    ax.plot(plot_data['workers'], plot_data['total_tdp'], color=COLORS['primary'], linewidth=3, 
           marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Total TDP Energy', alpha=0.9)
    
    # Plot average (per worker) TDP energy
    ax.plot(plot_data['workers'], plot_data['avg_tdp'], color=COLORS['secondary'], linewidth=3, 
           linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Per Worker TDP Energy', alpha=0.9)
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('TDP Energy Consumption (Joules)', fontweight='bold')
    ax.set_title('TDP Energy Consumption Analysis', fontweight='bold', pad=20)
    ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(plot_data['workers'])

def create_hypothesis_2_plots(data, output_path):
    """Create hypothesis 2 plots - TO BE IMPLEMENTED."""
    # This function is not yet implemented
    # For now, create a placeholder plot
    setup_plot_style()
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.text(0.5, 0.5, 'Hypothesis 2 Plot\n(Not Yet Implemented)', 
            ha='center', va='center', transform=ax.transAxes, fontsize=16)
    ax.set_title('Hypothesis 2 Analysis', fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()

def create_hypothesis_1_plots(data, output_path):
    """Create hypothesis 1 plots: 2 graphs (TDP energy scatter + merged energy consumption)."""
    # Set up professional styling
    setup_plot_style()
    
    # Create figure with 1 row and 2 columns
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Extract and organize data
    plot_data = extract_plot_data(data)
    
    # Plot 1: TDP Energy Scatter (removing RAPL)
    plot_tdp_energy_scatter(ax1, plot_data)
    
    # Plot 2: Merged Energy Consumption (total and per worker)
    plot_merged_energy_consumption(ax2, plot_data)
    
    # Add overall title
    fig.suptitle('TDP Energy Analysis', 
                fontsize=20, fontweight='bold', y=0.98)
    
    # Adjust layout with professional spacing
    plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.94])
    
    # Save with high quality for presentations
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()

def process_analysis_folder_with_hypothesis_1(analysis_folder, output_folder):
    """Process all 001_analyze_all_profiling_enhanced.json files and generate hypothesis 1 plots."""
    if not os.path.exists(analysis_folder):
        print(f"❌ Error: Analysis folder '{analysis_folder}' does not exist.")
        return
    
    # Create hypothesis 1 output folder
    hypothesis_1_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '007A_hypotesis_1')
    os.makedirs(hypothesis_1_folder, exist_ok=True)
    
    # Find all JSON analysis files
    analysis_files = []
    for root, dirs, files in os.walk(analysis_folder):
        for file in files:
            if file.endswith('.json') and 'analysis' in file:
                analysis_files.append(os.path.join(root, file))
    
    if not analysis_files:
        print(f"❌ Error: No '001_analyze_all_profiling_enhanced.json' files found in '{analysis_folder}'")
        return
    
    print(f"✓ Found {len(analysis_files)} analysis files to process for hypothesis 1")
    
    # Process each analysis file
    for i, json_path in enumerate(analysis_files):
        try:
            # Load data
            data = load_analysis_data(json_path)
            print(f"✓ Successfully loaded {len(data)} data points from {json_path}")
            
            # Generate output filename based on the relative path
            rel_path = os.path.relpath(json_path, analysis_folder)
            # Remove .json extension and add .png
            hypothesis_1_name = os.path.splitext(rel_path)[0] + '_hypothesis_1.png'
            hypothesis_1_name = hypothesis_1_name.replace(os.sep, '_')
            if hypothesis_1_name.startswith('_'):
                hypothesis_1_name = hypothesis_1_name[1:]
            hypothesis_1_path = os.path.join(hypothesis_1_folder, hypothesis_1_name)
            
            create_hypothesis_1_plots(data, hypothesis_1_path)
            print(f"✅ Generated hypothesis 1 plot: {hypothesis_1_path}")
            
        except FileNotFoundError:
            print(f"❌ Error: Could not find analysis results file at {json_path}")
        except Exception as e:
            print(f"❌ Error processing {json_path}: {str(e)}")
    
    print(f"✅ Hypothesis 1 processing complete! Generated plots in '{hypothesis_1_folder}'")

def create_hypothesis_3_ml_memory_types_plot(analysis_folder):
    """Create hypothesis 3 plots: separate 1x4 plots for each workload, memory type, and architecture combination."""
    # Create hypothesis 3 output folder
    hypothesis_3_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '007C_hypotesis_3')
    os.makedirs(hypothesis_3_folder, exist_ok=True)
    
    # Set up professional styling
    setup_plot_style()
    
    # Define workloads and stages to process (exclude titanic and pi)
    workloads = ['video', 'ml']
    stages = ['stage0', 'stage1', 'stage2', 'stage3']
    memory_configs = ['512Mb', '1024Mb', '2048Mb']
    architectures = ['arm', 'x86']
    
    generated_plots = []
    
    # Create separate plots for each workload, memory, and architecture combination
    for workload in workloads:
        for memory in memory_configs:
            for arch in architectures:
                print(f"Processing {workload.upper()} workload with {memory} memory on {arch.upper()} architecture...")
                
                # Create figure with 2 rows and 2 columns for this specific combination
                fig, axes = plt.subplots(2, 2, figsize=(16, 16))
                
                # Process each stage
                for stage_idx, stage in enumerate(stages):
                    # Calculate row and column for 2x2 layout
                    row = stage_idx // 2
                    col = stage_idx % 2
                    ax = axes[row, col]
                    
                    # Construct filename for this specific combination
                    filename = f"{workload}_{stage}_aws_{memory}_{arch}_analysis.json"
                    json_path = os.path.join(analysis_folder, filename)
                    
                    if not os.path.exists(json_path):
                        ax.text(0.5, 0.5, f'No data for {stage}', ha='center', va='center', 
                               transform=ax.transAxes, fontsize=14)
                        ax.set_title(f'Stage {stage_idx}', fontweight='bold', pad=20)
                        continue
                    
                    try:
                        # Load data for this specific file
                        data = load_analysis_data(json_path)
                        
                        # Verify data is in the expected format
                        if not isinstance(data, list):
                            print(f"Warning: Expected list but got {type(data)} for {filename}")
                            continue
                            
                        # Add metadata to each data point
                        for item in data:
                            if isinstance(item, dict):
                                item['workload'] = workload
                                item['memory'] = memory
                                item['architecture'] = arch
                                item['stage'] = stage
                            else:
                                print(f"Warning: Expected dict but got {type(item)} in {filename}")
                                break
                        
                        # Extract plot data for this stage
                        plot_data = extract_plot_data(data)
                        
                        # Plot performance variability (similar to graph 6)
                        # Use green for minimum line and architecture-specific colors for maximum
                        min_color = COLORS['accent1']  # Green for minimum line
                        max_color = COLORS['accent1'] if arch == 'arm' else COLORS['accent2']  # Architecture-specific for maximum
                        
                        # Plot minimum compute time (always green)
                        ax.plot(plot_data['workers'], plot_data['min_compute'], 
                               color=min_color, linewidth=3, linestyle='-', 
                               marker='^', markersize=8, markeredgecolor='black', markeredgewidth=1.5,
                               alpha=0.9, label='Minimum Compute Time')
                        
                        # Plot maximum compute time (architecture-specific color)
                        ax.plot(plot_data['workers'], plot_data['max_compute'], 
                               color=max_color, linewidth=3, linestyle='--', 
                               marker='s', markersize=8, markeredgecolor='black', markeredgewidth=1.5,
                               alpha=0.9, label='Maximum Compute Time')
                        
                        ax.set_xlabel('Number of Workers', fontweight='bold')
                        ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
                        ax.set_title(f'Stage {stage_idx} Performance', fontweight='bold', pad=20)
                        ax.grid(True, alpha=0.3, linestyle='--')
                        ax.legend(fontsize=10, loc='best', frameon=True, fancybox=True, shadow=True)
                        
                        # Set x-axis ticks to show worker counts
                        unique_workers = sorted(list(set(plot_data['workers'])))
                        ax.set_xticks(unique_workers)
                        
                    except Exception as e:
                        print(f"Warning: Could not load {filename}: {e}")
                        ax.text(0.5, 0.5, f'Error loading\n{stage}', ha='center', va='center', 
                               transform=ax.transAxes, fontsize=14)
                        ax.set_title(f'Stage {stage_idx}', fontweight='bold', pad=20)
                
                # Add overall title for the entire figure
                fig.suptitle(f'{workload.upper()} Workload - {memory} Memory - {arch.upper()} Architecture\nPerformance Variability Across 4 Stages', 
                            fontsize=20, fontweight='bold', y=0.98)
                
                # Adjust layout
                plt.tight_layout(pad=3.0, rect=[0, 0, 1, 0.94])
                
                # Save the plot with descriptive filename including architecture
                output_filename = f'hypothesis_3_{workload}_{memory}_{arch}_stages_performance.png'
                output_path = os.path.join(hypothesis_3_folder, output_filename)
                plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none', format='png')
                plt.close()
                
                generated_plots.append(output_path)
                print(f"✅ Generated plot: {output_path}")
    
    print(f"✅ Generated {len(generated_plots)} hypothesis 3 plots in '007C_hypotesis_3/' folder")
    return generated_plots


def main():
    # Define the analysis folder and output folder
    analysis_folder = '001_analysis_results'
    output_folder = '007_generate_combined_plots'
    
    print("🚀 Starting comprehensive plot generation...")
    print("=" * 60)
    
    # Execute all processing functions sequentially
    print("📊 Step 1: Generating combined plots (3x3 matrix)...")
    process_analysis_folder(analysis_folder, output_folder)
    
    print("\n📈 Step 2: Generating hypothesis 1 plots (1x2 matrix - TDP energy analysis)...")
    process_analysis_folder_with_hypothesis_1(analysis_folder, output_folder)
    
    # Note: hypothesis 2 function is not implemented yet
    # print("\n📉 Step 3: Generating hypothesis 2 plots (1x1 matrix - graph 6)...")
    # process_analysis_folder_with_hypothesis_2(analysis_folder, output_folder)
    
    print("\n� Step 4: Generating hypothesis 3 plots (1x4 matrix - video and ml stages)...")
    create_hypothesis_3_ml_memory_types_plot(analysis_folder)
    
    print("\n" + "=" * 60)
    print("✅ All plot generation completed successfully!")
    print(f"📊 Combined plots: '{output_folder}'")
    print(f"📁 Hypothesis 1 plots: '007A_hypotesis_1/'")
    # print(f"📁 Hypothesis 2 plots: '008_hypotesis_2/'")
    print(f"📁 Hypothesis 3 plots: '007C_hypotesis_3/'")
 

if __name__ == "__main__":
    main()

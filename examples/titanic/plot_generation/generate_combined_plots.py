import json
import matplotlib.pyplot as plt
import numpy as np
import os
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
    return data

def create_combined_plots(data, output_path=None):
    """Create a professional combined plot with multiple visualizations for public presentation."""
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'plot_energy_analysis_avg_combined.png')
    
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
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(1, 6, figsize=(48, 10))
    
    # Extract data for plotting
    workers = [d['workers'] for d in data]
    total_rapl = [d['total_rapl'] for d in data]
    total_tdp = [d['total_tdp'] for d in data]
    avg_rapl = [d['avg_rapl'] for d in data]
    avg_tdp = [d['avg_tdp'] for d in data]
    avg_compute = [d['avg_compute'] for d in data]
    min_compute = [d['min_compute'] for d in data]
    max_compute = [d['max_compute'] for d in data]
    min_rapl = [d['min_rapl'] for d in data]
    max_rapl = [d['max_rapl'] for d in data]
    
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
    
    # Plot 3: Energy Consumption Comparison by Worker Count
    ax3.plot(workers, avg_rapl, color=COLORS['primary'], linewidth=3, 
            marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Average RAPL Energy', alpha=0.9)
    ax3.plot(workers, avg_tdp, color=COLORS['secondary'], linewidth=3, 
            linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Average TDP Energy', alpha=0.9)
    
    ax3.set_xlabel('Number of Workers', fontweight='bold')
    ax3.set_ylabel('Average Energy Consumption (Joules)', fontweight='bold')
    ax3.set_title('Single Energy vs Worker', fontweight='bold', pad=20)
    ax3.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_xticks(workers)
    
    # Plot 4: Total Energy Consumption Comparison by Worker Count
    ax4.plot(workers, total_rapl, color=COLORS['primary'], linewidth=3, 
            marker='o', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Total RAPL Energy', alpha=0.9)
    ax4.plot(workers, total_tdp, color=COLORS['secondary'], linewidth=3, 
            linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Total TDP Energy', alpha=0.9)
    
    ax4.set_xlabel('Number of Workers', fontweight='bold')
    ax4.set_ylabel('Total Energy Consumption (Joules)', fontweight='bold')
    ax4.set_title('Total Energy vs Worker', fontweight='bold', pad=20)
    ax4.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_xticks(workers)
    
    # Plot 5: Compute Time Performance Analysis
    ax5.plot(workers, min_compute, color=COLORS['accent1'], linewidth=3,
            marker='^', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Minimum Compute Time', alpha=0.9)
    ax5.plot(workers, max_compute, color=COLORS['accent2'], linewidth=3,
            linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
            label='Maximum Compute Time', alpha=0.9)
    
    ax5.set_xlabel('Number of Workers', fontweight='bold')
    ax5.set_ylabel('Execution Time (seconds)', fontweight='bold')
    ax5.set_title('Performance Variability Analysis', fontweight='bold', pad=20)
    ax5.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax5.grid(True, alpha=0.3, linestyle='--')
    ax5.set_xticks(workers)
    
    # Plot 6: Energy Efficiency Analysis (RAPL vs TDP Deviation)
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
    box = ax6.boxplot(deviation_data, vert=True, patch_artist=True,
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
    ax6.plot(x_positions, p(x_positions), color='red', linewidth=3, 
            linestyle='-', alpha=0.8, label=f'Trend: {equation}')
    
    # Add legend in top-right corner
    ax6.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    ax6.set_xticks(range(1, len(sorted_workers)+1))
    ax6.set_xticklabels([f'{w}' for w in sorted_workers])
    ax6.set_xlabel('Number of Workers', fontweight='bold')
    ax6.set_ylabel('Energy Measurement Deviation (%)', fontweight='bold')
    ax6.set_title('RAPL vs TDP Measurement Accuracy', fontweight='bold', pad=20)
    ax6.grid(True, alpha=0.3, linestyle='--')
    
    # Adjust layout with professional spacing
    plt.tight_layout(pad=4.0)
    
    # Save with high quality for presentations
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()
    print(f"Professional energy analysis plots saved to {output_path}")
    print("✓ High-resolution plots ready for public presentation")
    print("✓ Professional styling with distinct colors and legends applied")
    print("✓ Key insights and annotations included for clarity")

def main():
    """Generate professional energy analysis plots for public presentation."""
    # Path to analysis results
    json_path = '/home/users/iarriazu/flexecutor-main/examples/titanic/plot_generation/analysis_results.json'
    
    print("🚀 Generating professional energy analysis visualization...")
    print("📊 Processing data and applying professional styling...")
    
    try:
        # Load data
        data = load_analysis_data(json_path)
        print(f"✓ Successfully loaded {len(data)} data points")
        
        # Generate professional combined plots
        create_combined_plots(data)
        print("✅ Professional visualization complete!")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find analysis results file at {json_path}")
        print("Please ensure the analysis_results.json file exists in the correct location.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please check your data format and try again.")

if __name__ == "__main__":
    main()

import json
import matplotlib.pyplot as plt
import numpy as np
import os

def load_analysis_data(json_path):
    """Load and parse the analysis_results.json file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def create_combined_plots(data, output_path=None):
    """Create a combined plot with multiple visualizations."""
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'plot_avg_combined.png')
    
    # Create figure with 1 row and 5 columns
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1, 5, figsize=(35, 8))
    
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
    
    # Plot 1: RAPL Scatter Plot
    ax1.scatter(avg_compute, total_rapl, c='blue', s=100)
    ax1.set_xlabel('Average Compute Time (seconds)', fontsize=12)
    ax1.set_ylabel('Total RAPL Energy (Joules)', fontsize=12)
    ax1.set_title('Total RAPL vs Compute Time', fontsize=14)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: TDP Scatter Plot 
    ax2.scatter(avg_compute, total_tdp, c='red', s=100, marker='s')
    ax2.set_xlabel('Average Compute Time (seconds)', fontsize=12)
    ax2.set_ylabel('Total TDP Energy (Joules)', fontsize=12)
    ax2.set_title('Total TDP vs Compute Time', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    # Add worker count labels to both scatter plots
    for i, (time, rapl, tdp, worker) in enumerate(zip(avg_compute, total_rapl, total_tdp, workers)):
        ax1.annotate(str(worker), (time, rapl), textcoords="offset points", xytext=(5,5), ha='center')
        ax2.annotate(str(worker), (time, tdp), textcoords="offset points", xytext=(5,5), ha='center')
    
    # Plot 3: Energy vs Workers
    ax3.plot(workers, avg_rapl, 'b-o', label='Average RAPL')
    ax3.plot(workers, avg_tdp, 'r--s', label='Average TDP')
    ax3.set_xlabel('Number of Workers', fontsize=12)
    ax3.set_ylabel('Energy (Joules)', fontsize=12)
    ax3.set_title('Energy Consumption vs Workers', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Compute Time Extremes vs Workers
    ax4.plot(workers, min_compute, 'g-^', label='Minimum Compute Time')
    ax4.plot(workers, max_compute, color='orange', linestyle='--', marker='s', label='Maximum Compute Time')
    ax4.set_xlabel('Number of Workers', fontsize=12)
    ax4.set_ylabel('Time (seconds)', fontsize=12)
    ax4.set_title('Compute Time Extremes vs Workers', fontsize=14)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Deviation by Workers
    # Group deviations by worker count
    worker_deviations = {}
    for worker, rapl, tdp in zip(workers, total_rapl, total_tdp):
        deviation = (rapl - tdp)/tdp * 100
        if worker not in worker_deviations:
            worker_deviations[worker] = []
        worker_deviations[worker].append(deviation)
    
    # Prepare data for boxplot
    sorted_workers = sorted(worker_deviations.keys())
    deviation_data = [worker_deviations[w] for w in sorted_workers]
    
    # Create boxplot for each worker group
    box = ax5.boxplot(deviation_data, vert=True, patch_artist=True,
                    boxprops=dict(facecolor='lightblue'),
                    medianprops=dict(color='black', linewidth=2))
    
    ax5.set_xticks(range(1, len(sorted_workers)+1))
    ax5.set_xticklabels([str(w) for w in sorted_workers])
    ax5.set_xlabel('Number of Workers', fontsize=12)
    ax5.set_ylabel('Percentage Deviation (%)', fontsize=12)
    ax5.set_title('RAPL/TDP Deviation by Worker Count', fontsize=14)
    ax5.grid(True, alpha=0.3)
    
    # Adjust layout and save
    plt.tight_layout(pad=3.0)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Combined plots saved to {output_path}")

def main():
    # Path to analysis results
    json_path = '/home/users/iarriazu/flexecutor-main/examples/titanic/plot_generation/analysis_results.json'
    
    try:
        # Load data
        data = load_analysis_data(json_path)
        
        # Generate combined plots
        create_combined_plots(data)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

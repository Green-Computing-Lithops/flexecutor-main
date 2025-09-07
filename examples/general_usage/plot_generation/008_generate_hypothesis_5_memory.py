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

# Memory-specific colors
MEMORY_COLORS = {
    '512Mb': COLORS['accent1'],   # Green
    '1024Mb': COLORS['primary'],  # Blue  
    '2048Mb': COLORS['accent2']   # Red
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

def extract_memory_comparison_data(analysis_folder, workload, stage, architecture):
    """Extract data for memory comparison for a specific workload, stage, and architecture."""
    memory_configs = ['512Mb', '1024Mb', '2048Mb']
    memory_data = {}
    
    for memory in memory_configs:
        filename = f"{workload}_{stage}_aws_{memory}_{architecture}_analysis.json"
        json_path = os.path.join(analysis_folder, filename)
        
        if os.path.exists(json_path):
            try:
                data = load_analysis_data(json_path)
                if data:
                    # Organize data by worker count
                    worker_data = {}
                    for d in data:
                        worker_count = d['workers']
                        if worker_count not in worker_data:
                            worker_data[worker_count] = []
                        worker_data[worker_count].append({
                            'execution_time': d['avg_worker_time_execution'],
                            'energy_consumption': d['avg_tdp']
                        })
                    
                    # Calculate averages for each worker count
                    for worker_count in worker_data:
                        avg_execution_time = np.mean([item['execution_time'] for item in worker_data[worker_count]])
                        avg_energy_consumption = np.mean([item['energy_consumption'] for item in worker_data[worker_count]])
                        
                        if worker_count not in memory_data:
                            memory_data[worker_count] = {}
                        
                        memory_data[worker_count][memory] = {
                            'avg_execution_time': avg_execution_time,
                            'avg_energy_consumption': avg_energy_consumption
                        }
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
                continue
    
    return memory_data

def plot_memory_execution_time_bars(ax, memory_data, workload, stage, architecture):
    """Plot execution time comparison across memory configurations grouped by workers."""
    if not memory_data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
               transform=ax.transAxes, fontsize=14)
        ax.set_title(f'{workload.upper()} {stage} - Execution Time\n({architecture.upper()} Architecture)', 
                    fontweight='bold', pad=20)
        return
    
    # Get sorted worker counts and memory configurations
    workers = sorted(memory_data.keys())
    memory_configs = ['512Mb', '1024Mb', '2048Mb']
    
    # Set up grouped bar chart
    x = np.arange(len(workers))  # Worker positions
    width = 0.25  # Width of bars
    
    # Create bars for each memory configuration
    for i, memory in enumerate(memory_configs):
        execution_times = []
        for worker in workers:
            if memory in memory_data[worker]:
                execution_times.append(memory_data[worker][memory]['avg_execution_time'])
            else:
                execution_times.append(0)  # Missing data
        
        bars = ax.bar(x + i * width, execution_times, width, 
                     label=f'{memory.replace("Mb", "MB")}',
                     color=MEMORY_COLORS[memory], alpha=0.8, 
                     edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar, time_val in zip(bars, execution_times):
            if time_val > 0:  # Only show labels for non-zero values
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height * 0.01,
                       f'{time_val:.2f}s', ha='center', va='bottom', 
                       fontweight='bold', fontsize=9, rotation=0)
    
    # Customize the plot
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Average Execution Time (seconds)', fontweight='bold')
    ax.set_title(f'{workload.upper()} {stage} - Execution Time\n({architecture.upper()} Architecture)', 
                fontweight='bold', pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels([f'{w}' for w in workers])
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')

def plot_memory_energy_consumption_bars(ax, memory_data, workload, stage, architecture):
    """Plot energy consumption comparison across memory configurations grouped by workers."""
    if not memory_data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
               transform=ax.transAxes, fontsize=14)
        ax.set_title(f'{workload.upper()} {stage} - Energy Consumption\n({architecture.upper()} Architecture)', 
                    fontweight='bold', pad=20)
        return
    
    # Get sorted worker counts and memory configurations
    workers = sorted(memory_data.keys())
    memory_configs = ['512Mb', '1024Mb', '2048Mb']
    
    # Set up grouped bar chart
    x = np.arange(len(workers))  # Worker positions
    width = 0.25  # Width of bars
    
    # Create bars for each memory configuration
    for i, memory in enumerate(memory_configs):
        energy_consumptions = []
        for worker in workers:
            if memory in memory_data[worker]:
                energy_consumptions.append(memory_data[worker][memory]['avg_energy_consumption'])
            else:
                energy_consumptions.append(0)  # Missing data
        
        bars = ax.bar(x + i * width, energy_consumptions, width, 
                     label=f'{memory.replace("Mb", "MB")}',
                     color=MEMORY_COLORS[memory], alpha=0.8, 
                     edgecolor='black', linewidth=1.5)
        
        # Store values for min/max calculation
        if i == 0:  # First iteration, initialize tracking
            all_energy_values = []
        all_energy_values.extend([val for val in energy_consumptions if val > 0])
    
    # Calculate min and max values across all memory configurations
    if all_energy_values:
        min_energy = min(all_energy_values)
        max_energy = max(all_energy_values)
        
        # Add value labels only for min and max values
        for i, memory in enumerate(memory_configs):
            energy_consumptions = []
            for worker in workers:
                if memory in memory_data[worker]:
                    energy_consumptions.append(memory_data[worker][memory]['avg_energy_consumption'])
                else:
                    energy_consumptions.append(0)  # Missing data
            
            bars = ax.containers[i]  # Get the bars for this memory configuration
            for bar, energy_val in zip(bars, energy_consumptions):
                if energy_val > 0 and (abs(energy_val - min_energy) < 0.001 or abs(energy_val - max_energy) < 0.001):
                    height = bar.get_height()
                    label_text = f'{energy_val:.2f}J'
                    if abs(energy_val - min_energy) < 0.001:
                        label_text += ' (MIN)'
                    if abs(energy_val - max_energy) < 0.001:
                        label_text += ' (MAX)'
                    
                    ax.text(bar.get_x() + bar.get_width()/2., height + height * 0.01,
                           label_text, ha='center', va='bottom', 
                           fontweight='bold', fontsize=9, rotation=0,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    # Customize the plot
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Average Energy Consumption (Joules)', fontweight='bold')
    ax.set_title(f'{workload.upper()} {stage} - Energy Consumption\n({architecture.upper()} Architecture)', 
                fontweight='bold', pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels([f'{w}' for w in workers])
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')

def create_hypothesis_5_memory_plots(analysis_folder, workload, stage, architecture, output_path):
    """Create hypothesis 5 memory comparison plots: 2 bar graphs (execution time + energy consumption)."""
    # Set up professional styling
    setup_plot_style()
    
    # Create figure with 1 row and 2 columns - larger figure for bigger graphs
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Extract memory comparison data
    memory_data = extract_memory_comparison_data(analysis_folder, workload, stage, architecture)
    
    # Plot 1: Execution Time Comparison
    plot_memory_execution_time_bars(ax1, memory_data, workload, stage, architecture)
    
    # Plot 2: Energy Consumption Comparison
    plot_memory_energy_consumption_bars(ax2, memory_data, workload, stage, architecture)
    
    # Add overall title with reduced spacing
    fig.suptitle(f'Memory Configuration Impact Analysis - {workload.upper()} {stage} - {architecture.upper()} Architecture', 
                fontsize=18, fontweight='bold', y=0.95)
    
    # Add legend for memory configurations at the bottom with reduced spacing
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=MEMORY_COLORS[mem], alpha=0.8, edgecolor='black') 
                      for mem in ['512Mb', '1024Mb', '2048Mb']]
    fig.legend(legend_elements, ['512MB Memory', '1024MB Memory', '2048MB Memory'], 
              loc='lower center', bbox_to_anchor=(0.5, 0.01), ncol=3, fontsize=12)
    
    # Adjust layout with minimal spacing to maximize graph size
    plt.tight_layout(pad=1.5, rect=[0, 0.04, 1, 0.92])
    
    # Save with high quality for presentations
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()

def process_hypothesis_5_memory_analysis(analysis_folder):
    """Process all combinations and generate hypothesis 5 memory comparison plots."""
    # Fix: Use consistent directory naming
    hypothesis_5_folder = "008_generate_hypothesis_5_memory"
    os.makedirs(hypothesis_5_folder, exist_ok=True)
    
    # Define workloads, stages, and architectures to process
    workloads = ['video', 'ml', 'pi', 'titanic']
    multi_stage_workloads = ['video', 'ml']  # Workloads with multiple stages
    single_stage_workloads = ['pi', 'titanic']  # Workloads with single stage
    architectures = ['arm', 'x86']
    
    generated_plots = []
    
    print("🚀 Starting Hypothesis 5 Memory Analysis...")
    print("=" * 60)
    
    # Process multi-stage workloads (video, ml)
    for workload in multi_stage_workloads:
        stages = ['stage0', 'stage1', 'stage2', 'stage3']
        for stage in stages:
            for arch in architectures:
                print(f"Processing {workload.upper()} {stage} on {arch.upper()} architecture...")
                
                # Generate output filename
                output_filename = f'hypothesis_5_memory_{workload}_{stage}_{arch}_comparison.png'
                output_path = os.path.join(hypothesis_5_folder, output_filename)
                
                # Create the memory comparison plots
                create_hypothesis_5_memory_plots(analysis_folder, workload, stage, arch, output_path)
                
                generated_plots.append(output_path)
                print(f"✅ Generated plot: {output_path}")
    
    # Process single-stage workloads (pi, titanic)
    for workload in single_stage_workloads:
        stage = 'stage'  # Single stage for pi and titanic
        for arch in architectures:
            print(f"Processing {workload.upper()} {stage} on {arch.upper()} architecture...")
            
            # Generate output filename
            output_filename = f'hypothesis_5_memory_{workload}_{stage}_{arch}_comparison.png'
            output_path = os.path.join(hypothesis_5_folder, output_filename)
            
            # Create the memory comparison plots
            create_hypothesis_5_memory_plots(analysis_folder, workload, stage, arch, output_path)
            
            generated_plots.append(output_path)
            print(f"✅ Generated plot: {output_path}")
    
    print(f"\n✅ Generated {len(generated_plots)} hypothesis 5 memory plots in '{hypothesis_5_folder}/' folder")
    print("=" * 60)
    return generated_plots

def main():
    """Main function to run hypothesis 5 memory analysis."""
    # Define the analysis folder
    analysis_folder = '001_analysis_results'
    
    if not os.path.exists(analysis_folder):
        print(f"❌ Error: Analysis folder '{analysis_folder}' does not exist.")
        return
    
    # Process hypothesis 5 memory analysis
    process_hypothesis_5_memory_analysis(analysis_folder)
    
    print("✅ Hypothesis 5 Memory Analysis completed successfully!")

if __name__ == "__main__":
    main()

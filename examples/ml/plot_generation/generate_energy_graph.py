import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import re

def load_and_parse_data(stage_files):
    """Load JSON data from multiple stage files and parse it into a structured format."""
    all_stages_data = {}
    
    for stage_name, json_file_path in stage_files.items():
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Dictionary to store data grouped by (cpu, memory)
            grouped_data = defaultdict(lambda: {'workers': [], 'energy_values': []})
            
            # Parse each configuration
            for config_key, config_data in data.items():
                # Extract cpu, memory, workers from key like "(4, 1536, 4)"
                match = re.match(r'\((\d+),\s*(\d+),\s*(\d+)\)', config_key)
                if match:
                    cpu = int(match.group(1))
                    memory = int(match.group(2))
                    workers = int(match.group(3))
                    
                    # Get TDP data (list of lists)
                    energy_data = config_data.get('TDP', [])
                    
                    # Calculate both mean and total energy for this configuration
                    all_energy_values = []
                    for run in energy_data:
                        all_energy_values.extend(run)
                    
                    # Get RAPL data (list of lists)
                    consumption_data = config_data.get('RAPL', [])
                    all_consumption_values = []
                    for run in consumption_data:
                        all_consumption_values.extend(run)
                    
                    # Get time_consumption data (list of values)
                    time_consumption_data = config_data.get('time_consumption', [])
                    all_time_consumption_values = []
                    if time_consumption_data:
                        for run in time_consumption_data:
                            if isinstance(run, list):
                                all_time_consumption_values.extend(run)
                            else:
                                all_time_consumption_values.append(run)
                    
                    # Get worker_time_execution data (list of values)
                    cpu_time_data = config_data.get('worker_time_execution', [])
                    all_cpu_time_values = []
                    if cpu_time_data:
                        for run in cpu_time_data:
                            if isinstance(run, list):
                                all_cpu_time_values.extend(run)
                            else:
                                all_cpu_time_values.append(run)
                    
                    if all_energy_values and all_consumption_values:
                        mean_energy = np.mean(all_energy_values)
                        total_energy = np.sum(all_energy_values)
                        mean_consumption = np.mean(all_consumption_values)
                        total_consumption = np.sum(all_consumption_values)
                        
                        # Calculate time consumption metrics if available
                        mean_time_consumption = np.mean(all_time_consumption_values) if all_time_consumption_values else 0
                        
                        # Calculate CPU time metrics if available
                        mean_cpu_time = np.mean(all_cpu_time_values) if all_cpu_time_values else 0
                        
                        # Group by (cpu, memory)
                        group_key = f"{cpu} CPU, {memory}MB"
                        grouped_data[group_key]['workers'].append(workers)
                        grouped_data[group_key]['energy_values'].append(mean_energy)
                        grouped_data[group_key]['total_energy_values'] = grouped_data[group_key].get('total_energy_values', [])
                        grouped_data[group_key]['total_energy_values'].append(total_energy)
                        grouped_data[group_key]['consumption_values'] = grouped_data[group_key].get('consumption_values', [])
                        grouped_data[group_key]['consumption_values'].append(mean_consumption)
                        grouped_data[group_key]['total_consumption_values'] = grouped_data[group_key].get('total_consumption_values', [])
                        grouped_data[group_key]['total_consumption_values'].append(total_consumption)
                        grouped_data[group_key]['time_consumption_values'] = grouped_data[group_key].get('time_consumption_values', [])
                        grouped_data[group_key]['time_consumption_values'].append(mean_time_consumption)
                        grouped_data[group_key]['cpu_time_values'] = grouped_data[group_key].get('cpu_time_values', [])
                        grouped_data[group_key]['cpu_time_values'].append(mean_cpu_time)
            
            all_stages_data[stage_name] = grouped_data
            
        except FileNotFoundError:
            print(f"Warning: Could not find file {json_file_path}")
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON format in file {json_file_path}")
    
    return all_stages_data

def create_energy_plot(all_stages_data, output_file='energy_vs_workers.png'):
    """Create a 2x4 matrix plot showing energy consumption vs number of workers for all stages."""
    fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(2, 4, figsize=(32, 16))
    
    # Define colors for each stage
    stage_colors = {
        'stage0': 'gold',
        'stage1': 'blue', 
        'stage2': 'green',
        'stage3': 'purple'
    }
    
    # Collect all worker counts for consistent x-axis
    all_workers = set()
    
    # Define the target configuration to plot (use the one with most data points)
    target_config = "4 CPU, 1536MB"
    
    # Plot data for each stage
    for stage_name, stage_data in all_stages_data.items():
        color = stage_colors.get(stage_name, 'black')
        
        # Look for the target configuration, or use the first available if not found
        group_data = None
        if target_config in stage_data:
            group_data = stage_data[target_config]
            config_label = target_config
        elif stage_data:  # If target config not found, use the first available
            config_label = list(stage_data.keys())[0]
            group_data = stage_data[config_label]
        
        if group_data:
            workers = group_data['workers']
            energy_values = group_data['energy_values']
            total_energy_values = group_data['total_energy_values']
            consumption_values = group_data['consumption_values']
            total_consumption_values = group_data['total_consumption_values']
            
            all_workers.update(workers)
            
            # Sort by workers for proper line plotting
            sorted_pairs = sorted(zip(workers, energy_values))
            workers_sorted, energy_sorted = zip(*sorted_pairs)
            
            sorted_total_pairs = sorted(zip(workers, total_energy_values))
            workers_total_sorted, total_energy_sorted = zip(*sorted_total_pairs)
            
            sorted_consumption_pairs = sorted(zip(workers, consumption_values))
            workers_consumption_sorted, consumption_sorted = zip(*sorted_consumption_pairs)
            
            sorted_total_consumption_pairs = sorted(zip(workers, total_consumption_values))
            workers_total_consumption_sorted, total_consumption_sorted = zip(*sorted_total_consumption_pairs)
            
            # Create label with stage and config info
            stage_label = f"{stage_name.upper()}"
            if config_label != target_config:
                stage_label += f" ({config_label})"
            
            # Top row
            # ax1 - Average Energy Lithops
            ax1.plot(workers_sorted, energy_sorted, 
                    marker='o', linewidth=2, markersize=8,
                    color=color,
                    label=stage_label)
            
            # ax2 - Average Energy Consumption
            ax2.plot(workers_consumption_sorted, consumption_sorted, 
                    marker='o', linewidth=2, markersize=8,
                    color=color,
                    label=stage_label)
            
            # ax3 - Time Consumption (only plot if data exists)
            time_consumption_values = group_data.get('time_consumption_values', [])
            if time_consumption_values and any(v > 0 for v in time_consumption_values):
                valid_time_data = [(w, t) for w, t in zip(workers, time_consumption_values) if t > 0]
                if valid_time_data:
                    workers_time, time_values = zip(*sorted(valid_time_data))
                    ax3.plot(workers_time, time_values, 
                            marker='o', linewidth=2, markersize=8,
                            color=color,
                            label=stage_label)
            
            # ax4 - Worker Function CPU User Time (only plot if data exists)
            cpu_time_values = group_data.get('cpu_time_values', [])
            if cpu_time_values and any(v > 0 for v in cpu_time_values):
                valid_cpu_data = [(w, c) for w, c in zip(workers, cpu_time_values) if c > 0]
                if valid_cpu_data:
                    workers_cpu, cpu_values_sorted = zip(*sorted(valid_cpu_data))
                    ax4.plot(workers_cpu, cpu_values_sorted, 
                            marker='o', linewidth=2, markersize=8,
                            color=color,
                            label=stage_label)
            
            # Bottom row
            # ax5 - Total Energy Lithops
            ax5.plot(workers_total_sorted, total_energy_sorted, 
                    marker='s', linewidth=2, markersize=8,
                    color=color, linestyle='--',
                    label=stage_label)
            
            # ax6 - Total Energy Consumption
            ax6.plot(workers_total_consumption_sorted, total_consumption_sorted, 
                    marker='s', linewidth=2, markersize=8,
                    color=color, linestyle='--',
                    label=stage_label)
            
            # ax7 - Total Time Consumption (only plot if data exists)
            if time_consumption_values and any(v > 0 for v in time_consumption_values):
                valid_time_data = [(w, t) for w, t in zip(workers, time_consumption_values) if t > 0]
                if valid_time_data:
                    workers_time, time_values = zip(*sorted(valid_time_data))
                    # Calculate total time consumption (sum for each worker count)
                    total_time_values = [t * w for w, t in zip(workers_time, time_values)]
                    ax7.plot(workers_time, total_time_values, 
                            marker='s', linewidth=2, markersize=8,
                            color=color, linestyle='--',
                            label=stage_label)
            
            # ax8 - Total CPU User Time (only plot if data exists)
            if cpu_time_values and any(v > 0 for v in cpu_time_values):
                valid_cpu_data = [(w, c) for w, c in zip(workers, cpu_time_values) if c > 0]
                if valid_cpu_data:
                    workers_cpu, cpu_values_sorted = zip(*sorted(valid_cpu_data))
                    # Calculate total CPU time (sum for each worker count)
                    total_cpu_values = [c * w for w, c in zip(workers_cpu, cpu_values_sorted)]
                    ax8.plot(workers_cpu, total_cpu_values, 
                            marker='s', linewidth=2, markersize=8,
                            color=color, linestyle='--',
                            label=stage_label)
    
    # Get worker ticks for all subplots
    worker_ticks = sorted(all_workers)
    
    # Customize all 6 subplots
    # Top row
    ax1.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Energy Lithops', fontsize=12, fontweight='bold')
    ax1.set_title('Average Energy Lithops vs Number of Workers', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(worker_ticks)
    
    ax2.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average Energy Consumption', fontsize=12, fontweight='bold')
    ax2.set_title('Average Energy Consumption vs Number of Workers', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(worker_ticks)
    
    ax3.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Time Consumption (seconds)', fontsize=12, fontweight='bold')
    ax3.set_title('Time Consumption vs Number of Workers', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(worker_ticks)
    
    ax4.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Worker Function CPU User Time', fontsize=12, fontweight='bold')
    ax4.set_title('Worker Function CPU User Time vs Number of Workers', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xticks(worker_ticks)
    
    # Bottom row
    ax5.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Total Energy Lithops', fontsize=12, fontweight='bold')
    ax5.set_title('Total Energy Lithops vs Number of Workers', fontsize=14, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_xticks(worker_ticks)
    
    ax6.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Total Energy Consumption', fontsize=12, fontweight='bold')
    ax6.set_title('Total Energy Consumption vs Number of Workers', fontsize=14, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    ax6.set_xticks(worker_ticks)
    
    ax7.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax7.set_ylabel('Total Time Consumption (seconds)', fontsize=12, fontweight='bold')
    ax7.set_title('Total Time Consumption vs Number of Workers', fontsize=14, fontweight='bold')
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    ax7.set_xticks(worker_ticks)
    
    ax8.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
    ax8.set_ylabel('Total CPU User Time', fontsize=12, fontweight='bold')
    ax8.set_title('Total CPU User Time vs Number of Workers', fontsize=14, fontweight='bold')
    ax8.legend()
    ax8.grid(True, alpha=0.3)
    ax8.set_xticks(worker_ticks)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {output_file}")
    
    # Close the plot to free memory
    plt.close()

def print_data_summary(all_stages_data):
    """Print a summary of the parsed data for all stages."""
    print("Data Summary:")
    print("=" * 120)
    
    for stage_name, stage_data in all_stages_data.items():
        print(f"\n{stage_name.upper()}:")
        print("-" * 60)
        
        for group_key, group_data in stage_data.items():
            workers = group_data['workers']
            energy_values = group_data['energy_values']
            total_energy_values = group_data['total_energy_values']
            consumption_values = group_data['consumption_values']
            total_consumption_values = group_data['total_consumption_values']
            time_consumption_values = group_data.get('time_consumption_values', [])
            cpu_time_values = group_data.get('cpu_time_values', [])
            
            print(f"\n{group_key}:")
            print("  Workers | Avg Lithops | Total Lithops | Avg Consumption | Total Consumption | Time Consumption | CPU Time")
            print("  --------|-------------|---------------|-----------------|-------------------|------------------|----------")
            
            for i, w in enumerate(sorted(range(len(workers)), key=lambda x: workers[x])):
                worker_count = workers[w]
                avg_e = energy_values[w]
                total_e = total_energy_values[w]
                avg_c = consumption_values[w]
                total_c = total_consumption_values[w]
                time_c = time_consumption_values[w] if w < len(time_consumption_values) else 0
                cpu_t = cpu_time_values[w] if w < len(cpu_time_values) else 0
                
                print(f"  {worker_count:7d} | {avg_e:11.2f} | {total_e:13.2f} | {avg_c:15.2f} | {total_c:17.2f} | {time_c:16.2f} | {cpu_t:8.0f}")

def main():
    # Paths to all stage JSON files
    stage_files = {
        'stage0': '/home/users/iarriazu/flexecutor-main/examples/ml/profiling/machine_learning/stage0.json',
        'stage1': '/home/users/iarriazu/flexecutor-main/examples/ml/profiling/machine_learning/stage1.json',
        'stage2': '/home/users/iarriazu/flexecutor-main/examples/ml/profiling/machine_learning/stage2.json',
        'stage3': '/home/users/iarriazu/flexecutor-main/examples/ml/profiling/machine_learning/stage3.json'
    }
    
    try:
        # Load and parse the data from all stages
        print("Loading data from all stage files...")
        all_stages_data = load_and_parse_data(stage_files)
        
        if not all_stages_data:
            print("Error: No data could be loaded from any stage files")
            return
        
        # Print data summary
        print_data_summary(all_stages_data)
        
        # Create the plot
        print("\nGenerating plot...")
        create_energy_plot(all_stages_data)
        
        print("\nGraph generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

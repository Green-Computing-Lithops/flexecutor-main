import json
import matplotlib.pyplot as plt
import numpy as np
import re

def load_and_parse_stage1_data(json_file_path):
    """Load and parse stage1.json data for scatter plot."""
    scatter_data = []
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Parse each configuration
        for config_key, config_data in data.items():
            # Extract cpu, memory, workers from key like "(4, 1536, 4)"
            match = re.match(r'\((\d+),\s*(\d+),\s*(\d+)\)', config_key)
            if match:
                cpu = int(match.group(1))
                memory = int(match.group(2))
                workers = int(match.group(3))
                
                # Get time_consumption data
                time_consumption_data = config_data.get('time_consumption', [])
                execution_time = 0
                if time_consumption_data:
                    # Calculate average execution time
                    all_time_values = []
                    for run in time_consumption_data:
                        if isinstance(run, list):
                            all_time_values.extend(run)
                        else:
                            all_time_values.append(run)
                    if all_time_values:
                        execution_time = np.mean(all_time_values)
                
                # Get RAPL data
                RAPL_data = config_data.get('RAPL', [])
                RAPL = 0
                if RAPL_data:
                    # Calculate average energy consumption
                    all_energy_values = []
                    for run in RAPL_data:
                        all_energy_values.extend(run)
                    if all_energy_values:
                        RAPL = np.mean(all_energy_values)
                
                # Only include points that have both time and energy data
                if execution_time > 0 and RAPL > 0:
                    scatter_data.append({
                        'cpu': cpu,
                        'memory': memory,
                        'workers': workers,
                        'execution_time': execution_time,
                        'RAPL': RAPL,
                        'label': f"({cpu}CPU, {memory}MB, {workers}W)"
                    })
    
    except FileNotFoundError:
        print(f"Error: Could not find the file {json_file_path}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the file")
    
    return scatter_data

def create_scatter_plot(scatter_data, output_file='energy_time_scatter.png'):
    """Create a scatter plot of execution time vs energy consumption."""
    if not scatter_data:
        print("No data available for scatter plot")
        return
    
    # Extract data for plotting
    execution_times = [point['execution_time'] for point in scatter_data]
    RAPLs = [point['RAPL'] for point in scatter_data]
    labels = [point['label'] for point in scatter_data]
    
    # Create the scatter plot
    plt.figure(figsize=(12, 8))
    
    # Create scatter plot with different colors for different worker counts
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    worker_counts = list(set([point['workers'] for point in scatter_data]))
    worker_counts.sort()
    
    for i, workers in enumerate(worker_counts):
        worker_data = [point for point in scatter_data if point['workers'] == workers]
        if worker_data:
            x_vals = [point['execution_time'] for point in worker_data]
            y_vals = [point['RAPL'] for point in worker_data]
            color = colors[i % len(colors)]
            
            plt.scatter(x_vals, y_vals, 
                       c=color, 
                       s=100, 
                       alpha=0.7, 
                       label=f'{workers} Workers',
                       edgecolors='black',
                       linewidth=1)
    
    # Add labels to each point
    for point in scatter_data:
        plt.annotate(point['label'], 
                    (point['execution_time'], point['RAPL']),
                    xytext=(5, 5), 
                    textcoords='offset points',
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7),
                    ha='left')
    
    # Customize the plot
    plt.xlabel('Tiempo de Ejecución (segundos)', fontsize=14, fontweight='bold')
    plt.ylabel('Consumo Energético', fontsize=14, fontweight='bold')
    plt.title('Consumo Energético vs Tiempo de Ejecución\n(Stage 1 - ML Workflow)', 
              fontsize=16, fontweight='bold')
    plt.legend(title='Configuración de Workers', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Format y-axis to use scientific notation for large numbers
    plt.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Scatter plot saved as {output_file}")
    
    # Close the plot to free memory
    plt.close()

def print_scatter_data_summary(scatter_data):
    """Print a summary of the scatter plot data."""
    print("Scatter Plot Data Summary:")
    print("=" * 80)
    print(f"{'Setup':<20} {'Execution Time (s)':<18} {'Energy Consumption':<20}")
    print("-" * 80)
    
    for point in sorted(scatter_data, key=lambda x: (x['workers'], x['cpu'], x['memory'])):
        setup = f"({point['cpu']}CPU, {point['memory']}MB, {point['workers']}W)"
        print(f"{setup:<20} {point['execution_time']:<18.2f} {point['RAPL']:<20.2e}")

def main():
    # Path to the stage1.json file
    json_file_path = '/home/users/iarriazu/flexecutor-main/examples/ml/profiling/machine_learning/stage1.json'
    
    try:
        # Load and parse the data
        print("Loading data from stage1.json...")
        scatter_data = load_and_parse_stage1_data(json_file_path)
        
        if not scatter_data:
            print("No valid data found for scatter plot")
            return
        
        # Print data summary
        print_scatter_data_summary(scatter_data)
        
        # Create the scatter plot
        print("\nGenerating scatter plot...")
        create_scatter_plot(scatter_data)
        
        print("\nScatter plot generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

import json
import matplotlib.pyplot as plt
import os
 
# json_path = '/home/users/iarriazu/flexecutor-main/examples/titanic/plot_generation/analysis_results.json'
json_path = '/home/bigrobbin/Desktop/green_computing/flexecutor-main/examples/titanic/plot_generation/analysis_results.json'

# Load the analysis results
with open(json_path) as f:
    data = json.load(f)

# Extract worker counts
workers = [entry['workers'] for entry in data]

# Metrics to plot with their min/max fields
metrics = [
    ('Compute Time (s)', 'min_compute', 'max_compute'),
    ('RAPL Energy (J)', 'min_rapl', 'max_rapl'),
    ('TDP Power (W)', 'min_tdp', 'max_tdp'),
    ('TDP/RAPL Ratio', 
     lambda e: e['min_tdp']/e['min_rapl'] if e['min_rapl'] != 0 else 0,
     lambda e: e['max_tdp']/e['max_rapl'] if e['max_rapl'] != 0 else 0)
]

# Create a figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Min/Max Performance Metrics by Worker Count', fontsize=16)

# Plot each metric
for i, (title, min_field, max_field) in enumerate(metrics):
    ax = axes[i//2, i%2]
    min_vals = [min_field(entry) if callable(min_field) else entry[min_field] for entry in data]
    max_vals = [max_field(entry) if callable(max_field) else entry[max_field] for entry in data]
    
    ax.plot(workers, min_vals, label='Min', marker='o')
    ax.plot(workers, max_vals, label='Max', marker='o')
    ax.set_title(title)
    ax.set_xlabel('Number of Workers')
    ax.set_ylabel(title)
    ax.legend()
    ax.grid(True)

plt.tight_layout()

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'plot_min_max_metrics.png')

plt.savefig(output_path)
print("Plot saved as min_max_metrics.png: " + output_path)

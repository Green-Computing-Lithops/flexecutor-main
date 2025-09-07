#!/usr/bin/env python3
"""
Local Video Profiling Hypothesis 2 Plot Generator

This script generates combined hypothesis 2 plots for local video profiling data,
grouping all worker configurations for each example type, stage, and memory setting
into comprehensive performance variability analysis plots.

Usage:
    python generate_local_hypothesis_2_plots.py

Output:
    Combined hypothesis 2 PNG files showing performance variability across all
    worker configurations for each specific example and memory combination
"""

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
    # Handle the case where data is a single analysis result (not a list of results)
    if isinstance(data, dict) and 'metrics' in data:
        # Single analysis file - create a single data point
        plot_data = {
            'workers': [data['workers']],
            'total_rapl': [data['metrics']['rapl_energy_cores']['total']],
            'total_tdp': [data['metrics']['TDP']['total']],
            'avg_rapl': [data['metrics']['rapl_energy_cores']['mean']],
            'avg_tdp': [data['metrics']['TDP']['mean']],
            'avg_compute': [data['metrics']['compute']['mean']],
            'min_compute': [data['metrics']['compute']['min']],
            'max_compute': [data['metrics']['compute']['max']],
            'min_rapl': [data['metrics']['rapl_energy_cores']['min']],
            'max_rapl': [data['metrics']['rapl_energy_cores']['max']],
            'avg_cold_start': [data['metrics']['cold_start']['mean']],
            'avg_worker_time_execution': [data['metrics']['worker_time_execution']['mean']],
            'avg_psutil_cpu_percent': [data['metrics']['psutil_cpu_percent']['mean']],
            'cpu_architecture': [data['metadata']['cpu_architecture']],
            'local_processing': [True]  # Always True for local processing
        }
    elif isinstance(data, list) and len(data) > 0:
        # Multiple analysis results - extract from each
        if isinstance(data[0], dict) and 'metrics' in data[0]:
            # New format with metrics structure
            plot_data = {
                'workers': [d['workers'] for d in data],
                'total_rapl': [d['metrics']['rapl_energy_cores']['total'] for d in data],
                'total_tdp': [d['metrics']['TDP']['total'] for d in data],
                'avg_rapl': [d['metrics']['rapl_energy_cores']['mean'] for d in data],
                'avg_tdp': [d['metrics']['TDP']['mean'] for d in data],
                'avg_compute': [d['metrics']['compute']['mean'] for d in data],
                'min_compute': [d['metrics']['compute']['min'] for d in data],
                'max_compute': [d['metrics']['compute']['max'] for d in data],
                'min_rapl': [d['metrics']['rapl_energy_cores']['min'] for d in data],
                'max_rapl': [d['metrics']['rapl_energy_cores']['max'] for d in data],
                'avg_cold_start': [d['metrics']['cold_start']['mean'] for d in data],
                'avg_worker_time_execution': [d['metrics']['worker_time_execution']['mean'] for d in data],
                'avg_psutil_cpu_percent': [d['metrics']['psutil_cpu_percent']['mean'] for d in data],
                'cpu_architecture': [d['metadata']['cpu_architecture'] for d in data],
                'local_processing': [True for d in data]  # Always True for local processing
            }
        else:
            # Old format - direct access to fields
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
                'cpu_architecture': [d['cpu_architecture'] for d in data],
                'local_processing': [d.get('local_processing', True) for d in data]
            }
    else:
        # Fallback - empty data
        plot_data = {
            'workers': [],
            'total_rapl': [],
            'total_tdp': [],
            'avg_rapl': [],
            'avg_tdp': [],
            'avg_compute': [],
            'min_compute': [],
            'max_compute': [],
            'min_rapl': [],
            'max_rapl': [],
            'avg_cold_start': [],
            'avg_worker_time_execution': [],
            'avg_psutil_cpu_percent': [],
            'cpu_architecture': [],
            'local_processing': []
        }
    
    # Create unique colors for each worker count
    if plot_data['workers']:
        unique_workers = sorted(list(set(plot_data['workers'])))
        plot_data['worker_colors'] = {worker: list(COLORS.values())[i % len(COLORS)] 
                                     for i, worker in enumerate(unique_workers)}
    else:
        plot_data['worker_colors'] = {}
    
    return plot_data


def create_combined_hypothesis_2_plots(combined_data, output_path, group_key, worker_counts):
    """Create hypothesis 2 plot combining all worker configurations for a specific example and memory setting."""
    # Set up professional styling
    setup_plot_style()
    
    # Create figure with single plot (1x1)
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Extract data from each worker configuration
    all_workers = []
    all_min_compute = []
    all_max_compute = []
    all_avg_compute = []
    all_avg_rapl = []
    all_avg_tdp = []
    cpu_architecture = None
    
    for i, data in enumerate(combined_data):
        plot_data = extract_plot_data(data)
        
        # Since each data point represents one worker configuration, we take the first (and only) value
        if plot_data['workers']:
            all_workers.append(plot_data['workers'][0])
            all_min_compute.append(plot_data['min_compute'][0])
            all_max_compute.append(plot_data['max_compute'][0])
            all_avg_compute.append(plot_data['avg_compute'][0])
            all_avg_rapl.append(plot_data['avg_rapl'][0])
            all_avg_tdp.append(plot_data['avg_tdp'][0])
            
            if cpu_architecture is None and plot_data['cpu_architecture']:
                cpu_architecture = plot_data['cpu_architecture'][0]
    
    # Sort all data by worker count
    sorted_data = sorted(zip(all_workers, all_min_compute, all_max_compute, all_avg_compute, all_avg_rapl, all_avg_tdp))
    if sorted_data:
        all_workers, all_min_compute, all_max_compute, all_avg_compute, all_avg_rapl, all_avg_tdp = zip(*sorted_data)
        all_workers = list(all_workers)
        all_min_compute = list(all_min_compute)
        all_max_compute = list(all_max_compute)
        all_avg_compute = list(all_avg_compute)
        all_avg_rapl = list(all_avg_rapl)
        all_avg_tdp = list(all_avg_tdp)
    
    # Plot Performance Variability (Min/Max Compute Time)
    ax.plot(all_workers, all_min_compute, color=COLORS['accent1'], linewidth=3,
           marker='^', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Minimum Compute Time', alpha=0.9)
    ax.plot(all_workers, all_max_compute, color=COLORS['accent2'], linewidth=3,
           linestyle='--', marker='s', markersize=10, markeredgecolor='black', markeredgewidth=1.5,
           label='Maximum Compute Time', alpha=0.9)
    
    # Add average compute time line for reference
    ax.plot(all_workers, all_avg_compute, color=COLORS['primary'], linewidth=2,
           linestyle=':', marker='o', markersize=8, markeredgecolor='black', markeredgewidth=1,
           label='Average Compute Time', alpha=0.7)
    
    # Fill area between min and max to show variability range
    ax.fill_between(all_workers, all_min_compute, all_max_compute, 
                   color=COLORS['neutral'], alpha=0.2, label='Variability Range')
    
    ax.set_xlabel('Number of Workers', fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
    
    # Create a more descriptive title based on the group key
    title_parts = group_key.split('_')
    if len(title_parts) >= 3:
        example_type = title_parts[0].upper()
        stage = title_parts[1].replace('stage', 'Stage ')
        memory = f"{title_parts[2]}MB"
        title = f'{example_type} {stage} - {memory} Memory: Performance Variability Analysis'
    else:
        title = f'{group_key}: Performance Variability Analysis'
    
    ax.set_title(title, fontweight='bold', pad=20)
    ax.legend(frameon=True, fancybox=True, shadow=True, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(all_workers)
    
    # Add annotations for key data points
    for i, (worker, min_time, max_time, avg_time) in enumerate(zip(
        all_workers, all_min_compute, all_max_compute, all_avg_compute)):
        
        # Calculate variability percentage
        variability = ((max_time - min_time) / avg_time) * 100 if avg_time > 0 else 0
        
        # Add variability annotation for every few points to avoid clutter
        if len(all_workers) <= 8 or i % max(1, len(all_workers) // 4) == 0:
            ax.annotate(f'{variability:.1f}%', 
                       (worker, max_time), 
                       textcoords="offset points", xytext=(0, 15), 
                       ha='center', fontweight='bold', fontsize=9,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    # Add subtitle with processor and configuration information
    subtitle_parts = []
    if cpu_architecture:
        subtitle_parts.append(f'Local Processing on {cpu_architecture} Architecture')
    subtitle_parts.append(f'Worker Range: {min(all_workers)}-{max(all_workers)} workers')
    
    if subtitle_parts:
        plt.figtext(0.5, 0.02, ' | '.join(subtitle_parts), 
                   ha='center', fontsize=11, style='italic')
    
    # Add statistics text box
    if all_avg_compute:
        stats_text = f'Avg Variability: {np.mean([(max_t - min_t) / avg_t * 100 for min_t, max_t, avg_t in zip(all_min_compute, all_max_compute, all_avg_compute) if avg_t > 0]):.1f}%\n'
        stats_text += f'Best Performance: {min(all_avg_compute):.4f}s @ {all_workers[all_avg_compute.index(min(all_avg_compute))]} workers\n'
        stats_text += f'Worst Performance: {max(all_avg_compute):.4f}s @ {all_workers[all_avg_compute.index(max(all_avg_compute))]} workers'
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))
    
    # Adjust layout with professional spacing
    plt.tight_layout(pad=3.0)
    
    # Save with high quality for presentations
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none', format='png')
    plt.close()

def process_local_analysis_folder():
    """Process all local analysis JSON files and generate hypothesis 2 plots grouped by example and memory."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    analysis_folder = os.path.join(script_dir, '100_local_analyze_universal_profiling')
    hypothesis_2_folder = os.path.join(script_dir, '101_local_generate_local_hypothesis_2_plots')
    
    if not os.path.exists(analysis_folder):
        print(f"❌ Error: Analysis folder '{analysis_folder}' does not exist.")
        print("Please run the local analysis script first: python analyze_video_local_profiling.py")
        return
    
    # Create hypothesis 2 output folder
    os.makedirs(hypothesis_2_folder, exist_ok=True)
    
    # Find all JSON analysis files
    analysis_files = []
    for root, dirs, files in os.walk(analysis_folder):
        for file in files:
            if file.endswith('.json') and 'analysis' in file and not file.startswith('universal_') and not file.endswith('_all_configurations_analysis.json'):
                analysis_files.append(os.path.join(root, file))
    
    if not analysis_files:
        print(f"❌ Error: No analysis JSON files found in '{analysis_folder}'")
        return
    
    print(f"✓ Found {len(analysis_files)} local analysis files to process for hypothesis 2")
    print("Grouping by example type, stage, and memory configuration...")
    print()
    
    # Group files by example type, stage, and memory
    grouped_files = {}
    for json_path in analysis_files:
        try:
            # Load data to get configuration info
            data = load_analysis_data(json_path)
            filename = os.path.basename(json_path)
            
            # Parse filename to extract grouping key
            if filename.startswith('video_'):
                # Format: video_stage0_4_512_4_analysis.json
                parts = filename.replace('_analysis.json', '').split('_')
                if len(parts) >= 5:
                    example_type = 'video'
                    stage = parts[1]  # stage0, stage1, etc.
                    memory = parts[3]  # 512, 1024, 2048
                    workers = parts[4]  # 4, 5, 6, etc.
                    
                    # Create grouping key: example_stage_memory
                    group_key = f"{example_type}_{stage}_{memory}"
                    
                    if group_key not in grouped_files:
                        grouped_files[group_key] = []
                    grouped_files[group_key].append((json_path, int(workers), data))
                    
            elif filename.startswith('pi_'):
                # Format: pi_stage_1_512_4_analysis.json
                parts = filename.replace('_analysis.json', '').split('_')
                if len(parts) >= 5:
                    example_type = 'pi'
                    stage = f"{parts[1]}_{parts[2]}"  # stage_1
                    memory = parts[3]  # 512, 1024, 2048
                    workers = parts[4]  # 4, 5, 6, etc.
                    
                    # Create grouping key: example_stage_memory
                    group_key = f"{example_type}_{stage}_{memory}"
                    
                    if group_key not in grouped_files:
                        grouped_files[group_key] = []
                    grouped_files[group_key].append((json_path, int(workers), data))
                    
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(json_path)} for grouping: {str(e)}")
            continue
    
    print(f"✓ Grouped files into {len(grouped_files)} configurations")
    print()
    
    # Process each group
    processed_count = 0
    for group_key, file_data_list in grouped_files.items():
        try:
            # Sort by worker count
            file_data_list.sort(key=lambda x: x[1])
            
            # Combine all data points from this group
            combined_data = []
            worker_counts = []
            
            for json_path, workers, data in file_data_list:
                combined_data.append(data)
                worker_counts.append(workers)
                
            print(f"✓ Processing group '{group_key}' with {len(combined_data)} worker configurations: {worker_counts}")
            
            # Generate output filename
            hypothesis_2_name = f"{group_key}_all_workers_hypothesis_2.png"
            hypothesis_2_path = os.path.join(hypothesis_2_folder, hypothesis_2_name)
            
            # Generate hypothesis 2 plot with combined data
            create_combined_hypothesis_2_plots(combined_data, hypothesis_2_path, group_key, worker_counts)
            print(f"✅ Generated combined hypothesis 2 plot: {hypothesis_2_name}")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing group {group_key}: {str(e)}")
    
    print(f"\n✅ Local hypothesis 2 processing complete!")
    print(f"✅ Generated {processed_count} combined plots in '{hypothesis_2_folder}'")
    print(f"📊 Each plot shows performance variability across all worker configurations for a specific example and memory setting")

def main():
    """Main function."""
    print("🚀 Starting local video profiling hypothesis 2 plot generation...")
    print("=" * 70)
    print("📊 Generating performance variability plots for local video processing")
    print()
    
    process_local_analysis_folder()
    
    print("\n" + "=" * 70)
    print("✅ Local hypothesis 2 plot generation completed successfully!")

if __name__ == "__main__":
    main()

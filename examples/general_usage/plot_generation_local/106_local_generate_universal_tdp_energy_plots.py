#!/usr/bin/env python3
"""
Universal TDP Energy Visualization - Combined Analysis

This script generates comprehensive TDP energy plots for all example types
(Monte Carlo Pi, Video, etc.), showing all worker configurations combined in single plots
for each example type, stage, and memory configuration.

Usage:
    python generate_universal_tdp_energy_plots.py

Output:
    PNG files with comprehensive TDP energy visualization for each configuration
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import glob
import re
import statistics
import seaborn as sns

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Professional color palette for TDP metrics
TDP_COLORS = {
    'tdp_power': '#3498db',           # Professional blue for TDP power
    'tdp_energy': '#e67e22',         # Professional orange for TDP energy
    'tdp_efficiency': '#2ecc71',     # Professional green for efficiency
    'tdp_baseline': '#9b59b6',       # Professional purple for baseline
    'background': '#f8f9fa',         # Light background
    'grid': '#e9ecef'                # Light grid
}

# TDP specifications for Intel i7-10510U
CPU_TDP_SPECS = {
    "base_tdp_watts": 15,      # Base TDP specification
    "max_tdp_watts": 25,       # Maximum TDP specification
    "cpu_name": "Intel(R) Core(TM) i7-10510U CPU @ 1.80GHz"
}

def load_analysis_data(json_path):
    """Load and parse the analysis JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

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
        'legend.fontsize': 11,
        'figure.titlesize': 18,
        'axes.grid': True,
        'grid.alpha': 0.3
    })

def extract_tdp_data(analysis_data, filename):
    """Extract TDP energy data from analysis results."""
    # Parse filename to get configuration details
    pi_match = re.search(r'pi_stage_1_(\d+)_(\d+)_analysis\.json', filename)
    if pi_match:
        example_type = 'pi'
        stage = 'stage1'
        memory = int(pi_match.group(1))
        workers = int(pi_match.group(2))
    else:
        video_match = re.search(r'video_stage(\d+)_4_(\d+)_(\d+)_analysis\.json', filename)
        if video_match:
            example_type = 'video'
            stage = f'stage{video_match.group(1)}'
            memory = int(video_match.group(2))
            workers = int(video_match.group(3))
        else:
            return None
    
    # Handle both old and new JSON structure
    if 'metrics' in analysis_data:
        metrics = analysis_data['metrics']
    else:
        metrics = analysis_data
    
    derived_metrics = analysis_data.get('derived_metrics', {})
    metadata = analysis_data.get('metadata', {})
    
    tdp_data = {
        'example_type': example_type,
        'stage': stage,
        'memory': memory,
        'workers': workers,
        'timestamp': analysis_data.get('analysis_timestamp', ''),
        'cpu_name': metadata.get('cpu_name', 'Unknown CPU'),
        'architecture': metadata.get('cpu_architecture', 'Unknown'),
    }
    
    # Extract TDP power measurements
    if 'TDP' in metrics:
        tdp_data['tdp_power'] = metrics['TDP']
    else:
        tdp_data['tdp_power'] = {'mean': 0, 'min': 0, 'max': 0, 'std_dev': 0, 'count': 0, 'total': 0}
    
    # Extract timing data
    if 'compute' in metrics:
        tdp_data['compute_time'] = metrics['compute']
    else:
        tdp_data['compute_time'] = {'mean': 0, 'min': 0, 'max': 0, 'std_dev': 0}
    
    if 'worker_time_execution' in metrics:
        tdp_data['execution_time'] = metrics['worker_time_execution']
    else:
        tdp_data['execution_time'] = {'mean': 0, 'min': 0, 'max': 0, 'std_dev': 0}
    
    # Calculate TDP-based energy consumption (Energy = Power × Time)
    if tdp_data['tdp_power']['mean'] > 0 and tdp_data['execution_time']['mean'] > 0:
        tdp_data['tdp_energy'] = {
            'mean': tdp_data['tdp_power']['mean'] * tdp_data['execution_time']['mean'],
            'min': tdp_data['tdp_power']['min'] * tdp_data['execution_time']['min'],
            'max': tdp_data['tdp_power']['max'] * tdp_data['execution_time']['max'],
            'std_dev': np.sqrt((tdp_data['tdp_power']['std_dev'] * tdp_data['execution_time']['mean'])**2 + 
                              (tdp_data['tdp_power']['mean'] * tdp_data['execution_time']['std_dev'])**2),
            'count': tdp_data['tdp_power']['count'],
            'total': tdp_data['tdp_power']['total'] * tdp_data['execution_time']['mean']
        }
        
        # Calculate efficiency
        if tdp_data['compute_time']['mean'] > 0:
            tdp_data['efficiency'] = {
                'joules_per_second': tdp_data['tdp_energy']['mean'] / tdp_data['compute_time']['mean'],
                'description': 'TDP energy consumption per second of computation'
            }
        else:
            tdp_data['efficiency'] = {'joules_per_second': 0, 'description': 'N/A'}
    else:
        tdp_data['tdp_energy'] = {'mean': 0, 'min': 0, 'max': 0, 'std_dev': 0, 'count': 0, 'total': 0}
        tdp_data['efficiency'] = {'joules_per_second': 0, 'description': 'N/A'}
    
    return tdp_data

def process_analysis_files(analysis_dir):
    """Process all analysis files and group by example type, stage, and memory configuration."""
    pi_pattern = os.path.join(analysis_dir, 'pi_stage_1_*_*_analysis.json')
    video_pattern = os.path.join(analysis_dir, 'video_stage*_4_*_*_analysis.json')
    
    pi_files = glob.glob(pi_pattern)
    video_files = glob.glob(video_pattern)
    files = pi_files + video_files
    
    if not files:
        return {}
    
    example_groups = {}
    
    for file_path in files:
        filename = os.path.basename(file_path)
        analysis_data = load_analysis_data(file_path)
        
        if analysis_data is None:
            continue
            
        tdp_data = extract_tdp_data(analysis_data, filename)
        if tdp_data is None:
            continue
            
        group_key = f"{tdp_data['example_type']}_{tdp_data['stage']}_{tdp_data['memory']}"
        if group_key not in example_groups:
            example_groups[group_key] = []
        
        example_groups[group_key].append(tdp_data)
    
    # Sort each group by worker count
    for group_key in example_groups:
        example_groups[group_key].sort(key=lambda x: x['workers'])
    
    return example_groups

def create_combined_tdp_energy_plots(example_groups, output_dir):
    """Create combined TDP energy plots for each example type, stage, and memory configuration."""
    setup_plot_style()
    
    generated_plots = []
    
    for group_key, data_list in example_groups.items():
        if not data_list:
            continue
            
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 14))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Extract data for plotting
        workers = [d['workers'] for d in data_list]
        power_means = [d['tdp_power']['mean'] for d in data_list]
        power_stds = [d['tdp_power']['std_dev'] for d in data_list]
        energy_means = [d['tdp_energy']['mean'] for d in data_list]
        energy_stds = [d['tdp_energy']['std_dev'] for d in data_list]
        efficiencies = [d['efficiency']['joules_per_second'] for d in data_list]
        
        # Main plot: TDP Power and Energy vs Workers
        ax1 = fig.add_subplot(gs[0, :])  # Top row, full width
        ax1_twin = ax1.twinx()
        
        x_pos = np.arange(len(workers))
        width = 0.35
        
        # Plot TDP power (left y-axis)
        bars1 = ax1.bar(x_pos - width/2, power_means, width, yerr=power_stds, 
                       capsize=5, color=TDP_COLORS['tdp_power'], 
                       alpha=0.8, label='TDP Power', edgecolor='black', linewidth=0.5)
        
        # Plot TDP energy (right y-axis)
        bars2 = ax1_twin.bar(x_pos + width/2, energy_means, width, yerr=energy_stds, 
                            capsize=5, color=TDP_COLORS['tdp_energy'], 
                            alpha=0.8, label='TDP Energy', edgecolor='black', linewidth=0.5)
        
        # Add value labels
        for bar, mean, std in zip(bars1, power_means, power_stds):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + std + max(power_means) * 0.02,
                    f'{mean:.1f}W', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        for bar, mean, std in zip(bars2, energy_means, energy_stds):
            height = bar.get_height()
            ax1_twin.text(bar.get_x() + bar.get_width()/2., height + std + max(energy_means) * 0.02,
                         f'{mean:.1f}J', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax1.set_xlabel('Number of Workers', fontweight='bold')
        ax1.set_ylabel('TDP Power (Watts)', fontweight='bold', color=TDP_COLORS['tdp_power'])
        ax1_twin.set_ylabel('TDP Energy (Joules)', fontweight='bold', color=TDP_COLORS['tdp_energy'])
        
        # Parse group key to get details
        parts = group_key.split('_')
        example_type = parts[0]
        stage = parts[1]
        memory = int(parts[2])
        
        title_map = {'pi': 'Monte Carlo Pi', 'video': 'Video Processing'}
        example_name = title_map.get(example_type, example_type.title())
        
        ax1.set_title(f'TDP Analysis - {example_name} {stage.title()} (Memory: {memory}MB)', 
                      fontweight='bold', pad=20)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(workers)
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.tick_params(axis='y', labelcolor=TDP_COLORS['tdp_power'])
        ax1_twin.tick_params(axis='y', labelcolor=TDP_COLORS['tdp_energy'])
        
        # Bottom left: Energy Efficiency vs Workers
        ax2 = fig.add_subplot(gs[1, 0])
        
        ax2.plot(workers, efficiencies, marker='o', linewidth=3, markersize=8, 
                color=TDP_COLORS['tdp_efficiency'], markerfacecolor='white', 
                markeredgewidth=2, markeredgecolor=TDP_COLORS['tdp_efficiency'])
        
        # Add value labels
        for i, (w, eff) in enumerate(zip(workers, efficiencies)):
            ax2.text(w, eff + max(efficiencies) * 0.02, f'{eff:.2f}', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax2.set_xlabel('Number of Workers', fontweight='bold')
        ax2.set_ylabel('Energy Efficiency (J/s)', fontweight='bold')
        ax2.set_title('TDP Energy Efficiency Trend', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(workers)
        
        # Bottom right: TDP Baseline Comparison
        ax3 = fig.add_subplot(gs[1, 1])
        
        # Calculate baseline energies for comparison
        sample_data = data_list[0]
        exec_time = sample_data['execution_time']['mean']
        base_energy = CPU_TDP_SPECS['base_tdp_watts'] * exec_time
        max_energy = CPU_TDP_SPECS['max_tdp_watts'] * exec_time
        
        # Create comparison bars
        comparison_data = ['Measured\nTDP Energy', 'Base TDP\nBaseline', 'Max TDP\nBaseline']
        comparison_values = [statistics.mean(energy_means), base_energy, max_energy]
        colors = [TDP_COLORS['tdp_energy'], TDP_COLORS['tdp_baseline'], 'red']
        
        bars = ax3.bar(comparison_data, comparison_values, color=colors, alpha=0.8, 
                      edgecolor='black', linewidth=0.5)
        
        # Add value labels
        for bar, value in zip(bars, comparison_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(comparison_values) * 0.02,
                    f'{value:.1f}J', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax3.set_ylabel('Energy (Joules)', fontweight='bold')
        ax3.set_title('TDP Energy vs Baseline', fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add configuration info
        config_text = f"Memory: {memory}MB | Workers: {min(workers)}-{max(workers)}\n"
        config_text += f"Processor: {sample_data['cpu_name']}\n"
        config_text += f"Architecture: {sample_data['architecture']}\n"
        config_text += f"TDP Spec: {CPU_TDP_SPECS['base_tdp_watts']}-{CPU_TDP_SPECS['max_tdp_watts']}W\n"
        config_text += f"Configurations: {len(data_list)} worker settings"
        
        fig.text(0.02, 0.98, config_text, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
        
        # Add overall title
        fig.suptitle(f'TDP Energy Analysis - {example_name} {stage.title()} (Memory: {memory}MB) - All Worker Configurations', 
                     fontsize=20, fontweight='bold', y=0.96)
        
        # Add timestamp
        if sample_data['timestamp']:
            fig.text(0.99, 0.01, f"Generated: {sample_data['timestamp'][:19]}", 
                    ha='right', va='bottom', fontsize=8, style='italic')
        
        # Save plot
        output_path = os.path.join(output_dir, f'{example_type}_{stage}_{memory}mb_all_workers_tdp_energy.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', format='png')
        plt.close()
        
        generated_plots.append(output_path)
        print(f"✅ Generated combined TDP plot for {example_name} {stage.title()} {memory}MB: {os.path.basename(output_path)}")
    
    return generated_plots

def main():
    """Main function."""
    print("🚀 Starting Universal TDP Energy Combined Visualization...")
    print("=" * 80)
    print("📊 Processing all example configurations (Monte Carlo Pi, Video, etc.)...")
    print()
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    analysis_dir = os.path.join(script_dir, '100_local_analyze_universal_profiling')
    
    # Process all analysis files
    print(f"📁 Scanning analysis files in: {analysis_dir}")
    example_groups = process_analysis_files(analysis_dir)
    
    if not example_groups:
        print("❌ No valid analysis files found!")
        return
    
    print(f"✓ Found {len(example_groups)} example configurations:")
    for group_key, data_list in example_groups.items():
        parts = group_key.split('_')
        example_type = parts[0]
        stage = parts[1]
        memory = int(parts[2])
        title_map = {'pi': 'Monte Carlo Pi', 'video': 'Video Processing'}
        example_name = title_map.get(example_type, example_type.title())
        
        worker_counts = [d['workers'] for d in data_list]
        print(f"  - {example_name} {stage.title()} {memory}MB: {len(data_list)} worker configurations ({min(worker_counts)}-{max(worker_counts)} workers)")
    
    # Create output directory
    output_dir = os.path.join(script_dir, '106_local_generate_universal_tdp_energy_plots')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate combined energy plots
    print(f"\n📊 Generating combined TDP energy plots...")
    energy_plots = create_combined_tdp_energy_plots(example_groups, output_dir)
    
    total_plots = len(energy_plots)
    
    print(f"\n✅ TDP energy visualization complete!")
    print(f"📁 Plots saved in: {output_dir}")
    print(f"📊 Generated {total_plots} combined plots")
    print(f"🔋 Each plot shows TDP energy analysis across all worker configurations")
    
    # Print summary statistics
    print(f"\n📈 Summary by Configuration:")
    for group_key, data_list in example_groups.items():
        parts = group_key.split('_')
        example_type = parts[0]
        stage = parts[1]
        memory = int(parts[2])
        title_map = {'pi': 'Monte Carlo Pi', 'video': 'Video Processing'}
        example_name = title_map.get(example_type, example_type.title())
        
        worker_counts = [d['workers'] for d in data_list]
        avg_power = statistics.mean([d['tdp_power']['mean'] for d in data_list])
        avg_energy = statistics.mean([d['tdp_energy']['mean'] for d in data_list])
        avg_efficiency = statistics.mean([d['efficiency']['joules_per_second'] for d in data_list])
        
        print(f"  {example_name} {stage.title()} {memory}MB ({len(data_list)} configurations, {min(worker_counts)}-{max(worker_counts)} workers):")
        print(f"    Average TDP Power:   {avg_power:.1f}W")
        print(f"    Average TDP Energy:  {avg_energy:.1f}J")
        print(f"    Average Efficiency:  {avg_efficiency:.2f} J/s")

if __name__ == "__main__":
    main()

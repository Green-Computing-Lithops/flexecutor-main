#!/usr/bin/env python3
"""
Universal eBPF Energy Visualization - Combined Analysis

This script generates comprehensive eBPF energy plots for all example types
(Monte Carlo Pi, Video, etc.), showing all worker configurations combined in single plots
for each example type, stage, and memory configuration.

Usage:
    python generate_universal_ebpf_energy_plots.py

Output:
    PNG files with comprehensive eBPF energy visualization for each configuration
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import glob
import re
from matplotlib.patches import Rectangle
import statistics
import seaborn as sns

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Professional color palette for eBPF metrics
EBPF_COLORS = {
    'ebpf_energy_pkg': '#e74c3c',      # Professional red for package
    'ebpf_energy_cores': '#f39c12',    # Professional amber for cores
    'ebpf_energy_total': '#16a085',    # Professional teal for total
    'ebpf_efficiency': '#8e44ad',      # Professional purple for efficiency
    'ebpf_cpu_cycles': '#34495e',      # Professional dark gray for cycles
    'background': '#f8f9fa',           # Light background
    'grid': '#e9ecef'                  # Light grid
}

def load_analysis_data(json_path):
    """Load and parse the analysis JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ Error: Analysis file not found at {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in {json_path}: {e}")
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

def extract_ebpf_data(analysis_data, filename):
    """Extract eBPF energy data from analysis results."""
    # Parse filename to get configuration details
    # Expected formats: 
    # - pi_stage_1_MEMORY_WORKERS_analysis.json
    # - video_stageN_4_MEMORY_WORKERS_analysis.json
    
    # Try Monte Carlo Pi pattern first
    pi_match = re.search(r'pi_stage_1_(\d+)_(\d+)_analysis\.json', filename)
    if pi_match:
        example_type = 'pi'
        stage = 'stage1'
        memory = int(pi_match.group(1))
        workers = int(pi_match.group(2))
    else:
        # Try video pattern
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
    
    ebpf_data = {
        'example_type': example_type,
        'stage': stage,
        'memory': memory,
        'workers': workers,
        'timestamp': analysis_data.get('analysis_timestamp', ''),
        'cpu_name': metadata.get('cpu_name', 'Unknown CPU'),
        'architecture': metadata.get('cpu_architecture', 'Unknown'),
        'ebpf_source': metadata.get('ebpf_source', 'Unknown'),
        'ebpf_available': metadata.get('ebpf_available', False),
    }
    
    # Extract eBPF energy metrics
    ebpf_metrics = ['ebpf_energy_pkg', 'ebpf_energy_cores', 'ebpf_energy_total', 'ebpf_cpu_cycles', 'ebpf_energy_from_cycles']
    for metric in ebpf_metrics:
        if metric in metrics:
            ebpf_data[metric] = metrics[metric]
        else:
            ebpf_data[metric] = {'mean': 0, 'min': 0, 'max': 0, 'std_dev': 0, 'count': 0, 'total': 0}
    
    # Extract efficiency data
    if 'ebpf_energy_efficiency' in derived_metrics:
        ebpf_data['efficiency'] = derived_metrics['ebpf_energy_efficiency']
    else:
        ebpf_data['efficiency'] = {'joules_per_second': 0, 'description': 'N/A'}
    
    # Extract timing data for context
    if 'compute' in metrics:
        ebpf_data['compute_time'] = metrics['compute']
    else:
        ebpf_data['compute_time'] = {'mean': 0, 'min': 0, 'max': 0, 'std_dev': 0}
    
    return ebpf_data

def process_analysis_files(analysis_dir):
    """Process all analysis files and group by example type, stage, and memory configuration."""
    # Get both Monte Carlo Pi and Video analysis files
    pi_pattern = os.path.join(analysis_dir, 'pi_stage_1_*_*_analysis.json')
    video_pattern = os.path.join(analysis_dir, 'video_stage*_4_*_*_analysis.json')
    
    pi_files = glob.glob(pi_pattern)
    video_files = glob.glob(video_pattern)
    files = pi_files + video_files
    
    if not files:
        print(f"❌ No analysis files found in {analysis_dir}")
        return {}
    
    # Group files by example_type_stage_memory
    example_groups = {}
    
    for file_path in files:
        filename = os.path.basename(file_path)
        analysis_data = load_analysis_data(file_path)
        
        if analysis_data is None:
            continue
            
        ebpf_data = extract_ebpf_data(analysis_data, filename)
        if ebpf_data is None:
            continue
            
        # Create group key: example_type_stage_memory
        group_key = f"{ebpf_data['example_type']}_{ebpf_data['stage']}_{ebpf_data['memory']}"
        if group_key not in example_groups:
            example_groups[group_key] = []
        
        example_groups[group_key].append(ebpf_data)
    
    # Sort each group by worker count
    for group_key in example_groups:
        example_groups[group_key].sort(key=lambda x: x['workers'])
    
    return example_groups

def create_combined_ebpf_energy_plots(example_groups, output_dir):
    """Create combined eBPF energy plots for each example type, stage, and memory configuration."""
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
        pkg_means = [d['ebpf_energy_pkg']['mean'] for d in data_list]
        pkg_stds = [d['ebpf_energy_pkg']['std_dev'] for d in data_list]
        cores_means = [d['ebpf_energy_cores']['mean'] for d in data_list]
        cores_stds = [d['ebpf_energy_cores']['std_dev'] for d in data_list]
        total_means = [d['ebpf_energy_total']['mean'] for d in data_list]
        total_stds = [d['ebpf_energy_total']['std_dev'] for d in data_list]
        efficiencies = [d['efficiency']['joules_per_second'] for d in data_list]
        
        # Main plot: eBPF Energy Components vs Workers
        ax1 = fig.add_subplot(gs[0, :])  # Top row, full width
        
        x_pos = np.arange(len(workers))
        width = 0.25
        
        # Create grouped bar plot
        bars1 = ax1.bar(x_pos - width, pkg_means, width, yerr=pkg_stds, 
                       capsize=5, color=EBPF_COLORS['ebpf_energy_pkg'], 
                       alpha=0.8, label='Package Energy', edgecolor='black', linewidth=0.5)
        bars2 = ax1.bar(x_pos, cores_means, width, yerr=cores_stds, 
                       capsize=5, color=EBPF_COLORS['ebpf_energy_cores'], 
                       alpha=0.8, label='Cores Energy', edgecolor='black', linewidth=0.5)
        bars3 = ax1.bar(x_pos + width, total_means, width, yerr=total_stds, 
                       capsize=5, color=EBPF_COLORS['ebpf_energy_total'], 
                       alpha=0.8, label='Total Energy', edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for bars, means, stds in [(bars1, pkg_means, pkg_stds), (bars2, cores_means, cores_stds), (bars3, total_means, total_stds)]:
            for bar, mean, std in zip(bars, means, stds):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + std + max(total_means) * 0.02,
                        f'{mean:.1f}J', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax1.set_xlabel('Number of Workers', fontweight='bold')
        ax1.set_ylabel('Energy Consumption (Joules)', fontweight='bold')
        
        # Parse group key to get details
        parts = group_key.split('_')
        example_type = parts[0]
        stage = parts[1]
        memory = int(parts[2])
        
        title_map = {'pi': 'Monte Carlo Pi', 'video': 'Video Processing'}
        example_name = title_map.get(example_type, example_type.title())
        
        ax1.set_title(f'eBPF Energy Analysis - {example_name} {stage.title()} (Memory: {memory}MB)', 
                      fontweight='bold', pad=20)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(workers)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Bottom left: Energy Efficiency vs Workers
        ax2 = fig.add_subplot(gs[1, 0])
        
        ax2.plot(workers, efficiencies, marker='o', linewidth=3, markersize=8, 
                color=EBPF_COLORS['ebpf_efficiency'], markerfacecolor='white', 
                markeredgewidth=2, markeredgecolor=EBPF_COLORS['ebpf_efficiency'])
        
        # Add value labels
        for i, (w, eff) in enumerate(zip(workers, efficiencies)):
            ax2.text(w, eff + max(efficiencies) * 0.02, f'{eff:.2f}', 
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax2.set_xlabel('Number of Workers', fontweight='bold')
        ax2.set_ylabel('Energy Efficiency (J/s)', fontweight='bold')
        ax2.set_title('Energy Efficiency Trend', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(workers)
        
        # Bottom right: Energy Range Analysis
        ax3 = fig.add_subplot(gs[1, 1])
        
        # Create box plots for energy ranges
        pkg_ranges = [[d['ebpf_energy_pkg']['min'], d['ebpf_energy_pkg']['max']] for d in data_list]
        cores_ranges = [[d['ebpf_energy_cores']['min'], d['ebpf_energy_cores']['max']] for d in data_list]
        total_ranges = [[d['ebpf_energy_total']['min'], d['ebpf_energy_total']['max']] for d in data_list]
        
        # Plot ranges as error bars
        ax3.errorbar(workers, pkg_means, 
                    yerr=[[pkg_means[i] - pkg_ranges[i][0] for i in range(len(workers))],
                          [pkg_ranges[i][1] - pkg_means[i] for i in range(len(workers))]],
                    fmt='o', capsize=5, capthick=2, color=EBPF_COLORS['ebpf_energy_pkg'], 
                    label='Package Range', markersize=6)
        ax3.errorbar(workers, cores_means, 
                    yerr=[[cores_means[i] - cores_ranges[i][0] for i in range(len(workers))],
                          [cores_ranges[i][1] - cores_means[i] for i in range(len(workers))]],
                    fmt='s', capsize=5, capthick=2, color=EBPF_COLORS['ebpf_energy_cores'], 
                    label='Cores Range', markersize=6)
        ax3.errorbar(workers, total_means, 
                    yerr=[[total_means[i] - total_ranges[i][0] for i in range(len(workers))],
                          [total_ranges[i][1] - total_means[i] for i in range(len(workers))]],
                    fmt='^', capsize=5, capthick=2, color=EBPF_COLORS['ebpf_energy_total'], 
                    label='Total Range', markersize=6)
        
        ax3.set_xlabel('Number of Workers', fontweight='bold')
        ax3.set_ylabel('Energy (Joules)', fontweight='bold')
        ax3.set_title('Energy Variability (Min-Max Range)', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks(workers)
        
        # Add configuration info
        sample_data = data_list[0]
        config_text = f"Memory: {memory}MB | Workers: {min(workers)}-{max(workers)}\n"
        config_text += f"Processor: {sample_data['cpu_name']}\n"
        config_text += f"Architecture: {sample_data['architecture']}\n"
        config_text += f"eBPF Source: {sample_data['ebpf_source']}\n"
        config_text += f"Configurations: {len(data_list)} worker settings"
        
        fig.text(0.02, 0.98, config_text, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.8))
        
        # Add overall title
        fig.suptitle(f'eBPF Energy Analysis - {example_name} {stage.title()} (Memory: {memory}MB) - All Worker Configurations', 
                     fontsize=20, fontweight='bold', y=0.96)
        
        # Add timestamp
        if sample_data['timestamp']:
            fig.text(0.99, 0.01, f"Generated: {sample_data['timestamp'][:19]}", 
                    ha='right', va='bottom', fontsize=8, style='italic')
        
        # Save plot
        output_path = os.path.join(output_dir, f'{example_type}_{stage}_{memory}mb_all_workers_ebpf_energy.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', format='png')
        plt.close()
        
        generated_plots.append(output_path)
        print(f"✅ Generated combined eBPF plot for {example_name} {stage.title()} {memory}MB: {os.path.basename(output_path)}")
    
    return generated_plots

def create_combined_ebpf_timeline_plots(example_groups, output_dir):
    """Create combined timeline plots showing energy trends across workers."""
    setup_plot_style()
    
    generated_plots = []
    
    for group_key, data_list in example_groups.items():
        if not data_list:
            continue
            
        # Create timeline plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)
        
        # Extract data
        workers = [d['workers'] for d in data_list]
        pkg_means = [d['ebpf_energy_pkg']['mean'] for d in data_list]
        cores_means = [d['ebpf_energy_cores']['mean'] for d in data_list]
        total_means = [d['ebpf_energy_total']['mean'] for d in data_list]
        efficiencies = [d['efficiency']['joules_per_second'] for d in data_list]
        cpu_cycles = [d['ebpf_cpu_cycles']['mean']/1e9 for d in data_list]  # Convert to billions
        
        # Top plot: Energy components
        ax1.plot(workers, pkg_means, marker='o', linewidth=3, markersize=8, 
                color=EBPF_COLORS['ebpf_energy_pkg'], label='Package Energy', 
                markerfacecolor='white', markeredgewidth=2)
        ax1.plot(workers, cores_means, marker='s', linewidth=3, markersize=8, 
                color=EBPF_COLORS['ebpf_energy_cores'], label='Cores Energy',
                markerfacecolor='white', markeredgewidth=2)
        ax1.plot(workers, total_means, marker='^', linewidth=3, markersize=8, 
                color=EBPF_COLORS['ebpf_energy_total'], label='Total Energy',
                markerfacecolor='white', markeredgewidth=2)
        
        ax1.set_ylabel('Energy Consumption (Joules)', fontweight='bold')
        
        # Parse group key to get details
        parts = group_key.split('_')
        example_type = parts[0]
        stage = parts[1]
        memory = int(parts[2])
        
        title_map = {'pi': 'Monte Carlo Pi', 'video': 'Video Processing'}
        example_name = title_map.get(example_type, example_type.title())
        
        ax1.set_title(f'eBPF Energy Timeline - {example_name} {stage.title()} (Memory: {memory}MB)', fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(workers)
        
        # Bottom plot: Efficiency and CPU cycles
        ax2_twin = ax2.twinx()
        
        line1 = ax2.plot(workers, efficiencies, marker='D', linewidth=3, markersize=8, 
                        color=EBPF_COLORS['ebpf_efficiency'], label='Energy Efficiency (J/s)',
                        markerfacecolor='white', markeredgewidth=2)
        line2 = ax2_twin.plot(workers, cpu_cycles, marker='*', linewidth=3, markersize=10, 
                             color=EBPF_COLORS['ebpf_cpu_cycles'], label='CPU Cycles (Billions)',
                             markerfacecolor='white', markeredgewidth=2)
        
        ax2.set_xlabel('Number of Workers', fontweight='bold')
        ax2.set_ylabel('Energy Efficiency (J/s)', fontweight='bold', color=EBPF_COLORS['ebpf_efficiency'])
        ax2_twin.set_ylabel('CPU Cycles (Billions)', fontweight='bold', color=EBPF_COLORS['ebpf_cpu_cycles'])
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper left')
        
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(workers)
        ax2.tick_params(axis='y', labelcolor=EBPF_COLORS['ebpf_efficiency'])
        ax2_twin.tick_params(axis='y', labelcolor=EBPF_COLORS['ebpf_cpu_cycles'])
        
        # Add configuration info
        sample_data = data_list[0]
        config_text = f"Memory: {memory}MB | Workers: {min(workers)}-{max(workers)} | Configurations: {len(data_list)}\n"
        config_text += f"Processor: {sample_data['cpu_name']} | Architecture: {sample_data['architecture']}\n"
        config_text += f"eBPF Source: {sample_data['ebpf_source']} | Available: {sample_data['ebpf_available']}"
        
        fig.text(0.5, 0.02, config_text, ha='center', fontsize=11, style='italic')
        
        plt.tight_layout()
        
        # Save plot
        output_path = os.path.join(output_dir, f'{example_type}_{stage}_{memory}mb_all_workers_ebpf_timeline.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', format='png')
        plt.close()
        
        generated_plots.append(output_path)
        print(f"✅ Generated combined eBPF timeline for {example_name} {stage.title()} {memory}MB: {os.path.basename(output_path)}")
    
    return generated_plots

def main():
    """Main function."""
    print("🚀 Starting Universal eBPF Energy Combined Visualization...")
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
    output_dir = os.path.join(script_dir, '103_local_generate_universal_ebpf_energy_plots')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate combined energy plots
    print(f"\n📊 Generating combined eBPF energy plots...")
    energy_plots = create_combined_ebpf_energy_plots(example_groups, output_dir)
    
    # Generate combined timeline plots
    print(f"\n📈 Generating combined eBPF timeline plots...")
    timeline_plots = create_combined_ebpf_timeline_plots(example_groups, output_dir)
    
    total_plots = len(energy_plots) + len(timeline_plots)
    
    print(f"\n✅ eBPF energy visualization complete!")
    print(f"📁 Plots saved in: {output_dir}")
    print(f"📊 Generated {total_plots} combined plots ({len(energy_plots)} energy + {len(timeline_plots)} timeline)")
    print(f"🔋 Each plot shows eBPF energy analysis across all worker configurations")
    
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
        avg_pkg = statistics.mean([d['ebpf_energy_pkg']['mean'] for d in data_list])
        avg_cores = statistics.mean([d['ebpf_energy_cores']['mean'] for d in data_list])
        avg_total = statistics.mean([d['ebpf_energy_total']['mean'] for d in data_list])
        avg_efficiency = statistics.mean([d['efficiency']['joules_per_second'] for d in data_list])
        
        print(f"  {example_name} {stage.title()} {memory}MB ({len(data_list)} configurations, {min(worker_counts)}-{max(worker_counts)} workers):")
        print(f"    Average Package Energy: {avg_pkg:.1f}J")
        print(f"    Average Cores Energy:   {avg_cores:.1f}J")
        print(f"    Average Total Energy:   {avg_total:.1f}J")
        print(f"    Average Efficiency:     {avg_efficiency:.2f} J/s")

if __name__ == "__main__":
    main()

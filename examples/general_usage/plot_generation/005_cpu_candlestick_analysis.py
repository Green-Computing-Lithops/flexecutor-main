#!/usr/bin/env python3
"""
CPU Performance Analysis - Simplified
=====================================
Generates a single architecture-memory comparison candlestick plot.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_and_process_data(analysis_dir):
    """Load and process all JSON files into a single DataFrame."""
    json_files = list(Path(analysis_dir).glob("*.json"))
    json_files = [f for f in json_files if f.name != 'enhanced_profiling_analysis.json']
    
    all_data = []
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Parse filename for metadata
            parts = json_file.stem.split('_')
            metadata = {}
            if len(parts) >= 6:
                metadata['example'] = parts[0]  # video, ml, titanic, pi
                metadata['stage'] = parts[1]    # stage0, stage1, stage2, stage3, or just "stage"
                metadata['memory'] = parts[3]
                metadata['architecture'] = parts[4]
            
            # Fix: Extract CPU data from correct structure
            results = data.get('001_analysis_results', data.get('analysis_results', []))
            for result in results:
                # Handle missing CPU data gracefully
                cpu_util = result.get('avg_psutil_cpu_percent', result.get('cpu_utilization', 0))
                all_data.append({
                    'workers': result.get('workers', 0),
                    'cpu_utilization': cpu_util,
                    'example': metadata.get('example', 'unknown'),
                    'stage': metadata.get('stage', 'unknown'),
                    'memory': metadata.get('memory', 'unknown'),
                    'architecture': metadata.get('architecture', 'unknown')
                })
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
    
    return pd.DataFrame(all_data)

def create_individual_cpu_plots(df, output_dir):
    """Create individual CPU plots for each example-stage-architecture-memory combination."""
    # Filter and normalize data
    df_filtered = df[df['architecture'].isin(['arm', 'x86', 'aarch64'])]
    df_filtered['architecture'] = df_filtered['architecture'].replace('aarch64', 'arm')
    df_filtered['memory'] = df_filtered['memory'].str.replace('2048MB', '2048Mb')
    
    examples = sorted(df_filtered['example'].unique())
    stages = sorted(df_filtered['stage'].unique())
    memory_sizes = sorted(df_filtered['memory'].unique())
    architectures = sorted(df_filtered['architecture'].unique())
    
    colors = {'arm': 'lightcoral', 'x86': 'lightblue'}
    
    generated_plots = []
    
    for example in examples:
        for stage in stages:
            for arch in architectures:
                for memory in memory_sizes:
                    # Filter data for this combination
                    subset = df_filtered[(df_filtered['example'] == example) &
                                       (df_filtered['stage'] == stage) &
                                       (df_filtered['architecture'] == arch) & 
                                       (df_filtered['memory'] == memory)]
                    
                    if not subset.empty:
                        # Calculate individual Y-axis limit for this specific graph
                        max_cpu_subset = subset['cpu_utilization'].max()
                        y_limit = max(5, min(100, max_cpu_subset * 1.2))  # Add 20% padding, min 5%, max 100%
                        
                        # Create individual plot
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        # Prepare box plot data
                        worker_groups = subset.groupby('workers')['cpu_utilization']
                        box_data = [cpu_values.values for workers, cpu_values in worker_groups]
                        worker_labels = [f'{workers}' for workers, cpu_values in worker_groups]
                        
                        if box_data:
                            ax.boxplot(box_data, labels=worker_labels, patch_artist=True,
                                      showmeans=True, meanline=True, showfliers=True,
                                      flierprops=dict(marker='o', markerfacecolor='red', markersize=5, alpha=0.7),
                                      medianprops=dict(color='black', linewidth=2),
                                      meanprops=dict(color='blue', linewidth=2, linestyle='--'),
                                      boxprops=dict(facecolor=colors.get(arch, 'lightgray'), alpha=0.7),
                                      whiskerprops=dict(color='black', linewidth=1.5),
                                      capprops=dict(color='black', linewidth=1.5))
                            
                            # Add mean statistics
                            stats = [f'W{workers}: μ={cpu_values.mean():.1f}%' 
                                    for workers, cpu_values in worker_groups]
                            ax.text(0.02, 0.98, '\n'.join(stats), transform=ax.transAxes,
                                   verticalalignment='top', fontsize=10, fontfamily='monospace',
                                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                        
                        # Customize plot
                        stage_display = stage.replace('stage', 'Stage ') if stage != 'stage' else 'Single Stage'
                        ax.set_title(f'CPU Utilization Distribution - {example.upper()} - {stage_display}\n{arch.upper()} Architecture - {memory} Memory', 
                                    fontsize=14, fontweight='bold')
                        ax.set_xlabel('Number of Workers', fontsize=12, fontweight='bold')
                        ax.set_ylabel('CPU Utilization (%)', fontsize=12, fontweight='bold')
                        ax.grid(True, alpha=0.3, axis='y')
                        ax.set_ylim(0, y_limit)
                        
                        # Add legend outside the plot area
                        legend_elements = [
                            plt.Line2D([0], [0], color='black', linewidth=2, label='Median'),
                            plt.Line2D([0], [0], color='blue', linewidth=2, linestyle='--', label='Mean'),
                            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=5, label='Outliers')
                        ]
                        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
                        
                        plt.tight_layout()
                        
                        # Save plot
                        filename = f'cpu_{example}_{stage}_{arch}_{memory}_performance.png'
                        output_path = output_dir / filename
                        plt.savefig(output_path, dpi=300, bbox_inches='tight')
                        plt.close()
                        
                        generated_plots.append(output_path)
                        print(f"Generated: {filename}")
    
    return generated_plots

def main():
    """Main function."""
    # Fix: Use correct relative path
    analysis_dir = "001_analysis_results"
    output_dir = Path("005_cpu_candlestick_analysis")
    output_dir.mkdir(exist_ok=True)
    
    # Load data and create individual plots
    df = load_and_process_data(analysis_dir)
    if not df.empty:
        generated_plots = create_individual_cpu_plots(df, output_dir)
        print(f"CPU analysis complete! Generated {len(generated_plots)} individual plots.")
    else:
        print("No data found!")

if __name__ == "__main__":
    main()

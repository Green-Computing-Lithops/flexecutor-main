#!/usr/bin/env python3
"""
Cost-Time-Energy Scatter Plot Generator
=======================================

This script generates scatter plots showing the relationship between:
- Y-axis: Cost in AWS (moneywise)
- X-axis: Time of execution  
- Bubble size: Total energy in TDP

For each JSON analysis file in the 001_analyze_all_profiling_enhanced directory.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import seaborn as sns
from typing import Dict, List

class CostTimeEnergyScatterPlotGenerator:
    def __init__(self, analysis_dir: str, output_dir: str):
        self.analysis_dir = Path(analysis_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_json_files(self):
        """Load all JSON analysis files from the directory."""
        json_files = list(self.analysis_dir.glob("*.json"))
        print(f"Found {len(json_files)} JSON files")
        return json_files
    
    def parse_filename(self, filename: str) -> Dict:
        """Parse metadata from filename."""
        parts = filename.stem.split('_')
        metadata = {}
        
        if len(parts) >= 6:
            metadata['example'] = parts[0]  # ml, video, titanic, pi
            metadata['stage'] = parts[1]    # stage0, stage1, etc.
            metadata['platform'] = parts[2] # aws
            metadata['memory'] = parts[3]   # 512Mb, 1024Mb, 2048Mb
            metadata['architecture'] = parts[4]  # arm, x86
        
        return metadata
    
    def generate_scatter_plot(self, json_path: Path):
        """Generate scatter plot for a single JSON file."""
        try:
            # Load JSON data
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Extract analysis results - Fix: Use correct key name
            analysis_results = data.get('analysis_results', [])
            if not analysis_results:
                print(f"No analysis results found in {json_path.name}")
                return None
            
            # Extract metadata
            metadata = data.get('metadata', {})
            filename_metadata = self.parse_filename(json_path)
            metadata.update(filename_metadata)
            
            # Prepare data for plotting
            plot_data = []
            for result in analysis_results:
                plot_data.append({
                    'workers': result.get('workers', 0),
                    'cost': result.get('cost_aws_moneywise', 0),
                    'time': result.get('avg_worker_time_execution', 0),
                    'energy': result.get('total_tdp', 0)
                })
            
            df = pd.DataFrame(plot_data)
            
            if df.empty:
                print(f"No valid data found in {json_path.name}")
                return None
            
            # Create scatter plot
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Scale bubble sizes for better visualization
            max_energy = df['energy'].max()
            min_energy = df['energy'].min()
            bubble_sizes = 100 + 900 * (df['energy'] - min_energy) / (max_energy - min_energy) if max_energy > min_energy else 500
            
            # Create scatter plot with different colors for each worker count
            unique_workers = sorted(df['workers'].unique())
            colors = plt.cm.Set3(np.linspace(0, 1, len(unique_workers)))
            worker_color_map = {worker: color for worker, color in zip(unique_workers, colors)}
            
            # Plot each worker count with different color
            for worker in unique_workers:
                worker_data = df[df['workers'] == worker]
                worker_bubble_sizes = 100 + 900 * (worker_data['energy'] - min_energy) / (max_energy - min_energy) if max_energy > min_energy else 500
                
                ax.scatter(
                    worker_data['time'], 
                    worker_data['cost'],
                    s=worker_bubble_sizes,
                    alpha=0.7,
                    color=worker_color_map[worker],
                    edgecolors='black',
                    linewidth=0.5,
                    label=f'{worker} workers'
                )
            
            # Customize the plot
            example = metadata.get('example', 'unknown').upper()
            stage = metadata.get('stage', 'unknown').upper()
            memory = metadata.get('memory', 'unknown')
            arch = metadata.get('architecture', 'unknown').upper()
            
            ax.set_xlabel('Execution Time (seconds)', fontsize=14, fontweight='bold')
            ax.set_ylabel('AWS Cost (USD per 1000 executions)', fontsize=14, fontweight='bold')
            ax.set_title(f'Cost vs Time vs Energy - {example} {stage} {memory} {arch}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add grid
            ax.grid(True, alpha=0.3)
            
            # Add legend for worker counts (top right corner of the graph)
            legend = ax.legend(title='Number of Workers', 
                              loc='upper right',
                              frameon=True, fancybox=True, shadow=True,
                              handlelength=1, handletextpad=0.5)
            
            # Make all legend markers the same size
            for handle in legend.legend_handles:
                handle.set_sizes([100])  # Consistent size for all legend markers
            
            # Add energy value annotations on each dot
            for i, row in df.iterrows():
                ax.annotate(f"{row['energy']:.0f} J", 
                           (row['time'], row['cost']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, fontweight='bold', alpha=0.8)
            
            plt.tight_layout()
            
            # Save the plot
            filename = f"{metadata.get('example', 'unknown')}_{metadata.get('stage', 'unknown')}_{metadata.get('memory', 'unknown')}_{metadata.get('architecture', 'unknown')}_cost_time_energy_scatter.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Generated: {filename}")
            return filepath
            
        except Exception as e:
            print(f"Error processing {json_path.name}: {e}")
            return None
    
    def generate_all_plots(self):
        """Generate scatter plots for all JSON files."""
        json_files = self.load_json_files()
        
        generated_count = 0
        for json_file in json_files:
            if json_file.name == 'enhanced_profiling_analysis.json':
                continue  # Skip the enhanced analysis file
            
            result = self.generate_scatter_plot(json_file)
            if result:
                generated_count += 1
        
        print(f"\nGenerated {generated_count} scatter plots in {self.output_dir}")
    
    def create_summary_comparison_plot(self):
        """Create a summary comparison plot showing all architectures together."""
        json_files = self.load_json_files()
        
        all_data = []
        for json_file in json_files:
            if json_file.name == 'enhanced_profiling_analysis.json':
                continue
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                analysis_results = data.get('analysis_results', [])
                metadata = data.get('metadata', {})
                filename_metadata = self.parse_filename(json_file)
                metadata.update(filename_metadata)
                
                for result in analysis_results:
                    all_data.append({
                        'example': metadata.get('example', 'unknown'),
                        'stage': metadata.get('stage', 'unknown'),
                        'memory': metadata.get('memory', 'unknown'),
                        'architecture': metadata.get('architecture', 'unknown'),
                        'workers': result.get('workers', 0),
                        'cost': result.get('cost_aws_moneywise', 0),
                        'time': result.get('avg_worker_time_execution', 0),
                        'energy': result.get('total_tdp', 0)
                    })
                    
            except Exception as e:
                print(f"Error reading {json_file.name}: {e}")
                continue
        
        if not all_data:
            print("No data found for summary plot")
            return
        
        df = pd.DataFrame(all_data)
        
        # Create summary plot
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Color mapping for architectures
        arch_colors = {'arm': '#ff7f0e', 'x86': '#1f77b4'}
        
        # Plot each architecture
        for arch, color in arch_colors.items():
            arch_data = df[df['architecture'] == arch]
            if not arch_data.empty:
                # Scale bubble sizes
                max_energy = arch_data['energy'].max()
                min_energy = arch_data['energy'].min()
                bubble_sizes = 100 + 900 * (arch_data['energy'] - min_energy) / (max_energy - min_energy) if max_energy > min_energy else 500
                
                scatter = ax.scatter(
                    arch_data['time'],
                    arch_data['cost'],
                    s=bubble_sizes,
                    alpha=0.6,
                    color=color,
                    edgecolors='black',
                    linewidth=0.5,
                    label=f'{arch.upper()} Architecture'
                )
        
        ax.set_xlabel('Execution Time (seconds)', fontsize=14, fontweight='bold')
        ax.set_ylabel('AWS Cost (USD per 1000 executions)', fontsize=14, fontweight='bold')
        ax.set_title('Cost vs Time vs Energy - All Architectures Comparison', 
                    fontsize=16, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3)
        ax.legend(frameon=True, fancybox=True, shadow=True)
        
        plt.tight_layout()
        
        # Save summary plot
        summary_path = self.output_dir / 'all_architectures_cost_time_energy_comparison.png'
        plt.savefig(summary_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Generated summary comparison: {summary_path.name}")

def main():
    """Main function to run the scatter plot generation."""
    analysis_dir = Path("001_analysis_results")
    # Fix: Use consistent output directory naming
    output_dir = Path("004_cost_time_energy_scatter_plots")
    
    if not analysis_dir.exists():
        print(f"Analysis directory not found: {analysis_dir}")
        return
    
    # Initialize generator
    generator = CostTimeEnergyScatterPlotGenerator(analysis_dir, output_dir)
    
    print("Starting Cost-Time-Energy Scatter Plot Generation...")
    print("=" * 60)
    
    # Generate individual plots
    generator.generate_all_plots()
    
    # Generate summary comparison plot
    print("\n" + "=" * 60)
    print("Generating summary comparison plot...")
    generator.create_summary_comparison_plot()
    
    print("\n" + "=" * 60)
    print("Scatter plot generation complete!")
    print(f"All plots saved to: {output_dir}")

if __name__ == "__main__":
    main()

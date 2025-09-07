#!/usr/bin/env python3
"""
Universal Multistage Stacked Graph Generator
===========================================

This script generates stacked graphs showing total energy consumption by stages
for universal examples (Video and Pi) across different memory configurations,
using the universal profiling analysis JSON files as the data source.

Features:
- Y-axis: Total energy stacked by stages
- X-axis: Number of workers
- One image with graphs for each memory configuration (512MB, 1024MB, 2048MB)
- Supports Video (multistage) and Pi (single stage) examples
- Uses universal profiling analysis data with comprehensive energy metrics
- Supports multiple energy measurement methods (RAPL, eBPF, Perf, TDP)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
import glob
import re

class UniversalMultistageStackedGraphGenerator:
    def __init__(self, local_dir: str):
        self.local_dir = Path(local_dir)
        self.analysis_dir = self.local_dir / "100_local_analyze_universal_profiling"
        self.data = {}
        self.memory_configs = ["512", "1024", "2048"]  # Memory in MB (without Mb suffix)
        # Examples available in universal profiling data
        self.examples = ["video", "pi"]
        # Video has multiple stages, Pi has single stage
        self.stage_mapping = {
            "video": ["stage0", "stage1", "stage2", "stage3"],
            "pi": ["stage"]
        }
        # Energy metrics to use (in order of preference)
        self.energy_metrics = ["rapl_energy_cores", "ebpf_energy_cores", "perf_energy_cores", "TDP"]
        
    def load_data(self):
        """Load data from the universal profiling analysis JSON files."""
        print("Loading data from universal profiling analysis JSON files...")
        
        # Find all analysis JSON files
        json_files = list(self.analysis_dir.glob("*_analysis.json"))
        # Filter out combined analysis files
        json_files = [f for f in json_files if not f.name.endswith("_all_configurations_analysis.json")]
        print(f"Found {len(json_files)} individual analysis files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Extract metadata from the analysis data
                example_type = data.get('example_type')
                stage = data.get('stage')
                memory = data.get('memory')  # This is in MB as integer
                workers = data.get('workers')
                
                if not all([example_type, stage, memory, workers]):
                    print(f"Skipping {json_file.name}: missing metadata")
                    continue
                
                # Convert memory to string for consistency
                memory_str = str(memory)
                
                # Store data with hierarchical key
                key = (example_type, stage, memory_str, workers)
                self.data[key] = data
                
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")
        
        print(f"Loaded data for {len(self.data)} configurations")
        
    def _get_best_energy_metric(self, analysis_data: dict) -> Tuple[str, float]:
        """Get the best available energy metric from the analysis data."""
        metrics = analysis_data.get('metrics', {})
        
        # Try each energy metric in order of preference
        for metric in self.energy_metrics:
            if metric in metrics:
                energy_value = metrics[metric].get('mean', 0)
                if energy_value > 0:  # Only use non-zero values
                    return metric, energy_value
        
        # If no energy metric found, return default
        return "unknown", 0.0
        
    def _aggregate_energy_data(self, example: str, memory: str) -> Dict[int, Dict[str, Tuple[float, str]]]:
        """Aggregate energy data for a specific configuration."""
        stages = self.stage_mapping.get(example, [])
        worker_stage_energy = {}
        
        for stage in stages:
            # Find all configurations for this example, stage, and memory
            matching_keys = [key for key in self.data.keys() 
                           if key[0] == example and key[1] == stage and key[2] == memory]
            
            for key in matching_keys:
                example_type, stage_name, memory_config, workers = key
                analysis_data = self.data[key]
                
                # Get the best available energy metric
                metric_name, energy_value = self._get_best_energy_metric(analysis_data)
                
                if workers not in worker_stage_energy:
                    worker_stage_energy[workers] = {}
                
                # Store both energy value and metric name for reference
                worker_stage_energy[workers][stage] = (energy_value, metric_name)
        
        return worker_stage_energy
    
    def generate_stacked_graphs(self):
        """Generate stacked graphs for all examples."""
        if not self.data:
            print("No data loaded. Please run load_data() first.")
            return
            
        # Create output directory
        output_dir = self.local_dir / "107_local_multistage_stacked_graphs_universal"
        output_dir.mkdir(exist_ok=True)
        
        # Generate graphs for each example
        for example in self.examples:
            self._create_example_graph(example, output_dir)
            
        print(f"Graphs saved to: {output_dir}")
    
    def _create_example_graph(self, example: str, output_dir: Path):
        """Create one image with 3 graphs for a specific example (one per memory config)."""
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle(f'Energy Consumption by Stages - {example.upper()} Example (Universal Profiling)', 
                     fontsize=16, fontweight='bold')
        
        # First pass: find maximum energy value across all subplots for consistent scaling
        max_energy = 0
        all_worker_stage_energy = {}
        
        for mem_idx, memory in enumerate(self.memory_configs):
            worker_stage_energy = self._aggregate_energy_data(example, memory)
            all_worker_stage_energy[memory] = worker_stage_energy
            
            if worker_stage_energy:
                # Find maximum total energy for this configuration
                for workers, stage_data in worker_stage_energy.items():
                    total_energy = sum(energy_info[0] for energy_info in stage_data.values())
                    max_energy = max(max_energy, total_energy)
        
        # Add some padding to the maximum value
        max_energy *= 1.1 if max_energy > 0 else 1000
        
        # Second pass: create plots with consistent Y-axis scale
        for mem_idx, memory in enumerate(self.memory_configs):
            ax = axes[mem_idx]
            worker_stage_energy = all_worker_stage_energy.get(memory, {})
            
            if not worker_stage_energy:
                ax.text(0.5, 0.5, f'No data available\nfor {example.upper()}\n{memory}MB', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{example.upper()} - {memory}MB')
                ax.set_ylim(0, max_energy)
                continue
            
            # Prepare data for stacking - only use workers that have data
            workers_list = sorted(worker_stage_energy.keys())
            
            # Determine which stages are present in the data
            all_stages_in_data = set()
            for worker_data in worker_stage_energy.values():
                all_stages_in_data.update(worker_data.keys())
            
            # Use only stages that exist in the data
            available_stages = [stage for stage in self.stage_mapping.get(example, []) 
                              if stage in all_stages_in_data]
            
            if not available_stages:
                ax.text(0.5, 0.5, f'No stage data available\nfor {example.upper()}\n{memory}MB', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{example.upper()} - {memory}MB')
                ax.set_ylim(0, max_energy)
                continue
            
            # Define colors for stages
            stage_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA07A']
            
            # Create arrays for each stage
            stage_arrays = {}
            energy_metrics_used = set()
            for stage in available_stages:
                stage_arrays[stage] = []
                for workers in workers_list:
                    if workers in worker_stage_energy and stage in worker_stage_energy[workers]:
                        energy_value, metric_name = worker_stage_energy[workers][stage]
                        stage_arrays[stage].append(energy_value)
                        energy_metrics_used.add(metric_name)
                    else:
                        stage_arrays[stage].append(0)
            
            # Create stacked bar chart using continuous positions (0, 1, 2, ...)
            x_positions = list(range(len(workers_list)))
            bottom = np.zeros(len(workers_list))
            bars = []
            
            for i, stage in enumerate(available_stages):
                color_idx = i % len(stage_colors)
                bar = ax.bar(x_positions, stage_arrays[stage], bottom=bottom, 
                           label=stage.capitalize(), color=stage_colors[color_idx], alpha=0.8, width=0.8)
                bars.append(bar)
                bottom += np.array(stage_arrays[stage])
            
            # Customize the plot with consistent Y-axis scale
            title = f'{example.upper()} - {memory}MB'
            if energy_metrics_used:
                metrics_str = ', '.join(sorted(energy_metrics_used))
                title += f'\n({metrics_str})'
            ax.set_title(title, fontweight='bold')
            ax.set_xlabel('Number of Workers')
            ax.set_ylabel('Energy Consumption (Joules)')
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, max_energy)  # Set consistent Y-axis scale
            
            # Set x-axis ticks and labels for the actual worker counts
            ax.set_xticks(x_positions)
            ax.set_xticklabels([str(w) for w in workers_list])
            
            # Add value labels on bars
            self._add_value_labels(ax, x_positions, bottom)
        
        plt.tight_layout()
        
        # Save the graph
        filename = f"multistage_energy_stacked_universal_{example}.png"
        filepath = output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Generated: {filename}")
    
    def _add_value_labels(self, ax, x_positions, totals):
        """Add total value labels on top of stacked bars."""
        for i, (x_pos, total) in enumerate(zip(x_positions, totals)):
            if total > 0:
                ax.text(x_pos, total + total * 0.02, f'{total:.0f}J', 
                       ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    def generate_summary_report(self):
        """Generate a summary report of the universal profiling data."""
        if not self.data:
            print("No data loaded. Please run load_data() first.")
            return
            
        print("\n" + "="*60)
        print("UNIVERSAL MULTISTAGE ENERGY ANALYSIS SUMMARY")
        print("="*60)
        
        for example in self.examples:
            print(f"\n{example.upper()} Example:")
            print("-" * 20)
            
            for memory in self.memory_configs:
                worker_stage_energy = self._aggregate_energy_data(example, memory)
                
                if worker_stage_energy:
                    workers_count = len(worker_stage_energy)
                    
                    # Calculate average energy per stage
                    stage_averages = {}
                    energy_metrics_used = set()
                    all_stages_in_data = set()
                    for worker_data in worker_stage_energy.values():
                        all_stages_in_data.update(worker_data.keys())
                    
                    for stage in all_stages_in_data:
                        energies = []
                        for worker_data in worker_stage_energy.values():
                            if stage in worker_data:
                                energy_value, metric_name = worker_data[stage]
                                energies.append(energy_value)
                                energy_metrics_used.add(metric_name)
                        if energies:
                            stage_averages[stage] = np.mean(energies)
                    
                    metrics_str = ', '.join(sorted(energy_metrics_used))
                    print(f"  {memory}MB: {workers_count} worker configs ({metrics_str})")
                    for stage, avg_energy in stage_averages.items():
                        print(f"    {stage}: {avg_energy:.0f}J average")
    
    def generate_comparison_graph(self):
        """Generate a comparison graph showing all examples and memory configs."""
        if not self.data:
            print("No data loaded. Please run load_data() first.")
            return
            
        # Create output directory
        output_dir = self.local_dir / "107_local_multistage_stacked_graphs_universal"
        output_dir.mkdir(exist_ok=True)
        
        # Create a large comparison plot
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Universal Energy Consumption Comparison - All Examples and Memory Configurations', 
                     fontsize=16, fontweight='bold')
        
        # Flatten axes for easier indexing
        axes_flat = axes.flatten()
        plot_idx = 0
        
        # Find global max energy for consistent scaling
        global_max_energy = 0
        for example in self.examples:
            for memory in self.memory_configs:
                worker_stage_energy = self._aggregate_energy_data(example, memory)
                if worker_stage_energy:
                    for workers, stage_data in worker_stage_energy.items():
                        total_energy = sum(energy_info[0] for energy_info in stage_data.values())
                        global_max_energy = max(global_max_energy, total_energy)
        
        global_max_energy *= 1.1 if global_max_energy > 0 else 1000
        
        # Create plots
        for example in self.examples:
            for memory in self.memory_configs:
                if plot_idx >= len(axes_flat):
                    break
                    
                ax = axes_flat[plot_idx]
                worker_stage_energy = self._aggregate_energy_data(example, memory)
                
                if not worker_stage_energy:
                    ax.text(0.5, 0.5, f'No data\n{example.upper()}\n{memory}MB', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=10)
                    ax.set_title(f'{example.upper()} - {memory}MB')
                    ax.set_ylim(0, global_max_energy)
                    plot_idx += 1
                    continue
                
                # Prepare data for stacking
                workers_list = sorted(worker_stage_energy.keys())
                available_stages = [stage for stage in self.stage_mapping.get(example, []) 
                                  if any(stage in worker_data for worker_data in worker_stage_energy.values())]
                
                if not available_stages:
                    ax.text(0.5, 0.5, f'No stage data\n{example.upper()}\n{memory}MB', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=10)
                    ax.set_title(f'{example.upper()} - {memory}MB')
                    ax.set_ylim(0, global_max_energy)
                    plot_idx += 1
                    continue
                
                # Define colors for stages
                stage_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA07A']
                
                # Create arrays for each stage
                stage_arrays = {}
                energy_metrics_used = set()
                for stage in available_stages:
                    stage_arrays[stage] = []
                    for workers in workers_list:
                        if workers in worker_stage_energy and stage in worker_stage_energy[workers]:
                            energy_value, metric_name = worker_stage_energy[workers][stage]
                            stage_arrays[stage].append(energy_value)
                            energy_metrics_used.add(metric_name)
                        else:
                            stage_arrays[stage].append(0)
                
                # Create stacked bar chart
                x_positions = list(range(len(workers_list)))
                bottom = np.zeros(len(workers_list))
                
                for i, stage in enumerate(available_stages):
                    color_idx = i % len(stage_colors)
                    ax.bar(x_positions, stage_arrays[stage], bottom=bottom, 
                          label=stage.capitalize(), color=stage_colors[color_idx], alpha=0.8, width=0.8)
                    bottom += np.array(stage_arrays[stage])
                
                # Customize the plot
                title = f'{example.upper()} - {memory}MB'
                if energy_metrics_used:
                    metrics_str = ', '.join(sorted(energy_metrics_used))
                    title += f'\n({metrics_str})'
                ax.set_title(title, fontweight='bold', fontsize=10)
                ax.set_xlabel('Workers')
                ax.set_ylabel('Energy (J)')
                ax.legend(loc='upper left', fontsize=8)
                ax.grid(True, alpha=0.3)
                ax.set_ylim(0, global_max_energy)
                
                # Set x-axis ticks
                ax.set_xticks(x_positions[::2])  # Show every other tick to avoid crowding
                ax.set_xticklabels([str(workers_list[i]) for i in range(0, len(workers_list), 2)])
                
                plot_idx += 1
        
        # Hide unused subplots
        for i in range(plot_idx, len(axes_flat)):
            axes_flat[i].set_visible(False)
        
        plt.tight_layout()
        
        # Save the comparison graph
        filename = "multistage_energy_stacked_universal_comparison.png"
        filepath = output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Generated comparison: {filename}")
    
    def run_analysis(self):
        """Run the complete analysis."""
        print("Starting Universal Multistage Stacked Graph Analysis...")
        print("Processing examples: video (multistage), pi (single stage)")
        print("Using universal profiling analysis data with multiple energy metrics")
        self.load_data()
        self.generate_stacked_graphs()
        self.generate_comparison_graph()
        self.generate_summary_report()
        print("\nUniversal analysis complete!")

def main():
    """Main function to run the analysis."""
    # Path to the local directory
    local_dir = Path(__file__).parent
    
    if not (local_dir / "100_local_analyze_universal_profiling").exists():
        print(f"Error: 100_local_analyze_universal_profiling directory not found at {local_dir}")
        return
    
    # Initialize the generator
    generator = UniversalMultistageStackedGraphGenerator(str(local_dir))
    
    # Run the complete analysis
    generator.run_analysis()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Multistage Stacked Graph Generator for FlexExecutor (CSV Version)
================================================================

This script generates stacked graphs showing total energy consumption by stages
for all examples (ML, Video, Pi, and Titanic) across different memory 
configurations, using the execution_summary.csv file as the data source.

Features:
- Y-axis: Total energy stacked by stages
- X-axis: Number of workers
- One image with 2 graphs per example (ARM and x86 architectures)
- Supports ML, Video, Pi, and Titanic examples
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List

class MultistageStackedGraphGeneratorCSV:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.data = None
        self.memory_configs = ["2048", "1024", "512"]
        self.architectures = ["ARM", "x86"]
        # All examples including ml and video
        self.examples = ["ml", "video", "pi", "titanic"]
        self.stages = ["stage0", "stage1", "stage2", "stage3", "stage"]  # Include "stage" for single-stage examples
        
    def load_data(self):
        """Load data from the CSV file."""
        print("Loading data from CSV...")
        self.data = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.data)} rows of data")
        
    def _aggregate_energy_data(self, example: str, memory: str, architecture: str) -> Dict[int, Dict[str, float]]:
        """Aggregate energy data for a specific configuration."""
        if self.data is None:
            return {}
            
        # Filter data for the specific configuration
        filtered_data = self.data[
            (self.data['Example'] == example) &
            (self.data['Memory_MB'] == int(memory)) &
            (self.data['Architecture'] == architecture.lower())
        ]
        
        # If no data found, try with uppercase architecture
        if filtered_data.empty:
            filtered_data = self.data[
                (self.data['Example'] == example) &
                (self.data['Memory_MB'] == int(memory)) &
                (self.data['Architecture'] == architecture)
            ]
        
        # Group by workers and stage, calculate average energy
        grouped = filtered_data.groupby(['Workers', 'Stage'])['Energy_J'].mean().reset_index()
        
        # Convert to the required format
        worker_stage_energy = {}
        for _, row in grouped.iterrows():
            workers = row['Workers']
            stage = row['Stage']
            energy = row['Energy_J']
            
            if workers not in worker_stage_energy:
                worker_stage_energy[workers] = {}
            worker_stage_energy[workers][stage] = energy
            
        return worker_stage_energy
    
    def generate_stacked_graphs(self):
        """Generate stacked graphs for all examples split by memory configuration."""
        if self.data is None:
            print("No data loaded. Please run load_data() first.")
            return
            
        # Create output directory
        output_dir = self.csv_path.parent / "014_multistage_stacked_graphs_csv"
        output_dir.mkdir(exist_ok=True)
        
        # Generate graphs for each example and memory configuration
        for example in self.examples:
            for memory in self.memory_configs:
                self._create_example_memory_graph(example, memory, output_dir)
            
        print(f"Graphs saved to: {output_dir}")
    
    def _create_example_memory_graph(self, example: str, memory: str, output_dir: Path):
        """Create one image with 2 graphs for a specific example and memory configuration."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'Energy Consumption by Stages - {example.upper()} Example ({memory}MB Memory)', fontsize=16, fontweight='bold')
        
        # First pass: find maximum energy value across all subplots for consistent scaling
        max_energy = 0
        all_worker_stage_energy = {}
        
        for arch_idx, architecture in enumerate(self.architectures):
            worker_stage_energy = self._aggregate_energy_data(example, memory, architecture)
            all_worker_stage_energy[architecture] = worker_stage_energy
            
            if worker_stage_energy:
                # Find maximum total energy for this configuration
                for workers, stage_data in worker_stage_energy.items():
                    total_energy = sum(stage_data.values())
                    max_energy = max(max_energy, total_energy)
        
        # Add some padding to the maximum value
        max_energy *= 1.1 if max_energy > 0 else 1000
        
        # Second pass: create plots with consistent Y-axis scale
        for arch_idx, architecture in enumerate(self.architectures):
            ax = axes[arch_idx]
            worker_stage_energy = all_worker_stage_energy[architecture]
            
            if not worker_stage_energy:
                ax.text(0.5, 0.5, f'No data available\nfor {example.upper()}\n{architecture}\n{memory}MB', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{example.upper()} - {architecture}')
                ax.set_ylim(0, max_energy)
                continue
            
            # Prepare data for stacking - only use workers that have data
            workers_list = sorted(worker_stage_energy.keys())
            
            # Determine which stages are present in the data
            all_stages_in_data = set()
            for worker_data in worker_stage_energy.values():
                all_stages_in_data.update(worker_data.keys())
            
            # Use only stages that exist in the data
            available_stages = [stage for stage in self.stages if stage in all_stages_in_data]
            
            if not available_stages:
                ax.text(0.5, 0.5, f'No stage data available\nfor {example.upper()}\n{architecture}\n{memory}MB', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{example.upper()} - {architecture}')
                ax.set_ylim(0, max_energy)
                continue
            
            # Define colors for stages
            stage_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA07A']
            
            # Create arrays for each stage
            stage_arrays = {}
            for stage in available_stages:
                stage_arrays[stage] = []
                for workers in workers_list:
                    energy = worker_stage_energy[workers].get(stage, 0)
                    stage_arrays[stage].append(energy)
            
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
            ax.set_title(f'{example.upper()} - {architecture}', fontweight='bold')
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
        filename = f"multistage_energy_stacked_{example}_{memory}MB.png"
        filepath = output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Generated: {filename}")

    def _create_example_graph(self, example: str, output_dir: Path):
        """Create one image with 2 graphs for a specific example."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'Energy Consumption by Stages - {example.upper()} Example', fontsize=16, fontweight='bold')
        
        # First pass: find maximum energy value across all subplots for consistent scaling
        max_energy = 0
        all_worker_stage_energy = {}
        
        for arch_idx, architecture in enumerate(self.architectures):
            # Try different memory configurations to find data
            worker_stage_energy = {}
            for memory in self.memory_configs:
                temp_data = self._aggregate_energy_data(example, memory, architecture)
                if temp_data:
                    worker_stage_energy = temp_data
                    break
            
            all_worker_stage_energy[architecture] = worker_stage_energy
            
            if worker_stage_energy:
                # Find maximum total energy for this configuration
                for workers, stage_data in worker_stage_energy.items():
                    total_energy = sum(stage_data.values())
                    max_energy = max(max_energy, total_energy)
        
        # Add some padding to the maximum value
        max_energy *= 1.1 if max_energy > 0 else 1000
        
        # Second pass: create plots with consistent Y-axis scale
        for arch_idx, architecture in enumerate(self.architectures):
            ax = axes[arch_idx]
            worker_stage_energy = all_worker_stage_energy[architecture]
            
            if not worker_stage_energy:
                ax.text(0.5, 0.5, f'No data available\nfor {example.upper()}\n{architecture}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{example.upper()} - {architecture}')
                ax.set_ylim(0, max_energy)
                continue
            
            # Prepare data for stacking - only use workers that have data
            workers_list = sorted(worker_stage_energy.keys())
            
            # Determine which stages are present in the data
            all_stages_in_data = set()
            for worker_data in worker_stage_energy.values():
                all_stages_in_data.update(worker_data.keys())
            
            # Use only stages that exist in the data
            available_stages = [stage for stage in self.stages if stage in all_stages_in_data]
            
            if not available_stages:
                ax.text(0.5, 0.5, f'No stage data available\nfor {example.upper()}\n{architecture}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'{example.upper()} - {architecture}')
                ax.set_ylim(0, max_energy)
                continue
            
            # Define colors for stages
            stage_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA07A']
            
            # Create arrays for each stage
            stage_arrays = {}
            for stage in available_stages:
                stage_arrays[stage] = []
                for workers in workers_list:
                    energy = worker_stage_energy[workers].get(stage, 0)
                    stage_arrays[stage].append(energy)
            
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
            ax.set_title(f'{example.upper()} - {architecture}', fontweight='bold')
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
        filename = f"multistage_energy_stacked_{example}.png"
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
        """Generate a summary report of the data."""
        if self.data is None:
            print("No data loaded. Please run load_data() first.")
            return
            
        print("\n" + "="*60)
        print("MULTISTAGE ENERGY ANALYSIS SUMMARY")
        print("="*60)
        
        for example in self.examples:
            example_data = self.data[self.data['Example'] == example]
            if example_data.empty:
                continue
                
            print(f"\n{example.upper()} Example:")
            print("-" * 20)
            
            for architecture in self.architectures:
                # Try different memory configurations to find data
                worker_stage_energy = {}
                memory_used = None
                for memory in self.memory_configs:
                    temp_data = self._aggregate_energy_data(example, memory, architecture)
                    if temp_data:
                        worker_stage_energy = temp_data
                        memory_used = memory
                        break
                
                if worker_stage_energy:
                    workers_count = len(worker_stage_energy)
                    
                    # Calculate average energy per stage
                    stage_averages = {}
                    all_stages_in_data = set()
                    for worker_data in worker_stage_energy.values():
                        all_stages_in_data.update(worker_data.keys())
                    
                    for stage in all_stages_in_data:
                        energies = []
                        for worker_data in worker_stage_energy.values():
                            if stage in worker_data:
                                energies.append(worker_data[stage])
                        if energies:
                            stage_averages[stage] = np.mean(energies)
                    
                    print(f"  {architecture} ({memory_used}MB): {workers_count} worker configs")
                    for stage, avg_energy in stage_averages.items():
                        print(f"    {stage}: {avg_energy:.0f}J average")
    
    def run_analysis(self):
        """Run the complete analysis."""
        print("Starting Multistage Stacked Graph Analysis (CSV Version)...")
        print("Processing examples: ml, video, pi, titanic (all examples)")
        self.load_data()
        self.generate_stacked_graphs()
        self.generate_summary_report()
        print("\nAnalysis complete!")

def main():
    """Main function to run the analysis."""
    # Fix: Check for CSV file existence and provide fallback
    csv_path = Path("execution_summary.csv")
    
    if not csv_path.exists():
        print("⚠️  execution_summary.csv not found, skipping multistage stacked graphs analysis")
        print("   This analysis requires a CSV summary file to be generated first")
        return
    
    # Initialize the generator
    generator = MultistageStackedGraphGeneratorCSV(str(csv_path))
    
    # Fix: Use consistent output directory
    generator.output_dir = Path("/Users/arriazui/Desktop/GreenComputing/flexecutor-main/examples/general_usage/plot_generation/014_multistage_stacked_graphs_csv")
    
    # Run the complete analysis
    generator.run_analysis()

if __name__ == "__main__":
    main()

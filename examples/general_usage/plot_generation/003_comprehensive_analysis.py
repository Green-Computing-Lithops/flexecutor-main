#!/usr/bin/env python3
"""
Comprehensive Statistical Analysis of FlexExecutor Performance Data
================================================================

This script analyzes performance data across different:
- Examples (video, ml, titanic, pi)
- Memory configurations (512MB, 1024MB, 2048MB)
- Architectures (ARM vs x86)
- Number of workers
- Stages (stage0, stage1, stage2, stage3)

Key metrics analyzed:
- Execution time
- AWS costs
- Energy consumption (TDP)
- Memory efficiency
- Worker scalability
"""

import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import re

class FlexExecutorAnalyzer:
    def __init__(self, data_dir: str, output_dir: str = "003_comprehensive_analysis"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.data = []
        self.df = None
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """Parse filename to extract metadata according to the naming convention."""
        # Remove _analysis.json suffix
        name = filename.replace('_analysis.json', '')
        
        # Handle special cases
        if name == 'enhanced_profiling_analysis':
            return None
        if 'processing_analysis' in name:
            return None
            
        # Split by underscore
        parts = name.split('_')
        
        if len(parts) < 4:
            return None
            
        result = {
            'example': parts[0],
            'stage': parts[1],
            'backend': 'NA',
            'memory': 'NA',
            'architecture': 'NA'
        }
        
        # Find backend, memory, and architecture
        for i, part in enumerate(parts[2:], 2):
            if part in ['aws', 'k8s']:
                result['backend'] = part
            elif part.endswith('Mb'):
                result['memory'] = part
            elif part in ['arm', 'x86']:
                result['architecture'] = part
                
        return result
    
    def load_data(self):
        """Load all JSON files and extract relevant data."""
        print("Loading data files...")
        
        for file_path in self.data_dir.glob('*.json'):
            metadata = self.parse_filename(file_path.name)
            if metadata is None:
                continue
                
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Extract analysis results - Fix: Use correct key name
                if 'analysis_results' in data:
                    for result in data['analysis_results']:
                        record = {
                            **metadata,
                            **result,
                            'filename': file_path.name
                        }
                        self.data.append(record)
                        
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        self.df = pd.DataFrame(self.data)
        print(f"Loaded {len(self.df)} records from {len(self.data)} configurations")
        
    def print_data_summary(self):
        """Print summary of loaded data."""
        if self.df is None or self.df.empty:
            print("No data loaded!")
            return
            
        print("\n" + "="*60)
        print("DATA SUMMARY")
        print("="*60)
        
        print(f"Total records: {len(self.df)}")
        print(f"Examples: {sorted(self.df['example'].unique())}")
        print(f"Stages: {sorted(self.df['stage'].unique())}")
        print(f"Backends: {sorted(self.df['backend'].unique())}")
        print(f"Memory configs: {sorted(self.df['memory'].unique())}")
        print(f"Architectures: {sorted(self.df['architecture'].unique())}")
        print(f"Worker range: {self.df['workers'].min()} - {self.df['workers'].max()}")
        
        # Data availability matrix
        print("\nData availability by configuration:")
        availability = self.df.groupby(['example', 'memory', 'architecture']).size().unstack(fill_value=0)
        print(availability)
        
    def analyze_architecture_performance(self):
        """Compare ARM vs x86 performance across different metrics."""
        print("\n" + "="*60)
        print("ARCHITECTURE COMPARISON (ARM vs x86)")
        print("="*60)
        
        # Filter data with both architectures
        arch_data = self.df[self.df['architecture'].isin(['arm', 'x86'])]
        
        if arch_data.empty:
            print("No architecture comparison data available")
            return
            
        # Group by architecture and calculate means
        arch_comparison = arch_data.groupby('architecture').agg({
            'avg_execution': 'mean',
            'cost_aws_moneywise': 'mean',
            'avg_tdp': 'mean',
            'avg_worker_time_execution': 'mean',
            'processor_tdp_watts': 'mean'
        }).round(3)
        
        print("Average Performance Metrics by Architecture:")
        print(arch_comparison)
        
        # Calculate percentage differences
        if len(arch_comparison) == 2:
            arm_metrics = arch_comparison.loc['arm']
            x86_metrics = arch_comparison.loc['x86']
            
            print("\nPerformance Differences (ARM vs x86):")
            for metric in arch_comparison.columns:
                diff_pct = ((arm_metrics[metric] - x86_metrics[metric]) / x86_metrics[metric]) * 100
                direction = "faster" if diff_pct < 0 else "slower"
                if metric == 'cost_aws_moneywise':
                    direction = "cheaper" if diff_pct < 0 else "more expensive"
                elif metric == 'avg_tdp':
                    direction = "more efficient" if diff_pct < 0 else "less efficient"
                    
                print(f"  {metric}: ARM is {abs(diff_pct):.1f}% {direction}")
        
        # Generate architecture comparison plots
        self.plot_architecture_comparison(arch_data)
        
        return arch_comparison
    
    def plot_architecture_comparison(self, arch_data):
        """Generate architecture comparison visualizations."""
        if arch_data.empty:
            return
            
        # Create a 2x2 subplot for architecture comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Architecture Performance Comparison (ARM vs x86)', fontsize=16, fontweight='bold')
        
        # Plot 1: Execution Time Comparison
        arch_exec = arch_data.groupby('architecture')['avg_execution'].mean()
        axes[0,0].bar(arch_exec.index, arch_exec.values, color=['#ff7f0e', '#1f77b4'])
        axes[0,0].set_title('Average Execution Time')
        axes[0,0].set_ylabel('Time (seconds)')
        
        # Plot 2: Cost Comparison
        arch_cost = arch_data.groupby('architecture')['cost_aws_moneywise'].mean()
        axes[0,1].bar(arch_cost.index, arch_cost.values, color=['#ff7f0e', '#1f77b4'])
        axes[0,1].set_title('Average AWS Cost')
        axes[0,1].set_ylabel('Cost (USD per 1000 executions)')
        
        # Plot 3: Energy Efficiency
        arch_energy = arch_data.groupby('architecture')['avg_tdp'].mean()
        axes[1,0].bar(arch_energy.index, arch_energy.values, color=['#ff7f0e', '#1f77b4'])
        axes[1,0].set_title('Average Energy Consumption')
        axes[1,0].set_ylabel('TDP (Watts)')
        
        # Plot 4: Box plot of execution times by architecture
        sns.boxplot(data=arch_data, x='architecture', y='avg_execution', ax=axes[1,1])
        axes[1,1].set_title('Execution Time Distribution')
        axes[1,1].set_ylabel('Time (seconds)')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'architecture_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: architecture_comparison.png")
    
    def analyze_memory_scaling(self):
        """Analyze performance scaling with memory configurations."""
        print("\n" + "="*60)
        print("MEMORY SCALING ANALYSIS")
        print("="*60)
        
        memory_data = self.df[self.df['memory'] != 'NA']
        
        if memory_data.empty:
            print("No memory scaling data available")
            return
            
        # Convert memory to numeric for sorting
        memory_data = memory_data.copy()
        # Handle both string and numeric memory values
        if memory_data['memory'].dtype == 'object':
            memory_data['memory_mb'] = memory_data['memory'].str.replace('Mb', '').astype(int)
        else:
            memory_data['memory_mb'] = memory_data['memory']
        
        memory_comparison = memory_data.groupby('memory_mb').agg({
            'avg_execution': 'mean',
            'cost_aws_moneywise': 'mean',
            'avg_tdp': 'mean',
            'avg_worker_time_execution': 'mean'
        }).round(3)
        
        print("Performance by Memory Configuration:")
        print(memory_comparison)
        
        # Calculate efficiency metrics
        print("\nMemory Efficiency Analysis:")
        for memory in sorted(memory_data['memory_mb'].unique()):
            subset = memory_data[memory_data['memory_mb'] == memory]
            efficiency = subset['avg_execution'].mean() / memory
            cost_efficiency = subset['cost_aws_moneywise'].mean() / memory
            print(f"  {memory}MB: {efficiency:.4f} sec/MB, ${cost_efficiency:.6f}/MB")
        
        # Generate memory scaling plots
        self.plot_memory_scaling(memory_data)
            
        return memory_comparison
    
    def plot_memory_scaling(self, memory_data):
        """Generate memory scaling visualizations."""
        if memory_data.empty:
            return
            
        # Create a 2x2 subplot for memory scaling analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Memory Configuration Performance Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Execution Time vs Memory
        memory_exec = memory_data.groupby('memory_mb')['avg_execution'].mean()
        axes[0,0].plot(memory_exec.index, memory_exec.values, marker='o', linewidth=2, markersize=8)
        axes[0,0].set_title('Execution Time vs Memory')
        axes[0,0].set_xlabel('Memory (MB)')
        axes[0,0].set_ylabel('Time (seconds)')
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Cost vs Memory
        memory_cost = memory_data.groupby('memory_mb')['cost_aws_moneywise'].mean()
        axes[0,1].plot(memory_cost.index, memory_cost.values, marker='s', linewidth=2, markersize=8, color='orange')
        axes[0,1].set_title('Cost vs Memory')
        axes[0,1].set_xlabel('Memory (MB)')
        axes[0,1].set_ylabel('Cost (USD per 1000 executions)')
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Energy vs Memory
        memory_energy = memory_data.groupby('memory_mb')['avg_tdp'].mean()
        axes[1,0].plot(memory_energy.index, memory_energy.values, marker='^', linewidth=2, markersize=8, color='green')
        axes[1,0].set_title('Energy Consumption vs Memory')
        axes[1,0].set_xlabel('Memory (MB)')
        axes[1,0].set_ylabel('TDP (Watts)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Memory efficiency heatmap by example and memory
        pivot_data = memory_data.pivot_table(values='avg_execution', index='example', columns='memory_mb', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[1,1])
        axes[1,1].set_title('Execution Time by Workload & Memory')
        axes[1,1].set_xlabel('Memory (MB)')
        axes[1,1].set_ylabel('Workload Type')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'memory_scaling_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: memory_scaling_analysis.png")
    
    def analyze_worker_scalability(self):
        """Analyze how performance scales with number of workers."""
        print("\n" + "="*60)
        print("WORKER SCALABILITY ANALYSIS")
        print("="*60)
        
        # Group by workers and calculate statistics
        worker_stats = self.df.groupby('workers').agg({
            'avg_execution': ['mean', 'std', 'count'],
            'cost_aws_moneywise': ['mean', 'std'],
            'avg_tdp': ['mean', 'std'],
            'avg_worker_time_execution': ['mean', 'std']
        }).round(3)
        
        print("Performance by Number of Workers:")
        print(worker_stats)
        
        # Find optimal worker count for different metrics
        worker_means = self.df.groupby('workers').agg({
            'avg_execution': 'mean',
            'cost_aws_moneywise': 'mean',
            'avg_tdp': 'mean'
        })
        
        print("\nOptimal Worker Counts:")
        print(f"  Fastest execution: {worker_means['avg_execution'].idxmin()} workers")
        print(f"  Lowest cost: {worker_means['cost_aws_moneywise'].idxmin()} workers")
        print(f"  Most energy efficient: {worker_means['avg_tdp'].idxmin()} workers")
        
        # Generate worker scalability plots
        self.plot_worker_scalability(worker_means)
        
        return worker_stats
    
    def plot_worker_scalability(self, worker_means):
        """Generate worker scalability visualizations."""
        if worker_means.empty:
            return
            
        # Create a 2x2 subplot for worker scalability analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Worker Scalability Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Execution Time vs Workers
        axes[0,0].plot(worker_means.index, worker_means['avg_execution'], marker='o', linewidth=2, markersize=8)
        axes[0,0].set_title('Execution Time vs Number of Workers')
        axes[0,0].set_xlabel('Number of Workers')
        axes[0,0].set_ylabel('Time (seconds)')
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Cost vs Workers
        axes[0,1].plot(worker_means.index, worker_means['cost_aws_moneywise'], marker='s', linewidth=2, markersize=8, color='orange')
        axes[0,1].set_title('Cost vs Number of Workers')
        axes[0,1].set_xlabel('Number of Workers')
        axes[0,1].set_ylabel('Cost (USD per 1000 executions)')
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Energy vs Workers
        axes[1,0].plot(worker_means.index, worker_means['avg_tdp'], marker='^', linewidth=2, markersize=8, color='green')
        axes[1,0].set_title('Energy Consumption vs Number of Workers')
        axes[1,0].set_xlabel('Number of Workers')
        axes[1,0].set_ylabel('TDP (Watts)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Efficiency (inverse of execution time) vs Workers
        efficiency = 1 / worker_means['avg_execution']
        axes[1,1].plot(worker_means.index, efficiency, marker='d', linewidth=2, markersize=8, color='red')
        axes[1,1].set_title('Performance Efficiency vs Number of Workers')
        axes[1,1].set_xlabel('Number of Workers')
        axes[1,1].set_ylabel('Efficiency (1/seconds)')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'worker_scalability_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: worker_scalability_analysis.png")
    
    def analyze_example_workloads(self):
        """Compare performance across different example workloads."""
        print("\n" + "="*60)
        print("WORKLOAD COMPARISON")
        print("="*60)
        
        workload_comparison = self.df.groupby('example').agg({
            'avg_execution': ['mean', 'std', 'min', 'max'],
            'cost_aws_moneywise': ['mean', 'std', 'min', 'max'],
            'avg_tdp': ['mean', 'std', 'min', 'max'],
            'workers': ['min', 'max', 'count']
        }).round(3)
        
        print("Performance by Workload Type:")
        print(workload_comparison)
        
        # Rank workloads by different criteria
        workload_means = self.df.groupby('example').agg({
            'avg_execution': 'mean',
            'cost_aws_moneywise': 'mean',
            'avg_tdp': 'mean'
        }).round(3)
        
        print("\nWorkload Rankings:")
        print("By execution time (fastest to slowest):")
        for i, (example, time) in enumerate(workload_means.sort_values('avg_execution').iterrows(), 1):
            print(f"  {i}. {example}: {time['avg_execution']:.3f}s")
            
        print("\nBy cost (cheapest to most expensive):")
        for i, (example, cost) in enumerate(workload_means.sort_values('cost_aws_moneywise').iterrows(), 1):
            print(f"  {i}. {example}: ${cost['cost_aws_moneywise']:.3f}")
            
        print("\nBy energy efficiency (most to least efficient):")
        for i, (example, energy) in enumerate(workload_means.sort_values('avg_tdp').iterrows(), 1):
            print(f"  {i}. {example}: {energy['avg_tdp']:.1f}W")
            
        return workload_comparison
    
    def analyze_cost_efficiency(self):
        """Analyze cost efficiency across different configurations."""
        print("\n" + "="*60)
        print("COST EFFICIENCY ANALYSIS")
        print("="*60)
        
        # Calculate cost per second of execution
        self.df['cost_per_second'] = self.df['cost_aws_moneywise'] / self.df['avg_execution']
        
        # Cost efficiency by architecture
        if 'arm' in self.df['architecture'].values and 'x86' in self.df['architecture'].values:
            arch_cost = self.df[self.df['architecture'].isin(['arm', 'x86'])].groupby('architecture').agg({
                'cost_aws_moneywise': 'mean',
                'cost_per_second': 'mean',
                'avg_execution': 'mean'
            }).round(4)
            
            print("Cost Efficiency by Architecture:")
            print(arch_cost)
            
        # Cost efficiency by memory
        memory_cost = self.df[self.df['memory'] != 'NA'].groupby('memory').agg({
            'cost_aws_moneywise': 'mean',
            'cost_per_second': 'mean',
            'avg_execution': 'mean'
        }).round(4)
        
        print("\nCost Efficiency by Memory Configuration:")
        print(memory_cost)
        
        # Find most cost-effective configurations
        print("\nMost Cost-Effective Configurations:")
        top_configs = self.df.nsmallest(5, 'cost_per_second')[
            ['example', 'memory', 'architecture', 'workers', 'cost_per_second', 'avg_execution']
        ]
        print(top_configs)
        
        return arch_cost, memory_cost
    
    def generate_insights_and_recommendations(self):
        """Generate key insights and recommendations."""
        print("\n" + "="*60)
        print("KEY INSIGHTS AND RECOMMENDATIONS")
        print("="*60)
        
        insights = []
        
        # Architecture insights
        if 'arm' in self.df['architecture'].values and 'x86' in self.df['architecture'].values:
            arm_data = self.df[self.df['architecture'] == 'arm']
            x86_data = self.df[self.df['architecture'] == 'x86']
            
            arm_avg_cost = arm_data['cost_aws_moneywise'].mean()
            x86_avg_cost = x86_data['cost_aws_moneywise'].mean()
            arm_avg_time = arm_data['avg_execution'].mean()
            x86_avg_time = x86_data['avg_execution'].mean()
            
            if arm_avg_cost < x86_avg_cost:
                cost_savings = ((x86_avg_cost - arm_avg_cost) / x86_avg_cost) * 100
                insights.append(f"💰 ARM architecture is {cost_savings:.1f}% more cost-effective than x86")
            
            if arm_avg_time < x86_avg_time:
                time_savings = ((x86_avg_time - arm_avg_time) / x86_avg_time) * 100
                insights.append(f"⚡ ARM architecture is {time_savings:.1f}% faster than x86")
        
        # Memory insights
        memory_data = self.df[self.df['memory'] != 'NA'].copy()
        if not memory_data.empty:
            # Handle both string and numeric memory values
            if memory_data['memory'].dtype == 'object':
                memory_data['memory_mb'] = memory_data['memory'].str.replace('Mb', '').astype(int)
            else:
                memory_data['memory_mb'] = memory_data['memory']
            memory_perf = memory_data.groupby('memory_mb')['avg_execution'].mean()
            
            if len(memory_perf) > 1:
                best_memory = memory_perf.idxmin()
                insights.append(f"🧠 {best_memory}MB memory configuration shows best average performance")
        
        # Worker scalability insights
        worker_perf = self.df.groupby('workers')['avg_execution'].mean()
        optimal_workers = worker_perf.idxmin()
        insights.append(f"👥 Optimal worker count for performance: {optimal_workers} workers")
        
        # Workload insights
        workload_perf = self.df.groupby('example').agg({
            'avg_execution': 'mean',
            'cost_aws_moneywise': 'mean'
        })
        fastest_workload = workload_perf['avg_execution'].idxmin()
        cheapest_workload = workload_perf['cost_aws_moneywise'].idxmin()
        
        insights.append(f"🏃 Fastest workload type: {fastest_workload}")
        insights.append(f"💵 Most cost-effective workload type: {cheapest_workload}")
        
        # Print insights
        for insight in insights:
            print(f"  {insight}")
        
        
        return insights

def main():
    """Main analysis function."""
    # Set up the analyzer
    data_dir = "001_analysis_results"
    analyzer = FlexExecutorAnalyzer(data_dir)
    
    # Load and analyze data
    analyzer.load_data()
    
    if analyzer.df is None or analyzer.df.empty:
        print("No data could be loaded. Please check the data directory and file formats.")
        return
    
    # Generate comprehensive analysis
    analyzer.print_data_summary()
    analyzer.analyze_architecture_performance()
    analyzer.analyze_memory_scaling()
    analyzer.analyze_worker_scalability()
    analyzer.analyze_example_workloads()
    analyzer.analyze_cost_efficiency()
    analyzer.generate_insights_and_recommendations()
    


if __name__ == "__main__":
    main()

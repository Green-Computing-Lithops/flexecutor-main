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
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data = []
        self.df = None
        
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
                    
                # Extract analysis results
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
        
        return arch_comparison
    
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
        memory_data['memory_mb'] = memory_data['memory'].str.replace('Mb', '').astype(int)
        
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
            
        return memory_comparison
    
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
        
        return worker_stats
    
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
            memory_data['memory_mb'] = memory_data['memory'].str.replace('Mb', '').astype(int)
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
        
        print("\n📊 RECOMMENDATIONS:")
        print("  1. For cost optimization: Prefer ARM architecture when available")
        print("  2. For performance: Test different worker counts to find optimal parallelization")
        print("  3. For memory efficiency: Start with 1024MB and scale based on workload requirements")
        print("  4. For energy efficiency: Monitor TDP values and prefer configurations with lower energy consumption")
        print("  5. For production: Consider workload characteristics when choosing configurations")
        
        return insights

def main():
    """Main analysis function."""
    # Set up the analyzer
    data_dir = "analysis_results"
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
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("This analysis provides comprehensive insights into FlexExecutor performance")
    print("across different configurations, architectures, and workloads.")

if __name__ == "__main__":
    main()

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
from pathlib import Path
from collections import defaultdict
import statistics

class FlexExecutorAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data = []
        
    def parse_filename(self, filename: str):
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
                
        print(f"Loaded {len(self.data)} records")
        
    def print_data_summary(self):
        """Print summary of loaded data."""
        if not self.data:
            print("No data loaded!")
            return
            
        print("\n" + "="*60)
        print("DATA SUMMARY")
        print("="*60)
        
        examples = set(record['example'] for record in self.data)
        stages = set(record['stage'] for record in self.data)
        backends = set(record['backend'] for record in self.data)
        memories = set(record['memory'] for record in self.data)
        architectures = set(record['architecture'] for record in self.data)
        workers = [record['workers'] for record in self.data]
        
        print(f"Total records: {len(self.data)}")
        print(f"Examples: {sorted(examples)}")
        print(f"Stages: {sorted(stages)}")
        print(f"Backends: {sorted(backends)}")
        print(f"Memory configs: {sorted(memories)}")
        print(f"Architectures: {sorted(architectures)}")
        print(f"Worker range: {min(workers)} - {max(workers)}")
        
    def analyze_architecture_performance(self):
        """Compare ARM vs x86 performance across different metrics."""
        print("\n" + "="*60)
        print("ARCHITECTURE COMPARISON (ARM vs x86)")
        print("="*60)
        
        # Group data by architecture
        arch_data = defaultdict(list)
        for record in self.data:
            if record['architecture'] in ['arm', 'x86']:
                arch_data[record['architecture']].append(record)
        
        if not arch_data:
            print("No architecture comparison data available")
            return
            
        print("Average Performance Metrics by Architecture:")
        
        for arch in sorted(arch_data.keys()):
            records = arch_data[arch]
            
            avg_execution = statistics.mean(r['avg_execution'] for r in records)
            avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in records)
            avg_tdp = statistics.mean(r['avg_tdp'] for r in records)
            avg_worker_time = statistics.mean(r['avg_worker_time_execution'] for r in records)
            avg_processor_tdp = statistics.mean(r['processor_tdp_watts'] for r in records)
            
            print(f"\n{arch.upper()} Architecture ({len(records)} records):")
            print(f"  Average execution time: {avg_execution:.3f}s")
            print(f"  Average AWS cost: ${avg_cost:.4f}")
            print(f"  Average TDP: {avg_tdp:.1f}W")
            print(f"  Average worker time: {avg_worker_time:.3f}s")
            print(f"  Processor TDP: {avg_processor_tdp:.0f}W")
        
        # Calculate differences if both architectures present
        if len(arch_data) == 2:
            arm_records = arch_data['arm']
            x86_records = arch_data['x86']
            
            arm_exec = statistics.mean(r['avg_execution'] for r in arm_records)
            x86_exec = statistics.mean(r['avg_execution'] for r in x86_records)
            arm_cost = statistics.mean(r['cost_aws_moneywise'] for r in arm_records)
            x86_cost = statistics.mean(r['cost_aws_moneywise'] for r in x86_records)
            arm_tdp = statistics.mean(r['avg_tdp'] for r in arm_records)
            x86_tdp = statistics.mean(r['avg_tdp'] for r in x86_records)
            
            print(f"\nPerformance Differences (ARM vs x86):")
            
            exec_diff = ((arm_exec - x86_exec) / x86_exec) * 100
            exec_direction = "faster" if exec_diff < 0 else "slower"
            print(f"  Execution time: ARM is {abs(exec_diff):.1f}% {exec_direction}")
            
            cost_diff = ((arm_cost - x86_cost) / x86_cost) * 100
            cost_direction = "cheaper" if cost_diff < 0 else "more expensive"
            print(f"  AWS cost: ARM is {abs(cost_diff):.1f}% {cost_direction}")
            
            tdp_diff = ((arm_tdp - x86_tdp) / x86_tdp) * 100
            tdp_direction = "more efficient" if tdp_diff < 0 else "less efficient"
            print(f"  Energy (TDP): ARM is {abs(tdp_diff):.1f}% {tdp_direction}")
    
    def analyze_memory_scaling(self):
        """Analyze performance scaling with memory configurations."""
        print("\n" + "="*60)
        print("MEMORY SCALING ANALYSIS")
        print("="*60)
        
        # Group data by memory
        memory_data = defaultdict(list)
        for record in self.data:
            if record['memory'] != 'NA':
                memory_data[record['memory']].append(record)
        
        if not memory_data:
            print("No memory scaling data available")
            return
            
        print("Performance by Memory Configuration:")
        
        memory_stats = {}
        for memory in sorted(memory_data.keys(), key=lambda x: int(str(x).replace('Mb', '')) if isinstance(x, str) else x):
            records = memory_data[memory]
            
            avg_execution = statistics.mean(r['avg_execution'] for r in records)
            avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in records)
            avg_tdp = statistics.mean(r['avg_tdp'] for r in records)
            
            memory_mb = int(str(memory).replace('Mb', '')) if isinstance(memory, str) else memory
            efficiency = avg_execution / memory_mb
            cost_efficiency = avg_cost / memory_mb
            
            memory_stats[memory] = {
                'avg_execution': avg_execution,
                'avg_cost': avg_cost,
                'avg_tdp': avg_tdp,
                'efficiency': efficiency,
                'cost_efficiency': cost_efficiency,
                'count': len(records)
            }
            
            print(f"\n{memory}MB ({len(records)} records):")
            print(f"  Average execution time: {avg_execution:.3f}s")
            print(f"  Average AWS cost: ${avg_cost:.4f}")
            print(f"  Average TDP: {avg_tdp:.1f}W")
            print(f"  Time efficiency: {efficiency:.6f} sec/MB")
            print(f"  Cost efficiency: ${cost_efficiency:.8f}/MB")
        
        # Find best configurations
        best_time = min(memory_stats.items(), key=lambda x: x[1]['avg_execution'])
        best_cost = min(memory_stats.items(), key=lambda x: x[1]['avg_cost'])
        best_efficiency = min(memory_stats.items(), key=lambda x: x[1]['efficiency'])
        
        print(f"\nBest Configurations:")
        print(f"  Fastest execution: {best_time[0]}MB ({best_time[1]['avg_execution']:.3f}s)")
        print(f"  Lowest cost: {best_cost[0]}MB (${best_cost[1]['avg_cost']:.4f})")
        print(f"  Most time-efficient: {best_efficiency[0]}MB ({best_efficiency[1]['efficiency']:.6f} sec/MB)")
    
    def analyze_worker_scalability(self):
        """Analyze how performance scales with number of workers."""
        print("\n" + "="*60)
        print("WORKER SCALABILITY ANALYSIS")
        print("="*60)
        
        # Group data by worker count
        worker_data = defaultdict(list)
        for record in self.data:
            worker_data[record['workers']].append(record)
        
        print("Performance by Number of Workers:")
        
        worker_stats = {}
        for workers in sorted(worker_data.keys()):
            records = worker_data[workers]
            
            executions = [r['avg_execution'] for r in records]
            costs = [r['cost_aws_moneywise'] for r in records]
            tdps = [r['avg_tdp'] for r in records]
            
            avg_execution = statistics.mean(executions)
            std_execution = statistics.stdev(executions) if len(executions) > 1 else 0
            avg_cost = statistics.mean(costs)
            avg_tdp = statistics.mean(tdps)
            
            worker_stats[workers] = {
                'avg_execution': avg_execution,
                'std_execution': std_execution,
                'avg_cost': avg_cost,
                'avg_tdp': avg_tdp,
                'count': len(records)
            }
            
            print(f"\n{workers} workers ({len(records)} records):")
            print(f"  Average execution time: {avg_execution:.3f}s ± {std_execution:.3f}")
            print(f"  Average AWS cost: ${avg_cost:.4f}")
            print(f"  Average TDP: {avg_tdp:.1f}W")
        
        # Find optimal configurations
        best_time = min(worker_stats.items(), key=lambda x: x[1]['avg_execution'])
        best_cost = min(worker_stats.items(), key=lambda x: x[1]['avg_cost'])
        best_energy = min(worker_stats.items(), key=lambda x: x[1]['avg_tdp'])
        
        print(f"\nOptimal Worker Counts:")
        print(f"  Fastest execution: {best_time[0]} workers ({best_time[1]['avg_execution']:.3f}s)")
        print(f"  Lowest cost: {best_cost[0]} workers (${best_cost[1]['avg_cost']:.4f})")
        print(f"  Most energy efficient: {best_energy[0]} workers ({best_energy[1]['avg_tdp']:.1f}W)")
    
    def analyze_example_workloads(self):
        """Compare performance across different example workloads."""
        print("\n" + "="*60)
        print("WORKLOAD COMPARISON")
        print("="*60)
        
        # Group data by example
        example_data = defaultdict(list)
        for record in self.data:
            example_data[record['example']].append(record)
        
        print("Performance by Workload Type:")
        
        workload_stats = {}
        for example in sorted(example_data.keys()):
            records = example_data[example]
            
            executions = [r['avg_execution'] for r in records]
            costs = [r['cost_aws_moneywise'] for r in records]
            tdps = [r['avg_tdp'] for r in records]
            workers = [r['workers'] for r in records]
            
            workload_stats[example] = {
                'avg_execution': statistics.mean(executions),
                'min_execution': min(executions),
                'max_execution': max(executions),
                'avg_cost': statistics.mean(costs),
                'min_cost': min(costs),
                'max_cost': max(costs),
                'avg_tdp': statistics.mean(tdps),
                'min_workers': min(workers),
                'max_workers': max(workers),
                'count': len(records)
            }
            
            print(f"\n{example.upper()} ({len(records)} records):")
            print(f"  Execution time: {workload_stats[example]['avg_execution']:.3f}s (range: {workload_stats[example]['min_execution']:.3f}-{workload_stats[example]['max_execution']:.3f})")
            print(f"  AWS cost: ${workload_stats[example]['avg_cost']:.4f} (range: ${workload_stats[example]['min_cost']:.4f}-${workload_stats[example]['max_cost']:.4f})")
            print(f"  TDP: {workload_stats[example]['avg_tdp']:.1f}W")
            print(f"  Workers tested: {workload_stats[example]['min_workers']}-{workload_stats[example]['max_workers']}")
        
        # Rankings
        print(f"\nWorkload Rankings:")
        
        print("By execution time (fastest to slowest):")
        sorted_by_time = sorted(workload_stats.items(), key=lambda x: x[1]['avg_execution'])
        for i, (example, stats) in enumerate(sorted_by_time, 1):
            print(f"  {i}. {example}: {stats['avg_execution']:.3f}s")
            
        print("\nBy cost (cheapest to most expensive):")
        sorted_by_cost = sorted(workload_stats.items(), key=lambda x: x[1]['avg_cost'])
        for i, (example, stats) in enumerate(sorted_by_cost, 1):
            print(f"  {i}. {example}: ${stats['avg_cost']:.4f}")
            
        print("\nBy energy efficiency (most to least efficient):")
        sorted_by_energy = sorted(workload_stats.items(), key=lambda x: x[1]['avg_tdp'])
        for i, (example, stats) in enumerate(sorted_by_energy, 1):
            print(f"  {i}. {example}: {stats['avg_tdp']:.1f}W")
    
    def analyze_cost_efficiency(self):
        """Analyze cost efficiency across different configurations."""
        print("\n" + "="*60)
        print("COST EFFICIENCY ANALYSIS")
        print("="*60)
        
        # Calculate cost per second for all records
        for record in self.data:
            record['cost_per_second'] = record['cost_aws_moneywise'] / record['avg_execution']
        
        # Cost efficiency by architecture
        arch_data = defaultdict(list)
        for record in self.data:
            if record['architecture'] in ['arm', 'x86']:
                arch_data[record['architecture']].append(record)
        
        if arch_data:
            print("Cost Efficiency by Architecture:")
            for arch in sorted(arch_data.keys()):
                records = arch_data[arch]
                avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in records)
                avg_cost_per_sec = statistics.mean(r['cost_per_second'] for r in records)
                avg_execution = statistics.mean(r['avg_execution'] for r in records)
                
                print(f"  {arch.upper()}: ${avg_cost:.4f} total, ${avg_cost_per_sec:.6f}/sec, {avg_execution:.3f}s avg")
        
        # Cost efficiency by memory
        memory_data = defaultdict(list)
        for record in self.data:
            if record['memory'] != 'NA':
                memory_data[record['memory']].append(record)
        
        if memory_data:
            print("\nCost Efficiency by Memory Configuration:")
            for memory in sorted(memory_data.keys(), key=lambda x: int(str(x).replace('Mb', '')) if isinstance(x, str) else x):
                records = memory_data[memory]
                avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in records)
                avg_cost_per_sec = statistics.mean(r['cost_per_second'] for r in records)
                avg_execution = statistics.mean(r['avg_execution'] for r in records)
                
                print(f"  {memory}MB: ${avg_cost:.4f} total, ${avg_cost_per_sec:.6f}/sec, {avg_execution:.3f}s avg")
        
        # Most cost-effective configurations
        print("\nMost Cost-Effective Configurations (by cost per second):")
        sorted_records = sorted(self.data, key=lambda x: x['cost_per_second'])[:5]
        
        for i, record in enumerate(sorted_records, 1):
            print(f"  {i}. {record['example']}-{record['memory']}-{record['architecture']}-{record['workers']}w: ${record['cost_per_second']:.6f}/sec ({record['avg_execution']:.3f}s)")
    
    def generate_insights_and_recommendations(self):
        """Generate key insights and recommendations."""
        print("\n" + "="*60)
        print("KEY INSIGHTS AND RECOMMENDATIONS")
        print("="*60)
        
        insights = []
        
        # Architecture insights
        arm_records = [r for r in self.data if r['architecture'] == 'arm']
        x86_records = [r for r in self.data if r['architecture'] == 'x86']
        
        if arm_records and x86_records:
            arm_avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in arm_records)
            x86_avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in x86_records)
            arm_avg_time = statistics.mean(r['avg_execution'] for r in arm_records)
            x86_avg_time = statistics.mean(r['avg_execution'] for r in x86_records)
            
            if arm_avg_cost < x86_avg_cost:
                cost_savings = ((x86_avg_cost - arm_avg_cost) / x86_avg_cost) * 100
                insights.append(f"💰 ARM architecture is {cost_savings:.1f}% more cost-effective than x86")
            
            if arm_avg_time < x86_avg_time:
                time_savings = ((x86_avg_time - arm_avg_time) / x86_avg_time) * 100
                insights.append(f"⚡ ARM architecture is {time_savings:.1f}% faster than x86")
        
        # Memory insights
        memory_records = defaultdict(list)
        for record in self.data:
            if record['memory'] != 'NA':
                memory_records[record['memory']].append(record)
        
        if memory_records:
            memory_perf = {}
            for memory, records in memory_records.items():
                memory_perf[memory] = statistics.mean(r['avg_execution'] for r in records)
            
            best_memory = min(memory_perf.items(), key=lambda x: x[1])
            insights.append(f"🧠 {best_memory[0]}MB memory configuration shows best average performance")
        
        # Worker scalability insights
        worker_perf = defaultdict(list)
        for record in self.data:
            worker_perf[record['workers']].append(record['avg_execution'])
        
        worker_avg = {w: statistics.mean(times) for w, times in worker_perf.items()}
        optimal_workers = min(worker_avg.items(), key=lambda x: x[1])
        insights.append(f"👥 Optimal worker count for performance: {optimal_workers[0]} workers")
        
        # Workload insights
        example_perf = defaultdict(list)
        example_cost = defaultdict(list)
        for record in self.data:
            example_perf[record['example']].append(record['avg_execution'])
            example_cost[record['example']].append(record['cost_aws_moneywise'])
        
        example_avg_perf = {e: statistics.mean(times) for e, times in example_perf.items()}
        example_avg_cost = {e: statistics.mean(costs) for e, costs in example_cost.items()}
        
        fastest_workload = min(example_avg_perf.items(), key=lambda x: x[1])
        cheapest_workload = min(example_avg_cost.items(), key=lambda x: x[1])
        
        insights.append(f"🏃 Fastest workload type: {fastest_workload[0]}")
        insights.append(f"💵 Most cost-effective workload type: {cheapest_workload[0]}")
        
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
    
    if not analyzer.data:
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

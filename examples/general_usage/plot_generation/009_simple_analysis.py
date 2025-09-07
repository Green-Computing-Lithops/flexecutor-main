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
import csv
from pathlib import Path
from collections import defaultdict
import statistics

class FlexExecutorAnalyzer:
    def __init__(self, data_dir: str, output_dir: str = "009_simple_analysis"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.data = []
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        print(f"Output directory created: {self.output_dir.absolute()}")
        
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
        
        return insights

    def save_raw_data_to_csv(self):
        """Save all raw data to CSV."""
        output_file = self.output_dir / "01_raw_data.csv"
        
        if not self.data:
            print("No data to save.")
            return
            
        # Get all unique keys from all records
        all_keys = set()
        for record in self.data:
            all_keys.update(record.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)
        
        print(f"✅ Raw data saved to: {output_file}")

    def save_architecture_comparison_to_csv(self):
        """Save architecture comparison data to CSV."""
        output_file = self.output_dir / "02_architecture_comparison.csv"
        
        # Group data by architecture
        arch_data = defaultdict(list)
        for record in self.data:
            if record['architecture'] in ['arm', 'x86']:
                arch_data[record['architecture']].append(record)
        
        if not arch_data:
            print("No architecture comparison data available")
            return
            
        rows = []
        for arch in sorted(arch_data.keys()):
            records = arch_data[arch]
            
            row = {
                'architecture': arch.upper(),
                'record_count': len(records),
                'avg_execution_time': statistics.mean(r['avg_execution'] for r in records),
                'avg_aws_cost': statistics.mean(r['cost_aws_moneywise'] for r in records),
                'avg_tdp': statistics.mean(r['avg_tdp'] for r in records),
                'avg_worker_time_execution': statistics.mean(r['avg_worker_time_execution'] for r in records),
                'avg_processor_tdp_watts': statistics.mean(r['processor_tdp_watts'] for r in records)
            }
            rows.append(row)
        
        fieldnames = ['architecture', 'record_count', 'avg_execution_time', 'avg_aws_cost', 
                     'avg_tdp', 'avg_worker_time_execution', 'avg_processor_tdp_watts']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Architecture comparison saved to: {output_file}")

    def save_memory_scaling_to_csv(self):
        """Save memory scaling analysis to CSV."""
        output_file = self.output_dir / "03_memory_scaling.csv"
        
        # Group data by memory
        memory_data = defaultdict(list)
        for record in self.data:
            if record['memory'] != 'NA':
                memory_data[record['memory']].append(record)
        
        if not memory_data:
            print("No memory scaling data available")
            return
            
        rows = []
        for memory in sorted(memory_data.keys(), key=lambda x: int(str(x).replace('Mb', '')) if isinstance(x, str) else x):
            records = memory_data[memory]
            
            avg_execution = statistics.mean(r['avg_execution'] for r in records)
            avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in records)
            avg_tdp = statistics.mean(r['avg_tdp'] for r in records)
            
            memory_mb = int(str(memory).replace('Mb', '')) if isinstance(memory, str) else memory
            efficiency = avg_execution / memory_mb
            cost_efficiency = avg_cost / memory_mb
            
            row = {
                'memory_mb': memory_mb,
                'record_count': len(records),
                'avg_execution_time': avg_execution,
                'avg_aws_cost': avg_cost,
                'avg_tdp': avg_tdp,
                'time_efficiency_sec_per_mb': efficiency,
                'cost_efficiency_usd_per_mb': cost_efficiency
            }
            rows.append(row)
        
        fieldnames = ['memory_mb', 'record_count', 'avg_execution_time', 'avg_aws_cost', 
                     'avg_tdp', 'time_efficiency_sec_per_mb', 'cost_efficiency_usd_per_mb']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Memory scaling analysis saved to: {output_file}")

    def save_worker_scalability_to_csv(self):
        """Save worker scalability analysis to CSV."""
        output_file = self.output_dir / "04_worker_scalability.csv"
        
        # Group data by worker count
        worker_data = defaultdict(list)
        for record in self.data:
            worker_data[record['workers']].append(record)
        
        rows = []
        for workers in sorted(worker_data.keys()):
            records = worker_data[workers]
            
            executions = [r['avg_execution'] for r in records]
            costs = [r['cost_aws_moneywise'] for r in records]
            tdps = [r['avg_tdp'] for r in records]
            
            row = {
                'worker_count': workers,
                'record_count': len(records),
                'avg_execution_time': statistics.mean(executions),
                'std_execution_time': statistics.stdev(executions) if len(executions) > 1 else 0,
                'min_execution_time': min(executions),
                'max_execution_time': max(executions),
                'avg_aws_cost': statistics.mean(costs),
                'avg_tdp': statistics.mean(tdps)
            }
            rows.append(row)
        
        fieldnames = ['worker_count', 'record_count', 'avg_execution_time', 'std_execution_time',
                     'min_execution_time', 'max_execution_time', 'avg_aws_cost', 'avg_tdp']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Worker scalability analysis saved to: {output_file}")

    def save_workload_comparison_to_csv(self):
        """Save workload comparison analysis to CSV."""
        output_file = self.output_dir / "05_workload_comparison.csv"
        
        # Group data by example
        example_data = defaultdict(list)
        for record in self.data:
            example_data[record['example']].append(record)
        
        rows = []
        for example in sorted(example_data.keys()):
            records = example_data[example]
            
            executions = [r['avg_execution'] for r in records]
            costs = [r['cost_aws_moneywise'] for r in records]
            tdps = [r['avg_tdp'] for r in records]
            workers = [r['workers'] for r in records]
            
            row = {
                'workload_type': example,
                'record_count': len(records),
                'avg_execution_time': statistics.mean(executions),
                'min_execution_time': min(executions),
                'max_execution_time': max(executions),
                'avg_aws_cost': statistics.mean(costs),
                'min_aws_cost': min(costs),
                'max_aws_cost': max(costs),
                'avg_tdp': statistics.mean(tdps),
                'min_workers_tested': min(workers),
                'max_workers_tested': max(workers)
            }
            rows.append(row)
        
        fieldnames = ['workload_type', 'record_count', 'avg_execution_time', 'min_execution_time', 
                     'max_execution_time', 'avg_aws_cost', 'min_aws_cost', 'max_aws_cost', 
                     'avg_tdp', 'min_workers_tested', 'max_workers_tested']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Workload comparison analysis saved to: {output_file}")

    def save_cost_efficiency_to_csv(self):
        """Save cost efficiency analysis to CSV."""
        output_file = self.output_dir / "06_cost_efficiency.csv"
        
        # Calculate cost per second for all records
        enhanced_data = []
        for record in self.data.copy():
            cost_per_second = record['cost_aws_moneywise'] / record['avg_execution'] if record['avg_execution'] > 0 else 0
            enhanced_record = record.copy()
            enhanced_record['cost_per_second'] = cost_per_second
            enhanced_data.append(enhanced_record)
        
        # Sort by cost per second (most efficient first)
        enhanced_data.sort(key=lambda x: x['cost_per_second'])
        
        # Take top 20 most cost-effective configurations
        top_configs = enhanced_data[:20]
        
        rows = []
        for i, record in enumerate(top_configs, 1):
            row = {
                'rank': i,
                'configuration': f"{record['example']}-{record['memory']}-{record['architecture']}-{record['workers']}w",
                'workload': record['example'],
                'memory_mb': record['memory'],
                'architecture': record['architecture'],
                'workers': record['workers'],
                'avg_execution_time': record['avg_execution'],
                'aws_cost_total': record['cost_aws_moneywise'],
                'cost_per_second': record['cost_per_second'],
                'avg_tdp': record['avg_tdp']
            }
            rows.append(row)
        
        fieldnames = ['rank', 'configuration', 'workload', 'memory_mb', 'architecture', 'workers',
                     'avg_execution_time', 'aws_cost_total', 'cost_per_second', 'avg_tdp']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Cost efficiency analysis saved to: {output_file}")

    def save_insights_to_csv(self):
        """Save key insights and recommendations to CSV."""
        output_file = self.output_dir / "07_insights_recommendations.csv"
        
        insights = []
        
        # Architecture insights
        arm_records = [r for r in self.data if r['architecture'] == 'arm']
        x86_records = [r for r in self.data if r['architecture'] == 'x86']
        
        if arm_records and x86_records:
            arm_avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in arm_records)
            x86_avg_cost = statistics.mean(r['cost_aws_moneywise'] for r in x86_records)
            arm_avg_time = statistics.mean(r['avg_execution'] for r in arm_records)
            x86_avg_time = statistics.mean(r['avg_execution'] for r in x86_records)
            arm_avg_tdp = statistics.mean(r['avg_tdp'] for r in arm_records)
            x86_avg_tdp = statistics.mean(r['avg_tdp'] for r in x86_records)
            
            insights.append({
                'category': 'Architecture',
                'metric': 'Cost Efficiency',
                'insight': f"ARM vs x86 cost difference: {((arm_avg_cost - x86_avg_cost) / x86_avg_cost) * 100:.1f}%",
                'recommendation': 'Prefer ARM architecture for cost optimization' if arm_avg_cost < x86_avg_cost else 'Prefer x86 architecture for cost optimization'
            })
            
            insights.append({
                'category': 'Architecture', 
                'metric': 'Performance',
                'insight': f"ARM vs x86 performance difference: {((arm_avg_time - x86_avg_time) / x86_avg_time) * 100:.1f}%",
                'recommendation': 'Prefer ARM architecture for performance' if arm_avg_time < x86_avg_time else 'Prefer x86 architecture for performance'
            })
            
            insights.append({
                'category': 'Architecture',
                'metric': 'Energy Efficiency', 
                'insight': f"ARM vs x86 energy difference: {((arm_avg_tdp - x86_avg_tdp) / x86_avg_tdp) * 100:.1f}%",
                'recommendation': 'Prefer ARM architecture for energy efficiency' if arm_avg_tdp < x86_avg_tdp else 'Prefer x86 architecture for energy efficiency'
            })
        
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
            insights.append({
                'category': 'Memory',
                'metric': 'Performance',
                'insight': f"Best performing memory configuration: {best_memory[0]}MB with {best_memory[1]:.3f}s average execution time",
                'recommendation': f"Use {best_memory[0]}MB memory for optimal performance"
            })
        
        # Worker insights
        worker_perf = defaultdict(list)
        for record in self.data:
            worker_perf[record['workers']].append(record['avg_execution'])
        
        worker_avg = {w: statistics.mean(times) for w, times in worker_perf.items()}
        optimal_workers = min(worker_avg.items(), key=lambda x: x[1])
        insights.append({
            'category': 'Scalability',
            'metric': 'Performance',
            'insight': f"Optimal worker count: {optimal_workers[0]} workers with {optimal_workers[1]:.3f}s average execution time",
            'recommendation': f"Use {optimal_workers[0]} workers for optimal performance"
        })
        
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
        
        insights.append({
            'category': 'Workload',
            'metric': 'Performance',
            'insight': f"Fastest workload type: {fastest_workload[0]} with {fastest_workload[1]:.3f}s average execution time",
            'recommendation': f"Choose {fastest_workload[0]} workload type for fastest execution"
        })
        
        insights.append({
            'category': 'Workload',
            'metric': 'Cost',
            'insight': f"Most cost-effective workload type: {cheapest_workload[0]} with ${cheapest_workload[1]:.4f} average cost",
            'recommendation': f"Choose {cheapest_workload[0]} workload type for cost optimization"
        })
        
        fieldnames = ['category', 'metric', 'insight', 'recommendation']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(insights)
        
        print(f"✅ Insights and recommendations saved to: {output_file}")

    def save_all_analysis_to_csv(self):
        """Save all analysis results to CSV files."""
        print("\n" + "="*60)
        print("SAVING ANALYSIS RESULTS TO CSV")
        print("="*60)
        
        self.save_raw_data_to_csv()
        self.save_architecture_comparison_to_csv()
        self.save_memory_scaling_to_csv()
        self.save_worker_scalability_to_csv()
        self.save_workload_comparison_to_csv()
        self.save_cost_efficiency_to_csv()
        self.save_insights_to_csv()
        
        print(f"\n✅ All analysis results saved to: {self.output_dir.absolute()}")

def main():
    """Main analysis function."""
    # Set up the analyzer with output directory
    data_dir = "001_analysis_results"
    output_dir = "009_simple_analysis"
    analyzer = FlexExecutorAnalyzer(data_dir, output_dir)
    
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
    
    # Save all analysis results to CSV files
    analyzer.save_all_analysis_to_csv()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("This analysis provides comprehensive insights into FlexExecutor performance")
    print("across different configurations, architectures, and workloads.")
    print(f"All results have been saved to CSV files in: {analyzer.output_dir.absolute()}")


if __name__ == "__main__":
    main()

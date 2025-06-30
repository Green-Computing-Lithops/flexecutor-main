import json
from collections import defaultdict

TDP_VALUE = 180  # AMD EPYC 7502 32-Core Processor tdp 180 W 


def analyze_stage_data(file_path):
    # Load the JSON data
    with open(file_path) as f:
        data = json.load(f)
    
    results = []
    
    for config, metrics in data.items():
        # Extract configuration values from tuple
        config_parts = config.strip('()').split(',')
        cpu = int(config_parts[0].strip())
        memory = int(config_parts[1].strip())
        workers = int(config_parts[2].strip())
        
        # Initialize stats
        stats = {
            'cpu': cpu,
            'memory': memory,
            'workers': workers,
            'total_executions': 0,
            'avg_read': 0,
            'avg_compute': 0,
            'avg_write': 0,
            'avg_rapl': 0,
            'avg_tdp': 0,
            'avg_execution': 0,
            'min_compute': float('inf'),
            'max_compute': 0,
            'total_compute': 0,
            'min_rapl': float('inf'),
            'max_rapl': 0,
            'total_rapl': 0,
            'min_tdp': float('inf'),
            'max_tdp': 0,
            'total_tdp': 0,
            'min_execution': float('inf'),
            'max_execution': 0,
            'total_execution': 0
        }
        
        # Calculate statistics
        total_read = 0
        total_compute = 0
        total_write = 0
        total_rapl = 0
        total_tdp = 0
        total_execution = 0
        count = 0
        
        for op in ['read', 'compute', 'write', 'RAPL', 'TDP']:
            if op in metrics:
                executions = metrics[op]
                # Count executions based on any operation's array length
                if count == 0:  # Only set once per configuration
                    stats['total_executions'] = len(executions)
                    count = len(executions)
                
                # Flatten nested lists (some operations have multiple values per execution)
                flat_values = [item for sublist in executions for item in sublist]
                
                if op == 'read':
                    total_read = sum(flat_values)
                    stats['avg_read'] = total_read / len(flat_values)
                elif op == 'compute':
                    total_compute = sum(flat_values)
                    stats['avg_compute'] = total_compute / len(flat_values)
                    stats['min_compute'] = min(min(flat_values), stats['min_compute'])
                    stats['max_compute'] = max(max(flat_values), stats['max_compute'])
                    stats['total_compute'] = stats['avg_compute'] * workers
                elif op == 'write':
                    total_write = sum(flat_values)
                    stats['avg_write'] = total_write / len(flat_values)
                elif op == 'RAPL':
                    total_rapl = sum(flat_values)
                    stats['avg_rapl'] = total_rapl / len(flat_values)
                    stats['min_rapl'] = min(min(flat_values), stats['min_rapl'])
                    stats['max_rapl'] = max(max(flat_values), stats['max_rapl'])
                    stats['total_rapl'] = stats['avg_rapl'] * workers
                elif op == 'TDP': # convert to juls before further calculations
                    total_tdp = sum(flat_values) * TDP_VALUE
                    stats['avg_tdp'] = total_tdp / len(flat_values)
                    stats['min_tdp'] = min(min(flat_values) * TDP_VALUE, stats['min_tdp'])
                    stats['max_tdp'] = max(max(flat_values) * TDP_VALUE, stats['max_tdp'])
                    stats['total_tdp'] = stats['avg_tdp'] * workers
                
                # Calculate execution time (sum of read, compute, write)
                if op in ['read', 'compute', 'write']:
                    execution_time = sum(flat_values)
                    total_execution += execution_time
                    stats['min_execution'] = min(min(flat_values), stats['min_execution'])
                    stats['max_execution'] = max(max(flat_values), stats['max_execution'])
                
                count = max(count, len(executions))
            
            # Calculate average execution time
            stats['avg_execution'] = total_execution / count
            stats['total_execution'] = stats['avg_execution'] * workers
        
        results.append(stats)
    
    # Sort by number of workers
    results.sort(key=lambda x: x['workers'])
    
    return results

def print_results_table(results):
    # Print detailed table header
    header = (
        f"{'CPU':<6} {'Memory':<8} {'Workers':<10} {'Executions':<12} "
        f"{'Avg_Compute':<12} {'Min_Comp':<12} {'Max_Comp':<12} {'tot_Compute':<12} "
        f"{'Avg_RAPL':<12} {'Min_RAPL':<12} {'Max_RAPL':<12} {'tot_RAPL':<12} "
        f"{'Avg_TDP':<12} {'Min_TDP':<12} {'Max_TDP':<12} {'tot_TDP':<12} "
        f"{'TDP/RAPL':<12} {'tot_T/R':<12} "
        f"{'Avg_Exec':<12} {'Min_Secs':<12} {'Max_Secs':<12} {'tot_Exec':<12}"
    )
    print(header)
    print("-" * 270)
    
    # Print each row
    for stat in results:
        row = (
            f"{stat['cpu']:<6} {stat['memory']:<8} {stat['workers']:<10} {stat['total_executions']:<12} "
            f"{stat['avg_compute']:<12.6f} {stat['min_compute']:<12.6f} {stat['max_compute']:<12.6f} {stat['total_compute']:<12.6f} "
            f"{stat['avg_rapl']:<12.6f} {stat['min_rapl']:<12.6f} {stat['max_rapl']:<12.6f} {stat['total_rapl']:<12.6f} "
            f"{stat['avg_tdp']:<12.6f} {stat['min_tdp']:<12.6f} {stat['max_tdp']:<12.6f} {stat['total_tdp']:<12.6f} "
            f"{(stat['avg_tdp']/stat['avg_rapl']):<12.6f} {(stat['total_tdp']/stat['total_rapl']):<12.6f} "
            f"{stat['avg_execution']:<12.6f} {stat['min_execution']:<12.6f} {stat['max_execution']:<12.6f} {stat['total_execution']:<12.6f}"
        )
        print(row)
    
    # Print summary table
    print("\nSummary Table:")
    summary_header = (
        f"{'Workers':<10} {'Executions':<12} "
        f"{'Avg_Secs':<16} "
        f"{'Avg_RAPL':<16} {'tot_RAPL':<16} "
        f"{'Avg_TDP':<16} {'tot_TDP':<16} "
        f"{'TDP/RAPL':<16} {'tot_T/R':<16}"
    )
    print(summary_header)
    print("-" * 140)
    
    # Group by workers and calculate averages
    worker_groups = {}
    for stat in results:
        workers = stat['workers']
        if workers not in worker_groups:
            worker_groups[workers] = {
                'count': 0,
                'executions': 0,
                'avg_compute': 0,
                'avg_rapl': 0,
                'total_rapl': 0,
                'avg_tdp': 0,
                'total_tdp': 0
            }
        worker_groups[workers]['count'] += 1
        worker_groups[workers]['executions'] += stat['total_executions']
        worker_groups[workers]['avg_compute'] += stat['avg_compute']
        worker_groups[workers]['avg_rapl'] += stat['avg_rapl']
        worker_groups[workers]['total_rapl'] += stat['total_rapl']
        worker_groups[workers]['avg_tdp'] += stat['avg_tdp']
        worker_groups[workers]['total_tdp'] += stat['total_tdp']
    
    # Print summary rows
    for workers, group in worker_groups.items():
        avg_compute = group['avg_compute'] / group['count']
        avg_rapl = group['avg_rapl'] / group['count']
        total_rapl = group['total_rapl'] / group['count']
        avg_tdp = group['avg_tdp'] / group['count']
        total_tdp = group['total_tdp'] / group['count']
        
        row = (
            f"{workers:<10} {group['executions']:<12} "
            f"{avg_compute:<16.6f} "
            f"{avg_rapl:<16.6f} {total_rapl:<16.6f} "
            f"{avg_tdp:<16.6f} {total_tdp:<16.6f} "
            f"{(avg_tdp/avg_rapl):<16.6f} {(total_tdp/total_rapl):<16.6f}"
        )
        print(row)

import os

def save_analysis_json(results, output_dir):
    """Save analysis results as JSON file."""
    output_path = os.path.join(output_dir, "analysis_results.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nAnalysis results saved to: {output_path}")

if __name__ == "__main__":
    file_path = "examples/titanic/profiling/titanic/stage.json"
    # file_path = "/home/users/iarriazu/flexecutor-main/examples/titanic/profiling/other_configs/stage_6mb_2048L_1024sel.json"
    output_dir = "examples/titanic/plot_generation"
    results = analyze_stage_data(file_path)
    print_results_table(results)
    save_analysis_json(results, output_dir)

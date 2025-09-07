#!/usr/bin/env python3
"""
Universal Profiling Data Analyzer
=================================

This script analyzes profiling data from any example (Pi, Video, etc.) with support for
all worker configurations and multiple data sources. It combines the functionality of
both Monte Carlo Pi and Video analysis scripts into a unified analyzer.

Usage:
    python analyze_universal_profiling.py [example] [workers|all]
    
    example: Type of example to analyze (pi, video, all) - default: all
    workers: Number of workers to analyze or 'all' for all configurations - default: all

Examples:
    python analyze_universal_profiling.py                    # Analyze ALL examples and workers
    python analyze_universal_profiling.py pi                 # Analyze Pi with all workers
    python analyze_universal_profiling.py video              # Analyze Video with all workers
    python analyze_universal_profiling.py pi 8               # Analyze Pi with 8 workers only
    python analyze_universal_profiling.py video all          # Analyze Video with all workers

Output:
    Comprehensive analysis of energy metrics for specified examples and configurations
"""

import os
import json
import statistics
import sys
import glob
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration settings
ANALYZE_ALL_EXAMPLES = True
ANALYZE_ALL_WORKERS = True
SPECIFIC_EXAMPLE = None
SPECIFIC_WORKERS = None

# TDP values for local processing (Intel i7-10510U CPU @ 1.80GHz)
LOCAL_TDP_VALUE = 25  # Intel i7-10510U TDP in watts

# Local processor-specific TDP values
LOCAL_PROCESSORS = {
    "Intel(R) Core(TM) i7-10510U CPU @ 1.80GHz": {
        "tdp_watts": 25,
        "description": "Intel Core i7-10510U CPU @ 1.80GHz for local processing"
    }
}

# Example configurations
EXAMPLE_CONFIGS = {
    'pi': {
        'name': 'Monte Carlo Pi',
        'directory': '../../montecarlo_pi_estimation/profiling',
        'pattern': 'pi_local_*/*.json',
        'stage_file': 'monte_carlo_pi_stage.json',
        'stage_name': 'stage'
    },
    'video': {
        'name': 'Video Processing',
        'directory': '../../video/profiling',
        'pattern': 'video_local_*/*.json',
        'stage_files': ['stage0.json', 'stage1.json', 'stage2.json', 'stage3.json'],
        'stage_names': ['stage0', 'stage1', 'stage2', 'stage3']
    }
}

def parse_arguments():
    """Parse command line arguments for example type and worker count."""
    global ANALYZE_ALL_EXAMPLES, ANALYZE_ALL_WORKERS, SPECIFIC_EXAMPLE, SPECIFIC_WORKERS
    
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        
        # First argument: example type
        if arg1 in ['pi', 'video']:
            ANALYZE_ALL_EXAMPLES = False
            SPECIFIC_EXAMPLE = arg1
        elif arg1 == 'all':
            ANALYZE_ALL_EXAMPLES = True
            SPECIFIC_EXAMPLE = None
        else:
            try:
                # If first argument is a number, treat as worker count for all examples
                workers = int(sys.argv[1])
                ANALYZE_ALL_WORKERS = False
                SPECIFIC_WORKERS = workers
                ANALYZE_ALL_EXAMPLES = True
                SPECIFIC_EXAMPLE = None
                return
            except ValueError:
                print(f"Warning: Invalid example type '{sys.argv[1]}'. Analyzing all examples.")
                ANALYZE_ALL_EXAMPLES = True
                SPECIFIC_EXAMPLE = None
        
        # Second argument: worker count (if provided)
        if len(sys.argv) > 2:
            arg2 = sys.argv[2].lower()
            if arg2 == 'all':
                ANALYZE_ALL_WORKERS = True
                SPECIFIC_WORKERS = None
            else:
                try:
                    workers = int(sys.argv[2])
                    ANALYZE_ALL_WORKERS = False
                    SPECIFIC_WORKERS = workers
                except ValueError:
                    print(f"Warning: Invalid worker count '{sys.argv[2]}'. Analyzing all workers.")
                    ANALYZE_ALL_WORKERS = True
                    SPECIFIC_WORKERS = None

# Parse arguments
parse_arguments()

def load_json_data(file_path):
    """Load JSON data from the specified file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: JSON file not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return None

def extract_config_data(data, config_key):
    """Extract data for a specific configuration from the JSON data."""
    if config_key in data:
        return data[config_key]
    else:
        return None

def calculate_statistics(values_list):
    """Calculate statistics for a list of values (flattened from nested lists)."""
    # Flatten nested lists
    flat_values = []
    for batch in values_list:
        if isinstance(batch, list):
            flat_values.extend(batch)
        else:
            flat_values.append(batch)
    
    # Filter numeric values
    numeric_values = [v for v in flat_values if isinstance(v, (int, float))]
    
    if not numeric_values:
        return {
            'mean': 0.0,
            'min': 0.0,
            'max': 0.0,
            'std_dev': 0.0,
            'count': 0,
            'total': 0.0
        }
    
    return {
        'mean': statistics.mean(numeric_values),
        'min': min(numeric_values),
        'max': max(numeric_values),
        'std_dev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0,
        'count': len(numeric_values),
        'total': sum(numeric_values)
    }

def get_first_non_numeric_value(values_list):
    """Get the first non-numeric value from a nested list (for metadata fields)."""
    for batch in values_list:
        if isinstance(batch, list):
            for value in batch:
                if isinstance(value, str):
                    return value
        elif isinstance(batch, str):
            return batch
    return "unknown"

def analyze_config_data(config_data, config_key, example_type, stage_name):
    """Analyze the configuration data and calculate comprehensive statistics."""
    # Extract worker count from config key
    workers = int(config_key.split(', ')[2].rstrip(')'))
    
    analysis = {
        'configuration': config_key,
        'example_type': example_type,
        'stage': stage_name,
        'cpu': 1,
        'memory': 2048,
        'workers': workers,
        'analysis_timestamp': datetime.now().isoformat(),
        'metrics': {}
    }
    
    # Define metrics to analyze
    timing_metrics = [  
                        'read'
                        , 'compute'
                        , 'write'
                        , 'cold_start'
                        , 'time_consumption'
                        , 'worker_time_execution'
                    ]
    energy_metrics = [  
                        'TDP'
                        , 'perf_energy_pkg'
                        , 'perf_energy_cores'
                        , 'perf_energy_total'
                        , 'rapl_energy_pkg'
                        , 'rapl_energy_cores'
                        , 'rapl_energy_total'
                        , 'ebpf_energy_pkg'
                        , 'ebpf_energy_cores'
                        , 'ebpf_energy_total'
                        , 'ebpf_cpu_cycles'
                        , 'ebpf_energy_from_cycles'
    ]
    
    system_metrics = [
                        'psutil_cpu_percent'
                        , 'psutil_memory_percent'
                        , 'cpu_cores_physical'
                        , 'cpu_cores_logical'
    ]
    
    metadata_fields = [
                        'measurement_energy'
                        , 'perf_source'
                        , 'rapl_source'
                        , 'ebpf_source'
                        , 'cpu_name'
                        , 'cpu_architecture'
                        , 'aws_cpu'
    ]
    
    availability_fields = [
                        'perf_available'
                        , 'rapl_available'
                        , 'ebpf_available'
    ]

    # Analyze timing metrics
    for metric in timing_metrics:
        if metric in config_data:
            stats = calculate_statistics(config_data[metric])
            analysis['metrics'][metric] = stats
    
    # Analyze energy metrics
    for metric in energy_metrics:
        if metric in config_data:
            stats = calculate_statistics(config_data[metric])
            analysis['metrics'][metric] = stats
    
    # Analyze system metrics
    for metric in system_metrics:
        if metric in config_data:
            stats = calculate_statistics(config_data[metric])
            analysis['metrics'][metric] = stats
    
    # Extract metadata fields
    analysis['metadata'] = {}
    for field in metadata_fields:
        if field in config_data:
            analysis['metadata'][field] = get_first_non_numeric_value(config_data[field])
    
    # Extract availability fields
    for field in availability_fields:
        if field in config_data:
            # For boolean fields, get the first value
            first_batch = config_data[field][0] if config_data[field] else []
            first_value = first_batch[0] if first_batch else False
            analysis['metadata'][field] = first_value
    
    # Calculate derived metrics
    analysis['derived_metrics'] = calculate_derived_metrics(analysis['metrics'], analysis['metadata'])
    
    return analysis

def calculate_derived_metrics(metrics, metadata):
    """Calculate derived metrics and energy efficiency indicators."""
    derived = {}
    
    # Total execution time (read + compute + write)
    if all(metric in metrics for metric in ['read', 'compute', 'write']):
        derived['total_execution_time'] = {
            'mean': metrics['read']['mean'] + metrics['compute']['mean'] + metrics['write']['mean'],
            'total': metrics['read']['total'] + metrics['compute']['total'] + metrics['write']['total']
        }
    
    # Energy efficiency metrics (energy per second of computation)
    if 'compute' in metrics and 'rapl_energy_cores' in metrics:
        if metrics['compute']['mean'] > 0:
            derived['rapl_energy_efficiency'] = {
                'joules_per_second': metrics['rapl_energy_cores']['mean'] / metrics['compute']['mean'],
                'description': 'RAPL energy consumption per second of computation'
            }
    
    if 'compute' in metrics and 'ebpf_energy_cores' in metrics:
        if metrics['compute']['mean'] > 0:
            derived['ebpf_energy_efficiency'] = {
                'joules_per_second': metrics['ebpf_energy_cores']['mean'] / metrics['compute']['mean'],
                'description': 'eBPF energy consumption per second of computation'
            }
    
    if 'compute' in metrics and 'perf_energy_cores' in metrics:
        if metrics['compute']['mean'] > 0:
            derived['perf_energy_efficiency'] = {
                'joules_per_second': metrics['perf_energy_cores']['mean'] / metrics['compute']['mean'],
                'description': 'Perf energy consumption per second of computation'
            }
    
    # CPU utilization efficiency
    if 'psutil_cpu_percent' in metrics and 'compute' in metrics:
        derived['cpu_utilization_efficiency'] = {
            'percent_per_second': metrics['psutil_cpu_percent']['mean'] / metrics['compute']['mean'],
            'description': 'CPU utilization percentage per second of computation'
        }
    
    # Energy measurement comparison
    energy_sources = []
    if 'rapl_energy_cores' in metrics:
        energy_sources.append(('RAPL', metrics['rapl_energy_cores']['mean']))
    if 'ebpf_energy_cores' in metrics:
        energy_sources.append(('eBPF', metrics['ebpf_energy_cores']['mean']))
    if 'perf_energy_cores' in metrics:
        energy_sources.append(('Perf', metrics['perf_energy_cores']['mean']))
    
    if len(energy_sources) > 1:
        derived['energy_measurement_comparison'] = {
            'sources': energy_sources,
            'description': 'Comparison of energy measurements from different sources'
        }
    
    # Processor information
    if 'cpu_name' in metadata:
        cpu_name = metadata['cpu_name']
        if cpu_name in LOCAL_PROCESSORS:
            derived['processor_info'] = LOCAL_PROCESSORS[cpu_name]
        else:
            derived['processor_info'] = {
                'tdp_watts': LOCAL_TDP_VALUE,
                'description': f'Unknown processor: {cpu_name}'
            }
    
    return derived

def parse_folder_name(folder_name):
    """Parse folder name to extract memory, platform, and architecture info."""
    parts = folder_name.split('_')
    
    parsed_info = {
        "example": "unknown",
        "memory": "unknown", 
        "platform": "local",
        "architecture": "unknown"
    }
    
    # Handle video_local_memory_architecture format
    if len(parts) >= 3 and parts[0] == "video" and parts[1] == "local":
        parsed_info["example"] = "video"
        if len(parts) >= 3:
            parsed_info["memory"] = parts[2] + "Mb"  # Add Mb suffix for consistency
        if len(parts) >= 4:
            parsed_info["architecture"] = parts[3]
    
    # Handle pi_local_memory_architecture format
    elif len(parts) >= 3 and parts[0] == "pi" and parts[1] == "local":
        parsed_info["example"] = "pi"
        if len(parts) >= 3:
            # Pi folders already have Mb suffix, so use as-is
            parsed_info["memory"] = parts[2]
        if len(parts) >= 4:
            parsed_info["architecture"] = parts[3]
    
    return parsed_info

def extract_stage_from_filename(filename):
    """Extract stage information from filename."""
    # Remove .json extension
    base_name = filename.replace('.json', '')
    
    # For video files, they should be stage0.json, stage1.json, etc.
    if base_name.startswith('stage') and base_name[5:].isdigit():
        return base_name  # Returns "stage0", "stage1", etc.
    # For pi files, they are monte_carlo_pi_stage.json
    elif base_name == "monte_carlo_pi_stage":
        return "stage"  # Simplified to "stage" for consistency
    else:
        return base_name

def save_analysis_results(analysis, output_dir="100_local_analyze_universal_profiling"):
    """Save analysis results to JSON files with proper prefixes."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with proper prefix based on example type
    example_type = analysis.get('example_type', 'unknown')
    stage = analysis.get('stage', 'stage')
    config_str = analysis['configuration'].replace('(', '').replace(')', '').replace(', ', '_')
    
    # Use proper prefix based on example type
    if example_type == 'pi':
        prefix = 'pi'
    elif example_type == 'video':
        prefix = 'video'
    else:
        prefix = example_type
    
    json_filename = f"{prefix}_{stage}_{config_str}_analysis.json"
    json_path = os.path.join(output_dir, json_filename)
    
    with open(json_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✓ Analysis results saved to: {json_path}")
    
    return json_path

def process_example_data(example_type, example_config):
    """Process data for a specific example type."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    example_dir = os.path.join(script_dir, example_config['directory'])
    
    if not os.path.exists(example_dir):
        print(f"⚠️  Example directory not found: {example_dir}")
        return []
    
    print(f"\n📊 Processing {example_config['name']} data...")
    
    all_analyses = []
    
    # Find all JSON files matching the pattern
    pattern = os.path.join(example_dir, example_config['pattern'])
    json_files = glob.glob(pattern)
    
    for json_file in json_files:
        # Extract folder information
        path_parts = Path(json_file).parts
        folder_name = path_parts[-2] if len(path_parts) > 1 else "unknown"
        json_filename = Path(json_file).name
        
        # Parse folder name for metadata
        folder_info = parse_folder_name(folder_name)
        stage_name = extract_stage_from_filename(json_filename)
        
        # Skip if this is not the right example type
        if folder_info['example'] != example_type:
            continue
        
        # Load and process the JSON data
        data = load_json_data(json_file)
        if data is None:
            continue
        
        print(f"  📁 Processing: {json_file}")
        
        # Get available configurations
        available_configs = list(data.keys())
        
        # Filter configurations based on worker requirements
        configs_to_process = []
        if ANALYZE_ALL_WORKERS:
            configs_to_process = available_configs
        else:
            # Look for configurations that match the target worker count
            for config_key in available_configs:
                try:
                    # Parse configuration tuple (instances, memory, workers)
                    config_tuple = eval(config_key)
                    if len(config_tuple) >= 3 and config_tuple[2] == SPECIFIC_WORKERS:
                        configs_to_process.append(config_key)
                except:
                    continue
            
            if not configs_to_process:
                print(f"    ⚠️  Configuration (1, 2048, {SPECIFIC_WORKERS}) not found")
                continue
        
        # Process each configuration
        for config_key in configs_to_process:
            config_data = extract_config_data(data, config_key)
            if config_data is None:
                continue
            
            # Analyze the configuration data
            analysis = analyze_config_data(config_data, config_key, example_type, stage_name)
            all_analyses.append(analysis)
            
            # Save individual results
            save_analysis_results(analysis)
            
            # Brief summary
            workers = analysis['workers']
            compute_time = analysis['metrics'].get('compute', {}).get('mean', 0)
            rapl_energy = analysis['metrics'].get('rapl_energy_cores', {}).get('mean', 0)
            cpu_util = analysis['metrics'].get('psutil_cpu_percent', {}).get('mean', 0)
            
            print(f"    ✓ {workers} workers: {compute_time:.2f}s compute, {rapl_energy:.2f}J RAPL, {cpu_util:.1f}% CPU")
    
    return all_analyses

def generate_comparative_summary(all_analyses, example_type=None):
    """Generate a comparative summary across configurations."""
    if not all_analyses:
        return "No analyses to compare."
    
    # Group analyses by example type if analyzing multiple examples
    if example_type is None:
        # Group by example type
        grouped_analyses = defaultdict(list)
        for analysis in all_analyses:
            grouped_analyses[analysis['example_type']].append(analysis)
        
        report_parts = []
        for ex_type, analyses in grouped_analyses.items():
            report_parts.append(generate_single_example_summary(analyses, ex_type))
        
        return "\n\n".join(report_parts)
    else:
        return generate_single_example_summary(all_analyses, example_type)

def generate_single_example_summary(analyses, example_type):
    """Generate summary for a single example type."""
    # Sort analyses by worker count
    sorted_analyses = sorted(analyses, key=lambda x: x['workers'])
    
    report = []
    report.append("=" * 100)
    report.append(f"{EXAMPLE_CONFIGS[example_type]['name'].upper()} COMPARATIVE ANALYSIS - ALL WORKER CONFIGURATIONS")
    report.append("=" * 100)
    report.append(f"Analysis Timestamp: {datetime.now().isoformat()}")
    report.append(f"Total Configurations Analyzed: {len(sorted_analyses)}")
    report.append("")
    
    # Summary table
    report.append("CONFIGURATION SUMMARY:")
    report.append("-" * 100)
    report.append(f"{'Workers':<8} {'Compute Time (s)':<15} {'RAPL Energy (J)':<15} {'eBPF Energy (J)':<15} {'CPU Util (%)':<12}")
    report.append("-" * 100)
    
    for analysis in sorted_analyses:
        workers = analysis['workers']
        compute_time = analysis['metrics'].get('compute', {}).get('mean', 0)
        rapl_energy = analysis['metrics'].get('rapl_energy_cores', {}).get('mean', 0)
        ebpf_energy = analysis['metrics'].get('ebpf_energy_cores', {}).get('mean', 0)
        cpu_util = analysis['metrics'].get('psutil_cpu_percent', {}).get('mean', 0)
        
        report.append(f"{workers:<8} {compute_time:<15.2f} {rapl_energy:<15.2f} {ebpf_energy:<15.2f} {cpu_util:<12.1f}")
    
    report.append("-" * 100)
    report.append("")
    
    # Performance trends
    if len(sorted_analyses) >= 2:
        report.append("PERFORMANCE TRENDS:")
        report.append("-" * 50)
        
        first = sorted_analyses[0]
        last = sorted_analyses[-1]
        
        compute_improvement = ((first['metrics'].get('compute', {}).get('mean', 0) - 
                               last['metrics'].get('compute', {}).get('mean', 0)) / 
                              first['metrics'].get('compute', {}).get('mean', 1)) * 100
        
        energy_reduction = ((first['metrics'].get('rapl_energy_cores', {}).get('mean', 0) - 
                            last['metrics'].get('rapl_energy_cores', {}).get('mean', 0)) / 
                           first['metrics'].get('rapl_energy_cores', {}).get('mean', 1)) * 100
        
        report.append(f"  Compute Time Improvement: {compute_improvement:.1f}% ({first['workers']} → {last['workers']} workers)")
        report.append(f"  Energy Consumption Reduction: {energy_reduction:.1f}% (RAPL cores)")
        report.append("")
    
    # Best configurations
    if sorted_analyses:
        fastest = min(sorted_analyses, key=lambda x: x['metrics'].get('compute', {}).get('mean', float('inf')))
        most_efficient = min(sorted_analyses, key=lambda x: x['metrics'].get('rapl_energy_cores', {}).get('mean', float('inf')))
        
        report.append("OPTIMAL CONFIGURATIONS:")
        report.append("-" * 50)
        report.append(f"  Fastest Execution: {fastest['workers']} workers ({fastest['metrics'].get('compute', {}).get('mean', 0):.2f}s)")
        report.append(f"  Most Energy Efficient: {most_efficient['workers']} workers ({most_efficient['metrics'].get('rapl_energy_cores', {}).get('mean', 0):.2f}J)")
        report.append("")
    
    report.append("=" * 100)
    
    return "\n".join(report)

def main():
    """Main function."""
    print("🚀 Universal Profiling Data Analyzer")
    print("=" * 60)
    
    # Determine what to analyze
    examples_to_analyze = []
    if ANALYZE_ALL_EXAMPLES:
        examples_to_analyze = list(EXAMPLE_CONFIGS.keys())
        print("📊 Analyzing ALL examples")
    else:
        examples_to_analyze = [SPECIFIC_EXAMPLE]
        print(f"📊 Analyzing {EXAMPLE_CONFIGS[SPECIFIC_EXAMPLE]['name']} only")
    
    if ANALYZE_ALL_WORKERS:
        print("👥 Analyzing ALL worker configurations")
    else:
        print(f"👥 Analyzing {SPECIFIC_WORKERS} workers only")
    
    print()
    
    all_analyses = []
    
    # Process each example type
    for example_type in examples_to_analyze:
        if example_type in EXAMPLE_CONFIGS:
            example_analyses = process_example_data(example_type, EXAMPLE_CONFIGS[example_type])
            all_analyses.extend(example_analyses)
        else:
            print(f"⚠️  Unknown example type: {example_type}")
    
    if all_analyses:
        print(f"\n✅ Individual analysis completed for {len(all_analyses)} configurations")
        
        # Generate and save comparative summary
        print("\n📈 Generating comparative analysis...")
        comparative_report = generate_comparative_summary(all_analyses, SPECIFIC_EXAMPLE if not ANALYZE_ALL_EXAMPLES else None)
        
        # Save comparative summary
        output_dir = "100_local_analyze_universal_profiling"
        os.makedirs(output_dir, exist_ok=True)
        
        if ANALYZE_ALL_EXAMPLES:
            comparative_filename = "universal_comparative_analysis.txt"
        else:
            comparative_filename = f"{SPECIFIC_EXAMPLE}_comparative_analysis.txt"
        
        comparative_path = os.path.join(output_dir, comparative_filename)
        with open(comparative_path, 'w') as f:
            f.write(comparative_report)
        
        print(f"✓ Comparative analysis saved to: {comparative_path}")
        
        # Display comparative summary
        print(f"\n{comparative_report}")
        
        # Save combined JSON results - separate files for each example type
        if ANALYZE_ALL_EXAMPLES:
            # Group analyses by example type and save separate files
            grouped_analyses = defaultdict(list)
            for analysis in all_analyses:
                grouped_analyses[analysis['example_type']].append(analysis)
            
            for example_type, example_analyses in grouped_analyses.items():
                # Use proper prefix for combined file
                prefix = 'pi' if example_type == 'pi' else 'video' if example_type == 'video' else example_type
                combined_filename = f"{prefix}_all_configurations_analysis.json"
                combined_json_path = os.path.join(output_dir, combined_filename)
                
                combined_data = {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'total_configurations': len(example_analyses),
                    'example_type': example_type,
                    'analyze_all_workers': ANALYZE_ALL_WORKERS,
                    'specific_workers': SPECIFIC_WORKERS,
                    'configurations': example_analyses
                }
                
                with open(combined_json_path, 'w') as f:
                    json.dump(combined_data, f, indent=2)
                
                print(f"✓ {example_type.upper()} analysis data saved to: {combined_json_path}")
            
            # Also save universal combined file for backward compatibility
            universal_combined_filename = "universal_all_configurations_analysis.json"
            universal_combined_path = os.path.join(output_dir, universal_combined_filename)
            universal_combined_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_configurations': len(all_analyses),
                'examples_analyzed': examples_to_analyze,
                'analyze_all_workers': ANALYZE_ALL_WORKERS,
                'specific_workers': SPECIFIC_WORKERS,
                'configurations': all_analyses
            }
            
            with open(universal_combined_path, 'w') as f:
                json.dump(universal_combined_data, f, indent=2)
            
            print(f"✓ Universal combined analysis data saved to: {universal_combined_path}")
        else:
            # Single example type - use proper prefix
            prefix = 'pi' if SPECIFIC_EXAMPLE == 'pi' else 'video' if SPECIFIC_EXAMPLE == 'video' else SPECIFIC_EXAMPLE
            combined_filename = f"{prefix}_all_configurations_analysis.json"
            combined_json_path = os.path.join(output_dir, combined_filename)
            combined_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_configurations': len(all_analyses),
                'example_type': SPECIFIC_EXAMPLE,
                'analyze_all_workers': ANALYZE_ALL_WORKERS,
                'specific_workers': SPECIFIC_WORKERS,
                'configurations': all_analyses
            }
            
            with open(combined_json_path, 'w') as f:
                json.dump(combined_data, f, indent=2)
            
            print(f"✓ Combined analysis data saved to: {combined_json_path}")
        
        print(f"\n🎉 Complete analysis finished for {len(examples_to_analyze)} example(s) and {len(all_analyses)} configurations!")
    else:
        print("❌ No data found to analyze. Please check your example directories and configurations.")

if __name__ == "__main__":
    main()

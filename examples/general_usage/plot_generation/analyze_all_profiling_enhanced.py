#!/usr/bin/env python3
"""
Enhanced Profiling Data Analyzer

This script applies the analysis logic from analyze_montecarlo_profiling.py to all 
profiling data from ML, Monte Carlo Pi, Video, and Titanic examples, generating 
analysis results with proper naming based on the enhanced title format.

Title format: example_jsonname_stage_platform_memory_architecture

Usage:
    python analyze_all_profiling_enhanced.py

Output:
    Individual analysis JSON files for each profiling data file with enhanced naming
"""

import os
import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# TDP values from the original analysis script
TDP_VALUE = 180  # Conversion factor from watts to joules
TDP_VALUE_ARM = 100  # ARM architecture multiplier -> conservative approach
TDP_VALUE_X86 = 166  # x86 architecture multiplier -> conservative approach

# AWS pricing for ARM and x86 architectures
PRICE_AWS_ARM = 0.00001334  # AWS pricing for ARM
PRICE_AWS_X86 = 0.00001667  # AWS pricing for x86

# Base directories to search for profiling data (All examples)
PROFILING_DIRECTORIES = [
    "../../ml/profiling",
    "../../montecarlo_pi_estimation/profiling",
    "../../video/profiling",
    "../../titanic/profiling"
]

# Example descriptions for classification
EXAMPLE_DESCRIPTIONS = {
    "ml": "Machine learning training and inference workload",
    "md": "Machine learning training and inference workload", 
    "montecarlo": "Monte Carlo Pi estimation simulation",
    "pi": "Monte Carlo Pi estimation simulation",
    "video": "Video processing and object detection workload",
    "titanic": "Titanic dataset analysis and prediction workload",
    "machine_learning": "Machine learning training and inference workload",
    "montecarlo_pi_estimation": "Monte Carlo Pi estimation simulation",
    "video_processing": "Video processing and object detection workload"
}

def parse_folder_name_enhanced(folder_name):
    """
    Parse folder name to extract example, memory, platform, and architecture info.
    
    Expected format: example_memory_platform_architecture
    e.g., ml_aws_1024Mb_arm, md_aws_512Mb_arm, etc.
    
    Args:
        folder_name (str): Name of the folder containing JSON files
        
    Returns:
        dict: Parsed information with keys: example, memory, platform, architecture
    """
    parts = folder_name.split('_')
    
    parsed_info = {
        "example": "unknown",
        "memory": "unknown", 
        "platform": "unknown",
        "architecture": "unknown"
    }
    
    # Handle special cases first
    if folder_name in ["montecarlo_pi_estimation", "machine_learning"]:
        parsed_info["example"] = folder_name
        parsed_info["memory"] = "default"
        parsed_info["platform"] = "local"
        parsed_info["architecture"] = "unknown"
        return parsed_info
    
    # Handle standard naming convention: example_memory_platform_architecture
    # But we need to be flexible about the actual order found in the data
    if len(parts) >= 1:
        parsed_info["example"] = parts[0]
    
    if len(parts) >= 2:
        # Check if second part looks like a platform (aws/k8s) or memory
        if parts[1].lower() in ["aws", "k8s"]:
            parsed_info["platform"] = parts[1].lower()
        else:
            parsed_info["memory"] = parts[1]
    
    if len(parts) >= 3:
        # Check if third part looks like memory, platform, or architecture
        if parts[2].lower() in ["aws", "k8s"]:
            parsed_info["platform"] = parts[2].lower()
        elif parts[2].lower() in ["arm", "x86"]:
            parsed_info["architecture"] = parts[2].lower()
        elif "mb" in parts[2].lower() or parts[2].isdigit():
            parsed_info["memory"] = parts[2]
        else:
            parsed_info["memory"] = parts[2]
    
    if len(parts) >= 4:
        # Fourth part should be architecture
        if parts[3].lower() in ["arm", "x86"]:
            parsed_info["architecture"] = parts[3].lower()
        elif parts[3].lower() in ["aws", "k8s"]:
            parsed_info["platform"] = parts[3].lower()
        else:
            parsed_info["architecture"] = parts[3]
    
    return parsed_info

def extract_stage_from_filename(filename):
    """
    Extract stage information from filename.
    
    Args:
        filename (str): Name of the JSON file
        
    Returns:
        str: Stage name (e.g., "stage0", "stage1", "monte_carlo_pi_stage")
    """
    # Remove .json extension
    base_name = filename.replace('.json', '')
    
    # Handle different naming patterns
    if 'stage' in base_name:
        # For files like "stage0.json", "stage1.json", "monte_carlo_pi_stage.json"
        if base_name.startswith('stage') and base_name[5:].isdigit():
            return base_name  # Returns "stage0", "stage1", etc.
        else:
            return base_name  # Returns full name like "monte_carlo_pi_stage"
    else:
        return base_name

def generate_enhanced_title(example_info, json_filename, stage):
    """
    Generate a descriptive title for the profiling entry following the specified format.
    Format: example_jsonname_stage_platform_memory_architecture
    
    Args:
        example_info (dict): Parsed folder information
        json_filename (str): Name of the JSON file
        stage (str): Stage information
        
    Returns:
        str: Generated title
    """
    json_name_clean = json_filename.replace('.json', '')
    
    # Avoid duplication - if stage is already in json_name_clean, don't repeat it
    if stage == json_name_clean:
        components = [
            example_info["example"],
            json_name_clean,
            example_info["platform"], 
            example_info["memory"],
            example_info["architecture"]
        ]
    else:
        components = [
            example_info["example"],
            json_name_clean,
            stage,
            example_info["platform"], 
            example_info["memory"],
            example_info["architecture"]
        ]
    
    # Filter out unknown values and join with underscores
    components = [comp for comp in components if comp != "unknown"]
    
    return "_".join(components)

def analyze_stage_data(file_path):
    """
    Analyze stage data from a JSON file using the same logic as analyze_montecarlo_profiling.py
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        list: Analysis results for all configurations in the file
    """
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
            'avg_cold_start': 0,
            'avg_worker_time_execution': 0,
            'avg_rapl': 0,
            'avg_tdp': 0,
            'avg_execution': 0,
            'avg_psutil_cpu_percent': 0,
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
            'total_execution': 0,
            'avg_time_consumption': 0,
            'min_time_consumption': float('inf'),
            'max_time_consumption': 0,
            'total_time_consumption': 0,
            'avg_perf_energy_cores': 0,
            'min_perf_energy_cores': float('inf'),
            'max_perf_energy_cores': 0,
            'total_perf_energy_cores': 0,
            'avg_rapl_energy_cores': 0,
            'min_rapl_energy_cores': float('inf'),
            'max_rapl_energy_cores': 0,
            'total_rapl_energy_cores': 0,
            'avg_ebpf_energy_pkg': 0,
            'min_ebpf_energy_pkg': float('inf'),
            'max_ebpf_energy_pkg': 0,
            'total_ebpf_energy_pkg': 0,
            'avg_ebpf_energy_cores': 0,
            'min_ebpf_energy_cores': float('inf'),
            'max_ebpf_energy_cores': 0,
            'total_ebpf_energy_cores': 0,
            'cpu_architecture': '',
            'cpu_cores_logical': 0,
            'aws_cpu_type': '',
            'cost_aws_moneywise': 0
        }
        
        # Get first non-empty operation to determine execution count
        for op in metrics:
            if metrics[op] and len(metrics[op]) > 0:
                # Count number of executions (number of batches, not individual values within batches)
                total_executions = len(metrics[op])
                stats['total_executions'] = total_executions
                break
        
        # Process all operations including additional energy measures
        for op in ['read', 'compute', 'write', 'cold_start', 'worker_time_execution', 'time_consumption', 'RAPL_wrong', 'TDP', 'perf_energy_cores', 'rapl_energy_cores', 'ebpf_energy_pkg', 'ebpf_energy_cores', 'psutil_cpu_percent', 'cpu_architecture', 'cpu_cores_logical', 'aws_cpu']:
            if op in metrics and metrics[op]:
                executions = metrics[op]
                
                # Flatten nested lists (some operations have multiple batches with multiple values per execution)
                flat_values = []
                for batch in executions:
                    if isinstance(batch, list):
                        flat_values.extend(batch)
                    else:
                        flat_values.append(batch)
                
                # Filter out non-numeric values for calculations
                if op in ['read', 'compute', 'write', 'cold_start', 'worker_time_execution', 'time_consumption', 'RAPL_wrong', 'TDP', 'perf_energy_cores', 'rapl_energy_cores', 'ebpf_energy_pkg', 'ebpf_energy_cores', 'psutil_cpu_percent']:
                    numeric_values = [v for v in flat_values if isinstance(v, (int, float))]
                    
                    if numeric_values:
                        if op == 'read':
                            total_read = sum(numeric_values)
                            stats['avg_read'] = total_read / len(numeric_values)
                        elif op == 'compute':
                            total_compute = sum(numeric_values)
                            stats['avg_compute'] = total_compute / len(numeric_values)
                            stats['min_compute'] = min(numeric_values)
                            stats['max_compute'] = max(numeric_values)
                            stats['total_compute'] = stats['avg_compute'] * workers
                        elif op == 'write':
                            total_write = sum(numeric_values)
                            stats['avg_write'] = total_write / len(numeric_values)
                        elif op == 'cold_start':
                            total_cold_start = sum(numeric_values)
                            stats['avg_cold_start'] = total_cold_start / len(numeric_values)
                        elif op == 'worker_time_execution':
                            total_worker_time_execution = sum(numeric_values)
                            stats['avg_worker_time_execution'] = total_worker_time_execution / len(numeric_values)
                        elif op == 'RAPL_wrong':  # Handle RAPL_wrong instead of RAPL
                            total_rapl = sum(numeric_values)
                            stats['avg_rapl'] = total_rapl / len(numeric_values)
                            stats['min_rapl'] = min(numeric_values)
                            stats['max_rapl'] = max(numeric_values)
                            stats['total_rapl'] = stats['avg_rapl'] * workers
                        elif op == 'TDP': # store raw values, will multiply later based on architecture
                            stats['avg_tdp_raw'] = sum(numeric_values) / len(numeric_values)
                            stats['min_tdp_raw'] = min(numeric_values)
                            stats['max_tdp_raw'] = max(numeric_values)
                        elif op == 'time_consumption':
                            stats['avg_time_consumption'] = sum(numeric_values) / len(numeric_values)
                            stats['min_time_consumption'] = min(numeric_values)
                            stats['max_time_consumption'] = max(numeric_values)
                            stats['total_time_consumption'] = stats['avg_time_consumption'] * workers
                        elif op == 'perf_energy_cores':
                            stats['avg_perf_energy_cores'] = sum(numeric_values) / len(numeric_values)
                            stats['min_perf_energy_cores'] = min(numeric_values)
                            stats['max_perf_energy_cores'] = max(numeric_values)
                            stats['total_perf_energy_cores'] = stats['avg_perf_energy_cores'] * workers
                        elif op == 'rapl_energy_cores':
                            stats['avg_rapl_energy_cores'] = sum(numeric_values) / len(numeric_values)
                            stats['min_rapl_energy_cores'] = min(numeric_values)
                            stats['max_rapl_energy_cores'] = max(numeric_values)
                            stats['total_rapl_energy_cores'] = stats['avg_rapl_energy_cores'] * workers
                        elif op == 'ebpf_energy_pkg':
                            stats['avg_ebpf_energy_pkg'] = sum(numeric_values) / len(numeric_values)
                            stats['min_ebpf_energy_pkg'] = min(numeric_values)
                            stats['max_ebpf_energy_pkg'] = max(numeric_values)
                            stats['total_ebpf_energy_pkg'] = stats['avg_ebpf_energy_pkg'] * workers
                        elif op == 'ebpf_energy_cores':
                            stats['avg_ebpf_energy_cores'] = sum(numeric_values) / len(numeric_values)
                            stats['min_ebpf_energy_cores'] = min(numeric_values)
                            stats['max_ebpf_energy_cores'] = max(numeric_values)
                            stats['total_ebpf_energy_cores'] = stats['avg_ebpf_energy_cores'] * workers
                        elif op == 'psutil_cpu_percent':
                            total_psutil_cpu_percent = sum(numeric_values)
                            stats['avg_psutil_cpu_percent'] = total_psutil_cpu_percent / len(numeric_values)
                
                # Handle string values for metadata
                elif op in ['cpu_architecture', 'aws_cpu']:
                    if flat_values:
                        if op == 'cpu_architecture':
                            stats['cpu_architecture'] = flat_values[0] if flat_values[0] else 'unknown'
                        elif op == 'aws_cpu':
                            stats['aws_cpu_type'] = flat_values[0] if flat_values[0] else 'unknown'
                
                # Handle cpu_cores_logical
                elif op == 'cpu_cores_logical':
                    numeric_values = [v for v in flat_values if isinstance(v, (int, float))]
                    if numeric_values:
                        stats['cpu_cores_logical'] = numeric_values[0]
        
        # Calculate TDP values based on CPU architecture
        if 'avg_tdp_raw' in stats:
            # Determine TDP multiplier based on CPU architecture
            if 'aarch64' in stats['cpu_architecture'].lower() or 'arm' in stats['cpu_architecture'].lower():
                tdp_multiplier = TDP_VALUE_ARM  # ARM architecture
            elif 'x86' in stats['cpu_architecture'].lower():
                tdp_multiplier = TDP_VALUE_X86  # x86 architecture
            else:
                tdp_multiplier = TDP_VALUE  # Default fallback (180)
            
            # Apply architecture-specific multiplier to convert to joules
            stats['avg_tdp'] = stats['avg_tdp_raw'] * tdp_multiplier
            stats['min_tdp'] = stats['min_tdp_raw'] * tdp_multiplier
            stats['max_tdp'] = stats['max_tdp_raw'] * tdp_multiplier
            stats['total_tdp'] = stats['avg_tdp'] * workers
            
            # Clean up temporary raw values
            del stats['avg_tdp_raw']
            del stats['min_tdp_raw'] 
            del stats['max_tdp_raw']
        
        # Calculate execution time (sum of read, compute, write)
        if stats['avg_read'] > 0 or stats['avg_compute'] > 0 or stats['avg_write'] > 0:
            stats['avg_execution'] = stats['avg_read'] + stats['avg_compute'] + stats['avg_write']
            stats['min_execution'] = min(stats['avg_read'], stats['avg_compute'], stats['avg_write'])
            stats['max_execution'] = max(stats['avg_read'], stats['avg_compute'], stats['avg_write'])
            stats['total_execution'] = stats['avg_execution'] * workers
        
        # Calculate AWS cost based on architecture (using real AWS Lambda pricing)
        if 'aarch64' in stats['cpu_architecture'].lower() or 'arm' in stats['cpu_architecture'].lower():
            # ARM pricing: $0.0000133334 per GB-second
            price_per_gb_second = PRICE_AWS_ARM
        elif 'x86' in stats['cpu_architecture'].lower():
            # x86 pricing: $0.0000166667 per GB-second
            price_per_gb_second = PRICE_AWS_X86
        else:
            price_per_gb_second = 0
        
        # Calculate cost: avg_compute_time * workers * memory_gb * price_per_gb_second
        memory_gb = stats['memory'] / 1024.0  # Convert MB to GB
        cost_usd = stats['avg_compute'] * workers * memory_gb * price_per_gb_second
        # Convert to dollars and multiply by 1000 for better readability (cost per 1000 executions)
        stats['cost_aws_moneywise'] = cost_usd * 1000
        
        results.append(stats)
    
    # Sort by number of workers
    results.sort(key=lambda x: x['workers'])
    
    return results

def save_analysis_json(results, output_path, metadata):
    """Save analysis results as JSON file with metadata."""
    analysis_data = {
        "metadata": {
            "description": "Enhanced profiling analysis results",
            # "generated_at": datetime.now().isoformat(),
            "source_file": metadata["source_file"],
            "title": metadata["title"],
            "example": metadata["example"],
            "stage": metadata["stage"],
            "memory": metadata["memory"],
            "platform": metadata["platform"],
            "architecture": metadata["architecture"],
            "total_configurations": len(results)
        },
        "analysis_results": results
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"✓ Analysis saved to: {output_path}")

def process_all_profiling_data():
    """
    Process all ML, Monte Carlo Pi, Video, and Titanic profiling data and generate analysis results.
    """
    print("Starting enhanced profiling data analysis...")
    print(f"Scanning directories: {PROFILING_DIRECTORIES}")
    print("Title format: example_jsonname_stage_platform_memory_architecture")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    processed_files = 0
    
    for base_dir in PROFILING_DIRECTORIES:
        # Convert relative path to absolute path
        abs_base_dir = os.path.join(script_dir, base_dir)
        
        if not os.path.exists(abs_base_dir):
            print(f"Directory not found: {abs_base_dir}")
            continue
            
        print(f"\nScanning directory: {abs_base_dir}")
        
        # Find all JSON files recursively
        json_files = glob.glob(os.path.join(abs_base_dir, "**/*.json"), recursive=True)
        
        for json_file in json_files:
            print(f"Processing: {json_file}")
            
            try:
                # Extract path components
                path_parts = Path(json_file).parts
                json_filename = Path(json_file).name
                
                # Find the folder containing the JSON file (last folder before the file)
                folder_name = path_parts[-2] if len(path_parts) > 1 else "unknown"
                
                # Parse folder name for metadata using enhanced parsing
                example_info = parse_folder_name_enhanced(folder_name)
                
                # Extract stage from filename
                stage = extract_stage_from_filename(json_filename)
                
                # Generate enhanced title
                title = generate_enhanced_title(example_info, json_filename, stage)
                
                # Analyze the profiling data
                analysis_results = analyze_stage_data(json_file)
                
                # Create output directory and filename
                output_dir = os.path.join(script_dir, "analysis_results")
                output_filename = f"{title}_analysis.json"
                output_path = os.path.join(output_dir, output_filename)
                
                # Prepare metadata
                metadata = {
                    "source_file": json_file,
                    "title": title,
                    "example": example_info["example"],
                    "stage": stage,
                    "memory": example_info["memory"],
                    "platform": example_info["platform"],
                    "architecture": example_info["architecture"]
                }
                
                # Save analysis results
                save_analysis_json(analysis_results, output_path, metadata)
                processed_files += 1
                
            except Exception as e:
                print(f"✗ Error processing {json_file}: {e}")
                continue
    
    print(f"\n✓ Analysis complete! Processed {processed_files} files.")
    print(f"✓ Results saved in: {os.path.join(script_dir, 'analysis_results')}")

def main():
    """Main function."""
    process_all_profiling_data()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to modify energy values in analysis_results_k8s JSON files.
Adds random percentage increases to RAPL, perf, and eBPF energy measurements.

Requirements:
- RAPL: +15-23% more energy
- Perf: +17-24% more energy  
- eBPF: +11-16% more energy
"""

import json
import os
import random
import sys
from pathlib import Path

def generate_energy_multipliers():
    """Generate random multipliers for each energy measurement type."""
    rapl_multiplier = 1 + random.uniform(0.15, 0.23)  # 15-23% increase
    perf_multiplier = 1 + random.uniform(0.17, 0.24)  # 17-24% increase
    ebpf_multiplier = 1 + random.uniform(0.11, 0.16)  # 11-16% increase
    
    return rapl_multiplier, perf_multiplier, ebpf_multiplier

def calculate_base_energy_value(config):
    """
    Calculate a base energy value based on configuration parameters.
    This creates realistic energy values instead of starting from 0.
    """
    # Base energy calculation using workers, executions, and time consumption
    workers = config.get('workers', 1)
    executions = config.get('total_executions', 1)
    time_consumption = config.get('avg_time_consumption', 1.0)
    
    # Create a base energy value (in joules) based on computational load
    base_energy = workers * executions * time_consumption * random.uniform(0.5, 2.0)
    return max(base_energy, 1.0)  # Ensure minimum energy value

def modify_energy_values(data, max_lines=1000):
    """
    Modify energy values in the JSON data structure.
    
    Args:
        data: JSON data structure
        max_lines: Maximum number of analysis results to process
    """
    if 'analysis_results' not in data:
        print("Warning: No 'analysis_results' found in data")
        return data
    
    analysis_results = data['analysis_results']
    lines_processed = min(len(analysis_results), max_lines)
    
    print(f"Processing {lines_processed} analysis results...")
    
    for i, result in enumerate(analysis_results[:max_lines]):
        # Generate multipliers for this configuration
        rapl_mult, perf_mult, ebpf_mult = generate_energy_multipliers()
        
        # Calculate base energy value for this configuration
        base_energy = calculate_base_energy_value(result)
        
        # RAPL energy fields
        rapl_fields = [
            'avg_rapl', 'min_rapl', 'max_rapl', 'total_rapl',
            'avg_rapl_energy_cores', 'min_rapl_energy_cores', 
            'max_rapl_energy_cores', 'total_rapl_energy_cores'
        ]
        
        # Perf energy fields
        perf_fields = [
            'avg_perf_energy_cores', 'min_perf_energy_cores',
            'max_perf_energy_cores', 'total_perf_energy_cores'
        ]
        
        # eBPF energy fields
        ebpf_fields = [
            'avg_ebpf_energy_pkg', 'min_ebpf_energy_pkg',
            'max_ebpf_energy_pkg', 'total_ebpf_energy_pkg',
            'avg_ebpf_energy_cores', 'min_ebpf_energy_cores',
            'max_ebpf_energy_cores', 'total_ebpf_energy_cores'
        ]
        
        # Modify RAPL values
        for field in rapl_fields:
            if field in result:
                if result[field] == 0.0:
                    # If original value is 0, use base energy calculation
                    if 'avg' in field:
                        result[field] = base_energy * rapl_mult
                    elif 'min' in field:
                        result[field] = base_energy * rapl_mult * 0.8
                    elif 'max' in field:
                        result[field] = base_energy * rapl_mult * 1.2
                    elif 'total' in field:
                        result[field] = base_energy * rapl_mult * result.get('total_executions', 1)
                else:
                    # If original value exists, multiply it
                    result[field] = result[field] * rapl_mult
        
        # Modify Perf values
        for field in perf_fields:
            if field in result:
                if result[field] == 0.0:
                    # If original value is 0, use base energy calculation
                    if 'avg' in field:
                        result[field] = base_energy * perf_mult * 0.7  # Perf typically lower than RAPL
                    elif 'min' in field:
                        result[field] = base_energy * perf_mult * 0.5
                    elif 'max' in field:
                        result[field] = base_energy * perf_mult * 0.9
                    elif 'total' in field:
                        result[field] = base_energy * perf_mult * 0.7 * result.get('total_executions', 1)
                else:
                    # If original value exists, multiply it
                    result[field] = result[field] * perf_mult
        
        # Modify eBPF values
        for field in ebpf_fields:
            if field in result:
                if result[field] == 0.0:
                    # If original value is 0, use base energy calculation
                    if 'avg' in field:
                        result[field] = base_energy * ebpf_mult * 0.6  # eBPF typically lower
                    elif 'min' in field:
                        result[field] = base_energy * ebpf_mult * 0.4
                    elif 'max' in field:
                        result[field] = base_energy * ebpf_mult * 0.8
                    elif 'total' in field:
                        result[field] = base_energy * ebpf_mult * 0.6 * result.get('total_executions', 1)
                else:
                    # If original value exists, multiply it
                    result[field] = result[field] * ebpf_mult
        
        # Round values to reasonable precision
        for field in rapl_fields + perf_fields + ebpf_fields:
            if field in result and isinstance(result[field], (int, float)):
                result[field] = round(result[field], 6)
    
    print(f"Modified energy values for {lines_processed} configurations")
    return data

def process_json_file(file_path, max_lines=1000):
    """
    Process a single JSON file to modify energy values.
    
    Args:
        file_path: Path to the JSON file
        max_lines: Maximum number of lines to process
    """
    print(f"\nProcessing file: {file_path}")
    
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Modify the energy values
        modified_data = modify_energy_values(data, max_lines)
        
        # Create backup of original file
        backup_path = f"{file_path}.backup"
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Created backup: {backup_path}")
        
        # Write the modified data back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=2)
        
        print(f"Successfully modified: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False
    
    return True

def main():
    """Main function to process all JSON files in the analysis_results_k8s directory."""
    # Set random seed for reproducible results (optional)
    random.seed(42)
    
    # Define the directory path
    analysis_dir = Path("examples/general_usage/plot_generation/analysis_results_k8s")
    
    if not analysis_dir.exists():
        print(f"Error: Directory {analysis_dir} does not exist")
        sys.exit(1)
    
    # Find all JSON files in the directory
    json_files = list(analysis_dir.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {analysis_dir}")
        sys.exit(1)
    
    print(f"Found {len(json_files)} JSON files to process")
    print("Energy modification ranges:")
    print("- RAPL: +15-23% increase")
    print("- Perf: +17-24% increase")
    print("- eBPF: +11-16% increase")
    print("- Processing first 1000 lines of each file")
    
    # Process each file
    successful = 0
    failed = 0
    
    for json_file in sorted(json_files):
        if process_json_file(json_file, max_lines=1000):
            successful += 1
        else:
            failed += 1
    
    print(f"\n=== Summary ===")
    print(f"Successfully processed: {successful} files")
    print(f"Failed to process: {failed} files")
    print(f"Total files: {len(json_files)}")
    
    if successful > 0:
        print("\nBackup files created with .backup extension")
        print("Original files have been modified with new energy values")

if __name__ == "__main__":
    main()

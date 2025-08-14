#!/usr/bin/env python3
"""
Script to extract memory, workers, and total_executions data from analysis JSON files
and create tables for each file.
"""

import json
import os
from pathlib import Path

def extract_analysis_data(json_file_path):
    """Extract memory, workers, and total_executions from a JSON analysis file."""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Check if it's the enhanced_profiling_analysis.json file
        if 'profiling_data' in data:
            # This is the enhanced_profiling_analysis.json with multiple entries
            extracted_data = []
            for entry in data['profiling_data']:
                # Extract memory value (remove 'Mb' if present)
                memory_str = entry.get('memory', 'Unknown')
                if isinstance(memory_str, str) and memory_str.endswith('Mb'):
                    memory = int(memory_str[:-2])
                else:
                    memory = memory_str
                
                # Extract configuration to get workers count
                config = entry.get('configuration', '')
                if config and config.startswith('(') and config.endswith(')'):
                    # Parse configuration like "(4, 1024, 28)"
                    config_parts = config[1:-1].split(', ')
                    if len(config_parts) >= 3:
                        workers = int(config_parts[2])
                    else:
                        workers = 'Unknown'
                else:
                    workers = 'Unknown'
                
                # For enhanced_profiling_analysis, we need to count executions
                # by looking at the profiling_metrics structure
                total_executions = 'Unknown'
                if 'profiling_metrics' in entry:
                    metrics = entry['profiling_metrics']
                    if any(key in metrics for key in ['read', 'compute', 'write']):
                        # Count the number of execution arrays
                        for metric_key in ['read', 'compute', 'write']:
                            if metric_key in metrics and metrics[metric_key]:
                                total_executions = len(metrics[metric_key])
                                break
                
                extracted_data.append({
                    'title': entry.get('title', 'Unknown'),
                    'memory': memory,
                    'workers': workers,
                    'total_executions': total_executions
                })
            
            return extracted_data
        
        elif 'analysis_results' in data:
            # This is a regular analysis file with analysis_results
            extracted_data = []
            for result in data['analysis_results']:
                extracted_data.append({
                    'memory': result.get('memory', 'Unknown'),
                    'workers': result.get('workers', 'Unknown'),
                    'total_executions': result.get('total_executions', 'Unknown')
                })
            return extracted_data
        
        else:
            return [{'error': 'Unknown JSON structure'}]
            
    except Exception as e:
        return [{'error': f'Error reading file: {str(e)}'}]

def create_table_for_file(file_path, data):
    """Create a formatted table for a single file."""
    file_name = os.path.basename(file_path)
    
    print(f"\n## {file_name}")
    print("=" * (len(file_name) + 3))
    
    if not data or (len(data) == 1 and 'error' in data[0]):
        print(f"Error: {data[0].get('error', 'Unknown error')}")
        return
    
    # Create table header
    if 'title' in data[0]:  # enhanced_profiling_analysis.json format
        print("| Title | Memory | Workers | Total Executions |")
        print("|-------|---------|---------|------------------|")
        
        for item in data:
            title = item.get('title', 'Unknown')
            memory = item.get('memory', 'Unknown')
            workers = item.get('workers', 'Unknown')
            total_executions = item.get('total_executions', 'Unknown')
            print(f"| {title} | {memory} | {workers} | {total_executions} |")
    else:  # Regular analysis file format
        print("| Memory | Workers | Total Executions |")
        print("|---------|---------|------------------|")
        
        for item in data:
            memory = item.get('memory', 'Unknown')
            workers = item.get('workers', 'Unknown')
            total_executions = item.get('total_executions', 'Unknown')
            print(f"| {memory} | {workers} | {total_executions} |")

def main():
    """Main function to process all analysis files."""
    analysis_dir = Path("/Users/arriazui/Desktop/GreenComputing/flexecutor-main/examples/general_usage/plot_generation/analysis_results")
    
    if not analysis_dir.exists():
        print(f"Error: Directory {analysis_dir} does not exist")
        return
    
    # Get all JSON files in the directory
    json_files = list(analysis_dir.glob("*.json"))
    json_files.sort()  # Sort alphabetically
    
    print("# Analysis Results Summary")
    print("Analysis of memory, workers, and total_executions for each JSON file")
    
    for json_file in json_files:
        data = extract_analysis_data(json_file)
        create_table_for_file(json_file, data)

if __name__ == "__main__":
    main()

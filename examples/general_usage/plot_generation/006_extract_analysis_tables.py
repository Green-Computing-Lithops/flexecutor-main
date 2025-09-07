#!/usr/bin/env python3
"""
Script to extract memory, workers, and total_executions data from analysis JSON files
and save them to a CSV file.
"""

import json
import os
import csv
from pathlib import Path

def extract_analysis_data(json_file_path):
    """Extract memory, workers, and total_executions from a JSON analysis file."""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Check if it's the new format with metadata and analysis_results
        if 'metadata' in data and 'analysis_results' in data:
            # This is the new analysis format with metadata and analysis_results
            extracted_data = []
            title = data['metadata'].get('title', 'Unknown')
            
            for result in data['analysis_results']:
                extracted_data.append({
                    'title': title,
                    'memory': result.get('memory', 'Unknown'),
                    'workers': result.get('workers', 'Unknown'), 
                    'total_executions': result.get('total_executions', 'Unknown')
                })
            
            return extracted_data
        
        # Check if it's the enhanced_profiling_analysis.json file
        elif 'profiling_data' in data:
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
        
        elif '001_analysis_results' in data:
            # This is a regular analysis file with 001_analyze_all_profiling_enhanced
            extracted_data = []
            for result in data['001_analysis_results']:
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

def collect_data_for_csv(file_path, data):
    """Collect data from a single file for CSV export."""
    file_name = os.path.basename(file_path).replace('_analysis.json', '').replace('.json', '')
    csv_rows = []
    
    if not data or (len(data) == 1 and 'error' in data[0]):
        # Add error row
        csv_rows.append({
            'filename': file_name,
            'title': 'Error',
            'memory': data[0].get('error', 'Unknown error') if data else 'No data',
            'workers': 'Error',
            'total_executions': 'Error'
        })
        return csv_rows
    
    # Process each data item
    for item in data:
        if 'title' in item:  # New format with title
            csv_rows.append({
                'filename': file_name,
                'title': item.get('title', 'Unknown'),
                'memory': item.get('memory', 'Unknown'),
                'workers': item.get('workers', 'Unknown'),
                'total_executions': item.get('total_executions', 'Unknown')
            })
        else:  # Old format without title
            csv_rows.append({
                'filename': file_name,
                'title': file_name,  # Use filename as title
                'memory': item.get('memory', 'Unknown'),
                'workers': item.get('workers', 'Unknown'),
                'total_executions': item.get('total_executions', 'Unknown')
            })
    
    return csv_rows

def main():
    """Main function to process all analysis files and save to CSV."""
    # Use relative path
    analysis_dir = Path("001_analysis_results")
    
    if not analysis_dir.exists():
        print(f"Error: Directory {analysis_dir} does not exist")
        return
    
    # Get all JSON files in the directory
    json_files = list(analysis_dir.glob("*.json"))
    json_files.sort()  # Sort alphabetically
    
    if not json_files:
        print("No JSON files found in the analysis directory")
        return
    
    # Collect all data for CSV
    all_csv_data = []
    
    print(f"Processing {len(json_files)} JSON files...")
    
    for json_file in json_files:
        data = extract_analysis_data(json_file)
        csv_rows = collect_data_for_csv(json_file, data)
        all_csv_data.extend(csv_rows)
        print(f"✓ Processed: {os.path.basename(json_file)}")
    
    # Define CSV output path
    output_csv = "006_extract_analysis_tables/006_extract_analysis_tables.csv"
    
    # Write to CSV file
    if all_csv_data:
        fieldnames = ['filename', 'title', 'memory', 'workers', 'total_executions']
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_csv_data)
        
        print(f"\n✅ Successfully saved {len(all_csv_data)} rows to: {output_csv}")
        print(f"📊 Total configurations analyzed: {len(all_csv_data)}")
        print(f"📁 Unique files processed: {len(json_files)}")
    else:
        print("❌ No data collected to save to CSV")

if __name__ == "__main__":
    main()

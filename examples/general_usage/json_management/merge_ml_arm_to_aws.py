#!/usr/bin/env python3
"""
Script to merge JSON files from ml_arm directory into ml_aws_512Mb_arm directory.
Creates merged files like stage0_merged.json, stage1_merged.json, etc.
"""

import json
import os
from pathlib import Path

def merge_json_files(stage_num):
    """Merge a stage file from ml_arm with its corresponding ml_aws_512Mb_arm file"""
    
    # File paths
    source_file = f"ml/{stage_num}.json"
    target_file = f"ml_aws_1024Mb_arm/stage{stage_num}.json"
    output_file = f"ml_aws_1024Mb_arm/stage{stage_num}_merged.json"
    
    # Check if both files exist
    if not os.path.exists(source_file):
        print(f"Warning: {source_file} not found")
        return False
    
    if not os.path.exists(target_file):
        print(f"Warning: {target_file} not found")
        return False
    
    # Load JSON data
    with open(source_file, 'r') as f:
        source_data = json.load(f)
    
    with open(target_file, 'r') as f:
        target_data = json.load(f)
    
    # Create merged data structure
    merged_data = {}
    
    # Add all data from target file first (ml_aws_512Mb_arm)
    for key, value in target_data.items():
        merged_data[key] = value
    
    # Add all data from source file (ml_arm)
    for key, value in source_data.items():
        if key in merged_data:
            # If key exists, we need to merge the metric arrays
            for metric_name, metric_values in value.items():
                if metric_name in merged_data[key]:
                    # Concatenate the arrays
                    merged_data[key][metric_name].extend(metric_values)
                else:
                    # Add new metric
                    merged_data[key][metric_name] = metric_values
        else:
            # Add new configuration key
            merged_data[key] = value
    
    # Write merged data to output file
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=4)
    
    print(f"Successfully merged {source_file} and {target_file} into {output_file}")
    return True

def main():
    """Main function to merge all stage files"""
    print("Starting JSON file merging process from ml_arm to ml_aws_512Mb_arm...")
    
    # Change to the profiling directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Merge all stage files (0-3)
    success_count = 0
    for stage_num in range(4):
        if merge_json_files(stage_num):
            success_count += 1
    
    print(f"\nMerging complete! Successfully merged {success_count} stage files.")
    print("Merged files created in ml_aws_512Mb_arm/ directory with '_merged.json' suffix.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to merge JSON files from the main directory and merge/ subdirectory.
Creates merged files like stage0_merged.json, stage1_merged.json, etc.
"""

import json
import os
from pathlib import Path

def merge_json_files(stage_num):
    """Merge a stage file with its corresponding merge/ file"""
    
    # File paths
    main_file = f"examples/ml/profiling/ml_aws_2048Mb_x86/merge/stage{stage_num}.json"
    merge_file = f"examples/ml/profiling/ml_aws_2048Mb_x86/stage{stage_num}_2048MB.json"
    output_file = f"examples/ml/profiling/ml_aws_2048Mb_x86/stage{stage_num}.json"

    # merge_file = f"ml_aws_512Mb_arm/stage{stage_num}_merged.json"
    # output_file = f"ml_aws_512Mb_arm/stage{stage_num}.json"
    
    # Check if both files exist
    if not os.path.exists(main_file):
        print(f"Warning: {main_file} not found")
        return False
    
    if not os.path.exists(merge_file):
        print(f"Warning: {merge_file} not found")
        return False
    
    # Load JSON data
    with open(main_file, 'r') as f:
        main_data = json.load(f)
    
    with open(merge_file, 'r') as f:
        merge_data = json.load(f)
    
    # Create merged data structure
    merged_data = {}
    
    # Add all data from main file
    for key, value in main_data.items():
        merged_data[key] = value
    
    # Add all data from merge file
    for key, value in merge_data.items():
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
    
    print(f"Successfully merged {main_file} and {merge_file} into {output_file}")
    return True

def main():
    """Main function to merge all stage files"""
    print("Starting JSON file merging process...")
    
    # Merge all stage files (0-3)
    success_count = 0
    for stage_num in range(4):
        if merge_json_files(stage_num):
            success_count += 1
    
    print(f"\nMerging complete! Successfully merged {success_count} stage files.")

if __name__ == "__main__":
    main()

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
    
    # Get the script directory and construct proper relative paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # Go up to flexecutor-main root
    
    # File paths - corrected to use proper relative paths and file names
    main_file = project_root / "examples/montecarlo_pi_estimation/profiling/pi_2048MB_x86/monte_carlo_pi_stage.json"
    merge_file = project_root / "examples/montecarlo_pi_estimation/profiling/pi_aws_2048MB_x86/stage.json"
    output_file = project_root / "examples/montecarlo_pi_estimation/profiling/pi_aws_2048MB_x86/stage_merged.json"

    # File paths --> F include the 
    # main_file = project_root / f"examples/video/profiling/video/stage{stage_num}.json"
    # merge_file = project_root / f"examples/video/profiling/video_aws_1024Mb_x86/stage{stage_num}.json"
    # output_file = project_root / f"examples/video/profiling/video_aws_1024Mb_x86/stage{stage_num}.json"

    # Check if both files exist
    if not main_file.exists():
        print(f"Warning: {main_file} not found")
        return False
    
    if not merge_file.exists():
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
    
    print(f"Successfully merged {main_file.name} and {merge_file.name} into {output_file.name}")
    return True

def main():
    """Main function to merge all stage files"""
    print("Starting JSON file merging process...")
    
    # Since we're only merging one pair of files, we don't need the loop
    success_count = 0
    if merge_json_files(4):  # stage_num parameter is not used in current logic
        success_count += 1

    for stage_num in range(4):
        if merge_json_files(stage_num):
            success_count += 1        
    
    print(f"\nMerging complete! Successfully merged {success_count} stage files.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced Profiling Data Collector

This script collects profiling data from all examples in the flexecutor project
and generates a consolidated analysis JSON with proper tagging for classification.

The script follows the naming convention:
- Folder name format: example_memory_aws/k8s_arm/x86
- First word before _ = example name
- Second word before _ = memory configuration  
- Third word before _ = aws or k8s
- Fourth word before _ = arm or x86

Output format includes: example, stage, memory, and architecture information
Title format: example_jsonname_stage_platform_memory_architecture

Usage:
    python collect_profiling_data_enhanced.py

Output:
    enhanced_profiling_analysis.json - Contains all profiling data with enhanced tags
"""

import os
import json
import glob
from pathlib import Path
from datetime import datetime
import re

# Base directories to search for profiling data
PROFILING_DIRECTORIES = [
    "../../ml/profiling",
    "../../montecarlo_pi_estimation/profiling", 
    "../../../AAA_information/video/profiling",
    "../../../AAA_information/titanic/profiling"
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
    
    Based on your specification:
    - First word before _ = example
    - Second word before _ = memory  
    - Third word before _ = aws or k8s
    - Fourth word before _ = arm or x86
    
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
    if folder_name in ["montecarlo_pi_estimation", "machine_learning", "video_processing"]:
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

def load_json_file(file_path):
    """
    Load JSON file and return its contents.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: JSON data or None if failed to load
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

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

def collect_enhanced_profiling_data():
    """
    Collect all profiling data from configured directories with enhanced parsing.
    
    Returns:
        dict: Consolidated profiling data with enhanced metadata
    """
    consolidated_data = {
        "metadata": {
            "description": "Enhanced consolidated profiling analysis from all examples",
            # "generated_at": datetime.now().isoformat(),
            "naming_convention": "example_memory_platform_architecture",
            "title_format": "example_jsonname_stage_platform_memory_architecture",
            "examples_included": []
        },
        "profiling_data": []
    }
    
    examples_found = set()
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for base_dir in PROFILING_DIRECTORIES:
        # Convert relative path to absolute path
        abs_base_dir = os.path.join(script_dir, base_dir)
        
        if not os.path.exists(abs_base_dir):
            print(f"Directory not found: {abs_base_dir}")
            continue
            
        print(f"Scanning directory: {abs_base_dir}")
        
        # Find all JSON files recursively
        json_files = glob.glob(os.path.join(abs_base_dir, "**/*.json"), recursive=True)
        
        for json_file in json_files:
            print(f"Processing: {json_file}")
            
            # Load JSON data
            json_data = load_json_file(json_file)
            if not json_data:
                continue
                
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
            
            # Add example to set
            examples_found.add(example_info["example"])
            
            # Process each configuration in the JSON file
            for config_key, config_data in json_data.items():
                entry = {
                    "title": title,
                    "example": example_info["example"],
                    "stage": stage,
                    "memory": example_info["memory"],
                    "platform": example_info["platform"],
                    "architecture": example_info["architecture"],
                    "source_file": json_file,
                    "source_folder": folder_name,
                    "json_filename": json_filename,
                    "configuration": config_key,
                    "example_description": EXAMPLE_DESCRIPTIONS.get(
                        example_info["example"], 
                        f"{example_info['example']} computational workload"
                    ),
                    "profiling_metrics": config_data
                }
                
                consolidated_data["profiling_data"].append(entry)
    
    # Update metadata with found examples
    consolidated_data["metadata"]["examples_included"] = sorted(list(examples_found))
    consolidated_data["metadata"]["total_entries"] = len(consolidated_data["profiling_data"])
    
    return consolidated_data

def save_consolidated_data(data, output_file):
    """
    Save consolidated data to JSON file.
    
    Args:
        data (dict): Consolidated profiling data
        output_file (str): Output file path
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Enhanced consolidated profiling data saved to: {output_file}")
        print(f"✓ Total entries: {data['metadata']['total_entries']}")
        print(f"✓ Examples included: {', '.join(data['metadata']['examples_included'])}")
    except Exception as e:
        print(f"✗ Error saving consolidated data: {e}")

def print_enhanced_summary(data):
    """
    Print a detailed summary of collected data.
    
    Args:
        data (dict): Consolidated profiling data
    """
    print("\n" + "="*70)
    print("ENHANCED PROFILING DATA COLLECTION SUMMARY")
    print("="*70)
    
    # Count by different categories
    example_counts = {}
    stage_counts = {}
    memory_counts = {}
    platform_counts = {}
    arch_counts = {}
    
    for entry in data["profiling_data"]:
        example = entry["example"]
        stage = entry["stage"]
        memory = entry["memory"]
        platform = entry["platform"]
        arch = entry["architecture"]
        
        example_counts[example] = example_counts.get(example, 0) + 1
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        memory_counts[memory] = memory_counts.get(memory, 0) + 1
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
        arch_counts[arch] = arch_counts.get(arch, 0) + 1
    
    print(f"Total entries: {len(data['profiling_data'])}")
    print(f"Examples found: {len(example_counts)}")
    print(f"Naming convention: {data['metadata']['naming_convention']}")
    print(f"Title format: {data['metadata']['title_format']}")
    
    print("\nBreakdown by Example:")
    for example, count in sorted(example_counts.items()):
        print(f"  {example}: {count} entries")
    
    print("\nBreakdown by Stage:")
    for stage, count in sorted(stage_counts.items()):
        print(f"  {stage}: {count} entries")
        
    print("\nBreakdown by Memory:")
    for memory, count in sorted(memory_counts.items()):
        print(f"  {memory}: {count} entries")
        
    print("\nBreakdown by Platform:")
    for platform, count in sorted(platform_counts.items()):
        print(f"  {platform}: {count} entries")
        
    print("\nBreakdown by Architecture:")
    for arch, count in sorted(arch_counts.items()):
        print(f"  {arch}: {count} entries")
    
    # Show some example titles
    print("\nExample Titles Generated:")
    for i, entry in enumerate(data["profiling_data"][:5]):
        print(f"  {i+1}. {entry['title']}")
    if len(data["profiling_data"]) > 5:
        print(f"  ... and {len(data['profiling_data']) - 5} more")

def main():
    """Main function."""
    print("Starting enhanced profiling data collection...")
    print(f"Scanning directories: {PROFILING_DIRECTORIES}")
    print("Following naming convention: example_memory_platform_architecture")
    print("Title format: example_jsonname_stage_platform_memory_architecture")
    
    # Collect all profiling data
    consolidated_data = collect_enhanced_profiling_data()
    
    # Print summary
    print_enhanced_summary(consolidated_data)
    
    # Save to file in analysis_results directory
    output_dir = "analysis_results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "enhanced_profiling_analysis.json")
    save_consolidated_data(consolidated_data, output_file)
    
    print(f"\n✓ Enhanced collection complete! Check {output_file} for results.")

if __name__ == "__main__":
    main()

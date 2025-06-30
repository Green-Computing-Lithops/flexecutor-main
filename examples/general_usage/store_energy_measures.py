#!/usr/bin/env python3
"""
store_energy_measures.py

This script extracts energy measurements from the energy_data directory
and stores them in the profiling JSON files in examples/ml/profiling/machine_learning.

Usage:
    python store_energy_measures.py

This script should be run after executing examples/ml/main.py to store the
energy measurements in the profiling JSON files.
"""

import os
import json
import glob
import re
from collections import defaultdict

# Paths
ENERGY_DATA_DIR = "energy_data"
PROFILING_DIR = "examples/ml/profiling/machine_learning"

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json_file(file_path, data):
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved {file_path}")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def extract_energy_measurements():
    """
    Extract energy measurements from the energy_data directory.
    Returns a dictionary mapping stage names to energy measurements.
    """
    # Dictionary to store energy measurements for each stage
    energy_measurements = defaultdict(list)
    
    # Get all JSON files in the energy_data directory
    energy_files = glob.glob(os.path.join(ENERGY_DATA_DIR, "*.json"))
    print(f"Found {len(energy_files)} energy data files")
    
    # Extract energy measurements from each file
    for file_path in energy_files:
        data = load_json_file(file_path)
        if not data or "RAPL" not in data:
            continue
        
        # Extract function name and energy measurements
        function_name = data["RAPL"].get("function_name")
        if not function_name:
            continue
        
        # Map function names to stage names
        stage_name = None
        if function_name == "pca":
            stage_name = "stage0"
        elif function_name == "train_with_multiprocessing":
            stage_name = "stage1"
        elif function_name == "aggregate":
            stage_name = "stage2"
        elif function_name == "test":
            stage_name = "stage3"
        else:
            # Try to extract stage number from function name
            match = re.search(r'stage(\d+)', function_name)
            if match:
                stage_name = f"stage{match.group(1)}"
        
        if not stage_name:
            continue
        
        # Extract energy measurements
        energy_pkg = data["RAPL"].get("energy_pkg", 0)
        energy_cores = data["RAPL"].get("energy_cores", 0)
        energy_total = data["RAPL"].get("energy_total", 0)
        
        # Store energy measurements
        energy_measurements[stage_name].append({
            "energy_pkg": energy_pkg,
            "energy_cores": energy_cores,
            "energy_total": energy_total
        })
    
    return energy_measurements

def update_profiling_files(energy_measurements):
    """
    Update the profiling JSON files with the extracted energy measurements.
    """
    # Check if the profiling directory exists
    if not os.path.exists(PROFILING_DIR):
        print(f"Profiling directory {PROFILING_DIR} does not exist")
        return
    
    # Get all JSON files in the profiling directory
    profiling_files = glob.glob(os.path.join(PROFILING_DIR, "*.json"))
    print(f"Found {len(profiling_files)} profiling files")
    
    # Update each profiling file
    for file_path in profiling_files:
        # Extract stage name from file path
        stage_name = os.path.basename(file_path).split('.')[0]
        
        # Check if we have energy measurements for this stage
        if stage_name not in energy_measurements:
            print(f"No energy measurements found for {stage_name}")
            continue
        
        # Load the profiling file
        profiling_data = load_json_file(file_path)
        if not profiling_data:
            continue
        
        # Update the profiling data with energy measurements
        for key in profiling_data:
            if "RAPL" not in profiling_data[key]:
                profiling_data[key]["RAPL"] = []
            
            # Add new energy measurements
            new_measurements = []
            for measurement in energy_measurements[stage_name]:
                new_measurements.append([
                    measurement["energy_pkg"],
                    measurement["energy_total"],
                    measurement["energy_cores"]
                ])
            
            # If there are existing measurements, append the new ones
            if profiling_data[key]["RAPL"]:
                profiling_data[key]["RAPL"].append(new_measurements)
            else:
                profiling_data[key]["RAPL"] = [new_measurements]
        
        # Save the updated profiling file
        save_json_file(file_path, profiling_data)

def main():
    """Main function."""
    print("Extracting energy measurements from energy_data directory...")
    energy_measurements = extract_energy_measurements()
    
    print("Updating profiling files with energy measurements...")
    update_profiling_files(energy_measurements)
    
    print("Done!")

if __name__ == "__main__":
    main()
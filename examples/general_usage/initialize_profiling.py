"""
initialize_profiling.py

This script initializes the profiling directory and creates empty JSON files
for each stage in examples/ml/profiling/machine_learning.

Usage:
    python initialize_profiling.py

This script should be run before executing examples/ml/main.py if the
profiling JSON files have been deleted.
"""

import os
import json

# Paths
PROFILING_DIR = "examples/ml/profiling/machine_learning"

def ensure_directory_exists(directory):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

def create_empty_profiling_file(stage_name):
    """Create an empty profiling JSON file for a stage."""
    file_path = os.path.join(PROFILING_DIR, f"{stage_name}.json")
    
    # Check if the file already exists
    if os.path.exists(file_path):
        print(f"Profiling file already exists: {file_path}")
        return
    
    # Create an empty profiling data structure
    profiling_data = {
        f"('{stage_name}', 0.0, 1)": {
            "read": [[]],
            "compute": [[]],
            "write": [[]],
            "cold_start": [[]],
            "energy_consumption": [[]],
            "energy_lithops": [[]],
            "energy_custom": [[]]
        }
    }
    
    # Save the profiling data to the file
    try:
        with open(file_path, 'w') as f:
            json.dump(profiling_data, f, indent=4)
        print(f"Created empty profiling file: {file_path}")
    except Exception as e:
        print(f"Error creating profiling file {file_path}: {e}")

def main():
    """Main function."""
    print("Initializing profiling directory...")
    ensure_directory_exists(PROFILING_DIR)
    
    print("Creating empty profiling files...")
    for i in range(4):
        create_empty_profiling_file(f"stage{i}")
    
    print("Done!")

if __name__ == "__main__":
    main()
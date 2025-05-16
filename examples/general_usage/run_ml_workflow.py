#!/usr/bin/env python3
"""
run_ml_workflow.py

This script automates the process of running the machine learning workflow
with energy measurement storage. It performs the following steps:
1. Initializes the profiling directory if needed
2. Runs the main.py script to initialize training data, execute the workflow,
   and store energy measurements
3. Verifies that energy measurements were stored in the profiling JSON files
4. Runs the minio_cleanup.py script to clean up temporary data

Usage:
    python3 run_ml_workflow.py
"""

import os
import subprocess
import json
import time

# Paths
PROFILING_DIR = "examples/ml/profiling/machine_learning"

def ensure_profiling_directory():
    """
    Ensure that the profiling directory exists and contains the necessary JSON files.
    If the directory doesn't exist or is empty, run the initialize_profiling.py script.
    """
    print("\n=== Checking profiling directory ===")
    
    # Check if the directory exists and contains JSON files
    if not os.path.exists(PROFILING_DIR) or not any(f.endswith('.json') for f in os.listdir(PROFILING_DIR)):
        print("Profiling directory is missing or empty. Running initialize_profiling.py...")
        subprocess.run(["python3", "initialize_profiling.py"], check=True)
        print("Profiling directory initialized.")
    else:
        print("Profiling directory exists and contains JSON files.")
        
    # Verify that all stage JSON files exist
    missing_files = []
    for i in range(4):
        file_path = os.path.join(PROFILING_DIR, f"stage{i}.json")
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Some stage JSON files are missing: {missing_files}")
        print("Running initialize_profiling.py to create missing files...")
        subprocess.run(["python3", "initialize_profiling.py"], check=True)
        print("Missing files created.")

def run_ml_workflow():   
    try:
        subprocess.run(["python3", "examples/ml/main.py"], check=True)
        print("Workflow execution completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing workflow: {e}")
        return False
    
    return True

def cleanup_minio():
   
    try:
        subprocess.run(["python3", "examples/general_usage/minio_cleanup.py"], check=True)
        print("MinIO cleanup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error cleaning up MinIO: {e}")
        return False
    
    return True

def verify_energy_measurements():
    """
    Verify that energy measurements have been stored in the profiling JSON files.
    """
    print("\n=== Verifying energy measurements ===")
    
    all_have_energy = True
    for i in range(4):
        file_path = os.path.join(PROFILING_DIR, f"stage{i}.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Check if any configuration has energy_consumption data
            has_energy = False
            for config, metrics in data.items():
                if "energy_consumption" in metrics and any(metrics["energy_consumption"]):
                    has_energy = True
                    break
            
            if has_energy:
                print(f"Stage{i} has energy measurements.")
            else:
                print(f"Stage{i} does not have energy measurements.")
                all_have_energy = False
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            all_have_energy = False
    
    return all_have_energy

def main():
    """Main function."""
    print("=== ML Workflow with Energy Measurement ===")
    print("This script will run the machine learning workflow and store energy measurements.")
    
    # Step 1: Ensure profiling directory exists with necessary JSON files
    ensure_profiling_directory()
    
    # Step 2: Run the ML workflow
    if not run_ml_workflow():
        print("Workflow execution failed. Exiting.")
        return
    
    # Step 3: Verify energy measurements
    if verify_energy_measurements():
        print("\nEnergy measurements have been successfully stored in the profiling JSON files.")
    else:
        print("\nSome stages may not have energy measurements.")
        print("You can run store_energy_measures.py to extract additional energy measurements.")
    
    # Step 4: Clean up MinIO
    if cleanup_minio():
        print("\nWorkflow completed successfully and MinIO has been cleaned up.")
    else:
        print("\nWorkflow completed but MinIO cleanup failed.")
    
    print("\nYou can find the energy measurements in examples/ml/profiling/machine_learning/")

if __name__ == "__main__":
    main()

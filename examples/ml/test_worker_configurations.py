#!/usr/bin/env python3
"""
test_worker_configurations.py

Test script to demonstrate the new worker configuration functionality.
This script shows different ways to run the ML workflow with various worker configurations.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, cwd="/home/users/iarriazu/flexecutor-main/examples/ml")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main test function."""
    python_path = "/home/users/iarriazu/flexecutor-main/.venv/bin/python"
    
    print("WORKER CONFIGURATION TESTING SUITE")
    print("=" * 60)
    print("This script demonstrates the new worker configuration functionality.")
    print("Note: These are dry-run examples. Uncomment to actually execute.")
    
    # Test cases - commented out to avoid actual execution during demonstration
    test_cases = [
        {
            "cmd": [python_path, "main.py", "--help"],
            "description": "Show help for main.py"
        },
        {
            "cmd": [python_path, "run_ml_workflow_with_cleanup.py", "--help"],
            "description": "Show help for run_ml_workflow_with_cleanup.py"
        },
        # Uncomment these to run actual tests:
        # {
        #     "cmd": [python_path, "main.py"],
        #     "description": "Run with default worker configurations (1 worker for stage0, 16 for others)"
        # },
        # {
        #     "cmd": [python_path, "main.py", "--workers-stage0", "4", "--workers-stages", "8"],
        #     "description": "Run with custom single worker configuration (4 for stage0, 8 for others)"
        # },
        # {
        #     "cmd": [python_path, "main.py", "--workers-stage0", "1", "4", "--workers-stages", "8", "16", "--run-mode", "batch"],
        #     "description": "Run batch mode with multiple worker configurations"
        # },
        # {
        #     "cmd": [python_path, "run_ml_workflow_with_cleanup.py"],
        #     "description": "Run with cleanup using default configurations"
        # },
        # {
        #     "cmd": [python_path, "run_ml_workflow_with_cleanup.py", "--workers-stage0", "1", "4", "8", "--workers-stages", "4", "8", "16", "32", "--run-mode", "batch"],
        #     "description": "Run batch mode with cleanup and multiple worker configurations"
        # }
    ]
    
    # Run only the help commands by default
    success_count = 0
    for i, test_case in enumerate(test_cases[:2], 1):  # Only run first 2 (help commands)
        print(f"\n[{i}/{len(test_cases[:2])}] Running test...")
        success = run_command(test_case["cmd"], test_case["description"])
        if success:
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"TESTING SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {len(test_cases[:2])}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(test_cases[:2]) - success_count}")
    
    print(f"\n{'='*60}")
    print("USAGE EXAMPLES")
    print(f"{'='*60}")
    print("To run the ML workflow with different worker configurations:")
    print()
    print("1. Default configuration:")
    print(f"   {python_path} main.py")
    print()
    print("2. Custom single configuration:")
    print(f"   {python_path} main.py --workers-stage0 4 --workers-stages 8")
    print()
    print("3. Batch mode with multiple configurations:")
    print(f"   {python_path} main.py --workers-stage0 1 4 8 --workers-stages 4 8 16 32 --run-mode batch")
    print()
    print("4. With cleanup (recommended):")
    print(f"   {python_path} run_ml_workflow_with_cleanup.py --workers-stage0 1 4 --workers-stages 8 16")
    print()
    print("5. Batch mode with cleanup:")
    print(f"   {python_path} run_ml_workflow_with_cleanup.py --workers-stage0 1 4 8 --workers-stages 4 8 16 32 --run-mode batch")

if __name__ == "__main__":
    main()

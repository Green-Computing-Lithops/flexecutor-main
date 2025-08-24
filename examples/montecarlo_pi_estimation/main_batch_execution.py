"""
main_batch_execution.py

Main execution script for Monte Carlo Pi estimation that executes multiple times 
with different worker configurations. This script generates 100,000,000 random points 
distributed across workers for each configuration.
"""

import sys
import os
import json
import time
from lithops import FunctionExecutor

# Add the project root to the path
# sys.path.insert(0, '/home/users/iarriazu/flexecutor-main')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from examples.montecarlo_pi_estimation.functions import monte_carlo_pi_estimation
from flexecutor.storage.storage import FlexData
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage
from flexecutor.utils.dataclass import StageConfig
from flexecutor.storage.storage import FlexData

from flexecutor.workflow.dag import DAG
# Import the modified DAGExecutor class
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage

from flexecutor.utils.dataclass import StageConfig

memory_runtime = 2048
stage_file_multiple = "pi_2048MB_x86"


def save_batch_execution_profiling(results, execution_time, num_workers):
    """Save profiling data for batch execution to JSON file."""
    profiling_file = "examples/montecarlo_pi_estimation/montecarlo_pi_batch_profiling.json"
    
    try:
        # Load existing data or create new structure
        if os.path.exists(profiling_file):
            with open(profiling_file, 'r') as f:
                profiling_data = json.load(f)
        else:
            profiling_data = {"PI_ESTIMATION_BATCH": {}}
        
        # Extract timing data if available
        timing_data = None
        if results and "monte_carlo_pi_stage" in results:
            timing_results = results["monte_carlo_pi_stage"].get_timings()
            if timing_results:
                timing_data = {
                    "worker_count": len(timing_results),
                    "average_compute_time": sum(t.compute for t in timing_results) / len(timing_results),
                    "total_compute_time": sum(t.compute for t in timing_results),
                    "average_read_time": sum(t.read for t in timing_results) / len(timing_results),
                    "total_read_time": sum(t.read for t in timing_results),
                    "completion_rate": len(timing_results) / num_workers,
                    "throughput": len(timing_results) / execution_time,
                    "efficiency": (len(timing_results) / execution_time) / num_workers,
                    "individual_timings": [
                        {
                            "compute": t.compute,
                            "read": t.read,
                            "total": t.compute + t.read
                        } for t in timing_results
                    ]
                }
        
        # Store the data with timestamp as key
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        execution_key = f"{num_workers}_workers_{timestamp}"
        profiling_data["PI_ESTIMATION_BATCH"][execution_key] = {
            "execution_time": execution_time,
            "status": "completed",
            "num_workers": num_workers,
            "timing_data": timing_data,
            "timestamp": timestamp
        }
        
        # Add metadata
        profiling_data["simulation_type"] = "PI_ESTIMATION_BATCH"
        
        # Save updated data
        with open(profiling_file, 'w') as f:
            json.dump(profiling_data, f, indent=2)
            
        print(f"[✓] Batch execution profiling data saved to {profiling_file}")
        
    except Exception as e:
        print(f"[✗] Error saving batch execution profiling data: {e}")


def run_monte_carlo_pi_estimation_with_workers(worker_count):
    """Run the Monte Carlo Pi estimation with a specific number of workers."""
    print(f"\n{'='*60}")
    print(f"STARTING PI ESTIMATION WITH {worker_count} WORKERS")
    print(f"{'='*60}")

    @flexorchestrator(bucket="lithops-us-east-1-45dk")
    def monte_carlo_pi_workflow():
        dag = DAG('pi')

        print(f"🎯 Running Pi Estimation with {worker_count} workers")

        # Create the pi estimation stage
        stage = Stage(
            stage_id="monte_carlo_pi_stage",
            func=monte_carlo_pi_estimation,
            inputs=[],  # No input data needed for Monte Carlo pi estimation
            outputs=[
                FlexData(
                    prefix="pi_estimation_result",
                    suffix=".json",
                )
            ],
        )
        
        # Configure the stage resources after it's created
        stage.resource_config = StageConfig(cpu=4, memory=memory_runtime, workers=worker_count) # better 1

        dag.add_stage(stage)
        executor = DAGExecutor(dag, executor=FunctionExecutor(
            config_file_path="/home/minirobbin/Desktop/GreenComputing/flexecutor-main/config_aws.yaml",
            log_level="INFO", 
            runtime_memory=memory_runtime
        ))

        print(f"🚀 Starting Pi estimation with {worker_count} workers...")
        print(f"   Total points: 100,000,000 (distributed as ~{100_000_000//worker_count:,} per worker)")
        
        start_time = time.time()
        
        # Execute with profiling to measure performance
        results = executor.execute_with_profiling(num_workers=worker_count)
 
        executor.shutdown()
        
        execution_time = time.time() - start_time
        
        # Print timing results
        timing_results = results["monte_carlo_pi_stage"].get_timings()
        print(f"✅ Pi estimation completed:")
        print(f"   Workers: {worker_count}")
        print(f"   Execution time: {execution_time:.2f}s")
        print(f"   Workers completed: {len(timing_results)}")
        print(f"   Timings: {timing_results}")
        
        # Save profiling data
        save_batch_execution_profiling(results, execution_time, worker_count)
        
        return results

    try:
        return monte_carlo_pi_workflow()
    except Exception as e:
        print(f"[✗] Pi estimation with {worker_count} workers failed: {e}")
        return False


if __name__ == "__main__":
    # Define worker configurations to test
    # worker_configurations = [28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    memory_runtime = 2048
    stage_file_multiple = "pi_2048MB_x86"

    worker_configurations = [
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,     
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4
    ]

    print("="*80)
    print("BATCH EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS - MONTE CARLO PI ESTIMATION")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Run the workflow with current worker configuration
            success = run_monte_carlo_pi_estimation_with_workers(worker_count)
            results[worker_count] = bool(success)
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            results[worker_count] = False
    
    # Print final summary
    print("\n" + "="*80)
    print("BATCH EXECUTION SUMMARY - MONTE CARLO PI ESTIMATION")
    print("="*80)
    
    for worker_count, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"Workers {worker_count:2d}: {status}")
    
    successful_runs = sum(1 for success in results.values() if success)
    total_runs = len(results)
    
    print(f"\nTotal successful runs: {successful_runs}/{total_runs}")
    
    if successful_runs == total_runs:
        print("✓ All worker configurations completed successfully!")
    else:
        print("✗ Some worker configurations failed.")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    memory_runtime = 1024
    stage_file_multiple = "pi_1024MB_x86"

    worker_configurations = [
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,     
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4
    ]

    print("="*80)
    print("BATCH EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS - MONTE CARLO PI ESTIMATION")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Run the workflow with current worker configuration
            success = run_monte_carlo_pi_estimation_with_workers(worker_count)
            results[worker_count] = bool(success)
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            results[worker_count] = False
    
    # Print final summary
    print("\n" + "="*80)
    print("BATCH EXECUTION SUMMARY - MONTE CARLO PI ESTIMATION")
    print("="*80)
    
    for worker_count, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"Workers {worker_count:2d}: {status}")
    
    successful_runs = sum(1 for success in results.values() if success)
    total_runs = len(results)
    
    print(f"\nTotal successful runs: {successful_runs}/{total_runs}")
    
    if successful_runs == total_runs:
        print("✓ All worker configurations completed successfully!")
    else:
        print("✗ Some worker configurations failed.")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    memory_runtime = 512
    stage_file_multiple = "pi_512MB_x86"

    worker_configurations = [
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,     
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        28, 24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4
    ]

    print("="*80)
    print("BATCH EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS - MONTE CARLO PI ESTIMATION")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Run the workflow with current worker configuration
            success = run_monte_carlo_pi_estimation_with_workers(worker_count)
            results[worker_count] = bool(success)
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            results[worker_count] = False
    
    # Print final summary
    print("\n" + "="*80)
    print("BATCH EXECUTION SUMMARY - MONTE CARLO PI ESTIMATION")
    print("="*80)
    
    for worker_count, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"Workers {worker_count:2d}: {status}")
    
    successful_runs = sum(1 for success in results.values() if success)
    total_runs = len(results)
    
    print(f"\nTotal successful runs: {successful_runs}/{total_runs}")
    
    if successful_runs == total_runs:
        print("✓ All worker configurations completed successfully!")
    else:
        print("✗ Some worker configurations failed.")

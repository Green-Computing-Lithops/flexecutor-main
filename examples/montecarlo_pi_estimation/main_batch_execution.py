"""
main_batch_execution.py

Main execution script for Monte Carlo Pi estimation that accepts command line arguments
for the number of workers. This script generates 100,000,000 random points distributed
across workers and is called by the batch execution cleanup script.
"""

import argparse
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


def save_batch_execution_profiling(results, execution_time, num_workers):
    """Save profiling data for batch execution to JSON file."""
    profiling_file = "examples/montecarlo_pi_estimation/montecarlo_batch_profiling.json"
    
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


def run_monte_carlo_pi_estimation(num_workers=4):
    """Run the Monte Carlo Pi estimation with specified number of workers."""
    
    @flexorchestrator(bucket="lithops-us-east-1-45dk")
    def monte_carlo_pi_workflow():
        dag = DAG("montecarlo_pi_estimation")

        print(f"🎯 Running Pi Estimation with {num_workers} workers")

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

        dag.add_stage(stage)
        executor = DAGExecutor(dag, executor=FunctionExecutor())

        print(f"🚀 Starting Pi estimation with {num_workers} workers...")
        print(f"   Total points: 100,000,000 (distributed as ~{100_000_000//num_workers:,} per worker)")
        
        start_time = time.time()
        
        # Execute with profiling to measure performance
        results = executor.execute_with_profiling(num_workers=num_workers)
 
        executor.shutdown()
        
        execution_time = time.time() - start_time
        
        # Print timing results
        timing_results = results["monte_carlo_pi_stage"].get_timings()
        print(f"✅ Pi estimation completed:")
        print(f"   Workers: {num_workers}")
        print(f"   Execution time: {execution_time:.2f}s")
        print(f"   Workers completed: {len(timing_results)}")
        print(f"   Timings: {timing_results}")
        
        # Save profiling data
        save_batch_execution_profiling(results, execution_time, num_workers)
        
        return results

    return monte_carlo_pi_workflow()


def main():
    """Main function that parses arguments and runs the pi estimation."""
    parser = argparse.ArgumentParser(description='Run Monte Carlo Pi estimation with FlexExecutor')
    
    parser.add_argument(
        '--num_workers', 
        type=int, 
        default=4,
        help='Number of workers to use for the simulation (default: 4)'
    )
    
    args = parser.parse_args()
    
    print("🎲 MONTE CARLO PI ESTIMATION - BATCH EXECUTION")
    print("="*60)
    print(f"Number of Workers: {args.num_workers}")
    print("="*60)
    
    try:
        results = run_monte_carlo_pi_estimation(args.num_workers)
        print("🎉 Pi estimation completed successfully!")
        
    except Exception as e:
        print(f"❌ Pi estimation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

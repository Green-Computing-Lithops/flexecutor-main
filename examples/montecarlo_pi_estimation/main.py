"""
Monte Carlo Pi Estimation with FlexExecutor

This module demonstrates Monte Carlo pi estimation using the FlexExecutor framework.
Uses random sampling to estimate the value of π by generating 100,000,000 random points
in a unit square and counting how many fall within a unit circle.

The simulation can be configured to run with different worker configurations
to compare performance across different parallel execution setups.
"""

import json
import os
import time
from lithops import FunctionExecutor

from examples.montecarlo_pi_estimation.functions import monte_carlo_pi_estimation
from flexecutor.storage.storage import FlexData
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage


def save_single_execution_profiling(results, execution_time, num_workers):
    """Save profiling data for single execution to JSON file."""
    profiling_file = "montecarlo_single_execution_profiling.json"
    
    try:
        # Load existing data or create new structure
        if os.path.exists(profiling_file):
            with open(profiling_file, 'r') as f:
                profiling_data = json.load(f)
        else:
            profiling_data = {"PI_ESTIMATION_SINGLE": {}}
        
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
                            "write": t.write,
                            "cold_start": t.cold_start,
                            "time_consumption": t.time_consumption,
                            "worker_time_execution": t.worker_time_execution,
                            "RAPL_wrong": t.RAPL_wrong,
                            "TDP": t.TDP,
                            "measurement_energy": t.measurement_energy,
                            "perf_energy_cores": t.perf_energy_cores,
                            "rapl_energy_cores": t.rapl_energy_cores,
                            "ebpf_energy_pkg": getattr(t, 'ebpf_energy_pkg', None),
                            "ebpf_energy_cores": t.ebpf_energy_cores,
                            "psutil_cpu_percent": t.psutil_cpu_percent,
                            "cpu_name": t.cpu_name,
                            "cpu_architecture": t.cpu_architecture,
                            "cpu_cores_physical": t.cpu_cores_physical,
                            "cpu_cores_logical": t.cpu_cores_logical,
                            "total": t.compute + t.read
                        } for t in timing_results
                    ]
                }
        
        # Store the data with timestamp as key
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        execution_key = f"{num_workers}_workers_{timestamp}"
        profiling_data["PI_ESTIMATION_SINGLE"][execution_key] = {
            "execution_time": execution_time,
            "status": "completed",
            "num_workers": num_workers,
            "timing_data": timing_data,
            "timestamp": timestamp
        }
        
        # Add metadata
        profiling_data["simulation_type"] = "PI_ESTIMATION_SINGLE"
        
        # Save updated data
        with open(profiling_file, 'w') as f:
            json.dump(profiling_data, f, indent=2)
            
        print(f"[✓] Single execution profiling data saved to {profiling_file}")
        
    except Exception as e:
        print(f"[✗] Error saving single execution profiling data: {e}")


if __name__ == "__main__":

    @flexorchestrator(bucket="lithops-us-east-1-45dk")
    def main():
        print("🎲 MONTE CARLO PI ESTIMATION - SINGLE EXECUTION")
        print("="*60)
        
        start_time = time.time()
        
        dag = DAG("pi")

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
        executor = DAGExecutor(dag, executor=FunctionExecutor(config_file=os.environ.get('LITHOPS_CONFIG_FILE', '../../config_aws.yaml')))

        # Execute with profiling to measure performance
        num_workers = 10
        print(f"🚀 Starting Pi estimation with {num_workers} workers...")
        print(f"   Total points: 100,000,000 (distributed as ~{100_000_000//num_workers:,} per worker)")
        results = executor.execute_with_profiling(num_workers=num_workers)
 
        executor.shutdown()
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ Pi Estimation Results:")
        timing_results = results["monte_carlo_pi_stage"].get_timings()
        print(f"   Execution time: {execution_time:.2f}s")
        print(f"   Workers completed: {len(timing_results)}")
        print(f"   Timings: {timing_results}")
        
        # Save profiling data
        save_single_execution_profiling(results, execution_time, num_workers)

    main()

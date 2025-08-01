"""
run_montecarlo_workflow_with_cleanup_batch_execution.py

Runs Monte Carlo Pi estimation with multiple worker configurations sequentially,
running each configuration for 5 minutes and cleaning up all execution artifacts 
after each run including:
- MinIO storage objects
- Kubernetes pods and jobs
- Temporary files

Usage:
    python run_montecarlo_workflow_with_cleanup_batch_execution.py
"""

import subprocess
import sys
import time
import os
import json
import signal
import argparse
from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject
from threading import Timer

# Add the project root to the path
sys.path.insert(0, '/home/users/iarriazu/flexecutor-main')

from lithops import FunctionExecutor
from examples.montecarlo_pi_estimation.functions import monte_carlo_pi_estimation
from flexecutor.storage.storage import FlexData
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
MINIO_ENDPOINT    = "192.168.5.24:9000"  # Based on the logs from execution
MINIO_ACCESS_KEY  = "lab144"
MINIO_SECRET_KEY  = "astl1a4b4"
MINIO_BUCKET      = "lithops-us-east-1-45dk"
KUBERNETES_NAMESPACE = "lithops-jobs"

# Worker configurations to test (each runs for 5 minutes)
# WORKER_CONFIGURATIONS = [ 8, 7, 6, 5, 4, 3, 2, 1]
# WORKER_CONFIGURATIONS = [1, 2, 3, 4, 5, 6, 7, 8]
WORKER_CONFIGURATIONS = [ 32, 16, 8, 6, 4]

EXECUTION_TIME_MINUTES = 5  # Increased from 3 to 5 minutes
EXECUTION_TIME_SECONDS = EXECUTION_TIME_MINUTES * 60
# ───────────────────────────────────────────────────────────────────────────────

def get_minio_file_info(prefix):
    """Get information about files in MinIO with the given prefix."""
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )
        
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"[!] Bucket '{MINIO_BUCKET}' does not exist")
            return [], 0
            
        objects = list(client.list_objects(MINIO_BUCKET, prefix=prefix, recursive=True))
        total_size = sum(obj.size for obj in objects)
        
        return objects, total_size
        
    except Exception as e:
        print(f"[✗] Error getting file info from MinIO: {e}")
        return [], 0


def cleanup_minio_storage():
    """Clean up all MinIO storage objects from the bucket."""
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )
        
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"[!] Bucket '{MINIO_BUCKET}' does not exist")
            return
            
        # List all objects in the bucket
        objects = list(client.list_objects(MINIO_BUCKET, recursive=True))
        
        if not objects:
            print("[✓] No objects found in MinIO bucket")
            return
            
        print(f"[•] Found {len(objects)} objects in MinIO bucket")
        
        # Prepare objects for deletion
        delete_objects = [DeleteObject(obj.object_name) for obj in objects]
        
        # Delete objects in batches
        errors = client.remove_objects(MINIO_BUCKET, delete_objects)
        error_count = 0
        for error in errors:
            print(f"[✗] Failed to delete {error.object_name}: {error}")
            error_count += 1
            
        if error_count == 0:
            print(f"[✓] Successfully deleted all {len(objects)} objects from MinIO")
        else:
            print(f"[!] Deleted {len(objects) - error_count}/{len(objects)} objects from MinIO")
            
    except S3Error as e:
        print(f"[✗] S3 error during MinIO cleanup: {e}")
    except Exception as e:
        print(f"[✗] Error during MinIO cleanup: {e}")


def cleanup_kubernetes_resources():
    """Clean up Kubernetes pods and jobs in the lithops namespace."""
    try:
        # Get all pods in the lithops namespace
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", KUBERNETES_NAMESPACE, "--no-headers"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pod_count = len(result.stdout.strip().split('\n'))
            print(f"[•] Found {pod_count} pods in namespace {KUBERNETES_NAMESPACE}")
            
            # Delete all pods
            delete_result = subprocess.run(
                ["kubectl", "delete", "pods", "--all", "-n", KUBERNETES_NAMESPACE, "--grace-period=0", "--force"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if delete_result.returncode == 0:
                print(f"[✓] Successfully deleted all pods from namespace {KUBERNETES_NAMESPACE}")
            else:
                print(f"[!] Warning: kubectl delete pods returned code {delete_result.returncode}")
                print(f"    stderr: {delete_result.stderr}")
        else:
            print(f"[✓] No pods found in namespace {KUBERNETES_NAMESPACE}")
            
        # Get all jobs in the lithops namespace  
        result = subprocess.run(
            ["kubectl", "get", "jobs", "-n", KUBERNETES_NAMESPACE, "--no-headers"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            job_count = len(result.stdout.strip().split('\n'))
            print(f"[•] Found {job_count} jobs in namespace {KUBERNETES_NAMESPACE}")
            
            # Delete all jobs
            delete_result = subprocess.run(
                ["kubectl", "delete", "jobs", "--all", "-n", KUBERNETES_NAMESPACE],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if delete_result.returncode == 0:
                print(f"[✓] Successfully deleted all jobs from namespace {KUBERNETES_NAMESPACE}")
            else:
                print(f"[!] Warning: kubectl delete jobs returned code {delete_result.returncode}")
                print(f"    stderr: {delete_result.stderr}")
        else:
            print(f"[✓] No jobs found in namespace {KUBERNETES_NAMESPACE}")
            
    except subprocess.TimeoutExpired:
        print("[✗] Timeout during Kubernetes cleanup")
    except Exception as e:
        print(f"[✗] Error during Kubernetes cleanup: {e}")


def cleanup_temporary_files():
    """Clean up temporary files and directories, being careful about logs."""
    try:
        # Clean up lithops temp files but preserve logs
        lithops_temp_dirs = [
            "/tmp/lithops-*/runtime",
            "/tmp/lithops-*/storage", 
            "/tmp/lithops-*/functions"
        ]
        
        for temp_pattern in lithops_temp_dirs:
            result = subprocess.run(
                ["bash", "-c", f"find /tmp -path '{temp_pattern}' -type d -exec rm -rf {{}} + 2>/dev/null || true"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
        # Clean up flexecutor temp files
        result = subprocess.run(
            ["bash", "-c", "find /tmp -name 'flexecutor-*' -type d -exec rm -rf {} + 2>/dev/null || true"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"[✓] Cleaned up temporary files (preserved logs)")
                
    except Exception as e:
        print(f"[!] Warning during temporary file cleanup: {e}")
        # Don't fail the entire process for cleanup issues


def cleanup_per_worker_profiling_folders():
    """Clean up any per-worker profiling folders that may have been created by the framework."""
    profiling_base = "/home/users/iarriazu/flexecutor-main/examples/montecarlo_pi_estimation/profiling"
    
    try:
        if not os.path.exists(profiling_base):
            return
            
        # Look for folders matching the pattern montecarlo_pi_estimation_*workers
        import glob
        worker_folders = glob.glob(os.path.join(profiling_base, "montecarlo_pi_estimation_*workers"))
        
        if worker_folders:
            print(f"[🧹] Found {len(worker_folders)} per-worker profiling folders to clean up")
            for folder in worker_folders:
                try:
                    import shutil
                    shutil.rmtree(folder)
                    folder_name = os.path.basename(folder)
                    print(f"[✓] Removed per-worker folder: {folder_name}")
                except Exception as e:
                    folder_name = os.path.basename(folder)
                    print(f"[!] Failed to remove {folder_name}: {e}")
        else:
            print(f"[✓] No per-worker profiling folders found to clean up")
            
    except Exception as e:
        print(f"[!] Error during per-worker folder cleanup: {e}")


def full_cleanup():
    """Perform complete cleanup of all resources."""
    print("\n" + "="*80)
    print("🧹 STARTING COMPREHENSIVE CLEANUP")
    print("="*80)
    
    print("\n[1/4] Cleaning up MinIO storage...")
    cleanup_minio_storage()
    
    print("\n[2/4] Cleaning up Kubernetes resources...")
    cleanup_kubernetes_resources()
    
    print("\n[3/4] Cleaning up temporary files...")
    cleanup_temporary_files()
    
    print("\n[4/4] Cleaning up per-worker profiling folders...")
    cleanup_per_worker_profiling_folders()
    
    print("\n[✓] Cleanup completed")
    print("="*80)


def run_monte_carlo_pi_estimation(num_workers):
    """Run the Monte Carlo Pi estimation with specified number of workers."""
    
    @flexorchestrator(bucket=MINIO_BUCKET)
    def monte_carlo_pi_workflow():
        # Use a consistent DAG name to avoid creating multiple profiling folders
        dag = DAG("montecarlo_pi_estimation")

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
        
        # Execute with profiling to measure performance
        results = executor.execute_with_profiling(num_workers=num_workers)
 
        executor.shutdown()
        
        return results

    return monte_carlo_pi_workflow()


def run_simulation_with_timeout(num_workers):
    """Run a single pi estimation configuration with timeout."""
    config_name = f"pi_estimation_{num_workers}workers"
    
    print(f"\n🚀 Starting {config_name}")
    print(f"   Workers: {num_workers}")
    print(f"   Duration: {EXECUTION_TIME_MINUTES} minutes")
    print("-" * 60)
    
    start_time = time.time()
    simulation_completed = False
    timeout_occurred = False
    results = None
    partial_results = None
    
    def timeout_handler():
        nonlocal timeout_occurred
        timeout_occurred = True
        print(f"\n[⏰] {EXECUTION_TIME_MINUTES} minute timeout reached for {config_name}")
        print(f"   Collecting partial results...")
    
    # Set up timeout
    timer = Timer(EXECUTION_TIME_SECONDS, timeout_handler)
    timer.start()
    
    try:
        # Run the simulation
        print(f"🎯 Running Pi estimation with {num_workers} workers")
        results = run_monte_carlo_pi_estimation(num_workers)
        simulation_completed = True
        
        # Cancel timeout since we completed
        timer.cancel()
        
        elapsed_time = time.time() - start_time
        
        print(f"[✓] {config_name} completed successfully in {elapsed_time:.1f}s")
        
        # Extract detailed timing data
        timing_data = None
        if results and "monte_carlo_pi_stage" in results:
            timing_results = results["monte_carlo_pi_stage"].get_timings()
            print(f"   📊 Timings: {len(timing_results)} workers completed")
            if timing_results:
                avg_compute_time = sum(t.compute for t in timing_results) / len(timing_results)
                total_compute_time = sum(t.compute for t in timing_results)
                avg_read_time = sum(t.read for t in timing_results) / len(timing_results)
                total_read_time = sum(t.read for t in timing_results)
                completion_rate = len(timing_results) / num_workers
                
                print(f"   ⏱️  Average compute time per worker: {avg_compute_time:.2f}s")
                print(f"   🔄 Total compute time across workers: {total_compute_time:.2f}s")
                print(f"   📈 Completion rate: {len(timing_results)}/{num_workers} ({completion_rate:.1%})")
                
                # Calculate performance metrics
                throughput = len(timing_results) / elapsed_time
                efficiency = throughput / num_workers
                print(f"   🚀 Throughput: {throughput:.2f} workers/sec")
                print(f"   💯 Efficiency: {efficiency:.3f}")
                
                # Prepare detailed timing data
                timing_data = {
                    "worker_count": len(timing_results),
                    "average_compute_time": avg_compute_time,
                    "total_compute_time": total_compute_time,
                    "average_read_time": avg_read_time,
                    "total_read_time": total_read_time,
                    "completion_rate": completion_rate,
                    "throughput": throughput,
                    "efficiency": efficiency,
                    "individual_timings": [
                        {
                            "compute": t.compute,
                            "read": t.read,
                            "total": t.compute + t.read
                        } for t in timing_results
                    ]
                }
        
        return {"status": "completed", "execution_time": elapsed_time, "timing_data": timing_data, "results": results}
            
    except Exception as e:
        timer.cancel()
        elapsed_time = time.time() - start_time
        
        # Try to get partial results even if there was an error
        try:
            if timeout_occurred:
                print(f"[⏰] {config_name} timed out after {elapsed_time:.1f}s")
                print(f"   Attempting to collect partial results...")
                return {"status": "timeout", "execution_time": elapsed_time, "timing_data": None, "results": results}
            else:
                print(f"[✗] {config_name} failed after {elapsed_time:.1f}s: {e}")
                import traceback
                print(f"   Error details: {traceback.format_exc()}")
                return {"status": "failed", "execution_time": elapsed_time, "timing_data": None, "results": None, "error": str(e)}
        except Exception as partial_error:
            print(f"[✗] Failed to collect partial results: {partial_error}")
            return {"status": "failed", "execution_time": elapsed_time, "timing_data": None, "results": None, "error": str(e)}
    
    finally:
        # Ensure timer is cancelled
        if timer.is_alive():
            timer.cancel()

# determines the format of the profiling data : ##JSON## 
def save_comprehensive_profiling_data(all_results):
    """Save comprehensive profiling data to a single JSON file in Titanic-like format."""
    profiling_file = "/home/users/iarriazu/flexecutor-main/examples/montecarlo_pi_estimation/profiling/montecarlo/stage.json"
    
    try:
        # Create the profiling directory structure
        profiling_dir = "/home/users/iarriazu/flexecutor-main/examples/montecarlo_pi_estimation/profiling/montecarlo"
        os.makedirs(profiling_dir, exist_ok=True)
        
        # Create comprehensive profiling data structure similar to Titanic format
        profiling_data = {}
        
        for worker_count, result_data in all_results.items():
            # Create key in format similar to Titanic: (cpu, memory, workers)
            worker_key = f"(1, 1024, {worker_count})"
            
            profiling_data[worker_key] = {
                "execution_time": [result_data.get("execution_time", 0)],
                "status": [result_data.get("status", "unknown")],
                "worker_count": [worker_count],
                "timeout_minutes": [EXECUTION_TIME_MINUTES],
                "simulation_type": ["PI_ESTIMATION"]
            }
            
            # Add timing data if available
            if result_data.get("timing_data"):
                profiling_data[worker_key]["timing_data"] = [result_data["timing_data"]]
            
            # Add error information if present
            if "error" in result_data:
                profiling_data[worker_key]["error"] = [result_data["error"]]
            
            # Add note for timeout cases
            if result_data.get("status") == "timeout":
                profiling_data[worker_key]["note"] = [f"Timed out after {EXECUTION_TIME_MINUTES} minutes - may have partial results"]
            
            # Add timestamp
            profiling_data[worker_key]["timestamp"] = [time.strftime("%Y-%m-%d %H:%M:%S")]
        
        # Save the comprehensive data
        with open(profiling_file, 'w') as f:
            json.dump(profiling_data, f, indent=2)
            
        print(f"[✓] Comprehensive profiling data saved to {profiling_file}")
        print(f"[✓] Data structure matches Titanic format with keys like (1, 1024, {list(all_results.keys())[0]})")
        
    except Exception as e:
        print(f"[✗] Error saving comprehensive profiling data: {e}")


def save_results_summary(results):
    """Save a summary of all results to a JSON file."""
    summary_file = "/home/users/iarriazu/flexecutor-main/examples/montecarlo_pi_estimation/batch_execution_summary.json"
    
    try:
        # Convert the detailed results to simple summary format for backward compatibility
        summary_data = {"PI_ESTIMATION": {}}
        
        for worker_count, result_data in results.items():
            worker_key = f"{worker_count}_workers"
            summary_data["PI_ESTIMATION"][worker_key] = {
                "execution_time": result_data.get("execution_time", 0),
                "status": result_data.get("status", "unknown")
            }
            
            if result_data.get("status") == "timeout":
                summary_data["PI_ESTIMATION"][worker_key]["note"] = f"Timed out after {EXECUTION_TIME_MINUTES} minutes - may have partial results"
        
        summary_data["total_configurations"] = len(results)
        summary_data["execution_time_per_config_minutes"] = EXECUTION_TIME_MINUTES
        summary_data["worker_configurations"] = WORKER_CONFIGURATIONS
        summary_data["simulation_type"] = "PI_ESTIMATION"
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        print(f"[✓] Results summary saved to {summary_file}")
    except Exception as e:
        print(f"[✗] Error saving results summary: {e}")


def main():
    """Main execution function."""
    print("🎲 MONTE CARLO PI ESTIMATION BATCH EXECUTION STARTED")
    print("="*80)
    print(f"Worker configurations: {WORKER_CONFIGURATIONS}")
    print(f"Execution time per config: {EXECUTION_TIME_MINUTES} minutes")
    print(f"Total estimated time: {len(WORKER_CONFIGURATIONS) * EXECUTION_TIME_MINUTES} minutes")
    print("="*80)
    
    # Perform initial cleanup
    full_cleanup()
    
    execution_results = {}
    total_configs = len(WORKER_CONFIGURATIONS)
    current_config = 0
    
    try:
        for num_workers in WORKER_CONFIGURATIONS:
            current_config += 1
            
            print(f"\n📊 Configuration {current_config}/{total_configs}")
            print(f"   Progress: {(current_config/total_configs)*100:.1f}%")
            
            config_start_time = time.time()
            
            # Run the simulation and get detailed results
            result_data = run_simulation_with_timeout(num_workers)
            
            # Clean up any per-worker profiling folders immediately after execution
            cleanup_per_worker_profiling_folders()
            
            # Store the detailed results
            execution_results[num_workers] = result_data
            
            status = result_data.get("status", "unknown")
            execution_time = result_data.get("execution_time", 0)
            
            if status == "timeout":
                print(f"[⏰] Configuration {num_workers} workers: TIMED OUT (took {execution_time:.1f}s)")
            elif status == "completed":
                print(f"[✓] Configuration {num_workers} workers: SUCCESS (took {execution_time:.1f}s)")
            else:
                print(f"[✗] Configuration {num_workers} workers: FAILED (took {execution_time:.1f}s)")
            
            # Cleanup after each configuration
            print(f"\n🧹 Cleaning up after pi_estimation_{num_workers}workers...")
            full_cleanup()
            
            # Brief pause between configurations
            if current_config < total_configs:
                print(f"⏸️  Waiting 30 seconds before next configuration...")
                time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n[!] Batch execution interrupted by user")
        full_cleanup()
        
    except Exception as e:
        print(f"\n[✗] Error during batch execution: {e}")
        full_cleanup()
        
    finally:
        # Save comprehensive profiling data (Titanic-like format)
        save_comprehensive_profiling_data(execution_results)
        
        # Save execution summary (for backward compatibility)
        save_results_summary(execution_results)
        
        print("\n" + "="*80)
        print("🎯 MONTE CARLO PI ESTIMATION BATCH EXECUTION COMPLETED")
        print("="*80)
        print(f"Total configurations tested: {total_configs}")
        print(f"Worker configurations: {WORKER_CONFIGURATIONS}")
        print(f"Check comprehensive profiling: /home/users/iarriazu/flexecutor-main/examples/montecarlo_pi_estimation/profiling/montecarlo/stage.json")
        print(f"Check results summary: /home/users/iarriazu/flexecutor-main/examples/montecarlo_pi_estimation/batch_execution_summary.json")


if __name__ == "__main__":
    main()

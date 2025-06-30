"""
run_ml_workflow_with_cleanup_batch_execution.py

Runs the ML workflow with multiple worker configurations (16, 32, 64) sequentially,
cleaning up all execution artifacts after each run including:
- MinIO storage objects
- Kubernetes pods and jobs
- Temporary files
"""

import subprocess
import sys
import time
from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
MINIO_ENDPOINT    = "192.168.5.24:9000"  # Based on the logs from execution
MINIO_ACCESS_KEY  = "lab144"
MINIO_SECRET_KEY  = "astl1a4b4"
MINIO_BUCKET      = "test-bucket"
KUBERNETES_NAMESPACE = "lithops-jobs"
PYTHON_PATH = "/home/users/iarriazu/flexecutor-main/.venv/bin/python"
ML_SCRIPT_PATH = "/home/users/iarriazu/flexecutor-main/examples/ml/main_batch_execution..py"
# ───────────────────────────────────────────────────────────────────────────────

def run_ml_workflow_with_workers(worker_count):
    """Run the ML workflow with a specific number of workers by importing and calling the function."""
    print(f"[+] Starting ML workflow execution with {worker_count} workers...")
    
    try:
        # Import the function from the batch execution script
        import sys
        import os
        
        # Add the ML directory to Python path
        ml_dir = "/home/users/iarriazu/flexecutor-main/examples/ml"
        if ml_dir not in sys.path:
            sys.path.insert(0, ml_dir)
        
        # Import the function from the batch execution script
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_batch_execution", 
                                                     "/home/users/iarriazu/flexecutor-main/examples/ml/main_batch_execution..py")
        main_batch_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_batch_module)
        run_workflow = main_batch_module.run_ml_workflow_with_workers
        
        # Run the workflow with the specified worker count
        success = run_workflow(worker_count)
        
        if success:
            print(f"[✓] ML workflow with {worker_count} workers completed successfully")
            return True
        else:
            print(f"[✗] ML workflow with {worker_count} workers failed")
            return False
            
    except Exception as e:
        print(f"[✗] Error running ML workflow with {worker_count} workers: {e}")
        return False

def cleanup_minio_objects():
    """Clean up MinIO storage objects created during execution."""
    print("[+] Starting MinIO cleanup...")
    
    try:
        # Connect to MinIO
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,  # Using http:// not https://
        )
        
        # Check if bucket exists
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"[!] Bucket '{MINIO_BUCKET}' does not exist, skipping MinIO cleanup")
            return
            
        print(f"[+] Connected to MinIO at {MINIO_ENDPOINT}")
        
        # List of prefixes to clean up (ML workflow artifacts)
        # NOTE: We preserve the input data 'training-data/' prefix
        temp_prefixes = [
            "training-data-transform",
            "vectors-pca", 
            "models",
            "predictions",
            "accuracies",
            "forests",
            "lithops.jobs",
            "lithops.runtimes"
        ]
        
        for prefix in temp_prefixes:
            # List all objects under this prefix
            objects = list(client.list_objects(MINIO_BUCKET, prefix=prefix, recursive=True))
            if not objects:
                print(f"[+] No objects found under prefix: {prefix!r}")
                continue

            # Wrap each object_name in a DeleteObject
            to_delete = [DeleteObject(obj.object_name) for obj in objects]
            print(f"[+] Deleting {len(to_delete)} objects under prefix: {prefix!r}")

            # Bulk-delete
            errors = client.remove_objects(MINIO_BUCKET, to_delete)
            for err in errors:
                print(f"    ✗ Failed to delete {err.object_name}: {err}")
            print(f"[✓] Cleaned up prefix: {prefix!r}")
            
        print("[✓] MinIO cleanup completed")
        
    except S3Error as err:
        print(f"[✗] MinIO cleanup error: {err}")
    except Exception as e:
        print(f"[✗] Unexpected error during MinIO cleanup: {e}")

def cleanup_kubernetes_resources():
    """Clean up Kubernetes pods and jobs created during execution."""
    print("[+] Starting Kubernetes cleanup...")
    
    try:
        # Get all lithops-related pods
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", KUBERNETES_NAMESPACE, "-o", "name"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"[!] Could not list Kubernetes pods: {result.stderr}")
            return
            
        pods = result.stdout.strip().split('\n') if result.stdout.strip() else []
        lithops_pods = [pod for pod in pods if 'lithops' in pod.lower()]
        
        if lithops_pods:
            print(f"[+] Found {len(lithops_pods)} Lithops pods to clean up")
            for pod in lithops_pods:
                pod_name = pod.replace('pod/', '')
                print(f"[+] Deleting pod: {pod_name}")
                subprocess.run(
                    ["kubectl", "delete", "pod", pod_name, "-n", KUBERNETES_NAMESPACE],
                    capture_output=True
                )
        else:
            print("[+] No Lithops pods found to clean up")
            
        # Get all lithops-related jobs
        result = subprocess.run(
            ["kubectl", "get", "jobs", "-n", KUBERNETES_NAMESPACE, "-o", "name"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            jobs = result.stdout.strip().split('\n') if result.stdout.strip() else []
            lithops_jobs = [job for job in jobs if 'lithops' in job.lower()]
            
            if lithops_jobs:
                print(f"[+] Found {len(lithops_jobs)} Lithops jobs to clean up")
                for job in lithops_jobs:
                    job_name = job.replace('job.batch/', '')
                    print(f"[+] Deleting job: {job_name}")
                    subprocess.run(
                        ["kubectl", "delete", "job", job_name, "-n", KUBERNETES_NAMESPACE],
                        capture_output=True
                    )
            else:
                print("[+] No Lithops jobs found to clean up")
                
        print("[✓] Kubernetes cleanup completed")
        
    except Exception as e:
        print(f"[✗] Kubernetes cleanup error: {e}")

def cleanup_temp_files():
    """Clean up temporary files created during execution."""
    print("[+] Starting temporary files cleanup...")
    
    try:
        # Clean up lithops temporary logs
        subprocess.run(
            ["find", "/tmp", "-name", "*lithops*", "-type", "f", "-delete"],
            capture_output=True
        )
        
        # Clean up any .pyc files in the examples directory
        subprocess.run(
            ["find", "/home/users/iarriazu/flexecutor-main/examples", "-name", "*.pyc", "-delete"],
            capture_output=True
        )
        
        print("[✓] Temporary files cleanup completed")
        
    except Exception as e:
        print(f"[✗] Temporary files cleanup error: {e}")

def run_single_worker_configuration(worker_count):
    """Run ML workflow with a specific worker configuration and clean up afterwards."""
    print(f"\n{'='*80}")
    print(f"EXECUTING WORKER CONFIGURATION: {worker_count} WORKERS")
    print(f"{'='*80}")
    
    # Step 1: Run the ML workflow with specific worker count
    workflow_success = run_ml_workflow_with_workers(worker_count)
    
    # Step 2: Wait a moment for resources to settle
    print(f"[+] Waiting 10 seconds for resources to settle after {worker_count} workers execution...")
    time.sleep(10)
    
    # Step 3: Clean up regardless of workflow success
    print(f"\n{'='*60}")
    print(f"STARTING CLEANUP PHASE FOR {worker_count} WORKERS")
    print(f"{'='*60}")
    
    cleanup_minio_objects()
    cleanup_kubernetes_resources()
    cleanup_temp_files()
    
    # Step 4: Additional wait to ensure cleanup is complete
    print(f"[+] Waiting 5 seconds for cleanup to complete...")
    time.sleep(5)
    
    print(f"\n{'='*60}")
    if workflow_success:
        print(f"✓ WORKER CONFIGURATION {worker_count}: COMPLETED SUCCESSFULLY AND CLEANED UP")
    else:
        print(f"✗ WORKER CONFIGURATION {worker_count}: FAILED BUT CLEANUP COMPLETED")
    print(f"{'='*60}")
    
    return workflow_success

def main():
    """Main execution function for batch processing with multiple worker configurations."""
    # Define worker configurations to test
    # worker_configurations = [1, 2, 4, 8, 10, 12, 16, 20, 22, 24, 28, 32]# important: 
    worker_configurations = [1, 2, 4, 8, 12 ]# important: 
    # worker_configurations = [1, 2, 4, 8, 12, 16, 20, 24]# important: 
    # worker_configurations = [16, 22, 32, 64, 128, 256]# important: 
    
    print("="*100)
    print("BATCH ML WORKFLOW EXECUTION WITH CLEANUP")
    print("SEQUENTIAL EXECUTION WITH WORKER CONFIGURATIONS: 16, 32, 64")
    print("="*100)
    print(f"Worker configurations to test: {worker_configurations}")
    print("Each configuration will run completely and clean up before starting the next one.")
    
    results = {}
    
    for i, worker_count in enumerate(worker_configurations, 1):
        print(f"\n{'='*100}")
        print(f"BATCH PROGRESS: {i}/{len(worker_configurations)} - WORKER CONFIGURATION {worker_count}")
        print(f"{'='*100}")
        
        try:
            # Run the workflow with current worker configuration and cleanup``
            success = run_single_worker_configuration(worker_count)
            results[worker_count] = success
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                
            # Wait between configurations to ensure complete separation
            if i < len(worker_configurations):  # Don't wait after the last one
                print(f"[+] Waiting 15 seconds before starting next worker configuration...")
                time.sleep(15)
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            results[worker_count] = False
    
    # Print final summary
    print("\n" + "="*100)
    print("BATCH EXECUTION FINAL SUMMARY")
    print("="*100)
    
    for worker_count, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"Workers {worker_count:2d}: {status}")
    
    successful_runs = sum(1 for success in results.values() if success)
    total_runs = len(results)
    
    print(f"\nTotal successful runs: {successful_runs}/{total_runs}")
    
    if successful_runs == total_runs:
        print("✓ ALL WORKER CONFIGURATIONS COMPLETED SUCCESSFULLY!")
        return_code = 0
    else:
        print("✗ SOME WORKER CONFIGURATIONS FAILED.")
        return_code = 1
    
    print("="*100)
    return return_code

if __name__ == "__main__":
    sys.exit(main())

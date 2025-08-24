"""
run_titanic_workflow_with_cleanup_batch_execution.py

Runs the Titanic workflow with multiple worker configurations sequentially,
cleaning up all execution artifacts after each run including:
- MinIO storage objects
- Kubernetes pods and jobs
- Temporary files
"""

import subprocess
import sys
import time
import os
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
TITANIC_SCRIPT_PATH = "/home/users/iarriazu/flexecutor-main/examples/titanic/main_batch_execution.py"
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

def print_input_file_info():
    """Print information about the input files to be processed."""
    print(f"\n{'='*60}")
    print("INPUT FILE INFORMATION")
    print(f"{'='*60}")
    
    objects, total_size = get_minio_file_info("titanic")
    
    if objects:
        print(f"[+] Found {len(objects)} file(s) in 'titanic' prefix:")
        for obj in objects:
            size_mb = obj.size / (1024 * 1024)
            print(f"    - {obj.object_name}: {size_mb:.2f} MB ({obj.size:,} bytes)")
        
        total_size_mb = total_size / (1024 * 1024)
        print(f"[+] Total input data size: {total_size_mb:.2f} MB ({total_size:,} bytes)")
    else:
        print("[!] No input files found in 'titanic' prefix")
        print("[+] Uploading default titanic data file...")
        
        try:
            client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False,
            )
            
            if not client.bucket_exists(MINIO_BUCKET):
                client.make_bucket(MINIO_BUCKET)
            
            local_file = "/home/users/iarriazu/flexecutor-main/test-bucket/titanic/titanic.csv"
            object_name = "titanic/titanic.csv"
            
            client.fput_object(
                MINIO_BUCKET,
                object_name,
                local_file
            )
            print(f"[✓] Successfully uploaded {local_file} to MinIO as {object_name}")
            
            # Refresh file info after upload
            objects, total_size = get_minio_file_info("titanic")
            if objects:
                print(f"[+] Now found {len(objects)} file(s) in 'titanic' prefix")
        except Exception as e:
            print(f"[✗] Error uploading titanic data file: {e}")
    
    print(f"{'='*60}")

def print_results_info():
    """Print information about the result files before cleanup."""
    print(f"\n{'='*60}")
    print("RESULTS INFORMATION (Before Cleanup)")
    print(f"{'='*60}")
    
    # Check results from different prefixes
    result_prefixes = ["titanic-accuracy", "lithops.jobs", "lithops.runtimes"]
    
    total_files = 0
    total_size = 0
    
    for prefix in result_prefixes:
        objects, size = get_minio_file_info(prefix)
        if objects:
            size_mb = size / (1024 * 1024)
            print(f"[+] {prefix} prefix: {len(objects)} file(s), {size_mb:.2f} MB")
            for obj in objects:
                obj_size_mb = obj.size / (1024 * 1024)
                print(f"    - {obj.object_name}: {obj_size_mb:.2f} MB")
            total_files += len(objects)
            total_size += size
        else:
            print(f"[+] {prefix} prefix: No files found")
    
    if total_files > 0:
        total_size_mb = total_size / (1024 * 1024)
        print(f"\n[+] TOTAL RESULTS: {total_files} file(s), {total_size_mb:.2f} MB ({total_size:,} bytes)")
    else:
        print("\n[!] No result files found")
    
    print(f"{'='*60}")

def run_titanic_workflow_with_workers(worker_count):
    """Run the Titanic workflow with a specific number of workers by importing and calling the function."""
    print(f"[+] Starting Titanic workflow execution with {worker_count} workers...")
    
    try:
        import signal
        import sys
        import os
        
        # Add timeout handler
        def timeout_handler(signum, frame):
            print(f"[✗] Workflow execution timed out after 10 minutes")
            raise TimeoutError("Workflow execution timed out")
        
        # Set timeout to 10 minutes
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(600)  # 10 minutes
        
        # Add the Titanic directory to Python path
        titanic_dir = "/home/users/iarriazu/flexecutor-main/examples/titanic"
        if titanic_dir not in sys.path:
            sys.path.insert(0, titanic_dir)
        
        # Import the function from the batch execution script
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_batch_execution", 
                                                     "/home/users/iarriazu/flexecutor-main/examples/titanic/main_batch_execution.py")
        main_batch_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_batch_module)
        run_workflow = main_batch_module.run_titanic_workflow_with_workers
        
        # Run the workflow with the specified worker count
        success = run_workflow(worker_count)
        
        # Cancel the alarm
        signal.alarm(0)
        
        if success:
            print(f"[✓] Titanic workflow with {worker_count} workers completed successfully")
            return True
        else:
            print(f"[✗] Titanic workflow with {worker_count} workers failed")
            return False
            
    except TimeoutError as e:
        print(f"[✗] Titanic workflow with {worker_count} workers timed out: {e}")
        # Force cleanup of stuck resources
        cleanup_kubernetes_resources()
        return False
    except Exception as e:
        print(f"[✗] Error running Titanic workflow with {worker_count} workers: {e}")
        # Cancel the alarm in case of other errors
        try:
            signal.alarm(0)
        except:
            pass
        return False

def cleanup_minio_objects(clean_all=False):
    """Clean up MinIO storage objects created during execution.
    If clean_all=True, deletes ALL objects in the bucket."""
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
        
        if clean_all:
            # Delete ALL objects in the bucket
            objects = list(client.list_objects(MINIO_BUCKET, recursive=True))
            if not objects:
                print("[+] No objects found in bucket")
                return

            to_delete = [DeleteObject(obj.object_name) for obj in objects]
            print(f"[+] Deleting ALL {len(to_delete)} objects in bucket")
        else:
            # List of prefixes to clean up (Titanic workflow artifacts)
            # NOTE: We preserve the input data 'titanic/' prefix
            temp_prefixes = [
                "titanic-accuracy",
                "lithops.jobs",
                "lithops.runtimes"
            ]
            
            to_delete = []
            for prefix in temp_prefixes:
                objects = list(client.list_objects(MINIO_BUCKET, prefix=prefix, recursive=True))
                if objects:
                    to_delete.extend([DeleteObject(obj.object_name) for obj in objects])
                    print(f"[+] Found {len(objects)} objects under prefix: {prefix!r}")
                else:
                    print(f"[+] No objects found under prefix: {prefix!r}")

        if to_delete:
            # Bulk-delete
            errors = client.remove_objects(MINIO_BUCKET, to_delete)
            error_count = 0
            for err in errors:
                print(f"    ✗ Failed to delete {err.object_name}: {err}")
                error_count += 1
            
            if error_count == 0:
                print(f"[✓] Successfully deleted {len(to_delete)} objects")
            else:
                print(f"[!] Deleted {len(to_delete) - error_count}/{len(to_delete)} objects ({error_count} errors)")
        else:
            print("[+] No objects to delete")
            
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

def cleanup_unwanted_titanic_input_files():
    """Clean up unwanted files in the titanic prefix, keeping only titanic/titanic.csv."""
    print("[+] Starting cleanup of unwanted titanic input files...")
    
    try:
        # Connect to MinIO
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )
        
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"[!] Bucket '{MINIO_BUCKET}' does not exist, skipping cleanup")
            return
            
        print(f"[+] Connected to MinIO at {MINIO_ENDPOINT}")
        
        # List all objects under titanic prefix
        objects = list(client.list_objects(MINIO_BUCKET, prefix="titanic", recursive=True))
        if not objects:
            print("[+] No objects found under titanic prefix")
            return

        # Filter objects to delete (everything except titanic/titanic.csv)
        target_file = "titanic/titanic.csv"
        objects_to_delete = []
        
        print(f"[+] Found {len(objects)} object(s) under titanic prefix:")
        for obj in objects:
            size_mb = obj.size / (1024 * 1024)
            if obj.object_name == target_file:
                print(f"    ✓ KEEPING: {obj.object_name}: {size_mb:.2f} MB ({obj.size:,} bytes)")
            else:
                print(f"    ✗ DELETING: {obj.object_name}: {size_mb:.2f} MB ({obj.size:,} bytes)")
                objects_to_delete.append(DeleteObject(obj.object_name))
        
        if not objects_to_delete:
            print("[+] No unwanted files found to delete")
            return
            
        # Bulk delete unwanted files
        print(f"[+] Deleting {len(objects_to_delete)} unwanted file(s)...")
        errors = client.remove_objects(MINIO_BUCKET, objects_to_delete)
        error_count = 0
        for err in errors:
            print(f"    ✗ Failed to delete {err.object_name}: {err}")
            error_count += 1
            
        if error_count == 0:
            print(f"[✓] Successfully deleted {len(objects_to_delete)} unwanted file(s)")
        else:
            print(f"[!] Deleted {len(objects_to_delete) - error_count}/{len(objects_to_delete)} files ({error_count} errors)")
            
        # Show final state
        print(f"\n[+] Final state of titanic prefix:")
        remaining_objects = list(client.list_objects(MINIO_BUCKET, prefix="titanic", recursive=True))
        for obj in remaining_objects:
            size_mb = obj.size / (1024 * 1024)
            print(f"    - {obj.object_name}: {size_mb:.2f} MB ({obj.size:,} bytes)")
        
        print("[✓] Titanic input files cleanup completed")
        
    except S3Error as err:
        print(f"[✗] MinIO cleanup error: {err}")
    except Exception as e:
        print(f"[✗] Unexpected error during titanic input cleanup: {e}")

def debug_workflow_status():
    """Debug function to check the status of stuck workflows."""
    print(f"\n{'='*60}")
    print("DEBUGGING WORKFLOW STATUS")
    print(f"{'='*60}")
    
    try:
        # Check Kubernetes pods
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", "inigo-jobs-energy", "--no-headers"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lithops_pods = [line for line in result.stdout.strip().split('\n') if 'lithops' in line and line.strip()]
            print(f"[+] Found {len(lithops_pods)} lithops pods:")
            
            running_count = 0
            completed_count = 0
            for pod_line in lithops_pods:
                parts = pod_line.split()
                pod_name = parts[0]
                status = parts[2] if len(parts) > 2 else "Unknown"
                age = parts[4] if len(parts) > 4 else "Unknown"
                
                if 'Running' in status:
                    running_count += 1
                elif 'Completed' in status:
                    completed_count += 1
                    
                print(f"    {pod_name}: {status} (Age: {age})")
            
            print(f"[+] Summary: {running_count} Running, {completed_count} Completed")
            
            # Check if pods are stuck (running for more than 5 minutes)
            stuck_pods = []
            for pod_line in lithops_pods:
                parts = pod_line.split()
                if len(parts) > 4 and 'Running' in parts[2]:
                    age = parts[4]
                    if 'm' in age:
                        minutes = int(age.replace('m', ''))
                        if minutes > 5:
                            stuck_pods.append(parts[0])
            
            if stuck_pods:
                print(f"[!] WARNING: {len(stuck_pods)} pods appear stuck (running >5min):")
                for pod in stuck_pods:
                    print(f"    - {pod}")
                    
        else:
            print(f"[✗] Error checking pods: {result.stderr}")
            
    except Exception as e:
        print(f"[✗] Error in debug function: {e}")
    
    print(f"{'='*60}")

def run_single_worker_configuration(worker_count):
    """Run Titanic workflow with a specific worker configuration and clean up afterwards."""
    print(f"\n{'='*80}")
    print(f"EXECUTING WORKER CONFIGURATION: {worker_count} WORKERS")
    print(f"{'='*80}")
    
    # Step 0: Print input file information
    print_input_file_info()
    
    # Step 1: Run the Titanic workflow with specific worker count
    workflow_success = run_titanic_workflow_with_workers(worker_count)
    
    # Step 2: Print results information before cleanup
    if workflow_success:
        print_results_info()
    
    # Step 3: Wait a moment for resources to settle
    print(f"[+] Waiting 10 seconds for resources to settle after {worker_count} workers execution...")
    time.sleep(10)
    
    # Step 4: Clean up regardless of workflow success
    print(f"\n{'='*60}")
    print(f"STARTING CLEANUP PHASE FOR {worker_count} WORKERS")
    print(f"{'='*60}")
    
    cleanup_minio_objects()
    cleanup_kubernetes_resources()
    cleanup_temp_files()
    
    # Step 5: Additional wait to ensure cleanup is complete
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
    # worker_configurations = [6, 8, 12, 16, 20, 24]
    # worker_configurations = [1, 2, 3, 4, 5, 6, 8, 12, 16, 20, 24, 28, 32]
    # worker_configurations = [32, 28, 24, 20, 16, 12, 8, 6, 5, 4, 3, 2, 1]
    # worker_configurations = [  20, 16, 12, 8, 6, 5, 4, 3, 2, 1]
    # worker_configurations = [ 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    # worker_configurations = [   10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    # worker_configurations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    worker_configurations = [   
        # 1, 2, 3, 4, 5, 6, 7,
        8, 9, 10 , 12, 16, 20, 24, 28
        # , 
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28,  
        # 8, 9, 10 , 12, 16, 20, 24, 28 # 32 el limite 
    ]   
    

    print("="*100)
    print("BATCH TITANIC WORKFLOW EXECUTION WITH CLEANUP")
    print("SEQUENTIAL EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS")
    print("="*100)
    print(f"Worker configurations to test: {worker_configurations}")
    print("Each configuration will run completely and clean up before starting the next one.")
    
    results = {}
    
    for i, worker_count in enumerate(worker_configurations, 1):
        print(f"\n{'='*100}")
        print(f"BATCH PROGRESS: {i}/{len(worker_configurations)} - WORKER CONFIGURATION {worker_count}")
        print(f"{'='*100}")
        
        try:
            # Run the workflow with current worker configuration and cleanup
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
    print("BATCH EXECUTION FINAL SUMMARY - TITANIC")
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Titanic workflow or cleanup files')
    parser.add_argument('--cleanup-input', action='store_true', 
                       help='Clean up unwanted titanic input files (keep only titanic/titanic.csv)')
    parser.add_argument('--cleanup-all', action='store_true',
                       help='Clean up ALL objects in MinIO bucket')
    
    args = parser.parse_args()
    
    # caso elementos extra / borrados 
    # if args.cleanup_all:
    #     print("="*80)
    #     print("CLEANING UP ALL MINIO OBJECTS")
    #     print("="*80)
    #     cleanup_minio_objects(clean_all=True)
    #     print("="*80)
    #     sys.exit(0)
    
    # elif args.cleanup_input:
    if args.cleanup_input:
        print("="*80)
        print("CLEANING UP UNWANTED TITANIC INPUT FILES")
        print("="*80)
        cleanup_unwanted_titanic_input_files()
        print("="*80)
        sys.exit(0)
    else:
        sys.exit(main())

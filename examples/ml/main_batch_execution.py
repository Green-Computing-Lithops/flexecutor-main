import sys
import os
import shutil

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lithops_fork')))
from lithops import FunctionExecutor

from examples.ml.functions import pca, train_with_multiprocessing, aggregate, test
from flexecutor.storage.storage import FlexData, StrategyEnum
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
# Import the modified DAGExecutor class
from flexecutor.workflow.executor import DAGExecutor
# from flexecutor.workflow.executor_modified import DAGExecutor # executor esp
from flexecutor.workflow.stage import Stage
from flexecutor.scheduling.jolteon import Jolteon
from flexecutor.utils.dataclass import StageConfig

# Import the shared S3 cleanup utility
from examples.general_usage.aws_s3_cleanup import S3Cleaner

MEMORY = 2048
stage_memory = MEMORY
runtime_memory = MEMORY



def run_ml_workflow_with_workers(worker_count):
    """Run the ML workflow with a specific number of workers."""
    print(f"\n{'='*60}")
    print(f"STARTING ML WORKFLOW WITH {worker_count} WORKERS")
    print(f"{'='*60}")
    
    @flexorchestrator(bucket="lithops-us-east-1-45dk")
    def main():
        dag = DAG("ml")

        data_training = FlexData("training-data", suffix=".txt")
        data_vectors_pca = FlexData("vectors-pca")
        data_training_transform = FlexData(
            "training-data-transform", read_strategy=StrategyEnum.BROADCAST
        )
        data_models = FlexData("models")
        data_forests = FlexData("forests")
        data_predictions = FlexData("predictions")
        data_accuracies = FlexData("accuracies", suffix=".txt")

        stage0 = Stage(
            stage_id="stage0",
            func=pca,
            inputs=[data_training],
            outputs=[data_vectors_pca, data_training_transform],
            params={"n_components": 2},
            max_concurrency=1,
        )

        stage1 = Stage(
            stage_id="stage1",
            func=train_with_multiprocessing,
            inputs=[data_training_transform],
            outputs=[data_models],
        )

        stage2 = Stage(
            stage_id="stage2",
            func=aggregate,
            inputs=[data_training_transform, data_models],
            outputs=[data_forests, data_predictions],
        )

        stage3 = Stage(
            stage_id="stage3",
            func=test,
            inputs=[data_predictions, data_training_transform],
            outputs=[data_accuracies],
            max_concurrency=1,
        )

        stage0 >> [stage1, stage2, stage3]
        stage1 >> stage2
        stage2 >> stage3

        dag.add_stages([stage0, stage1, stage2, stage3])

        entry_point = [
            StageConfig(workers=workers, cpu=cpu)
            for workers, cpu in zip([1, worker_count, 8, 1], [3] * 4)
        ]
        x_bounds = [
            StageConfig(workers=workers, cpu=cpu)
            for workers, cpu in zip(
                [1, 0.5] + [4, 0.5] * 2 + [1, 0.5], [2, 4.1] + [32, 4.1] * 2 + [2, 4.1]
            )
        ]

        executor = DAGExecutor(
            dag,
            executor=FunctionExecutor(log_level="INFO", runtime_memory=runtime_memory),
            scheduler=Jolteon(
                dag,
                bound=40,
                bound_type="latency",
                cpu_search_space=[0.6, 1, 1.5, 2, 2.5, 3, 4],
                entry_point=entry_point,
                x_bounds=x_bounds,
            ),
        )

        # Skip optimization to avoid errors
        # executor.optimize()
        
        for i, stage in enumerate(dag.stages):
            stage.resource_config = StageConfig(cpu=4, memory=stage_memory, workers=worker_count)
        
        print(f"[+] Executing DAG with {worker_count} workers...")
        futures = executor.execute_with_profiling()
        
        executor.shutdown()
        print(f"[✓] ML workflow with {worker_count} workers completed successfully")
        
        # Clean up temporary S3 files after successful execution
        print(f"[+] Starting cleanup of temporary S3 files...")
        cleaner = S3Cleaner("lithops-us-east-1-45dk")
        cleanup_success, total_deleted = cleaner.global_cleanup()
        if cleanup_success:
            print(f"[✓] S3 cleanup completed for worker configuration {worker_count}")
        else:
            print(f"[!] S3 cleanup had warnings for worker configuration {worker_count}")
        
        return True

    try:
        return main()
    except Exception as e:
        error_msg = str(e)
        print(f"[✗] ML workflow with {worker_count} workers failed: {e}")
        return False

if __name__ == "__main__":
    worker_configurations = [
        20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
        20, 16, 12, 10, 9, 8, 7, 6, 5, 4
    ]
    print("="*80)
    print("BATCH EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    # Perform initial cleanup before starting batch execution
    print(f"\n{'='*80}")
    print("PERFORMING INITIAL S3 CLEANUP BEFORE BATCH EXECUTION")
    print(f"{'='*80}")
    print("[+] Running initial cleanup to remove any leftover temporary files...")
    cleaner = S3Cleaner("lithops-us-east-1-45dk")
    initial_cleanup_success, _ = cleaner.global_cleanup()
    
    if initial_cleanup_success:
        print("[✓] Initial S3 cleanup completed successfully")
    else:
        print("[!] Initial S3 cleanup completed with warnings")
    
    print(f"\n{'='*80}")
    print("STARTING BATCH EXECUTION")
    print(f"{'='*80}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Clean up any leftover files before starting new configuration
            print(f"\n[+] Pre-execution cleanup for {worker_count} workers...")
            cleaner = S3Cleaner("lithops-us-east-1-45dk")
            cleaner.global_cleanup()
            
            # Run the workflow with current worker configuration
            success = run_ml_workflow_with_workers(worker_count)
            results[worker_count] = success
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                # Clean up after failed execution
                print(f"[+] Post-failure cleanup for {worker_count} workers...")
                cleaner.global_cleanup()
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            results[worker_count] = False
            # Clean up after exception
            try:
                print(f"[+] Exception cleanup for {worker_count} workers...")
                cleaner = S3Cleaner("lithops-us-east-1-45dk")
                cleaner.global_cleanup()
            except:
                print(f"[!] Warning: Exception cleanup failed for {worker_count} workers")
    
    # Print final summary
    print("\n" + "="*80)
    print("BATCH EXECUTION SUMMARY")
    print("="*80)
    
    for worker_count, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"Workers {worker_count:2d}: {status}")
    
    successful_runs = sum(1 for success in results.values() if success)
    total_runs = len(results)
    
    print(f"\nTotal successful runs: {successful_runs}/{total_runs}")
    
    # Perform final comprehensive cleanup
    print(f"\n{'='*80}")
    print("PERFORMING FINAL COMPREHENSIVE S3 CLEANUP")
    print(f"{'='*80}")
    print("[+] Running final cleanup to ensure all temporary files are removed...")
    cleaner = S3Cleaner("lithops-us-east-1-45dk")
    final_cleanup_success, _ = cleaner.global_cleanup()
    
    if final_cleanup_success:
        print("[✓] Final S3 cleanup completed successfully")
    else:
        print("[!] Final S3 cleanup completed with warnings")
    
    if successful_runs == total_runs:
        print("✓ All worker configurations completed successfully!")
    else:
        print("✗ Some worker configurations failed.")

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

def run_ml_workflow_with_workers(worker_count):
    """Run the ML workflow with a specific number of workers."""
    print(f"\n{'='*60}")
    print(f"STARTING ML WORKFLOW WITH {worker_count} WORKERS")
    print(f"{'='*60}")
    
    @flexorchestrator(bucket="test-bucket")
    def main():
        dag = DAG("machine_learning")

        data_training = FlexData("training-data")
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
            # Explicitly set runtime_memory to ensure enough memory is allocated
            executor=FunctionExecutor(log_level="INFO", runtime_memory=2048, runtime="iarriazu/inigo_runtime_ml:latest"),
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
        
        # Set default configurations for each stage with increased memory
        for i, stage in enumerate(dag.stages):
            # Increase memory allocation to prevent OOM errors
            # First stage (PCA) needs more memory
            if stage.stage_id == "stage0":
                # number of workers 
                stage.resource_config = StageConfig(cpu=4, memory=2048, workers=worker_count)
            else:
                stage.resource_config = StageConfig(cpu=4, memory=2048, workers=worker_count)
        
        print(f"[+] Executing DAG with {worker_count} workers...")
        futures = executor.execute_with_profiling()
        
        executor.shutdown()
        print(f"[✓] ML workflow with {worker_count} workers completed successfully")
        return True

    try:
        return main()
    except Exception as e:
        print(f"[✗] ML workflow with {worker_count} workers failed: {e}")
        return False

if __name__ == "__main__":
    # Define worker configurations to test
    worker_configurations = [16, 32, 64]
    
    print("="*80)
    print("BATCH EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Run the workflow with current worker configuration
            success = run_ml_workflow_with_workers(worker_count)
            results[worker_count] = success
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            results[worker_count] = False
    
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
    
    if successful_runs == total_runs:
        print("✓ All worker configurations completed successfully!")
    else:
        print("✗ Some worker configurations failed.")

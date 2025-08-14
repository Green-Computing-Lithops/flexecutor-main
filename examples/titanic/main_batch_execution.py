import sys
import os

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lithops_fork')))
from lithops import FunctionExecutor

# pip install git+https://github.com/CLOUDLAB-URV/dataplug
from dataplug.formats.generic.csv import CSV
from dataplug.formats.generic.csv import partition_num_chunks as chunking_dynamic_csv

from examples.titanic.functions import train_model
from flexecutor.storage.chunker import Chunker
from flexecutor.storage.chunking_strategies import chunking_static_csv
from flexecutor.storage.storage import FlexData
from flexecutor.utils.enums import ChunkerTypeEnum
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage
from flexecutor.utils.dataclass import StageConfig

CHUNKER_TYPE = "DYNAMIC"  # DYNAMIC
memory_runtime = 2048


def run_titanic_workflow_with_workers(worker_count):
    """Run the Titanic workflow with a specific number of workers."""
    print(f"\n{'='*60}")
    print(f"STARTING TITANIC WORKFLOW WITH {worker_count} WORKERS")
    print(f"{'='*60}")
    
    if CHUNKER_TYPE == "STATIC":
        chunker = Chunker(
            chunker_type=ChunkerTypeEnum.STATIC,
            chunking_strategy=chunking_static_csv,
        )
    elif CHUNKER_TYPE == "DYNAMIC":
        chunker = Chunker(
            chunker_type=ChunkerTypeEnum.DYNAMIC,
            chunking_strategy=chunking_dynamic_csv,
            cloud_object_format=CSV,
        )
    else:
        raise ValueError(f"Chunker type {CHUNKER_TYPE} not supported")

    @flexorchestrator(bucket="lithops-us-east-1-45dk" )
    def main():
        dag = DAG("titanic")

        stage = Stage(
            stage_id="stage",
            func=train_model,
            inputs=[FlexData(prefix="titanic", chunker=chunker)],
            outputs=[
                FlexData(
                    prefix="titanic-accuracy",
                    suffix=".txt",
                )
            ],
        )

        dag.add_stage(stage)
        
        # Create executor with 512MB memory configuration from config file
        executor = DAGExecutor(
            dag, 
            executor=FunctionExecutor(
                config_file_path="/Users/arriazui/Desktop/GreenComputing/flexecutor-main/config_aws.yaml",
                log_level="INFO", 
                runtime_memory=memory_runtime
            )
        )

        # Set resource configuration for the stage with specified worker count
        # Memory allocation is handled by the config file (512MB)
        stage.resource_config = StageConfig(cpu=1, workers=worker_count)
        
        print(f"[+] Executing Titanic DAG with {worker_count} workers...")
        results = executor.execute_with_profiling(num_workers=worker_count)
        
        executor.shutdown()
        print(f"[✓] Titanic workflow with {worker_count} workers completed successfully")
        print(f"[+] Stage timings: {results['stage'].get_timings()}")
        return True

    try:
        return main()
    except Exception as e:
        print(f"[✗] Titanic workflow with {worker_count} workers failed: {e}")
        return False

if __name__ == "__main__":
    # Define worker configurations to test
    worker_configurations = [
         24, 20, 16, 12, 10, 9, 8, 7, 6, 5, 4,
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
    print("BATCH EXECUTION WITH MULTIPLE WORKER CONFIGURATIONS - TITANIC")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Run the workflow with current worker configuration
            success = run_titanic_workflow_with_workers(worker_count)
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
    print("BATCH EXECUTION SUMMARY - TITANIC")
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

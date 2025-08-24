#!/usr/bin/env python3

import sys
import os

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'lithops_fork')))
from lithops import FunctionExecutor

# Import the shared S3 cleanup utility
from examples.general_usage.aws_s3_cleanup import S3Cleaner

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

def test_titanic_workflow():
    """Test the Titanic workflow with a small number of workers to verify fixes."""
    print("="*60)
    print("TESTING TITANIC WORKFLOW WITH FIXES")
    print("="*60)
    
    # Test with 4 workers first
    worker_count = 4
    
    # Perform pre-execution cleanup
    print(f"[+] Performing pre-execution S3 cleanup...")
    cleaner = S3Cleaner("lithops-us-east-1-45dk")
    pre_cleanup_success, pre_deleted = cleaner.global_cleanup()
    if pre_cleanup_success:
        print(f"[✓] Pre-execution cleanup completed - {pre_deleted} files removed")
    else:
        print(f"[!] Pre-execution cleanup completed with warnings - {pre_deleted} files removed")
    
    # Use STATIC chunker to test our fixed chunking strategy
    chunker = Chunker(
        chunker_type=ChunkerTypeEnum.STATIC,
        chunking_strategy=chunking_static_csv,
    )

    @flexorchestrator(bucket="lithops-us-east-1-45dk")
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
        
        # Create executor with config file
        executor = DAGExecutor(
            dag, 
            executor=FunctionExecutor(
                config_file_path="/home/minirobbin/Desktop/GreenComputing/flexecutor-main/config_aws.yaml",
                log_level="INFO", 
                runtime_memory=512
            )
        )

        # Set resource configuration for the stage
        stage.resource_config = StageConfig(cpu=1, workers=worker_count)
        
        print(f"[+] Executing Titanic DAG with {worker_count} workers...")
        results = executor.execute_with_profiling(num_workers=worker_count)
        
        executor.shutdown()
        print(f"[✓] Titanic workflow with {worker_count} workers completed successfully")
        print(f"[+] Stage timings: {results['stage'].get_timings()}")
        
        return True

    try:
        result = main()
        print(f"[✓] Test completed successfully!")
        return result
    except Exception as e:
        print(f"[✗] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_titanic_workflow()
    if success:
        print("\n" + "="*60)
        print("✓ FIXES VERIFIED - WORKFLOW RUNS SUCCESSFULLY")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✗ FIXES NEED FURTHER ADJUSTMENT")
        print("="*60)

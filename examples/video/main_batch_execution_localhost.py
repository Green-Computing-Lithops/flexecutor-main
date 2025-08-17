import sys
import os
import shutil

# Set matplotlib backend before any imports that might use it
import matplotlib
matplotlib.use('Agg')

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lithops_fork')))
from lithops import FunctionExecutor

from examples.video.functions import (
    split_videos,
    extract_frames,
    sharpening_filter,
    classify_images,
)
from flexecutor.storage.storage import FlexData
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
# Import the modified DAGExecutor class
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage
from flexecutor.scheduling.jolteon import Jolteon
from flexecutor.utils.dataclass import StageConfig

memory_runtime = 2048


def run_video_workflow_with_workers(worker_count):
    """Run the video processing workflow with a specific number of workers."""
    print(f"\n{'='*60}")
    print(f"STARTING VIDEO WORKFLOW WITH {worker_count} WORKERS (LOCALHOST)")
    print(f"{'='*60}")
    
    # Create local storage directory if it doesn't exist
    local_storage = "/tmp/flexecutor-data"
    os.makedirs(local_storage, exist_ok=True)
    print(f"[+] Using local storage: {local_storage}")
    
    @flexorchestrator(bucket=local_storage)
    def main():
        dag = DAG("video_processing")

        data_videos = FlexData("videos")
        data_video_chunks = FlexData("video-chunks", suffix=".mp4")
        data_mainframes = FlexData("mainframes", suffix=".jpg")
        data_filtered_frames = FlexData("filtered-frames", suffix=".jpg")
        data_classification = FlexData("classification", suffix=".json")

        stage0 = Stage(
            stage_id="stage0",
            func=split_videos,
            inputs=[data_videos],
            outputs=[data_video_chunks],
            max_concurrency=1,
        )
        
        stage1 = Stage(
            stage_id="stage1",
            func=extract_frames,
            inputs=[data_video_chunks],
            outputs=[data_mainframes],
        )
        
        stage2 = Stage(
            stage_id="stage2",
            func=sharpening_filter,
            inputs=[data_mainframes],
            outputs=[data_filtered_frames],
        )
        
        stage3 = Stage(
            stage_id="stage3",
            func=classify_images,
            inputs=[data_filtered_frames],
            outputs=[data_classification],
            max_concurrency=1,
        )

        stage0 >> stage1 >> [stage2, stage3]
        stage2 >> stage3

        dag.add_stages([stage0, stage1, stage2, stage3])

        entry_point = [
            StageConfig(workers=workers, cpu=cpu)
            for workers, cpu in zip([1, worker_count, worker_count, 1], [3] * 4)
        ]
        x_bounds = [
            StageConfig(workers=workers, cpu=cpu)
            for workers, cpu in zip(
                [1, 0.5] + [4, 0.5] * 2 + [1, 0.5], [2, 4.1] + [32, 4.1] * 2 + [2, 4.1]
            )
        ]

        # Use local configuration
        executor = DAGExecutor(
            dag,
            # Use local configuration file and set runtime_memory for video processing
            executor=FunctionExecutor(
                config_file_path="config_local.yaml",
                log_level="INFO", 
                runtime_memory=memory_runtime
            ),
            scheduler=Jolteon(
                dag,
                bound=60,  # Increased bound for video processing
                bound_type="latency",
                cpu_search_space=[0.6, 1, 1.5, 2, 2.5, 3, 4],
                entry_point=entry_point,
                x_bounds=x_bounds,
            ),
        )

        # Skip optimization to avoid errors
        # executor.optimize()
        
        # Set default configurations for each stage with increased memory for video processing
        for i, stage in enumerate(dag.stages):
            # Video processing needs more memory and CPU
            if stage.stage_id == "stage0":  # Video splitting stage
                stage.resource_config = StageConfig(cpu=4, memory=memory_runtime, workers=1) # Use 1 worker for splitting
            elif stage.stage_id == "stage1":  # Frame extraction stage
                stage.resource_config = StageConfig(cpu=4, memory=memory_runtime, workers=worker_count)
            elif stage.stage_id == "stage2":  # Sharpening filter stage
                stage.resource_config = StageConfig(cpu=4, memory=memory_runtime, workers=worker_count)
            elif stage.stage_id == "stage3":  # Classification stage
                stage.resource_config = StageConfig(cpu=4, memory=memory_runtime, workers=1) # Use 1 worker for classification
        
        print(f"[+] Executing video processing DAG with {worker_count} workers (localhost)...")
        
        # Execute with profiling to capture RAPL measurements
        try:
            futures = executor.execute_with_profiling()
            print(f"[✓] Video workflow with {worker_count} workers completed successfully")
            return True
                
        except Exception as exec_error:
            print(f"[✗] Execution failed: {exec_error}")
            return False
        finally:
            executor.shutdown()

    try:
        return main()
    except Exception as e:
        print(f"[✗] Video workflow with {worker_count} workers failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test with a smaller set of worker configurations for localhost
    worker_configurations = [2, 4]  # Start with small numbers for localhost testing
    
    print("="*80)
    print("BATCH EXECUTION WITH LOCALHOST CONFIGURATION - VIDEO PROCESSING")
    print("="*80)
    print(f"Worker configurations to test: {worker_configurations}")
    
    results = {}
    
    for worker_count in worker_configurations:
        try:
            # Run the workflow with current worker configuration
            success = run_video_workflow_with_workers(worker_count)
            results[worker_count] = success
            
            if success:
                print(f"[✓] Worker configuration {worker_count}: SUCCESS")
            else:
                print(f"[✗] Worker configuration {worker_count}: FAILED")
                
        except Exception as e:
            print(f"[✗] Worker configuration {worker_count}: FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results[worker_count] = False
    
    # Print final summary
    print("\n" + "="*80)
    print("BATCH EXECUTION SUMMARY - VIDEO PROCESSING (LOCALHOST)")
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

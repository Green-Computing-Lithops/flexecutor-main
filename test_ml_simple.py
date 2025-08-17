#!/usr/bin/env python3
"""
Simplified ML test script to verify the runtime works with a single worker configuration
"""
import sys
import os

# Add the lithops_fork directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'lithops_fork')))
from lithops import FunctionExecutor

from examples.ml.functions import pca, train_with_multiprocessing, aggregate, test
from flexecutor.storage.storage import FlexData, StrategyEnum
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage
from flexecutor.scheduling.jolteon import Jolteon
from flexecutor.utils.dataclass import StageConfig

MEMORY = 512
stage_memory = MEMORY
runtime_memory = MEMORY

def run_simple_ml_workflow():
    """Run a simple ML workflow with 4 workers to test the runtime."""
    print(f"\n{'='*60}")
    print(f"TESTING ML WORKFLOW WITH 4 WORKERS")
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

        worker_count = 4
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
        
        return True

    try:
        return main()
    except Exception as e:
        error_msg = str(e)
        print(f"[✗] ML workflow failed: {e}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("SIMPLE ML WORKFLOW TEST")
    print("="*80)
    
    success = run_simple_ml_workflow()
    
    if success:
        print("✓ ML workflow test completed successfully!")
    else:
        print("✗ ML workflow test failed.")

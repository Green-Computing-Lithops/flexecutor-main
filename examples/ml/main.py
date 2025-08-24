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

if __name__ == "__main__":

    @flexorchestrator(bucket="lithops-us-east-1-45dk")
    def main():
      
        dag = DAG("ml")

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
            func=aggregate,# cantidad incluye el numero en funcion de la agg --> mas workers mas agg  mas consume
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
            for workers, cpu in zip([1, 16, 8, 1], [3] * 4)
        ]
        x_bounds = [
            StageConfig(workers=workers, cpu=cpu)
            for workers, cpu in zip(
                [1, 0.5] + [4, 0.5] * 2 + [1, 0.5], [2, 4.1] + [32, 4.1] * 2 + [2, 4.1]
            )
        ]

        executor = DAGExecutor(
            dag,
            # Use our new ml_aws_arm64 runtime with config file
            executor=FunctionExecutor(config_file='../../config_aws.yaml', log_level="INFO", runtime_memory=2048, runtime='ml_aws_lambda_arm_greencomp_v1'),
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
                stage.resource_config = StageConfig(cpu=4, memory=2048, workers=1) # 1, 4,  8,  x,   16, 123, 322,
            else:
                stage.resource_config = StageConfig(cpu=4, memory=2048, workers=1) # 4, 8, 32, 64,  128, 196, 256
        
        # print("\nExecuting DAG...") # if you comment this reduce so much the exectuton for futures 
        # executor.execute()
        futures = executor.execute_with_profiling() #avoid profiling + execute : all in one  
 
        executor.shutdown()

    main()

# pip install git+https://github.com/CLOUDLAB-URV/dataplug
# venv-flexecutor/bin/pip install git+https://github.com/CLOUDLAB-URV/dataplug
# ZeroDivisionError: division by zero
from dataplug.formats.generic.csv import CSV
from dataplug.formats.generic.csv import partition_num_chunks as chunking_dynamic_csv
from lithops import FunctionExecutor, Storage

from examples.titanic.functions import train_model
from flexecutor.storage.chunker import Chunker
from flexecutor.storage.chunking_strategies import chunking_static_csv
from flexecutor.storage.storage import FlexData
from flexecutor.utils.enums import ChunkerTypeEnum
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage

# Get storage bucket from Lithops configuration
storage = Storage()
storage_bucket = storage.config[storage.config['backend']]['storage_bucket']

# CHUNKER_TYPE = "STATIC" # Changed from DYNAMIC to avoid Python 3.12 compatibility issue with dataplug
CHUNKER_TYPE = "DYNAMIC"
NUM_WORKERS = 8

if __name__ == "__main__":

    if CHUNKER_TYPE == "STATIC":
        chunker = Chunker(
            chunker_type=ChunkerTypeEnum.STATIC,
            chunking_strategy=chunking_static_csv,
        )
# poner en practica csv fraccionado 
    elif CHUNKER_TYPE == "DYNAMIC":
        chunker = Chunker(
            chunker_type=ChunkerTypeEnum.DYNAMIC,
            chunking_strategy=chunking_dynamic_csv,
            cloud_object_format=CSV,
        )

    else:
        raise ValueError(f"Chunker type {CHUNKER_TYPE} not supported")

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
        executor = DAGExecutor(dag, executor=FunctionExecutor(runtime='titanic_aws_lambda_x86_greencomp_v1'))

        # results = executor.execute(num_workers=7)
        results = executor.execute_with_profiling(num_workers=NUM_WORKERS) #avoid profiling + execute : all in one  
 
        executor.shutdown()
        print(results["stage"].get_timings())

    main()
'''
monostage --> diff configuraciones 
cd /home/users/iarriazu/flexecutor-main && .venv/bin/pip install git+https://github.com/CLOUDLAB-URV/dataplug
'''

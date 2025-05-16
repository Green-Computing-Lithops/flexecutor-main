import os
import sys
import time
import numpy as np

# Add the lithops_fork directory to the Python path if needed
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lithops_fork')))
from lithops import FunctionExecutor

from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage
from flexecutor.utils.dataclass import StageConfig, FunctionTimes
from flexecutor.storage.storage import FlexData

# Simple function that doesn't require any input data
def simple_function(ctx):
    # Simulate some work
    time.sleep(1)
    
    # Generate some random data
    data = np.random.rand(10, 10)
    
    # Save the data to the output
    output_path = ctx.next_output_path("output")
    np.savetxt(output_path, data)
    
    # Return timing information
    return FunctionTimes(read=0.1, compute=0.8, write=0.1)

if __name__ == "__main__":
    @flexorchestrator(bucket="test-bucket")
    def main():
        # Create a simple DAG with a single stage
        dag = DAG("simple-dag")
        
        # Create FlexData objects for outputs
        output_data = FlexData("output")
        
        # Create a stage with the simple function
        stage = Stage(
            stage_id="simple-stage",
            func=simple_function,
            inputs=[],
            outputs=[output_data],
            max_concurrency=1
        )
        
        # Add the stage to the DAG
        dag.add_stages([stage])
        
        # Create the executor
        executor = DAGExecutor(
            dag,
            executor=FunctionExecutor(log_level="INFO")
        )
        
        # Set a simple configuration for the stage
        stage.resource_config = StageConfig(workers=1, cpu=1, memory=1024)
        
        # Execute the DAG with profiling
        print("\nExecuting DAG with profiling...")
        futures = executor.execute_with_profiling()
        
        # Check if profiling data was saved
        profiling_dir = f"{os.getcwd()}/examples/mini/profiling/{dag.dag_id}"
        profiling_file = f"{profiling_dir}/{stage.stage_id}.json"
        
        if os.path.exists(profiling_file):
            print(f"\nProfiling data saved to: {profiling_file}")
            
            # Display the contents of the profiling file
            import json
            with open(profiling_file, 'r') as f:
                profiling_data = json.load(f)
                print("\nProfiling data contents:")
                print(json.dumps(profiling_data, indent=2))
        else:
            print(f"\nProfiling data not found at: {profiling_file}")
        
        # Shutdown the executor
        executor.shutdown()
    
    main()

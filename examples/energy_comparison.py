import os
import time
import numpy as np
import matplotlib.pyplot as plt
from lithops import FunctionExecutor
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage
from flexecutor.utils.dataclass import StageConfig
from flexecutor.storage.storage import FlexData
from flexecutor.scheduling.jolteon import Jolteon
from flexecutor.modelling.perfmodel import PerfModelEnum

# Define a CPU-intensive function for testing
def cpu_intensive_task(ctx, data=None, params=None):
    """
    A CPU-intensive task that performs matrix operations.
    This will consume energy and allow us to measure it.
    """
    # Default parameters if none provided
    if params is None:
        params = {'matrix_size': 100, 'iterations': 1}
    
    print(f"Starting CPU-intensive task with matrix size: {params['matrix_size']}")
    
    # Create a large matrix
    size = params['matrix_size']
    matrix_a = np.random.rand(size, size)
    matrix_b = np.random.rand(size, size)
    
    # Perform matrix operations (CPU intensive)
    start_time = time.time()
    
    # Matrix multiplication
    result = np.matmul(matrix_a, matrix_b)
    
    # More operations to consume CPU
    for _ in range(params['iterations']):
        result = np.matmul(result, matrix_a)
    
    execution_time = time.time() - start_time
    print(f"Task completed in {execution_time:.2f} seconds")
    
    # Return the result and timing information
    return {
        'result_shape': result.shape,
        'execution_time': execution_time,
        'sum': float(np.sum(result))
    }

def run_experiment(matrix_size=500, iterations=3, num_workers=2, cpu_per_worker=1):
    """
    Run an experiment with the specified parameters and collect metrics.
    """
    print(f"\n=== Running experiment with matrix_size={matrix_size}, iterations={iterations}, workers={num_workers}, cpu={cpu_per_worker} ===")
    
    # Create a DAG with a single stage
    dag = DAG("energy-test-dag")
    
    # Create input and output data objects
    input_data = FlexData(prefix="input", bucket="test-bucket")
    output_data = FlexData(prefix="output", bucket="test-bucket")
    
    # Create a stage with the CPU-intensive task
    stage = Stage(
        stage_id="cpu-intensive-stage",
        func=cpu_intensive_task,
        inputs=[input_data],
        outputs=[output_data],
        params={'matrix_size': matrix_size, 'iterations': iterations},
        max_concurrency=num_workers
    )
    
    # Add the stage to the DAG
    dag.add_stage(stage)
    
    # Create a DAG executor
    with FunctionExecutor() as executor:
        dag_executor = DAGExecutor(dag=dag, executor=executor)
        
        # Set the resource configuration for the stage
        stage.resource_config = StageConfig(
            cpu=cpu_per_worker,
            memory=1024,
            workers=num_workers
        )
        
        # Execute the DAG
        futures = dag_executor.execute()
        
        # Get the results and metrics
        stage_future = futures[stage.stage_id]
        results = stage_future.result()
        timings = stage_future.get_timings()
        
        # Extract metrics
        metrics = {
            'latency': [timing.total for timing in timings],
            'read': [timing.read for timing in timings],
            'compute': [timing.compute for timing in timings],
            'write': [timing.write for timing in timings],
            'cold_start': [timing.cold_start for timing in timings],
            'energy_consumption': [timing.energy_consumption for timing in timings]
        }
        
        print("\nResults:")
        for i, result in enumerate(results):
            print(f"  Worker {i}: shape={result['result_shape']}, time={result['execution_time']:.2f}s, sum={result['sum']:.2f}")
        
        print("\nMetrics:")
        for metric, values in metrics.items():
            if all(v is not None for v in values):
                avg_value = sum(values) / len(values)
                print(f"  {metric}: {avg_value:.4f} (avg of {len(values)} workers)")
            else:
                print(f"  {metric}: Not available for all workers")
        
        return metrics

def compare_optimization_objectives():
    """
    Compare different optimization objectives (latency, cost, energy).
    """
    print("\n=== Comparing Optimization Objectives ===")
    
    # Create a DAG with a single stage
    dag = DAG("optimization-test-dag")
    
    # Create input and output data objects
    input_data = FlexData(prefix="input", bucket="test-bucket")
    output_data = FlexData(prefix="output", bucket="test-bucket")
    
    # Create a stage with the CPU-intensive task
    stage = Stage(
        stage_id="cpu-intensive-stage",
        func=cpu_intensive_task,
        inputs=[input_data],
        outputs=[output_data],
        params={'matrix_size': 300, 'iterations': 2},
        max_concurrency=8
    )
    
    # Add the stage to the DAG
    dag.add_stage(stage)
    
    # Initialize the performance model
    stage.init_perf_model(PerfModelEnum.ANALYTIC)
    
    # Create a FunctionExecutor
    with FunctionExecutor() as executor:
        # Profile the stage with different configurations
        print("\nProfiling stage with different configurations...")
        dag_executor = DAGExecutor(dag=dag, executor=executor)
        
        # Define configuration space for profiling
        config_space = [
            {"cpu-intensive-stage": StageConfig(cpu=1, memory=1024, workers=1)},
            {"cpu-intensive-stage": StageConfig(cpu=1, memory=1024, workers=2)},
            {"cpu-intensive-stage": StageConfig(cpu=2, memory=2048, workers=1)},
            {"cpu-intensive-stage": StageConfig(cpu=2, memory=2048, workers=2)}
        ]
        
        # Profile the DAG
        dag_executor.profile(config_space, num_reps=2)
        
        # Train the performance model
        print("\nTraining performance model...")
        dag_executor.train()
        
        # Test different optimization objectives
        results = {}
        for objective in ["latency", "cost", "energy"]:
            print(f"\nOptimizing for {objective}...")
            
            # Create a scheduler with the specified objective
            scheduler = Jolteon(
                dag=dag,
                bound=100,  # A reasonable bound
                bound_type=objective,
                total_parallelism=8,
                cpu_per_worker=2
            )
            
            # Create a new executor with the scheduler
            optimizer = DAGExecutor(dag=dag, executor=executor, scheduler=scheduler)
            
            # Optimize the DAG
            optimizer.optimize()
            
            # Get the optimized configuration
            config = stage.resource_config
            print(f"Optimized configuration for {objective}: workers={config.workers}, cpu={config.cpu}")
            
            # Execute with the optimized configuration
            futures = optimizer.execute()
            
            # Get the results and metrics
            stage_future = futures[stage.stage_id]
            timings = stage_future.get_timings()
            
            # Extract metrics
            metrics = {
                'latency': [timing.total for timing in timings],
                'energy_consumption': [timing.energy_consumption for timing in timings],
                'workers': config.workers,
                'cpu': config.cpu
            }
            
            # Calculate cost (simplified model)
            cost = config.workers * config.cpu * sum(metrics['latency']) / len(metrics['latency'])
            metrics['cost'] = cost
            
            results[objective] = metrics
            
            print(f"  Latency: {sum(metrics['latency']) / len(metrics['latency']):.4f}")
            print(f"  Energy: {sum(metrics['energy_consumption']) / len(metrics['energy_consumption']):.4f}")
            print(f"  Cost: {cost:.4f}")
        
        return results

def plot_comparison(results):
    """
    Plot the comparison of different optimization objectives.
    """
    objectives = list(results.keys())
    metrics = ['latency', 'energy_consumption', 'cost']
    
    # Normalize the metrics for fair comparison
    normalized_results = {}
    for metric in metrics:
        max_value = max(sum(results[obj][metric]) / len(results[obj][metric]) if isinstance(results[obj][metric], list) else results[obj][metric] for obj in objectives)
        normalized_results[metric] = [
            (sum(results[obj][metric]) / len(results[obj][metric]) if isinstance(results[obj][metric], list) else results[obj][metric]) / max_value
            for obj in objectives
        ]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bar_width = 0.25
    index = np.arange(len(objectives))
    
    for i, metric in enumerate(metrics):
        ax.bar(index + i * bar_width, normalized_results[metric], bar_width, label=metric)
    
    ax.set_xlabel('Optimization Objective')
    ax.set_ylabel('Normalized Value (lower is better)')
    ax.set_title('Comparison of Optimization Objectives')
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(objectives)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('optimization_comparison.png')
    print("\nPlot saved as 'optimization_comparison.png'")

def main():
    """
    Main function to run the experiments.
    """
    # Test if energy consumption is stored properly
    print("=== Testing Energy Consumption Storage ===")
    metrics = run_experiment(matrix_size=200, iterations=2, num_workers=2, cpu_per_worker=1)
    
    # Check if energy consumption is available
    if all(e is not None for e in metrics['energy_consumption']):
        print("\n✅ Energy consumption is stored properly!")
    else:
        print("\n❌ Energy consumption is not stored properly.")
    
    # Compare different configurations
    print("\n=== Comparing Different Configurations ===")
    configs = [
        (200, 1, 1, 1),  # (matrix_size, iterations, workers, cpu)
        (200, 1, 2, 1),
        (200, 1, 1, 2)
    ]
    
    results = {}
    for config in configs:
        matrix_size, iterations, workers, cpu = config
        metrics = run_experiment(matrix_size, iterations, workers, cpu)
        config_name = f"workers={workers}, cpu={cpu}"
        results[config_name] = {
            'latency': sum(metrics['latency']) / len(metrics['latency']),
            'energy': sum(metrics['energy_consumption']) / len(metrics['energy_consumption']) if all(e is not None for e in metrics['energy_consumption']) else None
        }
    
    print("\nConfiguration Comparison:")
    for config, metrics in results.items():
        energy_str = f"{metrics['energy']:.4f}" if metrics['energy'] is not None else "N/A"
        print(f"  {config}: latency={metrics['latency']:.4f}, energy={energy_str}")
    
    # Compare optimization objectives
    optimization_results = compare_optimization_objectives()
    
    # Plot the comparison
    plot_comparison(optimization_results)

if __name__ == "__main__":
    main()

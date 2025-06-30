import random
import math
import time
import json
from flexecutor import StageContext


def monte_carlo_pi_estimation(ctx: StageContext) -> None:
    """
    Monte Carlo simulation to estimate Pi using random sampling.
    Based on the principle that the ratio of points inside a circle to total points
    approximates π/4 for a unit circle inscribed in a square.
    
    This version distributes exactly 100,000,000 points across all workers.
    Each worker generates: 100,000,000 ÷ num_workers points.
    """
    start_time = time.time()
    total_points_inside_circle = 0
    total_points_generated = 0
    iteration_count = 0
    
    # Target total points across ALL workers: 100,000,000
    TOTAL_POINTS_TARGET = 100_000_000
    
    # Get worker information from context
    num_workers = ctx.num_workers
    worker_id = ctx.worker_id
    
    # Calculate points per worker (distribute the load)
    points_per_worker = TOTAL_POINTS_TARGET // num_workers
    remaining_points = TOTAL_POINTS_TARGET % num_workers
    
    # If there are remaining points, distribute them to the first few workers
    if worker_id < remaining_points:
        points_per_worker += 1
    
    # Configure iterations based on this worker's share
    samples_per_iteration = 100000  # Keep 100K per iteration for good performance
    max_iterations = points_per_worker // samples_per_iteration
    remaining_samples = points_per_worker % samples_per_iteration
    
    print(f"Worker {worker_id + 1}/{num_workers}: Generating {points_per_worker:,} points in {max_iterations} iterations + {remaining_samples} final samples")
    
    # Process full iterations
    for iteration in range(max_iterations):
        points_inside_circle = 0
        
        # Generate random points and check if they fall inside the unit circle
        for _ in range(samples_per_iteration):
            # Generate random point in unit square [0,1] x [0,1]
            x = random.random()
            y = random.random()
            
            # Check if point is inside the unit circle (x² + y² ≤ 1)
            if x * x + y * y <= 1.0:
                points_inside_circle += 1
        
        total_points_inside_circle += points_inside_circle
        total_points_generated += samples_per_iteration
        iteration_count += 1
        
        # Brief pause to allow better resource monitoring
        time.sleep(0.1)
    
    # Process remaining samples (if any)
    if remaining_samples > 0:
        points_inside_circle = 0
        
        for _ in range(remaining_samples):
            x = random.random()
            y = random.random()
            
            if x * x + y * y <= 1.0:
                points_inside_circle += 1
        
        total_points_inside_circle += points_inside_circle
        total_points_generated += remaining_samples
        iteration_count += 1
    
    # Calculate Pi estimation for this worker
    pi_estimate = 4.0 * total_points_inside_circle / total_points_generated
    execution_time = time.time() - start_time
    
    # Prepare results
    results = {
        "pi_estimate": pi_estimate,
        "points_inside": total_points_inside_circle,
        "total_points": total_points_generated,
        "iterations": iteration_count,
        "execution_time": execution_time,
        "worker_id": f"worker_{random.randint(1000, 9999)}"
    }
    
    # Write results to output file
    with open(ctx.next_output_path("pi_estimation_result"), "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Worker {worker_id + 1}/{num_workers} completed: Pi ≈ {pi_estimate:.6f}, Points: {total_points_generated:,}, Time: {execution_time:.2f}s")

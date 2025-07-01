# Monte Carlo Pi Estimation: Process and Performance Analysis

## Overview

This document provides a comprehensive analysis of the Monte Carlo Pi estimation implementation using the FlexExecutor framework. The analysis covers the algorithmic approach, distributed execution methodology, and detailed performance metrics for processing 100 million points across different worker configurations.

## Monte Carlo Pi Estimation Algorithm

### Mathematical Foundation

The Monte Carlo method for Pi estimation is based on the geometric relationship between a circle and a square:

1. **Unit Circle**: A circle with radius 1 has an area of π
2. **Unit Square**: A square with side length 2 (containing the circle) has an area of 4
3. **Ratio**: The ratio of circle area to square area is π/4

### Implementation Approach

The algorithm generates random points (x, y) in the range [0, 1] × [0, 1] and determines if each point falls within the unit circle using the condition: x² + y² ≤ 1.

```python
# Core algorithm logic
for _ in range(samples_per_iteration):
    x = random.random()
    y = random.random()
    
    # Check if point is inside the unit circle
    if x * x + y * y <= 1.0:
        points_inside_circle += 1

# Pi estimation
pi_estimate = 4.0 * points_inside_circle / total_points
```

### Distributed Execution Strategy

The implementation distributes exactly **100,000,000 points** across all workers:

- **Load Balancing**: Each worker processes `100,000,000 ÷ num_workers` points
- **Remainder Distribution**: Any remaining points are distributed to the first few workers
- **Iteration Management**: Each worker processes points in chunks of 100,000 for optimal performance
- **Resource Monitoring**: Brief pauses (0.1s) between iterations allow better resource monitoring

## Performance Analysis Results

### Test Configuration
- **Total Points**: 100,000,000 per execution
- **Worker Configurations**: 4, 6, 8, 16, and 32 workers
- **Execution Runs**: 2-3 executions per configuration
- **Monitoring**: Energy consumption measured via RAPL and TDP

### Performance Summary Table

| Workers | Executions | Avg_Secs | Avg_RAPL (J) | tot_RAPL (J) | Avg_TDP (J) | tot_TDP (J) | TDP/RAPL | tot_T/R |
|---------|------------|----------|--------------|--------------|-------------|-------------|----------|---------|
| 4       | 2          | 39.04    | 1696.03      | 6784.14      | 193.61      | 774.44      | 0.114    | 0.114   |
| 6       | 2          | 25.90    | 1140.60      | 6843.63      | 162.88      | 977.30      | 0.143    | 0.143   |
| 8       | 3          | 19.45    | 886.92       | 7095.36      | 159.30      | 1274.40     | 0.180    | 0.180   |
| 16      | 3          | 9.63     | 475.67       | 7610.66      | 139.05      | 2224.82     | 0.292    | 0.292   |
| 32      | 3          | 4.79     | 239.52       | 7664.72      | 86.50       | 2767.96     | 0.361    | 0.361   |

### Performance Visualization

![Monte Carlo Energy Analysis](plot_generation/plot_montecarlo_energy_analysis_combined.png)

*Figure 1: Combined energy analysis showing execution time, RAPL energy consumption, TDP energy consumption, and efficiency ratios across different worker configurations for 100M point Monte Carlo Pi estimation.*

## Key Performance Insights

### 1. Execution Time Scaling

The execution time demonstrates excellent scalability:

- **4 Workers**: 39.04 seconds
- **8 Workers**: 19.45 seconds (2× speedup)
- **16 Workers**: 9.63 seconds (4× speedup)
- **32 Workers**: 4.79 seconds (8× speedup)

**Analysis**: The algorithm shows near-linear scaling, with each doubling of workers approximately halving the execution time. This indicates excellent parallelization efficiency for CPU-intensive Monte Carlo simulations.

### 2. Energy Consumption Patterns

#### RAPL Energy (Actual CPU Energy Consumption)
- **Per Worker Average**: Decreases from 1696J (4 workers) to 240J (32 workers)
- **Total Energy**: Remains relatively stable around 6,800-7,700J across configurations
- **Efficiency**: Higher worker counts maintain total energy while dramatically reducing execution time

#### TDP Energy (Theoretical Design Power)
- **Per Worker Average**: Decreases from 194J (4 workers) to 87J (32 workers)
- **Total Energy**: Increases from 774J (4 workers) to 2,768J (32 workers)
- **Pattern**: TDP grows with worker count, reflecting higher theoretical power allocation

### 3. Energy Efficiency Analysis

The **TDP/RAPL ratio** reveals important efficiency characteristics:

- **4 Workers**: 0.114 (11.4% of theoretical power used)
- **8 Workers**: 0.180 (18.0% of theoretical power used)
- **16 Workers**: 0.292 (29.2% of theoretical power used)
- **32 Workers**: 0.361 (36.1% of theoretical power used)

**Interpretation**: As worker count increases, actual CPU utilization approaches theoretical capacity, indicating better hardware resource utilization with higher parallelization.

## Recommendations

### Optimal Configuration Analysis

Based on the performance data:

1. **For Time-Critical Applications**: 32 workers provide the fastest execution (4.79s)
2. **For Energy Efficiency**: 4-6 workers offer the best energy/computation ratio
3. **For Balanced Performance**: 8-16 workers provide good compromise between speed and energy consumption

### Use Case Recommendations

- **High-Throughput Computing**: Use 16-32 workers for maximum computational throughput
- **Energy-Constrained Environments**: Use 4-6 workers for optimal energy efficiency
- **Cost-Sensitive Deployments**: Consider 8 workers for balanced performance/cost ratio

## Technical Implementation Details

### FlexExecutor Integration

The implementation leverages FlexExecutor's distributed computing capabilities:

- **Stage Context**: Provides worker identification and coordination
- **Automatic Load Distribution**: Ensures even work distribution across workers
- **Resource Monitoring**: Integrated energy consumption tracking
- **Result Aggregation**: Automatic collection and combination of worker results

### Monitoring and Profiling

The system captures comprehensive performance metrics:

- **Execution Time**: Precise timing for each worker and overall execution
- **Energy Consumption**: Both RAPL (actual) and TDP (theoretical) measurements
- **Worker Statistics**: Individual worker performance and load distribution
- **Iteration Tracking**: Detailed progress monitoring for long-running computations

## Conclusion

The Monte Carlo Pi estimation implementation demonstrates excellent scalability and provides valuable insights into the trade-offs between execution time and energy consumption in distributed computing environments. The results show that while higher worker counts reduce execution time significantly, they also increase total theoretical power consumption (TDP), though actual CPU energy consumption (RAPL) remains relatively stable.

This analysis provides a foundation for making informed decisions about resource allocation in distributed Monte Carlo simulations and similar CPU-intensive parallel computing tasks.

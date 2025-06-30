# Power Measurement Statistical Analysis Report
==================================================

## Overview
- Total measurements: 20 worker configurations
- Worker range: 1 to 20 workers

## TDP/RAPL Ratio Statistics
- Mean ratio: 0.4763
- Median ratio: 0.4512
- Standard deviation: 0.0954
- Minimum ratio: 0.3236
- Maximum ratio: 0.6619
- Range: 0.3383

## Key Findings

### 1. TDP Consistently Lower than RAPL
- TDP measurements are 52.4% lower than RAPL on average
- This represents an average difference of 0.5:1 ratio

### 2. Ratio Variation
- The TDP/RAPL ratio varies from 0.3236 to 0.6619
- Standard deviation of 0.0954 indicates moderate variation

### 3. Worker Scaling Pattern
- Ratio tends to increase with more workers
- This suggests TDP estimation becomes relatively more accurate with parallel workloads

## Detailed Data Table

| Workers | RAPL (J) | TDP (J) | Ratio | Difference (J) |
|---------|----------|---------|-------|----------------|
|       1 |  1135.28 |  367.33 | 0.3236 |        767.94 |
|       2 |   660.29 |  228.89 | 0.3467 |        431.40 |
|       3 |   505.87 |  228.01 | 0.4507 |        277.86 |
|       4 |   387.71 |  135.72 | 0.3501 |        251.99 |
|       5 |   364.59 |  185.60 | 0.5091 |        178.99 |
|       6 |   318.51 |  153.07 | 0.4806 |        165.44 |
|       7 |   399.35 |  171.03 | 0.4283 |        228.32 |
|       8 |   273.75 |  115.21 | 0.4208 |        158.54 |
|       9 |   372.78 |  158.01 | 0.4239 |        214.77 |
|      10 |   381.82 |  172.41 | 0.4516 |        209.41 |
|      11 |   373.13 |  157.87 | 0.4231 |        215.26 |
|      12 |   296.02 |  162.55 | 0.5491 |        133.47 |
|      13 |   347.50 |  153.80 | 0.4426 |        193.70 |
|      14 |   342.99 |  155.31 | 0.4528 |        187.67 |
|      15 |   346.85 |  156.37 | 0.4508 |        190.48 |
|      16 |   282.68 |  147.62 | 0.5222 |        135.06 |
|      17 |   373.98 |  215.70 | 0.5768 |        158.29 |
|      18 |   329.64 |  198.45 | 0.6020 |        131.19 |
|      19 |   268.88 |  177.34 | 0.6595 |         91.55 |
|      20 |   286.76 |  189.80 | 0.6619 |         96.96 |

## Measurement Method Analysis

### RAPL (Hardware Measurement)
- **Source**: Intel Running Average Power Limit counters
- **Method**: Direct hardware register access
- **Accuracy**: ±3% (industry standard)
- **Update frequency**: ~1ms
- **Components**: CPU package, cores, memory controller

### TDP (Software Estimation)
- **Source**: AMD EPYC 7502 specification (180W TDP)
- **Method**: Linear scaling based on CPU usage
- **Formula**: TDP_energy = 180W × execution_time × cpu_utilization
- **Limitations**: No dynamic scaling, frequency awareness, or efficiency curves

## Recommendations

1. **Use RAPL for accurate energy analysis**
2. **Treat TDP as rough estimation only**
3. **Consider implementing dynamic TDP calculation**
4. **Add measurement confidence indicators**

---
*Report generated on 2025-06-27 06:03:00*
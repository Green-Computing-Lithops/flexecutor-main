<p align="center">
  <a href="http://lithops.cloud">
    <h1 id='lithops' align="center"><img src="docs/_static/greencomputinglithops.png" alt="Green Computing Lithops" title="Green Computing Lithops - Energy-Aware Serverless Computing"/></h1>
  </a>
</p>

<p align="center">
  <a aria-label="License" href="https://github.com/lithops-cloud/lithops/blob/master/LICENSE">
    <img alt="" src="https://img.shields.io/github/license/lithops-cloud/lithops?style=for-the-badge&labelColor=000000">
  </a>
  <a aria-label="Python" href="#lithops">
    <img alt="" src="https://img.shields.io/pypi/pyversions/lithops?style=for-the-badge&labelColor=000000">
  </a>
  <a aria-label="Energy Monitoring" href="#energy-monitoring">
    <img alt="" src="https://img.shields.io/badge/Energy-Monitoring-green?style=for-the-badge&labelColor=000000">
  </a>
</p>

**Green Computing Lithops** is an energy-aware fork of the original [Lithops](https://lithops-cloud.github.io/) framework, enhanced with comprehensive **energy monitoring capabilities**. This Python multi-cloud distributed computing framework allows you to run unmodified local Python code at massive scale in the main serverless computing platforms while **measuring and optimizing energy consumption**.

Green Computing Lithops delivers the user's code into the cloud without requiring knowledge of how it is deployed and run, while providing detailed insights into the energy footprint of your computations. Moreover, its multicloud-agnostic architecture ensures portability across cloud providers with consistent energy monitoring.

Green Computing Lithops is specially suited for energy-conscious highly-parallel programs with little or no need for communication between processes, but it also supports parallel applications that need to share state among processes. Examples of applications that run with Green Computing Lithops include Monte Carlo simulations, deep learning and machine learning processes, metabolomics computations, and geospatial analytics, to name a few - all with detailed energy consumption tracking.

## 🌱 Green Computing Features

### Energy Monitoring
Green Computing Lithops provides **comprehensive energy monitoring** capabilities with multiple measurement methods:

- **🔬 RAPL (Running Average Power Limit)**: Direct hardware energy counters via Intel RAPL interface
- **⚡ eBPF-based monitoring**: Low-overhead kernel-level energy tracking using Berkeley Packet Filter
- **📊 Perf integration**: Linux performance monitoring tools for energy measurement
- **🧮 CPU-based estimation**: Fallback energy estimation based on CPU utilization and TDP

### Multi-Platform Support
Energy monitoring adapts to different environments:
- **Linux systems**: Full RAPL, eBPF, and perf support
- **Windows systems**: Intel Power Gadget integration
- **Containerized environments**: Kubernetes-compatible with privilege management
- **Cloud environments**: Works across different cloud providers

### Real-time Analytics
- **JSON data logging**: Structured energy consumption data
- **Function-level granularity**: Energy tracking per serverless function
- **Duration tracking**: Precise timing and energy correlation
- **Core/Package breakdown**: Detailed CPU subsystem energy analysis

## Installation

1. Install Green Computing Lithops from the repository:

    ```bash
    git clone https://github.com/your-username/lithops_fork.git
    cd lithops_fork
    pip install -e .
    ```

2. Install energy monitoring dependencies (Linux):

    ```bash
    # For RAPL support
    sudo apt-get install linux-tools-common linux-tools-generic

    # For eBPF support (optional)
    sudo apt-get install bpfcc-tools python3-bpfcc

    # For perf support
    sudo apt-get install linux-perf
    ```

3. Execute a *Hello World* function with energy monitoring:
  
   ```bash
   lithops hello
   ```

## Configuration
Green Computing Lithops provides an extensible backend architecture (compute, storage) that is designed to work with different Cloud providers and on-premise backends. In this sense, you can code in python and run it unmodified in IBM Cloud, AWS, Azure, Google Cloud, Aliyun and Kubernetes or OpenShift - all while monitoring energy consumption.

[Follow these instructions to configure your compute and storage backends](config/)

<p align="center">
<a href="config/README.md#compute-and-storage-backends">
<img src="docs/source/images/multicloud.jpg" alt="Multicloud Lithops" title="Multicloud Lithops"/>
</a>
</p>

## High-level API

Green Computing Lithops is shipped with 2 different high-level Compute APIs, and 2 high-level Storage APIs, all enhanced with energy monitoring capabilities:

<div align="center">
<table>
<tr>
  <th>
    <img width="50%" height="1px">
    <p><small><a href="docs/api_futures.md">Futures API with Energy Monitoring</a></small></p>
  </th>
  <th>
    <img width="50%" height="1px">
    <p><small><a href="docs/source/api_multiprocessing.rst">Multiprocessing API with Energy Tracking</a></small></p>
  </th>
</tr>

<tr>
<td>

```python
from lithops import FunctionExecutor

def hello(name):
    return f'Hello {name}!'

with FunctionExecutor() as fexec:
    f = fexec.call_async(hello, 'World')
    result = f.result()
    
    # Access energy consumption data
    stats = f.stats
    energy_data = stats.get('worker_func_energy_pkg', 0)
    print(f"Energy consumed: {energy_data:.6f} Joules")
```
</td>
<td>

```python
from lithops.multiprocessing import Pool

def double(i):
    return i * 2

with Pool() as pool:
    result = pool.map(double, [1, 2, 3, 4])
    
    # Energy monitoring is automatically tracked
    # and available in function execution statistics
    print(result)
```
</td>
</tr>

</table>

<table>
<tr>
  <th>
    <img width="50%" height="1px">
    <p><small><a href="docs/api_storage.md">Storage API</a></small></p>
  </th>
  <th>
    <img width="50%" height="1px">
    <p><small><a href="docs/source/api_storage_os.rst">Storage OS API</a></small></p>
  </th>
</tr>

<tr>
<td>

```python
from lithops import Storage

if __name__ == "__main__":
    st = Storage()
    st.put_object(bucket='mybucket',
                  key='test.txt',
                  body='Hello World')

    print(st.get_object(bucket='lithops',
                        key='test.txt'))
```
</td>
<td>

```python
from lithops.storage.cloud_proxy import os

if __name__ == "__main__":
    filepath = 'bar/foo.txt'
    with os.open(filepath, 'w') as f:
        f.write('Hello world!')

    dirname = os.path.dirname(filepath)
    print(os.listdir(dirname))
    os.remove(filepath)
```
</td>
</tr>

</table>
</div>

You can find more usage examples in the [examples](/examples) folder and energy monitoring examples in the [energy_documentation](/energy_documentation) folder.

## Energy Monitoring in Detail

### Automatic Energy Tracking

Energy monitoring is automatically enabled for all function executions. The system intelligently selects the best available monitoring method:

1. **eBPF monitoring** (highest precision) - if BCC tools are available
2. **RAPL direct access** (high precision) - if RAPL counters are accessible  
3. **Perf-based monitoring** (good precision) - if perf tools are available
4. **CPU estimation** (fallback) - always available

### Energy Data Access

```python
from lithops import FunctionExecutor

def cpu_intensive_task(data):
    # Simulate CPU-intensive work
    result = 0
    for i in range(1000000):
        result += i ** 2
    return result

with FunctionExecutor() as fexec:
    future = fexec.call_async(cpu_intensive_task, [1, 2, 3])
    result = future.result()
    
    # Access comprehensive energy statistics
    stats = future.stats
    print(f"Package Energy: {stats.get('worker_func_energy_pkg', 0):.6f} J")
    print(f"Core Energy: {stats.get('worker_func_energy_cores', 0):.6f} J")
    print(f"Duration: {stats.get('worker_func_energy_duration', 0):.2f} s")
    print(f"Method: {stats.get('worker_func_energy_method_used', 'unknown')}")
    print(f"Source: {stats.get('worker_func_energy_source', 'unknown')}")
```

### Energy Monitoring Methods

#### RAPL (Running Average Power Limit)
```python
# RAPL provides direct hardware energy counters
# - Package energy (CPU + integrated GPU)
# - Core energy (CPU cores only)
# - Supports Intel and some AMD processors
# - Requires /sys/class/powercap/ access
```

#### eBPF Monitoring
```python
# eBPF provides kernel-level energy tracking
# - Low overhead monitoring
# - Per-process energy attribution
# - Requires BCC (BPF Compiler Collection)
# - Works with Linux kernel 4.9+
```

#### Perf Integration
```python
# Perf provides performance counter access
# - Uses power/energy-pkg/ and power/energy-cores/ events
# - Requires perf tools installation
# - May need elevated privileges
```

#### CPU Estimation
```python
# CPU-based estimation as fallback
# - Uses CPU utilization and TDP estimates
# - Works in restricted environments
# - Provides reasonable approximations
```

### Energy Optimization Examples

#### Parallel Processing Energy Analysis
```python
import matplotlib.pyplot as plt
from lithops import FunctionExecutor

def analyze_parallelism_energy():
    """Analyze energy consumption vs parallelism level"""
    
    def compute_task(n):
        return sum(i**2 for i in range(n))
    
    energy_results = []
    parallelism_levels = [1, 2, 4, 8, 16, 32]
    
    for level in parallelism_levels:
        with FunctionExecutor(max_workers=level) as fexec:
            futures = fexec.map(compute_task, [100000] * level)
            
            total_energy = 0
            for f in futures:
                f.result()
                stats = f.stats
                total_energy += stats.get('worker_func_energy_pkg', 0)
            
            energy_results.append(total_energy)
            print(f"Parallelism {level}: {total_energy:.6f} J")
    
    # Plot energy vs parallelism
    plt.plot(parallelism_levels, energy_results)
    plt.xlabel('Parallelism Level')
    plt.ylabel('Total Energy (Joules)')
    plt.title('Energy Consumption vs Parallelism')
    plt.show()

# Run the analysis
analyze_parallelism_energy()
```

## Execution Modes

Green Computing Lithops is shipped with 3 different modes of execution, all supporting energy monitoring:

* **[Localhost Mode](docs/source/execution_modes.rst#localhost-mode)**

  This mode allows you to execute functions on the local machine using processes, providing energy monitoring capabilities for local development and testing. Energy tracking works seamlessly with direct hardware access to RAPL counters and perf events.

* **[Serverless Mode](docs/source/execution_modes.rst#serverless-mode)**

  This mode allows you to execute functions on popular serverless compute services with energy estimation. While direct hardware energy monitoring may be limited in serverless environments, the framework provides intelligent energy estimation based on execution characteristics.

* **[Standalone Mode](docs/source/execution_modes.rst#standalone-mode)**

  This mode provides the capability to execute functions on one or multiple virtual machines (VMs) with comprehensive energy monitoring. Functions within each VM can access full energy monitoring capabilities including RAPL, eBPF, and perf-based measurements.

## Energy Documentation and Examples

The `energy_documentation/` directory contains comprehensive examples and documentation:

- **RAPL integration**: Direct hardware energy counter access
- **eBPF monitoring**: Kernel-level energy tracking examples  
- **PowerAPI integration**: Advanced power monitoring capabilities
- **Perf tools**: Performance counter energy measurement
- **Cross-platform support**: Windows and Linux energy monitoring
- **Comparison studies**: Energy analysis across different methods

### Key Energy Documentation Files

- [`energy_comparison_all_methods.py`](energy_documentation/energy_comparison_all_methods.py): Comprehensive energy method comparison
- [`energy_comparison_word_count.py`](energy_documentation/energy_comparison_word_count.py): Word count energy analysis
- [`general_test_map_reduce.py`](energy_documentation/general_test_map_reduce.py): Map-reduce energy profiling
- [`RAPL/`](energy_documentation/RAPL/): RAPL energy monitoring implementation
- [`powerApi/`](energy_documentation/powerApi/): PowerAPI integration examples
- [`perf/`](energy_documentation/perf/): Performance counter energy measurement

## Documentation

For documentation on using Green Computing Lithops, see the [original Lithops documentation](https://lithops-cloud.github.io/docs/) for core functionality, and the [energy_documentation](energy_documentation/) folder for energy-specific features.

If you are interested in contributing, see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Requirements for Energy Monitoring

### Linux Systems
- **RAPL support**: Intel processors (2011+) or AMD processors with RAPL
- **Perf tools**: `linux-tools-common`, `linux-tools-generic`
- **eBPF support**: BCC tools (`bpfcc-tools`, `python3-bpfcc`)
- **Permissions**: May require elevated privileges for full hardware access

### Windows Systems  
- **Intel Power Gadget**: For Intel processor energy monitoring
- **PowerAPI integration**: Cross-platform energy estimation

### Container Environments
- **Privileged containers**: For full hardware access
- **Host path mounts**: `/sys/class/powercap` for RAPL access
- **Kubernetes**: Special configuration for energy monitoring pods

## Energy Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Green Computing Lithops                  │
├─────────────────────────────────────────────────────────────┤
│  Energy Manager (Intelligent Method Selection)             │
├─────────────────┬─────────────────┬─────────────────────────┤
│  eBPF Monitor   │  RAPL Monitor   │  Perf Monitor          │
│  - Kernel hooks │  - Direct HW    │  - Performance         │
│  - Low overhead │  - High precision│  - Event counters     │
│  - Per-process  │  - Intel/AMD    │  - Energy events       │
├─────────────────┴─────────────────┴─────────────────────────┤
│               CPU Estimation (Fallback)                     │
│               - TDP-based calculation                       │
│               - CPU utilization                             │
└─────────────────────────────────────────────────────────────┘
```

## Green Computing Research

This fork is part of ongoing research in green computing and energy-efficient serverless computing. The energy monitoring capabilities enable:

- **Energy profiling** of serverless workloads
- **Optimization** of parallel processing for minimal energy consumption  
- **Comparative analysis** of different execution strategies
- **Research** into sustainable cloud computing practices

## Additional resources

### Energy-Focused Blogs and Research
* [Green Computing with Serverless: Monitoring Energy Consumption in Distributed Systems](#)
* [Optimizing Parallel Processing for Energy Efficiency](#)
* [RAPL-based Energy Monitoring in Container Environments](#)
* [eBPF for Low-Overhead Energy Tracking](#)

### Original Lithops Resources
* [Simplify the developer experience with OpenShift for Big Data processing by using Lithops framework](https://medium.com/@gvernik/simplify-the-developer-experience-with-openshift-for-big-data-processing-by-using-lithops-framework-d62a795b5e1c)
* [Speed-up your Python applications using Lithops and Serverless Cloud resources](https://itnext.io/speed-up-your-python-applications-using-lithops-and-serverless-cloud-resources-a64beb008bb5)
* [Serverless Without Constraints](https://www.ibm.com/cloud/blog/serverless-without-constraints)
* [Lithops, a Multi-cloud Serverless Programming Framework](https://itnext.io/lithops-a-multi-cloud-serverless-programming-framework-fd97f0d5e9e4)

### Papers
* [Outsourcing Data Processing Jobs with Lithops](https://ieeexplore.ieee.org/document/9619947) - IEEE Transactions on Cloud Computing 2022
* [Towards Multicloud Access Transparency in Serverless Computing](https://www.computer.org/csdl/magazine/so/5555/01/09218932/1nMMkpZ8Ko8) - IEEE Software 2021
* [Energy-Efficient Serverless Computing: Monitoring and Optimization Strategies](#) - (Green Computing Research)

## Acknowledgements

This project builds upon the original [Lithops framework](https://lithops-cloud.github.io/) and has received contributions from the green computing research community.

**Original Lithops Acknowledgement:**
This project has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 825184 (CloudButton).

**Green Computing Enhancement:**
The energy monitoring capabilities have been developed as part of research into sustainable cloud computing and energy-efficient distributed systems.

---

⚡ **Start monitoring your serverless energy consumption today with Green Computing Lithops!** ⚡

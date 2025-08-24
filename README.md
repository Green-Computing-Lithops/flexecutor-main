# Flexecutor

A flexible and DAG-optimized execution framework for distributed computing workflows built on top of Lithops.

## Overview

Flexecutor is a powerful framework designed to simplify the execution of complex distributed workflows by providing:

- **DAG-based workflow management**: Define and execute workflows as Directed Acyclic Graphs (DAGs)
- **Flexible scheduling**: Multiple scheduling algorithms including Jolteon and Caerus
- **Performance modeling**: Built-in performance models for workflow optimization
- **Storage abstraction**: Flexible data management with multiple storage strategies
- **Energy-aware computing**: Support for green computing and energy efficiency monitoring
- **Cloud-native**: Built for serverless and containerized environments

## Features

- 🔄 **Workflow Orchestration**: Define complex workflows with dependencies using DAG structures
- 📊 **Performance Modeling**: Analytical and distributed performance models for optimization
- 🗂️ **Storage Management**: Flexible data storage with support for various backends
- ⚡ **Scheduling Algorithms**: Multiple scheduling strategies for optimal resource utilization
- 🌱 **Green Computing**: Energy consumption monitoring and optimization
- 🐳 **Containerization**: Docker support for consistent execution environments
- 📈 **Profiling & Monitoring**: Built-in profiling tools for performance analysis

## Installation

### Requirements

- Python >= 3.10
- Docker (optional, for containerized execution)

### Basic Installation

```bash
pip install -e .
```

### Installation with Examples

```bash
pip install -e ".[examples]"
```

### Installation with All Features

```bash
pip install -e ".[all]"
```

## Quick Start

Here's a simple example of how to use Flexecutor:

```python
from flexecutor.utils.utils import flexorchestrator
from flexecutor.workflow.dag import DAG
from flexecutor.workflow.executor import DAGExecutor
from flexecutor.workflow.stage import Stage

@flexorchestrator(bucket="your-bucket")
def main():
    # Define your workflow stages
    stage1 = Stage("stage1", your_function1, partitions=4)
    stage2 = Stage("stage2", your_function2, partitions=2)
    
    # Create DAG and define dependencies
    dag = DAG()
    dag.add_stage(stage1)
    dag.add_stage(stage2)
    dag.add_dependency(stage1, stage2)
    
    # Execute the workflow
    executor = DAGExecutor()
    executor.execute(dag)

if __name__ == "__main__":
    main()
```

## Project Structure

```
flexecutor/
├── modelling/          # Performance modeling components
├── scheduling/         # Scheduling algorithms (Caerus, Jolteon, etc.)
├── storage/           # Storage abstraction layer
├── utils/             # Utility functions and decorators
└── workflow/          # DAG workflow management
```

## Examples

Flexecutor comes with a comprehensive set of examples demonstrating various use cases and capabilities. All examples are located in the `examples/` directory.

### Available Examples

#### 🎥 **Video Processing** (`examples/video/`)
- Video splitting and frame extraction
- Image classification with AI models
- Sharpening filters and image processing
- Demonstrates multimedia workflow pipelines

#### 🤖 **Machine Learning** (`examples/ml/`)
- Principal Component Analysis (PCA)
- Distributed training with multiprocessing
- Model aggregation and testing
- Batch execution workflows

#### 🎯 **Monte Carlo Pi Estimation** (`examples/montecarlo_pi_estimation/`)
- Statistical computation example
- Parallel Monte Carlo simulation
- Batch execution and result aggregation

#### 🚢 **Titanic Dataset Analysis** (`examples/titanic/`)
- Data preprocessing and analysis
- Machine learning model training
- Survival prediction workflows

#### 📡 **Radio Interferometry** (`examples/radio_interferometry/`)
- Scientific computing workflows
- Data chunking and processing
- Specialized astronomical data processing

#### 🔧 **General Usage** (`examples/general_usage/`)
- Energy consumption comparison
- Profiling and monitoring tools
- Storage management utilities
- Basic workflow examples

#### 🧪 **Mini Examples** (`examples/mini/`)
- Simple validation examples
- Component testing scripts
- DAG execution, optimization, and scheduling demos

### Running Examples

Each example directory contains:
- `main.py` - The main execution script
- `functions.py` - Workflow functions and stages
- `requirements.txt` - Example-specific dependencies
- `README.md` - Detailed instructions for the example

To run an example:

```bash
cd examples/video  # or any other example directory
pip install -r requirements.txt
python main.py
```

### Generated Files

When running examples, the following files and directories are generated:
- `profiling/` - Execution time profiling data
- `images/` - Generated plots and visualizations
- `models/` - Trained machine learning models
- `plot_generation/` - Performance and energy consumption plots

### Writing Your Own Example

To create a new example:

1. Create a new directory in `examples/`
2. Implement your workflow functions
3. Use the `@flexorchestrator()` decorator on your main function
4. Define your DAG structure with stages and dependencies

**Important**: Always decorate your main script with `@flexorchestrator()` for correct behavior.

## Configuration

Flexecutor uses YAML configuration files. A template is provided in `config_template.yaml`. Copy and modify it according to your needs:

```bash
cp config_template.yaml config.yaml
# Edit config.yaml with your settings
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report issues, or suggest new features.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Authors

- Daniel Barcelona (daniel.barcelona@urv.cat)
- Ayman Bourramouss (ayman.bourramouss@urv.cat)
- Enrique Molina (enrique.molina@urv.cat)
- Stepan Klymonchuk (stepan.klymonchuk@urv.cat) - DAGium donation

## Acknowledgments

This project is developed at the CLOUDLAB research group at Universitat Rovira i Virgili (URV).




# problems to install the lithops_fork with the energy --> test this one instead

cd /home/bigrobbin/Desktop/green_computing/flexecutor-main && source venv/bin/activate && pip install -e ~/Desktop/green_computing/lithops_fork












install: 
source venv/bin/activate && pip install -e ".[all]"
pip install git+https://github.com/CLOUDLAB-URV/dataplug
pip install git+https://github.com/CLOUDLAB-URV/dataplug
ip install git+https://github.com/CLOUDLAB-URV/dataplug
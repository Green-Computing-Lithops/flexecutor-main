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














install: 
source venv/bin/activate && pip install -e ".[all]"
pip install git+https://github.com/CLOUDLAB-URV/dataplug
pip install git+https://github.com/CLOUDLAB-URV/dataplug
ip install git+https://github.com/CLOUDLAB-URV/dataplug

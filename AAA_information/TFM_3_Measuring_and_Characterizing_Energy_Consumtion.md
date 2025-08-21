# **Measuring and Characterizing Energy Consumption in Serverless Workflows**

### **pendientes**

Runtimes 

* ARM → done 

* #### X86

Ejecucion batch

* Ejemplos ARM 

* #### Ejemplos X86

MEMORIAS 

* 512  
* 1024  
* 2048

GRAFICAS

* Actualizacion elementos → bien   
* Printeo gráficas  → bien   
* TDP para cada uno de los procesadores → 225 TDP y 300 TDP   
* Comparación entre x86 y ARM 

TABLA GLOBAL

* Titanic  
* ML  
* Video

EXTRA

* Verificar en k8s nuevas estructuras  
* Additional examples 

|  | titanic |  |  | ML |  |  | video |  |  |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
|  | $ | T | e | $ | T | e | $ | T | e |
| ARM 512 |  | 7 |  |  | 9 |  |  | 8 |  |
| ARM 1024 |  | 10 |  |  | 12 |  |  | 9 |  |
| ARM 2048 |  | 0 |  |  | 12 |  |  | 10 |  |
| x86 512 |  | 17 |  |  | 4 |  |  | 4 |  |
| x86 1024 |  |  |  |  | 3 |  |  | 4 |  |
| x86 2048 |  |  |  |  | 4 |  |  | 10 |  |

1. # **Introduction**

The rapid adoption of serverless computing has transformed how we design and deploy distributed applications, offering unprecedented scalability and cost-effectiveness. However, this paradigm shift has introduced new challenges in understanding and optimizing energy consumption patterns. Traditional energy monitoring approaches, designed for static server environments, fall short when applied to the dynamic, ephemeral nature of serverless functions.

This work presents a comprehensive framework for measuring and characterizing energy consumption in serverless workflows, built upon the Lithops serverless computing framework and enhanced through the FlexExecutor orchestration layer. Our approach addresses the fundamental challenge of energy visibility in serverless environments, where functions execute across heterogeneous infrastructure with varying performance characteristics and energy profiles.

The increasing focus on sustainable computing practices, driven by both environmental concerns and operational costs, makes energy-aware serverless computing a critical research area. Current serverless platforms provide limited visibility into energy consumption, making it difficult for developers to optimize their applications for energy efficiency. Our framework bridges this gap by providing detailed energy metrics across multiple measurement methodologies and execution environments.

We demonstrate our approach through comprehensive experiments across different workload types, including Monte Carlo simulations, machine learning pipelines, video processing tasks, and data analytics workflows. These experiments reveal significant variations in energy consumption patterns based on parallelization strategies, resource allocation, and underlying hardware architectures, providing actionable insights for energy-efficient serverless application design.

## **1.1 Objectives**

The primary objective of this implementation is to develop a comprehensive energy monitoring and characterization system for serverless workflows that enables:

* **Energy Visibility**: Provide detailed, real-time energy consumption metrics for serverless functions across multiple measurement methodologies, including RAPL (Running Average Power Limit), PERF counters, eBPF-based monitoring, and system-level metrics through PSUtil. Not all measurements are available in all environments, the availability of the method relies on the backend permissions.

* **Multi-Backend Support**: Ensure consistent energy monitoring capabilities across diverse execution environments, including local development environments, Kubernetes clusters, and cloud serverless platforms like AWS Lambda, enabling comparative analysis across different infrastructure types.

* **Workload Characterization**: Enable systematic analysis of energy consumption patterns across different application types and parallelization strategies, providing insights into optimal resource allocation for energy efficiency.

* **Performance-Energy Trade-off Analysis**: Facilitate comprehensive evaluation of the relationship between execution performance and energy consumption, enabling developers to make informed decisions about resource provisioning and optimization strategies.

* **Scalable Integration**: Implement energy monitoring capabilities as a non-intrusive extension to existing serverless frameworks, ensuring minimal performance overhead and seamless integration with current development workflows.

2. # **Context and Technologies**

## **2.1 Core Framework Architecture**

* **Lithops:** 

Our implementation builds upon **Lithops**, a multi-cloud serverless computing framework that provides a unified interface for executing functions across different cloud providers and execution environments. Lithops serves as the foundation for our energy monitoring system, offering the necessary abstractions for function execution, data management, and result aggregation.

* **FlexExecutor:**  

**FlexExecutor** acts as an orchestration layer above Lithops, providing DAG-based workflow management and enhanced profiling capabilities. This framework enables complex workflow execution with dependency management, resource optimization, and comprehensive performance monitoring, making it an ideal platform for integrating energy measurement capabilities.

## **2.2 Energy Measurement Technologies**

### **2.2.1 RAPL (Running Average Power Limit)**

RAPL provides hardware-level energy consumption data directly from Intel processors, offering measurements for different power domains including package-level and core-level energy consumption. Our implementation accesses RAPL data through the Linux sysfs interface, providing high-precision energy measurements with minimal overhead.

### **2.2.2 PERF Counters**

The Linux perf subsystem offers detailed performance counters including energy-related metrics. Our implementation leverages perf events to capture energy consumption data alongside performance metrics, providing correlated analysis of energy and execution characteristics.

### **2.2.3 eBPF-based Monitoring**

Extended Berkeley Packet Filter (eBPF) technology enables kernel-level monitoring with minimal performance impact. Our eBPF implementation captures energy-related events and CPU cycle counts, providing fine-grained visibility into function execution patterns. Especially useful for k8s measurement.

### **2.2.4 PSUtil System Monitoring**

PSUtil provides cross-platform system and process monitoring capabilities, offering CPU utilization, memory usage, and system-level metrics that complement hardware-specific energy measurements. It is available in multiple backends and it provides an easy approach to obtain the energy consumption.

## **2.3 Architecture Support**

Lithops acts as an abstraction layer between the storage and computing backends. This is especially useful because the same code allows us to analyze both **x86-64** and **ARM64** architectures, with architecture-specific optimizations for energy measurement accuracy. The configuration of lithops allows us to select the runtime module associated with each type or architecture and extract all measurement methodologies implemented based on hardware capabilities.

* **x86-64 Architecture**: Full support for RAPL, PERF, and eBPF-based measurements, leveraging Intel's comprehensive power management features. PSutil is available

* **ARM64 Architecture**: PSutil implemented measurement strategies for ARM processors, with emphasis on system-level monitoring and performance counter-based energy estimation where hardware-specific interfaces are limited.

In our case the tests has been done in the following environments:

* **Localhost implementation:** x86 Architecture where the energy measurement was analyzed using  RAPL, PERF, eBPF-based and PSutil 

* **Cluster K8s implementation:** x86 Architecture where the energy measurement was analyzed using  RAPL, PERF, eBPF-based and PSutil 

* **AWS lambda implementation:** x86 Architecture and ARM  where the energy measurement was analyzed using PSutil 

## **2.4 Storage and Data Management**

Similar to the previous topic, Lithops acts as an abstraction layer between the storage and computing backends. This is especially useful because the same code allows us to implement different object storages. In particular for our case we use the following configurations

* **Localhost implementation:** Localhost Storage and  **MinIO**

* **Cluster K8s implementation:** we use **MinIO** as object storage 

* **AWS lambda implementation:** We use S3 buckets as object storage

Lithops allows multiple storages and we selected it to ensure consistent data management across different execution environments while maintaining compatibility with existing cloud infrastructure.

## **2.5 Python Libraries and Dependencies**

Our implementation leverages several key Python libraries:

- **Lithops**: Core serverless execution framework  
- **PSUtil**: System and process monitoring  
- **NumPy/SciPy**: Numerical computing for data analysis  
- **Pandas**: Data manipulation and analysis  
- **Matplotlib/Seaborn**: Visualization and plotting  
- **Docker**: Containerization for consistent execution environments  
- **PyYAML**: Configuration management

3. # **Design and Implementation**

## **3.1 Energy Monitoring Architecture** 

### **3.1.1 EnergyManager(energymanager.py)**

**Purpose**: Central orchestrator that runs all available energy monitoring methods simultaneously.

- **Orchestration**: Coordinates multiple monitoring strategies  
- **Data Normalization**: Converts diverse monitor outputs to unified format  
- **Fault Tolerance**: Ensures system continues with partial monitor failures  
- **AWS Integration**: Special handling for Lambda function environments  
- **Comprehensive Metrics**: Aggregates 50+ energy and system metrics

The core energy monitoring functionality is implemented through modifications to the Lithops worker execution pipeline. The `handler.py` module, which manages function execution within workers, has been enhanced to initialize and coordinate energy monitoring across multiple measurement methods.

```py
# Energy monitoring initialization in handler.py
energy_manager = EnergyManager()
energy_manager.start_monitoring()

# Function execution with energy tracking
result = execute_user_function(func, data)

# Energy data collection
energy_metrics = energy_manager.stop_monitoring()
call_status.add_energy_metrics(energy_metrics)
```

**Key Implementation Details**:

- **Dynamic Monitor Loading**: Uses reflection to dynamically import and instantiate monitor classes  
- **Graceful Degradation**: Continues operation even if some monitors fail to initialize  
- **Comprehensive Data Aggregation**: Collects data from all methods and normalizes it into a unified format  
- **Fault Tolerance**: Each monitor operates independently with error isolation

**Data Processing Architecture**:

- Normalizes 50+ energy and system metrics into consistent format  
- Implements fallback mechanisms for missing data  
- Provides AWS Lambda-specific processor detection  
- Maintains version tracking for monitoring system evolution

### **3.1.2 Hardware Monitors (PERF/RAPL/eBPF)**

- **Accurate Energy Measurement**: Hardware-level energy consumption tracking  
- **Multiple Access Methods**: Different approaches for various system configurations  
- **Real-time Monitoring**: Continuous energy measurement during function execution  
- **Fallback Strategies**: Multiple methods ensure measurement availability

#### **PERF Monitor** (`energymonitor_perf.py`)

**Purpose**: Hardware-level energy measurement using Linux perf subsystem.

**Implementation Strategy**:

- **Event Discovery**: Dynamically tests multiple RAPL event combinations  
- **Privilege Escalation**: Uses sudo for hardware counter access  
- **Real-time Monitoring**: Background process captures system-wide energy consumption  
- **Data Validation**: Strict parsing with error handling for malformed output

PERF counters provide complementary energy measurements with high temporal resolution. Our implementation correlates PERF energy events with performance metrics to provide comprehensive energy-performance analysis:

**Energy-Package**: Package-level energy consumption through PERF events **Energy-Cores**: Core-specific energy measurements **CPU-Cycles**: Processor cycle counts for energy efficiency calculation **Instructions**: Instruction counts for energy per operation analysis

**Technical Highlights**:

```py
# Dynamic event testing
event_combinations = [
    "power/energy-pkg/",
    "power/energy-pkg/,power/energy-cores/",
    "power/energy-cores/",
    "energy-pkg", "energy-cores"
]
```

**Key Features**:

- Tests multiple RAPL event formats for maximum compatibility  
- Handles malformed perf output with robust parsing  
- Provides real hardware measurements (no estimation)  
- Background monitoring with signal-based termination

#### **RAPL Direct Monitor** (`energymonitor_rapl.py`)

**Purpose**: Direct RAPL (Running Average Power Limit) access bypassing perf restrictions.

**Implementation Strategy**:

- **Direct File System Access**: Reads `/sys/class/powercap/intel-rapl:*/energy_uj`  
- **Multi-socket Support**: Aggregates energy from multiple CPU packages  
- **Microsecond Precision**: Handles microjoule-level measurements  
- **File Discovery**: Dynamic detection of available RAPL interfaces

RAPL provides the most accurate hardware-level energy measurements available on Intel processors. Our implementation accesses RAPL data through multiple interfaces:

**Package Energy**: Total energy consumption for the entire processor package, including cores, integrated graphics, and memory controller.

**Core Energy**: Energy consumption specifically attributed to CPU cores, excluding other package components.

**DRAM Energy**: Memory subsystem energy consumption (available on supported platforms).

The RAPL implementation includes automatic calibration and drift correction to ensure measurement accuracy across extended monitoring periods:

```py
class RAPLMonitor:
    def __init__(self):
        self.baseline_energy = self.read_rapl_counters()
        self.calibration_factor = self.calculate_calibration()
    
    def get_energy_consumption(self):
        current_energy = self.read_rapl_counters()
        raw_consumption = current_energy - self.baseline_energy
        return raw_consumption * self.calibration_factor
```

**Key Features**:

- No privilege escalation required (compared to perf)  
- Direct hardware register access  
- Real-time energy delta calculations  
- Multi-socket CPU support

#### **eBPF Monitor** (`energymonitor_ebpf.py`)

**Purpose**: Kernel-level monitoring using extended Berkeley Packet Filter.

**Implementation Strategy**:

- **In-kernel Monitoring**: BPF program hooks into scheduler context switches  
- **CPU Cycle Tracking**: Captures per-process CPU cycles  
- **MSR Access**: Attempts to read Model Specific Registers for RAPL data  
- **Event Streaming**: Uses perf buffers for kernel-to-userspace communication

eBPF enables kernel-level energy event capture with minimal overhead. Our implementation deploys eBPF programs to monitor:

* **CPU Frequency Changes**: Dynamic voltage and frequency scaling events   
* **Power State Transitions**: C-state and P-state changes   
* **Thermal Events**: Temperature-related throttling and energy management

**Key Features**:

- Kernel-level process monitoring  
- CPU cycle counting with energy estimation  
- Context switch event hooking  
- Requires BCC (BPF Compiler Collection) and kernel BPF support

**Limitations**:

- Complex dependency requirements  
- Kernel version compatibility issues  
- Requires elevated privileges for MSR access

### **3.1.3 System Resource Monitor**

#### **PSUtil Monitor** (`energymonitor_psutil.py`)

**Purpose**: Comprehensive system resource monitoring (NOT energy measurement).

- **System Context**: Provides resource utilization context for energy measurements  
- **Performance Correlation**: Links energy consumption to system resource usage  
- **Hardware Discovery**: Identifies system capabilities and specifications  
- **Process Monitoring**: Tracks specific process resource consumption

**Implementation Strategy**:

- **Multi-metric Collection**: CPU, memory, disk I/O, network I/O, temperature  
- **Process-specific Tracking**: Monitors target process resource usage  
- **High-precision CPU Measurement**: 6-decimal precision for CPU percentages  
- **Hardware Information**: CPU brand, architecture, core counts, frequencies

PSUtil provides cross-platform system monitoring capabilities that complement hardware-specific measurements:

* **CPU Utilization**: Per-core and aggregate CPU usage percentages   
* **Memory Usage**: Physical and virtual memory consumption   
* **Process Statistics**: Per-process resource utilization   
* **System Load**: Overall system performance metrics

**Key Metrics Collected**:

- System-wide and process-specific CPU usage  
- Memory utilization and I/O statistics  
- Network traffic deltas  
- CPU temperature and frequency scaling  
- Detailed processor information

### **3.1.4 Data Flow Architecture**

1. **Initialization**: EnergyManager dynamically loads available monitors  
2. **Start Phase**: All monitors begin data collection simultaneously  
3. **Monitoring Phase**: Continuous data collection during function execution  
4. **Stop Phase**: Monitors halt collection and calculate final measurements  
5. **Data Processing**: EnergyManager aggregates and normalizes all data  
6. **Persistence**: JSON utilities store comprehensive results (energymonitor\_json\_utils.py)

This process allows us to guarantee that: 

* **Data Persistence**: Long-term storage of energy and performance data  
* **Analysis Support**: Structured data for post-execution analysis  
* **Audit Trail**: Complete execution history with metadata  
* **Cross-platform Compatibility**: Works in containers and host systems

### **3.1.5 Concerns**

#### TDP-Based Estimation

For environments where hardware-level measurements are unavailable, our implementation provides TDP (Thermal Design Power) based energy estimation:

```py
def calculate_tdp_energy(cpu_percent, execution_time, tdp_watts):
    """Calculate energy consumption based on TDP and CPU utilization."""
    power_consumption = tdp_watts * (cpu_percent / 100.0)
    energy_joules = power_consumption * execution_time
    return energy_joules
```

### 

## **3.2 Backend-Specific Implementations**

### **3.2.1 Localhost Backend**

The localhost backend serves as the reference implementation for comprehensive energy monitoring, providing direct access to hardware interfaces and system-level monitoring capabilities.

The localhost backend provides the most comprehensive energy monitoring capabilities, with direct access to hardware interfaces and system-level monitoring tools. This environment serves as the reference implementation for energy measurement accuracy and methodology validation.

#### Full Monitoring Access 

**Full Hardware Access:** Direct access to RAPL, PERF, and eBPF interfaces   
**System-Level Monitoring**: Complete PSUtil functionality   
**Real-Time Measurements**: High-frequency energy sampling   
**Validation Environment**: Reference measurements for other backends  
**Implementation Details**  
The localhost backend implementation includes specialized monitoring processes that run alongside function execution:

```py
class LocalhostEnergyMonitor:
    def __init__(self):
        self.rapl_monitor = RAPLMonitor()
        self.perf_monitor = PERFMonitor()
        self.ebpf_monitor = eBPFMonitor()
        self.psutil_monitor = PSUtilMonitor()
    
    def start_monitoring(self):
        """Start all monitoring subsystems."""
        self.rapl_monitor.start()
        self.perf_monitor.start()
        self.ebpf_monitor.deploy_programs()
        self.psutil_monitor.start()
    
    def collect_metrics(self):
        """Collect comprehensive energy metrics."""
        return {
            'rapl': self.rapl_monitor.get_metrics(),
            'perf': self.perf_monitor.get_metrics(),
            'ebpf': self.ebpf_monitor.get_metrics(),
            'psutil': self.psutil_monitor.get_metrics()
        }
```

### **3.2.2 Kubernetes Backend**

The Kubernetes backend extends energy monitoring capabilities to containerized environments, addressing the challenges of container isolation and resource management.

Kubernetes deployments require containerized energy monitoring solutions that work within the constraints of container isolation. Our implementation uses privileged containers with host system access for hardware-level energy measurements, while providing fallback mechanisms for restricted environments.

#### Container-Based Energy Monitoring

Kubernetes deployments require specialized approaches to energy monitoring within containerized environments:

**Privileged Containers**: Enable access to host system interfaces for hardware-level measurements   
**Host Network Access**: Provide connectivity to system monitoring interfaces   
**Volume Mounts**: Mount host filesystem paths for RAPL and PERF access   
**Resource Limits**: Ensure monitoring overhead doesn't impact function execution

### **3.2.3 AWS Lambda Backend**

AWS Lambda presents unique challenges for energy monitoring due to the fully managed nature of the execution environment and limited access to underlying hardware.

AWS Lambda presents unique challenges for energy monitoring due to the managed nature of the execution environment. Our implementation focuses on indirect energy estimation through CPU utilization metrics and execution time correlation, supplemented by AWS-specific instance information for energy modeling.

#### Indirect Energy Measurement

AWS Lambda energy monitoring relies on indirect measurement techniques due to platform constraints:

**CPU Utilization Correlation**: Correlate CPU usage patterns with energy consumption models **Execution Time Analysis**: Use execution duration as a proxy for energy consumption **Memory Allocation Impact**: Factor memory allocation into energy estimation **Instance Type Detection**: Identify underlying hardware for accurate energy modeling

## **3.3 Flexecutor code implementation?**

# **4.Evaluacion:**

## **4.1 Serverless applications**

In this project we analyze four key examples from the FlexExecutor framework, a distributed computing platform designed for energy-efficient serverless workflows. Each example demonstrates different computational paradigms and their energy consumption characteristics across various worker configurations and architectures (x86 vs ARM).

**Examples Analyzed:**

1. **Monte Carlo Pi Estimation** \- Numerical computation and statistical sampling  
2. **Video Processing** \- Computer vision and multimedia processing pipeline  
3. **Machine Learning** \- Distributed ensemble learning with PCA and LightGBM  
4. **Titanic Survival Prediction** \- Classification workflow with Random Forest

### **4.1.1 Monte Carlo Pi Estimation**

#### Research Area: Numerical Computing & Statistical Methods

   
The Monte Carlo Pi estimation example implements a distributed statistical sampling algorithm to approximate the mathematical constant π using random point generation within a unit circle. This represents a classic embarrassingly parallel computational problem ideal for studying distributed computing efficiency.

**Key Perks & Applications:**

- **Perfect Parallelization**: Each worker operates independently with no inter-worker communication  
- **Scalability Testing**: Ideal benchmark for measuring distributed system performance  
- **Energy Efficiency Analysis**: Pure computational workload for baseline energy measurements  
- **Statistical Convergence**: Demonstrates law of large numbers in distributed environments

**Technical Objectives**

* **Primary Objective**: Estimate π by distributing 100,000,000 random point generations across multiple workers, where each point (x,y) in the unit square \[0,1\]×\[0,1\] is tested for inclusion within the unit circle using the condition x² \+ y² ≤ 1\.

* **Mathematical Foundation**

```
π ≈ 4 × (points_inside_circle / total_points)
```

* Implementation Details  
- **Total Sample Size**: 100,000,000 points distributed across all workers  
- **Per-Worker Allocation**: `total_points ÷ num_workers` with remainder distribution  
- **Iteration Strategy**: 100,000 samples per iteration to optimize memory usage  
- **Convergence Monitoring**: Real-time π estimation with execution time tracking

* Technical Specifications

```py
def monte_carlo_pi_estimation(ctx: StageContext) -> None:
    TOTAL_POINTS_TARGET = 100_000_000
    points_per_worker = TOTAL_POINTS_TARGET // ctx.num_workers
    samples_per_iteration = 100000
    
    # Statistical sampling loop
    for iteration in range(max_iterations):
        points_inside_circle = 0
        for _ in range(samples_per_iteration):
            x, y = random.random(), random.random()
            if x * x + y * y <= 1.0:
                points_inside_circle += 1
```

* Performance Characteristics  
- **Computational Complexity**: O(n) where n \= total sample points  
- **Memory Requirements**: Minimal \- only counters and random number generation  
- **Communication Overhead**: Zero inter-worker communication required  
- **Scalability**: Linear scaling expected with worker count

### **4.1.2 Titanic Survival Prediction**

#### Research Area: Classification & Distributed Data Science

The Titanic example implements a distributed machine learning workflow for binary classification using the famous Titanic passenger dataset. This represents a typical data science workflow with preprocessing, feature engineering, and model evaluation, optimized for energy efficiency analysis.

Key Perks & Applications

- **Real-world Dataset**: Historical passenger data with mixed feature types  
- **Feature Engineering**: Categorical encoding and missing value handling  
- **Scalability Testing**: Synthetic datasets (6MB, 60MB) for performance analysis  
- **Energy Benchmarking**: Comprehensive energy consumption analysis across worker configurations

**Technical Objectives**

* **Primary Objective:**

Predict passenger survival probability using Random Forest classification with distributed data processing, while measuring energy consumption patterns across different worker configurations and dataset sizes.

* **Dataset Characteristics**  
- **Original Features**: Pclass, Sex, Age, SibSp, Parch, Fare  
- **Target Variable**: Survived (binary: 0=No, 1=Yes)  
- **Synthetic Scaling**:  
  - 6MB dataset: \~89,100 records  
  - 60MB dataset: \~891,000 records


* **Implementation Details**

```py
def train_model(ctx: StageContext) -> None:
    # Data preprocessing
    features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]
    chunk = chunk.dropna(subset=features + ["Survived"])
    
    # Feature engineering
    X = pd.get_dummies(chunk[features], columns=["Sex"], drop_first=True)
    y = chunk["Survived"]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Model training and evaluation
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
```

- **Algorithm**: Random Forest with 100 estimators  
- **Chunking Strategy**: Dynamic CSV partitioning with dataplug  
- **Data Processing**: Pandas-based preprocessing with scikit-learn  
- **Monitoring**: RAPL and TDP energy measurements  
- **Storage**: Flexible input/output with FlexExecutor storage abstraction

### **4.1.3 Machine Learning Ensemble Pipeline**

#### Research Area: Distributed Machine Learning & Ensemble Methods

The ML example implements a sophisticated distributed machine learning pipeline combining Principal Component Analysis (PCA) for dimensionality reduction with LightGBM ensemble training. This represents a compute-intensive, memory-efficient approach to large-scale machine learning.

Key Perks & Applications

- **Dimensionality Reduction**: PCA preprocessing for high-dimensional datasets  
- **Ensemble Learning**: Multiple LightGBM models for improved prediction accuracy  
- **Memory Efficiency**: Optimized for large datasets with memory constraints  
- **Production Ready**: Complete ML pipeline from preprocessing to prediction

**Technical Objectives:** 

* **Primary Objective**

Implement a distributed machine learning pipeline that processes high-dimensional training data through PCA dimensionality reduction, trains multiple LightGBM models in parallel, and aggregates predictions for improved accuracy.

##### Pipeline Architecture

**Stage 1: Principal Component Analysis (`pca`)**

- **Input**: High-dimensional training data (tab-separated format)  
- **Process**: Eigenvalue decomposition for dimensionality reduction  
- **Algorithm**: Covariance matrix eigenanalysis  
- **Output**: 100 principal components \+ transformation vectors  
- **Technical Implementation**:

```py
# Compute covariance matrix and eigendecomposition
ma = np.mean(a.T, axis=1)  # Mean centering
ca = a - ma                # Centered matrix
va = np.cov(ca.T)         # Covariance matrix
values, vectors = eig(va)  # Eigendecomposition
pa = vectors.T.dot(ca.T)   # Principal components
```

**Stage 2: Distributed Model Training (`train_with_multiprocessing`)**

- **Input**: PCA-transformed training data  
- **Process**: Sequential training of multiple LightGBM models  
- **Model Configuration**:  
  - Gradient Boosting Decision Trees (GBDT)  
  - Multi-class classification (10 classes)  
  - 30 boosting rounds per model  
  - Feature fraction and bagging for diversity  
- **Output**: Trained model files for ensemble aggregation

**Stage 3: Model Aggregation (`aggregate`)**

- **Input**: Multiple trained LightGBM models  
- **Process**: Model ensemble creation and prediction averaging  
- **Algorithm**: Weighted average of individual model predictions  
- **Output**: Merged ensemble model \+ accuracy metrics

**Stage 4: Final Testing (`test`)**

- **Input**: Ensemble predictions from multiple workers  
- **Process**: Cross-validation and final accuracy computation  
- **Output**: Final accuracy scores and performance metrics

* **Technical Specifications**

```py
# LightGBM Configuration
params = {
    "boosting_type": "gbdt",
    "objective": "multiclass",
    "num_classes": 10,
    "metric": {"multi_logloss"},
    "num_leaves": 50,
    "learning_rate": 0.05,
    "feature_fraction": feature_fraction,
    "bagging_fraction": chance,
    "max_depth": max_depth,
    "num_threads": 2,
}

# Memory-efficient ensemble prediction
class MergedLGBMClassifier(BaseEstimator):
    def predict(self, X):
        pred_list = [m.predict(X) for m in self.model_list]
        return sum(pred_list) / len(pred_list)
```

#### 

* **Performance Characteristics**  
- **Computational Complexity**: O(n×d×t) where n=samples, d=features, t=trees  
- **Memory Usage**: Optimized with sequential processing and cleanup  
- **Accuracy**: Ensemble methods typically achieve 5-15% improvement over single models  
- **Scalability**: Linear scaling with number of models in ensemble

### **4.1.4 Video Processing Pipeline**

#### Research Area: Computer Vision & Multimedia Processing

The video processing example implements a complete computer vision pipeline for video analysis, including temporal segmentation, frame extraction, image enhancement, and basic object analysis. This represents a memory-intensive, I/O-heavy workload typical of multimedia applications.

**Key Perks & Applications**

- **Pipeline Architecture**: Multi-stage processing workflow with data dependencies  
- **Memory Intensive**: Large video files require significant RAM and storage  
- **I/O Bound Operations**: Heavy disk and network I/O for video file handling  
- **Computer Vision Integration**: OpenCV and MoviePy for professional video processing

**Technical Objectives:**

* **Primary Objective**

Process video files through a four-stage pipeline: video segmentation → frame extraction → image enhancement → feature analysis, optimized for distributed serverless environments.

* **Pipeline Architecture**

**Stage 1: Video Segmentation (`split_videos`)**

- **Input**: Raw video files from storage  
- **Process**: Temporal chunking into 10-second segments  
- **Output**: Video chunks without audio (Lambda optimization)  
- **Technical Details**:

```py
clip_vc = vc.subclipped(start_time, end_time)
clip_vc.write_videofile(chunk_path, codec="libx264", audio=False)
```

**Stage 2: Frame Extraction (`extract_frames`)**

- **Input**: Video chunks from Stage 1  
- **Process**: Extract highest-quality frame per chunk using pixel intensity analysis  
- **Algorithm**: Grayscale conversion \+ average pixel value maximization  
- **Output**: Representative frames in PIL format  
- **Technical Details**:

```py
def calculate_average_pixel_value(image):
    gray_image = np.mean(image, axis=2).astype(np.uint8)
    return np.mean(gray_image)
```

**Stage 3: Image Enhancement (`sharpening_filter`)**

- **Input**: Extracted frames from Stage 2  
- **Process**: Convolution-based sharpening using custom kernel  
- **Kernel**: 3×3 sharpening matrix `[[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]`  
- **Output**: Enhanced frames with improved edge definition

**Stage 4: Feature Analysis (`classify_images`)**

- **Input**: Enhanced frames from Stage 3  
- **Process**: Computer vision feature extraction and analysis  
- **Features Extracted**:  
  - Image dimensions and color statistics  
  - Edge density using Canny edge detection  
  - Complexity scoring based on edge distribution  
- **Output**: JSON metadata with quantitative image analysis

* **Technical Specifications**

```py
# Memory optimization for serverless environments
temp_audiofile="/tmp/temp_audio.m4a"
remove_temp=True
ffmpeg_params=["-f", "mp4"]

# Edge detection for complexity analysis
edges = cv2.Canny(gray, 50, 150)
edge_density = np.sum(edges > 0) / (height * width)
complexity_score = edge_density * 100
```

#### Performance Characteristics

- **Memory Requirements**: High \- video files loaded entirely into memory  
- **I/O Intensity**: Extremely high \- multiple file read/write operations per stage  
- **CPU Usage**: Moderate \- primarily I/O bound with some image processing  
- **Storage Requirements**: Temporary storage for intermediate video chunks and frames

---

## **4.2 Comparative Analysis: Energy Efficiency Across Examples**

### **4.2.1 Computational Characteristics**

| Example | Type | CPU Intensity | Memory Usage | I/O Requirements | Parallelization |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Monte Carlo | Numerical | High | Low | Minimal | Perfect |
| Video Processing | Multimedia | Medium | Very High | Very High | Pipeline |
| ML Ensemble | Machine Learning | High | Medium | Medium | Model-parallel |
| Titanic | Data Science | Medium | Low | Low | Data-parallel |

### **4.2.2 Energy Consumption Patterns**

**Monte Carlo Pi Estimation**

- **Energy Profile**: CPU-bound with minimal memory/I/O overhead  
- **Scaling**: Linear energy scaling with perfect parallelization  
- **Efficiency**: Highest computational efficiency per joule

**Video Processing**

- **Energy Profile**: I/O-bound with high memory allocation costs  
- **Scaling**: Limited by memory bandwidth and storage I/O  
- **Efficiency**: Lower computational efficiency due to I/O overhead

**ML Ensemble**

- **Energy Profile**: Balanced CPU/memory usage with model complexity  
- **Scaling**: Good scaling with ensemble parallelization  
- **Efficiency**: Moderate efficiency with accuracy trade-offs

**Titanic Classification**

- **Energy Profile**: Moderate CPU usage with efficient data processing  
- **Scaling**: Sublinear scaling due to data preprocessing overhead  
- **Efficiency**: Good efficiency for data science workflows

## **4.3 Fiabilidad de TDP vs HW energy measurement (medido en k8s cluster)**

### **4.3.1 Gráficas de ejecuciones de las apps en lambda:** **Para cada app y para cada arch:**

1. #### Gráfico energy-cost

   2. #### Gráfico energy-time

### **4.3.2 Análisis comparativo entre x86 y arm (media, dist, por app, more...):**

3. #### % de ahorro € entre utilizar x86 vs arm

   4. #### % de \+time entre utilizar x86 vs arm

      5. #### % de ±cost entre utilizar x86 vs arm

### **4.3.3 (cualquier otro punto interesante que puedas derivar de las trazas de ejecución que has obtenido).**

# **5\. Conclusión (y next steps)**

Concluimos el trabajo destacando qué hemos conseguido con este TFG. Abrimos la puerta a que el presente trabajo serviría como base del green smart provisioner.


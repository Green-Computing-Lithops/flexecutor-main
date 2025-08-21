

# **An Expert-Level Report and Critical Feedback on the Flexecutor Framework for Green Computing in Lithops**

## **I. Foundational Analysis: Lithops, Serverless Computing, and the Green Computing Imperative**

This section establishes the fundamental context for the Master's Thesis (TFM). It defines the baseline system, the Lithops framework, explains its architectural philosophy, and frames the critical problem domain—energy consumption in cloud computing—that the thesis aims to address. A thorough understanding of these foundations is essential to properly evaluate the novelty and efficacy of the proposed flexecutor system.

### **1.1. The Serverless Paradigm and the Lithops Framework: A Baseline for Innovation**

The evolution of cloud computing has led to progressively higher levels of abstraction, culminating in the serverless computing model, often realized as Function-as-a-Service (FaaS). This paradigm fundamentally alters the developer's relationship with infrastructure, forming the operational environment into which the TFM's contributions are introduced.

#### **Core Principles of Serverless (FaaS)**

Serverless computing is characterized by a set of core principles that differentiate it from traditional infrastructure-as-a-service (IaaS) or platform-as-a-service (PaaS) models. The primary principle is the complete abstraction of the underlying servers, operating systems, and resource management.1 Developers deploy code in the form of functions, and the cloud provider is solely responsible for provisioning, scaling, and managing the infrastructure required to run that code. Execution is event-driven; functions are instantiated and run in response to specific triggers, such as an HTTP request or a new file appearing in an object store. This model is underpinned by a fine-grained, pay-per-use billing system, where costs are typically calculated based on the number of invocations and the precise duration of execution, often measured in milliseconds.1

This high level of abstraction presents a significant duality. On one hand, it dramatically simplifies development and deployment, allowing teams to focus on business logic rather than infrastructure management.2 On the other hand, it creates an "abstraction barrier" that obscures the underlying hardware and execution environment. This opacity makes direct measurement and control of non-functional properties like performance, and especially energy consumption, exceptionally difficult—a central challenge the TFM must confront.

#### **Lithops as a Multi-Cloud Abstraction Layer**

Within this serverless ecosystem, the Lithops framework emerges as a powerful tool for distributed computing. Its primary purpose is to enable developers to run unmodified local Python code at a massive scale across various cloud environments.3 Lithops' core value proposition is its "Write once, run anywhere" philosophy, providing a universal API that abstracts away the provider-specific nuances of different serverless platforms like AWS Lambda, Google Cloud Functions, or IBM Cloud Functions.1 This multi-cloud portability is a defining feature and a critical aspect against which any modification, including the TFM's energy-aware modules, must be evaluated.

#### **Architectural Pillars of Lithops**

The architecture of Lithops is modular and designed for extensibility, resting on three key pillars:

1. **FunctionExecutor:** This is the main user-facing API and the central orchestrator of any Lithops job.4 When a user calls a method like  
   map() or map\_reduce(), the FunctionExecutor is responsible for serializing the function and its data, invoking the necessary backend resources, and collecting the results. The TFM's flexecutor is a direct modification or replacement of this component, placing it at the very heart of the framework's logic.5  
2. **Compute Backends:** Lithops' portability is achieved through a pluggable architecture for compute backends. It supports a diverse range of execution environments, including serverless FaaS platforms, serverless container services like Google Cloud Run, traditional Virtual Machines (VMs), Kubernetes clusters, and even local machine processes for development and debugging.2 This modularity allows a single Python script to be executed seamlessly across vastly different infrastructures.  
3. **Storage Backends:** Given the stateless nature of serverless functions, Lithops relies on an intermediate storage layer, typically a cloud object store like Amazon S3 or IBM Cloud Object Storage, to manage state and communication.7 This storage backend is used for multiple critical tasks: staging the serialized code and dependencies for the workers, passing input data to each function invocation, and storing the results of each computation before they are collected by the client. This makes the object store the de facto communication backbone of a Lithops application.5

#### **Primary Use Cases**

The architecture of Lithops makes it exceptionally well-suited for workloads that are embarrassingly parallel—tasks that can be broken down into many independent sub-problems with little to no communication required between them.8 This has led to its successful application in a wide range of domains, including:

* **Big Data Analytics:** Processing massive datasets stored in object storage by partitioning the data and running an analytical function over each partition in parallel.2  
* **Monte Carlo Simulations:** Running thousands or millions of independent simulations simultaneously to model complex systems or estimate numerical values.8  
* **Hyperparameter Tuning:** Exploring a large search space of model parameters by training and evaluating numerous model variations in parallel.2  
* **Geospatial and Genomics Pipelines:** Executing complex, multi-stage data processing workflows where individual stages can be parallelized.9

These established use cases provide a clear set of representative benchmarks that should be used to validate the performance and effectiveness of the flexecutor.

### **1.2. The Energy Challenge in Distributed Cloud Systems: Framing the Problem**

The convenience and scalability of cloud computing come at a significant environmental cost. The TFM positions itself within the field of Green Computing, which seeks to mitigate this impact.

#### **The Environmental Impact of Cloud Computing**

Data centers, the physical foundation of all cloud services, are massive consumers of electrical energy.11 The Information and Communication Technologies (ICT) sector is a significant contributor to global carbon emissions, and as the demand for cloud services grows, so does the energy footprint of these facilities.12 This has created a strong economic and societal impetus to improve the energy efficiency of cloud operations, a movement broadly known as Green Computing or Green IT.13

The core challenge, as previously noted, is the abstraction inherent in public cloud and especially serverless platforms. Users are typically billed for resource-time (e.g., GB-seconds) and invocations, not for energy consumption (kWh).15 This lack of direct feedback or control makes it difficult for users to make energy-conscious decisions. The TFM's primary goal is to pierce this veil of abstraction by creating a system that can estimate and act upon energy consumption data.

#### **Goals of Green Computing**

The field of Green Computing encompasses a broad set of objectives. The primary goals include maximizing energy efficiency throughout a product's lifetime, reducing the use of hazardous materials in hardware manufacturing, and promoting the recyclability or biodegradability of obsolete equipment and waste.13 The TFM's work is squarely focused on the first and most prominent of these goals: improving the operational energy efficiency of software running in the cloud.

#### **Metrics for "Greenness"**

The data center industry has developed several high-level metrics to quantify efficiency. These include:

* **Power Usage Effectiveness (PUE):** The ratio of total facility energy to the energy delivered to IT equipment. A PUE of 1.0 would represent a perfectly efficient facility with no overhead for cooling or power distribution.16  
* **Carbon Usage Effectiveness (CUE):** The ratio of total carbon dioxide equivalent emissions (kgCO2​eq) to the energy consumption of the IT equipment (kWh).16  
* **Green Energy Coefficient (GEC):** A measure of the proportion of energy consumed by a data center that comes from renewable sources.16

While the TFM's flexecutor cannot directly measure or influence these facility-level metrics, they form the essential vocabulary of the problem domain. The "energy modules" proposed in the thesis must define their own, more granular metrics at the level of individual functions and jobs, which can then be seen as contributing to the improvement of these higher-level indicators.

A critical point of analysis for the TFM is the inherent tension between Lithops' core design philosophy and the requirements of an energy-aware system. Lithops' greatest strength is its multi-cloud portability, the ability to run code seamlessly across different providers.1 However, energy monitoring and optimization are often deeply tied to the specific hardware and APIs of a particular cloud provider. For example, the metrics available through AWS CloudWatch are different from those in Azure Monitor.17 This creates a dilemma: an energy module that is generic enough to be portable may be too inaccurate to be useful, while a module that is accurate for one cloud may not be portable to others. The TFM's design must therefore be critically evaluated on how it navigates this portability-versus-specialization trade-off. A successful implementation would need to define an abstract energy model that can be implemented with provider-specific drivers, preserving the modularity of the Lithops backend architecture.

Furthermore, the introduction of energy as an optimization metric fundamentally changes the definition of "efficiency" in a serverless context. Historically, serverless optimization has been a two-dimensional problem, seeking to balance execution time (performance) and monetary cost.15 The TFM introduces energy as a third, competing dimension. The fastest execution configuration (e.g., allocating more memory to a Lambda function) might not be the most energy-efficient. The cheapest option might be slow and consume more total energy. The core intellectual contribution of the

flexecutor, therefore, is not merely to measure energy, but to navigate this new, three-dimensional optimization space. Its scheduling policy must, whether explicitly or implicitly, implement a utility function that weighs the relative importance of time, cost, and energy. The thesis must clearly articulate how this balance is struck and provide a robust justification for the trade-offs it chooses to make.

## **II. Architectural and Implementation Review: The flexecutor and Energy-Aware Fork**

This section provides a deep, critical analysis of the TFM's primary software artifacts: the flexecutor component and the modifications made in the lithops\_fork to introduce energy-awareness. The assessment focuses on the soundness of the design choices, their integration with the existing Lithops architecture, and their potential impact on the framework's stability, maintainability, and core principles.

### **2.1. Deconstruction of the flexecutor Architecture**

The flexecutor is presented as the central innovation of the TFM. Its name implies a flexible execution engine, presumably one that can adapt its behavior based on energy-related inputs. A rigorous evaluation requires deconstructing its design and comparing it to established patterns.

#### **Relationship to lithops.FunctionExecutor**

The method of integrating flexecutor with the standard lithops.FunctionExecutor is a critical architectural decision. The FunctionExecutor is the primary entry point for all Lithops jobs, orchestrating the entire execution flow.4 There are several possible implementation strategies for

flexecutor, each with distinct implications:

* **Subclassing:** flexecutor could inherit from FunctionExecutor and override key methods (e.g., \_invoke, map) to inject the energy-aware scheduling logic. This is often the cleanest and most maintainable approach, as it preserves API compatibility and allows for the reuse of the parent class's extensive logic.  
* **Wrapping (Decorator Pattern):** flexecutor could act as a wrapper object that holds an instance of a standard FunctionExecutor and delegates most calls to it, intercepting only those necessary to implement its scheduling policy. This promotes composition over inheritance but can be more complex to implement correctly.  
* **Full Replacement:** flexecutor could be an entirely new implementation of the executor interface. This approach offers the most freedom but carries the highest risk and maintenance burden, as it would require re-implementing a significant amount of complex orchestration logic.

The TFM must justify its chosen approach, with subclassing being the most architecturally sound option for this type of extension.

#### **The Locus of Control: The Scheduling Policy**

The "brain" of the flexecutor is its scheduling policy. This is the algorithm that consumes data from the energy modules and makes decisions to optimize for energy efficiency. The power and sophistication of the entire system are determined by the scope of these decisions. The key questions to analyze are:

* **Backend Selection:** Does the policy operate at the highest level, choosing which compute backend to use for a given job? For example, it might decide to run a short, CPU-intensive task on a serverless FaaS platform but route a long-running, memory-heavy task to a standalone VM backend, based on their respective energy profiles.  
* **Parameter Tuning:** Does the policy influence the runtime parameters *within* a specific backend? A prime example in AWS Lambda is the memory allocation, which is directly tied to the allocated CPU power. An intelligent scheduler could select the memory size that provides the optimal balance of performance and energy consumption for a given function.  
* **Workload Partitioning:** Does the policy affect how the workload itself is structured? Lithops' map function includes a chunksize parameter that determines how many data items are processed by a single function invocation.4 The energy profile of a function can vary with its duration. A sophisticated scheduler could adjust the  
  chunksize to create invocations of a duration that is known to be most energy-efficient for the target backend.

#### **Comparison with Existing Executor Patterns**

To assess the novelty of the flexecutor, it is useful to compare it with other executor frameworks. The Java Executor Framework, for instance, provides several concrete executor types with different scheduling policies, such as FixedThreadPool (executes tasks with a fixed number of threads) and CachedThreadPool (creates new threads as needed and reuses old ones).18 In the domain of federated learning, frameworks like NVIDIA FLARE use an

Executor concept on the client side to manage specific tasks like training and validation.19 These examples show a common pattern of specialized executors for specific scheduling behaviors. The

flexecutor fits this pattern, but its claim to "flexibility" must be substantiated by a policy engine that is configurable or adaptive, rather than implementing a single, hard-coded energy-saving strategy.

### **2.2. Analysis of the lithops\_fork and the "Energy Modules"**

The flexecutor relies on data provided by the "energy modules" integrated into a fork of the Lithops source code. The quality and design of these modules are paramount to the system's success.

#### **Code-Level Implementation**

A thorough review of the lithops\_fork would focus on several key aspects of the energy modules' implementation:

* **Data Collection Method:** The most critical question is how energy-related data is acquired. Given the opacity of FaaS platforms, direct measurement is impossible. The modules must therefore rely on indirect methods, such as querying cloud provider monitoring APIs (e.g., AWS CloudWatch for metrics like Duration and BilledDuration) or, more likely, implementing an estimation model based on performance counters and resource allocation (e.g., a model that predicts energy based on CPU time, memory size, and execution duration).  
* **Data Persistence and Management:** Where is the collected energy data stored? Is it held transiently in memory for the duration of a job, or is it persisted to the storage backend (e.g., as metadata alongside the job's results)? Persisting this data is crucial, as it creates a historical record that can be used to train and refine the energy models over time, transforming the system from a static estimator into a learning system.  
* **Modularity and Intrusiveness:** A well-architected solution would implement the energy modules in a way that is minimally intrusive to the Lithops core. Ideally, energy monitoring should be a feature that can be enabled or disabled through the Lithops configuration file. The modules should be designed to be pluggable, allowing new models for different backends (e.g., one for AWS Lambda, another for Azure Functions) to be added without modifying the core orchestration logic in the FunctionExecutor or the worker-side JobRunner.5 Invasive changes that tightly couple the energy logic with the core framework would be a significant architectural flaw, making the fork difficult to maintain and merge with upstream Lithops updates.

#### **Impact on Core Lithops Functionality**

The introduction of new modules inevitably carries the risk of unintended side effects. The analysis must consider:

* **Performance Overhead:** The act of collecting, processing, and storing energy data consumes resources and time. This introduces overhead into the execution flow. The TFM must rigorously quantify this overhead to demonstrate that the energy saved by the flexecutor's decisions is not negated by the cost of making those decisions.  
* **Portability:** As highlighted in Section I, this is a primary concern. The code for the energy modules must be scrutinized for any hard-coded dependencies on a specific cloud provider's services, metrics, or APIs. If the modules rely on AWS CloudWatch metrics that have no equivalent in Google Cloud Monitoring, for example, then the system has compromised Lithops' fundamental promise of multi-cloud portability.  
* **Scalability:** Lithops is designed to scale to thousands of concurrent function invocations.8 The energy monitoring system must be able to scale accordingly. If, for example, every function invocation attempts to write its energy data to a single, centralized collection point, that point could easily become a performance bottleneck, crippling the scalability of the entire application. A scalable design would likely leverage the distributed nature of the object storage backend.

A fundamental challenge in the design of an energy-aware scheduler is the "chicken-and-egg" problem of decision-making. To make an optimal, energy-efficient scheduling decision (e.g., choosing a backend or configuring its parameters), the flexecutor requires data on the expected energy consumption of the task. However, this data can only be obtained with certainty *after* the task has been executed on that backend. This creates a classic exploration-versus-exploitation dilemma. The system must either rely on *a priori* models, which may be inaccurate, or it must perform exploratory "probe" executions on different backends to build an energy profile, a process which itself consumes time and energy. The TFM's architecture must explicitly address this. A naive implementation might rely on static, pre-configured models, which would be a significant weakness. A more sophisticated flexecutor would incorporate a learning component, perhaps using techniques like multi-armed bandits, to continuously refine its energy models based on observed performance, balancing the need to exploit known-good configurations with the need to explore potentially better new ones.

This leads to a deeper architectural tension with the core philosophy of the underlying platform. Both Lithops and the serverless functions it orchestrates are designed to be fundamentally stateless.1 Each invocation is, in theory, a self-contained, independent unit of work. However, an effective, learning-based, energy-aware scheduler is inherently

*stateful*. It requires a persistent, historical database of past task executions—their characteristics, the configuration they ran with, and their resulting performance and energy consumption—to inform future scheduling decisions. The TFM's architecture must therefore introduce a stateful component into this stateless ecosystem. The implementation of this state management is a non-trivial architectural problem. Using the object storage backend (e.g., S3) is a natural choice within the Lithops model, but it raises questions of data consistency, query performance, and cost at scale. This necessary introduction of state represents a significant departure from the standard Lithops execution model and is a key point of critical analysis for the TFM's design.

## **III. Critical Evaluation of the Energy-Aware Methodology**

This section transitions from evaluating the system's architecture (*what* was built) to scrutinizing the scientific and engineering validity of its core methodology (*how credible* its claims are). The entire value of the TFM rests on the soundness of its approach to measuring and optimizing energy consumption. Without a robust and verifiable methodology, the flexecutor is merely an exercise in software engineering; with one, it becomes a contribution to scientific research.

To provide a clear framework for this evaluation, the following table compares common software energy measurement techniques, highlighting their principles and their applicability to the challenging FaaS environment.

**Table 1: Comparative Analysis of Software Energy Measurement Techniques**

| Technique | Principle | Accuracy | Overhead | Granularity | Applicability to FaaS |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Hardware-based** | Direct measurement of electrical power drawn by the system or its components using external power monitors or internal power supply unit (PSU) sensors.21 | Very High | Low (measurement) | System-level or Component-level | **None.** The user has no physical access to the underlying server hardware in a public cloud. |
| **Software-based (PMCs)** | Reading hardware Performance Monitoring Counters (PMCs) from the CPU (e.g., instructions retired, cache misses) and using them in a model to estimate power. | High | Low to Medium | Process-level, Core-level | **None.** FaaS environments do not expose low-level hardware counters to user code due to security and multi-tenancy isolation. |
| **Cloud Provider Metrics** | Aggregating and analyzing metrics provided by the cloud vendor's monitoring service (e.g., AWS CloudWatch, Azure Monitor).15 | Low to Medium | Low | VM-level or Function-level (for duration, memory) | **High.** This is the most direct source of performance data available in a FaaS environment, but it does not directly report energy. |
| **Model-based Estimation** | Creating a mathematical model that predicts energy consumption based on high-level, observable software metrics like CPU utilization, memory usage, and execution time.23 | Variable (depends on model quality and calibration) | Low | Application-level or Function-level | **Very High.** This is the most feasible and likely approach for the TFM, as it relies only on data that can be obtained from within the function or from provider APIs. |

### **3.1. Energy Measurement and Modeling: A Critique of the Approach**

Given the constraints outlined in Table 1, the TFM's "energy modules" almost certainly employ a **Model-based Estimation** approach. This is a valid and pragmatic choice, but its scientific credibility depends entirely on the rigor with which the model is designed, calibrated, and validated.

#### **Model Design and Justification**

The first step in a critical analysis is to examine the model itself. The TFM must clearly define the mathematical form of its energy model and justify the inclusion of each variable. Typical variables in such models include:

* CPU utilization or, in a serverless context, a proxy like billed execution duration.  
* Memory allocation, as larger function configurations often come with more powerful virtual CPUs.  
* I/O operations, as data transfer to and from storage or over the network consumes energy.23

The thesis must provide a strong theoretical or empirical rationale for its choice of variables and the relationship between them (e.g., linear, polynomial, or more complex). For instance, a simple linear model might take the form:

Etotal​=Pidle​×t+βcpu​×(CPUutil​×t)+βmem​×(Memalloc​)

where Etotal​ is the total energy, Pidle​ is the baseline power draw, t is time, and βcpu​ and βmem​ are coefficients for CPU and memory usage. The TFM must present and defend its specific model.

#### **Calibration and Validation**

This is the single most critical aspect of the TFM's methodology. An uncalibrated and unvalidated model produces numbers that are, scientifically speaking, arbitrary. The only way to establish the "ground truth" necessary to validate the model is to compare its predictions against direct, **Hardware-based** measurements.25

A rigorous TFM must describe, in detail, a calibration experiment. This would involve:

1. Setting up a dedicated physical machine (e.g., a server or desktop) where the hardware is known and constant.  
2. Connecting this machine to a high-precision external power meter to measure its real power consumption.22  
3. Running a series of controlled workloads on this machine that are representative of the tasks to be run in the cloud.  
4. Simultaneously, collecting the software metrics (CPU usage, memory, etc.) that are the inputs to the energy model.  
5. Using this paired dataset (real energy measurements and software metrics) to train the model's coefficients (e.g., using linear regression) and validate its predictive accuracy against a hold-out test set.

Without a detailed account of such an experiment, the energy figures produced by the TFM's modules are unsubstantiated, and any conclusions drawn from them are scientifically unsound.

#### **Generality of the Model**

The public cloud is a massively heterogeneous environment. A function may run on an Intel Xeon processor in one invocation and an AMD EPYC or AWS Graviton (ARM) processor in the next. These architectures have vastly different power characteristics.23 Therefore, a single, universal energy model is highly unlikely to be accurate across all possible hardware. A sophisticated TFM would acknowledge this heterogeneity. It might propose a methodology for creating different models for different processor families or, at a minimum, quantify the model's error on different hardware types and discuss this as a limitation. A failure to address the issue of hardware heterogeneity is a significant methodological weakness.

### **3.2. Energy-Driven Optimization Strategies: From Data to Decisions**

Once the energy modules produce data, the flexecutor must use that data to make intelligent decisions. The quality of these decisions depends on the sophistication of the optimization strategy.

#### **The Optimization Algorithm**

The TFM must clearly describe the scheduling algorithm implemented within the flexecutor. Is it a simple, greedy algorithm, such as "always select the compute backend with the lowest predicted energy consumption per task"? While simple to implement, such an approach ignores the critical dimensions of performance and cost and may lead to unacceptable trade-offs (e.g., choosing a very slow but slightly more energy-efficient option).

A more advanced approach would frame the problem as a multi-objective optimization, seeking to find a solution on the Pareto frontier of energy, cost, and time. This would allow a user to specify their priorities, leading to a more genuinely "flexible" executor.

#### **Carbon-Awareness vs. Energy-Awareness**

A key distinction in modern Green Computing is the difference between minimizing energy consumption (measured in kWh) and minimizing carbon emissions (measured in kgCO2​eq).14 These are not the same. The carbon intensity of the electrical grid varies significantly by geographical region and time of day, depending on the mix of power sources (e.g., solar, wind, coal).

A truly advanced system would be **carbon-aware**. It would not just seek to use less energy, but to use energy when and where it is "greener." This involves integrating real-time grid carbon intensity data from external services and using this information to influence scheduling decisions. For example, a carbon-aware flexecutor might choose to run a job in a cloud region powered by renewables, even if it is slightly less energy-efficient, or delay a non-urgent job until a time when the local grid's carbon intensity is lower. The TFM should be evaluated on whether it makes this crucial distinction. Conflating energy with carbon is a common but significant oversimplification in the field.

#### **Static vs. Dynamic Optimization**

The scheduling strategy can be either static or dynamic. A static scheduler makes a single, upfront decision at the beginning of a job (e.g., "run this entire map job on AWS Lambda with 1024 MB of memory"). A dynamic scheduler, in contrast, could adapt its strategy during the job's execution. For a long-running job involving thousands of function calls, a dynamic scheduler could monitor performance and energy consumption in real-time and adjust its strategy on the fly, perhaps by shifting the remaining workload to a different backend or reconfiguring runtime parameters. The TFM's implementation should be analyzed to determine which approach it takes, as a dynamic strategy is considerably more powerful and complex.

The entire optimization framework operates under the principle of "Garbage In, Garbage Out." The flexecutor's sophisticated scheduling algorithm is entirely dependent on the data provided by the energy modules.27 If the underlying energy model is poorly calibrated, inaccurate, or not generalizable to the cloud's heterogeneous hardware, it will produce flawed data ("Garbage In"). The scheduler will then diligently process this flawed data and make what it calculates to be an optimal decision, but this decision will be based on a false representation of reality, leading to suboptimal or even counterproductive outcomes ("Garbage Out"). This dependency chain means that the TFM's single greatest point of potential failure is the empirical validation of its energy model. The scientific credibility of the entire thesis stands or falls on the strength and rigor of that validation experiment.

This focus on operational energy, while a valid and important research area, also highlights a potential limitation when viewed through the broader lens of Green Computing. A holistic analysis of environmental impact considers the entire product lifecycle, which includes the energy and resources consumed during manufacturing (often called "embodied carbon" or "embodied energy") and the environmental cost of disposal (e-waste).13 The TFM's methodology, like most software-focused research, exclusively addresses the

*operational* phase. While likely beyond the scope of a Master's thesis to solve, a truly deep understanding of the field would involve acknowledging this limitation. A discussion in the "Future Work" section could speculate on how a future, more advanced flexecutor might consider lifecycle impact. For example, given a choice between scheduling a workload on newer, more operationally efficient hardware versus older, less efficient hardware, the decision is not obvious. The former reduces operational energy, while the latter extends the useful life of existing hardware, delaying its contribution to e-waste and amortizing its embodied carbon over a longer period. Acknowledging this complex trade-off would demonstrate a mature and nuanced perspective on the challenges of sustainable computing.

## **IV. Assessment of Experimental Validation and Contribution**

This section evaluates the TFM as a piece of scientific work. It critically assesses the experiments designed to prove the flexecutor's effectiveness, the metrics used to define success, and the overall positioning of the work within the existing landscape of academic and industrial research, particularly in light of high-impact precedents.

### **4.1. Benchmarking and Performance Analysis: A Critique of the Experimental Design**

The credibility of the TFM's claims hinges on a well-designed and rigorously executed set of experiments. The goal is not just to show that the flexecutor "works," but to quantify its benefits and costs in a scientifically defensible manner.

#### **Defining the Baseline**

The choice of a baseline for comparison is fundamental to any experiment. The only valid and compelling baseline for this TFM is the **unmodified, stock lithops.FunctionExecutor**. The central experimental question is: "Does the flexecutor's energy-aware scheduling policy provide a tangible, measurable benefit over Lithops' default scheduling behavior?" Comparing against any other system (e.g., a different framework or a hypothetical "straw man" scheduler) would fail to demonstrate the value of the TFM's specific modifications to Lithops. The experiments must clearly show a "before and after" picture.

#### **Workload Selection**

The benchmarks used for evaluation must be representative of the real-world use cases for which Lithops is designed.10 A robust experimental suite would not rely on a single "hello world" function but would include a variety of workloads with different performance characteristics to test the

flexecutor's adaptability. Appropriate choices would include:

* **A CPU-bound task:** An application where the execution time is dominated by computation. Classic examples include Monte Carlo simulations for PI estimation or the calculation of Mandelbrot sets.10 This tests the scheduler's ability to optimize for computational efficiency.  
* **An I/O-bound task:** A workload where the bottleneck is reading from or writing to the storage backend. An example would be a data processing job that reads and aggregates data from thousands of small objects in cloud storage. This tests the scheduler's awareness of data transfer energy costs.  
* **A mixed workload:** A more realistic application that involves both significant computation and I/O. Hyperparameter tuning for a small machine learning model, where data is loaded and then a model is trained, would be an excellent example.10

Using a diverse set of workloads allows the TFM to demonstrate the generality of its solution and identify the conditions under which it is most (and least) effective.

#### **Metrics for Success**

To provide a complete picture, the TFM must report on the trifecta of key metrics that define serverless efficiency:

1. **Energy Savings:** This is the primary claim of the thesis. Results should be reported in standardized units (Joules or kWh) per job or per task, allowing for clear comparison. This data would be generated by the TFM's own energy modules.  
2. **Performance Impact:** The effect on total execution time (wall-clock time). It is crucial to determine if the energy savings came at the cost of a significant performance penalty. A scheduler that saves 5% on energy but makes the job 50% slower is unlikely to be adopted in practice.  
3. **Cost Impact:** The effect on the final bill from the cloud provider. Since serverless billing is based on execution time and resource allocation, changes made by the scheduler will directly impact cost.

The TFM should present these results clearly, ideally using visualizations that illustrate the trade-offs. A 3D scatter plot with axes for Energy, Time, and Cost, or a series of 2D plots showing the relationship between each pair, would be highly effective at communicating the nuanced performance of the flexecutor.

A critical flaw in a simple experimental design is the failure to isolate variables. A naive experiment might only compare two conditions: (A) the baseline stock Lithops, and (B) the flexecutor with both energy measurement and the new scheduling policy enabled. If condition B shows an improvement over A, it is impossible to definitively attribute that improvement to the scheduling policy. The improvement could be an artifact of the measurement process itself, or the measurement overhead could be masking the true benefit of the scheduler. A much more rigorous experimental design would employ an **ablation study** with at least three conditions:

* **(a) Baseline:** Stock Lithops, with no modifications.  
* **(b) Measurement Only:** Lithops with the energy measurement modules *enabled*, but with a "dummy" scheduler that ignores the energy data and uses the default Lithops behavior.  
* **(c) Full System:** Lithops with both energy measurement and the flexecutor's intelligent scheduling policy enabled.

This design allows for a much more precise analysis. The difference between (a) and (b) quantifies the performance and cost *overhead* of the measurement system itself. The difference between (b) and (c) isolates and quantifies the net *benefit* of the scheduling policy. Adopting this more sophisticated experimental design would dramatically increase the scientific validity of the TFM's conclusions.

### **4.2. Positioning and Novelty: Comparison with the State of the Art**

A Master's Thesis must not only present a working system but also situate that work within the broader field of research and clearly articulate its novel contribution.

#### **The MareNostrum5 Precedent**

Recent research on deploying Lithops on the MareNostrum5 (MN5) supercomputer sets an extremely high bar for work in this area.30 This research, conducted by researchers at the Barcelona Supercomputing Center (BSC) and Universitat Rovira i Virgili (URV), demonstrates the creation of a new Lithops HPC compute backend. Their evaluation shows that Lithops-HPC on MN5 can achieve significantly higher performance (up to 1.5x the FLOPS of AWS) and superior object storage bandwidth (3-5x faster than AWS S3) compared to commercial cloud platforms, while also reducing CPU wastage.31 This work proves that the Lithops framework is adaptable enough to be optimized for high-performance, resource-efficient computing in demanding HPC environments.

#### **Key Differentiators**

The TFM must clearly and explicitly differentiate its contribution from this precedent. A failure to do so risks having the work perceived as incremental or less significant. The key points of differentiation are likely to be:

* **Difference in Focus:** The MN5 research is primarily focused on maximizing *performance* (FLOPS, bandwidth) and *resource efficiency* (reducing CPU idle time) within an HPC context.30 In contrast, the TFM's stated focus is on minimizing  
  *environmental impact* (energy consumption and, potentially, carbon emissions) in a general-purpose public cloud context. These are related but distinct optimization goals.  
* **Difference in Environment:** The MN5 work is conducted on a known, controlled, on-premise supercomputer. In such an environment, the underlying hardware is homogeneous and well-understood, and direct, accurate performance and power monitoring is more feasible. The TFM, conversely, targets the "messy" reality of the public cloud: a heterogeneous, opaque, and geographically distributed environment where direct measurement is impossible. This makes the TFM's technical problem significantly harder, but its solution, if successful, is potentially more broadly applicable to the majority of cloud users.

#### **Contribution to Knowledge**

The TFM's introduction and conclusion must be laser-focused on defining and defending its specific, novel contribution to the field. Based on the analysis, the most defensible claims of novelty are likely to be one of the following:

1. **A Novel Energy Model for Serverless Platforms:** The development and, crucially, the rigorous empirical validation of a new model for accurately estimating the energy consumption of FaaS functions.  
2. **The flexecutor Architecture:** The design and implementation of a flexible, policy-driven executor for a serverless framework that can perform multi-objective optimization across energy, cost, and performance.  
3. **The First Empirical Demonstration:** The first comprehensive, empirical study showing that energy-aware scheduling can be practically implemented within a general-purpose, multi-cloud serverless framework like Lithops and can yield significant energy savings under realistic workloads.

The distinction between the goals of the MareNostrum5 work and the TFM is fundamental. The MN5 research is about achieving HPC-level *efficiency*, which is concerned with maximizing the amount of computational work done per unit of time on a fixed, high-value asset. The TFM's goal is to achieve cloud *greenness*, which is concerned with minimizing the total environmental impact (energy and carbon) across a vast, flexible, on-demand fleet of commodity resources. These are different paradigms. HPC efficiency aims to make a single serverless function run as fast as possible. Cloud greenness aims to orchestrate thousands of such functions across the globe in the most environmentally responsible manner. Framing the TFM's contribution in this way—as a tool for **"Green Orchestration"** rather than "HPC-style Performance Optimization"—will more accurately position its novelty and highlight its unique value to the field of sustainable computing.

## **V. Synthesis and Recommendations for Advancement**

This final section provides a consolidated, high-level assessment of the TFM. It summarizes the project's principal strengths and weaknesses and offers concrete, actionable recommendations for improving the thesis for submission and for guiding future research in this promising area.

### **5.1. Summary of Strengths and Weaknesses**

The TFM represents a significant and commendable effort to address a challenging and highly relevant problem at the intersection of serverless computing and sustainable IT. The evaluation identifies several key strengths alongside areas that require further development to elevate the work to its full potential.

#### **Strengths**

* **Novelty and Relevance:** The core concept of creating an energy-aware execution engine for a popular multi-cloud serverless framework like Lithops is both strong and novel. It directly addresses the growing concern over the environmental impact of cloud computing, placing the work at the forefront of the Green Computing field.  
* **Practical Implementation:** The development of a working software artifact—the flexecutor and the associated lithops\_fork—is a substantial accomplishment for a Master's-level project. It demonstrates not only a theoretical understanding but also the practical engineering skills required to modify a complex, real-world framework.  
* **Ambitious Scope:** By attempting to tackle the problem of energy measurement within the opaque and heterogeneous environment of public FaaS platforms, the TFM demonstrates a strong grasp of the key challenges in the field and a willingness to engage with a difficult, unsolved problem.

#### **Weaknesses (to be addressed)**

* **Methodological Rigor:** The project's scientific credibility is critically dependent on the accuracy of its energy model. As analyzed in Section III, without a rigorous calibration and validation experiment comparing the model's estimates to ground-truth measurements from a hardware power meter, the results are scientifically unsubstantiated. This stands as the most significant potential weakness of the thesis.  
* **Experimental Design:** The current experimental plan may lack the necessary controls to produce definitive conclusions. The absence of an ablation study makes it difficult to isolate the overhead of measurement from the benefit of the scheduling policy. Furthermore, relying on overly simplistic benchmarks could limit the generalizability of the findings.  
* **Architectural Purity:** The implementation introduces architectural trade-offs that must be more explicitly acknowledged and justified. The potential compromise of Lithops' core multi-cloud portability principle and the introduction of a stateful data requirement into a fundamentally stateless execution model are significant design decisions that warrant a thorough discussion of their implications.

### **5.2. Strategic Recommendations for Future Work**

The following recommendations are divided into short-term actions to strengthen the thesis for submission and long-term research directions that could build upon this work.

#### **Short-Term (Thesis Improvements)**

1. **Prioritize Model Validation:** The highest priority must be to conduct and thoroughly document a rigorous calibration experiment for the energy model. This involves comparing the model's predictions against real-world measurements from a hardware power meter on a controlled physical system. This single addition will provide the empirical foundation that the entire thesis needs to be scientifically credible.  
2. **Implement an Ablation Study:** Refine the experimental design to include an ablation study, as described in Section IV. This will allow for the precise quantification of both the overhead introduced by the energy modules and the net benefit provided by the flexecutor's scheduling algorithm, leading to much stronger and more defensible conclusions.  
3. **Explicitly Discuss Trade-offs:** Dedicate a section of the thesis to a frank discussion of the architectural trade-offs made. Acknowledge the tension between the energy modules and Lithops' portability, and explain the necessity of introducing state into a stateless model. Justifying these decisions demonstrates architectural maturity and intellectual honesty.

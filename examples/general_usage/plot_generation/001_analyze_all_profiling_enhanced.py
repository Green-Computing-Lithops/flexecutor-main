
import os
import json
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# TDP values from the original analysis script
TDP_VALUE = 180  # Conversion factor from watts to joules
TDP_VALUE_ARM = 100  # ARM architecture multiplier -> conservative approach
TDP_VALUE_X86 = 220  # x86 architecture multiplier -> conservative approach

# AWS x86 processor-specific TDP values (Thermal Design Power in Watts)
AWS_X86_PROCESSORS = {
    "AMD EPYC": {
        "tdp_watts": 225,
        "description": "AMD EPYC processor for AWS x86 instances"
    },
    "Intel(R) Xeon(R) Processor @ 2.50GHz": {
        "tdp_watts": 240,
        "description": "Intel Xeon processor @ 2.50GHz for AWS x86 instances"
    },
    "Intel(R) Xeon(R) Processor @ 2.90GHz": {
        "tdp_watts": 240,
        "description": "Intel Xeon processor @ 2.90GHz for AWS x86 instances"
    },
    "Intel(R) Xeon(R) Processor @ 3.00GHz": {
        "tdp_watts": 300,
        "description": "Intel Xeon processor @ 3.00GHz for AWS x86 instances"
    },
    "Intel(R) Core(TM) i7-10510U CPU @ 1.80GHz": {
        "tdp_watts": 15,
        "description": "Intel Core i7-10510U CPU @ 1.80GHz for AWS x86 instances"
    },
    # arm processors typically have lower TDP, handled separately
    "aarch64": {
        "tdp_watts": 100,
        "description": "GRAVITON 2: ARM architecture for AWS instances"
   }

}

# AWS pricing for ARM and x86 architectures
PRICE_AWS_ARM = 0.00001334  # AWS pricing for ARM
PRICE_AWS_X86 = 0.00001667  # AWS pricing for x86

# Base directories to search for profiling data (All examples)
PROFILING_DIRECTORIES = [
    "../../ml/profiling",
    "../../montecarlo_pi_estimation/profiling",
    "../../video/profiling",
    "../../titanic/profiling"
]

# Example descriptions for classification
EXAMPLE_DESCRIPTIONS = {
    "ml": "Machine learning training and inference workload",
    "md": "Machine learning training and inference workload", 
    "montecarlo": "Monte Carlo Pi estimation simulation",
    "pi": "Monte Carlo Pi estimation simulation",
    "video": "Video processing and object detection workload",
    "titanic": "Titanic dataset analysis and prediction workload",
    "machine_learning": "Machine learning training and inference workload",
    "montecarlo_pi_estimation": "Monte Carlo Pi estimation simulation",
    "video_processing": "Video processing and object detection workload"
}

def parse_folder_name_enhanced(folder_name):
    """
    Parse folder name to extract example, memory, platform, and architecture info.
    
    Expected format: example_memory_platform_architecture
    e.g., ml_aws_1024Mb_arm, md_aws_512Mb_arm, etc.
    
    Args:
        folder_name (str): Name of the folder containing JSON files
        
    Returns:
        dict: Parsed information with keys: example, memory, platform, architecture
    """
    parts = folder_name.split('_')
    
    parsed_info = {
        "example": "unknown",
        "memory": "unknown", 
        "platform": "unknown",
        "architecture": "unknown"
    }
    
    # Handle special cases first
    if folder_name in ["montecarlo_pi_estimation", "machine_learning"]:
        parsed_info["example"] = folder_name
        parsed_info["memory"] = "default"
        parsed_info["platform"] = "local"
        parsed_info["architecture"] = "unknown"
        return parsed_info
    
    # Handle standard naming convention: example_memory_platform_architecture
    # But we need to be flexible about the actual order found in the data
    if len(parts) >= 1:
        parsed_info["example"] = parts[0]
    
    if len(parts) >= 2:
        # Check if second part looks like a platform (aws/k8s/local) or memory
        if parts[1].lower() in ["aws", "k8s", "local"]:
            parsed_info["platform"] = parts[1].lower()
        else:
            parsed_info["memory"] = parts[1]
    
    if len(parts) >= 3:
        # Check if third part looks like memory, platform, or architecture
        if parts[2].lower() in ["aws", "k8s", "local"]:
            parsed_info["platform"] = parts[2].lower()
        elif parts[2].lower() in ["arm", "x86"]:
            parsed_info["architecture"] = parts[2].lower()
        elif "mb" in parts[2].lower() or parts[2].isdigit():
            parsed_info["memory"] = parts[2]
        else:
            parsed_info["memory"] = parts[2]
    
    if len(parts) >= 4:
        # Fourth part should be architecture
        if parts[3].lower() in ["arm", "x86"]:
            parsed_info["architecture"] = parts[3].lower()
        elif parts[3].lower() in ["aws", "k8s", "local"]:
            parsed_info["platform"] = parts[3].lower()
        else:
            parsed_info["architecture"] = parts[3]
    
    return parsed_info

def extract_stage_from_filename(filename):
    """
    Extract stage information from filename.
    
    Args:
        filename (str): Name of the JSON file
        
    Returns:
        str: Stage name (e.g., "stage0", "stage1", "monte_carlo_pi_stage")
    """
    # Remove .json extension
    base_name = filename.replace('.json', '')
    
    # Handle different naming patterns
    if 'stage' in base_name:
        # For files like "stage0.json", "stage1.json", "monte_carlo_pi_stage.json"
        if base_name.startswith('stage') and base_name[5:].isdigit():
            return base_name  # Returns "stage0", "stage1", etc.
        else:
            return base_name  # Returns full name like "monte_carlo_pi_stage"
    else:
        return base_name

def generate_enhanced_title(example_info, json_filename, stage):
    """
    Generate a descriptive title for the profiling entry following the specified format.
    Format: example_jsonname_stage_platform_memory_architecture
    
    Args:
        example_info (dict): Parsed folder information
        json_filename (str): Name of the JSON file
        stage (str): Stage information
        
    Returns:
        str: Generated title
    """
    json_name_clean = json_filename.replace('.json', '')
    
    # Avoid duplication - if stage is already in json_name_clean, don't repeat it
    if stage == json_name_clean:
        components = [
            example_info["example"],
            json_name_clean,
            example_info["platform"], 
            example_info["memory"],
            example_info["architecture"]
        ]
    else:
        components = [
            example_info["example"],
            json_name_clean,
            stage,
            example_info["platform"], 
            example_info["memory"],
            example_info["architecture"]
        ]
    
    # Filter out unknown values and join with underscores
    components = [comp for comp in components if comp != "unknown"]
    
    return "_".join(components)

def get_processor_tdp(cpu_type, architecture):
    """
    Get processor-specific TDP value based on CPU type and architecture.
    
    Args:
        cpu_type (str): CPU type identifier from aws_cpu field
        architecture (str): CPU architecture (arm, x86, etc.)
        
    Returns:
        int: TDP value in watts, or default multiplier for calculations
    """
    if architecture.lower() in ['x86', 'x86_64'] and cpu_type:
        # Check for specific AWS x86 processors
        for processor_name, processor_info in AWS_X86_PROCESSORS.items():
            if processor_name.lower() in cpu_type.lower():
                return processor_info["tdp_watts"]
        
        # Default x86 TDP if specific processor not found
        return TDP_VALUE_X86
    elif architecture.lower() in ['aarch64', 'arm', 'arm64']:
        return TDP_VALUE_ARM
    else:
        return TDP_VALUE

def analyze_stage_data(file_path):
    """
    Analyze stage data from a JSON file using the same logic as analyze_montecarlo_profiling.py
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        list: Analysis results for all configurations in the file
    """
    # Load the JSON data
    with open(file_path) as f:
        data = json.load(f)
    
    results = []
    
    for config, metrics in data.items():
        # Extract configuration values from tuple
        config_parts = config.strip('()').split(',')
        cpu = int(config_parts[0].strip())
        memory = int(config_parts[1].strip())
        workers = int(config_parts[2].strip())
        
        # Initialize stats with all metrics from the reference file
        stats = {
            'cpu': cpu,
            'memory': memory,
            'workers': workers,
            'total_executions': 0,
            'cost_aws_moneywise': 0
        }
        
        # Define metrics to analyze (from reference file)
        timing_metrics = [  
                            'read'
                            , 'compute'
                            , 'write'
                            , 'cold_start'
                            , 'time_consumption'
                            , 'worker_time_execution'
                        ]
        energy_metrics = [  
                            'TDP'
                            , 'perf_energy_pkg'
                            , 'perf_energy_cores'
                            , 'perf_energy_total'
                            , 'rapl_energy_pkg'
                            , 'rapl_energy_cores'
                            , 'rapl_energy_total'
                            , 'ebpf_energy_pkg'
                            , 'ebpf_energy_cores'
                            , 'ebpf_energy_total'
                            , 'ebpf_cpu_cycles'
                            , 'ebpf_energy_from_cycles'
        ]
        
        system_metrics = [
                            'psutil_cpu_percent'
                            , 'psutil_memory_percent'
                            , 'cpu_cores_physical'
                            , 'cpu_cores_logical'
        ]
        
        metadata_fields = [
                            'measurement_energy'
                            , 'perf_source'
                            , 'rapl_source'
                            , 'ebpf_source'
                            , 'cpu_name'
                            , 'cpu_architecture'
                            , 'aws_cpu'
        ]
        
        availability_fields = [
                            'perf_available'
                            , 'rapl_available'
                            , 'ebpf_available'
        ]
        
        # Initialize all metrics with default values
        all_metrics = timing_metrics + energy_metrics + system_metrics
        for metric in all_metrics:
            stats[f'avg_{metric}'] = 0
            stats[f'min_{metric}'] = 0
            stats[f'max_{metric}'] = 0
            stats[f'total_{metric}'] = 0
        
        # Initialize metadata fields with default values
        for field in metadata_fields:
            stats[field] = None
        
        # Initialize availability fields with default values
        for field in availability_fields:
            stats[field] = False
        
        # Legacy field mappings for backward compatibility
        stats['avg_rapl'] = 0  # Maps to rapl_energy_cores
        stats['avg_tdp'] = 0   # Maps to TDP
        stats['avg_execution'] = 0
        stats['min_execution'] = 0
        stats['max_execution'] = 0
        stats['total_execution'] = 0
        stats['aws_cpu_type'] = ''
        
        # Get first non-empty operation to determine execution count
        for op in metrics:
            if metrics[op] and len(metrics[op]) > 0:
                # Count number of executions (number of batches, not individual values within batches)
                total_executions = len(metrics[op])
                stats['total_executions'] = total_executions
                break
        
        # Process all operations including all new metrics
        all_operations = timing_metrics + energy_metrics + system_metrics + metadata_fields + availability_fields + ['aws_cpu']

        for op in all_operations:
            if op in metrics and metrics[op]:
                executions = metrics[op]
                
                # Flatten nested lists (some operations have multiple batches with multiple values per execution)
                flat_values = []
                for batch in executions:
                    if isinstance(batch, list):
                        flat_values.extend(batch)
                    else:
                        flat_values.append(batch)
                
                # Handle numeric metrics (timing, energy, system)
                if op in timing_metrics + energy_metrics + system_metrics:
                    numeric_values = [v for v in flat_values if isinstance(v, (int, float))]
                    
                    if numeric_values:
                        # Calculate statistics for all numeric metrics
                        avg_value = sum(numeric_values) / len(numeric_values)
                        min_value = min(numeric_values)
                        max_value = max(numeric_values)
                        total_value = avg_value * workers
                        
                        # Store values with proper naming
                        if op == 'rapl_energy_cores':
                            # Legacy mapping for rapl_energy_cores
                            stats['avg_rapl'] = avg_value
                            stats['min_rapl'] = min_value
                            stats['max_rapl'] = max_value
                            stats['total_rapl'] = total_value
                        elif op == 'TDP':
                            # Store raw TDP values for later processing
                            stats['avg_tdp_raw'] = avg_value
                            stats['min_tdp_raw'] = min_value
                            stats['max_tdp_raw'] = max_value
                        else:
                            # Standard metric processing
                            stats[f'avg_{op}'] = avg_value
                            stats[f'min_{op}'] = min_value
                            stats[f'max_{op}'] = max_value
                            stats[f'total_{op}'] = total_value
                
                # Handle metadata fields (string values)
                elif op in metadata_fields:
                    if flat_values:
                        first_value = flat_values[0] if flat_values[0] else None
                        if op == 'aws_cpu':
                            stats['aws_cpu_type'] = first_value if first_value else 'unknown'
                        else:
                            stats[op] = first_value
                
                # Handle availability fields (boolean values)
                elif op in availability_fields:
                    if flat_values:
                        # Get first boolean value
                        first_batch = flat_values[0] if isinstance(flat_values[0], list) else [flat_values[0]]
                        first_value = first_batch[0] if first_batch else False
                        stats[op] = bool(first_value)
        
        # Calculate TDP values based on CPU architecture and specific processor type
        if 'avg_tdp_raw' in stats:
            # Get processor-specific TDP value
            tdp_multiplier = get_processor_tdp(stats['aws_cpu_type'], stats['cpu_architecture'])
            
            # Apply processor-specific multiplier to convert to joules
            stats['avg_tdp'] = stats['avg_tdp_raw'] * tdp_multiplier
            stats['min_tdp'] = stats['min_tdp_raw'] * tdp_multiplier
            stats['max_tdp'] = stats['max_tdp_raw'] * tdp_multiplier
            stats['total_tdp'] = stats['avg_tdp'] * workers
            
            # Store processor information for analysis
            stats['processor_tdp_watts'] = tdp_multiplier
            stats['processor_type'] = stats['aws_cpu_type']
            
            # Clean up temporary raw values
            del stats['avg_tdp_raw']
            del stats['min_tdp_raw'] 
            del stats['max_tdp_raw']
        
        # Calculate execution time (sum of read, compute, write)
        if stats['avg_read'] > 0 or stats['avg_compute'] > 0 or stats['avg_write'] > 0:
            stats['avg_execution'] = stats['avg_read'] + stats['avg_compute'] + stats['avg_write']
            stats['min_execution'] = min(stats['avg_read'], stats['avg_compute'], stats['avg_write'])
            stats['max_execution'] = max(stats['avg_read'], stats['avg_compute'], stats['avg_write'])
            stats['total_execution'] = stats['avg_execution'] * workers
        
        # Calculate AWS cost based on architecture (using real AWS Lambda pricing)
        if 'aarch64' in stats['cpu_architecture'].lower() or 'arm' in stats['cpu_architecture'].lower():
            # ARM pricing: $0.0000133334 per GB-second
            price_per_gb_second = PRICE_AWS_ARM
        elif 'x86' in stats['cpu_architecture'].lower():
            # x86 pricing: $0.0000166667 per GB-second
            price_per_gb_second = PRICE_AWS_X86
        else:
            price_per_gb_second = 0
        
        # Calculate cost: avg_compute_time * workers * memory_gb * price_per_gb_second
        memory_gb = stats['memory'] / 1024.0  # Convert MB to GB
        cost_usd = stats['avg_compute'] * workers * memory_gb * price_per_gb_second
        # Convert to dollars and multiply by 1000 for better readability (cost per 1000 executions)
        stats['cost_aws_moneywise'] = cost_usd * 1000
        
        results.append(stats)
    
    # Sort by number of workers
    results.sort(key=lambda x: x['workers'])
    
    return results

def save_analysis_json(results, output_path, metadata):
    """Save analysis results as JSON file with metadata."""
    # Extract processor information from results for metadata
    processor_info = {}
    if results:
        for result in results:
            if 'processor_type' in result and result['processor_type']:
                processor_type = result['processor_type']
                if processor_type in AWS_X86_PROCESSORS:
                    processor_info = {
                        "detected_processor": processor_type,
                        "tdp_watts": AWS_X86_PROCESSORS[processor_type]["tdp_watts"],
                        "description": AWS_X86_PROCESSORS[processor_type]["description"]
                    }
                break
    
    analysis_data = {
        "metadata": {
            "description": "Enhanced profiling analysis results with processor-specific TDP calculations",
            # "generated_at": datetime.now().isoformat(),
            "source_file": metadata["source_file"],
            "title": metadata["title"],
            "example": metadata["example"],
            "stage": metadata["stage"],
            "memory": metadata["memory"],
            "platform": metadata["platform"],
            "architecture": metadata["architecture"],
            "total_configurations": len(results),
            "aws_x86_processors": AWS_X86_PROCESSORS,
            "processor_info": processor_info if processor_info else None
        },
        "analysis_results": results
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"✓ Analysis saved to: {output_path}")

def process_all_profiling_data():
    """
    Process all ML, Monte Carlo Pi, Video, and Titanic profiling data and generate analysis results.
    """
    print("Starting enhanced profiling data analysis...")
    print(f"Scanning directories: {PROFILING_DIRECTORIES}")
    print("Title format: example_jsonname_stage_platform_memory_architecture")
    print("\nAWS x86 Processor TDP Configuration:")
    for processor, info in AWS_X86_PROCESSORS.items():
        print(f"  - {processor}: {info['tdp_watts']}W TDP ({info['description']})")
    print()
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    processed_files = 0
    
    for base_dir in PROFILING_DIRECTORIES:
        # Convert relative path to absolute path
        abs_base_dir = os.path.join(script_dir, base_dir)
        
        if not os.path.exists(abs_base_dir):
            print(f"Directory not found: {abs_base_dir}")
            continue
            
        print(f"\nScanning directory: {abs_base_dir}")
        
        # Find all JSON files recursively
        json_files = glob.glob(os.path.join(abs_base_dir, "**/*.json"), recursive=True)
        
        for json_file in json_files:
            print(f"Processing: {json_file}")
            
            try:
                # Extract path components
                path_parts = Path(json_file).parts
                json_filename = Path(json_file).name
                
                # Find the folder containing the JSON file (last folder before the file)
                folder_name = path_parts[-2] if len(path_parts) > 1 else "unknown"
                
                # Parse folder name for metadata using enhanced parsing
                example_info = parse_folder_name_enhanced(folder_name)
                
                # Extract stage from filename
                stage = extract_stage_from_filename(json_filename)
                
                # Generate enhanced title
                title = generate_enhanced_title(example_info, json_filename, stage)
                
                # Analyze the profiling data
                analysis_results = analyze_stage_data(json_file)
                
                # Create output directory and filename
                output_dir = os.path.join(script_dir, "001_analysis_results")
                output_filename = f"{title}_analysis.json"
                output_path = os.path.join(output_dir, output_filename)
                
                # Prepare metadata
                metadata = {
                    "source_file": json_file,
                    "title": title,
                    "example": example_info["example"],
                    "stage": stage,
                    "memory": example_info["memory"],
                    "platform": example_info["platform"],
                    "architecture": example_info["architecture"]
                }
                
                # Save analysis results
                save_analysis_json(analysis_results, output_path, metadata)
                processed_files += 1
                
            except Exception as e:
                print(f"✗ Error processing {json_file}: {e}")
                continue
    
    print(f"\n✓ Analysis complete! Processed {processed_files} files.")
    print(f"✓ Results saved in: {os.path.join(script_dir, '001_analysis_results')}")

def main():
    """Main function."""
    process_all_profiling_data()

if __name__ == "__main__":
    main()

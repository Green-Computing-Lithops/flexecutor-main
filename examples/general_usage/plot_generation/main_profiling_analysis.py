#!/usr/bin/env python3
"""
Complete Profiling Analysis Workflow with Table Extraction

Runs the complete profiling analysis workflow and generates summary tables:
1. Collects and consolidates profiling data
2. Analyzes profiling data with enhanced metrics  
3. Generates visualization plots
4. Extracts and displays analysis results in table format

Usage: python main_profiling_analysis.py
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Import the expanded execution summary function
try:
    from minimum_execution_summary_generator import generate_expanded_execution_summary
except ImportError:
    print("⚠️  Warning: Could not import expanded execution summary generator")
    generate_expanded_execution_summary = None

# GENERATE_PLOTS = True
GENERATE_PLOTS = False

def run_script(script_name, description):
    """Run a Python script and return success status."""
    print(f"\n🚀 {description}")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.stdout:
            print("📊 Output:", result.stdout.strip())
        if result.stderr:
            print("⚠️  Warnings:", result.stderr.strip())
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed (code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_plot_generation():
    """Generate visualization plots from analysis results."""
    print(f"\n🎨 Generating plots")
    
    analysis_folder = "analysis_results"
    if not os.path.exists(analysis_folder):
        print(f"❌ Analysis folder '{analysis_folder}' not found")
        return False
    
    success_count = 0
    
    # Combined plots
    try:
        result = subprocess.run([
            sys.executable, "generate_combined_plots.py", 
            analysis_folder, "--output", "combined_plots_output"
        ], capture_output=True, text=True, 
           cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("✅ Combined plots generated")
            success_count += 1
        else:
            print("❌ Combined plots failed")
    except Exception as e:
        print(f"❌ Combined plots error: {e}")
    
    # Min/Max plots
    try:
        result = subprocess.run([
            sys.executable, "generate_plot_min_max.py", 
            analysis_folder, "--output", "min_max_plots_output"
        ], capture_output=True, text=True, 
           cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("✅ Min/Max plots generated")
            success_count += 1
        else:
            print("❌ Min/Max plots failed")
    except Exception as e:
        print(f"❌ Min/Max plots error: {e}")
    
    return success_count > 0

def extract_analysis_data(json_file_path):
    """Extract memory, workers, and total_executions from JSON analysis file."""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        if 'profiling_data' in data:
            # Enhanced profiling analysis format
            extracted_data = []
            for entry in data['profiling_data']:
                memory_str = entry.get('memory', 'NA')
                if isinstance(memory_str, str) and memory_str.endswith('Mb'):
                    memory = int(memory_str[:-2])
                else:
                    memory = memory_str
                
                config = entry.get('configuration', '')
                if config and config.startswith('(') and config.endswith(')'):
                    config_parts = config[1:-1].split(', ')
                    workers = int(config_parts[2]) if len(config_parts) >= 3 else 'NA'
                else:
                    workers = 'NA'
                
                total_executions = 'NA'
                if 'profiling_metrics' in entry:
                    metrics = entry['profiling_metrics']
                    for metric_key in ['read', 'compute', 'write']:
                        if metric_key in metrics and metrics[metric_key]:
                            total_executions = len(metrics[metric_key])
                            break
                
                extracted_data.append({
                    'title': entry.get('title', 'NA'),
                    'memory': memory,
                    'workers': workers,
                    'total_executions': total_executions
                })
            return extracted_data
        
        elif 'analysis_results' in data:
            # Regular analysis format
            extracted_data = []
            for result in data['analysis_results']:
                extracted_data.append({
                    'memory': result.get('memory', 'NA'),
                    'workers': result.get('workers', 'NA'),
                    'total_executions': result.get('total_executions', 'NA')
                })
            return extracted_data
        
        else:
            return [{'error': 'NA JSON structure'}]
            
    except Exception as e:
        return [{'error': f'Error reading file: {str(e)}'}]

def cleanup_all_output_directories():

    # Define all target directories that need complete cleanup
    target_directories = [
        "analysis_results",
        "architecture_analysis_output", 
        "combined_plots_output",
        "min_max_plots_output"
    ]
    
    total_removed_files = 0
    total_removed_dirs = 0
    
    for dir_name in target_directories:
        dir_path = Path(dir_name)
        
        print(f"\n📁 Processing directory: {dir_name}")
        
        if not dir_path.exists():
            print(f"   📂 Directory doesn't exist, creating it...")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created {dir_name} directory")
            continue
        
        # Count existing contents before cleanup
        all_files = list(dir_path.rglob("*"))
        files_count = len([f for f in all_files if f.is_file()])
        dirs_count = len([f for f in all_files if f.is_dir()])
        
        if files_count == 0 and dirs_count == 0:
            print(f"   ✅ Directory is already empty")
            continue
        
        print(f"   📊 Found {files_count} files and {dirs_count} subdirectories")
        
        # Remove all contents completely
        removed_files = 0
        removed_dirs = 0
        
        try:
            # Remove all files and subdirectories
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()
                    removed_files += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    removed_dirs += 1
            
            total_removed_files += removed_files
            total_removed_dirs += removed_dirs
            
            print(f"   ✅ Cleaned {dir_name}: removed {removed_files} files and {removed_dirs} subdirectories")
            
        except Exception as e:
            print(f"   ⚠️  Error cleaning {dir_name}: {e}")
            return False
    
    print(f"\n🎯 CLEANUP SUMMARY:")
    print(f"   📁 Directories processed: {len(target_directories)}")
    print(f"   🗑️  Total files removed: {total_removed_files}")
    print(f"   📂 Total subdirectories removed: {total_removed_dirs}")
    print(f"   ✅ All output directories are now completely clean")
    
    return True

def simplify_title(title):
    """Simplify execution titles by removing redundant parts."""
    # Remove redundant "monte_carlo_pi_" prefix
    title = title.replace("monte_carlo_pi_stage", "stage")
    
    # Handle specific patterns
    if "pi_monte_carlo_pi_stage_v2" in title:
        title = title.replace("pi_monte_carlo_pi_stage_v2", "pi_stage_v2")
    elif "pi_monte_carlo_pi_stage" in title:
        title = title.replace("pi_monte_carlo_pi_stage", "pi_stage")
    elif "montecarlo_pi_estimation_monte_carlo_pi_stage" in title:
        title = title.replace("montecarlo_pi_estimation_monte_carlo_pi_stage", "montecarlo_pi_estimation_stage")
    
    return title

def parse_filename_structure(filename):
    """
    Parse filename structure: example_file_title_backend_memory_architecture
    Returns dict with parsed components or error information.
    
    Rules:
    - Split by '_'
    - First part: example (video, titanic, pi, ml)
    - Second part: file_title (stage3, etc.)
    - Third part: backend (aws, k8s, or NA if not these values)
    - Fourth part: memory (512Mb, 1024Mb, etc.)
    - Fifth part: architecture (arm, x86)
    - If any field from backend onwards is undefined, should be shown as error in table
    """
    parts = filename.split('_')
    
    if len(parts) < 2:
        return {'error': 'Invalid filename structure - too few parts'}
    
    result = {
        'example': parts[0] if len(parts) > 0 else 'NA',
        'file_title': parts[1] if len(parts) > 1 else 'NA',
        'backend': 'NA',
        'memory': 'NA', 
        'architecture': 'NA',
        'error': None
    }
    
    # Check if we have the full structure (at least 5 parts)
    if len(parts) >= 5:
        # Full structure: example_file_title_backend_memory_architecture
        potential_backend = parts[2]
        potential_memory = parts[3]
        potential_architecture = parts[4]
        
        # Validate backend - must be aws or k8s, otherwise NA
        if potential_backend.lower() in ['aws', 'k8s']:
            result['backend'] = potential_backend.lower()
        else:
            result['backend'] = 'NA'
            
        # Memory field - keep as is
        result['memory'] = potential_memory
        
        # Validate architecture - must be arm or x86, otherwise NA
        if potential_architecture.lower() in ['arm', 'x86']:
            result['architecture'] = potential_architecture.lower()
        else:
            result['architecture'] = 'NA'
            
    elif len(parts) >= 3:
        # Partial structure - try to identify what we have
        remaining_parts = parts[2:]
        
        # Look for known patterns in remaining parts
        for part in remaining_parts:
            part_lower = part.lower()
            
            # Check for backend
            if part_lower in ['aws', 'k8s'] and result['backend'] == 'NA':
                result['backend'] = part_lower
            # Check for memory (contains 'mb' or is numeric)
            elif ('mb' in part_lower or part.isdigit()) and result['memory'] == 'NA':
                result['memory'] = part
            # Check for architecture
            elif part_lower in ['arm', 'x86'] and result['architecture'] == 'NA':
                result['architecture'] = part_lower
        
        # If we have 3+ parts but missing critical fields, it's an error
        # unless it's a processing file (special case)
        if 'processing' not in filename.lower():
            if result['backend'] == 'NA' or result['memory'] == 'NA' or result['architecture'] == 'NA':
                result['error'] = 'Missing required fields (backend, memory, or architecture)'
    
    # Special handling for processing files - they can have NA values without error
    if 'processing' in filename.lower():
        # Processing files are allowed to have NA values
        result['error'] = None
    
    return result

def extract_architecture_from_title(title):
    """Extract architecture from title or filename using structured parsing."""
    parsed = parse_filename_structure(title)
    
    if parsed['error']:
        return "ERROR"
    
    # Return the parsed architecture, converting to standard format
    arch = parsed['architecture'].upper() if parsed['architecture'] != 'NA' else 'NA'
    if arch == 'ARM':
        return 'ARM'
    elif arch == 'X86':
        return 'x86'
    else:
        return 'NA'

def extract_memory_from_title(title):
    """Extract memory from title or filename using structured parsing."""
    parsed = parse_filename_structure(title)
    
    if parsed['error']:
        return 'ERROR'
    
    memory = parsed['memory']
    if memory == 'NA':
        return 'NA'
    
    # Extract numeric value from memory string like "512Mb"
    import re
    memory_match = re.search(r'(\d+)', memory)
    if memory_match:
        return int(memory_match.group(1))
    
    return memory

def extract_example_from_title(title):
    """Extract example name from title or filename using structured parsing."""
    parsed = parse_filename_structure(title)
    
    if parsed['error']:
        return 'ERROR'
    
    return parsed['example']

def generate_analysis_tables():
    """Generate consolidated summary table from analysis results."""
    print(f"\n📋 Generating Analysis Tables")
    
    # Use the correct path relative to the script location
    script_dir = Path(__file__).parent
    analysis_dir = script_dir / "analysis_results"
    
    if not analysis_dir.exists():
        print(f"❌ Analysis directory not found at {analysis_dir}")
        return False
    
    json_files = sorted(list(analysis_dir.glob("*.json")))
    if not json_files:
        print("❌ No JSON files found in analysis_results")
        return False
    
    print("\n# Analysis Results Summary")
    print("Consolidated table with all analysis results\n")
    
    # Collect all data first for proper formatting
    table_data = []
    
    # Process all files and collect data
    for json_file in json_files:
        file_name = os.path.basename(json_file).replace('_analysis.json', '').replace('.json', '')
        data = extract_analysis_data(json_file)
        
        if not data or (len(data) == 1 and 'error' in data[0]):
            table_data.append([file_name, "Error", "Error", "Error", "Error"])
            continue
        
        # For enhanced_profiling_analysis.json, use the individual titles
        if 'title' in data[0]:
            for item in data:
                title = item.get('title', 'NA')
                # Apply title simplification
                simplified_title = simplify_title(title)
                architecture = extract_architecture_from_title(simplified_title)
                memory = item.get('memory', 'NA')
                workers = item.get('workers', 'NA')
                total_executions = item.get('total_executions', 'NA')
                
                # Use parsed memory if available
                parsed_memory = extract_memory_from_title(simplified_title)
                if parsed_memory != 'NA' and parsed_memory != 'ERROR':
                    memory = parsed_memory
                
                table_data.append([simplified_title, architecture, str(memory), str(workers), str(total_executions)])
        else:
            # For regular analysis files, use filename as title and show each configuration
            for item in data:
                memory = item.get('memory', 'NA')
                workers = item.get('workers', 'NA')
                total_executions = item.get('total_executions', 'NA')
                # Apply title simplification to filename too
                simplified_file_name = simplify_title(file_name)
                architecture = extract_architecture_from_title(simplified_file_name)
                
                # Use parsed memory if available
                parsed_memory = extract_memory_from_title(simplified_file_name)
                if parsed_memory != 'NA' and parsed_memory != 'ERROR':
                    memory = parsed_memory
                elif memory == 0 and ('Mb' in file_name or 'mb' in file_name.lower()):
                    # Extract memory from filename like "titanic_stage_aws_2048Mb_arm"
                    import re
                    memory_match = re.search(r'(\d+)[Mm]b', file_name)
                    if memory_match:
                        memory = int(memory_match.group(1))
                
                table_data.append([simplified_file_name, architecture, str(memory), str(workers), str(total_executions)])
    
    # Calculate column widths for proper formatting
    if table_data:
        col_widths = [
            max(len("Execution Title"), max(len(row[0]) for row in table_data)),
            max(len("Arch"), max(len(row[1]) for row in table_data)),
            max(len("Memory"), max(len(row[2]) for row in table_data)),
            max(len("Workers"), max(len(row[3]) for row in table_data)),
            max(len("Total Ex"), max(len(row[4]) for row in table_data))
        ]
        
        # Print formatted table header
        header = f"| {'Execution Title':<{col_widths[0]}} | {'Arch':<{col_widths[1]}} | {'Memory':<{col_widths[2]}} | {'Workers':<{col_widths[3]}} | {'Total Ex':<{col_widths[4]}} |"
        separator = f"|{'-' * (col_widths[0] + 2)}|{'-' * (col_widths[1] + 2)}|{'-' * (col_widths[2] + 2)}|{'-' * (col_widths[3] + 2)}|{'-' * (col_widths[4] + 2)}|"
        
        print(header)
        print(separator)
        
        # Print formatted table rows
        for row in table_data:
            formatted_row = f"| {row[0]:<{col_widths[0]}} | {row[1]:<{col_widths[1]}} | {row[2]:<{col_widths[2]}} | {row[3]:<{col_widths[3]}} | {row[4]:<{col_widths[4]}} |"
            print(formatted_row)
    
    print(f"\n📊 Total configurations analyzed: {len(table_data)}")
    return True

def generate_min_execution_summary():
    """Generate minimum execution summary table by example and architecture/memory."""
    print(f"\n📊 Generating Minimum Execution Summary Table")
    
    # Use the correct path relative to the script location
    script_dir = Path(__file__).parent
    analysis_dir = script_dir / "analysis_results"
    
    if not analysis_dir.exists():
        print(f"❌ Analysis directory not found at {analysis_dir}")
        return False
    
    json_files = sorted(list(analysis_dir.glob("*.json")))
    if not json_files:
        print("❌ No JSON files found in analysis_results")
        return False
    
    # Data structure to store min executions: {arch_memory: {example: min_executions}}
    summary_data = {}
    detailed_info = {}
    
    # Process all files and collect data
    for json_file in json_files:
        file_name = os.path.basename(json_file).replace('_analysis.json', '').replace('.json', '')
        data = extract_analysis_data(json_file)
        
        if not data or (len(data) == 1 and 'error' in data[0]):
            continue
        
        # For enhanced_profiling_analysis.json, use the individual titles
        if 'title' in data[0]:
            for item in data:
                title = item.get('title', 'NA')
                simplified_title = simplify_title(title)
                memory = item.get('memory', 'NA')
                total_executions = item.get('total_executions', 'NA')
                workers = item.get('workers', 'NA')
                
                # Skip if we don't have valid data
                if memory == 'NA' or total_executions == 'NA':
                    continue
                
                # Use new parsing logic
                example = extract_example_from_title(simplified_title)
                architecture = extract_architecture_from_title(simplified_title)
                parsed_memory = extract_memory_from_title(simplified_title)
                
                # Use parsed memory if available, otherwise use item memory
                if parsed_memory != 'NA' and parsed_memory != 'ERROR':
                    memory = parsed_memory
                
                # Skip if parsing failed
                if example == 'ERROR' or architecture == 'ERROR':
                    continue
                
                # Skip unknown examples or architectures
                if example not in ['titanic', 'pi', 'ml', 'video'] or architecture == 'unknown':
                    continue
                
                # Create key for architecture and memory
                arch_memory_key = f"{architecture} {memory}"
                detail_key = f"{arch_memory_key}_{example}"
                
                if arch_memory_key not in summary_data:
                    summary_data[arch_memory_key] = {}
                
                if example not in summary_data[arch_memory_key]:
                    summary_data[arch_memory_key][example] = total_executions
                    detailed_info[detail_key] = {
                        'min_executions': total_executions,
                        'min_workers': workers,
                        'filename': file_name,
                        'title': simplified_title
                    }
                else:
                    # Keep minimum execution count
                    if total_executions < summary_data[arch_memory_key][example]:
                        summary_data[arch_memory_key][example] = total_executions
                        detailed_info[detail_key] = {
                            'min_executions': total_executions,
                            'min_workers': workers,
                            'filename': file_name,
                            'title': simplified_title
                        }
                    elif total_executions == summary_data[arch_memory_key][example] and workers < detailed_info[detail_key]['min_workers']:
                        detailed_info[detail_key]['min_workers'] = workers
        else:
            # For regular analysis files, use filename to determine example and process each configuration
            for item in data:
                memory = item.get('memory', 'NA')
                total_executions = item.get('total_executions', 'NA')
                workers = item.get('workers', 'NA')
                
                # Skip if we don't have valid data
                if memory == 'NA' or total_executions == 'NA':
                    continue
                
                # Use new parsing logic
                example = extract_example_from_title(file_name)
                architecture = extract_architecture_from_title(file_name)
                parsed_memory = extract_memory_from_title(file_name)
                
                # Use parsed memory if available, otherwise use item memory
                actual_memory = memory
                if parsed_memory != 'NA' and parsed_memory != 'ERROR':
                    actual_memory = parsed_memory
                elif memory == 0 and ('Mb' in file_name or 'mb' in file_name.lower()):
                    # Extract memory from filename like "titanic_stage_aws_2048Mb_arm"
                    import re
                    memory_match = re.search(r'(\d+)[Mm]b', file_name)
                    if memory_match:
                        actual_memory = int(memory_match.group(1))
                
                # Skip if parsing failed
                if example == 'ERROR' or architecture == 'ERROR':
                    continue
                
                # Skip unknown examples or architectures
                if example not in ['titanic', 'pi', 'ml', 'video'] or architecture == 'unknown':
                    continue
                
                # Handle memory value conversion
                if actual_memory == 0 or actual_memory == 'default':
                    memory_key = "default"
                else:
                    memory_key = str(actual_memory)
                
                # Create key for architecture and memory
                arch_memory_key = f"{architecture} {memory_key}"
                detail_key = f"{arch_memory_key}_{example}"
                
                if arch_memory_key not in summary_data:
                    summary_data[arch_memory_key] = {}
                
                if example not in summary_data[arch_memory_key]:
                    summary_data[arch_memory_key][example] = total_executions
                    detailed_info[detail_key] = {
                        'min_executions': total_executions,
                        'min_workers': workers,
                        'filename': file_name,
                        'title': file_name
                    }
                else:
                    # Keep minimum execution count
                    if total_executions < summary_data[arch_memory_key][example]:
                        summary_data[arch_memory_key][example] = total_executions
                        detailed_info[detail_key] = {
                            'min_executions': total_executions,
                            'min_workers': workers,
                            'filename': file_name,
                            'title': file_name
                        }
                    elif total_executions == summary_data[arch_memory_key][example] and workers < detailed_info[detail_key]['min_workers']:
                        detailed_info[detail_key]['min_workers'] = workers
    
    # Generate the table
    print("\n# Minimum Execution Summary")
    print("Minimum number of executions for each example by architecture and memory\n")
    
    # Define the examples in order
    examples = ['titanic', 'pi', 'ml', 'video']
    
    # Sort architecture/memory combinations
    # Custom sorting to put NA at the end and handle numeric memory values
    def sort_key(key):
        parts = key.split()
        arch = parts[0]
        memory = parts[1]
        
        # Sort order: ARM first, then x86, then NA
        arch_order = {'ARM': 0, 'x86': 1, 'NA': 2}
        arch_priority = arch_order.get(arch, 3)
        
        # Handle memory sorting
        if memory.isdigit():
            memory_value = int(memory)
        else:
            memory_value = 9999  # Put non-numeric at end
            
        return (arch_priority, memory_value)
    
    arch_memory_keys = sorted(summary_data.keys(), key=sort_key)
    
    if not arch_memory_keys:
        print("❌ No valid data found for summary table")
        return False
    
    # Calculate column widths
    col_widths = [max(12, max(len(key) for key in arch_memory_keys))]  # First column
    for example in examples:
        col_widths.append(max(len(example), 8))  # Example columns
    
    # Print table header
    header_parts = [f"{'':^{col_widths[0]}}"]
    for i, example in enumerate(examples):
        header_parts.append(f"{example:^{col_widths[i+1]}}")
    
    print("|" + "|".join(header_parts) + "|")
    
    # Print separator
    separator_parts = ["-" * col_widths[0]]
    for i in range(len(examples)):
        separator_parts.append("-" * col_widths[i+1])
    print("|" + "|".join(separator_parts) + "|")
    
    # Print data rows
    for arch_memory in arch_memory_keys:
        row_parts = [f"{arch_memory:^{col_widths[0]}}"]
        
        for i, example in enumerate(examples):
            value = summary_data[arch_memory].get(example, "")
            row_parts.append(f"{str(value):^{col_widths[i+1]}}")
        
        print("|" + "|".join(row_parts) + "|")
    
    print(f"\n📊 Summary table generated with {len(arch_memory_keys)} configurations")
    
    # Print detailed information about minimum execution configurations
    print(f"\n# Detailed Minimum Execution Information")
    print("Details about the configurations that achieved minimum executions\n")
    
    for arch_memory in arch_memory_keys:
        print(f"## {arch_memory}")
        for example in examples:
            if example in summary_data[arch_memory]:
                detail_key = f"{arch_memory}_{example}"
                if detail_key in detailed_info:
                    info = detailed_info[detail_key]
                    print(f"  • {example}: {info['min_executions']} executions, {info['min_workers']} workers")
                    print(f"    └─ File: {info['filename']}")
                    if info['title'] != info['filename']:
                        print(f"    └─ Title: {info['title']}")
        print()
    
    return True

def main():
    """Main workflow execution."""
    print("="*60)
    print(" COMPLETE PROFILING ANALYSIS WORKFLOW")
    print("="*60)
    
    start_time = datetime.now()
    
    # Stage 0: Cleanup
    print("\n🧹 STAGE 0: CLEANUP")
    cleanup_success = cleanup_all_output_directories()
    
    if not cleanup_success:
        print("\n❌ Workflow stopped - cleanup failed")
        return False
    
    # Stage 1: Data Collection
    print("\n📊 STAGE 1: DATA COLLECTION")
    collection_success = run_script(
        "collect_profiling_data_enhanced.py",
        "Collecting profiling data"
    )
    
    if not collection_success:
        print("\n❌ Workflow stopped - data collection failed")
        return False
    
    # Stage 2: Data Analysis  
    print("\n🔬 STAGE 2: DATA ANALYSIS")
    analysis_success = run_script(
        "analyze_all_profiling_enhanced.py", 
        "Analyzing profiling data"
    )
    
    if not analysis_success:
        print("\n❌ Data analysis failed")
        return False
    
    # Stage 3: Plot Generation (optional)
    plot_success = False
    if GENERATE_PLOTS:
        print("\n🎨 STAGE 3: PLOT GENERATION")
        plot_success = run_plot_generation()
    
    # Stage 4: Table Generation
    print("\n📋 STAGE 4: TABLE GENERATION")
    table_success = generate_analysis_tables()
    
    # Stage 5: Minimum Execution Summary
    print("\n📊 STAGE 5: MINIMUM EXECUTION SUMMARY")
    summary_success = generate_min_execution_summary()
    
    # Stage 6: Expanded Execution Summary with Costs
    print("\n📊 STAGE 6: EXPANDED EXECUTION SUMMARY WITH COSTS")
    expanded_summary_success = False
    if generate_expanded_execution_summary:
        try:
            expanded_summary_success = generate_expanded_execution_summary()
        except Exception as e:
            print(f"❌ Expanded execution summary failed: {e}")
            expanded_summary_success = False
    else:
        print("⚠️  Expanded execution summary generator not available")
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print(f" WORKFLOW COMPLETED")
    print(f"{'='*60}")
    print(f"⏱️  Duration: {duration}")
    print(f"📁 Results saved to:")
    print(f"   • analysis_results/ - Analysis data")
    if plot_success:
        print(f"   • combined_plots_output/ - Combined plots")
        print(f"   • min_max_plots_output/ - Min/Max plots")
    if summary_success:
        print(f"   • Minimum execution summary table generated")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

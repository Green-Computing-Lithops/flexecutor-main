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
                memory_str = entry.get('memory', 'Unknown')
                if isinstance(memory_str, str) and memory_str.endswith('Mb'):
                    memory = int(memory_str[:-2])
                else:
                    memory = memory_str
                
                config = entry.get('configuration', '')
                if config and config.startswith('(') and config.endswith(')'):
                    config_parts = config[1:-1].split(', ')
                    workers = int(config_parts[2]) if len(config_parts) >= 3 else 'Unknown'
                else:
                    workers = 'Unknown'
                
                total_executions = 'Unknown'
                if 'profiling_metrics' in entry:
                    metrics = entry['profiling_metrics']
                    for metric_key in ['read', 'compute', 'write']:
                        if metric_key in metrics and metrics[metric_key]:
                            total_executions = len(metrics[metric_key])
                            break
                
                extracted_data.append({
                    'title': entry.get('title', 'Unknown'),
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
                    'memory': result.get('memory', 'Unknown'),
                    'workers': result.get('workers', 'Unknown'),
                    'total_executions': result.get('total_executions', 'Unknown')
                })
            return extracted_data
        
        else:
            return [{'error': 'Unknown JSON structure'}]
            
    except Exception as e:
        return [{'error': f'Error reading file: {str(e)}'}]

def cleanup_analysis_results():
    """Clean up analysis_results folder by removing all JSON files."""
    print(f"\n🧹 Cleaning Analysis Results Folder")
    
    analysis_dir = Path("analysis_results")
    
    if not analysis_dir.exists():
        print(f"📁 Analysis directory doesn't exist, creating it...")
        analysis_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created analysis_results directory")
        return True
    
    # Find all JSON files in the directory
    json_files = list(analysis_dir.glob("*.json"))
    
    if not json_files:
        print(f"✅ Analysis directory is already clean (no JSON files found)")
        return True
    
    # Remove all JSON files
    removed_count = 0
    for json_file in json_files:
        try:
            json_file.unlink()
            removed_count += 1
        except Exception as e:
            print(f"⚠️  Failed to remove {json_file.name}: {e}")
    
    print(f"✅ Cleaned analysis_results folder: removed {removed_count} JSON files")
    return True

def generate_analysis_tables():
    """Generate consolidated summary table from analysis results."""
    print(f"\n📋 Generating Analysis Tables")
    
    analysis_dir = Path("analysis_results")
    if not analysis_dir.exists():
        print(f"❌ Analysis directory not found")
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
            table_data.append([file_name, "Error", "Error", "Error"])
            continue
        
        # For enhanced_profiling_analysis.json, use the individual titles
        if 'title' in data[0]:
            for item in data:
                title = item.get('title', 'Unknown')
                memory = item.get('memory', 'Unknown')
                workers = item.get('workers', 'Unknown')
                total_executions = item.get('total_executions', 'Unknown')
                table_data.append([title, str(memory), str(workers), str(total_executions)])
        else:
            # For regular analysis files, use filename as title and show each configuration
            for item in data:
                memory = item.get('memory', 'Unknown')
                workers = item.get('workers', 'Unknown')
                total_executions = item.get('total_executions', 'Unknown')
                table_data.append([file_name, str(memory), str(workers), str(total_executions)])
    
    # Calculate column widths for proper alignment
    if table_data:
        col_widths = [
            max(len("Execution Title"), max(len(row[0]) for row in table_data)),
            max(len("Memory"), max(len(row[1]) for row in table_data)),
            max(len("Workers"), max(len(row[2]) for row in table_data)),
            max(len("Total Executions"), max(len(row[3]) for row in table_data))
        ]
        
        # Print formatted table header
        header = f"| {'Execution Title':<{col_widths[0]}} | {'Memory':<{col_widths[1]}} | {'Workers':<{col_widths[2]}} | {'Total Executions':<{col_widths[3]}} |"
        separator = f"|{'-' * (col_widths[0] + 2)}|{'-' * (col_widths[1] + 2)}|{'-' * (col_widths[2] + 2)}|{'-' * (col_widths[3] + 2)}|"
        
        print(header)
        print(separator)
        
        # Print formatted table rows
        for row in table_data:
            formatted_row = f"| {row[0]:<{col_widths[0]}} | {row[1]:<{col_widths[1]}} | {row[2]:<{col_widths[2]}} | {row[3]:<{col_widths[3]}} |"
            print(formatted_row)
    
    print(f"\n📊 Total configurations analyzed: {len(table_data)}")
    return True

def main():
    """Main workflow execution."""
    print("="*60)
    print(" COMPLETE PROFILING ANALYSIS WORKFLOW")
    print("="*60)
    
    start_time = datetime.now()
    
    # Stage 0: Cleanup
    print("\n🧹 STAGE 0: CLEANUP")
    cleanup_success = cleanup_analysis_results()
    
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
    
    # Stage 3: Plot Generation
    print("\n🎨 STAGE 3: PLOT GENERATION")
    plot_success = run_plot_generation()
    
    # Stage 4: Table Generation
    print("\n📋 STAGE 4: TABLE GENERATION")
    table_success = generate_analysis_tables()
    
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
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

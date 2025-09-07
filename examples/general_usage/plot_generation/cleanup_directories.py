#!/usr/bin/env python3
"""
Directory Cleanup Utility for Plot Generation
==============================================

This module provides functionality to clean up output directories
for the plot generation and profiling analysis pipeline.

Author: Energy Analysis Suite
Date: 2025
"""

import shutil
from pathlib import Path


def cleanup_output_directories(script_dir=None, output_directories=None):
    """
    Clean up all output directories before running the pipeline.
    
    Args:
        script_dir (Path, optional): Directory containing the scripts. 
                                   If None, uses current file's parent.
        output_directories (list, optional): List of directory names to clean.
                                           If None, uses default directories.
    
    Returns:
        dict: Summary of cleanup results with 'cleaned' and 'skipped' lists
    """
    if script_dir is None:
        script_dir = Path(__file__).parent
    
    if output_directories is None:
        output_directories = [
            "001_analysis_results",
            "002_collect_profiling_data_enhanced",
            "003_comprehensive_analysis",
            "004_cost_time_energy_scatter_plots",
            "005_cpu_candlestick_analysis",
            "006_extract_analysis_tables",
            "007_generate_combined_plots",
            "007A_hypotesis_1",
            "007B_hypotesis_2",
            "007C_hypotesis_3",
            "008_generate_hypothesis_5_memory",
            "009_simple_analysis",
            "010_generate_plot_min_max",
            "011_grouped_memory_2048",
            "013_minimum_execution_summary_generator",
            "014_multistage_stacked_graphs_csv",
            "015_x86_vs_arm_architecture_analysis"
        ]
    
    print("🧹 CLEANING OUTPUT DIRECTORIES")
    print("-" * 80)
    
    processed_dirs = []
    skipped_dirs = []
    total_removed_files = 0
    total_removed_dirs = 0
    
    for dir_name in output_directories:
        dir_path = script_dir / dir_name
        
        print(f"\n📁 Processing directory: {dir_name}")
        
        if not dir_path.exists():
            try:
                # Create the directory if it doesn't exist
                dir_path.mkdir(parents=True, exist_ok=True)
                processed_dirs.append(dir_name)
                print(f"   📂 Created: {dir_name}/")
            except Exception as e:
                print(f"   ⚠️  Failed to create {dir_name}/: {e}")
                skipped_dirs.append(dir_name)
            continue
        
        if dir_path.is_dir():
            try:
                # Count existing contents before cleanup
                all_files = list(dir_path.rglob("*"))
                files_count = len([f for f in all_files if f.is_file()])
                dirs_count = len([f for f in all_files if f.is_dir()])
                
                if files_count == 0 and dirs_count == 0:
                    print(f"   ✅ Directory is already empty")
                    processed_dirs.append(dir_name)
                    continue
                
                print(f"   📊 Found {files_count} files and {dirs_count} subdirectories")
                
                # Remove only the contents of the directory, not the directory itself
                removed_files = 0
                removed_dirs = 0
                
                for item in dir_path.iterdir():
                    if item.is_file():
                        item.unlink()
                        removed_files += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        removed_dirs += 1
                
                total_removed_files += removed_files
                total_removed_dirs += removed_dirs
                processed_dirs.append(dir_name)
                print(f"   🗑️  Cleaned contents of: {dir_name}/ (removed {removed_files} files, {removed_dirs} subdirs)")
                
            except Exception as e:
                print(f"   ⚠️  Failed to clean {dir_name}/: {e}")
                skipped_dirs.append(dir_name)
        else:
            skipped_dirs.append(dir_name)
    
    print(f"\n🎯 Cleanup completed! Ready for fresh analysis.")
    print()
    if processed_dirs:
        print(f"✅ Successfully processed {len(processed_dirs)} directories:")
        for dir_name in processed_dirs:
            print(f"   ✓ {dir_name}/")
    
    if skipped_dirs:
        print(f"ℹ️  Skipped {len(skipped_dirs)} directories (couldn't process):")
        for dir_name in skipped_dirs:
            print(f"   • {dir_name}/")
    
    print()
    
    return {
        'processed': processed_dirs,
        'skipped': skipped_dirs,
        'total_processed': len(processed_dirs),
        'total_skipped': len(skipped_dirs),
        'total_removed_files': total_removed_files,
        'total_removed_dirs': total_removed_dirs
    }


def cleanup_all_output_directories():
    """
    Legacy function name for backward compatibility.
    Calls the new cleanup_output_directories function.
    """
    result = cleanup_output_directories()
    
    print(f"🎯 CLEANUP SUMMARY:")
    print(f"   📁 Directories processed: {result['total_processed']}")
    print(f"   🗑️  Total files removed: {result['total_removed_files']}")
    print(f"   📂 Total subdirectories removed: {result['total_removed_dirs']}")
    print(f"   ✅ All 14 output directories are now completely clean")
    
    return result['total_skipped'] == 0  # Return True if no directories were skipped


def main():
    """Main function for standalone cleanup execution."""
    result = cleanup_output_directories()
    
    print("=" * 80)
    print("📊 CLEANUP SUMMARY")
    print("=" * 80)
    print(f"✅ Processed: {result['total_processed']} directories")
    print(f"🗑️  Removed: {result['total_removed_files']} files, {result['total_removed_dirs']} subdirectories")
    print(f"ℹ️  Skipped: {result['total_skipped']} directories")
    
    if result['total_processed'] > 0:
        print("🎉 Cleanup completed successfully!")
    else:
        print("ℹ️  No directories needed processing.")


if __name__ == "__main__":
    main()

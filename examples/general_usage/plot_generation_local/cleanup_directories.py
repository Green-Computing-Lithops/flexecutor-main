#!/usr/bin/env python3
"""
Directory Cleanup Utility
=========================

This module provides functionality to clean up output directories
for the energy analysis pipeline.

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
            '100_local_analyze_universal_profiling',
            '101_local_generate_local_hypothesis_2_plots',
            '102_local_generate_local_hypothesis_3_plots',
            '103_local_generate_universal_ebpf_energy_plots',
            '104_local_generate_universal_perf_energy_plots',
            '105_local_generate_universal_rapl_energy_plots',
            '106_local_generate_universal_tdp_energy_plots',
            '107_local_multistage_stacked_graphs_universal'
        ]
    
    print("🧹 CLEANING OUTPUT DIRECTORIES")
    print("-" * 80)
    
    cleaned_dirs = []
    skipped_dirs = []
    
    for dir_name in output_directories:
        dir_path = script_dir / dir_name
        
        if dir_path.exists() and dir_path.is_dir():
            try:
                # Remove only the contents of the directory, not the directory itself
                for item in dir_path.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                cleaned_dirs.append(dir_name)
                print(f"🗑️  Cleaned contents of: {dir_name}/")
            except Exception as e:
                print(f"⚠️  Failed to clean {dir_name}/: {e}")
                skipped_dirs.append(dir_name)
        else:
            # Create the directory if it doesn't exist
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                cleaned_dirs.append(dir_name)
                print(f"📁 Created: {dir_name}/")
            except Exception as e:
                print(f"⚠️  Failed to create {dir_name}/: {e}")
                skipped_dirs.append(dir_name)
    
    print()
    if cleaned_dirs:
        print(f"✅ Successfully processed {len(cleaned_dirs)} directories:")
        for dir_name in cleaned_dirs:
            print(f"   ✓ {dir_name}/")
    
    if skipped_dirs:
        print(f"ℹ️  Skipped {len(skipped_dirs)} directories (couldn't process):")
        for dir_name in skipped_dirs:
            print(f"   • {dir_name}/")
    
    print(f"\n🎯 Cleanup completed! Ready for fresh analysis.")
    print()
    
    return {
        'cleaned': cleaned_dirs,
        'skipped': skipped_dirs,
        'total_cleaned': len(cleaned_dirs),
        'total_skipped': len(skipped_dirs)
    }


def main():
    """Main function for standalone cleanup execution."""
    result = cleanup_output_directories()
    
    print("=" * 80)
    print("📊 CLEANUP SUMMARY")
    print("=" * 80)
    print(f"✅ Cleaned: {result['total_cleaned']} directories")
    print(f"ℹ️  Skipped: {result['total_skipped']} directories")
    
    if result['total_cleaned'] > 0:
        print("🎉 Cleanup completed successfully!")
    else:
        print("ℹ️  No directories needed cleaning.")


if __name__ == "__main__":
    main()

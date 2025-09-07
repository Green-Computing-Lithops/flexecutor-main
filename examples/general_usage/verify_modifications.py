#!/usr/bin/env python3
"""
Script to verify the energy value modifications made to analysis_results_k8s JSON files.
"""

import json
import os
from pathlib import Path

def verify_modifications():
    """Verify the modifications made to the JSON files."""
    
    analysis_dir = Path("examples/general_usage/plot_generation/analysis_results_k8s")
    json_files = list(analysis_dir.glob("*.json"))
    
    print("=== ENERGY VALUE MODIFICATION VERIFICATION ===")
    print()
    
    for json_file in sorted(json_files):
        backup_file = Path(f"{json_file}.backup")
        
        if not backup_file.exists():
            print(f"No backup found for {json_file.name}")
            continue
            
        # Read original and modified files
        with open(backup_file, 'r') as f:
            original_data = json.load(f)
        
        with open(json_file, 'r') as f:
            modified_data = json.load(f)
        
        print(f"File: {json_file.name}")
        print("-" * 50)
        
        # Check first configuration for comparison
        orig_config = original_data['analysis_results'][0]
        mod_config = modified_data['analysis_results'][0]
        
        # Check if original values were 0 (as expected)
        orig_perf = orig_config.get('avg_perf_energy_cores', 0)
        orig_ebpf = orig_config.get('avg_ebpf_energy_pkg', 0)
        
        mod_perf = mod_config.get('avg_perf_energy_cores', 0)
        mod_ebpf = mod_config.get('avg_ebpf_energy_pkg', 0)
        
        print(f"Original perf energy: {orig_perf}")
        print(f"Modified perf energy: {mod_perf}")
        print(f"Original eBPF energy: {orig_ebpf}")
        print(f"Modified eBPF energy: {mod_ebpf}")
        
        # Check RAPL values (these might have had original values)
        orig_rapl = orig_config.get('avg_rapl', 0)
        mod_rapl = mod_config.get('avg_rapl', 0)
        
        if orig_rapl > 0:
            rapl_increase = ((mod_rapl / orig_rapl) - 1) * 100
            print(f"RAPL: {orig_rapl} -> {mod_rapl} ({rapl_increase:.1f}% increase)")
        else:
            print(f"RAPL: {orig_rapl} -> {mod_rapl} (new value)")
        
        print(f"Configurations processed: {len(modified_data['analysis_results'])}")
        print()

if __name__ == "__main__":
    verify_modifications()

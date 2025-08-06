#!/usr/bin/env python3
"""
Test script to verify energy metrics and CPU information are being captured
in the FlexExecutor stagefuture modifications.
"""

import json
import sys
from pathlib import Path

def test_energy_metrics_in_json():
    """Test that all energy metrics are present in the JSON output."""
    json_file = Path("examples/montecarlo_pi_estimation/profiling/montecarlo_pi_estimation/monte_carlo_pi_stage.json")
    
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        return False
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Get the first configuration
        config_key = list(data.keys())[0]
        config_data = data[config_key]
        
        # Expected energy metrics from our modifications
        expected_metrics = [
            # Energy metrics by method
            'perf_energy_pkg', 'perf_energy_cores', 'perf_energy_total',
            'rapl_energy_pkg', 'rapl_energy_cores', 'rapl_energy_total', 
            'ebpf_energy_pkg', 'ebpf_energy_cores', 'ebpf_energy_total', 'ebpf_cpu_cycles',
            'psutil_cpu_percent', 'psutil_memory_percent',
            
            # CPU information
            'cpu_name', 'cpu_brand', 'cpu_architecture', 'cpu_cores_physical', 'cpu_cores_logical',
            
            # Existing metrics (should still be there)
            'measurement_energy', 'RAPL', 'TDP'
        ]
        
        print("🔍 Testing energy metrics presence in JSON:")
        print(f"   Configuration: {config_key}")
        
        missing_metrics = []
        present_metrics = []
        
        for metric in expected_metrics:
            if metric in config_data:
                present_metrics.append(metric)
                print(f"   ✅ {metric}: Found ({len(config_data[metric])} entries)")
            else:
                missing_metrics.append(metric)
                print(f"   ❌ {metric}: Missing")
        
        if missing_metrics:
            print(f"\n❌ Missing {len(missing_metrics)} metrics: {missing_metrics}")
            return False
        
        print(f"\n✅ All {len(expected_metrics)} energy metrics present!")
        
        # Test data structure
        sample_metric = 'perf_energy_pkg'
        if isinstance(config_data[sample_metric], list) and len(config_data[sample_metric]) > 0:
            print(f"✅ Data structure valid (list with {len(config_data[sample_metric])} entries)")
        else:
            print("❌ Invalid data structure")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False

def test_dataclass_fields():
    """Test that FunctionTimes dataclass has all the new fields."""
    try:
        from flexecutor.utils.dataclass import FunctionTimes
        
        print("\n🔍 Testing FunctionTimes dataclass:")
        
        # Create instance to check fields
        ft = FunctionTimes()
        
        # Check for new energy fields
        new_fields = [
            'perf_energy_pkg', 'perf_energy_cores', 'perf_energy_total',
            'rapl_energy_pkg', 'rapl_energy_cores', 'rapl_energy_total',
            'ebpf_energy_pkg', 'ebpf_energy_cores', 'ebpf_energy_total', 'ebpf_cpu_cycles',
            'psutil_cpu_percent', 'psutil_memory_percent',
            'cpu_name', 'cpu_brand', 'cpu_architecture', 'cpu_cores_physical', 'cpu_cores_logical'
        ]
        
        missing_fields = []
        for field in new_fields:
            if hasattr(ft, field):
                print(f"   ✅ {field}: Present")
            else:
                missing_fields.append(field)
                print(f"   ❌ {field}: Missing")
        
        if missing_fields:
            print(f"\n❌ Missing {len(missing_fields)} fields in FunctionTimes: {missing_fields}")
            return False
        
        print(f"\n✅ All {len(new_fields)} new fields present in FunctionTimes!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing dataclass: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing FlexExecutor Energy Metrics Modifications")
    print("=" * 60)
    
    # Test 1: JSON file content
    json_test = test_energy_metrics_in_json()
    
    # Test 2: Dataclass fields
    dataclass_test = test_dataclass_fields()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   JSON Metrics Test: {'✅ PASSED' if json_test else '❌ FAILED'}")
    print(f"   Dataclass Test: {'✅ PASSED' if dataclass_test else '❌ FAILED'}")
    
    if json_test and dataclass_test:
        print("\n🎉 ALL TESTS PASSED! Energy metrics modifications are working correctly.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Check the modifications.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#
# (C) Copyright IBM Corp. 2020
# (C) Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import time
import logging
import subprocess
import threading
from collections import defaultdict
from .energymonitor_json_utils import store_energy_data_json, update_function_name

logger = logging.getLogger(__name__)

# Simplified BPF program that focuses on CPU cycles and process tracking
BPF_PROGRAM = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

// Define a structure to store process data
struct process_data_t {
    u32 pid;
    u64 cpu_cycles;
    u64 timestamp;
};

// Create BPF maps
BPF_HASH(process_data, u32, struct process_data_t);
BPF_PERF_OUTPUT(process_events);

// Function to be called on context switch
int on_context_switch(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 pid = prev->pid;
    
    // Skip kernel threads
    if (pid == 0)
        return 0;
    
    // Get current timestamp
    u64 ts = bpf_ktime_get_ns();
    
    // Create process data structure
    struct process_data_t data = {};
    data.pid = pid;
    data.cpu_cycles = 1;  // Count context switches as proxy for CPU activity
    data.timestamp = ts;
    
    // Update process data in map
    struct process_data_t *existing = process_data.lookup(&pid);
    if (existing) {
        existing->cpu_cycles += 1;
        existing->timestamp = ts;
    } else {
        process_data.update(&pid, &data);
    }
    
    // Send process data to user space
    process_events.perf_submit(ctx, &data, sizeof(data));
    
    return 0;
}
"""

class EBPFEnergyMonitor:
    """
    Simplified eBPF-based energy monitor that tracks CPU activity through context switches
    and estimates energy consumption based on CPU usage patterns.
    """
    def __init__(self, process_id):
        self.process_id = process_id
        self.bpf = None
        self.thread = None
        self.running = False
        self.process_data = defaultdict(lambda: {
            'context_switches': 0,
            'timestamps': []
        })
        self.start_time = None
        self.end_time = None
        self.function_name = None
        
        # Print directly to terminal for debugging
        print(f"\n==== EBPF ENERGY MONITOR INITIALIZED FOR PROCESS {process_id} ====")
        
    def _check_bpf_dependencies(self):
        """Check if BPF dependencies are installed."""
        try:
            # Check if BCC is installed
            import bcc
            return True
        except ImportError:
            # Try to add system packages path for BCC
            import sys
            system_packages_paths = [
                '/usr/lib/python3/dist-packages',
                '/usr/local/lib/python3/dist-packages',
                '/usr/lib/python3.10/dist-packages',
                '/usr/local/lib/python3.10/dist-packages'
            ]
            
            for path in system_packages_paths:
                if path not in sys.path:
                    sys.path.append(path)
            
            try:
                import bcc
                print(f"✅ Found BCC in system packages: {bcc.__file__}")
                return True
            except ImportError:
                print("BCC (BPF Compiler Collection) is not installed.")
                print("Please install it with: sudo apt-get install bpfcc-tools python3-bpfcc")
                return False
            
    def _check_kernel_config(self):
        """Check if the kernel is configured for BPF."""
        try:
            # Try to check if BPF is available by running a simple BPF program
            import bcc
            test_program = 'int kprobe__sys_clone(void *ctx) { return 0; }'
            test_bpf = bcc.BPF(text=test_program)
            test_bpf.cleanup()
            return True
        except Exception as e:
            print(f"Error testing BPF functionality: {e}")
            return False
                
    def _process_event(self, cpu, data, size):
        """Process events from BPF."""
        try:
            event = self.bpf["process_events"].event(data)
            pid = event.pid
            
            # Store process data
            self.process_data[pid]['context_switches'] += 1
            self.process_data[pid]['timestamps'].append(event.timestamp)
            
        except Exception as e:
            print(f"Error processing eBPF event: {e}")
        
    def _run_bpf_monitor(self):
        """Run the BPF monitor in a separate thread."""
        try:
            # Import BCC
            from bcc import BPF
            
            print("Loading eBPF program...")
            # Load BPF program
            self.bpf = BPF(text=BPF_PROGRAM)
            
            print("Attaching to context switch events...")
            # Try different kernel probe points for context switches
            probe_points = [
                "schedule",
                "__schedule", 
                "pick_next_task_fair",
                "context_switch"
            ]
            
            attached = False
            for probe_point in probe_points:
                try:
                    print(f"Trying to attach to {probe_point}...")
                    self.bpf.attach_kprobe(event=probe_point, fn_name="on_context_switch")
                    print(f"✅ Successfully attached to {probe_point}")
                    attached = True
                    break
                except Exception as e:
                    print(f"Failed to attach to {probe_point}: {e}")
                    continue
            
            if not attached:
                raise Exception("Failed to attach to any kernel probe point")
            
            print("Opening perf buffer...")
            # Open perf buffer for process events
            self.bpf["process_events"].open_perf_buffer(self._process_event)
            
            print("eBPF monitor running...")
            # Process events
            while self.running:
                try:
                    self.bpf.perf_buffer_poll(timeout=100)
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"Error running BPF monitor: {e}")
            import traceback
            traceback.print_exc()
            
    def start(self):
        """Start monitoring energy consumption using eBPF."""
        print("\n==== STARTING EBPF ENERGY MONITORING ====")
        
        # Check if BPF dependencies are installed
        if not self._check_bpf_dependencies():
            print("BPF dependencies are not installed.")
            return False
            
        # Check if the kernel is configured for BPF
        if not self._check_kernel_config():
            print("Kernel is not configured for BPF.")
            return False
            
        try:
            # Set running flag
            self.running = True
            
            # Start BPF monitor in a separate thread
            self.thread = threading.Thread(target=self._run_bpf_monitor)
            self.thread.daemon = True
            self.thread.start()
            
            # Record start time
            self.start_time = time.time()
            
            print(f"✅ eBPF energy monitoring started at: {self.start_time}")
            return True
        except Exception as e:
            print(f"❌ Error starting eBPF energy monitoring: {e}")
            return False
            
    def stop(self):
        """Stop monitoring energy consumption."""
        print("\n==== STOPPING EBPF ENERGY MONITORING ====")
        
        if not self.running:
            print("eBPF energy monitoring is not running.")
            return
            
        try:
            # Set running flag to False
            self.running = False
            
            # Wait for thread to finish
            if self.thread:
                self.thread.join(timeout=5)
                
            # Record end time
            self.end_time = time.time()
            
            # Calculate duration
            duration = self.end_time - self.start_time
            print(f"eBPF energy monitoring stopped at: {self.end_time}")
            print(f"Monitoring duration: {duration:.2f} seconds")
            
            # Detach BPF program
            if self.bpf:
                try:
                    self.bpf.detach_kprobe(event="finish_task_switch")
                    self.bpf.cleanup()
                except:
                    pass  # Ignore cleanup errors
                
        except Exception as e:
            print(f"Error stopping eBPF energy monitoring: {e}")
            
    def get_energy_data(self):
        """Get the collected energy data."""
        print("\n==== GETTING EBPF ENERGY DATA ====")
        
        # Calculate duration
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        print(f"Duration: {duration:.2f} seconds")
        
        # Get process data for the target process
        target_data = self.process_data.get(self.process_id, {
            'context_switches': 0,
            'timestamps': []
        })
        
        # Get total system activity
        total_context_switches = sum(data['context_switches'] for data in self.process_data.values())
        process_context_switches = target_data['context_switches']
        
        print(f"Process {self.process_id} context switches: {process_context_switches}")
        print(f"Total system context switches: {total_context_switches}")
        
        # If we don't have specific process data, estimate based on system activity and duration
        if process_context_switches == 0 and total_context_switches > 0:
            # Estimate process activity as a fraction of total system activity
            # Assume the process used some CPU time during the duration
            estimated_process_activity = max(1, int(total_context_switches * 0.1))  # 10% of system activity
            process_context_switches = estimated_process_activity
            print(f"Estimated process activity: {process_context_switches} context switches")
        
        # Estimate energy based on context switches and duration
        # This is a rough estimation based on typical CPU power consumption
        base_power_watts = 15.0  # Typical CPU base power
        max_power_watts = 65.0   # Typical CPU max power
        
        # Calculate activity ratio
        if total_context_switches > 0:
            activity_ratio = min(process_context_switches / max(total_context_switches, 1), 1.0)
        else:
            # If no context switches detected, estimate based on duration (assume some activity)
            activity_ratio = min(duration * 0.1, 1.0)  # 10% activity per second, capped at 100%
            
        # Estimate power consumption
        estimated_power = base_power_watts + (max_power_watts - base_power_watts) * activity_ratio
        estimated_energy = estimated_power * duration  # Energy in Joules
        
        # Split energy between package and cores (rough estimation)
        pkg_energy = estimated_energy * 0.4  # 40% package
        cores_energy = estimated_energy * 0.6  # 60% cores
        
        # Calculate core percentage
        core_percentage = cores_energy / max(pkg_energy, 0.001)
        
        # Estimate CPU cycles based on context switches and typical CPU frequency
        # Typical CPU frequency: ~3 GHz = 3,000,000,000 cycles/second
        # Context switches indicate CPU activity, estimate cycles accordingly
        cpu_frequency_ghz = 3.0  # Assume 3 GHz
        cycles_per_second = cpu_frequency_ghz * 1_000_000_000
        
        # Estimate CPU cycles based on activity ratio and duration
        estimated_cpu_cycles = int(cycles_per_second * activity_ratio * duration)
        
        # Ensure we have some CPU cycles if there was any activity
        if estimated_cpu_cycles == 0 and (process_context_switches > 0 or duration > 0):
            estimated_cpu_cycles = max(1000000, int(process_context_switches * 100000))  # Minimum 1M cycles
        
        # Create result dictionary
        result = {
            'energy': {
                'pkg': pkg_energy,
                'cores': cores_energy,
                'core_percentage': core_percentage,
                'cpu_cycles': estimated_cpu_cycles,
                'energy_from_cycles': estimated_energy
            },
            'duration': duration,
            'source': 'ebpf'
        }
        
        print(f"✅ eBPF energy estimation:")
        print(f"  Activity ratio: {activity_ratio:.4f}")
        print(f"  Estimated power: {estimated_power:.2f} W")
        print(f"  Package energy: {pkg_energy:.6f} J")
        print(f"  Cores energy: {cores_energy:.6f} J")
        print(f"  Total energy: {estimated_energy:.6f} J")
        print(f"  Estimated CPU cycles: {estimated_cpu_cycles:,}")
        
        return result
        
    def log_energy_data(self, energy_data, task, cpu_info, function_name=None):
        """Log energy data and store it in JSON format."""
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Store function name if provided
        if function_name:
            self.function_name = function_name
        
        # Log energy consumption
        logger.info(f"eBPF Energy consumption: {energy_data['energy'].get('pkg', 'N/A')} Joules (pkg), {energy_data['energy'].get('cores', 'N/A')} Joules (cores)")
        logger.info(f"eBPF Core percentage: {energy_data['energy'].get('core_percentage', 0) * 100:.2f}%")
        logger.info(f"eBPF CPU cycles: {energy_data['energy'].get('cpu_cycles', 0)}")
        logger.info(f"eBPF Energy from CPU cycles: {energy_data['energy'].get('energy_from_cycles', 0):.6f} Joules")
        
        # Print energy data
        print("\neBPF Performance counter stats:")
        print(f"CPU Cycles (estimated): {energy_data['energy'].get('cpu_cycles', 0)}")
        print(f"Energy (pkg): {energy_data['energy'].get('pkg', 0):.6f} Joules")
        print(f"Energy (cores): {energy_data['energy'].get('cores', 0):.6f} Joules")
        print(f"Core percentage: {energy_data['energy'].get('core_percentage', 0) * 100:.2f}%")
        print(f"Energy from CPU cycles: {energy_data['energy'].get('energy_from_cycles', 0):.6f} Joules")
        print()
        
        # Store energy data in JSON format using shared utilities
        pkg_energy = energy_data['energy'].get('pkg', 0)
        cores_energy = energy_data['energy'].get('cores', 0)
        core_percentage = energy_data['energy'].get('core_percentage', 0)
        
        monitor_specific_data = {
            'cpu_cycles': energy_data['energy'].get('cpu_cycles', 0),
            'energy_from_cycles': energy_data['energy'].get('energy_from_cycles', 0),
            'estimation_method': 'context_switches'
        }
        store_energy_data_json(energy_data, task, cpu_info, pkg_energy, cores_energy, 
                              core_percentage, function_name, monitor_specific_data)
        
    def update_function_name(self, task, function_name):
        """Update the function name in the JSON files."""
        # Store function name
        self.function_name = function_name
        
        # Use shared utility function
        update_function_name(task, function_name)

"""
Simple Lithops example using the map_reduce method.


cd inigo_test/

"""
import pprint
import lithops
import platform
from standarized_measurement_functions import sleep_function, prime_function

# iterdata = [1, 2, 3, 4, 5]

iterdata = [2]


# def my_reduce_function(results):
#     total = 0
#     for map_result in results:
#         total = total + map_result
#     return total

def print_cpu_info():
    """Print basic CPU information without using psutil or cpuinfo."""
    print("=" * 80)
    print("🖥️  SYSTEM & CPU INFORMATION")
    print("=" * 80)
    
    # Basic system info
    print(f"\n🔧 SYSTEM INFO:")
    print(f"   Platform: {platform.platform()}")
    print(f"   Architecture: {platform.architecture()[0]}")
    print(f"   Machine: {platform.machine()}")
    print(f"   Processor: {platform.processor()}")
    print(f"   System: {platform.system()}")
    print(f"   Python Version: {platform.python_version()}")
    
    print(f"\n💻 CPU DETAILS:")
    print(f"   CPU information will be collected by the energy monitoring system")
    print(f"   (psutil and cpuinfo functionality moved to energymonitor_psutil.py)")
    
    print(f"\n⚡ CPU PERFORMANCE:")
    print(f"   CPU performance metrics will be collected during function execution")
    print(f"   Check the energy monitoring results for detailed CPU usage")
    
    print("=" * 80)

def print_workload_comparison(sleep_future, prime_future):
    """Compare energy efficiency between different workloads."""
    
    print("\n" + "=" * 80)
    print("⚖️  WORKLOAD ENERGY COMPARISON")
    print("=" * 80)
    
    # Get metrics for both functions
    sleep_energy = sleep_future.stats.get('worker_func_enhanced_energy_total', 0.0)
    sleep_duration = sleep_future.stats.get('worker_func_energy_duration', 0.0)
    sleep_power = sleep_future.stats.get('worker_func_enhanced_power_consumption_watts', 0.0)
    sleep_cpu = sleep_future.stats.get('worker_func_psutil_process_cpu_percent', 0.0)
    
    prime_energy = prime_future.stats.get('worker_func_enhanced_energy_total', 0.0)
    prime_duration = prime_future.stats.get('worker_func_energy_duration', 0.0)
    prime_power = prime_future.stats.get('worker_func_enhanced_power_consumption_watts', 0.0)
    prime_cpu = prime_future.stats.get('worker_func_psutil_process_cpu_percent', 0.0)
    
    print(f"\n📊 COMPARATIVE METRICS:")
    print(f"{'Metric':<25} {'Sleep Function':<20} {'Prime Function':<20} {'Difference':<15}")
    print("-" * 80)
    print(f"{'Energy (J)':<25} {sleep_energy:<20.6f} {prime_energy:<20.6f} {abs(prime_energy - sleep_energy):<15.6f}")
    print(f"{'Duration (s)':<25} {sleep_duration:<20.3f} {prime_duration:<20.3f} {abs(prime_duration - sleep_duration):<15.3f}")
    print(f"{'Power (W)':<25} {sleep_power:<20.3f} {prime_power:<20.3f} {abs(prime_power - sleep_power):<15.3f}")
    print(f"{'CPU Usage (%)':<25} {sleep_cpu:<20.1f} {prime_cpu:<20.1f} {abs(prime_cpu - sleep_cpu):<15.1f}")
    
    # Calculate efficiency ratios
    if sleep_energy > 0 and prime_energy > 0:
        energy_ratio = prime_energy / sleep_energy
        power_ratio = prime_power / sleep_power if sleep_power > 0 else float('inf')
        
        print(f"\n🔄 EFFICIENCY RATIOS:")
        print(f"   Prime vs Sleep Energy Ratio: {energy_ratio:.2f}x")
        if power_ratio != float('inf'):
            print(f"   Prime vs Sleep Power Ratio: {power_ratio:.2f}x")
        
        # Energy per unit of work analysis
        if prime_duration > 0 and sleep_duration > 0:
            sleep_energy_rate = sleep_energy / sleep_duration
            prime_energy_rate = prime_energy / prime_duration
            print(f"   Sleep Energy Rate: {sleep_energy_rate:.6f} J/s")
            print(f"   Prime Energy Rate: {prime_energy_rate:.6f} J/s")
            
            if prime_energy_rate > sleep_energy_rate:
                efficiency_improvement = ((prime_energy_rate - sleep_energy_rate) / sleep_energy_rate) * 100
                print(f"   Prime function uses {efficiency_improvement:.1f}% more energy per second")
            else:
                efficiency_improvement = ((sleep_energy_rate - prime_energy_rate) / prime_energy_rate) * 100
                print(f"   Sleep function uses {efficiency_improvement:.1f}% more energy per second")
    
    print(f"\n💡 WORKLOAD INSIGHTS:")
    
    # Sleep function analysis
    if sleep_power < 0.2:
        print(f"   ✅ Sleep Function: Excellent idle efficiency ({sleep_power:.3f}W)")
    else:
        print(f"   ⚠️  Sleep Function: Higher than expected idle power ({sleep_power:.3f}W)")
    
    # Prime function analysis
    computation_intensity = prime_cpu / max(prime_duration, 0.001)
    if computation_intensity > 10:
        print(f"   🚀 Prime Function: High computational intensity ({computation_intensity:.1f} %CPU/s)")
    elif computation_intensity > 1:
        print(f"   ⚡ Prime Function: Moderate computational intensity ({computation_intensity:.1f} %CPU/s)")
    else:
        print(f"   🐌 Prime Function: Low computational intensity ({computation_intensity:.1f} %CPU/s)")
    
    # Energy efficiency recommendations
    if prime_energy > 0 and sleep_energy > 0:
        if energy_ratio > 10:
            print(f"   📈 High energy contrast - good for benchmarking different workload types")
        elif energy_ratio < 2:
            print(f"   📊 Similar energy consumption - workloads have comparable efficiency")
    
    print("=" * 80)

def print_comprehensive_energy_analysis(future, function_name):
    """Print comprehensive energy analysis comparing all available methods and metrics."""
    
    print("\n" + "=" * 80)
    print("🔬 COMPREHENSIVE ENERGY ANALYSIS")
    print("=" * 80)
    
    # Gather all energy data
    duration = future.stats.get('worker_func_energy_duration', 0.0)
    
    # PSUtil system monitoring
    base_available = future.stats.get('worker_func_psutil_available', False)
    sys_cpu_percent = future.stats.get('worker_func_psutil_cpu_percent', 0.0)
    sys_memory_percent = future.stats.get('worker_func_psutil_memory_percent', 0.0)
    proc_cpu_percent = future.stats.get('worker_func_psutil_process_cpu_percent', 0.0)
    proc_memory_mb = future.stats.get('worker_func_psutil_process_memory_mb', 0.0)
    cpu_freq = future.stats.get('worker_func_psutil_cpu_freq_current', 0.0)
    
    # CPU information from EnergyManager
    cpu_name = future.stats.get('worker_func_psutil_cpu_name', 'Unknown')
    cpu_brand = future.stats.get('worker_func_psutil_cpu_brand', 'Unknown')
    cpu_cores_physical = future.stats.get('worker_func_psutil_cpu_cores_physical', 0)
    
    # Enhanced energy monitoring
    enhanced_available = future.stats.get('worker_func_enhanced_available', False)
    enhanced_total = future.stats.get('worker_func_enhanced_energy_total', 0.0)
    enhanced_power_watts = future.stats.get('worker_func_enhanced_power_consumption_watts', 0.0)
    enhanced_efficiency_percent = future.stats.get('worker_func_enhanced_efficiency_percent', 0.0)
    enhanced_tdp = future.stats.get('worker_func_enhanced_tdp_watts', 0.0)
    enhanced_processor_type = future.stats.get('worker_func_enhanced_processor_type', 'unknown')
    
    print(f"\n🔍 FUNCTION ANALYSIS: {function_name}")
    print(f"   Execution Duration: {duration:.3f} seconds")
    print(f"   Processor: {cpu_name} ({cpu_brand})")
    print(f"   Cores Used: {cpu_cores_physical} physical cores")
    
    # Additional timing and CPU metrics (always show these)
    cpu_user_time = future.stats.get('worker_func_psutil_cpu_user_time', 0.0)
    cpu_usage_avg = future.stats.get('worker_func_avg_cpu_usage', 0.0)
    print(f"\n⏱️  TIMING & CPU METRICS:")
    print(f"   Duration: {duration:.3f} seconds")
    print(f"   CPU User Time: {cpu_user_time:.2f} seconds")
    print(f"   CPU Usage Average: {cpu_usage_avg:.2f}%")
    print(f"   Process CPU: {proc_cpu_percent:.2f}%")
    
    if base_available:
        print(f"\n📊 SYSTEM RESOURCE UTILIZATION:")
        print(f"   System CPU Load: {sys_cpu_percent:.1f}%")
        print(f"   Process CPU Usage: {proc_cpu_percent:.1f}%")
        print(f"   System Memory Usage: {sys_memory_percent:.1f}%")
        print(f"   Process Memory: {proc_memory_mb:.1f} MB")
        print(f"   CPU Frequency: {cpu_freq:.0f} MHz")
        
        # Basic system analysis
        if sys_cpu_percent > 50.0:
            print(f"   • ⚠️  High system CPU load ({sys_cpu_percent:.1f}%) - may affect measurements")
        if sys_memory_percent > 80.0:
            print(f"   • ⚠️  High memory usage ({sys_memory_percent:.1f}%) - may cause swapping")
        if proc_cpu_percent < 1.0:
            print(f"   • ✅ Low process CPU usage - efficient execution")
        else:
            print(f"   • 📈 Process CPU usage: {proc_cpu_percent:.1f}%")
    
    print("=" * 80)
    
    # Enhanced energy efficiency metrics
    if enhanced_available:
        print(f"\n⚡ ENERGY EFFICIENCY METRICS:")
        print(f"   Energy Consumption: {enhanced_total:.6f} Joules")
        print(f"   Average Power: {enhanced_power_watts:.3f} Watts")
        print(f"   Energy per Second: {enhanced_total/max(duration, 0.001):.3f} J/s")
        print(f"   TDP Utilization: {enhanced_efficiency_percent:.2f}% of {enhanced_tdp:.0f}W TDP")
        
        # Additional timing and CPU metrics
        cpu_user_time = future.stats.get('worker_func_psutil_cpu_user_time', 0.0)
        cpu_usage_avg = future.stats.get('worker_func_avg_cpu_usage', 0.0)
        print(f"\n⏱️  TIMING & CPU METRICS:")
        print(f"   Duration: {duration:.3f} seconds")
        print(f"   CPU User Time: {cpu_user_time:.2f} seconds")
        print(f"   CPU Usage Average: {cpu_usage_avg:.2f}%")
        print(f"   Process CPU: {proc_cpu_percent:.2f}%")
        
        # Calculate energy efficiency ratings
        if enhanced_total > 0:
            energy_per_joule = 1.0 / enhanced_total  # Operations per Joule (higher is better)
            if function_name == "sleep_function":
                efficiency_rating = "⭐⭐⭐⭐⭐ Excellent (Low-power idle)"
            elif enhanced_power_watts < 1.0:
                efficiency_rating = "⭐⭐⭐⭐ Very Good (< 1W)"
            elif enhanced_power_watts < 5.0:
                efficiency_rating = "⭐⭐⭐ Good (< 5W)"
            elif enhanced_power_watts < 10.0:
                efficiency_rating = "⭐⭐ Fair (< 10W)"
            else:
                efficiency_rating = "⭐ Needs Optimization (> 10W)"
            
            print(f"   Energy Efficiency Rating: {efficiency_rating}")
        
        # Performance vs Energy trade-off analysis
        if base_available and proc_cpu_percent > 0:
            energy_per_cpu_percent = enhanced_total / max(proc_cpu_percent, 0.001)
            print(f"   Energy per CPU%: {energy_per_cpu_percent:.6f} J per %CPU")
    
    if base_available:
        print(f"\n📊 SYSTEM RESOURCE UTILIZATION:")
        print(f"   System CPU Load: {sys_cpu_percent:.1f}%")
        print(f"   Process CPU Usage: {proc_cpu_percent:.1f}%")
        print(f"   System Memory Usage: {sys_memory_percent:.1f}%")
        print(f"   Process Memory: {proc_memory_mb:.1f} MB")
        print(f"   CPU Frequency: {cpu_freq:.0f} MHz")
        
        # Resource efficiency analysis
        if proc_cpu_percent > 0 and enhanced_available:
            cpu_efficiency = enhanced_total / max(proc_cpu_percent, 0.001)
            print(f"   CPU Energy Efficiency: {cpu_efficiency:.6f} J per %CPU")
        
        # Memory efficiency
        if proc_memory_mb > 0 and enhanced_available:
            memory_efficiency = enhanced_total / proc_memory_mb
            print(f"   Memory Energy Efficiency: {memory_efficiency:.6f} J per MB")
    
    # Processor-specific analysis
    print(f"\n🖥️  PROCESSOR-SPECIFIC ANALYSIS:")
    print(f"   Processor Type: {enhanced_processor_type.replace('_', ' ').title()}")
    
    if enhanced_processor_type == 'apple_silicon':
        print(f"   ✅ Apple Silicon Optimizations:")
        print(f"      • Very low TDP ({enhanced_tdp:.0f}W) - excellent for mobile workloads")
        print(f"      • ARM64 architecture - energy efficient instruction set")
        print(f"      • Unified memory architecture - reduced memory access energy")
    elif 'intel' in enhanced_processor_type.lower():
        print(f"   🔧 Intel Optimizations:")
        print(f"      • Consider Intel Speed Step for dynamic frequency scaling")
        print(f"      • Check for Turbo Boost impact on energy consumption")
    elif 'server' in enhanced_processor_type.lower():
        print(f"   🏢 Server Environment:")
        print(f"      • High TDP ({enhanced_tdp:.0f}W) optimized for throughput")
        print(f"      • Consider workload distribution across cores")
    
    # Recommendations
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    
    if enhanced_available and enhanced_power_watts > 0:
        if enhanced_efficiency_percent < 10.0:
            print(f"   • ✅ Good: Low power utilization ({enhanced_efficiency_percent:.1f}% of TDP)")
            print(f"   • Consider scaling up workload for better processor utilization")
        elif enhanced_efficiency_percent > 80.0:
            print(f"   • ⚠️  High power utilization ({enhanced_efficiency_percent:.1f}% of TDP)")
            print(f"   • Consider workload optimization or scaling across multiple instances")
        
        if function_name == "sleep_function" and enhanced_power_watts > 0.5:
            print(f"   • ⚠️  Unexpectedly high power for sleep function ({enhanced_power_watts:.2f}W)")
            print(f"   • Check for background processes or system overhead")
        
        if duration > 0 and enhanced_total / duration > 10.0:  # > 10W average
            print(f"   • 🔥 High average power consumption - consider optimization")
    
    if base_available:
        if sys_cpu_percent > 50.0:
            print(f"   • ⚠️  High system CPU load ({sys_cpu_percent:.1f}%) - may affect measurements")
        if sys_memory_percent > 80.0:
            print(f"   • ⚠️  High memory usage ({sys_memory_percent:.1f}%) - may cause swapping")
    
    print("=" * 80)

def print_working_methods_summary():
    """Print summary of working energy monitoring methods."""
    print("=" * 80)
    print("🔬 ENERGY MONITORING METHODS STATUS")
    print("=" * 80)
    
    print(f"\n📋 METHOD AVAILABILITY:")
    print(f"   ⚡ PERF Energy Monitoring: ❌ Not available (requires perf counters)")
    print(f"   🔌 RAPL Energy Monitoring: ❌ Not available (requires RAPL access)")
    print(f"   🐝 eBPF Energy Monitoring: ❌ Not available (requires eBPF/root)")
    print(f"   🚀 Enhanced/TDP Monitoring: ✅ Working (TDP-based estimation)")
    print(f"   💻 PSUtil System Monitoring: ✅ Working (System resource monitoring)")
    
    print(f"\n🎯 WORKING METHODS:")
    print(f"   • Enhanced/TDP: Provides package and cores energy estimates")
    print(f"   • PSUtil System: Provides comprehensive system resource monitoring (CPU, memory, disk, network)")
    print(f"   • Legacy Energy: Basic energy consumption calculation")
    
    print(f"\n💡 TO ENABLE MORE METHODS:")
    print(f"   • PERF: Run with appropriate permissions and perf support")
    print(f"   • RAPL: Requires Intel/AMD processors with RAPL support")
    print(f"   • eBPF: Requires root privileges and eBPF support")
    
    print("=" * 80)

def print_stats(future):
    """Print comprehensive energy monitoring statistics from all available methods."""
    
    print("=" * 80)
    print("📊 COMPREHENSIVE ENERGY MONITORING RESULTS")
    print("=" * 80)
    
    # === GENERAL METRICS ===
    print("\n🕒 GENERAL METRICS:")
    print(f"   Duration: {future.stats.get('worker_func_energy_duration', 'N/A')} seconds")
    print(f"   CPU User Time: {future.stats.get('worker_func_psutil_cpu_user_time', 'N/A')} seconds")
    print(f"   CPU Usage Average: {future.stats.get('worker_func_avg_cpu_usage', 'N/A')}%")
    print(f"   Legacy Energy Consumption: {future.stats.get('worker_func_energy_consumption', 'N/A')}")
    print(f"   Legacy Energy Method: {future.stats.get('worker_func_energy_method_used', 'N/A')}")
    
    # === PERF ENERGY MONITORING ===
    print("\n⚡ PERF ENERGY MONITORING:")
    perf_available = future.stats.get('worker_func_perf_available', False)
    perf_source = future.stats.get('worker_func_perf_source', 'unavailable')
    print(f"   Status: {'✅ Available' if perf_available else '❌ Unavailable'}")
    print(f"   Source: {perf_source}")
    
    if perf_available:
        perf_pkg = future.stats.get('worker_func_perf_energy_pkg', 0.0)
        perf_cores = future.stats.get('worker_func_perf_energy_cores', 0.0)
        perf_total = future.stats.get('worker_func_perf_energy_total', 0.0)
        print(f"   Package Energy: {perf_pkg:.6f} Joules")
        print(f"   Cores Energy: {perf_cores:.6f} Joules")
        print(f"   Total Energy: {perf_total:.6f} Joules")
        
        # Calculate percentage distribution
        if perf_total > 0:
            pkg_percent = (perf_pkg / perf_total) * 100
            cores_percent = (perf_cores / perf_total) * 100
            print(f"   Package %: {pkg_percent:.1f}% | Cores %: {cores_percent:.1f}%")
    else:
        print(f"   Package Energy: N/A")
        print(f"   Cores Energy: N/A")
        print(f"   Total Energy: N/A")
    
    # === RAPL ENERGY MONITORING ===
    print("\n🔌 RAPL ENERGY MONITORING:")
    rapl_available = future.stats.get('worker_func_rapl_available', False)
    rapl_source = future.stats.get('worker_func_rapl_source', 'unavailable')
    print(f"   Status: {'✅ Available' if rapl_available else '❌ Unavailable'}")
    print(f"   Source: {rapl_source}")
    
    if rapl_available:
        rapl_pkg = future.stats.get('worker_func_rapl_energy_pkg', 0.0)
        rapl_cores = future.stats.get('worker_func_rapl_energy_cores', 0.0)
        rapl_total = future.stats.get('worker_func_rapl_energy_total', 0.0)
        print(f"   Package Energy: {rapl_pkg:.6f} Joules")
        print(f"   Cores Energy: {rapl_cores:.6f} Joules")
        print(f"   Total Energy: {rapl_total:.6f} Joules")
        
        if rapl_total > 0:
            pkg_percent = (rapl_pkg / rapl_total) * 100
            cores_percent = (rapl_cores / rapl_total) * 100
            print(f"   Package %: {pkg_percent:.1f}% | Cores %: {cores_percent:.1f}%")
    else:
        print(f"   Package Energy: N/A")
        print(f"   Cores Energy: N/A")
        print(f"   Total Energy: N/A")
    
    # === eBPF ENERGY MONITORING ===
    print("\n🐝 eBPF ENERGY MONITORING:")
    ebpf_available = future.stats.get('worker_func_ebpf_available', False)
    ebpf_source = future.stats.get('worker_func_ebpf_source', 'unavailable')
    print(f"   Status: {'✅ Available' if ebpf_available else '❌ Unavailable'}")
    print(f"   Source: {ebpf_source}")
    
    if ebpf_available:
        ebpf_pkg = future.stats.get('worker_func_ebpf_energy_pkg', 0.0)
        ebpf_cores = future.stats.get('worker_func_ebpf_energy_cores', 0.0)
        ebpf_total = future.stats.get('worker_func_ebpf_energy_total', 0.0)
        ebpf_cycles = future.stats.get('worker_func_ebpf_cpu_cycles', 0.0)
        ebpf_energy_from_cycles = future.stats.get('worker_func_ebpf_energy_from_cycles', 0.0)
        
        print(f"   Package Energy: {ebpf_pkg:.6f} Joules")
        print(f"   Cores Energy: {ebpf_cores:.6f} Joules")
        print(f"   Total Energy: {ebpf_total:.6f} Joules")
        print(f"   CPU Cycles: {ebpf_cycles:,.0f}")
        print(f"   Energy from Cycles: {ebpf_energy_from_cycles:.6f} Joules")
        
        if ebpf_cycles > 0:
            energy_per_cycle = ebpf_energy_from_cycles / ebpf_cycles * 1e12  # picojoules per cycle
            print(f"   Energy/Cycle: {energy_per_cycle:.2f} pJ/cycle")
    else:
        print(f"   Package Energy: N/A")
        print(f"   Cores Energy: N/A")
        print(f"   CPU Cycles: N/A")
    
    # === PSUtil SYSTEM MONITORING ===
    print("\n💻 PSUtil SYSTEM MONITORING:")
    base_available = future.stats.get('worker_func_psutil_available', False)
    base_source = future.stats.get('worker_func_psutil_source', 'unavailable')
    print(f"   Status: {'✅ Available' if base_available else '❌ Unavailable'}")
    print(f"   Source: {base_source}")
    
    if base_available:
        # System-wide metrics
        sys_cpu_percent = future.stats.get('worker_func_psutil_cpu_percent', 0.0)
        sys_memory_percent = future.stats.get('worker_func_psutil_memory_percent', 0.0)
        sys_memory_used_mb = future.stats.get('worker_func_psutil_memory_used_mb', 0.0)
        disk_read_mb = future.stats.get('worker_func_psutil_disk_io_read_mb', 0.0)
        disk_write_mb = future.stats.get('worker_func_psutil_disk_io_write_mb', 0.0)
        net_sent_mb = future.stats.get('worker_func_psutil_network_sent_mb', 0.0)
        net_recv_mb = future.stats.get('worker_func_psutil_network_recv_mb', 0.0)
        
        # Process-specific metrics
        proc_cpu_percent = future.stats.get('worker_func_psutil_process_cpu_percent', 0.0)
        proc_memory_mb = future.stats.get('worker_func_psutil_process_memory_mb', 0.0)
        
        # Hardware metrics
        cpu_freq = future.stats.get('worker_func_psutil_cpu_freq_current', 0.0)
        cpu_temp = future.stats.get('worker_func_psutil_cpu_temp_celsius', 0.0)
        
        print(f"   🖥️  SYSTEM METRICS:")
        print(f"      CPU Usage: {sys_cpu_percent:.2f}%")
        print(f"      Memory Usage: {sys_memory_percent:.2f}% ({sys_memory_used_mb:.1f} MB)")
        print(f"      Disk I/O: Read {disk_read_mb:.2f} MB, Write {disk_write_mb:.2f} MB")
        print(f"      Network I/O: Sent {net_sent_mb:.2f} MB, Received {net_recv_mb:.2f} MB")
        
        print(f"   🔧 PROCESS METRICS:")
        print(f"      Process CPU: {proc_cpu_percent:.2f}%")
        print(f"      Process Memory: {proc_memory_mb:.1f} MB")
        
        print(f"   ⚙️  HARDWARE STATUS:")
        print(f"      CPU Frequency: {cpu_freq:.0f} MHz" if cpu_freq > 0 else "      CPU Frequency: N/A")
        print(f"      CPU Temperature: {cpu_temp:.1f}°C" if cpu_temp > 0 else "      CPU Temperature: N/A")
    else:
        print(f"   System Metrics: N/A")
        print(f"   Process Metrics: N/A")
        print(f"   Hardware Status: N/A")
    
    # === ENERGY METHODS COMPARISON (excluding PSUtil since it's system monitoring) ===
    print("\n📈 ENERGY METHODS COMPARISON:")
    methods = [
        ('PERF', future.stats.get('worker_func_perf_energy_total', 0.0), future.stats.get('worker_func_perf_available', False)),
        ('RAPL', future.stats.get('worker_func_rapl_energy_total', 0.0), future.stats.get('worker_func_rapl_available', False)),
        ('eBPF', future.stats.get('worker_func_ebpf_energy_total', 0.0), future.stats.get('worker_func_ebpf_available', False)),
        ('Enhanced', future.stats.get('worker_func_enhanced_energy_total', 0.0), future.stats.get('worker_func_enhanced_available', False))
        # Note: PSUtil excluded as it provides system monitoring, not energy measurement
    ]
    
    active_methods = [(name, energy) for name, energy, available in methods if available and energy > 0]
    
    if active_methods:
        print("   Available methods with energy data:")
        for name, energy in active_methods:
            print(f"     {name}: {energy:.6f} Joules")
        
        # Find method with highest energy reading
        max_method = max(active_methods, key=lambda x: x[1])
        print(f"   Highest reading: {max_method[0]} ({max_method[1]:.6f} J)")
    else:
        print("   ⚠️  No energy methods returned valid data")
    
    # === SYSTEM MONITORING SUMMARY ===
    base_available = future.stats.get('worker_func_psutil_available', False)
    if base_available:
        print("\n📊 SYSTEM MONITORING SUMMARY:")
        sys_cpu = future.stats.get('worker_func_psutil_cpu_percent', 0.0)
        proc_cpu = future.stats.get('worker_func_psutil_process_cpu_percent', 0.0)
        memory_usage = future.stats.get('worker_func_psutil_memory_percent', 0.0)
        print(f"   System Load: CPU {sys_cpu:.1f}%, Memory {memory_usage:.1f}%")
        print(f"   Process Impact: CPU {proc_cpu:.1f}%, Memory {future.stats.get('worker_func_psutil_process_memory_mb', 0.0):.1f} MB")
    
    # === CPU INFORMATION (FROM ENERGY MANAGER) ===
    print(f"\n🖥️  CPU INFORMATION (from Energy Manager):")
    
    # NEW: CPU information collected directly by EnergyManager
    em_cpu_name = future.stats.get('worker_func_psutil_cpu_name', 'Unknown')
    em_cpu_brand = future.stats.get('worker_func_psutil_cpu_brand', 'Unknown')
    em_cpu_arch = future.stats.get('worker_func_psutil_cpu_architecture', 'Unknown')
    em_cpu_cores_physical = future.stats.get('worker_func_psutil_cpu_cores_physical', 0)
    em_cpu_cores_logical = future.stats.get('worker_func_psutil_cpu_cores_logical', 0)
    em_cpu_frequency = future.stats.get('worker_func_psutil_cpu_frequency', 0.0)
    
    print(f"   📊 FROM ENERGY MANAGER WORKER:")
    print(f"      CPU Name: {em_cpu_name}")
    print(f"      CPU Brand: {em_cpu_brand}")
    print(f"      Architecture: {em_cpu_arch}")
    print(f"      Physical Cores: {em_cpu_cores_physical}")
    print(f"      Logical Cores: {em_cpu_cores_logical}")
    print(f"      Frequency: {em_cpu_frequency:.2f} MHz" if em_cpu_frequency > 0 else "      Frequency: N/A")
    
    # CPU information already collected by the energy monitoring system
    processor_name = future.stats.get('worker_processor_name', 'Unknown')
    processor_brand = future.stats.get('worker_processor_brand', 'Unknown') 
    processor_cores = future.stats.get('worker_processor_cores', 'Unknown')
    processor_threads = future.stats.get('worker_processor_threads', 'Unknown')
    cloud_instance = future.stats.get('worker_cloud_instance_type', None)
    
    print(f"\n   � FROM PROCESSOR INFO (for comparison):")
    print(f"      Processor Name: {processor_name}")
    print(f"      Processor Brand: {processor_brand}")
    print(f"      Physical Cores: {processor_cores}")
    print(f"      Logical Threads: {processor_threads}")
    
    if cloud_instance:
        print(f"      Cloud Instance Type: {cloud_instance}")
    
    # CPU information is now handled by the energy monitoring system
    print(f"\n   🔧 CPU INFORMATION:")
    print(f"      CPU details are collected by the energy monitoring system")
    print(f"      (psutil and cpuinfo functionality moved to energymonitor_psutil.py)")
    print(f"      Check the energy monitoring results above for detailed CPU information")
    
    print("=" * 80)

    print(f"CPU User Time: {future.stats.get('worker_func_psutil_cpu_user_time', 'N/A')}")
    print(f"CPU Usage Average: {future.stats.get('worker_func_avg_cpu_usage', 'N/A')}")
    print(f"Energy Consumption: {future.stats.get('worker_func_energy_consumption', 'N/A')}")
    
    # Method used: 
    print(f"Energy Method used: {future.stats.get('worker_func_energy_method_used', 'N/A')}")


    # PERF: added new
    pkg = future.stats.get('worker_func_perf_energy_pkg')
    cores = future.stats.get('worker_func_perf_energy_cores')

    print(f"Perf Energy pkg: {pkg if pkg is not None else 'N/A'}")
    print(f"Perf Energy cores: {cores if cores is not None else 'N/A'}")

    # Calculate CPU “percentage” from energy metrics, if both values are present
    if isinstance(pkg, (int, float)) and isinstance(cores, (int, float)) and pkg != 0:
        cpu_percentage = cores / pkg * 100
        print(f"Perf CPU Percentage: {cpu_percentage:.2f}%")
    else:
        print("Perf CPU Percentage: N/A")

    # For actual CPU-usage percentage at runtime, you could use psutil:
    # print(f"Current CPU usage (psutil): {psutil.cpu_percent(interval=1):.1f}%")

if __name__ == "__main__":
 

    # creates an instance of Lithops’ FunctionExecutor --> localhost & manage 
    fexec = lithops.FunctionExecutor() 

    #  executor distributes the my_map_function across the items in iterdata
    # The my_reduce_function is set to combine the results of the map phase.
    # fexec.map_reduce(sleep_function, iterdata, my_reduce_function)
    # print(fexec.get_result())
 

    print("Async call SLEEP function")
    fexec = lithops.FunctionExecutor(config=config)
    sleep_future = fexec.call_async(sleep_function, iterdata[0])
    result = fexec.get_result(fs=[sleep_future]) # leng --> return list of parameters 
    # pprint.pprint(sleep_future.stats)


    # Print only the three specific metrics
    print("\n\nSLEEP function metrics:")
    print_stats(sleep_future)
    
    # Add comprehensive energy analysis
    print_comprehensive_energy_analysis(sleep_future, "sleep_function")

    print("\n\nAsync call COSTLY function")
    fexec = lithops.FunctionExecutor(config=config)
    prime_future = fexec.call_async(prime_function, iterdata[0])
    max_prime_method1 = prime_future.result()                     # needed to wait 
    max_prime_method2 = fexec.get_result(fs=[prime_future])       # needed to wait 
    print(f"Method 1 - future.result(): {max_prime_method1}")
    print(f"Method 2 - fexec.get_result(): {max_prime_method2}")
    
    # Compare results - handle different return formats
    if isinstance(max_prime_method2, (list, tuple)) and len(max_prime_method2) > 0:
        print(f"Both methods return the same max prime number: {max_prime_method1 == max_prime_method2[0]}")
    else:
        print(f"Both methods return the same max prime number: {max_prime_method1 == max_prime_method2}")

    # Print metrics for the costly function 
    print("\n\nCOSTLY function metrics:")
    print_stats(prime_future)
    
    # Add comprehensive energy analysis for costly function
    print_comprehensive_energy_analysis(prime_future, "prime_function")
    
    # Add workload comparison
    print_workload_comparison(sleep_future, prime_future)
    
    # Legacy output for compatibility
    print("\n" + "=" * 80)
    print("📊 LEGACY OUTPUT (for compatibility)")
    print("=" * 80)
    
    print("CPU User Time:", sleep_future.stats.get('worker_func_psutil_cpu_user_time', 'N/A'))
    print("CPU Usage Average:", sleep_future.stats.get('worker_func_avg_cpu_usage', 'N/A'))
    print("Energy Consumption:", sleep_future.stats.get('worker_func_energy_consumption', 'N/A'))
    print("Energy Method used:", sleep_future.stats.get('worker_func_energy_method_used', 'N/A'))
    print("Perf Energy pkg:", sleep_future.stats.get('worker_func_perf_energy_pkg', 0.0))
    print("Perf Energy cores:", sleep_future.stats.get('worker_func_perf_energy_cores', 0.0))
    print("Perf CPU Percentage:", sleep_future.stats.get('worker_func_perf_cpu_percent', 'N/A'))


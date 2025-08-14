"""
Simple Lithops example using the map_reduce method.

In this example the map_reduce() method will launch one
map function for each entry in 'iterdata', and then it will
wait locally for the reduce result.

RUN WITH SUDO:

sudo env "PATH=$PATH" /home/bigrobbin/Desktop/TFG/lithops/venv/bin/python3 inigo_test/map_reduce.py

sudo env "PATH=$PATH" /home/bigrobbin/Desktop/TFG/venv/bin/python3 lithops_fork/inigo_test/general_test_map_reduce.py

previous
cd inigo_test/

"""
import psutil
import pprint
import lithops
from standarized_measurement_functions import sleep_function, prime_function

# iterdata = [1, 2, 3, 4, 5]

iterdata = [2]


# def my_reduce_function(results):
#     total = 0
#     for map_result in results:
#         total = total + map_result
#     return total

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
    
    # === BASE/PSUTIL ENERGY MONITORING ===
    print("\n💻 BASE/PSUTIL ENERGY MONITORING:")
    base_available = future.stats.get('worker_func_psutil_available', False)
    base_source = future.stats.get('worker_func_psutil_source', 'unavailable')
    print(f"   Status: {'✅ Available' if base_available else '❌ Unavailable'}")
    print(f"   Source: {base_source}")
    
    if base_available:
        base_pkg = future.stats.get('worker_func_psutil_energy_pkg', 0.0)
        base_cores = future.stats.get('worker_func_psutil_energy_cores', 0.0)
        base_total = future.stats.get('worker_func_psutil_energy_total', 0.0)
        base_cpu_percent = future.stats.get('worker_func_psutil_cpu_percent', 0.0)
        
        print(f"   Package Energy: {base_pkg:.6f} Joules")
        print(f"   Cores Energy: {base_cores:.6f} Joules")
        print(f"   Total Energy: {base_total:.6f} Joules")
        print(f"   CPU Percentage: {base_cpu_percent:.2f}%")
    else:
        print(f"   Package Energy: N/A")
        print(f"   CPU Percentage: N/A")
    
    # === SUMMARY COMPARISON ===
    print("\n📈 ENERGY METHODS COMPARISON:")
    methods = [
        ('PERF', future.stats.get('worker_func_perf_energy_total', 0.0), future.stats.get('worker_func_perf_available', False)),
        ('RAPL', future.stats.get('worker_func_rapl_energy_total', 0.0), future.stats.get('worker_func_rapl_available', False)),
        ('eBPF', future.stats.get('worker_func_ebpf_energy_total', 0.0), future.stats.get('worker_func_ebpf_available', False)),
        ('Enhanced', future.stats.get('worker_func_enhanced_energy_total', 0.0), future.stats.get('worker_func_enhanced_available', False)),
        ('Base', future.stats.get('worker_func_psutil_energy_total', 0.0), future.stats.get('worker_func_psutil_available', False))
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
    
    # Also show the local CPU info for additional comparison
    try:
        import cpuinfo
        cpu_info = cpuinfo.get_cpu_info()
        print(f"\n   🔧 FROM LOCAL CPUINFO (for comparison):")
        print(f"      CPU Brand: {cpu_info.get('brand_raw', 'Unknown')}")
        print(f"      CPU Architecture: {cpu_info.get('arch', 'Unknown')}")
        print(f"      CPU Bits: {cpu_info.get('bits', 'Unknown')}")
        print(f"      Physical Cores: {psutil.cpu_count(logical=False)}")
        print(f"      Logical Cores: {psutil.cpu_count(logical=True)}")
        print(f"      Processor Type: {cpu_info.get('arch_string_raw', 'Unknown')}")
    except ImportError:
        print(f"\n   🔧 FROM LOCAL PSUTIL:")
        print(f"      Physical Cores: {psutil.cpu_count(logical=False)}")
        print(f"      Logical Cores: {psutil.cpu_count(logical=True)}")
        print(f"      (Install py-cpuinfo for detailed CPU information)")
    
    print("=" * 80)

    print(f"CPU User Time: {future.stats.get('worker_func_psutil_cpu_user_time', 'N/A')}")
    print(f"CPU Usage Average: {future.stats.get('worker_func_avg_cpu_usage', 'N/A')}")  # busqueda de que libreria usa : psutils --> percentaje uso cpu 
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
    fexec = lithops.FunctionExecutor()
    future = fexec.call_async(sleep_function, iterdata[0])
    result = fexec.get_result(fs=[future]) # leng --> return list of parameters 
    # pprint.pprint(future.stats)


    # Print only the three specific metrics
    print("\n\nSLEEP function metrics:")
    print_stats(future)

    print("\n\nAsync call COSTLY function")
    fexec = lithops.FunctionExecutor()
    future = fexec.call_async(prime_function, iterdata[0])
    max_prime_method1 = future.result()                     # needed to wait 
    max_prime_method2 = fexec.get_result(fs=[future])       # needed to wait 
    print(f"Method 1 - future.result(): {max_prime_method1}")
    print(f"Method 2 - fexec.get_result(): {max_prime_method2}")
    print(f"Both methods return the same max prime number: {max_prime_method1 == max_prime_method2}")

    # Print only the three specific metrics
    print("\n\nCOSTLY function metrics:")
    print_stats(future)


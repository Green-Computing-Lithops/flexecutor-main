import platform
import os
import psutil
import subprocess
import re

def get_processor_info():
    info = {
        "current_core": None,
        "processor_name": None,
        "cores": None,
        "threads": None,
        "architecture": None,
        "frequency": None,
        "cache_size": None,
        "detailed_info": None
    }
    
    # Get current core
    try:
        process = psutil.Process(os.getpid())
        info["current_core"] = process.cpu_num()
    except:
        info["current_core"] = "Unable to determine"
    
    # Get processor name and basic info
    info["architecture"] = platform.machine()
    
    # Different methods based on OS
    if platform.system() == "Linux":
        # Get processor name from /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if "model name" in line:
                        info["processor_name"] = re.sub(".*model name.*:", "", line, 1).strip()
                        break
            
            # Get detailed CPU information using lscpu
            try:
                lscpu_output = subprocess.check_output("lscpu", shell=True).decode()
                info["detailed_info"] = lscpu_output
                
                # Extract key information
                for line in lscpu_output.split('\n'):
                    if "CPU(s):" in line and "NUMA" not in line:
                        info["threads"] = line.split(':')[1].strip()
                    elif "Core(s) per socket:" in line:
                        cores_per_socket = int(line.split(':')[1].strip())
                        sockets_line = [l for l in lscpu_output.split('\n') if "Socket(s):" in l]
                        if sockets_line:
                            sockets = int(sockets_line[0].split(':')[1].strip())
                            info["cores"] = cores_per_socket * sockets
                    elif "CPU max MHz:" in line:
                        info["frequency"] = line.split(':')[1].strip() + " MHz"
                    elif "Cache:" in line or "L3 cache:" in line:
                        info["cache_size"] = line.split(':')[1].strip()
            except:
                pass
                
        except FileNotFoundError:
            info["processor_name"] = "Unable to determine"
    
    elif platform.system() == "Darwin":  # macOS
        try:
            output = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            info["processor_name"] = output
            
            # Get core count
            physical_cores = subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"]).decode().strip()
            logical_cores = subprocess.check_output(["sysctl", "-n", "hw.logicalcpu"]).decode().strip()
            info["cores"] = physical_cores
            info["threads"] = logical_cores
            
            # Get CPU frequency
            try:
                freq = subprocess.check_output(["sysctl", "-n", "hw.cpufrequency"]).decode().strip()
                info["frequency"] = str(int(freq) // 1000000) + " MHz"
            except:
                pass
                
            # Get detailed info
            detailed = subprocess.check_output(["sysctl", "machdep.cpu"]).decode().strip()
            info["detailed_info"] = detailed
        except:
            pass
            
    elif platform.system() == "Windows":
        try:
            import wmi
            computer = wmi.WMI()
            cpu_info = computer.Win32_Processor()[0]
            info["processor_name"] = cpu_info.Name
            info["cores"] = cpu_info.NumberOfCores
            info["threads"] = cpu_info.NumberOfLogicalProcessors
            info["frequency"] = f"{cpu_info.MaxClockSpeed} MHz"
            info["detailed_info"] = str(cpu_info)
        except:
            try:
                # Fallback using Windows Management Instrumentation Command-line
                output = subprocess.check_output("wmic cpu get name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed", shell=True).decode()
                info["detailed_info"] = output
                lines = output.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        info["frequency"] = parts[-1] + " MHz"
                        info["threads"] = parts[-2]
                        info["cores"] = parts[-3]
                        info["processor_name"] = ' '.join(parts[:-3])
            except:
                pass
    
    # Use psutil as a fallback for core/thread count if not already determined
    if not info["cores"] or not info["threads"]:
        info["cores"] = psutil.cpu_count(logical=False)
        info["threads"] = psutil.cpu_count(logical=True)
    
    # Get CPU frequency using psutil if not already determined
    if not info["frequency"]:
        freq = psutil.cpu_freq()
        if freq:
            info["frequency"] = f"{freq.current} MHz"
    
    return info

# Example usage
if __name__ == "__main__":
    processor_info = get_processor_info()
    
    print("Processor Information:")
    print(f"Current core being executed on: {processor_info['current_core']}")
    print(f"Processor: {processor_info['processor_name']}")
    print(f"Physical cores: {processor_info['cores']}")
    print(f"Logical processors (threads): {processor_info['threads']}")
    print(f"Architecture: {processor_info['architecture']}")
    print(f"Max frequency: {processor_info['frequency']}")
    print(f"Cache size: {processor_info['cache_size']}")
    print("\nDetailed CPU Information:")
    print(processor_info['detailed_info'])
import os
import re
import subprocess

def check_rapl_support():
    """Check if Intel RAPL is supported on this processor."""
    
    # Method 1: Check for RAPL MSR (Model-Specific Register)
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
            
        # Check if it's an Intel processor
        if not re.search(r'vendor_id\s+:\s+GenuineIntel', cpu_info):
            return False, "Not an Intel processor"
        
        # Check for model name to determine generation
        model_match = re.search(r'model name\s+:\s+(.*)', cpu_info)
        if not model_match:
            return False, "Could not determine processor model"
        
        model_name = model_match.group(1)
        
        # Method 2: Check for RAPL interface in sysfs (more reliable)
        rapl_path = '/sys/class/powercap/intel-rapl'
        if os.path.exists(rapl_path):
            return True, f"RAPL supported on {model_name} (verified via powercap interface)"
        
        # Method 3: Try to access energy counter directly (requires root)
        try:
            result = subprocess.run(['sudo', 'rdmsr', '0x611'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   timeout=1)
            if result.returncode == 0:
                return True, f"RAPL supported on {model_name} (verified via MSR)"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Fallback: Check model name for known supported architectures
        supported_archs = ['sandy bridge', 'ivy bridge', 'haswell', 'broadwell', 
                          'skylake', 'kaby lake', 'coffee lake', 'comet lake',
                          'ice lake', 'tiger lake', 'alder lake', 'raptor lake',
                          'cascade lake', 'cannon lake']
        
        model_lower = model_name.lower()
        for arch in supported_archs:
            if arch in model_lower:
                return True, f"RAPL likely supported on {model_name} (based on architecture)"
        
        # Check generation by model number
        model_number = re.search(r'model\s+:\s+(\d+)', cpu_info)
        if model_number:
            model_num = int(model_number.group(1))
            # Sandy Bridge and newer generally have model numbers >= 42
            if model_num >= 42:
                return True, f"RAPL likely supported on {model_name} (based on model number {model_num})"
        
        return False, f"RAPL likely not supported on {model_name}"
        
    except Exception as e:
        return False, f"Error checking RAPL support: {str(e)}"

# Check for kernel module
def check_rapl_module():
    try:
        lsmod_output = subprocess.check_output(['lsmod'], text=True)
        if 'intel_rapl' in lsmod_output:
            return True, "Intel RAPL kernel module is loaded"
        
        # Check if module is available but not loaded
        modinfo_result = subprocess.run(['modinfo', 'intel_rapl'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True)
        if modinfo_result.returncode == 0:
            return True, "Intel RAPL kernel module is available but not loaded"
        
        return False, "Intel RAPL kernel module not found"
    except Exception as e:
        return False, f"Error checking RAPL module: {str(e)}"

if __name__ == "__main__":
    supported, reason = check_rapl_support()
    module_available, module_info = check_rapl_module()
    
    print(f"RAPL Support: {'Yes' if supported else 'No'}")
    print(f"Reason: {reason}")
    print(f"RAPL Module: {module_info}")
    
    if supported:
        print("\nAvailable RAPL domains:")
        rapl_path = '/sys/class/powercap/intel-rapl'
        if os.path.exists(rapl_path):
            domains = os.listdir(rapl_path)
            for domain in domains:
                if domain.startswith('intel-rapl:'):
                    domain_path = os.path.join(rapl_path, domain)
                    name_path = os.path.join(domain_path, 'name')
                    if os.path.exists(name_path):
                        with open(name_path, 'r') as f:
                            domain_name = f.read().strip()
                        print(f"  - {domain}: {domain_name}")
    
        print("\nNotes on using RAPL:")
        print("1. Root privileges may be required to access RAPL interfaces")
        print("2. RAPL MSR access requires msr kernel module to be loaded ('sudo modprobe msr')")
        print("3. For programmatic access, consider using libraries like pyRAPL or PAPI")
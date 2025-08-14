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

import platform
import os
import re
import logging
import subprocess
import json

logger = logging.getLogger(__name__)

def get_processor_info():
    """
    Get detailed information about the processor.
    Works on Intel, AMD, EC2, and S3 machines.
    
    Returns:
        dict: A dictionary containing processor information
    """
    info = {
        "processor_name": None,
        "processor_brand": None,  # Intel, AMD, etc.
        "cores": None,
        "threads": None,
        "architecture": None,
        "frequency": None,
        "cache_size": None,
        "cloud_instance_type": None,
        "is_virtual": False
    }
    
    # Get architecture
    info["architecture"] = platform.machine()
    
    # Check if running on a cloud instance
    try:
        # Check for EC2 instance
        if os.path.exists('/sys/hypervisor/uuid'):
            with open('/sys/hypervisor/uuid', 'r') as f:
                if f.read().startswith('ec2'):
                    info["is_virtual"] = True
                    # Try to get instance type from EC2 metadata service
                    try:
                        cmd = "curl -s http://169.254.169.254/latest/meta-data/instance-type"
                        instance_type = subprocess.check_output(cmd, shell=True).decode().strip()
                        info["cloud_instance_type"] = instance_type
                    except:
                        pass
        
        # Alternative check for EC2
        try:
            cmd = "curl -s --connect-timeout 1 http://169.254.169.254/latest/meta-data/instance-type"
            instance_type = subprocess.check_output(cmd, shell=True).decode().strip()
            if instance_type:
                info["is_virtual"] = True
                info["cloud_instance_type"] = instance_type
        except:
            pass
            
        # Check for virtualization
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'hypervisor' in cpuinfo:
                    info["is_virtual"] = True
        except:
            pass
    except:
        pass
    
    # Different methods based on OS
    if platform.system() == "Linux":
        # Get processor name from /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # Extract model name
                model_match = re.search(r'model name\s+:\s+(.*)', cpuinfo)
                if model_match:
                    info["processor_name"] = model_match.group(1).strip()
                    
                    # Determine brand (Intel, AMD, etc.)
                    if "intel" in info["processor_name"].lower():
                        info["processor_brand"] = "Intel"
                    elif "amd" in info["processor_name"].lower():
                        info["processor_brand"] = "AMD"
                    elif "arm" in info["processor_name"].lower():
                        info["processor_brand"] = "ARM"
                    else:
                        # Try to extract brand from the first word
                        first_word = info["processor_name"].split()[0]
                        if first_word and first_word[0].isupper():
                            info["processor_brand"] = first_word
            
            # Get detailed CPU information using lscpu
            try:
                lscpu_output = subprocess.check_output("lscpu", shell=True).decode()
                
                # Extract key information
                for line in lscpu_output.split('\n'):
                    if "CPU(s):" in line and "NUMA" not in line:
                        info["threads"] = int(line.split(':')[1].strip())
                    elif "Core(s) per socket:" in line:
                        cores_per_socket = int(line.split(':')[1].strip())
                        sockets_line = [l for l in lscpu_output.split('\n') if "Socket(s):" in l]
                        if sockets_line:
                            sockets = int(sockets_line[0].split(':')[1].strip())
                            info["cores"] = cores_per_socket * sockets
                    elif "CPU max MHz:" in line:
                        info["frequency"] = float(line.split(':')[1].strip())
                    elif "CPU min MHz:" in line:
                        info["min_frequency"] = float(line.split(':')[1].strip())
                    elif "Cache:" in line or "L3 cache:" in line:
                        info["cache_size"] = line.split(':')[1].strip()
                    elif "Vendor ID:" in line:
                        vendor = line.split(':')[1].strip()
                        if info["processor_brand"] is None:
                            if "intel" in vendor.lower():
                                info["processor_brand"] = "Intel"
                            elif "amd" in vendor.lower():
                                info["processor_brand"] = "AMD"
                            else:
                                info["processor_brand"] = vendor
            except Exception as e:
                logger.warning(f"Error getting lscpu info: {e}")
                
        except Exception as e:
            logger.warning(f"Error reading /proc/cpuinfo: {e}")
            info["processor_name"] = "Unable to determine"
    
    elif platform.system() == "Darwin":  # macOS
        try:
            output = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            info["processor_name"] = output
            
            # Determine brand
            if "intel" in output.lower():
                info["processor_brand"] = "Intel"
            elif "amd" in output.lower():
                info["processor_brand"] = "AMD"
            elif "apple" in output.lower():
                info["processor_brand"] = "Apple"
            
            # Get core count
            physical_cores = int(subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"]).decode().strip())
            logical_cores = int(subprocess.check_output(["sysctl", "-n", "hw.logicalcpu"]).decode().strip())
            info["cores"] = physical_cores
            info["threads"] = logical_cores
            
            # Get CPU frequency
            try:
                freq = int(subprocess.check_output(["sysctl", "-n", "hw.cpufrequency"]).decode().strip())
                info["frequency"] = freq / 1000000  # Convert to MHz
            except:
                pass
        except Exception as e:
            logger.warning(f"Error getting macOS CPU info: {e}")
            
    elif platform.system() == "Windows":
        try:
            # Try using WMI
            import wmi
            computer = wmi.WMI()
            cpu_info = computer.Win32_Processor()[0]
            info["processor_name"] = cpu_info.Name
            info["cores"] = cpu_info.NumberOfCores
            info["threads"] = cpu_info.NumberOfLogicalProcessors
            info["frequency"] = cpu_info.MaxClockSpeed
            
            # Determine brand
            if "intel" in cpu_info.Name.lower():
                info["processor_brand"] = "Intel"
            elif "amd" in cpu_info.Name.lower():
                info["processor_brand"] = "AMD"
        except:
            try:
                # Fallback using Windows Management Instrumentation Command-line
                output = subprocess.check_output("wmic cpu get name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed", shell=True).decode()
                lines = output.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        info["frequency"] = float(parts[-1])
                        info["threads"] = int(parts[-2])
                        info["cores"] = int(parts[-3])
                        info["processor_name"] = ' '.join(parts[:-3])
                        
                        # Determine brand
                        if "intel" in info["processor_name"].lower():
                            info["processor_brand"] = "Intel"
                        elif "amd" in info["processor_name"].lower():
                            info["processor_brand"] = "AMD"
            except Exception as e:
                logger.warning(f"Error getting Windows CPU info: {e}")
    
    # Use platform module as a fallback for processor name
    if not info["processor_name"]:
        info["processor_name"] = platform.processor()
    
    # Use platform module as a fallback for core/thread count
    if not info["cores"] or not info["threads"]:
        try:
            import psutil
            info["cores"] = psutil.cpu_count(logical=False)
            info["threads"] = psutil.cpu_count(logical=True)
        except:
            import multiprocessing
            info["threads"] = multiprocessing.cpu_count()
    
    # Convert numeric values to strings for JSON serialization
    for key, value in info.items():
        if isinstance(value, (int, float)):
            info[key] = value
    
    return info

def get_processor_info_json():
    """
    Get processor information as a JSON string.
    
    Returns:
        str: JSON string containing processor information
    """
    return json.dumps(get_processor_info(), indent=2)

def add_processor_info_to_task(task, call_status):
    """
    Get processor information and add it to the task's call status and stats file.
    This function handles all the logging, call status updates, and stats file writing.
    
    Args:
        task: The task object
        call_status: The call status object
        
    Returns:
        dict: The processor information dictionary
    """
    try:
        # Get processor information
        processor_info = get_processor_info()
        
        # Log processor information
        logger.info(f"Processor: {processor_info['processor_name']} ({processor_info['processor_brand']})")
        logger.info(f"Cores: {processor_info['cores']}, Threads: {processor_info['threads']}")
        
        # Add processor information to call status
        call_status.add('worker_processor_info', processor_info)
        call_status.add('worker_processor_name', processor_info['processor_name'])
        call_status.add('worker_processor_brand', processor_info['processor_brand'])
        call_status.add('worker_processor_cores', processor_info['cores'])
        call_status.add('worker_processor_threads', processor_info['threads'])
        
        # Add cloud instance information if available
        if processor_info['cloud_instance_type']:
            call_status.add('worker_cloud_instance_type', processor_info['cloud_instance_type'])
            logger.info(f"Cloud instance type: {processor_info['cloud_instance_type']}")
        
        # Add to stats file for future reference
        with open(task.stats_file, 'a') as f:
            f.write(f"processor_name {processor_info['processor_name']}\n")
            f.write(f"processor_brand {processor_info['processor_brand']}\n")
            f.write(f"processor_cores {processor_info['cores']}\n")
            f.write(f"processor_threads {processor_info['threads']}\n")
            if processor_info['frequency']:
                f.write(f"processor_frequency {processor_info['frequency']}\n")
            if processor_info['cloud_instance_type']:
                f.write(f"cloud_instance_type {processor_info['cloud_instance_type']}\n")
        
        return processor_info
    except Exception as e:
        logger.warning(f"Error getting processor information: {e}")
        return None

if __name__ == "__main__":
    # Test the function
    processor_info = get_processor_info()
    print(json.dumps(processor_info, indent=2))

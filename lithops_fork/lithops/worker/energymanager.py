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
import logging

logger = logging.getLogger(__name__)

class EnergyManager:
    """
    Unified energy manager that runs all available energy monitoring methods simultaneously.
    Collects data from all methods and stores them as separate fields in the result.
    """
    
    def __init__(self, process_id):
        """
        Initialize the energy manager with all available monitoring methods.
        
        Args:
            process_id: The process ID to monitor
        """
        self.process_id = process_id
        self.function_name = None
        
        # Initialize all energy monitors
        self.monitors = {}
        self.monitor_status = {}
        
        # Initialize each monitoring method
        self._initialize_monitors()
        
    def _initialize_monitors(self):
        """Initialize all available energy monitoring methods."""
        monitor_configs = {
            'perf': {
                'class': 'EnergyMonitor',
                'module': 'lithops.worker.energymonitor_perf'
            },
            'rapl': {
                'class': 'EnergyMonitor', 
                'module': 'lithops.worker.energymonitor_rapl'
            },
            'ebpf': {
                'class': 'EBPFEnergyMonitor',
                'module': 'lithops.worker.energymonitor_ebpf'
            },
            'psutil': {
                'class': 'EnergyMonitor',
                'module': 'lithops.worker.energymonitor_psutil'
            }
        }
        
        for method_name, config in monitor_configs.items():
            try:
                # Dynamically import the module
                module = __import__(config['module'], fromlist=[config['class']])
                monitor_class = getattr(module, config['class'])
                
                # Initialize the monitor
                monitor = monitor_class(self.process_id)
                self.monitors[method_name] = monitor
                self.monitor_status[method_name] = False
                
                logger.debug(f"Initialized {method_name} energy monitor")
                
            except Exception as e:
                logger.warning(f"Failed to initialize {method_name} energy monitor: {e}")
                self.monitors[method_name] = None
                self.monitor_status[method_name] = False
    
    def start(self):
        """Start all available energy monitoring methods."""
        any_started = False
        
        for method_name, monitor in self.monitors.items():
            if monitor is not None:
                try:
                    started = monitor.start()
                    self.monitor_status[method_name] = started
                    if started:
                        logger.info(f"Started {method_name} energy monitor")
                        any_started = True
                    else:
                        logger.warning(f"Failed to start {method_name} energy monitor")
                except Exception as e:
                    logger.error(f"Error starting {method_name} energy monitor: {e}")
                    self.monitor_status[method_name] = False
            else:
                self.monitor_status[method_name] = False
        
        logger.info(f"Energy monitoring started. Active monitors: {[m for m, s in self.monitor_status.items() if s]}")
        return any_started
    
    def stop(self):
        """Stop all active energy monitoring methods."""
        for method_name, monitor in self.monitors.items():
            if monitor is not None and self.monitor_status[method_name]:
                try:
                    monitor.stop()
                    logger.debug(f"Stopped {method_name} energy monitor")
                except Exception as e:
                    logger.error(f"Error stopping {method_name} energy monitor: {e}")
    
    def _get_aws_processor_info(self):
        """Get AWS processor information for Lambda functions in just a few lines."""
        import os
        import urllib.request
        import json
        import platform
        
        processor_info = {}
        
        # Quick AWS detection - check for Lambda environment
        if os.environ.get('AWS_LAMBDA_RUNTIME_API'):
            processor_info['instance_type'] = 'lambda-function'
            processor_info['is_lambda'] = True
            processor_info['memory_size'] = os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE', 'unknown')
            processor_info['architecture'] = platform.machine()
            
            # Try quick IMDS call for instance type (works in some AWS environments)
            try:
                with urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-type', timeout=1) as response:
                    processor_info['instance_type'] = response.read().decode('utf-8')
            except:
                pass  # Keep default lambda-function type
        else:
            processor_info['is_lambda'] = False
            processor_info['instance_type'] = 'unknown'
        
        return processor_info
    
    def read_function_name_from_stats(self, stats_file):
        """Read function name from stats file."""
        if not os.path.exists(stats_file):
            return None
            
        logger.info(f"Reading stats file for function name: {stats_file}")
        try:
            with open(stats_file, 'r') as fid:
                for line in fid.readlines():
                    try:
                        key, value = line.strip().split(" ", 1)
                        if key == 'function_name':
                            self.function_name = value
                            logger.info(f"Found function name in stats file: {self.function_name}")
                            return self.function_name
                    except Exception as e:
                        logger.error(f"Error processing stats file line: {line} - {e}")
        except Exception as e:
            logger.error(f"Error reading stats file: {e}")
        
        return None
    def process_energy_data(self, task, call_status, cpu_info):
        """Process energy data from all monitors and add to call status."""
        
        # Calculate CPU metrics first
        avg_cpu_usage = sum(cpu_info['usage']) / len(cpu_info['usage']) if cpu_info['usage'] else 0
        energy_consumption = avg_cpu_usage * round(cpu_info['user'], 8)
        
        # Initialize all energy fields to 0
        energy_fields = {
            # Duration and overall metrics
            'worker_func_energy_duration': 0.0,
            
            # PERF metrics
            'worker_func_perf_energy_pkg': 0.0,
            'worker_func_perf_energy_cores': 0.0,
            'worker_func_perf_energy_total': 0.0,
            'worker_func_perf_source': 'unavailable',
            'worker_func_perf_available': False,
            
            # RAPL metrics
            'worker_func_rapl_energy_pkg': 0.0,
            'worker_func_rapl_energy_cores': 0.0,
            'worker_func_rapl_energy_total': 0.0,
            'worker_func_rapl_source': 'unavailable',
            'worker_func_rapl_available': False,
            
            # eBPF metrics
            'worker_func_ebpf_energy_pkg': 0.0,
            'worker_func_ebpf_energy_cores': 0.0,
            'worker_func_ebpf_energy_total': 0.0,
            'worker_func_ebpf_cpu_cycles': 0.0,
            'worker_func_ebpf_energy_from_cycles': 0.0,
            'worker_func_ebpf_source': 'unavailable',
            'worker_func_ebpf_available': False,
            
            # PSUtil system monitoring metrics (no energy, but system resource monitoring)
            'worker_func_psutil_cpu_percent': 0.0,
            'worker_func_psutil_memory_percent': 0.0,
            'worker_func_psutil_memory_used_mb': 0.0,
            'worker_func_psutil_disk_io_read_mb': 0.0,
            'worker_func_psutil_disk_io_write_mb': 0.0,
            'worker_func_psutil_network_sent_mb': 0.0,
            'worker_func_psutil_network_recv_mb': 0.0,
            'worker_func_psutil_process_cpu_percent': 0.0,
            'worker_func_psutil_process_memory_mb': 0.0,
            'worker_func_psutil_cpu_freq_current': 0.0,
            'worker_func_psutil_cpu_temp_celsius': 0.0,
            'worker_func_psutil_source': 'unavailable',
            'worker_func_psutil_available': False,
            
            # CPU Information from EnergyManager
            'worker_func_psutil_cpu_name': 'Unknown',
            'worker_func_psutil_cpu_brand': 'Unknown',
            'worker_func_psutil_cpu_architecture': 'Unknown',
            'worker_func_psutil_cpu_cores_physical': 0,
            'worker_func_psutil_cpu_cores_logical': 0,
            'worker_func_psutil_cpu_frequency': 0.0,
            
            # CPU metrics calculated from CPU info
            'worker_func_avg_cpu_usage': avg_cpu_usage,
            'worker_func_energy_consumption': energy_consumption, # old rapl , wrong format 
        }
        
        # CPU information will be collected from PSUtil monitor when available
        # Add basic platform info as fallback
        import platform
        energy_fields['worker_func_psutil_cpu_architecture'] = platform.machine()
        
        # Process data from each monitor
        max_duration = 0.0
        
        for method_name, monitor in self.monitors.items():
            if monitor is not None and self.monitor_status.get(method_name, False):
                try:
                    energy_data = monitor.get_energy_data()
                    
                    # Update maximum duration
                    duration = energy_data.get('duration', 0.0)
                    max_duration = max(max_duration, duration)
                    
                    # Extract energy values
                    energy = energy_data.get('energy', {})
                    pkg_energy = energy.get('pkg', 0.0)
                    cores_energy = energy.get('cores', 0.0)
                    total_energy = pkg_energy + cores_energy if pkg_energy > 0 or cores_energy > 0 else 0.0
                    
                    source = energy_data.get('source', 'unknown')
                    
                    # Store method-specific data
                    if method_name == 'perf':
                        energy_fields['worker_func_perf_energy_pkg'] = pkg_energy
                        energy_fields['worker_func_perf_energy_cores'] = cores_energy
                        energy_fields['worker_func_perf_energy_total'] = total_energy
                        energy_fields['worker_func_perf_source'] = source
                        energy_fields['worker_func_perf_available'] = True
                        
                    elif method_name == 'rapl':
                        energy_fields['worker_func_rapl_energy_pkg'] = pkg_energy
                        energy_fields['worker_func_rapl_energy_cores'] = cores_energy
                        energy_fields['worker_func_rapl_energy_total'] = total_energy
                        energy_fields['worker_func_rapl_source'] = source
                        energy_fields['worker_func_rapl_available'] = True
                        
                    elif method_name == 'ebpf':
                        energy_fields['worker_func_ebpf_energy_pkg'] = pkg_energy
                        energy_fields['worker_func_ebpf_energy_cores'] = cores_energy
                        energy_fields['worker_func_ebpf_energy_total'] = total_energy
                        energy_fields['worker_func_ebpf_cpu_cycles'] = energy.get('cpu_cycles', 0.0)
                        energy_fields['worker_func_ebpf_energy_from_cycles'] = energy.get('energy_from_cycles', 0.0)
                        energy_fields['worker_func_ebpf_source'] = source
                        energy_fields['worker_func_ebpf_available'] = True
                        
                    elif method_name == 'psutil':
                        # PSUtil provides system resource monitoring and CPU information
                        system_data = energy_data.get('system', {})
                        process_data = energy_data.get('process', {})
                        cpu_info_data = energy_data.get('cpu_info', {})
                        
                        # System and process monitoring with enhanced CPU metrics
                        energy_fields['worker_func_psutil_cpu_percent'] = system_data.get('cpu_percent', 0.0)
                        energy_fields['worker_func_psutil_cpu_percent_initial'] = system_data.get('cpu_percent_initial', 0.0)
                        energy_fields['worker_func_psutil_cpu_percent_final'] = system_data.get('cpu_percent_final', 0.0)
                        energy_fields['worker_func_psutil_cpu_percent_avg_initial'] = system_data.get('cpu_percent_avg_initial', 0.0)
                        energy_fields['worker_func_psutil_cpu_percent_avg_final'] = system_data.get('cpu_percent_avg_final', 0.0)
                        energy_fields['worker_func_psutil_cpu_percent_max_initial'] = system_data.get('cpu_percent_max_initial', 0.0)
                        energy_fields['worker_func_psutil_cpu_percent_max_final'] = system_data.get('cpu_percent_max_final', 0.0)
                        energy_fields['worker_func_psutil_memory_percent'] = system_data.get('memory_percent', 0.0)
                        energy_fields['worker_func_psutil_memory_used_mb'] = system_data.get('memory_used_mb', 0.0)
                        energy_fields['worker_func_psutil_disk_io_read_mb'] = system_data.get('disk_io_read_mb', 0.0)
                        energy_fields['worker_func_psutil_disk_io_write_mb'] = system_data.get('disk_io_write_mb', 0.0)
                        energy_fields['worker_func_psutil_network_sent_mb'] = system_data.get('network_sent_mb', 0.0)
                        energy_fields['worker_func_psutil_network_recv_mb'] = system_data.get('network_recv_mb', 0.0)
                        energy_fields['worker_func_psutil_process_cpu_percent'] = process_data.get('cpu_percent', 0.0)
                        energy_fields['worker_func_psutil_process_cpu_percent_initial'] = process_data.get('cpu_percent_initial', 0.0)
                        energy_fields['worker_func_psutil_process_cpu_percent_final'] = process_data.get('cpu_percent_final', 0.0)
                        energy_fields['worker_func_psutil_process_memory_mb'] = process_data.get('memory_mb', 0.0)
                        energy_fields['worker_func_psutil_cpu_freq_current'] = system_data.get('cpu_freq_current', 0.0)
                        energy_fields['worker_func_psutil_cpu_temp_celsius'] = system_data.get('cpu_temp_celsius', 0.0)
                        energy_fields['worker_func_psutil_source'] = source
                        energy_fields['worker_func_psutil_available'] = True
                        
                        # CPU information from PSUtil
                        energy_fields['worker_func_psutil_cpu_cores_physical'] = cpu_info_data.get('cores_physical', 0)
                        energy_fields['worker_func_psutil_cpu_cores_logical'] = cpu_info_data.get('cores_logical', 0)
                        energy_fields['worker_func_psutil_cpu_frequency'] = cpu_info_data.get('frequency_current', 0.0)
                        energy_fields['worker_func_psutil_cpu_brand'] = cpu_info_data.get('brand', 'Unknown')
                        energy_fields['worker_func_psutil_cpu_name'] = cpu_info_data.get('model', 'Unknown')
                        energy_fields['worker_func_psutil_cpu_architecture'] = cpu_info_data.get('arch', energy_fields['worker_func_psutil_cpu_architecture'])
                        
                        logger.info(f"Collected CPU info from PSUtil: {energy_fields['worker_func_psutil_cpu_name']} ({energy_fields['worker_func_psutil_cpu_brand']})")
                    
                    # Log energy data for each method
                    try:
                        monitor.log_energy_data(energy_data, task, cpu_info, self.function_name)
                    except Exception as log_e:
                        logger.warning(f"Failed to log energy data for {method_name}: {log_e}")
                        
                except Exception as e:
                    logger.error(f"Error processing energy data from {method_name}: {e}")
        
        # Set the overall duration to the maximum from all monitors
        energy_fields['worker_func_energy_duration'] = max_duration
        
        # Add all energy fields to call status
        for field_name, field_value in energy_fields.items():
            call_status.add(field_name, field_value)
        
        # Get AWS processor information for Lambda functions
        aws_processor_info = self._get_aws_processor_info()
        for key, value in aws_processor_info.items():
            call_status.add(f'worker_func_aws_{key}', value)
        
        # Add version indicator for new energy monitoring system
        call_status.add('worker_func_uss_55', 12)  # Version indicator: 12 = enhanced PSUtil CPU measurement with high precision

        # Create worker_func_energy_method_used field with consistent ordering
        method_order = ['perf', 'rapl', 'ebpf', 'psutil']
        available_methods = []
        
        for method in method_order:
            if self.monitor_status.get(method, False) and self.monitors.get(method) is not None:
                available_methods.append(method)
            else:
                available_methods.append('null')
        
        # Set the energy method used field
        if available_methods:
            energy_method_used = ', '.join(available_methods)
        else:
            energy_method_used = 'n/a'
        
        call_status.add('worker_func_energy_method_used', energy_method_used)
        
        # Log summary of collected data
        active_methods = [m for m, s in self.monitor_status.items() if s and self.monitors[m] is not None]
        logger.info(f"Energy data collected from {len(active_methods)} methods: {active_methods}")
        logger.info(f"Energy method used: {energy_method_used}")
        
        # Log non-zero energy values for debugging
        non_zero_fields = {k: v for k, v in energy_fields.items() if isinstance(v, (int, float)) and v > 0}
        if non_zero_fields:
            logger.debug(f"Non-zero energy values: {non_zero_fields}")
    
    def update_function_name(self, task, cpu_info, stats_file):
        """Update function name in energy data for all monitors if available."""
        if not any(self.monitor_status.values()):
            return
            
        if not os.path.exists(stats_file):
            logger.warning("Stats file not found for updating function name")
            return
            
        function_name = self.read_function_name_from_stats(stats_file)
        if not function_name:
            logger.warning("Function name not found in stats file for energy monitoring")
            return
            
        logger.info(f"Updating function name in energy data: {function_name}")
        
        # Update function name in all active monitors
        for method_name, monitor in self.monitors.items():
            if monitor is not None and self.monitor_status.get(method_name, False):
                try:
                    if hasattr(monitor, 'update_function_name'):
                        monitor.update_function_name(task, function_name)
                    elif hasattr(monitor, '_store_energy_data_json'):
                        # For eBPF monitor specifically
                        monitor._store_energy_data_json(
                            monitor.get_energy_data(), 
                            task, 
                            cpu_info, 
                            function_name
                        )
                except Exception as e:
                    logger.warning(f"Failed to update function name for {method_name}: {e}")

from __future__ import annotations

from typing import Any, Optional, List

from lithops.utils import FuturesList

from flexecutor.utils.dataclass import FunctionTimes


class StageFuture:
    def __init__(self, stage_id: str, future: Optional[FuturesList] = None):
        self.__stage_id = stage_id
        self.__future = future

    def result(self) -> Any:
        return [i[0] for i in self.__future.get_result()]

    def _timings_list(self) -> list[FunctionTimes]:
        return [i[1] for i in self.__future.get_result()]

    @property
    def stats(self):
        return [f.stats for f in self.__future]

    def error(self) -> bool:
        return any([f.error for f in self.__future])

    def __getattr__(self, item):
        if item in vars(self):
            return getattr(self, item)
        elif "__future" in vars(self) and item in vars(self.__future):
            return getattr(self.__future, item)
        raise AttributeError(f"Future object has no attribute {item}")

    def get_timings(self) -> List[FunctionTimes]:
        """Get the timings of the future."""
        timings_list = []
        for r, s in zip(self._timings_list(), self.stats):
            host_submit_tstamp = s["host_submit_tstamp"]
            worker_start_tstamp = s["worker_start_tstamp"]
            r.cold_start = worker_start_tstamp - host_submit_tstamp
            
            ##~~TIME~~##
            r.time_consumption = s["worker_exec_time"]
            worker_end_tstamp = s["worker_end_tstamp"]

            ##~~ENERGY~~##
            # Extract CPU usage and calculate TDP = execution_time * cpu_percent
            r.worker_time_execution = worker_end_tstamp - worker_start_tstamp 
            exec_time = s["worker_exec_time"]
            cpu_percent = s.get("worker_func_avg_cpu_usage", 0)  # Use avg CPU usage, default to 0 if not available

            # r.TDP = exec_time * (cpu_percent / 100.0) # old TDP calculation, avoid cold start time
            r.TDP = r.worker_time_execution * (cpu_percent / 100.0)  # optimize TDP calculation

            # r.RAPL_wrong = s.get("worker_func_energy_consumption", 0)  # Use the actual energy consumption key. worker_func_uss_55
            r.RAPL_wrong = s.get("RAPL_wrong", s.get("worker_func_uss_55", 1))
            # Extract energy measurement method used
            r.measurement_energy = s.get("worker_func_energy_method_used", "n/a")
            
            # Extract PERF energy metrics
            r.perf_energy_pkg = s.get("worker_func_perf_energy_pkg", 0.0)
            r.perf_energy_cores = s.get("worker_func_perf_energy_cores", 0.0)
            r.perf_energy_total = s.get("worker_func_perf_energy_total", 0.0)
            
            # Extract RAPL energy metrics
            r.rapl_energy_pkg = s.get("worker_func_rapl_energy_pkg", 0.0)
            r.rapl_energy_cores = s.get("worker_func_rapl_energy_cores", 0.0)
            r.rapl_energy_total = s.get("worker_func_rapl_energy_total", 0.0)
            
            # Extract eBPF energy metrics
            r.ebpf_energy_pkg = s.get("worker_func_ebpf_energy_pkg", 0.0)
            r.ebpf_energy_cores = s.get("worker_func_ebpf_energy_cores", 0.0)
            r.ebpf_energy_total = s.get("worker_func_ebpf_energy_total", 0.0)
            r.ebpf_cpu_cycles = s.get("worker_func_ebpf_cpu_cycles", 0.0)
            
            # Extract PSUtil (base) system monitoring metrics
            r.psutil_cpu_percent = s.get("worker_func_psutil_cpu_percent", 0.0)
            r.psutil_memory_percent = s.get("worker_func_psutil_memory_percent", 0.0)
            
            # Extract CPU information
            # Get processor info dict for more detailed information
            processor_info = s.get("worker_processor_info", {})
            
            r.cpu_name = s.get("worker_processor_name", processor_info.get("processor_name", "Unknown"))
            r.cpu_brand = s.get("worker_processor_brand", processor_info.get("processor_brand", "Unknown"))
            r.cpu_architecture = processor_info.get("architecture", "Unknown")
            r.cpu_cores_physical = s.get("worker_processor_cores", processor_info.get("cores", 0)) or 0
            r.cpu_cores_logical = s.get("worker_processor_threads", processor_info.get("threads", 0)) or 0
            
            # Extract AWS processor information
            aws_instance_type = s.get("worker_func_aws_instance_type", "Unknown")
            aws_architecture = s.get("worker_func_aws_architecture", "Unknown") 
            aws_is_lambda = s.get("worker_func_aws_is_lambda", False)
            aws_memory_size = s.get("worker_func_aws_memory_size", "unknown")
            
            # Create comprehensive AWS CPU identifier with all information
            r.aws_cpu = f"type:{aws_instance_type}|arch:{aws_architecture}|lambda:{aws_is_lambda}|mem:{aws_memory_size}"
            
            timings_list.append(r)
        return timings_list

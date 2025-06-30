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
            r.worker_time_execution = worker_end_tstamp - worker_start_tstamp
            # r.worker_time_execution = s["worker_func_cpu_user_time"] # not used now --> keep as check   # REVIEW: worker_func_cpu_user_time --> USED IN MANY PLACES 

            
            ##~~ENERGY~~##
            # Extract CPU usage and calculate TDP = execution_time * cpu_percent
            exec_time = s["worker_exec_time"]
            #cpu_percent = s["worker_cpu_percent"] # ERROR
            cpu_percent = s.get("worker_func_avg_cpu_usage", 0)  # Use avg CPU usage, default to 0 if not available
            r.TDP = exec_time * (cpu_percent / 100.0)
            
            # r.RAPL = s["worker_func_energy_consumption"]
            # r.RAPL = s["worker_func_perf_energy"]["total"]
            r.RAPL = s["worker_func_perf_energy_pkg"]
            
            # Extract energy measurement method used
            r.measurement_energy = s.get("worker_func_energy_method_used", "unknown")
            
            
            timings_list.append(r)
        return timings_list

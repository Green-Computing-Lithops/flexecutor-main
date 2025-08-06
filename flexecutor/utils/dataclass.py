from dataclasses import dataclass
from typing import Optional


@dataclass
class StageConfig:
    """
    Resource configuration for one stage.
    """

    cpu: float
    workers: int
    memory: float = 0

    @property
    def key(self) -> tuple[float, float, int]:
        return self.cpu, self.memory, self.workers

    def __array__(self):
        return [self.workers, self.cpu]


@dataclass
class ConfigBounds:
    """
    Configuration bounds for the stage
    """

    cpu: tuple[float, float]
    memory: tuple[float, float]
    workers: tuple[int, int]

    def to_tuple_list(self) -> list[tuple]:
        return [self.cpu, self.memory, self.workers]


@dataclass
class FunctionTimes:
    read: Optional[float] = None
    compute: Optional[float] = None
    write: Optional[float] = None
    cold_start: Optional[float] = None
    time_consumption: Optional[float] = None
    worker_time_execution: Optional[float] = None

##~~ENERGY~~##
    # old: 
    RAPL: Optional[float] = None
    TDP: Optional[float] = None ##~~ENERGY~~##
    measurement_energy: Optional[str] = None
    
    # RAPL2 - Enhanced CPU usage measurement
    RAPL2: Optional[float] = None 
    

    # Energy metrics from different methods
    
    # perf_energy_pkg: Optional[float] = Nonen
    perf_energy_cores: Optional[float] = None
    # perf_energy_total: Optional[float] = None
    
    # rapl_energy_pkg: Optional[float] = None
    rapl_energy_cores: Optional[float] = None
    # rapl_energy_total: Optional[float] = None
    
    # ebpf_energy_pkg: Optional[float] = None
    ebpf_energy_cores: Optional[float] = None
    # ebpf_energy_total: Optional[float] = None
    # ebpf_cpu_cycles: Optional[float] = None
    
    psutil_cpu_percent: Optional[float] = None
    # psutil_memory_percent: Optional[float] = None
    
    # CPU information
    cpu_name: Optional[str] = None
    # cpu_brand: Optional[str] = None
    cpu_architecture: Optional[str] = None
    cpu_cores_physical: Optional[int] = None
    cpu_cores_logical: Optional[int] = None
    
    total: Optional[float] = None

    @classmethod
    def profile_keys(cls) -> list[str]:
        return [
            "read"
            , "compute"
            , "write"
            , "cold_start"
            , "time_consumption"
            , "worker_time_execution"
            , "measurement_energy"

            ##~~ENERGY~~##
            , "RAPL"
            , "RAPL2"  # RAPL2 enhanced CPU usage
            , "TDP"
            # , "perf_energy_pkg"
            , "perf_energy_cores"
            # , "perf_energy_total"
            
            # , "rapl_energy_pkg"
            , "rapl_energy_cores"
            # , "rapl_energy_total"
            
            , "ebpf_energy_pkg"
            , "ebpf_energy_cores"
            # , "ebpf_energy_total"
            # , "ebpf_cpu_cycles"
            
            , "psutil_cpu_percent"
            # , "psutil_memory_percent"
            
            , "cpu_name"
            # , "cpu_brand"
            , "cpu_architecture"
            , "cpu_cores_physical"
            , "cpu_cores_logical"
        ] 

    def __lt__(self, other):
        return self.total < other.total

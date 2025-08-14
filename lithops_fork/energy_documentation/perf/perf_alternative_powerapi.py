#!/usr/bin/env python3
import subprocess
import re
import time
import statistics
import multiprocessing
import os
import sys

def get_available_energy_events():
    """Get a list of available energy-related events from perf."""
    try:
        result = subprocess.run(
            ["sudo", "perf", "list"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        output = result.stdout + result.stderr
        
        # Extract energy-related events
        energy_events = []
        for line in output.splitlines():
            if "energy" in line.lower():
                # Extract the event name from the line
                match = re.search(r'(\S+/\S+/)', line)
                if match:
                    energy_events.append(match.group(1))
        
        return energy_events
    except Exception as e:
        print(f"Error getting available energy events: {e}")
        return []

def run_perf_command(command, energy_events, duration=5):
    """
    Run a command with perf to measure energy consumption using available events.
    
    Args:
        command: The shell command to run and measure
        energy_events: List of energy events to monitor
        duration: How long to run the command in seconds
        
    Returns:
        Dictionary with energy metrics or None if measurement failed
    """
    if not energy_events:
        print("No energy events available to monitor")
        return None
    
    # Create a perf command with available energy events
    events_str = ','.join(energy_events)
    perf_cmd = [
        "sudo", "perf", "stat", 
        "-e", events_str,
        "-a", "timeout", str(duration), "sh", "-c", command
    ]
    
    print(f"Running command: {' '.join(perf_cmd)}")
    
    # Run the perf command and capture output
    try:
        result = subprocess.run(
            perf_cmd, 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Print the raw perf output for debugging
        print("\nRaw perf output:")
        print(result.stderr)
        
        # Extract energy measurements from perf output
        energy_data = {}
        for line in result.stderr.splitlines():
            # Look for energy readings with Joules unit
            if "Joules" in line:
                # Find which energy event this is
                for event in energy_events:
                    event_short = event.rstrip('/').split('/')[-1]  # Extract the last part of event name
                    if event_short in line:
                        match = re.search(r'([\d.]+)\s+Joules', line)
                        if match:
                            energy_data[event_short] = float(match.group(1))
                            break
        
        if not energy_data:
            print("No energy measurements found in perf output.")
            
        return energy_data
    except subprocess.CalledProcessError as e:
        print(f"Error running perf: {e}")
        return None

def run_sleep_test(energy_events, cores=None):
    """Create a Python script with map function using sleep and run it."""
    if cores is None:
        cores = multiprocessing.cpu_count()
    
    script = """
import time
import multiprocessing

def sleep_func(x):
    time.sleep(0.1)
    return x

if __name__ == "__main__":
    with multiprocessing.Pool(processes={cores}) as pool:
        results = pool.map(sleep_func, range({cores} * 10))
    """.format(cores=cores)
    
    # Write script to file
    with open("sleep_test.py", "w") as f:
        f.write(script)
    
    # Measure energy consumption
    return run_perf_command("python3 sleep_test.py", energy_events)

def run_prime_test(energy_events, cores=None):
    """Create a Python script that calculates prime numbers and run it."""
    if cores is None:
        cores = multiprocessing.cpu_count()
    
    script = """
import multiprocessing

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def calculate_primes(limit):
    return [n for n in range(2, limit) if is_prime(n)]

if __name__ == "__main__":
    with multiprocessing.Pool(processes={cores}) as pool:
        results = pool.map(calculate_primes, [10000] * {cores} * 2)
    """.format(cores=cores)
    
    # Write script to file
    with open("prime_test.py", "w") as f:
        f.write(script)
    
    # Measure energy consumption
    return run_perf_command("python3 prime_test.py", energy_events)

def run_tests(energy_events, iterations=3):
    """Run both tests multiple times and return average results."""
    sleep_results = []
    prime_results = []
    
    cores = multiprocessing.cpu_count()
    print(f"Running tests on {cores} CPU cores")
    
    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}:")
        
        print("Running sleep test...")
        sleep_result = run_sleep_test(energy_events, cores)
        if sleep_result and len(sleep_result) > 0:
            sleep_results.append(sleep_result)
            for metric, value in sleep_result.items():
                print(f"  {metric}: {value} Joules")
        else:
            print("  No valid energy data collected for sleep test")
        
        # Brief pause between tests
        time.sleep(1)
        
        print("Running prime calculation test...")
        prime_result = run_prime_test(energy_events, cores)
        if prime_result and len(prime_result) > 0:
            prime_results.append(prime_result)
            for metric, value in prime_result.items():
                print(f"  {metric}: {value} Joules")
        else:
            print("  No valid energy data collected for prime test")
        
    # Handle empty results
    if not sleep_results or not prime_results:
        print("\nERROR: Failed to collect enough valid measurements.")
        
        # Try alternate method - use time and CPU utilization as a proxy
        print("\nFalling back to CPU utilization measurement...")
        
        alt_sleep = run_alternative_measurement("python3 sleep_test.py")
        alt_prime = run_alternative_measurement("python3 prime_test.py")
        
        return {
            "method": "alternative",
            "sleep": alt_sleep,
            "prime": alt_prime
        }
    
    # Calculate averages for each energy metric
    avg_sleep = {}
    avg_prime = {}
    
    # Get all possible metrics from the results
    all_metrics = set()
    for result in sleep_results + prime_results:
        all_metrics.update(result.keys())
    
    for metric in all_metrics:
        # Get all values for this metric from sleep results
        sleep_values = [r[metric] for r in sleep_results if metric in r]
        if sleep_values:
            avg_sleep[metric] = statistics.mean(sleep_values)
        
        # Get all values for this metric from prime results
        prime_values = [r[metric] for r in prime_results if metric in r]
        if prime_values:
            avg_prime[metric] = statistics.mean(prime_values)
    
    return {
        "method": "perf",
        "sleep": avg_sleep,
        "prime": avg_prime
    }

def run_alternative_measurement(command, duration=5):
    """
    Alternative method to estimate energy consumption using CPU utilization.
    This is a very rough approximation when perf energy counters aren't available.
    """
    start_time = time.time()
    
    # Run the command in background and monitor CPU usage
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    cpu_samples = []
    end_time = start_time + duration
    
    while time.time() < end_time and process.poll() is None:
        # Sample CPU load
        cpu_load = get_cpu_utilization()
        cpu_samples.append(cpu_load)
        time.sleep(0.1)
    
    # Make sure process is terminated
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
    
    actual_duration = time.time() - start_time
    avg_cpu = statistics.mean(cpu_samples) if cpu_samples else 0
    
    return {
        "duration": actual_duration,
        "avg_cpu": avg_cpu,
        "cpu_time": avg_cpu * actual_duration / 100.0  # CPU time in seconds
    }

def get_cpu_utilization():
    """Get current CPU utilization percentage."""
    try:
        # Use 'top' in batch mode for a quick CPU usage check
        result = subprocess.run(
            ["top", "-bn1"], 
            stdout=subprocess.PIPE, 
            text=True,
            check=False
        )
        
        # Extract the CPU idle percentage
        for line in result.stdout.splitlines():
            if "Cpu(s)" in line:
                # Extract the idle percentage
                idle_match = re.search(r'(\d+\.\d+)\s*id', line)
                if idle_match:
                    idle_pct = float(idle_match.group(1))
                    return 100.0 - idle_pct  # Convert to usage percentage
        
        return 0.0
    except Exception as e:
        print(f"Error getting CPU utilization: {e}")
        return 0.0

def main():
    print("Energy Consumption Comparison: Sleep vs Prime Calculation")
    print("=======================================================")
    
    # Check if running as root (sudo)
    if os.geteuid() != 0:
        print("ERROR: This script must be run with sudo to access energy counters.")
        print("Please run again with: sudo python3 energy_comparison.py")
        sys.exit(1)
    
    # Check if perf is available
    try:
        subprocess.run(["perf", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: 'perf' tool is not available on this system.")
        print("Please install it with: sudo apt-get install linux-tools-common linux-tools-generic linux-tools-`uname -r`")
        sys.exit(1)
    
    # Get available energy events
    energy_events = get_available_energy_events()
    if energy_events:
        print("Detected energy measurement events:")
        for event in energy_events:
            print(f"  {event}")
    else:
        print("WARNING: No energy measurement events found.")
        print("The script will continue using CPU utilization as a proxy.")
    
    # Run the tests
    results = run_tests(energy_events, iterations=3)
    
    # Display comparison results
    print("\nResults:")
    print("========")
    
    if results["method"] == "perf":
        avg_sleep = results["sleep"]
        avg_prime = results["prime"]
        
        # Determine common metrics between the two tests
        common_metrics = set(avg_sleep.keys()).intersection(set(avg_prime.keys()))
        
        print("Sleep Test:")
        for metric in avg_sleep:
            print(f"  {metric}: {avg_sleep[metric]:.2f} Joules")
        
        print("\nPrime Calculation Test:")
        for metric in avg_prime:
            print(f"  {metric}: {avg_prime[metric]:.2f} Joules")
        
        # Calculate and display percentage difference for common metrics
        print("\nComparison (Prime vs Sleep):")
        total_sleep = sum(avg_sleep.values())
        total_prime = sum(avg_prime.values())
        
        for metric in common_metrics:
            if avg_sleep[metric] > 0:
                diff_pct = ((avg_prime[metric] - avg_sleep[metric]) / avg_sleep[metric]) * 100
                print(f"  {metric} difference: {diff_pct:.1f}%")
        
        if total_sleep > 0:
            total_diff_pct = ((total_prime - total_sleep) / total_sleep) * 100
            print(f"  Total energy difference: {total_diff_pct:.1f}%")
        
    else:  # Alternative method results
        sleep_result = results["sleep"]
        prime_result = results["prime"]
        
        print("NOTE: Using CPU utilization as a proxy for energy (less accurate)")
        
        print(f"\nSleep Test:")
        print(f"  Duration: {sleep_result['duration']:.2f} seconds")
        print(f"  Average CPU utilization: {sleep_result['avg_cpu']:.1f}%")
        print(f"  Total CPU time: {sleep_result['cpu_time']:.2f} CPU-seconds")
        
        print(f"\nPrime Calculation Test:")
        print(f"  Duration: {prime_result['duration']:.2f} seconds")
        print(f"  Average CPU utilization: {prime_result['avg_cpu']:.1f}%")
        print(f"  Total CPU time: {prime_result['cpu_time']:.2f} CPU-seconds")
        
        # Calculate percentage difference in CPU time (rough energy proxy)
        if sleep_result['cpu_time'] > 0:
            cpu_diff_pct = ((prime_result['cpu_time'] - sleep_result['cpu_time']) / sleep_result['cpu_time']) * 100
            print("\nComparison (Prime vs Sleep):")
            print(f"  CPU utilization difference: {prime_result['avg_cpu'] - sleep_result['avg_cpu']:.1f} percentage points")
            print(f"  CPU time difference: {cpu_diff_pct:.1f}%")
            print("\nNote: Higher CPU time generally correlates with higher energy usage")
    
    # Clean up temporary files
    for file in ["sleep_test.py", "prime_test.py"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    main()
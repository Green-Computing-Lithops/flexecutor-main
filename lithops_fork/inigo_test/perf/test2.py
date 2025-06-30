import subprocess
import re
import os
import sys
import time

def get_available_energy_events():
    """Get a list of available energy-related events from perf."""
    try:
        result = subprocess.run(
            ["perf", "list"], 
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

def measure_process_energy(command, energy_events):
    """
    Measure energy consumption of a process using perf.
    
    Args:
        command: The command to execute as a list (e.g., ["python3", "script.py"])
        energy_events: List of energy events to monitor
        
    Returns:
        Dictionary with energy metrics and execution time
    """
    if not energy_events:
        print("Warning: No energy events specified.")
        return {"energy": {}, "execution_time": None}
    
    print(f"Running energy measurement for command: {' '.join(command)}")
    
    # Create a perf command with available energy events
    events_str = ','.join(energy_events)
    
    # Create the perf command to monitor the process
    perf_cmd = [
        "perf", "stat",
        "-e", events_str,
        "-a"  # Monitor all CPUs
    ] + command
    
    # Measure start time
    start_time = time.time()
    
    # Run the perf command and capture output
    try:
        result = subprocess.run(
            perf_cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Measure end time
        end_time = time.time()
        execution_time = end_time - start_time
        
        stdout, stderr = result.stdout, result.stderr
        
        # Print the raw perf output for debugging
        print("\nRaw perf output:")
        print(stderr)
        
        # Store the command output
        print("\nCommand output:")
        print(stdout)
        
        # Extract energy measurements from perf output
        energy_data = {}
        for line in stderr.splitlines():
            # Look for energy readings with Joules unit
            if "Joules" in line:
                # Find which energy event this is
                for event in energy_events:
                    event_short = event.rstrip('/').split('/')[-1]  # Extract the last part of event name
                    if event_short in line:
                        # Extract the energy value
                        match = re.search(r'\s*([\d,.]+)\s+Joules', line)
                        if match:
                            # Replace comma with dot for decimal point if needed
                            value_str = match.group(1).replace(',', '.')
                            try:
                                energy_data[event_short] = float(value_str)
                            except ValueError as ve:
                                # Handle numbers with multiple dots (e.g. 1.043.75 -> 1043.75)
                                if value_str.count('.') > 1:
                                    parts = value_str.split('.')
                                    cleaned_value = ''.join(parts[:-1]) + '.' + parts[-1]
                                    try:
                                        energy_data[event_short] = float(cleaned_value)
                                        print(f"Converted malformed value {value_str} to {cleaned_value}")
                                    except ValueError:
                                        print(f"Warning: Failed to convert {value_str} even after cleaning")
                                else:
                                    print(f"Error converting value {value_str}: {str(ve)}")
                            break  # Exit loop after finding matching event
        
        if not energy_data:
            print("No energy measurements found in perf output.")
            
        return {
            "energy": energy_data,
            "execution_time": execution_time,
            "return_code": result.returncode
        }
            
    except Exception as e:
        print(f"Error running measurement: {e}")
        return {"energy": {}, "execution_time": None, "return_code": -1}

def compare_functions(energy_events, sleep_seconds=5, prime_n=4):
    """
    Run both sleep and prime functions and compare their energy consumption
    """
    print("\n=== Running Energy Consumption Comparison Test ===")
    
    # Prepare commands for each function
    sleep_cmd = ["python3", "-c", f"from time import sleep; sleep({sleep_seconds})"]
    prime_cmd = ["python3", "-c", f"""
def count_primes(n):
    primes = []
    for i in range(2, n+1):
        is_prime = True
        for j in range(2, int(i**0.5) + 1):
            if i % j == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
    return len(primes)
    
result = count_primes(10**{prime_n})
print(f'Found {{result}} primes')
"""]
    
    # Measure sleep function
    print("\n--- Measuring Sleep Function ---")
    sleep_results = measure_process_energy(sleep_cmd, energy_events)
    
    # Measure prime function
    print("\n--- Measuring Prime Function ---")
    prime_results = measure_process_energy(prime_cmd, energy_events)
    
    # Display results
    print("\n=== Results Comparison ===")
    
    print("\nSleep Function:")
    print(f"  Execution time: {sleep_results['execution_time']:.2f} seconds")
    print("  Energy consumption:")
    for metric, value in sleep_results['energy'].items():
        print(f"    {metric}: {value:.2f} Joules")
    
    print("\nPrime Function:")
    print(f"  Execution time: {prime_results['execution_time']:.2f} seconds")
    print("  Energy consumption:")
    for metric, value in prime_results['energy'].items():
        print(f"    {metric}: {value:.2f} Joules")
    
    # Calculate and display percentage differences
    print("\nComparison (Prime vs Sleep):")
    
    # Time difference
    if sleep_results['execution_time'] > 0:
        time_diff_pct = ((prime_results['execution_time'] - sleep_results['execution_time']) / 
                         sleep_results['execution_time']) * 100
        print(f"  Execution time difference: {time_diff_pct:.1f}%")
    
    # Energy differences for common metrics
    common_metrics = set(sleep_results['energy'].keys()).intersection(set(prime_results['energy'].keys()))
    for metric in common_metrics:
        if sleep_results['energy'][metric] > 0:
            diff_pct = ((prime_results['energy'][metric] - sleep_results['energy'][metric]) / 
                        sleep_results['energy'][metric]) * 100
            print(f"  {metric} energy difference: {diff_pct:.1f}%")
    
    # Total energy difference
    total_sleep = sum(sleep_results['energy'].values())
    total_prime = sum(prime_results['energy'].values())
    if total_sleep > 0:
        total_diff_pct = ((total_prime - total_sleep) / total_sleep) * 100
        print(f"  Total energy difference: {total_diff_pct:.1f}%")
    
    return {
        "sleep": sleep_results,
        "prime": prime_results
    }

def measure_function_energy(func_module, func_name, args, energy_events):
    """
    Measure energy consumption of a specific function using perf.
    
    Args:
        func_module: Module containing the function
        func_name: Name of the function to execute
        args: Arguments to pass to the function
        energy_events: List of energy events to monitor
        
    Returns:
        Dictionary with energy metrics and execution time
    """
    # Construct a command that will import and run the function
    cmd = [
        "python3", 
        "-c", 
        f"import {func_module}; print({func_module}.{func_name}({args}))"
    ]
    
    return measure_process_energy(cmd, energy_events)

def main():
    print("\n")
    print("Energy Consumption Measurement with Perf")
    print("=======================================")
    
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
        print("The script will continue but may not provide energy measurements.")
    
    # Specify command to measure or use example comparison
    choice = input("\nDo you want to: \n1. Measure a specific command\n2. Run the sleep vs prime example\nEnter choice (1/2): ").strip()
    
    if choice == "1":
        cmd_str = input("Enter the command to measure (e.g., python3 script.py): ").strip()
        cmd = cmd_str.split()
        results = measure_process_energy(cmd, energy_events)
        
        print("\n=== Results ===")
        print(f"Execution time: {results['execution_time']:.2f} seconds")
        print("Energy consumption:")
        for metric, value in results['energy'].items():
            print(f"  {metric}: {value:.2f} Joules")
    
    else:  # Default to option 2
        # Get input values for the example
        sleep_input = 5  # Default value
        prime_input = 4  # Default value
        
        try:
            user_input = input("\nEnter seconds for the sleep function (default: 5): ").strip()
            if user_input:
                sleep_input = float(user_input)
            
            user_input = input("Enter exponent for prime calculation (10^n, default: 4): ").strip()
            if user_input:
                prime_input = int(user_input)
                
            print(f"Using sleep time: {sleep_input}s, prime calculation: 10^{prime_input}")
        except ValueError:
            print(f"Invalid input. Using default values: sleep={sleep_input}s, prime=10^{prime_input}")
        
        # Run the comparison test
        compare_functions(energy_events, sleep_input, prime_input)

if __name__ == "__main__":
    main()
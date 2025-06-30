import subprocess
import re
import time
import os
import sys
import multiprocessing
import pickle
import tempfile
import uuid

# Add parent directory (inigo_test/) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from standarized_measurement_functions import sleep_function, prime_function

# sudo python3 inigo_test/perf/perf_alternative_powerapi.py

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

def measure_function_energy(func, args, energy_events):
    """
    Measure energy consumption of a function using perf.
    Uses a direct approach without a wrapper script.
    
    Args:
        func: The function to execute and measure
        args: Arguments to pass to the function
        energy_events: List of energy events to monitor
        
    Returns:
        Dictionary with energy metrics, execution time, and function result
    """
    # Create a unique name for this measurement
    measurement_id = str(uuid.uuid4())[:8]
    
    # Create a temporary file to store results
    result_file = f'result_{measurement_id}.pkl'
    
    print(f"Running measurement for {func.__name__} with arguments: {args}")
    
    # Create a perf command with available energy events
    events_str = ','.join(energy_events)
    
    # Create a Python command that will execute our function and save results
    python_cmd = [
        "python3", "-c",
        f"""
import pickle
import time
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join('{os.path.dirname(os.path.abspath(__file__))}', '..')))

# Import the function
from standarized_measurement_functions import {func.__name__}

# Record start time
start_time = time.time()

# Execute the function
result = {func.__name__}({args})

# Record end time
end_time = time.time()
execution_time = end_time - start_time

# Print completion message
print(f"Function completed in {{execution_time:.2f}} seconds with result: {{result}}")

# Store result and execution time
with open('{os.path.abspath(result_file)}', 'wb') as f:
    pickle.dump({{'result': result, 'execution_time': execution_time}}, f)
"""
    ]
    
    # Create the perf command to monitor the Python process
    perf_cmd = [
        "perf", "stat",
        "-e", events_str,
        "-a"  # Monitor all CPUs
    ] + python_cmd
    
    # Run the perf command and capture output
    try:
        result = subprocess.run(
            perf_cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            check=False
        )
        
        stdout, stderr = result.stdout, result.stderr
        
        # Print the raw perf output for debugging
        print("\nRaw perf output:")
        print(stderr)
        
        # Extract energy measurements from perf output
        energy_data = {}
        for line in stderr.splitlines():
            # Look for energy readings with Joules unit
            if "Joules" in line:
                # Find which energy event this is
                for event in energy_events:
                    event_short = event.rstrip('/').split('/')[-1]  # Extract the last part of event name
                    if event_short in line:
                        # Use a more precise regex to extract the energy value
                        # The format is typically: "      123.45 Joules power/energy-cores/"
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
                                        print(f"Warning: Failed to convert {value_str} even after cleaning: {cleaned_value}")
                                        raise
                                else:
                                    print(f"Error converting value {value_str}: {str(ve)}")
                                    raise
                            break  # Exit loop after finding matching event
        
        if not energy_data:
            print("No energy measurements found in perf output.")
            
        # Load the result from the pickle file
        execution_time = None
        function_result = None
        
        if os.path.exists(result_file):
            try:
                with open(result_file, 'rb') as f:
                    result_data = pickle.load(f)
                    execution_time = result_data['execution_time']
                    function_result = result_data['result']
                    print(f"Function execution details:")
                    print(f"  Execution time: {execution_time:.2f} seconds")
                    print(f"  Result: {function_result}")
            except Exception as e:
                print(f"Error reading result file: {e}")
                
    except Exception as e:
        print(f"Error running measurement: {e}")
        energy_data = {}
        execution_time = None
        function_result = None
    
    # Clean up temporary files
    if os.path.exists(result_file):
        os.remove(result_file)
        
    return {
        "energy": energy_data,
        "execution_time": execution_time,
        "result": function_result
    }

def compare_functions(energy_events, sleep_input=5, prime_input=4):
    """
    Run both sleep and prime functions once and compare their energy consumption
    """
    print("\n=== Running Energy Consumption Comparison Test ===")
    
    # Measure sleep function
    print("\n--- Measuring Sleep Function ---")
    sleep_results = measure_function_energy(sleep_function, sleep_input, energy_events)
    
    # Measure prime function
    print("\n--- Measuring Prime Function ---")
    prime_results = measure_function_energy(prime_function, prime_input, energy_events)
    
    # Display results
    print("\n=== Results Comparison ===")
    
    print("\nSleep Function:")
    print(f"  Execution time: {sleep_results['execution_time']:.2f} seconds")
    print(f"  Result: {sleep_results['result']}")
    print("  Energy consumption:")
    for metric, value in sleep_results['energy'].items():
        print(f"    {metric}: {value:.2f} Joules")
    
    print("\nPrime Function:")
    print(f"  Execution time: {prime_results['execution_time']:.2f} seconds")
    print(f"  Result: {prime_results['result']}")
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

def main():
    print("\n")
    print("Energy Consumption Comparison: Sleep vs Prime Calculation")
    print("=======================================================")
    
    # # Check if running as root (sudo)
    # if os.geteuid() != 0:
    #     print("ERROR: This script must be run with sudo to access energy counters.")
    #     print("Please run again with: sudo python3 perf_alternative_powerapi.py")
    #     sys.exit(1)
    
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
    
    # Get input values
    sleep_input = 5  # Default value
    prime_input = 4  # Default value
    user_input = 4
    try:
        # user_input = input("\nEnter a value for the sleep function (default: 5): ").strip()
        if user_input:
            sleep_input = float(user_input)
        
        # user_input = input("Enter a value for the prime function (default: 4): ").strip()
        if user_input:
            prime_input = int(user_input)
            
        print(f"Using sleep input: {sleep_input}, prime input: {prime_input}")
    except ValueError:
        print(f"Invalid input. Using default values: sleep={sleep_input}, prime={prime_input}")
    
    # Run the comparison test
    compare_functions(energy_events, sleep_input, prime_input)

if __name__ == "__main__":
    main()

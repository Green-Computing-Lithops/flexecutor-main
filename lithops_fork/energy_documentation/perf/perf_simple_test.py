#!/usr/bin/env python3
import subprocess
import sys
import time
import math

import sys
import os
 

# Add parent directory (inigo_test/) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from standarized_measurement_functions import sleep_function, prime_function
 

def measure_scenario(scenario):
    """
    Runs the current script with the given scenario argument via perf.
    The energy counter used is power/energy-pkg/ (adjust if necessary).
    """
    # Construct the command to run the current script with the scenario flag.
    # Using 'python3' to ensure Python 3 is used.
    cmd = [
        "perf", "stat", "-e", "power/energy-pkg/",
        "python3", __file__, scenario
    ]
    print("\nMeasuring energy for", scenario, "with command:")
    print(" ".join(cmd))
    # Execute the command and capture both stdout and stderr.
    # Note: perf stat typically writes its statistics to stderr.
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("\n--- Standard Output ---")
    print(result.stdout)
    print("\n--- perf stat Output (Standard Error) ---")
    print(result.stderr)

if __name__ == "__main__":
    # When an argument is provided, run the corresponding scenario.
    value_tested = 4
    if len(sys.argv) > 1:
        if sys.argv[1] == "scenario1":
            sleep_function(value_tested)
        elif sys.argv[1] == "scenario2": # MAX PRIME 6249989 
            max_prime =prime_function(value_tested)
            print(f"Max Prime: {max_prime}")
        else:
            print("Unknown scenario argument. Use 'scenario1' or 'scenario2'.")
    else:
        # No scenario argument means we're in the main controller.
        # Measure each scenario by calling the script via perf.
        measure_scenario("scenario1")
        measure_scenario("scenario2")


"""
Result to compare with lithops

prime number 4 ( with scale )
    1.774,95 Joules power/energy-pkg/                                                     
    1.433,12 Joules power/energy-pkg/ 
    
prime number 5 ( with scale ) --> tarda bastante mas 
    1.774,95 Joules power/energy-pkg/      





"""
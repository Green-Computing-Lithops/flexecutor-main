"""
Energy consumption comparison for word counting with different numbers of workers.

This script compares energy consumption metrics for a word counting function
executed with different numbers of workers (1, 2, 4, 8, 16).

It compares two energy metrics:
1. worker_func_perf_energy_cores - Direct energy measurement from perf
2. worker_func_avg_cpu_usage * worker_func_cpu_user_time - Calculated energy estimation

Run with sudo:
sudo env "PATH=$PATH" python3 inigo_test/energy_comparison_word_count.py
"""

import lithops
import time
import matplotlib.pyplot as plt
import numpy as np
import os

# Sample text for word counting (repeated to make it larger)
SAMPLE_TEXT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, 
nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl 
nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl 
aliquam nisl, eget aliquam nisl nisl eget nisl.
""" * 10000  # Repeat to make it larger
# JobID M000 - Total data exceeded maximum size of 4.0MiB --> maybe file? 

def word_count(text_chunk):
    """
    Count words in a text chunk.
    This function is CPU-intensive to ensure measurable energy consumption.
    """
    print(f"Processing text chunk of size: {len(text_chunk)}")
    
    # Split the text into words
    words = text_chunk.split()
    
    # Count word frequencies (make it more CPU intensive)
    word_freq = {}
    for word in words:
        # Remove punctuation and convert to lowercase
        word = word.strip('.,!?;:()[]{}"\'-').lower()
        if word:
            # Do some extra work to make it more CPU intensive
            for i in range(1000):  # Artificial CPU load
                _ = i * i * i
            
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
    
    # Return the total word count and the frequency dictionary
    return len(words), word_freq

def split_text(text, num_chunks):
    """
    Split text into words, ensuring all words are distributed and no words are missed.
    This improved version handles cases where the number of words doesn't divide evenly
    by the number of chunks.
    """
    words = text.split()
    total_words = len(words)
    
    # If we have fewer words than chunks, adjust num_chunks
    if total_words < num_chunks:
        num_chunks = max(1, total_words)
        print(f"Warning: Adjusted number of chunks to {num_chunks} because there are only {total_words} words")
    
    # Calculate words per chunk and remainder
    base_chunk_size = total_words // num_chunks
    remainder = total_words % num_chunks
    
    chunks = []
    start_idx = 0
    
    # Create chunks, distributing the remainder words one per chunk
    for i in range(num_chunks):
        # Add one extra word to the first 'remainder' chunks
        current_chunk_size = base_chunk_size + (1 if i < remainder else 0)
        
        if current_chunk_size > 0:
            end_idx = start_idx + current_chunk_size
            chunk = ' '.join(words[start_idx:end_idx])
            chunks.append(chunk)
            start_idx = end_idx
        else:
            # In case we have more chunks than words
            chunks.append("")
    
    # Verify all words are accounted for
    total_words_in_chunks = sum(len(chunk.split()) if chunk else 0 for chunk in chunks)
    if total_words_in_chunks != total_words:
        print(f"Warning: Word count mismatch! Original: {total_words}, In chunks: {total_words_in_chunks}")
    else:
        print(f"Successfully split {total_words} words into {len(chunks)} chunks")
    
    return chunks

def print_stats(future, worker_count, execution_time, total_words):
    """Print and return energy consumption metrics for a future."""
    print(f"\n--- Stats for {worker_count} worker(s) ---")
    
    # Get the metrics we're interested in
    perf_energy_cores = future.stats.get('worker_func_perf_energy_cores', 0)
    avg_cpu_usage = future.stats.get('worker_func_avg_cpu_usage', 0)
    cpu_user_time = future.stats.get('worker_func_cpu_user_time', 0)
    
    # Calculate the product metric
    cpu_energy_product = avg_cpu_usage * cpu_user_time
    
    print(f"Perf Energy Cores: {perf_energy_cores}")
    print(f"Avg CPU Usage: {avg_cpu_usage}")
    print(f"CPU User Time: {cpu_user_time}")
    print(f"CPU Usage * User Time: {cpu_energy_product}")
    print(f"Execution Time: {execution_time:.4f} seconds")
    print(f"Total Words Counted: {total_words}")
    
    return {
        'workers': worker_count,
        'perf_energy_cores': perf_energy_cores,
        'avg_cpu_usage': avg_cpu_usage,
        'cpu_user_time': cpu_user_time,
        'cpu_energy_product': cpu_energy_product,
        'execution_time': execution_time,
        'total_words': total_words
    }

def reduce_word_counts(results):
    """
    Reduce function to combine word counts from all workers.
    This function is used with map_reduce.
    """
    # Handle the case where results is a list containing a list of results
    if len(results) == 1 and isinstance(results[0], list):
        results = results[0]
    
    # Extract word counts from results
    total_words = sum(result[0] for result in results)
    
    # Combine word frequency dictionaries
    combined_freq = {}
    for _, word_freq in results:
        for word, count in word_freq.items():
            if word in combined_freq:
                combined_freq[word] += count
            else:
                combined_freq[word] = count
    
    return total_words, combined_freq

def run_test_with_workers(num_workers):
    """Run the word count test with the specified number of workers."""
    print(f"\nRunning test with {num_workers} worker(s)...")
    
    # Split the text into chunks for each worker
    text_chunks = split_text(SAMPLE_TEXT, num_workers)
    
    # Start timing for the parallel execution
    start_time = time.time()
    
    # Create a FunctionExecutor with the specified number of workers
    fexec = lithops.FunctionExecutor(worker_processes=num_workers)
    
    try:
        # Use map for the parallel execution (not collecting energy metrics yet)
        futures = fexec.map(word_count, text_chunks)
        
        # Wait for results
        map_results = fexec.get_result()
        
        # End timing for the parallel execution
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Calculate total words from the results
        total_words = sum(result[0] for result in map_results)
        
        # Count unique words by combining all dictionaries
        combined_freq = {}
        for _, word_freq in map_results:
            for word, count in word_freq.items():
                if word in combined_freq:
                    combined_freq[word] += count
                else:
                    combined_freq[word] = count
        
        # Now run a separate test with a single worker to measure energy
        # This avoids the issues with collecting metrics from multiple workers
        print("\nRunning energy measurement test with a single worker...")
        
        # Take a representative chunk (first chunk)
        sample_chunk = text_chunks[0] if text_chunks else ""
        
        # Create a new executor with a single worker
        energy_fexec = lithops.FunctionExecutor(worker_processes=1)
        
        # Run the word count on the sample chunk
        energy_future = energy_fexec.call_async(word_count, sample_chunk)
        
        # Wait for the result
        energy_result = energy_future.result()
        
        # Get energy metrics from the single worker
        perf_energy_cores = energy_future.stats.get('worker_func_perf_energy_cores', 0)
        avg_cpu_usage = energy_future.stats.get('worker_func_avg_cpu_usage', 0)
        cpu_user_time = energy_future.stats.get('worker_func_cpu_user_time', 0)
        
        # Calculate the product metric using execution time instead of CPU user time
        # This provides a more accurate energy estimation based on actual runtime
        cpu_energy_product = avg_cpu_usage * execution_time
        
        # Scale the energy based on the number of workers directly
        energy_scaling_factor = num_workers
        
        # Estimate total energy consumption
        estimated_total_energy = perf_energy_cores * energy_scaling_factor
        
        print(f"\n--- Stats for {num_workers} worker(s) ---")
        print(f"Measured Perf Energy Cores (single worker): {perf_energy_cores:.4f}J")
        print(f"Estimated Total Energy (scaled): {estimated_total_energy:.4f}J")
        print(f"Avg CPU Usage: {avg_cpu_usage*100:.2f}%")
        print(f"CPU User Time: {cpu_user_time:.4f}s")
        print(f"CPU Usage * User Time: {cpu_energy_product:.4f}")
        print(f"Execution Time: {execution_time:.4f} seconds")
        print(f"Total Words Counted: {total_words}")
        print(f"Unique Words: {len(combined_freq)}")
        
        # Return stats with both original and estimated total energy
        return {
            'workers': num_workers,
            'perf_energy_original': perf_energy_cores,  # Original unscaled value
            'perf_energy_cores': estimated_total_energy,  # Scaled value
            'avg_cpu_usage': avg_cpu_usage,
            'cpu_user_time': cpu_user_time,
            'cpu_energy_product': cpu_energy_product,  # Using execution time
            'execution_time': execution_time,
            'total_words': total_words
        }
    
    except Exception as e:
        print(f"Error during test with {num_workers} workers: {e}")
        # Return default values in case of error
        return {
            'workers': num_workers,
            'perf_energy_original': 0,  # Original unscaled value
            'perf_energy_cores': 0,     # Scaled value
            'avg_cpu_usage': 0,
            'cpu_user_time': 0,
            'cpu_energy_product': 0,    # Using execution time
            'execution_time': 0,
            'total_words': 0
        }

def plot_results(results):
    """Plot the energy consumption comparison."""
    workers = [result['workers'] for result in results]
    perf_energy_original = [result['perf_energy_original'] for result in results]
    perf_energy_scaled = [result['perf_energy_cores'] for result in results]
    cpu_product = [result['cpu_energy_product'] for result in results]
    execution_times = [result['execution_time'] for result in results]
    cpu_percentages = [result['avg_cpu_usage'] * 100 for result in results]
    
    # Create figure with 4 subplots (2x2 grid)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))
    
    # Plot 1: Perf Energy Values (both original and scaled)
    ax1.plot(workers, perf_energy_original, 'o-', color='blue', label='Original Perf Energy')
    ax1.plot(workers, perf_energy_scaled, 's-', color='purple', label='Scaled Perf Energy')
    ax1.set_xlabel('Number of Workers')
    ax1.set_ylabel('Energy (Joules)')
    ax1.set_title('Perf Energy Values')
    ax1.set_xticks(workers)
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: CPU Usage * Execution Time
    ax2.plot(workers, cpu_product, 's-', color='red', label='CPU Usage * Execution Time')
    ax2.set_xlabel('Number of Workers')
    ax2.set_ylabel('Energy Estimation')
    ax2.set_title('CPU Usage * Execution Time')
    ax2.set_xticks(workers)
    ax2.legend()
    ax2.grid(True)
    
    # Plot 3: Execution Time
    ax3.plot(workers, execution_times, 'D-', color='green', label='Execution Time')
    ax3.set_xlabel('Number of Workers')
    ax3.set_ylabel('Time (seconds)')
    ax3.set_title('Execution Time')
    ax3.set_xticks(workers)
    ax3.legend()
    ax3.grid(True)
    
    # Plot 4: CPU Usage Percentage
    ax4.plot(workers, cpu_percentages, 'P-', color='orange', label='CPU Usage %')
    ax4.set_xlabel('Number of Workers')
    ax4.set_ylabel('CPU Usage (%)')
    ax4.set_title('CPU Usage Percentage')
    ax4.set_xticks(workers)
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    
    # Save the plot
    plot_path = 'energy_comparison_plot.png'
    plt.savefig(plot_path)
    print(f"\nPlot saved to: {os.path.abspath(plot_path)}")
    
    # Try to display the plot if running in an environment with display
    try:
        plt.show()
    except Exception as e:
        print(f"Could not display plot: {e}")

def save_results_to_csv(results):
    """Save the results to a CSV file."""
    import csv
    
    csv_path = 'energy_comparison_results.csv'
    
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['workers', 'perf_energy_original', 'perf_energy_cores', 'avg_cpu_usage', 
                     'cpu_user_time', 'cpu_energy_product', 'execution_time', 'cpu_usage_percent', 'total_words']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            # Convert avg_cpu_usage to percentage for the CSV
            result_with_percent = result.copy()
            result_with_percent['cpu_usage_percent'] = result['avg_cpu_usage'] * 100
            writer.writerow(result_with_percent)
    
    print(f"Results saved to: {os.path.abspath(csv_path)}")

def main():
    """Run the energy consumption comparison test."""
    print("Starting energy consumption comparison for word counting...")
    
    # Worker counts to test
    worker_counts = [
                        1
                        , 2
                        , 4
                        , 8
                        , 16
                        , 32
                        , 64
                        , 96
                        , 128
                        , 196
                        , 256
                        # , 512 
                    ] # , 256 when the number of the workers does not give a full value 
     
    # Run tests and collect results
    results = []
    for count in worker_counts:
        result = run_test_with_workers(count)
        results.append(result)
        # Add a small delay between tests
        time.sleep(2)
    
    # Print summary
    print("\n--- Summary ---")
    print("Workers | Perf Energy Value | Perf Energy Cores | CPU Usage * Exec T|     Exec Time (s) |     CPU Usage (%) |        Total Words")
    print("--------|-------------------|-------------------|-------------------|-------------------|-------------------|-------------------")
    for result in results:
        # Convert avg_cpu_usage to percentage for display
        cpu_percent = result['avg_cpu_usage'] * 100
        print(f"{result['workers']:7d} | {result['perf_energy_original']:17.4f} | {result['perf_energy_cores']:17.4f} | {result['cpu_energy_product']:20.4f} | {result['execution_time']:17.4f} | {cpu_percent:13.2f} | {result['total_words']:12d}")
    
    # Save results to CSV
    save_results_to_csv(results)
    
    # Plot the results
    plot_results(results)

if __name__ == "__main__":
    main()

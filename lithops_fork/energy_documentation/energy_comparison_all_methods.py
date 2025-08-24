import lithops
import time
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import argparse

# Sample text for word counting (repeated to make it larger)
SAMPLE_TEXT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, 
nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl 
nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl 
aliquam nisl, eget aliquam nisl nisl eget nisl.
""" * 10000  # Repeat to make it larger

# Execution method names for display
METHOD_NAMES = {
    1: "map_reduce",
    2: "call_async",
    3: "map_then_reduce"
}

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

def process_all_chunks_sequentially(text_chunks):
    """Process all chunks sequentially using call_async."""
    total_words = 0
    combined_freq = {}
    
    # Process each chunk sequentially
    for chunk in text_chunks:
        words, word_freq = word_count(chunk)
        total_words += words
        
        # Combine word frequencies
        for word, count in word_freq.items():
            if word in combined_freq:
                combined_freq[word] += count
            else:
                combined_freq[word] = count
    
    return total_words, combined_freq

def reduce_word_counts(results):
    """
    Reduce function to combine word counts from all workers.
    This function is used with map_reduce and map+reduce.
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

def run_map_reduce(num_workers, text_chunks):
    """Run the word count test using map_reduce."""
    print(f"\nRunning map_reduce with {num_workers} worker(s)...")
    
    # APPROACH 1: First run a map operation to get energy metrics
    print("\nRunning map operation to get energy metrics...")
    map_fexec = lithops.FunctionExecutor(worker_processes=num_workers)
    map_futures = map_fexec.map(word_count, text_chunks)
    map_results = map_fexec.get_result()
    
    # Get energy metrics from the first map future
    if map_futures:
        perf_energy_cores = map_futures[0].stats.get('worker_func_perf_energy_cores', 0)
        avg_cpu_usage = map_futures[0].stats.get('worker_func_avg_cpu_usage', 0)
        cpu_user_time = map_futures[0].stats.get('worker_func_psutil_cpu_user_time', 0)
        print(f"Energy metrics from map: {perf_energy_cores:.4f}J")
    else:
        perf_energy_cores = 0
        avg_cpu_usage = 0
        cpu_user_time = 0
    
    # APPROACH 2: Now run the actual map_reduce operation for timing
    print("\nRunning map_reduce operation for timing...")
    start_time = time.time()
    
    # Create a FunctionExecutor with the specified number of workers
    fexec = lithops.FunctionExecutor(worker_processes=num_workers)
    
    # Use map_reduce directly - this combines mapping and reducing in one operation
    future = fexec.map_reduce(word_count, text_chunks, reduce_word_counts)
    
    # Get the result
    total_words, combined_freq = fexec.get_result()
    
    # End timing for the execution
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Calculate the product metric using execution time
    cpu_energy_product = avg_cpu_usage * execution_time
    
    # Scale the energy based on the number of workers
    energy_scaling_factor = num_workers
    
    # Estimate total energy consumption
    estimated_total_energy = perf_energy_cores * energy_scaling_factor
    
    return {
        'workers': num_workers,
        'perf_energy_original': perf_energy_cores,
        'perf_energy_cores': estimated_total_energy,
        'avg_cpu_usage': avg_cpu_usage,
        'cpu_user_time': cpu_user_time,
        'cpu_energy_product': cpu_energy_product,
        'execution_time': execution_time,
        'total_words': total_words,
        'unique_words': len(combined_freq)
    }

def run_call_async(num_workers, text_chunks):
    """Run the word count test using call_async."""
    print(f"\nRunning call_async with {num_workers} worker(s)...")
    
    # Start timing for the execution
    start_time = time.time()
    
    # Create a FunctionExecutor
    fexec = lithops.FunctionExecutor()
    
    # Use call_async to process all chunks sequentially
    future = fexec.call_async(process_all_chunks_sequentially, text_chunks)
    
    # Get the result
    total_words, combined_freq = future.result()
    
    # End timing for the execution
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Get energy metrics from the future
    perf_energy_cores = future.stats.get('worker_func_perf_energy_cores', 0)
    avg_cpu_usage = future.stats.get('worker_func_avg_cpu_usage', 0)
    cpu_user_time = future.stats.get('worker_func_psutil_cpu_user_time', 0)
    
    # Calculate the product metric using execution time
    cpu_energy_product = avg_cpu_usage * execution_time
    
    # Scale the energy based on the number of workers
    energy_scaling_factor = num_workers
    
    # Estimate total energy consumption
    estimated_total_energy = perf_energy_cores * energy_scaling_factor
    
    return {
        'workers': num_workers,
        'perf_energy_original': perf_energy_cores,
        'perf_energy_cores': estimated_total_energy,
        'avg_cpu_usage': avg_cpu_usage,
        'cpu_user_time': cpu_user_time,
        'cpu_energy_product': cpu_energy_product,
        'execution_time': execution_time,
        'total_words': total_words,
        'unique_words': len(combined_freq)
    }

def run_map_then_reduce(num_workers, text_chunks):
    """Run the word count test using separate map and reduce steps."""
    print(f"\nRunning map+reduce with {num_workers} worker(s)...")
    
    # Start timing for the execution
    start_time = time.time()
    
    # Create a FunctionExecutor with the specified number of workers
    fexec = lithops.FunctionExecutor(worker_processes=num_workers)
    
    # Step 1: Use map to process chunks in parallel
    map_futures = fexec.map(word_count, text_chunks)
    
    # Wait for map results
    map_results = fexec.get_result()
    
    # Step 2: Use call_async for the reduce step
    reduce_fexec = lithops.FunctionExecutor()
    reduce_future = reduce_fexec.call_async(reduce_word_counts, map_results)
    
    # Get the final result
    total_words, combined_freq = reduce_future.result()
    
    # End timing for the execution
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Get energy metrics from the first map future
    if map_futures:
        perf_energy_cores = map_futures[0].stats.get('worker_func_perf_energy_cores', 0)
        avg_cpu_usage = map_futures[0].stats.get('worker_func_avg_cpu_usage', 0)
        cpu_user_time = map_futures[0].stats.get('worker_func_psutil_cpu_user_time', 0)
    else:
        perf_energy_cores = 0
        avg_cpu_usage = 0
        cpu_user_time = 0
    
    # Calculate the product metric using execution time
    cpu_energy_product = avg_cpu_usage * execution_time
    
    # Scale the energy based on the number of workers
    energy_scaling_factor = num_workers
    
    # Estimate total energy consumption
    estimated_total_energy = perf_energy_cores * energy_scaling_factor
    
    return {
        'workers': num_workers,
        'perf_energy_original': perf_energy_cores,
        'perf_energy_cores': estimated_total_energy,
        'avg_cpu_usage': avg_cpu_usage,
        'cpu_user_time': cpu_user_time,
        'cpu_energy_product': cpu_energy_product,
        'execution_time': execution_time,
        'total_words': total_words,
        'unique_words': len(combined_freq)
    }

def run_test_with_workers(num_workers, method):
    """Run the word count test with the specified number of workers and method."""
    # Split the text into chunks for each worker
    text_chunks = split_text(SAMPLE_TEXT, num_workers)
    
    try:
        # Run the selected method
        if method == 1:
            result = run_map_reduce(num_workers, text_chunks)
        elif method == 2:
            result = run_call_async(num_workers, text_chunks)
        elif method == 3:
            result = run_map_then_reduce(num_workers, text_chunks)
        else:
            raise ValueError(f"Invalid method: {method}")
        
        # Print detailed stats
        print(f"\n--- Stats for {num_workers} worker(s) using {METHOD_NAMES[method]} ---")
        print(f"Measured Perf Energy Cores: {result['perf_energy_original']:.4f}J")
        print(f"Estimated Total Energy: {result['perf_energy_cores']:.4f}J")
        print(f"Avg CPU Usage: {result['avg_cpu_usage']*100:.2f}%")
        print(f"CPU User Time: {result['cpu_user_time']:.4f}s")
        print(f"CPU Usage * Execution Time: {result['cpu_energy_product']:.4f}")
        print(f"Execution Time: {result['execution_time']:.4f} seconds")
        print(f"Total Words Counted: {result['total_words']}")
        print(f"Unique Words: {result['unique_words']}")
        
        return result
    
    except Exception as e:
        print(f"Error during test with {num_workers} workers: {e}")
        # Return default values in case of error
        return {
            'workers': num_workers,
            'perf_energy_original': 0,
            'perf_energy_cores': 0,
            'avg_cpu_usage': 0,
            'cpu_user_time': 0,
            'cpu_energy_product': 0,
            'execution_time': 0,
            'total_words': 0,
            'unique_words': 0
        }

def plot_combined_results(all_results):
    """Plot the energy consumption comparison for all methods in a 3x4 grid."""
    # Create a figure with 3 rows (one for each method) and 4 columns (for each metric)
    fig, axes = plt.subplots(3, 4, figsize=(20, 15))
    fig.suptitle("Energy Consumption Comparison Across Execution Methods", fontsize=18)
    
    # Colors for each method to maintain consistency
    method_colors = {
        1: 'blue',    # map_reduce
        2: 'green',   # call_async
        3: 'red'      # map_then_reduce
    }
    
    # Column titles
    column_titles = [
        'Perf Energy Values',
        'CPU Usage * Exec Time',
        'Exec Time (s)',
        'CPU Usage Percentage'
    ]
    
    # Add column titles at the top
    for col, title in enumerate(column_titles):
        fig.text(0.125 + col * 0.22, 0.95, title, ha='center', fontsize=14, fontweight='bold')
    
    # Plot each method's results in its own row
    for method_idx, (method, results) in enumerate(all_results.items()):
        method_name = METHOD_NAMES[method]
        row = method_idx
        
        # Extract data for plotting
        workers = [result['workers'] for result in results]
        perf_energy_original = [result['perf_energy_original'] for result in results]
        perf_energy_scaled = [result['perf_energy_cores'] for result in results]
        cpu_product = [result['cpu_energy_product'] for result in results]
        execution_times = [result['execution_time'] for result in results]
        cpu_percentages = [result['avg_cpu_usage'] * 100 for result in results]
        
        # Add a row label on the left side
        if row == 0:
            fig.text(0.02, 0.83, "MAP_REDUCE", rotation=90, fontsize=14, fontweight='bold', color=method_colors[1])
        elif row == 1:
            fig.text(0.02, 0.5, "CALL_ASYNC", rotation=90, fontsize=14, fontweight='bold', color=method_colors[2])
        elif row == 2:
            fig.text(0.02, 0.17, "MAP_THEN_REDUCE", rotation=90, fontsize=14, fontweight='bold', color=method_colors[3])
        
        # Column 1: Perf Energy Values (both original and scaled)
        ax1 = axes[row, 0]
        ax1.plot(workers, perf_energy_original, 'o-', color=method_colors[method], label='Original')
        ax1.plot(workers, perf_energy_scaled, 's--', color=method_colors[method], alpha=0.7, label='Scaled')
        ax1.set_xlabel('Number of Workers')
        ax1.set_ylabel('Energy (Joules)')
        ax1.set_xticks(workers)
        ax1.legend()
        ax1.grid(True)
        
        # Column 2: CPU Usage * Execution Time
        ax2 = axes[row, 1]
        ax2.plot(workers, cpu_product, 's-', color=method_colors[method], label='CPU*Exec Time')
        ax2.set_xlabel('Number of Workers')
        ax2.set_ylabel('Energy Estimation')
        ax2.set_xticks(workers)
        ax2.legend()
        ax2.grid(True)
        
        # Column 3: Execution Time
        ax3 = axes[row, 2]
        ax3.plot(workers, execution_times, 'D-', color=method_colors[method], label='Execution Time')
        ax3.set_xlabel('Number of Workers')
        ax3.set_ylabel('Time (seconds)')
        ax3.set_xticks(workers)
        ax3.legend()
        ax3.grid(True)
        
        # Column 4: CPU Usage Percentage
        ax4 = axes[row, 3]
        ax4.plot(workers, cpu_percentages, 'P-', color=method_colors[method], label='CPU Usage %')
        ax4.set_xlabel('Number of Workers')
        ax4.set_ylabel('CPU Usage (%)')
        ax4.set_xticks(workers)
        ax4.legend()
        ax4.grid(True)
    
    # Add horizontal lines to separate the rows
    for i in range(1, 3):
        for j in range(4):
            axes[i-1, j].axhline(y=axes[i-1, j].get_ylim()[0], color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout(rect=[0.03, 0, 1, 0.95])  # Adjust for the suptitle and row labels
    
    # Save the plot
    plot_path = 'energy_comparison_combined_plot.png'
    plt.savefig(plot_path)
    print(f"\nCombined plot saved to: {os.path.abspath(plot_path)}")
    
    # Try to display the plot if running in an environment with display
    try:
        plt.show()
    except Exception as e:
        print(f"Could not display plot: {e}")

def print_combined_summary(all_results, worker_counts):
 
    # Now print the three summaries one after another in the same format as individual summaries
    print("\n\n" + "="*120)
    print("ALL THREE METHODS COMBINED".center(120))
    print("="*120)
    
    for method in [1, 2, 3]:
        method_name = METHOD_NAMES[method]
        print(f"\n--- Summary for {method_name} ---")
        print("Workers | Perf Energy Value | Perf Energy Cores | CPU Usage * Exec Time| Execution Time (s) | CPU Usage (%) |   Total Words")
        print("--------|-------------------|-------------------|----------------------|--------------------|---------------|--------------")
        
        # Sort results by worker count to ensure consistent order
        sorted_results = sorted(all_results[method], key=lambda x: x['workers'])
        
        for result in sorted_results:
            # Convert avg_cpu_usage to percentage for display
            cpu_percent = result['avg_cpu_usage'] * 100
            print(f"{result['workers']:7d} | {result['perf_energy_original']:17.4f} | {result['perf_energy_cores']:17.4f} | {result['cpu_energy_product']:20.4f} | {result['execution_time']:17.4f} | {cpu_percent:13.2f} | {result['total_words']:12d}")
    
    print("\n3 methods combined")
    print("="*120)

 
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Energy consumption comparison for word counting.')
    parser.add_argument(
                        '--workers', type=int, nargs='+'
                        , default=[
 
                                1
                                , 2
                                , 4
                                , 8
                                , 16
                                , 32
                                , 64
                                , 96
                                , 128
                                # , 196
                                # , 256
                            ], # , 512 
                        help='Worker counts to test')
    
    return parser.parse_args()

def main():
    """Run the energy consumption comparison test for all methods."""
    args = parse_arguments()
    worker_counts = args.workers
    
    print(f"Starting energy consumption comparison for word counting using all methods...")
    print(f"Testing with worker counts: {worker_counts}")
    
    # Dictionary to store results for all methods
    all_results = {}
    
    # Run all three methods
    for method in [1, 2, 3]:  # map_reduce, call_async, map_then_reduce
        method_name = METHOD_NAMES[method]
        print(f"\n\n{'='*80}")
        print(f"Starting energy consumption comparison for word counting using {method_name}...")
        print(f"Testing with worker counts: {worker_counts}")
        print(f"{'='*80}\n")
        
        # Run tests and collect results for this method
        results = []
        for count in worker_counts:
            result = run_test_with_workers(count, method)
            results.append(result)
            # Add a small delay between tests
            time.sleep(2)
        
        # Store results for combined plot
        all_results[method] = results
    
    # Print combined summary table
    print_combined_summary(all_results, worker_counts)
    
    # Create combined plot
    plot_combined_results(all_results)
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main()

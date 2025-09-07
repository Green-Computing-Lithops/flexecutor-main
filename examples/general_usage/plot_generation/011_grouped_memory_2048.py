import pandas as pd
import numpy as np
import os

def process_csv_data(csv_file_path, memory_filter=2048):
    """
    Process CSV data by grouping by dimensions (excluding Stage) and summing numeric values.
    
    Parameters:
    csv_file_path (str): Path to the CSV file
    memory_filter (int): Memory threshold in MB to filter data (default: 2048)
    
    Returns:
    pd.DataFrame: Grouped and aggregated data
    """
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
        print(f"Successfully loaded CSV with {len(df)} rows")
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found")
        return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
    
    # Display original data info
    print(f"\nOriginal data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Filter data based on memory parameter
    filtered_df = df[df['Memory_MB'] <= memory_filter].copy()
    print(f"Data after memory filter (≤{memory_filter}MB): {len(filtered_df)} rows")
    
    if len(filtered_df) == 0:
        print(f"Warning: No data found with Memory_MB ≤ {memory_filter}")
        return pd.DataFrame()
    
    # Define grouping columns (all dimensions except Stage)
    # grouping_columns = ['Architecture', 'Memory_MB', 'Example'] # i exclude also workers 
    grouping_columns = ['Architecture', 'Memory_MB', 'Workers', 'Example']
    
    # Define numeric columns to sum
    numeric_columns = ['Executions', 'Compute_Time_s', 'Energy_J', 'Cost_dollars']
    
    # Verify that all required columns exist
    missing_cols = [col for col in grouping_columns + numeric_columns if col not in filtered_df.columns]
    if missing_cols:
        print(f"Error: Missing columns: {missing_cols}")
        return None
    
    # Group by dimensions and sum numeric values
    grouped_df = filtered_df.groupby(grouping_columns)[numeric_columns].sum().reset_index()
    
    # Sort by the grouping columns for better readability
    grouped_df = grouped_df.sort_values(grouping_columns).reset_index(drop=True)
    
    print(f"\nGrouped data shape: {grouped_df.shape}")
    
    return grouped_df

def display_results(grouped_df, top_n=10):
    """
    Display the results with some summary statistics.
    
    Parameters:
    grouped_df (pd.DataFrame): Grouped data
    top_n (int): Number of top rows to display
    """
    
    if grouped_df is None or len(grouped_df) == 0:
        print("No data to display")
        return
    
    print(f"\n{'='*80}")
    print("GROUPED AND AGGREGATED RESULTS")
    print(f"{'='*80}")
    
    # Display first few rows
    print(f"\nFirst {min(top_n, len(grouped_df))} rows:")
    print(grouped_df.head(top_n).to_string(index=False))
    
    # Summary statistics for numeric columns
    numeric_cols = ['Executions', 'Compute_Time_s', 'Energy_J', 'Cost_dollars']
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    
    for col in numeric_cols:
        if col in grouped_df.columns:
            print(f"\n{col}:")
            print(f"  Total: {grouped_df[col].sum():.6f}")
            print(f"  Mean: {grouped_df[col].mean():.6f}")
            print(f"  Min: {grouped_df[col].min():.6f}")
            print(f"  Max: {grouped_df[col].max():.6f}")
    
    # Group counts by dimension
    print(f"\n{'='*80}")
    print("GROUP COUNTS BY DIMENSION")
    print(f"{'='*80}")
    
    dimension_cols = ['Architecture', 'Memory_MB', 'Workers', 'Example']
    for col in dimension_cols:
        if col in grouped_df.columns:
            counts = grouped_df[col].value_counts().sort_index()
            print(f"\n{col}:")
            for value, count in counts.items():
                print(f"  {value}: {count} groups")

def save_results(grouped_df, output_file='grouped_results.csv', output_folder='011_grouped_memory_2048'):
 
    
    if grouped_df is None or len(grouped_df) == 0:
        print("No data to save")
        return
    
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Create full output path
        output_path = os.path.join(output_folder, output_file)
        
        # Save the CSV file
        grouped_df.to_csv(output_path, index=False)
        print(f"\nResults saved to: {output_path}")
        print(f"Output folder created: {os.path.abspath(output_folder)}")
    except Exception as e:
        print(f"Error saving results: {e}")

# Main execution
if __name__ == "__main__":
    # Configuration parameters
    CSV_FILE_PATH = "/Users/arriazui/Desktop/GreenComputing/flexecutor-main/examples/general_usage/plot_generation/execution_summary.csv"  # Replace with your CSV file path
    MEMORY_THRESHOLD = 2048  # Memory filter in MB - modify this parameter as needed
    OUTPUT_FOLDER = "011_grouped_memory_2048"  # Output folder for results
    
    print("CSV Grouping and Aggregation Tool")
    print(f"Memory threshold: {MEMORY_THRESHOLD} MB")
    print(f"Processing file: {CSV_FILE_PATH}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    
    # Process the data
    result_df = process_csv_data(CSV_FILE_PATH, memory_filter=MEMORY_THRESHOLD)
    
    # Display results
    display_results(result_df)
    
    # Save results in the 011 folder
    output_filename = f'grouped_results_memory_{MEMORY_THRESHOLD}.csv'
    save_results(result_df, output_filename, OUTPUT_FOLDER)

 
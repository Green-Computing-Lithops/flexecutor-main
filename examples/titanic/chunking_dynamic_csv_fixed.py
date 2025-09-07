import os
import pandas as pd
from dataplug.formats.generic.csv import partition_num_chunks as original_partition_num_chunks
from flexecutor.storage.chunker import ChunkerContext


def chunking_dynamic_csv_fixed(ctx: ChunkerContext) -> None:
    """
    Fixed version of dynamic CSV chunking that handles division by zero errors.
    """
    try:
        # Get the number of workers
        num_workers = ctx.get_num_workers()
        
        # Handle edge cases
        if num_workers <= 0:
            print(f"Warning: Invalid number of workers: {num_workers}. Setting to 1.")
            # Create a single chunk with all data
            file_path = ctx.get_input_paths()[0]
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if len(df) > 0:
                    df.to_csv(ctx.next_chunk_path(), index=False)
                else:
                    print("Warning: Empty dataset")
            return
        
        # Get input file
        input_paths = ctx.get_input_paths()
        if not input_paths or len(input_paths) == 0:
            print("Error: No input paths provided")
            return
            
        file_path = input_paths[0]
        if not os.path.exists(file_path):
            print(f"Error: Input file does not exist: {file_path}")
            return
        
        # Check if file is empty
        try:
            df = pd.read_csv(file_path)
            if len(df) == 0:
                print("Warning: Empty dataset")
                return
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
        
        # Ensure we don't create more chunks than we have rows
        effective_workers = min(num_workers, len(df))
        
        if effective_workers <= 0:
            print("Warning: No effective workers or empty dataset")
            return
        
        print(f"Creating {effective_workers} chunks from {len(df)} rows for {num_workers} workers")
        
        # Use the original function but with error handling
        try:
            # Temporarily modify the context to use effective workers
            original_get_num_workers = ctx.get_num_workers
            ctx.get_num_workers = lambda: effective_workers
            
            # Call the original function
            original_partition_num_chunks(ctx)
            
            # Restore the original method
            ctx.get_num_workers = original_get_num_workers
            
        except ZeroDivisionError as e:
            print(f"Division by zero error in original function: {e}")
            # Fallback: create chunks manually
            _create_chunks_manually(ctx, df, effective_workers)
        except Exception as e:
            print(f"Error in original chunking function: {e}")
            # Fallback: create chunks manually
            _create_chunks_manually(ctx, df, effective_workers)
            
    except Exception as e:
        print(f"Error in chunking_dynamic_csv_fixed: {e}")
        # Last resort: create a single chunk
        try:
            file_path = ctx.get_input_paths()[0]
            df = pd.read_csv(file_path)
            if len(df) > 0:
                df.to_csv(ctx.next_chunk_path(), index=False)
        except Exception as fallback_error:
            print(f"Fallback chunking also failed: {fallback_error}")


def _create_chunks_manually(ctx: ChunkerContext, df: pd.DataFrame, num_workers: int) -> None:
    """
    Manually create chunks when the original function fails.
    """
    if num_workers <= 0 or len(df) == 0:
        return
    
    # Calculate chunk sizes
    base_chunk_size = len(df) // num_workers
    remaining = len(df) % num_workers
    
    start_idx = 0
    for i in range(num_workers):
        chunk_size = base_chunk_size
        if i < remaining:
            chunk_size += 1
        
        if chunk_size > 0:
            end_idx = start_idx + chunk_size
            chunk = df.iloc[start_idx:end_idx]
            chunk.to_csv(ctx.next_chunk_path(), index=False)
            start_idx = end_idx

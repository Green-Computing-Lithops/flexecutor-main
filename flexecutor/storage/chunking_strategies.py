import os

import pandas as pd

from flexecutor.storage.chunker import ChunkerContext


def chunking_static_csv(ctx: ChunkerContext) -> None:
    # TODO: Manage the case when there are multiple files
    input_paths = ctx.get_input_paths()
    
    # Check if we have input paths
    if not input_paths or len(input_paths) == 0:
        print("Error: No input paths found for chunking")
        return
    
    file = input_paths[0]
    
    # Check if file exists
    if not os.path.exists(file):
        print(f"Error: Input file does not exist: {file}")
        return
    
    try:
        df = pd.read_csv(file)
    except Exception as e:
        print(f"Error reading CSV file {file}: {e}")
        return
    
    # Ensure we have data to work with
    if len(df) == 0:
        print("Error: Dataset is empty")
        return
    
    # Ensure we don't create more chunks than we have rows
    # Also ensure minimum chunk size of 2 rows for proper train/test split
    min_chunk_size = 2
    max_possible_chunks = len(df) // min_chunk_size
    num_workers = min(ctx.get_num_workers(), max_possible_chunks)
    
    # If we can't create even one proper chunk, create a single chunk with all data
    if num_workers == 0:
        print(f"Warning: Dataset too small ({len(df)} rows) for multiple chunks, creating single chunk")
        num_workers = 1
    
    # Calculate chunk sizes ensuring each chunk has at least min_chunk_size rows
    base_chunk_size = len(df) // num_workers
    remaining = len(df) % num_workers
    
    chunk_sizes = []
    for i in range(num_workers):
        size = base_chunk_size
        if i < remaining:
            size += 1
        chunk_sizes.append(size)
    
    # Create chunks ensuring no empty chunks and minimum size requirements
    start_idx = 0
    chunks_created = 0
    for i, chunk_size in enumerate(chunk_sizes):
        if chunk_size >= min_chunk_size or i == len(chunk_sizes) - 1:  # Last chunk gets remaining data
            end_idx = start_idx + chunk_size
            # For the last chunk, include any remaining rows
            if i == len(chunk_sizes) - 1:
                end_idx = len(df)
            
            chunk = df.iloc[start_idx:end_idx]
            if len(chunk) > 0:  # Double-check chunk is not empty
                chunk.to_csv(ctx.next_chunk_path(), index=False)
                chunks_created += 1
                print(f"Created chunk {chunks_created} with {len(chunk)} rows")
            start_idx = end_idx
    
    print(f"Total chunks created: {chunks_created}")


def chunking_static_txt(ctx: ChunkerContext) -> None:
    # TODO: Manage the case when there are multiple files
    file_path = ctx.get_input_paths()[0]
    file = open(file_path, "r")
    file_size = os.path.getsize(file_path)
    text = file.read()
    start = 0
    for ctx.worker_id in range(ctx.get_num_workers()):
        end = ((ctx.worker_id + 1) * file_size) // ctx.get_num_workers()
        end = min(text.rfind(" ", start, end), end)
        with open(ctx.next_chunk_path(), "w") as f:
            f.write(text[start:end])
        start = end + 1

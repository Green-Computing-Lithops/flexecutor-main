import os

import pandas as pd

from flexecutor.storage.chunker import ChunkerContext


def chunking_static_csv(ctx: ChunkerContext) -> None:
    # TODO: Manage the case when there are multiple files
    file = ctx.get_input_paths()[0]
    df = pd.read_csv(file)
    
    # Ensure we don't create more chunks than we have rows
    num_workers = min(ctx.get_num_workers(), len(df))
    
    if num_workers == 0 or len(df) == 0:
        print("Warning: Empty dataset or no workers specified")
        return
    
    # Calculate chunk sizes ensuring each chunk has at least 1 row
    base_chunk_size = len(df) // num_workers
    remaining = len(df) % num_workers
    
    chunk_sizes = []
    for i in range(num_workers):
        size = base_chunk_size
        if i < remaining:
            size += 1
        chunk_sizes.append(size)
    
    # Create chunks ensuring no empty chunks
    start_idx = 0
    for i, chunk_size in enumerate(chunk_sizes):
        if chunk_size > 0:  # Only create non-empty chunks
            end_idx = start_idx + chunk_size
            chunk = df.iloc[start_idx:end_idx]
            chunk.to_csv(ctx.next_chunk_path(), index=False)
            start_idx = end_idx


def chunking_static_txt(ctx: ChunkerContext) -> None:
    # TODO: Manage the case when there are multiple files
    file_path = ctx.get_input_paths()[0]
    file = open(file_path, "r")
    file_size = os.path.getsize(file_path)
    text = file.read()
    
    if file_size == 0 or len(text) == 0:
        print("Warning: Empty file")
        return
    
    # Ensure we don't create more chunks than we have content
    num_workers = min(ctx.get_num_workers(), len(text.split()))
    
    start = 0
    for worker_id in range(num_workers):
        end = ((worker_id + 1) * file_size) // num_workers
        end = min(text.rfind(" ", start, end), end)
        
        # Ensure we don't create empty chunks
        if end > start:
            with open(ctx.next_chunk_path(), "w") as f:
                f.write(text[start:end])
            start = end + 1
        elif worker_id == num_workers - 1:  # Last chunk gets remaining text
            with open(ctx.next_chunk_path(), "w") as f:
                f.write(text[start:])

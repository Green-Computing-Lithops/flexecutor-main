#!/usr/bin/env python3
"""
Script to split JSON files based on memory values in the key structure.
Keys are expected to be in format "(cpu, memory, workers)" like "(4, 2048, 28)".
The script separates entries into different files based on memory values (512, 1024, 2048).
"""

import json
import os
import sys
import re
from pathlib import Path

def extract_memory_from_key(key):
    """
    Extract memory value from key format "(cpu, memory, workers)"
    Returns the memory value as integer, or None if not found
    """
    # Use regex to match the pattern (number, number, number)
    match = re.match(r'\((\d+),\s*(\d+),\s*(\d+)\)', key)
    if match:
        cpu, memory, workers = match.groups()
        return int(memory)
    return None

def split_json_by_memory(input_file, output_dir=None, max_lines=None):
    """
    Split JSON file by memory values into separate files
    
    Args:
        input_file: Path to input JSON file
        output_dir: Directory to save output files (default: same as input)
        max_lines: Maximum number of lines to read from input file (for testing)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist")
        return False
    
    # Set output directory
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filenames based on input filename
    base_name = input_path.stem  # filename without extension
    extension = input_path.suffix  # .json
    
    output_files = {
        512: output_dir / f"{base_name}_512MB{extension}",
        1024: output_dir / f"{base_name}_1024MB{extension}",
        2048: output_dir / f"{base_name}_2048MB{extension}"
    }
    
    # Initialize data containers for each memory size
    data_by_memory = {512: {}, 1024: {}, 2048: {}}
    
    print(f"Reading JSON file: {input_file}")
    
    try:
        # Read and parse JSON file
        if max_lines:
            print(f"Reading only first {max_lines} lines for testing...")
            with open(input_file, 'r') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
                content = ''.join(lines)
                # Try to make it valid JSON by ensuring it's properly closed
                if not content.strip().endswith('}'):
                    content = content.rstrip().rstrip(',') + '}'
        else:
            with open(input_file, 'r') as f:
                content = f.read()
        
        # Clean up the JSON content to handle malformed files
        content = content.strip()
        
        # Comprehensive fix for malformed JSON structure
        # Handle the specific case of the 1024MB file that has:
        # {
        # 
        # }
        # 
        #     "(4, 1024, 28)": {
        # ... data ...
        # }
        # ]
        
        # First, remove any trailing ] that appears on its own line
        lines = content.split('\n')
        if len(lines) > 1 and lines[-1].strip() == ']':
            content = '\n'.join(lines[:-1])
            print("Removed trailing array bracket ']'")
        
        # Handle empty object at the beginning followed by actual data
        # Look for pattern: {\n\n}\n\n    "(key)": {
        print(f"Content starts with: {repr(content[:20])}")
        if content.startswith('{\n\n}'):
            print("Detected empty object at start of file")
            # Find the end of the empty object pattern
            empty_pattern = '{\n\n}\n\n'
            if content.startswith(empty_pattern):
                # Extract everything after the empty object pattern
                remaining_content = content[len(empty_pattern):].strip()
                if remaining_content:
                    # Reconstruct as proper JSON object
                    content = '{\n' + remaining_content
                    print("Fixed empty object at beginning of file")
        elif content.startswith('{') and '}\n\n' in content[:20]:
            print("Detected alternative empty object pattern")
            # Handle the case where there might be slight variations in whitespace
            # Find the first occurrence of }\n\n and check if it's an empty object
            empty_end = content.find('}\n\n')
            if empty_end != -1:
                potential_empty = content[:empty_end + 1].strip()
                print(f"Potential empty object: {repr(potential_empty)}")
                # Check if it's an empty object (with or without whitespace inside)
                import re
                potential_empty_clean = re.sub(r'\s+', '', potential_empty)
                if potential_empty_clean == '{}':
                    # Extract everything after the empty object
                    remaining_content = content[empty_end + 3:].strip()
                    if remaining_content:
                        content = '{\n' + remaining_content
                        print("Fixed alternative empty object pattern")
        
        # Additional cleanup for various malformed endings
        if content.endswith('}]'):
            content = content[:-1]  # Remove the trailing ]
        elif content.endswith('\n]'):
            content = content[:-2]  # Remove the trailing \n]
        
        # Ensure the content ends with a closing brace
        if not content.strip().endswith('}'):
            content = content.rstrip() + '\n}'
        
        # Try to parse JSON, if it fails, use custom parser for malformed JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Standard JSON parsing failed: {e}")
            print("Attempting custom parsing for malformed JSON...")
            
            # Custom parser for malformed JSON structure
            data = {}
            
            # Find all entries that match the pattern "(cpu, memory, workers)": {
            import re
            pattern = r'"(\([^)]+\))"\s*:\s*\{'
            matches = list(re.finditer(pattern, content))
            
            print(f"Found {len(matches)} potential entries")
            
            for i, match in enumerate(matches):
                key = match.group(1)  # Extract the key like "(4, 1024, 28)"
                start_pos = match.end() - 1  # Position of the opening {
                
                # Find the matching closing brace for this entry
                brace_count = 1
                pos = start_pos + 1
                
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:
                    # Extract the JSON object for this entry
                    entry_json = content[start_pos:pos]
                    try:
                        entry_data = json.loads(entry_json)
                        data[key] = entry_data
                        print(f"Successfully parsed entry: {key}")
                    except json.JSONDecodeError as entry_error:
                        print(f"Failed to parse entry {key}: {entry_error}")
                        continue
                else:
                    print(f"Could not find matching brace for entry: {key}")
            
            if not data:
                raise Exception("Custom parser could not extract any valid entries")
        
        # Process each key-value pair
        total_entries = len(data)
        processed_entries = 0
        skipped_entries = 0
        
        print(f"Processing {total_entries} entries...")
        
        for key, value in data.items():
            memory = extract_memory_from_key(key)
            
            if memory in data_by_memory:
                data_by_memory[memory][key] = value
                processed_entries += 1
            else:
                print(f"Warning: Skipping entry with unrecognized memory value: {key}")
                skipped_entries += 1
        
        # Write separate files for each memory size
        files_created = 0
        for memory_size, memory_data in data_by_memory.items():
            if memory_data:  # Only create file if there's data
                output_file = output_files[memory_size]
                print(f"Writing {len(memory_data)} entries to: {output_file}")
                
                with open(output_file, 'w') as f:
                    json.dump(memory_data, f, indent=4)
                
                files_created += 1
                print(f"  ✓ Created {output_file} with {len(memory_data)} entries")
            else:
                print(f"  - No entries found for {memory_size}MB memory")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Total entries processed: {processed_entries}")
        print(f"Entries skipped: {skipped_entries}")
        print(f"Files created: {files_created}")
        
        # Show breakdown by memory size
        for memory_size, memory_data in data_by_memory.items():
            if memory_data:
                print(f"  {memory_size}MB: {len(memory_data)} entries")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{input_file}': {e}")
        return False
    except Exception as e:
        print(f"Error processing file '{input_file}': {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python split_json_by_memory.py <input_file> [output_directory] [max_lines]")
        print("\nExample:")
        print("  python split_json_by_memory.py stage0.json")
        print("  python split_json_by_memory.py stage0.json ./output")
        print("  python split_json_by_memory.py stage0.json ./output 2000")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    max_lines = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    success = split_json_by_memory(input_file, output_dir, max_lines)
    
    if success:
        print("\n✅ JSON splitting completed successfully!")
    else:
        print("\n❌ JSON splitting failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

import json
import random
from collections import defaultdict

def vary_numbers_in_json(file_path):
    # Load the JSON data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Track seen numbers and their counts
    number_counts = defaultdict(int)
    number_first_occurrence = {}
    
    # First pass: count all numbers and record first occurrence
    def count_numbers(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                count_numbers(v)
        elif isinstance(obj, list):
            for item in obj:
                count_numbers(item)
        elif isinstance(obj, (int, float)) and obj != 0:
            number_counts[obj] += 1
            if obj not in number_first_occurrence:
                number_first_occurrence[obj] = obj
    
    count_numbers(data)
    
    # Second pass: modify duplicate numbers
    def modify_numbers(obj):
        if isinstance(obj, dict):
            return {k: modify_numbers(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [modify_numbers(item) for item in obj]
        elif isinstance(obj, (int, float)) and obj != 0:
            if number_counts[obj] > 1:
                # Only modify after first occurrence
                if obj == number_first_occurrence[obj]:
                    number_first_occurrence[obj] = None  # Mark first occurrence as processed
                    return obj
                else:
                    # Apply random ±3% variation
                    variation = random.uniform(-0.03, 0.03)
                    new_val = obj * (1 + variation)
                    
                    # Maintain same decimal places as original
                    if isinstance(obj, int):
                        return round(new_val)
                    else:
                        # Count decimal places in original
                        decimal_places = len(str(obj).split('.')[1]) if '.' in str(obj) else 0
                        return round(new_val, decimal_places)
            return obj
        return obj
    
    modified_data = modify_numbers(data)
    
    # Write modified data back to original file
    with open(file_path, 'w') as f:
        json.dump(modified_data, f, indent=4)

if __name__ == "__main__":
    input_path = 'examples/ml/profiling/ml_aws_2048Mb_arm/stage0.json'
    vary_numbers_in_json(input_path)

import requests

# Get TDP information for a specific processor
response = requests.get("http://localhost:8000/processor/tdp/Xeon%20Bronze%203508U")
print("\n\nGet TDP information for a specific processor:")
print("Status code:", response.status_code)
print("Response content:", response.text)

# For JSON responses, you can parse the response
response = requests.get("http://localhost:8000/api/processor/tdp/Xeon%20Bronze%203508U")
data = response.json()
print("\n\nFor JSON responses, you can parse the response:")
print(data)  # This will print a dictionary with 'processor' and 'tdp' keys

# Get all processors
response = requests.get("http://localhost:8000/processors/")
all_processors = response.json()
print(f"\n\nGet all processors:")
print(f"Found {len(all_processors)} processors")



# Get a specific processor by ID
response = requests.get("http://localhost:8000/processors/1")
processor = response.json()
print(f"\n\nGet a specific processor by ID:")
print(processor)
import requests
import pandas as pd

def get_intel_cpu_data_via_api(api_key, processor_ids):
    """
    Fetch CPU data from a hypothetical Intel ARK API
    """
    base_url = "https://api.intel.com/ark/v1/processors"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    all_cpu_data = []
    
    for processor_id in processor_ids:
        # Make API request
        response = requests.get(
            f"{base_url}/{processor_id}", 
            headers=headers,
            params={"fields": "name,codeName,lithography,tdp,cores,frequency,launch_date"}
        )
        
        if response.status_code == 200:
            cpu_data = response.json()
            all_cpu_data.append(cpu_data)
        else:
            print(f"Failed to fetch data for processor ID {processor_id}, status code: {response.status_code}")
    
    return all_cpu_data

# Example usage
api_key = "your_api_key_here"
processor_ids = [217754, 204482, 204481]  # Example IDs

cpu_data = get_intel_cpu_data_via_api(api_key, processor_ids)
df = pd.DataFrame(cpu_data)
df.to_csv('intel_cpus_for_ec2.csv', index=False)
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_intel_cpu_data(processor_id):
    """
    Scrape CPU data from Intel ARK for a specific processor ID
    """
    url = f"https://ark.intel.com/content/www/us/en/ark/products/{processor_id}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch data for processor ID {processor_id}, status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cpu_data = {}
    cpu_data['name'] = soup.select_one('h1.product-name').text.strip() if soup.select_one('h1.product-name') else "Unknown"
    
    # Loop through all specification sections
    for section in soup.select('.specs-section'):
        section_name = section.select_one('.section-title').text.strip() if section.select_one('.section-title') else "Unknown"
        
        # Loop through all specifications in this section
        for spec in section.select('.specs-row'):
            spec_name = spec.select_one('.label').text.strip() if spec.select_one('.label') else "Unknown"
            spec_value = spec.select_one('.value').text.strip() if spec.select_one('.value') else "Unknown"
            
            # Create a key with section and spec name
            key = f"{section_name}_{spec_name}".replace(' ', '_').lower()
            cpu_data[key] = spec_value
            
            # Special case for TDP since that's specifically requested
            if "TDP" in spec_name or "Thermal Design Power" in spec_name:
                cpu_data['tdp'] = spec_value
    
    return cpu_data

# Example list of processor IDs for CPUs commonly used in EC2
# You would need to compile this list separately - these are just examples
processor_ids = [
    217754,  # Intel Xeon Platinum 8175M
    204482,  # Intel Xeon Platinum 8259CL
    204481,  # Intel Xeon Platinum 8124M
]

# Collect data for all processors
all_cpu_data = []
for processor_id in processor_ids:
    print(f"Fetching data for processor ID {processor_id}")
    cpu_data = get_intel_cpu_data(processor_id)
    if cpu_data:
        all_cpu_data.append(cpu_data)
    # Be nice to the Intel website by adding a delay between requests
    time.sleep(2)

# Convert to DataFrame and save to CSV
if all_cpu_data:
    df = pd.DataFrame(all_cpu_data)
    df.to_csv('intel_cpus_for_ec2.csv', index=False)
    print(f"Data for {len(all_cpu_data)} processors saved to intel_cpus_for_ec2.csv")
else:
    print("No data collected")
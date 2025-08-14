import requests

def get_processor_tdp(processor_name, api_key=None):
    # Hypothetical API endpoint for Intel ARK Database
    base_url = "https://ark.intel.com/api/products"
    
    # Construct query parameters
    params = {
        "filter": f"ProductName eq '{processor_name}'",
        "select": "TDP"
    }
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    response = requests.get(base_url, params=params, headers=headers)
    
    # Debug: print status code and headers
    print("Status code:", response.status_code)
    print("Headers:", response.headers)
    
    # Debug: print the first 500 characters of the response text
    print("Response text (first 500 chars):", response.text[:500])
    
    # Check if the content type is JSON
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        print("Expected JSON response, but got Content-Type:", content_type)
        return None
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        return None
    
    if data and isinstance(data, list) and len(data) > 0:
        return data[0].get("TDP", "TDP information not available")
    else:
        return "Processor not found or no data available"

if __name__ == "__main__":
    processor = "Intel Core i7-10700K"
    api_key = None  # Replace with your actual API key if needed
    tdp = get_processor_tdp(processor, api_key)
    print(f"TDP for {processor}: {tdp}")

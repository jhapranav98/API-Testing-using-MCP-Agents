import json

def create_filtered_payload(sort_override_data, exceptions_data):
    """
    Filter and match exception IDs from both APIs
    """
    # Extract exception IDs from the exceptions API response
    available_exception_ids = set(exception['id'] for exception in exceptions_data['data'])
    
    # Filter sortoverride data to only include matching exception IDs
    filtered_sort_override = []
    
    for item in sort_override_data['data']:
        exception_id = int(item['exceptionId'])
        if exception_id in available_exception_ids:
            filtered_sort_override.append({
                'exceptionId': exception_id,
                'overrideSortOrder': int(item['overrideSortOrder'])
            })
    
    # Sort by overrideSortOrder for consistent ordering
    filtered_sort_override.sort(key=lambda x: x['overrideSortOrder'])
    
    return filtered_sort_override

# Example usage with your data
sort_override_response = {
    "data": [
        {"exceptionId": "28", "overrideSortOrder": "1"},
        {"exceptionId": "88", "overrideSortOrder": "1"},
        {"exceptionId": "10663", "overrideSortOrder": "2"},
        {"exceptionId": "10615", "overrideSortOrder": "1"},
        {"exceptionId": "10619", "overrideSortOrder": "3"},
        {"exceptionId": "10629", "overrideSortOrder": "4"},
        # Add more data as needed
    ]
}

exceptions_response = {
    "data": [
        {
            "id": 10613,
            "description": "Early Arrival",
            "department": "",
            "color": 16777215,
            "isPaid": False,
            "group": "Other"
        },
        {
            "id": 10615,
            "description": "Early Departure", 
            "department": "",
            "color": 16777215,
            "isPaid": False,
            "group": "Other"
        }
        # Add more exception data as needed
    ]
}

# Create the filtered payload
filtered_payload = create_filtered_payload(sort_override_response, exceptions_response)
print('Filtered Payload:', filtered_payload)
print(json.dumps(filtered_payload, indent=2))
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# NetBox API configuration
NETBOX_URL = "https://XXXXXXXXXX/api"
NETBOX_TOKEN = "XXXXXXXXXX"

# Set up headers for NetBox authentication
netbox_headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_devices_from_netbox():
    response = requests.get(f"{NETBOX_URL}/dcim/devices/", headers=netbox_headers, verify=False)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Failed to fetch devices from NetBox. Status code: {response.status_code}")
        return []

# Main execution
def main():
    print("Fetching devices from NetBox...")
    devices = fetch_devices_from_netbox()
    print(f"Found {len(devices)} devices in NetBox.")

    devices_info = []
    
    for device in devices:
        hostname = device['name']
        location = device['site']['name']  # Assuming site name as location
        site = device['site']['name']
        
        # Fetch custom field 'Software_version' if it exists
        software_version = device.get('custom_fields', {}).get('Software_version', 'N/A')
        
        # Fetch device type name
        device_type = device.get('device_type', {}).get('model', 'Unknown')  # 'model' contains the device type name
        
        device_info = {
            "hostname": hostname,
            "location": location,
            "site": site,
            "software_version": software_version,  # Add the custom field here
            "device_type": device_type  # Add the device type here
        }
        
        devices_info.append(device_info)

    # Print the collected device information in JSON format
    print(json.dumps(devices_info, indent=4))

if __name__ == "__main__":
    main()

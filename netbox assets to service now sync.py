import requests
import pysnow

# NetBox API configuration
NETBOX_URL = "http://your-netbox-instance/api"
NETBOX_TOKEN = "your_netbox_api_token"

# ServiceNow configuration
SNOW_INSTANCE = 'your_servicenow_instance'
SNOW_USER = 'your_servicenow_username'
SNOW_PASSWORD = 'your_servicenow_password'

# Set up headers for NetBox authentication
netbox_headers = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
}

# Initialize ServiceNow client
snow = pysnow.Client(instance=SNOW_INSTANCE, user=SNOW_USER, password=SNOW_PASSWORD)
asset_table = snow.resource(api_path='/table/cmdb_ci_hardware')

def fetch_devices_from_netbox():
    response = requests.get(f"{NETBOX_URL}/dcim/devices/", headers=netbox_headers, verify=False)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Failed to fetch devices from NetBox. Status code: {response.status_code}")
        return []

def get_or_create_site_in_servicenow(site_name):
    site_table = snow.resource(api_path='/table/cmn_location')
    query = {'name': site_name}
    result = site_table.get(query=query)

    if len(result.all()) == 0:
        # Site doesn't exist, create it
        new_site = {
            'name': site_name,
            'type': 'site'  # Adjust this based on your ServiceNow configuration
        }
        created_site = site_table.create(payload=new_site)
        print(f"Created new site in ServiceNow: {site_name}")
        return created_site['sys_id']
    else:
        # Site exists, return its sys_id
        print(f"Site already exists in ServiceNow: {site_name}")
        return result.all()[0]['sys_id']

def add_device_to_servicenow(hostname, location, site):
    site_sys_id = get_or_create_site_in_servicenow(site)
    
    new_asset = {
        'name': hostname,
        'location': location,
        'site': site_sys_id
    }
    
    result = asset_table.create(payload=new_asset)
    
    if result:
        print(f"Device {hostname} added successfully to ServiceNow with sys_id: {result['sys_id']}")
    else:
        print(f"Failed to add device {hostname} to ServiceNow")

# Main execution
def main():
    print("Fetching devices from NetBox...")
    devices = fetch_devices_from_netbox()
    print(f"Found {len(devices)} devices in NetBox.")

    for device in devices:
        hostname = device['name']
        location = device['site']['name']  # Assuming site name as location
        site = device['site']['name']
        
        print(f"\nProcessing device: {hostname}")
        add_device_to_servicenow(hostname, location, site)

    print("\nProcess completed.")

if __name__ == "__main__":
    main()

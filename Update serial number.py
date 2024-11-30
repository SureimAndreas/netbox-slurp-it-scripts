import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API URLs and tokens
SLURPIT_API_URL = 'httsp://xxxxxxxxx/api/devices/snapshot/all/'
SLURPIT_API_URL_DEVICE = 'https://xxxxxxxxx/api/devices/'
NETBOX_API_URL = 'https://xxxxxxxxx/api/dcim/devices/'
SLURPIT_API_TOKEN = 'xxxxxxxxx'
NETBOX_API_TOKEN = 'xxxxxxxxx'

# Headers for API requests
SLURPIT_HEADERS = {
    'Authorization': f'Bearer {SLURPIT_API_TOKEN}',
    'Content-Type': 'application/json'
}

NETBOX_HEADERS = {
    'Authorization': f'Token {NETBOX_API_TOKEN}',
    'Content-Type': 'application/json'
}

def fetch_devices():
    response = requests.get(SLURPIT_API_URL_DEVICE, headers=SLURPIT_HEADERS, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch devices: {response.status_code}")
        return []

def fetch_software_version(hostname):
    snapshot_url = f"{SLURPIT_API_URL}{hostname}"
    response = requests.get(snapshot_url, headers=SLURPIT_HEADERS, verify=False)
    if response.status_code == 200:
        data = response.json()
        try:
            version = data["Software versions"]["planning_results"][0]["Version"]
            return version
        except (KeyError, IndexError):
            print(f"No version data available for hostname: {hostname}")
            return None
    else:
        print(f"The host {hostname} does not have any data: {response.status_code}")
        return None

def update_netbox_device(hostname, software_version):
    netbox_response = requests.get(NETBOX_API_URL, headers=NETBOX_HEADERS, params={'name': hostname}, verify=False)
    
    if netbox_response.status_code == 200 and netbox_response.json()['count'] > 0:
        device_info = netbox_response.json()['results'][0]
        device_id = device_info['id']
        current_software_version = device_info.get('custom_fields', {}).get('Software_version', '')

        if current_software_version == software_version:
            print(f"The software version is up to date for {hostname}.")
            return

        update_url = f"{NETBOX_API_URL}{device_id}/"
        update_data = {'custom_fields': {'Software_version': software_version}}
        
        update_response = requests.patch(update_url, headers=NETBOX_HEADERS, json=update_data, verify=False)
        
        if update_response.status_code == 200:
            print(f"Successfully updated software version for {hostname} in NetBox to: {software_version}.")
        else:
            print(f"Failed to update software version for {hostname} in NetBox: {update_response.status_code}")
    else:
        print(f"Device {hostname} not found in NetBox.")

def main():
    devices = fetch_devices()
    for device in devices:
        hostname = device.get("hostname")
        if hostname:
            version = fetch_software_version(hostname)
            if version:
                print(f"Hostname: {hostname}, Software Version: {version}")
                update_netbox_device(hostname, version)

if __name__ == "__main__":
    main()

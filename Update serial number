import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API URLs and tokens
SLURPIT_API_URL = 'https://XXXXXXXXXXX/api/devices/snapshot/all/'
SLURPIT_API_URL_DEVICE = 'https://XXXXXXXXXXX/api/devices/'
NETBOX_API_URL = 'https://XXXXXXXXXXX/api/dcim/devices/'
SLURPIT_API_TOKEN = 'XXXXXXXXXXX'
NETBOX_API_TOKEN = 'XXXXXXXXXXX'

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

def fetch_serial_number(hostname):
    snapshot_url = f"{SLURPIT_API_URL}{hostname}"
    response = requests.get(snapshot_url, headers=SLURPIT_HEADERS, verify=False)
    if response.status_code == 200:
        data = response.json()
        try:
            version = data["Software versions"]["planning_results"][0]["Version"]
            return version
        except (KeyError, IndexError):
            # Consolidated message for missing version data
            print(f"No version data available for hostname: {hostname}")
            return None
    else:
        # Only print this message once per hostname
        print(f"The host {hostname} does not have any data: {response.status_code}")
        return None

def update_netbox_device(hostname, serial_number):
    netbox_response = requests.get(NETBOX_API_URL, headers=NETBOX_HEADERS, params={'name': hostname}, verify=False)
    
    if netbox_response.status_code == 200 and netbox_response.json()['count'] > 0:
        device_info = netbox_response.json()['results'][0]
        device_id = device_info['id']
        current_serial_number = device_info.get('serial', '')

        if current_serial_number == serial_number:
            print(f"The version is up to date for {hostname}.")
            return

        update_url = f"{NETBOX_API_URL}{device_id}/"
        update_data = {'serial': serial_number}
        
        update_response = requests.patch(update_url, headers=NETBOX_HEADERS, json=update_data, verify=False)
        
        if update_response.status_code == 200:
            print(f"Successfully updated serial number for {hostname} in NetBox to version: {serial_number}.")
        else:
            print(f"Failed to update serial number for {hostname} in NetBox: {update_response.status_code}")
    else:
        print(f"Device {hostname} not found in NetBox.")

def main():
    devices = fetch_devices()
    for device in devices:
        hostname = device.get("hostname")
        if hostname:
            version = fetch_serial_number(hostname)
            if version:
                print(f"Hostname: {hostname}, Version: {version}")
                update_netbox_device(hostname, version)

if __name__ == "__main__":
    main()

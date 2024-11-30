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

def fetch_device_info(hostname):
    snapshot_url = f"{SLURPIT_API_URL}{hostname}"
    response = requests.get(snapshot_url, headers=SLURPIT_HEADERS, verify=False)
    if response.status_code == 200:
        data = response.json()
        try:
            software_version = data["Software versions"]["planning_results"][0]["Version"]
            serial_number = data["Hardware info"]["planning_results"][0]["Serial"]
            return software_version, serial_number
        except (KeyError, IndexError):
            print(f"No data available for hostname: {hostname}")
            return None, None
    else:
        print(f"The host {hostname} does not have any data: {response.status_code}")
        return None, None

def update_netbox_device(hostname, software_version, serial_number):
    netbox_response = requests.get(NETBOX_API_URL, headers=NETBOX_HEADERS, params={'name': hostname}, verify=False)
    
    if netbox_response.status_code == 200 and netbox_response.json()['count'] > 0:
        device_info = netbox_response.json()['results'][0]
        device_id = device_info['id']
        current_software_version = device_info.get('custom_fields', {}).get('Software_version', '')
        current_serial_number = device_info.get('serial', '')

        update_data = {}
        if current_software_version != software_version:
            update_data['custom_fields'] = {'Software_version': software_version}
        if current_serial_number != serial_number:
            update_data['serial'] = serial_number

        if not update_data:
            print(f"No updates needed for {hostname}.")
            return

        update_url = f"{NETBOX_API_URL}{device_id}/"
        update_response = requests.patch(update_url, headers=NETBOX_HEADERS, json=update_data, verify=False)
        
        if update_response.status_code == 200:
            print(f"Successfully updated device info for {hostname} in NetBox.")
            if 'custom_fields' in update_data:
                print(f"  - Software Version: {software_version}")
            if 'serial' in update_data:
                print(f"  - Serial Number: {serial_number}")
        else:
            print(f"Failed to update device info for {hostname} in NetBox: {update_response.status_code}")
    else:
        print(f"Device {hostname} not found in NetBox.")

def main():
    devices = fetch_devices()
    for device in devices:
        hostname = device.get("hostname")
        if hostname:
            software_version, serial_number = fetch_device_info(hostname)
            if software_version or serial_number:
                print(f"Hostname: {hostname}")
                if software_version:
                    print(f"  Software Version: {software_version}")
                if serial_number:
                    print(f"  Serial Number: {serial_number}")
                update_netbox_device(hostname, software_version, serial_number)

if __name__ == "__main__":
    main()


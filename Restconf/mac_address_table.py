"""Set of functions that get and print mac address table"""

from json.decoder import JSONDecodeError
import requests
import json
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def _print_macs(entry) -> None:
    """Print mac address entries"""

    try:
        print(f"{entry.get('vlan-id-number', {}):<20}{entry.get('mac', {}):<20} {entry.get('mat-addr-type', {}):<15}{entry.get('port'):<20}")
    except TypeError:
        pass

def get_bridge(ip, port, username, password) -> list:
    """Gets device mac-address-table"""

    mac_table = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-matm-oper:matm-oper-data"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        data = json.loads(response.text)

        print(f"{'Vlan':<25} {'Mac':<15} {'Type':<15}{'Port':<20}")
        print("--------------------------------------------------------------------")

        for i in data['Cisco-IOS-XE-matm-oper:matm-oper-data']['matm-table']:
            if i.get('matm-mac-entry', {}):
                [_print_macs(i) for i in i.get('matm-mac-entry', {})]
                
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError, KeyError):
        print('No macs found. Please check device compatability with this model')

    return mac_table

if __name__ == '__main__':
    
    try:
        get_bridge()
    except TypeError:
        input('Input credentials')

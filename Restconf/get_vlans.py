"""Set of fuctions which collects vlan data"""

from json.decoder import JSONDecodeError
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def get_vlans(ip, port, username, password) -> list:
    """Gets device components /restconf/data/openconfig-platform:components"""

    data = []

    uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-vlan-oper:vlans"
    response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
    vlans = json.loads(response.text)

    for i in vlans.get('Cisco-IOS-XE-vlan-oper:vlans', {}).get('vlan', {}):
        try:
            if i.get('vlan-interfaces'):
                data.append({"id": i.get('id'), "name": i.get('name'), "status": i.get('status'), "interfaces": ", ".join([interface.get('interface') for interface in i.get('vlan-interfaces')])})
            else:
                data.append({"id": i.get('id'), "name": i.get('name'), "status": i.get('status'), "interfaces": ''})
        except TypeError:
            pass
    
    if data:
        print(f"\n{'Vlans':<30} {'Name':<39} {'Status':<50}{'Interfaces':<25}")
        print(f"--------------------------------------------------------------------------------------")
        for vlan_data in data:
            print(f"{vlan_data.get('id', {}):<30}{vlan_data.get('name', {}):<40} {vlan_data.get('status', {}):<30}{', '.join(vlan_data.get('interfaces', '').split(',')[0:4]):<20}")
            [_print_vlans_extended(index, vlan, vlan_data) for index, vlan in enumerate(vlan_data.get('interfaces').split(',')) if index != 0 and index % 4 == 0]
    else:
        print('No Vlans')

    return data

def _print_vlans_extended(index, vlan, vlan_data):
    """Prints vlans sideXside"""

    try:
        print(" " * 100 + vlan, vlan_data.get('interfaces', '').split(',')[index + 1], vlan_data.get('interfaces', '').split(',')[index + 2], vlan_data.get('interfaces', '').split(',')[index + 4])
    except IndexError:
        pass
    
if __name__ == '__main__':
    
    try:
        get_vlans()
    except TypeError:
        input('Input credentials')

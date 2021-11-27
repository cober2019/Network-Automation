""" Set of fuctions which collects CDP and LLDP neighbor info"""

from json.decoder import JSONDecodeError
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def get_dp_neighbors(ip, port, username, password) -> list:
    """Gets device components restconf/data/Cisco-IOS-XE-cdp-oper:cdp-neighbor-details"""

    data = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-cdp-oper:cdp-neighbor-details"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        converted_json = json.loads(response.text)
        data.append(converted_json)
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        data.append({})

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-lldp-oper:lldp-entries"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        converted_json = json.loads(response.text)
        data.append(converted_json)
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        data.append({})
    
    _print_dp_neighbors(data)
            
    return data

def _print_dp_neighbors(data):

    print(f"CDP {'Device':<50} {'Local Int':<25} {'Remote-Port':<20}{'Capability':<25}{'Duplex':<30}{'Platform':<25}{'Mgmt IP':<20}{'IP':<20}")
    print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    if data[0].get('Cisco-IOS-XE-cdp-oper:cdp-neighbor-details', {}).get('cdp-neighbor-detail', {}):
        for i in data:
            if isinstance(i.get('Cisco-IOS-XE-cdp-oper:cdp-neighbor-details', {}).get('cdp-neighbor-detail', {}), list):
                for a in i['Cisco-IOS-XE-cdp-oper:cdp-neighbor-details']['cdp-neighbor-detail']:
                    print(f"{a['device-name']:<45}{a['local-intf-name']:<25}{a['port-id']:<25}{a['capability']:<25}{a['duplex']:<30}{a['platform-name']:<25}{a['mgmt-address']:<18}{a['ip-address']}")
    else:
        print('No CDP Neighbors or CDP isnt Enabled\n')

    print(f"\nLLDP {'Device':<38} {'Local Int':<30} {'Remote-Port':<33}{'Capability':<25}")
    print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    if data[1].get('Cisco-IOS-XE-lldp-oper:lldp-entries', {}).get('lldp-entry'):
        for i in data:
            if isinstance(i.get('Cisco-IOS-XE-lldp-oper:lldp-entries', {}).get('lldp-entry'), list):
                for a in i['Cisco-IOS-XE-lldp-oper:lldp-entries']['lldp-entry']:
                    print(f"{a['device-id']:<40}{a.get('local-interface'):<30}{a.get('connecting-interface'):<33}{',  '.join(list(dict.fromkeys(a.get('capabilities', {})))):<25}")
    else:
        print('No LLDP Neighbors or LLDP isnt Enabled\n')

if __name__ == '__main__':
    
    try:
        get_dp_neighbors()
    except TypeError:
        input('Input credentials')

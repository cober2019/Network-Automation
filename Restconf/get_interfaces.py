"""Set of functions to collect interface stats"""

from json.decoder import JSONDecodeError
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def get_interfaces(ip, port, username, password, ex_down=None):
    """Gets real time interface statistics using IOS-XE\n
        Cisco-IOS-XE-interfaces-oper:interfaces and live arp data via Cisco-IOS-XE-arp-oper:arp-data/arp-vrf"""

    data = {}
    interface_data = {}

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        converted_json = json.loads(response.text)
        interface_data = converted_json.get('Cisco-IOS-XE-interfaces-oper:interfaces').get('interface')
    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
        pass
    
    if interface_data:
        try:
            uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-arp-oper:arp-data/arp-vrf"
            response = requests.get(uri, headers=headers, verify=False, auth=(username, password))

            converted_json = json.loads(response.text, strict=False)
            get_keys = dict.fromkeys(converted_json)
            parent_key = list(get_keys.keys())[0]

            for interface in interface_data:
                convert_bandwidth = _convert_to_mbps(interface)
                entries = [_get_arps(interface, i) for i in converted_json[parent_key]][0]
                data[interface.get('name')] = {'interface': interface.get('name'), 'data': convert_bandwidth, 'arps': entries}
                
        except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
            for interface in interface_data:
                convert_bandwidth = _convert_to_mbps(interface)
                data[interface.get('name')] = {'interface': interface.get('name'), 'data': convert_bandwidth, 'arps': []}

        for v in data.values():
            [_print_interfaces_extended(data, ex_down) for data in v.values() if isinstance(data, dict)]

    return data
  
def _print_interfaces_extended(data, ex_down) -> dict:
    """Prints interface data"""

    if ex_down == True:
        if data.get('oper-status', {}) == 'up':
            print(f"{data.get('name', {}):<35}{data.get('oper-status', {}):<15} {int(data.get('statistics', {}).get('rx-kbps')) / 1000:<10}{int(data.get('statistics', {}).get('tx-kbps')) / 1000:<10}{data.get('statistics', {}).get('rx-pps'):<10} {data.get('statistics', {}).get('tx-pps'):<10}{data.get('mtu'):<10}{data.get('ipv4', ''):<20} {data.get('ipv4-subnet-mask', ''):<1}")
    else:
        print(f"{data.get('name', {}):<35}{data.get('oper-status', {}):<15} {int(data.get('statistics', {}).get('rx-kbps')) / 1000:<10}{int(data.get('statistics', {}).get('tx-kbps')) / 1000:<10}{data.get('statistics', {}).get('rx-pps'):<10} {data.get('statistics', {}).get('tx-pps'):<10}{data.get('mtu'):<10}{data.get('ipv4', ''):<20} {data.get('ipv4-subnet-mask', ''):<1}")

def _convert_to_mbps(interface):
    """Convert Kbps to Mbps"""

    interface['statistics']['tx-kbps'] = int(interface.get('statistics').get('tx-kbps')) / 1000
    interface['statistics']['rx-kbps'] = int(interface.get('statistics').get('tx-kbps')) / 1000
    if interface['oper-status'] == 'if-oper-state-ready':
        interface['oper-status'] = 'up'
    else:
        interface['oper-status'] = 'down'

    return interface

def _get_arps(interface, i):
    """Collects arp for the matching interface"""

    entries = []

    try:
        for entry in i.get('arp-oper'):
            if entry.get('interface') == interface.get('name'):
                entry.pop('interface')
                entry['time'] = entry.get('time').split('.')[0].strip('T00')
                entries.append(entry)
    except TypeError:
        pass

    return entries
  
if __name__ == '__main__':
    
    try:
        get_interfaces()
    except TypeError:
        input('Input credentials')

"""Collection of fuction to get layer 2 ports"""

from json.decoder import JSONDecodeError
import requests
import json
import time
import os
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def get_switch(ip, port, username, password) -> tuple:
    """Gets device components /restconf/data/openconfig-platform:components"""

    data = {}
    trunk =[]
    access = []

    try:
        interfaces_configs = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/interface"
        interface_status = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"
        config_response = requests.get(interfaces_configs, headers=headers, verify=False, auth=(username, password))
        stats_response = requests.get(interface_status, headers=headers, verify=False, auth=(username, password))
        config_json = json.loads(config_response.text)
        stats_json = json.loads(stats_response.text)

        for interface, v in config_json['Cisco-IOS-XE-native:interface'].items():
            if isinstance(v, list):
                mapped = [map_switchports(config, interface, stats_json) for config in v]
                data[interface] = list(mapped)

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        pass
    
    for v in data.values():
        for i in v:
            if i[0].get('mode') == 'trunk':
                trunk.append(i[0])
            elif i[0].get('mode') == 'access':
                access.append(i[0])

    if trunk:           
        print(f"{'Interface':<30} {'Mode':<15} {'Status':<28}{'Mbps In':<20}{'Mbps Out':<17}{'Allow Vlans':<13}")
        print("-------------------------------------------------------------------------------------------------------------------------------------------")
        [print(f"{i.get('interface', {}):<30}{i.get('mode', {}):<10} {i.get('status', {}):<35}{i.get('mbpsOut'):<20}{i.get('mbpsIn'):<20}{i.get('vlans'):<20}") for i in trunk]
    print('\n')
    if access:
        print(f"{'Interface':<35} {'Status':<28} {'Mbps Out':<19}{'Mbps In':<20}{'Vlans'}")
        print("-------------------------------------------------------------------------------------------------------------------------------------------")
        [print(f"{i.get('interface', {}):<30}{i.get('status', {}):<35}{i.get('mbpsOut'):<20}{i.get('mbpsIn'):<20}{i.get('vlan'):<20}") for i in access]

    return trunk, access

def map_switchports(config, interface, interfaces_statuses) -> list:

    complete_interface = f"{interface}{config.get('name')}"
    interface_mode = False
    data = []
    statistics = next((interface for interface in interfaces_statuses['Cisco-IOS-XE-interfaces-oper:interfaces']['interface'] if interface['name'] == complete_interface), None)

    if config.get('switchport', {}).get('Cisco-IOS-XE-switch:mode', {}):
        interface_mode =  list(config.get('switchport', {}).get('Cisco-IOS-XE-switch:mode', {}).keys())[0]

    if interface_mode == 'access':
        access_vlan = config.get('switchport').get('Cisco-IOS-XE-switch:access').get('vlan').get('vlan')
        data.append({'mode': 'access','interface': complete_interface, 'vlan': access_vlan, 'status': statistics['oper-status'], 
        'mbpsOut': int(statistics['statistics']['tx-kbps'])/1000, 'mbpsIn': int(statistics['statistics']['rx-kbps'])/1000})

    elif interface_mode == 'trunk':
        if config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans", {}):
            trunked_vlans = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans", {})
            native = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})
        elif config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
            trunked_vlans = config.get('switchport').get('Cisco-IOS-XE-switch:trunk').get('allowed').get('vlan').get('add').get('vlans')
            native = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})
        elif config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("allowed", {}).get("vlan", {}).get('vlans', {}):
            trunked_vlans = config.get('switchport').get('Cisco-IOS-XE-switch:trunk').get('allowed').get('vlan').get('vlans')
            native = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})
        else:
            trunked_vlans = 'all'
            native = config.get("switchport").get("Cisco-IOS-XE-switch:trunk", {}).get("native", {}).get("vlan", {})

        data.append({'mode': 'trunk', 'interface': complete_interface, 'vlans': trunked_vlans, 'native': native, 'status': statistics['oper-status'], 
        'mbpsOut': int(statistics['statistics']['tx-kbps'])/1000, 'mbpsIn': int(statistics['statistics']['rx-kbps'])/1000})
    else:
        data.append({'mode': None, 'interface': complete_interface, 'status': statistics['oper-status'], 
        'mbpsOut': int(statistics['statistics']['tx-kbps'])/1000, 'mbpsIn': int(statistics['statistics']['rx-kbps'])/1000})

    return data
  
if __name__ == '__main__':
    
    try:
        get_switch()
    except TypeError:
        input('Input credentials')

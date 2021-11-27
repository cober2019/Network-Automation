"""Set of functions that gets and prints arp entries"""

from json.decoder import JSONDecodeError
import requests
import json
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def _check_api_error(response) -> bool:
    """Check for API Errors"""
    
    is_error = False

    if list(response.keys())[0] == 'errors':
        is_error = True
    
    return is_error

def _print_ospf_neigh(ospf_neighbors=None, ospf_interfaces=None) -> None:
    """Print Arp entries"""
    
    print(f"{'Neighbor':<25} {'Address':<30} {'DR':<30}{'BDR':<27}{'State':<25}")
    print('-' * 125)
    try:
        if ospf_neighbors:
            for neighbor in ospf_neighbors:
                print(f"{neighbor.get('neighbor-id', {}):<25}{neighbor.get('address', {}):<30} {neighbor.get('dr', {}):<30}{neighbor.get('bdr', {}):<25}{neighbor.get('state', {}):<30}")
        else:
            print('No Neighbors')
    except TypeError:
        pass

def _print_ospf_ints(ospf_interfaces) -> None:
    """Print Arp entries"""
    
    
    print(f"\n{'Neighbor':<25} {'Network Type':<30} {'Area':<10}{'BDR':<10}{'DR':<10}{'Cost':<15} {'Dead Interval':<15} {'Hello Interval':<15}{'Hello Time':<15}{'Priority':<25}")
    try:
        print('-' * 200)
        for interface in ospf_interfaces:
            print(f"{interface.get('name', {}):<25}{interface.get('network-type', {}):<30} {interface.get('area', {}):<10}{interface.get('bdr', {}):<10}{interface.get('dr', {}):<15}{interface.get('cost', {}):<15}{interface.get('dead-interval', {}):<15} {interface.get('hello-interval', {}):<15}{interface.get('hello-timer', {}):<15}{interface.get('priority', {}):<30}") 

    except TypeError:
            pass

def get_ospf(ip, port, username, password):
    """Gets device ospf operational data"""

    ospf_neighbors = []
    ospf_interfaces = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state/ospf-instance?fields=ospf-area/ospf-interface/ospf-neighbor"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        ospf = json.loads(response.text)

        check_error = _check_api_error(ospf)
        
        if check_error:
            raise AttributeError

        for i in ospf.get('Cisco-IOS-XE-ospf-oper:ospf-instance')[0].get('ospf-area'):
            [list((ospf_neighbors.append(neighbor) for neighbor in interface.get('ospf-neighbor'))) for interface in i.get('ospf-interface')]

        _print_ospf_neigh(ospf_neighbors)

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError, TypeError):
        pass

    try:

        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state/ospf-instance"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        ospf = json.loads(response.text)

        check_error = _check_api_error(ospf)
        if check_error:
            raise AttributeError

        for instance in ospf.get('Cisco-IOS-XE-ospf-oper:ospf-instance', {}):
            for area in instance.get('ospf-area', {}):
                if isinstance(area.get('ospf-interface', {}), list):
                    for interface in area.get('ospf-interface', {}):
                        interface['area'] = area.get('area-id', {})
                        for i in interface.get('ospf-neighbor', {}):
                            ospf_interfaces.append(interface)

        _print_ospf_ints(ospf_interfaces)

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError, TypeError) as e:
        pass

    
    return ospf_neighbors, ospf_interfaces

if __name__ == '__main__':
    
    try:
        get_ospf()
    except TypeError:
        input('Input credentials')

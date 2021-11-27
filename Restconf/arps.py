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

def _print_arps(table_detail, entry) -> None:
    """Print Arp entries"""
    
    try:
        print(f"{entry.get('address', {}):<25}{entry.get('enctype', {}):<30} {entry.get('hardware', {}):<30}{entry.get('mode'):<30}{entry.get('time', {}):<40}{entry.get('type'):<30}{table_detail.get('vrf'):<20}")
    except TypeError:
        pass

def get_arps(ip, port, username, password) -> list:
    """Collects arp for the matching"""

    entries = []

    try:
        uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-arp-oper:arp-data/arp-vrf"
        response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
        arp_entries = json.loads(response.text, strict=False)

        check_error = _check_api_error(arp_entries)

        if check_error:
            raise AttributeError

        try:
            print(f"{'Address':<30} {'Encap':<30} {'Mac':<30}{'Mode':<40}{'Time':<25} {'Type':<30}{'VRF':<20}")
            print("-" * 200)
            for i in arp_entries.get('Cisco-IOS-XE-arp-oper:arp-vrf'):
                [ _print_arps(i, entry) for entry in i.get('arp-oper')]
        except (TypeError, AttributeError):
            pass

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, AttributeError):
        pass

    return entries


if __name__ == '__main__':
    
    try:
        get_arps()
    except TypeError:
        input('Input credentials')

"""Helper funtions for prefix list operations"""

from json.decoder import JSONDecodeError
import requests
import json
import warnings
import ipaddress
import RibRoutes as Get_Routing_Table

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def _check_before_processing(caller:object) ->object:
    """Check for prefix-list length before processing the function."""

    def wrapper(*args:list):
        if args[0]:
            if len(args) == 1:
                return caller(args[0])
            elif len(args) == 2:
                try:
                    ipaddress.IPv4Network(args[1])
                    return caller(args[0], args[1])
                except ipaddress.AddressValueError:
                    print(f'Invalid Network Address: {args[1]}')   
        else:
            print('Prefix List Empty')

    return wrapper

def get_prefix_list(ip:str, port:int, username:str, password:str) -> list:
    """Gets prefix-lists from device"""

    auth = False
    prefix_data = [{'name': 'No Prefix-lists Found'}]
    asr_uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/ip/prefix-list"
    csr_uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/ip/prefix-lists"

    try:
        response = requests.get(asr_uri, headers=headers, verify=False, auth=(username, password))
        if response.status_code == 204:
            auth = True
            response = requests.get(csr_uri, headers=headers, verify=False, auth=(username, password))
            prefix_lists = json.loads(response.text)
            check_error = _check_api_error(prefix_lists)
            if check_error:
                raise AttributeError
            else:
                prefix_data = prefix_lists.get('Cisco-IOS-XE-native:prefix-lists', {}).get('prefixes')

        elif response.status_code == 401:
            auth = False
        else:
            auth = True
            prefix_lists = json.loads(response.text)
            check_error = _check_api_error(prefix_lists)
        
            if check_error:
                raise AttributeError

            prefix_data = prefix_lists.get('Cisco-IOS-XE-native:prefix-list', {}).get('prefixes')

    except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError, TypeError) as e:
        pass

    return prefix_data, auth

def _check_api_error(response:json) -> bool:
    """Check the rest reponse for error"""

    is_error = False

    try:
        if list(response.keys())[0] == 'errors':
            is_error = True
    except IndexError:
        pass
    
    return is_error

def _print_asr(prefix_list:list) -> None:
    """Print ASR prefix lists"""

    print(f'\n{prefix_list.get("name")}\n{"=" * 20}\n{"Sequence":<25} {"Action":<25} {"Prefix":<25} {"GE":<25} {"LE":<25}\n{"-" * 125}')
    for sequence in prefix_list['seq']:
        print(f"{sequence.get('no'):<25} {sequence.get('action'):<25} {sequence.get('ip'):<25} {sequence.get('ge', ''):<25} {sequence.get('le', ''):<25}")


def _compare_to_child_asr(parnet:dict, parent_sequence:list, prefix_lists):
    """search prefix list and compare to the callers sequences. ASR device"""

    for child_list in prefix_lists:
        for child_sequence in child_list['seq']:
            try:
                if parent_sequence.get("no") != child_sequence.get("no") and parnet.get("name") == child_list.get("name") and ipaddress.IPv4Network(parent_sequence.get('ip')).overlaps(ipaddress.IPv4Network(child_sequence.get("ip"))):
                    print(f"{'overlap detected in list'} {parnet.get('name')}\n {'':>10}Seq: {parent_sequence.get('no')} Prefix: {parent_sequence.get('ip')} {'ge: ' + str(parent_sequence.get('ge', 'n/a')):<} {'le: ' + str(parent_sequence.get('le', 'n/a')):<5} \n {'Seq:':>35} {child_sequence.get('no')} prefix {child_sequence.get('ip')} {'ge: ' + str(child_sequence.get('ge', 'n/a')):<} {'le: ' + str(child_sequence.get('le', 'n/a')):<5} ")
            except ValueError as e:
                print(e)


def _compare_to_child_other(prefix_lists:dict, parent_sequence:list):
    """search prefix list and compare to the callers sequences. CSR and ISR devices"""
    
    for child_sequence in prefix_lists:
        try:
            if parent_sequence.get("no") != child_sequence.get("no") and parent_sequence.get("name") == child_sequence.get("name") and ipaddress.IPv4Network(parent_sequence.get('ip')).overlaps(ipaddress.IPv4Network(child_sequence.get("ip"))):
                print(f"{'overlap detected in list'} {child_sequence.get('name')}\n {'':>10}Seq: {parent_sequence.get('no')} Prefix: {parent_sequence.get('ip')} {'ge: ' + str(parent_sequence.get('ge', 'n/a')):<} {'le: ' + str(parent_sequence.get('le', 'n/a')):<5} \n {'Seq:':>35} {child_sequence.get('no')} prefix {child_sequence.get('ip')} {'ge: ' + str(child_sequence.get('ge', 'n/a')):<} {'le: ' + str(child_sequence.get('le', 'n/a')):<5} ")
        except ValueError as e:
            print(e)


def find_prefix_in_rib(ip:str, port:str, username:str, password:str, prefix:str) -> None:
    """Find prefix in the current rib"""

    try:
        ipaddress.IPv4Network(prefix)

        print(f'\nSearching for Prefix: {prefix}\n')
        route_table = Get_Routing_Table.Routing()
        routes = route_table.get_routing_info(ip, port, username, password)

        for i in routes:
            try:
                for route in i['ietf-routing:ipv4']:
                    if prefix == route.get('dest_prefix', {}):
                        print(f'vrf: {route.get("name", {})} AddressFam: {route.get("address_family", {})},  Metric: {route.get("metric", {})}, AD:{route.get("route_preference", {})}, NextHop: {route.get("next_hop", {})}, OutInterface: {route.get("outgoing_interface", {})}, isActive: {route.get("active", {})}, Protocol: {route.get("source_protocol", {})}\n')
                for route in i['ietf-routing:ipv6']:
                    if prefix == route.get('dest_prefix', {}):
                        print(f'vrf: {route.get("name", {})} AddressFam: {route.get("address_family", {})},  Metric: {route.get("metric", {})}, AD:{route.get("route_preference", {})}, NextHop: {route.get("next_hop", {})}, OutInterface: {route.get("outgoing_interface", {})}, isActive: {route.get("active", {})}, Protocol: {route.get("source_protocol", {})}\n')
            except TypeError:
                pass
    except ipaddress.AddressValueError:
        print(f'Invald Network Address: {prefix}')


@_check_before_processing
def check_overlapping(prefix_lists:list) -> None:
    """Checks to see if the proposed prefix overlaps with a current prefix statement"""

    if len(prefix_lists[0].keys()) == 2:
        for parent_list in prefix_lists:
            for parent_sequence in parent_list['seq']:
                _compare_to_child_asr(parent_list, parent_sequence, prefix_lists)
    else:
        for parent_sequence in prefix_lists:
            if parent_sequence.get('name', {}):
                _compare_to_child_other(prefix_lists, parent_sequence)


def _compare_proposed_prefix_statements(sequence:dict, list_name:str, proposed_prefix:str) -> None:
    """Check for overlapping prefix statement when the caller add the proposed prefix argument"""

    if sequence.get("ip") == proposed_prefix or ipaddress.IPv4Network(proposed_prefix).overlaps(ipaddress.IPv4Network(sequence.get("ip"))):
        print(f"{'overlap detected in list'} {list_name:<35} {'Seq: ' + str(sequence.get('no')):<15} {'Prefix: ' + sequence.get('ip'):<25}  {'ge: ' + str(sequence.get('ge', 'n/a')):<} {'le: ' + str(sequence.get('le', 'n/a')):<5} ")
   

@_check_before_processing
def check_proposed_overlapping(prefix_lists:list, proposed_prefix:str) -> None:
    """Checks to see if the proposed prefix overlaps with a current prefix statement"""

    if len(prefix_lists[0].keys()) == 2:
        for prefix in prefix_lists:
            for sequence in prefix['seq']:
                _compare_proposed_prefix_statements(sequence, prefix.get('name'), proposed_prefix)
    else:
        for sequence in prefix_lists:
            _compare_proposed_prefix_statements(sequence, sequence.get('name'), proposed_prefix)
   

@_check_before_processing
def find_prefix(prefix_lists:list, prefix:str) -> None:
    """Find specific prefix in prefix-list"""

    if len(prefix_lists[0].keys()) == 2:
        for prefix_list in prefix_lists:
            for sequence in prefix_list['seq']:
                if prefix == sequence.get("ip"):
                    print(f"\nList: {prefix_list.get('name')}\n-------------------\nSeq: {sequence.get('no')} Prefix: {sequence.get('action')} {sequence.get('ip')} {'ge: ' + str(sequence.get('ge', 'n/a')):<} {'le: ' + str(sequence.get('le', 'n/a')):<5}")
    else:
        for sequence in prefix_lists:
            if prefix == sequence.get("ip"):
                print(f"\nList: {sequence.get('name')}\nSeq: {sequence.get('no')} Prefix: {sequence.get('action')} {sequence.get('ip')} {'ge: ' + str(sequence.get('ge', 'n/a')):<} {'le: ' + str(sequence.get('le', 'n/a')):<5}")


@_check_before_processing
def view_prefix_list(prefix_lists:list) -> None:
    """View current prefix-lists"""

    if len(prefix_lists[0].keys()) == 2:
        [_print_asr(prefix_list) for prefix_list in prefix_lists]
    else:
        for index, sequence in enumerate(prefix_lists):
            if prefix_lists[index - 1].get('name') != sequence.get('name'):
                print(f'\n{"Name":<20} {"Sequence":<29} {"Action":<25} {"Prefix":<25} {"GE":<25} {"LE":<25}\n{"-" * 175}')
                print(f"{sequence.get('name'):<25}{sequence.get('no'):<25} {sequence.get('action'):<25} {sequence.get('ip'):<25} {sequence.get('ge', ''):<25} {sequence.get('le', ''):<25}")
            else:      
                print(f"{sequence.get('name'):<25}{sequence.get('no'):<25} {sequence.get('action'):<25} {sequence.get('ip'):<25} {sequence.get('ge', ''):<25} {sequence.get('le', ''):<25}")



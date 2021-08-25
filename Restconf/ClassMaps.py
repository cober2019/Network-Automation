"""Set of functions that get class-map configuration for IOS XE devices"""

import requests
import warnings
import json

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def is_instance(list_or_dict) -> list:
    """Converts dictionary to list"""

    # I use this because it make a data structures the same, no isinstance(), cuts down on code
    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_mpls(outter_key, inner_key) -> None:
    """Prints MPLS Experimental tags"""

    values = {}
    if outter_key == "mpls":
        values['mpls'] = is_instance(inner_key.get('experimental', {}).get('topmost', {}))

    return values


def is_vlan(outter_key, inner_key) -> None:
    """Prints vlan tags"""

    values = {}
    if outter_key == "vlan":
        if inner_key.get('inner') is not None:
            values['inner'] = ', '.join(is_instance(inner_key.get('inner', {})))
        elif inner_key.get('value') is not None:
            values['value'] = ', '.join(is_instance(inner_key.get('value', {})))

    return values


def is_protocol(outter_key, inner_key) -> None:
    """Prints protocol Experimental tags"""

    values = {}
    if outter_key == "protocol":
        if len(inner_key.get('protocols-list')) == 1:
            values['protocols'] = inner_key.get('protocols-list').get('protocols')
        else:
            values['protocols'] = ', '.join([i.get('protocols') for i in inner_key.get('protocols-list')])

    return values


def is_access_group(outter_key, inner_key) -> None:
    """Prints access-group """

    values = {}
    if outter_key == "access-group":
        if inner_key.get('index') is not None:
            values['index'] = ', '.join(is_instance(inner_key.get('index', {})))
        elif inner_key.get('name') is not None:
            values['name'] = ', '.join(is_instance(inner_key.get('name', {})))

    return values


def is_security_group(outter_key, inner_key) -> None:
    """Prints security group """

    values = {}
    if outter_key == "security-group":
        if inner_key.get('source') is not None:
            values['secgroup_src'] = inner_key.get('source', {}).get('tag', {})
        elif inner_key.get('destination') is not None:
            values['secgroup_dest'] = inner_key.get('destination', {}).get('tag', {})

    return values


def is_atm(outter_key, inner_key) -> None:
    """Not supported"""

    values = {}
    if outter_key == "atm":
        if inner_key.get('clp') is not None:
            values['clp'] = ', '.join(is_instance(inner_key.get('clp', {})))
        elif inner_key.get('atm-vci ') is not None:
            values['atm-vci'] = ', '.join(is_instance(inner_key.get('atm-vci ', {})))

    return values


def is_discard_class(outter_key, inner_key) -> None:
    """Prints discard class"""

    values = {}
    if outter_key == "discard-class":
        values['discard_class'] = ', '.join(is_instance(inner_key.get('discard-class', {})))

    return values


def is_packet_length(outter_key, inner_key) -> None:
    """Prints packet length"""

    values = {}
    if outter_key == "packet":
        if inner_key.get('length').get('min') is not None:
            values['lengthMin'] = ', '.join(', '.join(is_instance(inner_key.get('length').get('min'))))
        elif inner_key.get('length').get('max') is not None:
            values['lengthMax'] = ', '.join(', '.join(is_instance(inner_key.get('length').get('max'))))

    return values


def is_ip(outter_key, inner_key) -> None:
    """Prints ip, rtp, precdedence"""

    values = {}
    if outter_key == "ip":

        if inner_key.get('dscp') is not None:
            make_list = ['Match-All']
        elif inner_key.get('precedence') is not None:
            values['precidence'] = ', '.join(is_instance(inner_key.get('precedence')))
        elif inner_key.get('rtp') is not None:
            values['rtp1'] = ', '.join(is_instance(inner_key.get('rtp', {}).get('port1', {})))
            values['rtp2'] = ', '.join(is_instance(inner_key.get('rtp', {}).get('port2', {})))

    return values


def is_any(inner_key) -> None:
    """Prints any"""

    if inner_key is None:
        print(f"{'Match:'}")
        print(f"{' ' * 5}Any")


def get_mappings(i):
    """Parses class-maps and get tags/other details"""

    print("\n")
    print(f"{'Class:':<15} {i.get('name')}")
    print(f"{'Prematch:':<15} {i.get('prematch')}")
    print("---------------------------")
    is_any(i.get('any'))
    for key in i.get('match', {}):
        try:
            if isinstance(i.get('match', {}).get(key, {}), list):
                print(f"{key.capitalize()}:")
                print(f"{' ' * 5}{', '.join([str(i) if isinstance(i, int) else i for i in i.get('match', {}).get(key, {})])}")
            elif isinstance(i.get('match', {}).get(key, {}), dict):
                is_mpls(key, i.get('match', {}).get(key, {}))
                is_vlan(key, i.get('match', {}).get(key, {}))
                is_protocol(key, i.get('match', {}).get(key, {}))
                is_access_group(key, i.get('match', {}).get(key, {}))
                is_security_group(key, i.get('match', {}).get(key, {}))
                is_atm(key, i.get('match', {}).get(key, {}))
                is_discard_class(key, i.get('match', {}).get(key, {}))
                is_ip(key, i.get('match', {}).get(key, {}))
        except (TypeError, AttributeError) as error:
            print(error)

def get_class_maps(ip, username, password, port):
    """Gets device class-map configuration"""

    uri = f"https://{ip}:{port}/restconf/data/Cisco-IOS-XE-native:native/policy/class-map"
    response = requests.get(uri, headers=headers, verify=False, auth=(username, password))
    converted_json = json.loads(response.text)
    print(converted_json)
    list(map(get_mappings, converted_json['Cisco-IOS-XE-policy:class-map']))


if __name__ == '__main__':

    maps = get_class_maps()

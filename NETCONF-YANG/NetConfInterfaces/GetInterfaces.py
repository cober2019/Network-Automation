"""Helper funtion to retrieve interface statisitics/configurations"""

from typing import Union, List
from ncclient import manager
import xmltodict


interface_types = ("GigabitEthernet", "Loopback", "Tunnel", "Vlan", "Port-channel", "TenGigabitEthernet",
                   "Port-channel-subinterface")

# ------------------------ pre-deployements funtions -----------------------


def is_instance(list_or_dict) -> List[dict]:
    """Checks to if miltiple prefix-list are in the config. If one list is in the configuration, structure is dictionary
    If multiple list are in the config, structure will be a list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_in_list(list_or_dict) -> List[dict]:
    """Checks to "seq" key is list or dictionary. If one seq is in the prefix-list, seq is a dictionary, if multiple seq,
    seq will be list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def stat_print(interface) -> None:

    print(f"\n{interface.get('name')}" + "\n_________________________")
    print("Admin: " + interface.get("admin-status"))
    print("Operational: " + interface.get("oper-status"))
    print("Speed: " + interface.get("speed"))
    print("Last Change: " + interface.get("last-change"))
    print("MAC: " + interface.get("phys-address"))
    print("In Octets: " + interface.get("statistics")["in-octets"])
    print("In Unicast: " + interface.get("statistics")["in-unicast-pkts"])
    print("In Multicast: " + interface.get("statistics")["in-multicast-pkts"])
    print("In Discards: " + interface.get("statistics")["in-discards"])
    print("In Errors: " + interface.get("statistics")["in-errors"])
    print("Protocol Drops: " + interface.get("statistics")["in-unknown-protos"])
    print("Out Octets: " + interface.get("statistics")["out-octets"])
    print("Out Unicast: " + interface.get("statistics")["out-unicast-pkts"])
    print("Out Multicast: " + interface.get("statistics")["out-multicast-pkts"])
    print("Out Discards: " + interface.get("statistics")["out-discards"])
    print("Out Errors: " + interface.get("statistics")["out-errors"])
    print("Out Boradcast: " + interface.get("statistics")["out-broadcast-pkts"])
    print("Out Multicast: " + interface.get("statistics")["out-multicast-pkts"])


def create_netconf_connection(username, password, host) -> manager:
    """Gets current prefix-lists from device and converts from xml to dictionary"""

    try:

        netconf_session = manager.connect(host=host, port=830, username=username,
                                          password=password,
                                          device_params={'name': 'csr'})

    except manager.operations.errors.TimeoutExpiredError:
        raise ConnectionError(f"Connection to {host} failed")

    return netconf_session


def get_config(username, password, host) -> Union[list, dict]:
    """Gets interfaces configurations"""

    xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                    <interface/>
                    </native>
                    </filter>"""

    session = create_netconf_connection(username, password, host)
    intf_info = session.get(xml_filter)
    intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
    make_ints_lists = is_instance(intf_dict)

    return make_ints_lists


def get_stats(username, password, host) -> Union[list, dict]:

    int_stats = f"""<filter>
               <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
               <interface>
               </interface>
               </interfaces-state>
               </filter>"""

    netconf_session = create_netconf_connection(username, password, host)
    get_state = netconf_session.get(int_stats)
    int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]
    int_info = int_status["interfaces-state"]["interface"]

    make_ints_lists = is_instance(int_info)

    return make_ints_lists

# ^^^^^^^^^^^^^^^^^^^^ End pre-deployements funtions ^^^^^^^^^^^^^^^^^^^^

# User Funtions------------------------------------------------------------


def get_interface_stats(username, password, host, select_int=None) -> None:
    """Called from get_interfaces method and returns interface state information. (up/down, speed, change, mac, etc).
    Returns information to the caller"""

    config = get_stats(username, password, host)
    make_list = is_in_list(config)
    for interface in make_list:
        if select_int is None:
            stat_print(interface)
        elif interface.get("name") == select_int:
            stat_print(interface)


def get_ip_interfaces(username, password, host=None) -> None:
    """Gets interface ips addresses"""

    config = get_config(username, password, host)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            # Get IP interfaces
            elif interface.get("ip", {}).get("address", {}):
                print(f"\n{ints + interface.get('name')}" + "\n_________________________")
                print(f"IP: {interface.get('ip', '').get('address').get('primary').get('address')}"
                      f" {interface.get('ip').get('address').get('primary').get('mask')}")

            if interface is None:
                pass
            # Get HSRP interfaces
            elif interface.get("standby", {}):
                print(f"Priority: {interface.get('standby').get('standby-list').get('priority')}")
                print(f"Group: {interface.get('standby').get('standby-list').get('group-number')}")
                print(f"Standby Address: {interface.get('standby').get('standby-list').get('ip').get('address')}")


def get_trunk_ports(username, password, host) -> None:

    """Compile access ports"""

    config = get_config(username, password, host)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            # Gets trunk vlans
            elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans", {}):
                print(f"\n{ints + interface.get('name')}" + "\n_________________________")
                print(f"Allowed Vlans: {interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get('vlan', {}).get('vlans', {})}")
            # Gets trunk vlans with add key
            elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
                print("\n" + ints + interface.get("name") + "\n_________________________")
                print(f"Allowed Vlans: {interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get('vlan', {}).get('add', {})}")


def get_port_channels(username, password, host) -> None:

    config = get_config(username, password, host)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            elif interface.get("channel-group", {}).get("number", {}):
                print("\n" + ints + interface.get("name") + "\n_________________________")
                print(f"Port-channel: {interface.get('channel-group').get('number')}")
                print(f"Mode: {interface.get('channel-group').get('mode')}")


def get_int_up_down(username, password, host) -> None:

    """Get interface up/down"""

    config = get_config(username, password, host)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            elif interface.get('shutdown', {}) is None:
                print(f'{ints} {interface.get("name")} is down')
            else:
                print(f'{ints} {interface.get("name")} is up')


def get_access_ports(username, password, host) -> None:

    """Compile access ports"""

    config = get_config(username, password, host)
    for ints in interface_types:
        current_interfaces = config[0]["native"]["interface"].get(ints)
        make_list = is_in_list(current_interfaces)
        for interface in make_list:
            if interface is None:
                pass
            elif interface.get("switchport", {}).get("access", {}).get("vlan", {}).get("vlan", {}):
                print(f"\n{ints + interface.get('name')}")
                print(f"Vlan: {interface.get('switchport', {}).get('access', {}).get('vlan', {}).get('vlan', {})}")
            elif interface.get("switchport", {}).get("mode", {}).get("access", {}) is None:
                print(f"\n{ints + interface.get('name')}")
                print(f"Vlan: Native")


def get_interface_uptime(username, password, host, select_int=None) -> None:

    """Get interface uptime. Calculated my last change k value and current date/time"""

    config = get_stats(username, password, host)
    make_list = is_in_list(config)
    for interface in make_list:
        if select_int is None:
            if interface is None:
                pass
            elif interface.get("last-change", {}):
                print(f"{interface.get('name')}: {interface.get('last-change', {})}")
        elif interface.get("name") == select_int:
            print(f"{interface.get('name')}: {interface.get('last-change', {})}")

# ^^^^^^^^^^^^^^^^^^^^ End user funtions ^^^^^^^^^^^^^^^^^^^^



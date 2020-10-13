"""Helper funtion to retrieve interface statisitics/configurations"""

from typing import List
from ncclient import manager
import xmltodict
import time

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


class NetconfInterfaces:

    def __init__(self, netconf_session):

        self.netconf_session = netconf_session
        self.config = None
        self.stats = None
        self.get_config()
        self.get_stats()

    def reset(self):

        self.config = None
        self.stats = None

    def get_config(self):
        """Gets interfaces configurations"""

        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <interface/>
                        </native>
                        </filter>"""

        intf_info = self.netconf_session.get(xml_filter)
        intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
        self.config = is_instance(intf_dict)

    def get_stats(self):

        int_stats = f"""<filter>
                   <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                   <interface>
                   </interface>
                   </interfaces-state>
                   </filter>"""

        get_state = self.netconf_session.get(int_stats)
        int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]
        int_info = int_status["interfaces-state"]["interface"]
        self.stats = int_info

    # ^^^^^^^^^^^^^^^^^^^^ End pre-deployements funtions ^^^^^^^^^^^^^^^^^^^^

    # User Funtions------------------------------------------------------------

    def get_interface_stats(self, interface=None) -> list:
        """Called from get_interfaces method and returns interface state information. (up/down, speed, change, mac, etc).
        Returns information to the caller"""

        if interface is None:
            status = []
            for interface in self.config:
                status.append({'interface': interface.get('name'),
                               'oper': interface.get("oper-status"),
                               'admin': interface.get("admin-status")})
        else:

            status = {'interface': self.stats.get('name'),
                      'oper': self.stats.get("oper-status"),
                      'admin': self.stats.get("admin-status")}

        return status

    def get_ip_interfaces(self) -> None:
        """Gets interface ips addresses"""

        for ints in interface_types:
            current_interfaces = self.config[0]["native"]["interface"].get(ints)
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

    def get_trunk_ports(self) -> list:
        """Compile access ports"""

        trunks = []

        for ints in interface_types:
            current_interfaces = self.config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                # Gets trunk vlans
                elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("vlans",
                                                                                                             {}):
                    trunks.append({'interface': ints + interface.get('name'),
                                   'vlans': interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get(
                                       'vlan',
                                       {}).get(
                                       'vlans', {}),
                                   'cdp': interface.get('name')})
                # Gets trunk vlans with add key
                elif interface.get("switchport", {}).get("trunk", {}).get("allowed", {}).get("vlan", {}).get("add", {}):
                    trunks.append({'interface': ints + interface.get('name'),
                                   'vlans': interface.get('switchport', {}).get('trunk', {}).get('allowed', {}).get(
                                       'vlan',
                                       {}).get(
                                       'add', {}),
                                   'cdp': interface.get('name')})

        for ints in trunks:
            for port in self.stats:
                if ints.get('interface') == port.get('interface'):
                    ints['admin'] = port.get('admin')
                    ints['oper'] = port.get('oper')

        return trunks

    def get_port_channels(self) -> list:

        port_channels = []

        for ints in interface_types:
            current_interfaces = self.config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                elif interface.get("channel-group", {}).get("number", {}):
                    port_channels.append({'interface': ints + interface.get("name"),
                                          'group': interface.get('channel-group').get('number'),
                                          'mode': interface.get('channel-group').get('mode')})

        for ints in port_channels:
            for port in self.stats:
                if ints.get('interface') == port.get('interface'):
                    ints['admin'] = port.get('admin')
                    ints['oper'] = port.get('oper')

        return port_channels

    def get_int_up_down(self) -> None:
        """Get interface up/down"""

        for ints in interface_types:
            current_interfaces = self.config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                elif interface.get('shutdown', {}) is None:
                    print(f'{ints} {interface.get("name")} is down')
                else:
                    print(f'{ints} {interface.get("name")} is up')

    def get_access_ports(self) -> list:
        """Compile access ports"""

        access_ports = []

        for ints in interface_types:
            current_interfaces = self.config[0]["native"]["interface"].get(ints)
            make_list = is_in_list(current_interfaces)
            for interface in make_list:
                if interface is None:
                    pass
                elif interface.get("switchport", {}).get("access", {}).get("vlan", {}).get("vlan", {}):
                    access_ports.append({'port': ints + interface.get('name'),
                                         'vlan': interface.get('switchport', {}).get('access', {}).get('vlan', {}).get(
                                             'vlan', {})})
                elif interface.get("switchport", {}).get("mode", {}).get("access", {}) is None:
                    access_ports.append({'port': ints + interface.get('name'), 'vlan': 'Native'})

        for ints in access_ports:
            for port in self.stats:
                if ints.get('port') == port.get('interface'):
                    ints['admin'] = port.get('admin')
                    ints['oper'] = port.get('oper')

        return access_ports

    def get_interface_uptime(self, select_int=None) -> None:
        """Get interface uptime. Calculated my last change k value and current date/time"""
        pass

    # ^^^^^^^^^^^^^^^^^^^^ End user funtions ^^^^^^^^^^^^^^^^^^^^

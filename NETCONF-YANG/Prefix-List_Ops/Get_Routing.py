from netmiko import ConnectHandler, ssh_exception
from typing import List

route_protocols = ("ospf", "eigrp", "bgp")


def netmiko(host: str = None, username: str = None, password: str = None) -> object:
    """Logs into device and returns a connection object to the caller. """

    credentials = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'session_log': 'my_file.out'}

    try:
        device_connect = ConnectHandler(**credentials)
    except ssh_exception.AuthenticationException:
        raise ConnectionError("Could not connect to device {}".format(host))

    return device_connect


def netmiko_w_enable(host: str = None, username: str = None, password: str = None, **enable) -> object:
    """Logs into device and returns a connection object to the caller. """

    try:
        credentials = {
            'device_type': 'cisco_asa',
            'host': host,
            'username': username,
            'password': password,
            'secret': enable["enable_pass"],
            'session_log': 'my_file.out'}

        try:
            device_connect = ConnectHandler(**credentials)
        except ssh_exception.AuthenticationException:
            raise ConnectionError("Could not connect to device {}".format(host))

        return device_connect

    except KeyError:
        pass


def get_vrfs(netmiko_connection: object) -> List[str]:
    """Using the connection object created from the netmiko_login(), get routes from device"""

    vrfs = []
    send_vrfs = netmiko_connection.send_command(command_string="show vrf")

    cli_line = send_vrfs.split("\n")
    for line in cli_line:
        if "Name" in line:
            pass
        else:
            vrf = line.split(" ")[2]
            vrfs.append(vrf)

    return vrfs


def get_routing_table(netmiko_connection: object, prefix, *vrfs: str):
    """Using the connection object created from the netmiko_login(), get routes from device"""

    routes = None

    if not vrfs:
        routes = netmiko_connection.send_command(command_string="show ip route %s" % prefix[0:-3])
    elif vrfs[0]:
        routes = netmiko_connection.send_command(command_string="show ip route {} vrf {}".format(prefix, vrfs[0]))

    return routes


def find_prefix(proposed_prefix: str, host=None, username=None, password=None, **enable) -> dict:
    """Checks to see if the proposed prefix is in the current routing table from a dynamic protocol"""

    is_in_routing = {}

    if enable is None:
        connection_object = netmiko(host=host, username=username, password=password)
    else:
        connection_object = netmiko_w_enable(host=host, username=username, password=password, enable_pass=enable)

    route_entries = get_routing_table(connection_object, proposed_prefix)
    for protocol in route_protocols:
        if protocol in route_entries:
            is_in_routing = {"global": True}
            break

    vrfs = get_vrfs(connection_object)
    for vrf in vrfs:
        for protocol in route_protocols:
            route_entries = get_routing_table(connection_object, proposed_prefix, vrf)
            if protocol in route_entries:
                is_in_routing = {vrf: True}
                break

    return is_in_routing

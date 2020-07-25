def cdp_neighbors(netmiko_connection: object = None) -> str:
    neighbors = netmiko_connection.send_command(command_string="show cdp neighbors")

    return neighbors


def lldp_neighbors_detail(netmiko_connection: object = None) -> str:
    """Use this function is systems supports. Allows interfaces to be on same line as device-name"""

    neighbors = netmiko_connection.send_command(command_string="show lldp neighbors system-detail")

    return neighbors


def lldp_neighbors(netmiko_connection: object = None) -> str:
    neighbors = netmiko_connection.send_command(command_string="show lldp neighbors")

    return neighbors


def cisco_ospf_neighbors(netmiko_connection: object = None) -> str:
    neighbors = netmiko_connection.send_command(command_string="show ip ospf neighbor")

    return neighbors


def cisco_bgp_neighbors(netmiko_connection: object = None) -> str:
    neighbors = netmiko_connection.send_command(command_string="show ip bgp summary")

    return neighbors

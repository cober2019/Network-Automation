import re
import Database.DatabaseOps as databaseops
import Abstract
import Software.DeviceLogin as connect_with

def cdp_neighbors(netmiko_connection: object = None) -> str:

    cdp_neighbors = netmiko_connection.send_command(command_string="show cdp neighbors")
    
    return  cdp_neighbors

def lldp_neighbors_detail(netmiko_connection: object = None) -> str:
    """Use this function is systems supports. Allows interfaces to be on same line as device-name"""

    lldp_neighbors = netmiko_connection.send_command(command_string="show lldp neighbors system-detail")
    
    return lldp_neighbors


def lldp_neighbors(netmiko_connection: object = None) -> str:
    lldp_neighbors = netmiko_connection.send_command(command_string="show lldp neighbors")

    return lldp_neighbors
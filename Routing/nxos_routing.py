"""Helper class to parse Nexus routing table"""

import time
import ipaddress

route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

def get_routing_table(netmiko_connection, vrf) -> str:
    """Using the connection object created from the netmiko_login() and vdc gtp, get_vdcs(), get routes from device"""

    if not vrf:
        routes = netmiko_connection.send_command(command_string="show ip route")
    else:
        routes = netmiko_connection.send_command(command_string=f"show ip route vrf {vrf}")

    return routes


def get_vdcs(netmiko_connection) -> list:
    """Using the connection object created from the netmiko_login(), get vdcs"""

    vdcs = []
    netmiko_connection = netmiko_connection
    netmiko_connection.send_command(command_string="terminal length 0")
    get_vdc = netmiko_connection.send_command(command_string="show vdc detail")
    lines = get_vdc.split("\n")

    for line in lines:
        if line.rfind("vdc name") != -1:
            vdc = line.split()[2]
            vdcs.append(vdc)
        else:
            pass

    return vdcs


def get_vrfs(netmiko_connection, vdc) -> list:
    """Using the connection object created from the netmiko_login(), get routes from device"""

    vrfs = []
    netmiko_connection.send_command(command_string=f"switchto vdc {vdc}", expect_string="")
    time.sleep(3)
    netmiko_connection.send_command(command_string="terminal length 0")
    send_vrfs = netmiko_connection.send_command(command_string="show vrf")
    lines = send_vrfs.split("\n")

    for line in lines:
        if line.rfind("VRF-Name") != -1:
            pass
        elif not line.split():
            pass
        else:
            vrfs.append(line.split()[0])

    return vrfs


class RoutingNexus():

    def __init__(self, connection_obj):
        
        self.netmiko_connection = connection_obj
        self.prefix = None
        self.protocol = None
        self.vrf = None
        self.vdc = None

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []
        self._route_table = []

        self._parse_vrf_routing_entries()

    def _parse_vrf_routing_entries(self) -> None:
        """Gets route table from device and begin calling parser funtions"""

        vdcs = get_vdcs(self.netmiko_connection)

        for vdc in vdcs:
            self.vdc = vdc
            vrfs = get_vrfs(self.netmiko_connection, vdc)
            for vrf in vrfs:
                self.vrf = vrf
                route_entries = get_routing_table(self.netmiko_connection, vrf)
                list(map(self._route_breakdown, route_entries.splitlines()))
                self.database()
                self.clear_lists(marker=1)

    def _find_prefix(self, prefix) -> None:
        """splits string and finds ip address"""

        if prefix.rfind("via") == -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[0].strip(","))) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[0].strip(",")))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

    def _get_protocol(self, routing_entry) -> None:

        try:
            self.protocol = routing_entry.split()[5].strip(",")
        except IndexError:
            pass

        try:
            self.protocol = routing_entry.split()[5].replace(",", " ") + routing_entry.split()[6].strip(",")
        except IndexError:
            pass

    def _route_breakdown(self, routing_entry: str) -> None:

        """Breaks down each routing entry for routing attributes"""

        self._find_prefix(routing_entry)

        if routing_entry.rfind("attached") != -1:
            self.admin_dis.append("0")
            self.protocol = "C"
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[3].rfind("[") != -1:
                self.admin_dis.append(routing_entry.split()[3].split("/")[0].strip("["))
                self.metric.append(routing_entry.split()[3].split("/")[1].strip("],"))
                self.next_hop.append(routing_entry.split()[1].strip(","))
                self.route_age.append(routing_entry.split()[4].strip(","))
                self.interface.append(routing_entry.split()[2].strip(","))
                self._get_protocol(routing_entry)
            elif routing_entry.split()[2].rfind("[") != -1:
                # Static Routes
                self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                self.metric.append(routing_entry.split()[2].split("/")[1].strip("],"))
                self.next_hop.append(routing_entry.split()[1].strip(","))
                self.route_age.append(routing_entry.split()[3].strip(","))
                self.interface.append("Local")
                self.protocol = routing_entry.split()[4]

    def clear_lists(self, marker=None) -> None:
        """Called if self.prefix is changed. Clear instance lists"""

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []
        # Marker is set on last db write to clear attributes for next vrf
        if marker == 1:
            self.prefix = None
            self.protocol = None

    def database(self) -> None:
        """Write route attributes to database"""

        try:
            self._route_table.append([self.vdc, self.vrf, self.prefix, self.protocol,
                                        self.admin_dis[0], ", ".join(self.metric),
                                        ", ".join(self.next_hop), ", ".join(self.interface),
                                         ", ".join(self.route_age)])
        except IndexError:
            pass
    
    @property
    def route_table(self):
        return self._route_table
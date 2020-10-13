"""Helper class to extract routing information from an ASA"""

import ipaddress
from app.Parse.ProjectRouting.Database import DatabaseOps as DatabaseOps
import app.Parse.ProjectRouting.Abstract as Abstract
import app.Parse.ProjectRouting.Software.DeviceLogin as ConnectWith


def get_routing_table(netmiko_connection: object) -> str:
    """Using the connection object created from the netmiko_login(), get routes from device"""

    netmiko_connection.send_command(command_string="terminal pager 0")
    routes = netmiko_connection.send_command(command_string="show route")

    return routes


class RoutingAsa(Abstract.Routing):
    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*", "V")

    def __init__(self, host, username, password, enable=None):

        self.host = host
        self.username = username
        self.password = password
        self.enable = enable
        self.netmiko_connection = None
        self.prefix = None
        self.protocol = None
        self.vrf = None

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []

        self.create_db = DatabaseOps.RoutingDatabase()
        self.device_login()
        self._parse_global_routing_entries()

    def device_login(self):
        """Logs into a device using netmiko. Check for enables password, begins parsing data and call databse
        method for DB writing"""

        # Check to see if self.enable has been assigned. Create connection object, save object to instance attribute

        if self.enable is None:
            self.netmiko_connection = ConnectWith.netmiko_w_enable(host=self.host,
                                                                   username=self.username,
                                                                   password=self.password)
        else:
            self.netmiko_connection = ConnectWith.netmiko_w_enable(host=self.host,
                                                                   username=self.username,
                                                                   password=self.password,
                                                                   enable_pass=self.enable)

    def _parse_global_routing_entries(self):
        """Gets routing table and calls methods to parse and save routing attributes"""

        route_entries = get_routing_table(self.netmiko_connection)
        list(map(self._route_breakdown, route_entries.splitlines()))
        self.database()

    def _find_prefix(self, prefix):
        """Finds current prefix in routing entry"""

        if prefix.rfind("via") == -1:
            if len(prefix.split()) == 4:
                try:
                    if str(ipaddress.IPv4Address(prefix.split()[2])) + " " + prefix.split()[3] != self.prefix:
                        self.database()
                        self.clear_lists()
                        self.prefix = str(ipaddress.IPv4Address(prefix.split()[2])) + " " + prefix.split()[3]
                except (ipaddress.AddressValueError, IndexError, ValueError):
                    pass
            elif len(prefix.split()) == 3:
                try:
                    if str(ipaddress.ip_address(prefix.split()[1])) + " " + prefix.split()[2] != self.prefix:
                        self.database()
                        self.clear_lists()
                        self.prefix = str(ipaddress.ip_address(prefix.split()[1])) + " " + prefix.split()[2]
                except (ipaddress.AddressValueError, IndexError, ValueError):
                    pass

        if prefix.rfind("via") != -1 and prefix.split()[0].rfind("S") != -1:
            self.database()
            self.clear_lists()
            self.prefix = f"{prefix.split()[1]} {prefix.split()[2]}"

    def _get_protocol(self, routing_entry):
        """Gets routing protocol from routing entry"""

        find_protocol = [protocol for protocol in RoutingAsa.route_protocols if protocol in routing_entry[0:5]]

        if len(find_protocol) == 2:
            self.protocol = find_protocol[1]
        elif len(find_protocol) == 1:
            self.protocol = find_protocol[0]
        else:
            pass

    def _route_breakdown(self, routing_entry: str) -> None:

        """Breaks down each routing entry for routing attributes"""

        self._find_prefix(routing_entry)
        self._get_protocol(routing_entry)

        if routing_entry.rfind("connected") != -1:
            self.admin_dis.append("0")
            self.protocol = "C"
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[0].rfind("[") != -1:
                self.admin_dis.append(routing_entry.split()[0].split("/")[0].strip("["))
                self.metric.append(routing_entry.split()[0].split("/")[1].strip("]"))
                self.next_hop.append(routing_entry.split()[2].strip(","))
                self.route_age.append(routing_entry.split()[3].strip(","))
                self.interface.append(routing_entry.split()[4])
                self._get_protocol(routing_entry)
            if routing_entry.split()[3].rfind("[") != -1:
                self.admin_dis.append(routing_entry.split()[3].split("/")[0].strip("["))
                self.metric.append(routing_entry.split()[3].split("/")[1].strip("]"))
                self.next_hop.append(routing_entry.split()[5].strip(","))
                self.route_age.append("permanent")
                self.interface.append(routing_entry.split()[6])
                self.protocol = routing_entry.split()[0]

    def clear_lists(self):
        """Clear route attribute lists"""

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []

    def database(self):
        """Write route entry to database"""
        try:
            DatabaseOps.db_update_asa(vrf=self.vrf, prefix=self.prefix, protocol=self.protocol,
                                      admin_distance=self.admin_dis[0],metric=", ".join(self.metric),
                                      nexthops=", ".join(self.next_hop), interfaces=", ".join(self.interface),
                                      tag=None, age=", ".join(self.route_age))
        except IndexError:
            pass

"""Helper class to extract routing information from an ASA"""

import collections
import ipaddress
from Database import DatabaseOps as DatabaseOps
import Abstract
import Software.DeviceLogin as ConnectWith


def get_routing_table(netmiko_connection: object) -> str:
    """Using the connection object created from the netmiko_login(), get routes from device"""

    routes = None

    netmiko_connection.send_command(command_string="terminal pager 0")
    routes = netmiko_connection.send_command(command_string="show route")

    return routes


class RoutingAsa(Abstract.Routing):
    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    def __init__(self, host, username, password, enable=None):

        self.host = host
        self.username = username
        self.password = password
        self.netmiko_connection = None
        self.routes = collections.defaultdict(list)
        self._routing = {}
        self.prefix = None
        self.protocol = None

        try:
            self.enable = enable
        except TypeError:
            self.enable = None

        self.create_db = DatabaseOps.RoutingDatabase()
        self.initialize_class_methods()

    def initialize_class_methods(self):
        """Logs into a device using netmiko. Check for enables password, begins parsing data and call databse
        method for DB writing"""

        # Check to see if self.enable has been assigned. Create connection object, save object to instance attribute

        if self.enable is None:
            create_netmiko_connection = ConnectWith.netmiko_w_enable(host=self.host,
                                                                     username=self.username,
                                                                     password=self.password)
        else:
            create_netmiko_connection = ConnectWith.netmiko_w_enable(host=self.host,
                                                                     username=self.username,
                                                                     password=self.password,
                                                                     enable_pass=self.enable)

        self.netmiko_connection = create_netmiko_connection
        self._parse_global_routing_entries()
        self.database()

    def _parse_global_routing_entries(self):
        """Gets routing table and calls methods to parse and save routing attributes"""

        route_entries = get_routing_table(self.netmiko_connection)
        cli_line = route_entries.split("\n")
        for routing_entry in cli_line:
            self._find_prefix(routing_entry)
            self._route_breakdown(routing_entry)

        self._routing["None"] = self.routes
        self.routes = collections.defaultdict(list)

    def _find_prefix(self, prefix):
        """Finds current prefix in routing entry"""

        # Standard routing entires will mask
        if prefix.rfind("via") == -1:
            if len(prefix.split()) == 4:
                try:
                    self.prefix = str(ipaddress.IPv4Address(prefix.split()[2])) + " " + prefix.split()[3]
                except (ipaddress.AddressValueError, IndexError, ValueError):
                    pass
            elif len(prefix.split()) == 3:
                try:
                    self.prefix = str(ipaddress.ip_address(prefix.split()[1])) + " " + prefix.split()[2]
                except (ipaddress.AddressValueError, IndexError, ValueError):
                    pass
        if prefix.rfind("via") != -1:
            if prefix.split()[1] == "S" or "S*":
                try:
                    self.prefix = str(ipaddress.ip_address(prefix.split()[1])) + " " + prefix.split()[2]
                except (ipaddress.AddressValueError, IndexError, ValueError):
                    pass

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

        route_details = {"protocol": None, "admin-distance": None, "metric": None,
                         "next-hop": None, "route-age": None, "interface": "None"}

        self._get_protocol(routing_entry)
        if routing_entry.rfind("connected") != -1:
            route_details["admin-distance"] = 0
            route_details["protocol"] = "C"
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[0].rfind("[") != -1:
                route_details["admin-distance"] = routing_entry.split()[0].split("/")[0].strip("[")
                route_details["metric"] = routing_entry.split()[0].split("/")[1].strip("]")
                route_details["next-hop"] = routing_entry.split()[2].strip(",")
                route_details["route-age"] = routing_entry.split()[3].strip(",")
                route_details["interface"] = routing_entry.split()[4]
                route_details["protocol"] = self.protocol
            if routing_entry.split()[3].rfind("[") != -1:
                route_details["admin-distance"] = routing_entry.split()[3].split("/")[0].strip("[")
                route_details["metric"] = routing_entry.split()[3].split("/")[1].strip("]")
                route_details["next-hop"] = routing_entry.split()[5].strip(",")
                route_details["route-age"] = "Permanant"
                route_details["interface"] = routing_entry.split()[6]
                route_details["protocol"] = routing_entry.split()[0]

        self._write_to_dict(route_details)

    def _write_to_dict(self, route_details):
        """Writes routing attributes to local dictionary"""

        # Pass if protocol key is None. Preventsd type errors elsewhere
        if route_details.get("protocol") is None:
            pass
        else:
            self.routes[self.prefix].append(route_details)

    def database(self):
        """Writes routing attributes to local sql database"""

        for vrf, values_vrf in self._routing.items():
            for prefix, val_prefix in values_vrf.items():
                routes_attributes = []
                for attributes in val_prefix:
                    for attribute, value in attributes.items():
                        routes_attributes.append(value)

                if len(routes_attributes) == 6:
                    DatabaseOps.db_update_asa(vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                              admin_distance=routes_attributes[1],
                                              metric=routes_attributes[2], nexthops=routes_attributes[3],
                                              interfaces=routes_attributes[5], tag=None, age=routes_attributes[4])
                if len(routes_attributes) == 12:
                    next_hops = routes_attributes[3] + ", " + routes_attributes[9]
                    route_metrics = routes_attributes[2] + ", " + routes_attributes[8]
                    interfaces = routes_attributes[5] + ", " + routes_attributes[11]
                    route_age = routes_attributes[4] + ", " + routes_attributes[10]

                    DatabaseOps.db_update_asa(vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                              admin_distance=routes_attributes[1], metric=route_metrics,
                                              nexthops=next_hops, interfaces=interfaces, tag=None, age=route_age)



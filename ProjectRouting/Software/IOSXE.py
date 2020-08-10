"""Helper class to parse routing entries and store to sql database"""

import collections
import Database.DatabaseOps as DatabaseOps
import Abstract
import Software.DeviceLogin as ConnectWith
import sqlite3
import ipaddress


def get_vrfs(netmiko_connection: object):
    """Using the connection object created from the netmiko_login(), get routes from device"""

    vrfs = []
    send_vrfs = netmiko_connection.send_command(command_string="show vrf")

    cli_line = send_vrfs.split("\n")
    for line in cli_line:
        if "Name" in line:
            pass
        else:
            vrf = line.split()[0]
            vrfs.append(vrf)

    return vrfs


def get_routing_table(netmiko_connection: object, vrfs=None):
    """Using the connection object created from the netmiko_login(), get routes from device"""

    routes = None

    if not vrfs:
        netmiko_connection.send_command(command_string="terminal length 0")
        routes = netmiko_connection.send_command(command_string="show ip route")
    elif vrfs:
        netmiko_connection.send_command(command_string="terminal length 0")
        routes = netmiko_connection.send_command(command_string=f"show ip route vrf {vrfs}")

    return routes


class RoutingIos(Abstract.Routing):
    """Begin route enty breakdown with various methods"""

    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    Routing_db = sqlite3.connect("Routing")
    cursor = Routing_db.cursor()

    def __init__(self, host=None, username=None, password=None, **enable):

        self.host = host
        self.username = username
        self.password = password
        self.netmiko_connection = None
        self.routes = collections.defaultdict(list)
        self._routing = {}
        self.prefix = None
        self.protocol = None
        self.mask = None
        self.vrf = None

        try:
            self.enable = enable["enable"]
        except KeyError:
            self.enable = None

        self.create_db = DatabaseOps.RoutingDatabase()
        self.device_login()
        self._parse_global_routing_entries()
        self._parse_vrf_routing_entries()
        self.database()

    def device_login(self):

        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        # Check to see if self.enable has been assigned. Create connection object, save object to instance attribute

        if self.enable is None:
            self.netmiko_connection = ConnectWith.netmiko(host=self.host,
                                                          username=self.username,
                                                          password=self.password)
        else:
            self.netmiko_connection = ConnectWith.netmiko_w_enable(host=self.host,
                                                                   username=self.username,
                                                                   password=self.password,
                                                                   enable_pass=self.enable)

    def _parse_vrf_routing_entries(self):

        self.prefix = None
        vrfs = get_vrfs(self.netmiko_connection)
        for vrf in vrfs:
            self.vrf = vrf
            route_entries = get_routing_table(self.netmiko_connection, vrfs=vrf)
            list(map(self._route_breakdown, route_entries.splitlines()))
            self._routing[self.vrf] = self.routes

    def _parse_global_routing_entries(self):

        route_entries = get_routing_table(self.netmiko_connection)
        list(map(self._route_breakdown, route_entries.splitlines()))
        self._routing["global"] = self.routes
        self.routes = collections.defaultdict(list)

    def _write_to_dict(self, route_details):

        if self.vrf is None and route_details.get("protocol") is not None:
            self.routes[self.prefix].append(route_details)

        elif self.vrf is not None and route_details.get("protocol") is not None:
            self.routes[self.prefix].append(route_details)

    def _find_prefix(self, prefix):

        if prefix.rfind("via") == -1:
            try:
                self.prefix = str(ipaddress.IPv4Network(prefix.split()[2]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

            try:
                self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        elif prefix.rfind("via") != -1:

            try:
                self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        # Find mask in line with variably subnetted. Save mask for nexts lines until a line provides a new mask
        if prefix.rfind("subnetted") != -1:
            try:
                self.mask = prefix.split()[0][-3:]
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        # Add self.mask to entries that are variably subnetted, line 139
        try:
            if prefix.rfind("via") != -1 and prefix.split()[1][-3] != "/" and prefix.split()[1][-2] != "/":
                self.prefix = str(ipaddress.IPv4Network(prefix.split()[1] + self.mask))
        except (ipaddress.AddressValueError, IndexError, ValueError, TypeError):
            pass

    def _get_protocol(self, routing_entry) -> str:
        """Gets routing protocol from routing entry"""

        find_protocol = [protocol for protocol in RoutingIos.route_protocols if protocol in routing_entry[0:5]]

        if len(find_protocol) == 2:
            self.protocol = find_protocol[1]
        elif len(find_protocol) == 1:
            self.protocol = find_protocol[0]
        else:
            pass

        if len(routing_entry.split()) > 3:
            protocol = f"{routing_entry.split()[0]} {routing_entry.split()[1]}"
        else:
            protocol = "none"

        return protocol

    def _route_breakdown(self, routing_entry: str) -> None:

        """Breaks down each routing entry for routing attributes"""

        route_details = {"protocol": None, "admin-distance": None, "metric": None,
                         "next-hop": None, "route-age": None, "interface": "None"}

        self._find_prefix(routing_entry)
        protocol = self._get_protocol(routing_entry)

        if routing_entry.rfind("connected") != -1:
            route_details["admin-distance"] = 0
            route_details["metric"] = 0
            route_details["next-hop"] = routing_entry.split()[4].strip(",")
            route_details["route-age"] = "permanent"
            route_details["interface"] = routing_entry.split()[5].strip(",")
            route_details["protocol"] = "C"
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[0].rfind("[") == -1:
                if protocol in RoutingIos.route_protocols:
                    route_details["admin-distance"] = routing_entry.split()[3].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[3].split("/")[1].strip("]")
                    route_details["next-hop"] = routing_entry.split()[5].strip(",")
                    route_details["route-age"] = routing_entry.split()[6].strip(",")
                    route_details["interface"] = routing_entry.split()[7].strip(",")
                    route_details["protocol"] = self.protocol
                elif len(routing_entry.split()) == 6:
                    route_details["admin-distance"] = routing_entry.split()[2].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[2].split("/")[1].strip("]")
                    route_details["next-hop"] = routing_entry.split()[4].strip(",")
                    route_details["route-age"] = routing_entry.split()[5].strip(",")
                    route_details["protocol"] = self.protocol
                elif len(routing_entry.split()) == 7:
                    route_details["admin-distance"] = routing_entry.split()[2].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[2].split("/")[1].strip("]")
                    route_details["next-hop"] = routing_entry.split()[4].strip(",")
                    route_details["route-age"] = routing_entry.split()[5].strip(",")
                    route_details["interface"] = routing_entry.split()[6].strip(",")
                    route_details["protocol"] = self.protocol
                else:
                    route_details["admin-distance"] = routing_entry.split()[2].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[2].split("/")[1].strip("]")
                    route_details["next-hop"] = routing_entry.split()[4].strip(",")
                    route_details["protocol"] = routing_entry.split()[0]

            else:
                route_details["admin-distance"] = routing_entry.split()[0].split("/")[0].strip("[")
                route_details["metric"] = routing_entry.split()[0].split("/")[1].strip("]")
                route_details["next-hop"] = routing_entry.split()[2].strip(",")
                route_details["route-age"] = routing_entry.split()[3].strip(",")
                route_details["interface"] = routing_entry.split()[4].strip(",")
                route_details["protocol"] = self.protocol

        self._write_to_dict(route_details)

    def database(self):
        """Unpacks routes from dictionary and write the to our database since our route attribute are prediible lengths,
        we can easily combine and write if needed"""

        for vrf, values_vrf in self._routing.items():
            for prefix, val_prefix in values_vrf.items():
                routes_attributes = []
                for attributes in val_prefix:
                    for attribute, value in attributes.items():
                        routes_attributes.append(value)

                if len(routes_attributes) == 6:
                    DatabaseOps.db_update_ios_xe(vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                                 admin_distance=routes_attributes[1],
                                                 metric=routes_attributes[2], nexthops=routes_attributes[3],
                                                 interfaces=routes_attributes[5], tag=None, age=routes_attributes[4])

                if len(routes_attributes) == 12:
                    next_hops = routes_attributes[3] + ", " + routes_attributes[9]
                    route_metrics = routes_attributes[2] + ", " + routes_attributes[8]
                    interfaces = routes_attributes[5] + ", " + routes_attributes[11]
                    route_age = routes_attributes[4] + ", " + routes_attributes[10]

                    DatabaseOps.db_update_ios_xe(vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                                 admin_distance=routes_attributes[1], metric=route_metrics,
                                                 nexthops=next_hops, interfaces=interfaces, tag=None, age=route_age)




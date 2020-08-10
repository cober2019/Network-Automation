"""Helper class to parse Nexus routing table"""

import collections
import ipaddress
from Database import DatabaseOps as DataBaseOps
import Abstract
import Software.DeviceLogin as ConnectWith


def get_routing_table(netmiko_connection, *vrf) -> str:
    """Using the connection object created from the netmiko_login() and vdc gtp, get_vdcs(), get routes from device"""

    if not vrf:
        routes = netmiko_connection.send_command(command_string="show ip route")
    else:
        routes = netmiko_connection.send_command(command_string="show ip route vrf %s" % vrf[0])

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
    netmiko_connection.send_command(command_string="switchto vdc %s" % vdc, expect_string="")
    netmiko_connection.send_command(command_string="terminal length 0")
    send_vrfs = netmiko_connection.send_command(command_string="show vrf")
    lines = send_vrfs.split("\n")

    for line in lines:
        if line.rfind("VRF-Name") != -1:
            pass
        elif not line.split():
            pass
        else:
            vrf = line.split()[0]
            vrfs.append(vrf)

    return vrfs


class RoutingNexus(Abstract.Routing):
    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    def __init__(self, host=None, username=None, password=None, **enable):

        self.host = host
        self.username = username
        self.password = password
        self.netmiko_connection = None
        self.routes = collections.defaultdict(list)
        self._vdcroutes = collections.defaultdict(list)
        self.cdp_lldp_neighbors = {}
        self.prefix = None
        self.vrf = None
        self.vdc = None

        try:
            self.enable = enable["enable"]
        except KeyError:
            self.enable = None

        self.create_db = DataBaseOps.RoutingDatabase()
        self.device_login()  # Initiate class methods
        self._parse_vrf_routing_entries()
        self.database()

    def device_login(self):

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

        vdcs = get_vdcs(self.netmiko_connection)

        for vdc in vdcs:
            self.vdc = vdc
            vrfs = get_vrfs(self.netmiko_connection, vdc)
            for vrf in vrfs:
                self.vrf = vrf
                route_entries = get_routing_table(self.netmiko_connection, vrf)
                list(map(self._route_breakdown, route_entries.splitlines()))

    def _write_to_dict(self, route_details):

        if route_details.get("protocol") is None:
            pass
        else:
            vrf_routes = {}
            self.routes = collections.defaultdict(list)

            self.routes[self.prefix].append(route_details)
            vrf_routes[self.vrf] = self.routes
            self._vdcroutes[self.vdc].append(vrf_routes)

    def _find_prefix(self, prefix):
        """splits string and finds ip address"""

        if prefix.rfind("via") == -1:
            try:
                self.prefix = str(ipaddress.IPv4Network(prefix.split()[0].strip(",")))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

    def _route_breakdown(self, routing_entry: str) -> None:

        """Breaks down each routing entry for routing attributes"""

        route_details = {"protocol": None, "admin-distance": None, "metric": None,
                         "next-hop": None, "route-age": None, "interface": "None"}

        self._find_prefix(routing_entry)

        if routing_entry.rfind("attached") != -1:
            route_details["admin-distance"] = 0
            route_details["protocol"] = "C"
            route_details["append"] = "append"
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[3].rfind("[") != -1:
                if len(routing_entry.split()) == 6:
                    route_details["admin-distance"] = routing_entry.split()[3].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[3].split("/")[1].strip("],")
                    route_details["next-hop"] = routing_entry.split()[1].strip(",")
                    route_details["route-age"] = routing_entry.split()[4].strip(",")
                    route_details["interface"] = routing_entry.split()[2].strip(",")
                    route_details["protocol"] = routing_entry.split()[5]
                elif len(routing_entry.split()) == 7:
                    route_details["admin-distance"] = routing_entry.split()[3].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[3].split("/")[1].strip("],")
                    route_details["next-hop"] = routing_entry.split()[1].strip(",")
                    route_details["route-age"] = routing_entry.split()[4].strip(",")
                    route_details["interface"] = routing_entry.split()[2].strip(",")
                    route_details["protocol"] = routing_entry.split()[5] + routing_entry.split()[6].strip(",")
                elif len(routing_entry.split()) == 9:
                    route_details["admin-distance"] = routing_entry.split()[3].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[3].split("/")[1].strip("],")
                    route_details["next-hop"] = routing_entry.split()[1].strip(",")
                    route_details["route-age"] = routing_entry.split()[4].strip(",")
                    route_details["interface"] = routing_entry.split()[2].strip(",")
                    route_details["protocol"] = routing_entry.split()[5] + routing_entry.split()[6].strip(",")
            elif routing_entry.split()[2].rfind("[") != -1:
                if len(routing_entry.split()) == 5:
                    route_details["admin-distance"] = routing_entry.split()[2].split("/")[0].strip("[")
                    route_details["metric"] = routing_entry.split()[2].split("/")[1].strip("],")
                    route_details["next-hop"] = routing_entry.split()[1].strip(",")
                    route_details["route-age"] = routing_entry.split()[3].strip(",")
                    route_details["interface"] = "Local"
                    route_details["protocol"] = routing_entry.split()[4]

        self._write_to_dict(route_details)

    def database(self):

        # Unpack routing dictionary
        for vdc, values_vdc in self._vdcroutes.items():
            for i in values_vdc:
                for vrf, route_contents in i.items():
                    for prefix, val_prefix in route_contents.items():
                        routes_attributes = []
                        for attributes in val_prefix:
                            for attribute, value in attributes.items():
                                routes_attributes.append(value)

                        if len(routes_attributes) == 6:
                            DataBaseOps.db_update_nexus(vdc=vdc, vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                                        admin_distance=routes_attributes[1], metric=routes_attributes[2],
                                                        nexthops=routes_attributes[3], interfaces=routes_attributes[5],
                                                        tag=None,
                                                        age=routes_attributes[4])

                        if len(routes_attributes) == 12:
                            next_hops = routes_attributes[3] + ", " + routes_attributes[9]
                            route_metrics = routes_attributes[2] + ", " + routes_attributes[8]
                            interfaces = routes_attributes[5] + ", " + routes_attributes[11]
                            route_age = routes_attributes[4] + ", " + routes_attributes[10]

                            DataBaseOps.db_update_nexus(vdc=vdc, vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                                        admin_distance=routes_attributes[1], metric=route_metrics,
                                                        nexthops=next_hops, interfaces=interfaces, tag=None,
                                                        age=route_age)

                        if len(routes_attributes) == 14:
                            DataBaseOps.db_update_nexus(vdc=vdc, vrf=vrf, prefix=prefix, protocol=routes_attributes[0],
                                                        admin_distance=routes_attributes[1], metric=routes_attributes[2],
                                                        nexthops=routes_attributes[3], interfaces=routes_attributes[5],
                                                        tag=None,
                                                        age=routes_attributes[4])

    def _parse_global_routing_entries(self):
        pass

    def _get_protocol(self, routing_entry) -> str:
        pass



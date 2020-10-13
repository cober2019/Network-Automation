"""Helper class to parse routing entries and store to sql database"""

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
            vrfs.append(line.split()[0])

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

    routes = routes.split("\n")

    return routes


def is_subneted(prefix):

    mask = None

    if prefix.rfind("subnetted") != -1:
        mask = "/" + prefix.split()[0].split("/")[1]

    return mask


class RoutingIos:
    """Begin route enty breakdown with various methods"""

    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    def __init__(self, netmiko_connection, db_obj, db, cursor):

        self.db_obj = db_obj
        self.netmiko_connection = netmiko_connection
        self.mask = None
        self.prefix = None
        self.protocol = None
        self.vrf = "global"
        self.db = db
        self.cursor = cursor

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []

        self._parse_global_routing_entries()
        self._parse_vrf_routing_entries()

    def _parse_vrf_routing_entries(self):
        """Parses entries for vrf table"""

        vrfs = get_vrfs(self.netmiko_connection)
        for vrf in vrfs:
            self.vrf = vrf
            route_entries = get_routing_table(self.netmiko_connection, vrfs=vrf)
            list(map(self._route_breakdown, route_entries))

    def _parse_global_routing_entries(self):
        """Parses entries with no vrfs"""

        route_entries = get_routing_table(self.netmiko_connection)
        list(map(self._route_breakdown, route_entries))
        # Writes last entry to database
        self.database()
        # Clear list for next method
        self.clear_lists()

    def _find_prefix(self, prefix):

        if prefix.rfind("via") == -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[2])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[2]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

            try:
                if str(ipaddress.IPv4Network(prefix.split()[1])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        elif prefix.rfind("via") != -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[1])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass
            try:
                if str(ipaddress.IPv4Network(prefix.split()[2])) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1]))
            except (ipaddress.AddressValueError, IndexError, ValueError):
                pass

        # Combines self.mask with variablly subnetted prefixes
        if prefix.rfind("via") != -1 and prefix.split()[1].rfind("/") == -1:
            try:
                if str(ipaddress.IPv4Network(prefix.split()[1] + self.mask)) != self.prefix:
                    self.database()
                    self.clear_lists()
                    self.prefix = str(ipaddress.IPv4Network(prefix.split()[1] + self.mask))
            except (ipaddress.AddressValueError, IndexError, ValueError, TypeError):
                pass

    def _get_protocol(self, routing_entry) -> None:
        """Gets routing protocol from routing entry"""

        find_protocol = [protocol for protocol in RoutingIos.route_protocols if protocol in routing_entry[0:5]]

        if len(find_protocol) == 2:
            self.protocol = find_protocol[1]
        elif len(find_protocol) == 1:
            self.protocol = find_protocol[0]
        else:
            pass

    def _route_breakdown(self, routing_entry: str) -> None:

        """Breaks down each routing entry for routing attributes"""

        self.mask = is_subneted(routing_entry)
        self._find_prefix(routing_entry)
        self._get_protocol(routing_entry)

        if routing_entry.rfind("directly connected") != -1:
            self.admin_dis.append("0")
            self.metric.append("0")
            self.next_hop.append(routing_entry.split()[4].strip(","))
            self.route_age.append("permanent")
            self.interface.append(routing_entry.split()[5].strip(","))
        elif routing_entry.rfind("via") != -1:
            if routing_entry.split()[0].rfind("[") == -1:
                if len(routing_entry.split()) == 6:
                    self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[2].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[4].strip(","))
                    self.route_age.append(routing_entry.split()[5].strip(","))
                elif len(routing_entry.split()) == 7:
                    self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[2].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[4].strip(","))
                    self.route_age.append(routing_entry.split()[5].strip(","))
                    self.interface.append(routing_entry.split()[6].strip(","))
                elif len(routing_entry.split()) == 8:
                    self.admin_dis.append(routing_entry.split()[3].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[3].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[5].strip(","))
                    self.route_age.append(routing_entry.split()[6].strip(","))
                    self.interface.append(routing_entry.split()[7].strip(","))
                else:
                    # Static routes
                    self.admin_dis.append(routing_entry.split()[2].split("/")[0].strip("["))
                    self.metric.append(routing_entry.split()[2].split("/")[1].strip("]"))
                    self.next_hop.append(routing_entry.split()[4].strip(","))
                    self.route_age.append("permanent")
                    self.protocol = routing_entry.split()[0]
            else:
                self.admin_dis.append(routing_entry.split()[0].split("/")[0].strip("["))
                self.metric.append(routing_entry.split()[0].split("/")[1].strip("]"))
                self.next_hop.append(routing_entry.split()[2].strip(","))
                self.route_age.append(routing_entry.split()[3].strip(","))
                self.interface.append(routing_entry.split()[4].strip(","))

    def clear_lists(self):

        self.admin_dis = []
        self.metric = []
        self.next_hop = []
        self.route_age = []
        self.interface = []

    def database(self):

        if self.route_age:
            try:
                self.db_obj.db_update_ios_xe(self.db, self.cursor, vrf=self.vrf, prefix=self.prefix, protocol=self.protocol,
                                             admin_distance=self.admin_dis[0], metric=", ".join(self.metric),
                                             nexthops=", ".join(self.next_hop), interfaces=", ".join(self.interface),
                                             tag=None, age=", ".join(self.route_age))
            except IndexError:
                pass

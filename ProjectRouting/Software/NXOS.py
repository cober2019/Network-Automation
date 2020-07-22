from netmiko import ConnectHandler, ssh_exception
import re
import collections
import time
import Database.DatabaseOps as databaseops
import Database.DB_queries as db_queries
from Software import Neighbors
import Abstract
import Software.DeviceLogin as connect_with


def get_routing_table(netmiko_connection: object, *vrf: str) -> str:
    """Using the connection object created from the netmiko_login() and vdc gtp, get_vdcs(), get routes from device"""

    routes = None

    if not vrf:
        routes = netmiko_connection.send_command(command_string="show ip route")
    else:
        routes = netmiko_connection.send_command(command_string="show ip route vrf %s" % vrf[0])

    return routes


def get_vdcs(netmiko_connection: object) -> str:
    """Using the connection object created from the netmiko_login(), get vdcs"""

    vdcs = []
    netmiko_connection = netmiko_connection
    netmiko_connection.send_command(command_string="terminal length 0")
    get_vdc = netmiko_connection.send_command(command_string="show vdc detail")

    line = re.findall(r'.*(?=\n)', get_vdc)
    for _ in line:
        if "vdc name:" in _:
            vdc_name = re.findall(r'(?<=vdc\sname:\s)[a-z-A-Z0-9].*', _)
            vdcs.append(vdc_name[0])

    return vdcs


def get_vrfs(netmiko_connection: object, vdc: str) -> list:
    """Using the connection object created from the netmiko_login(), get routes from device"""

    netmiko_connection.send_command(command_string="switchto vdc %s" % vdc, expect_string="")
    time.sleep(3)
    netmiko_connection.send_command(command_string="terminal length 0")
    send_vrfs = netmiko_connection.send_command(command_string="show vrf")
    vrfs = []

    line = re.findall(r'.*$', send_vrfs)
    if not line:
        pass
    else:
        for _ in line:
            try:
                vrf = re.match(r'^[a-zA-Z].*(?=[0-9])', _)
                vrf_cleanup = vrf[0].replace(" ", "")
                vrfs.append(vrf_cleanup)
            except (AttributeError, TypeError, IndexError):
                pass

        edit_vrf_list = list(dict.fromkeys(vrfs))

        return edit_vrf_list


class Routing_Nexus(Abstract.Routing):

    """Collect Routing table details using netmiko and re. Methods will return a dictionary with routes, protocol,
    next-hop, interfaces. for code readlabilty, Each method contains inner fuctions to perfrom actions for that
    particular method """

    def __init__(self, host=None, username=None, password=None, **enable):

        """Initialize instance attributes. Credentials
        _host
        _username
        _password
        routes = maintains parse route data in dictionary format
        prefix = maintains current prefix in the loop
        _vdcroutes = parent dictionary, routes are value
        initialize_class_methods() = initializes class methods
        """

        self._host = host
        self._username = username
        self._password = password
        self.netmiko_connection = None
        self.routes = collections.defaultdict(list)
        self._vdcroutes = collections.defaultdict(list)
        self.cdp_lldp_neighbors = {}
        self.prefix = None

        try:
            self.enable = enable["enable"]
        except KeyError:
            self.enable = None

        self.initialize_class_methods()  # Initiate class methods
        self.database()

    def initialize_class_methods(self):

        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        def find_prefix(prefix: str) -> None:

            """Finds the prefix on the current line"""


            if re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9](?=,)', prefix):
                prefix = re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9](?=,)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[0-9](?=,)', prefix):
                prefix = re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[0-9](?=,)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\.[0-9]/[1-9][0-9](?=,)', prefix):
                prefix = re.findall(r'^[0-9].*\..*[0-9]\.[0-9]\..*[0-9]/[1-9][0-9](?=,)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\.[0-9]/[0-9](?=,)', prefix):
                prefix = re.findall(r'^[0-9].*\..*[0-9]\..*[0-9]\.[0-9]/[0-9](?=,)', prefix)
                self.prefix = prefix[0]

        def parse_routing_entries_with_vrfs():

            vrf = None
            vrf_routes = {}

            for vdc in vdcs:
                vrfs = get_vrfs(self.netmiko_connection, vdc)
                for vrf in vrfs:
                    vrf_routes = {}
                    get_vdc_routes = get_routing_table(self.netmiko_connection, vrf)
                    line = re.findall(r'.*(?=\n)', get_vdc_routes)
                    for i in line:

                        # Find the prefix in the current line/routing entry
                        find_prefix(i)

                        # Matches prefix mask, use other methods to find route type, next-hop, outgoing interfaces
                        if re.findall(r'via', i):
                            if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', i):
                                self.protocols_and_metrics(i)
                                self.slash_ten_and_up(i)
                            elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', i):
                                self.protocols_and_metrics(i)
                                self.slash_nine_and_below(i)
                            else:
                                self.protocols_and_metrics(i)
                                self.no_mask(i)
                        else:
                            pass

                # Save routes to dictionary, reset dictionary k,v's
                vrf_routes[vrf] = self.routes
                self._vdcroutes[vdc].append(vrf_routes)

                self.routes = collections.defaultdict(list)

        def parse_global_routing_entries():

            vrf_routes = {}

            for vdc in vdcs:
                get_vdc_routes = get_routing_table(self.netmiko_connection)
                line = re.findall(r'.*(?=\n)', get_vdc_routes)
                for i in line:

                    # Find the prefix in the current line/routing entry
                    find_prefix(i)

                    # Matches prefix mask, use other methods to find route type, next-hop, outgoing interfaces
                    if re.findall(r'via', i):
                        if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', i):
                            self.protocols_and_metrics(i)
                            self.slash_ten_and_up(i)
                        elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', i):
                            self.protocols_and_metrics(i)
                            self.slash_nine_and_below(i)
                        else:
                            self.protocols_and_metrics(i)
                            self.no_mask(i)
                    else:
                        pass

                # Save routes to dictionary, reset dictionary k,v's
                vrf_routes["default"] = self.routes
                self._vdcroutes[vdc].append(vrf_routes)
                self.routes = collections.defaultdict(list)

        # Check to see if self.enable has been assigned. Create connection object, save object to instance attribute

        if self.enable is None:
            create_netmiko_connection = connect_with.netmiko(host= self.host, username= self.username, password= self.password)
        else:
            create_netmiko_connection = connect_with.netmiko_w_enable(host= self.host, username= self.username, password= self.password,
                                                                        enable_pass=self.enable)
        self.netmiko_connection = create_netmiko_connection

        # Get VDCs
        vdcs = get_vdcs(self.netmiko_connection)

        # Use inner functions to start collecting routes and route particulars
        parse_global_routing_entries()
        parse_routing_entries_with_vrfs()
        self.neighbors()

    def slash_ten_and_up(self, routing_entry: str) -> None:

        """Gets routes with a mask /10 +, writes next hope to instance attribute self.routes"""

        route_details = {"next-hop": None, "interface": None, "metric": None}
        split_route_entry = routing_entry.split(",")

        def outgoing_interfaces():

            try:
                if re.findall(r'(?<=\s)[A-Z].*', split_route_entry[1]):
                    route_details["interface"] = split_route_entry[1].replace(" ", "")
                else:
                    pass
            except IndexError:
                pass

        def find_metric():

            try:
                if re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry):
                    ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
                    route_metric = re.findall(r'(?<=/)[0-9].*', ad_and_metric[0])
                    route_details["metric"] = route_metric[0]
                else:
                    pass
            except IndexError:
                pass

        def find_next_hop():

            try:
                next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*', split_route_entry[0])
                route_details["next-hop"] = next_hop[0]
            except IndexError:
                pass

        def write_to_dictionary():

            if route_details in self.routes[self.prefix]:
                pass
            else:
                self.routes[self.prefix].append(route_details)

        # Use inner functions to start collecting routes and route particulars
        if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*', split_route_entry[0]):
            outgoing_interfaces()
            find_metric()
            find_next_hop()
        if re.findall(r'(?<=,\s)direct', routing_entry):
            route_details["next-hop"] = "direct"
            outgoing_interfaces()
            find_metric()
        if re.findall(r'(?<=,\s)local', routing_entry):
            route_details["next-hop"] = "local"
            outgoing_interfaces()
            find_metric()

        write_to_dictionary()

    def slash_nine_and_below(self, routing_entry: str) -> None:

        """Gets routes with a mask - /10 , writes next hope to instance attribute self.routes"""

        route_details = {"next-hop": None, "interface": None, "metric": None}
        split_route_entry = routing_entry.split(",")

        def outgoing_interfaces():

            try:
                if re.findall(r'(?<=\s)[A-Z].*', split_route_entry[1]):
                    route_details["interface"] = split_route_entry[1].replace(" ", "")
                else:
                    pass
            except IndexError:
                pass

        def find_metric():

            try:
                if re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry):
                    ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
                    route_metric = re.findall(r'(?<=/)[0-9].*', ad_and_metric[0])
                    route_details["metric"] = route_metric[0]
            except IndexError:
                pass

        def find_next_hop():

            try:
                next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*', split_route_entry[0])
                route_details["next-hop"] = next_hop[0]
            except IndexError:
                pass

        def write_to_dictionary():

            if route_details in self.routes[self.prefix]:
                pass
            else:
                self.routes[self.prefix].append(route_details)

        # Use inner functions to start collecting routes and route particulars
        if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*', split_route_entry[0]):
            find_next_hop()
            outgoing_interfaces()
            find_metric()
        if re.findall(r'(?<=,\s)direct', routing_entry):
            route_details["next-hop"] = "direct"
            outgoing_interfaces()
            find_metric()
        if re.findall(r'(?<=,\s)local', routing_entry):
            route_details["next-hop"] = "local"
            outgoing_interfaces()
            find_metric()

        write_to_dictionary()

    def no_mask(self, routing_entry: str) -> None:

        """Gets routes with no mask/show in the routing table as \"subnetted\""""

        route_details = {"next-hop": None, "interface": None, "metric": None}
        split_route_entry = routing_entry.split(",")

        def outgoing_interfaces():

            try:
                if re.findall(r'(?<=\s)[A-Z].*', split_route_entry[1]):
                    route_details["interface"] = split_route_entry[1].replace(" ", "")
                    if route_details in self.routes[self.prefix]:
                        pass
                    else:
                        self.routes[self.prefix].append(route_details)
                else:
                    pass
            except IndexError:
                pass

        def find_metric():

            try:
                if re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry):
                    ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
                    route_metric = re.findall(r'(?<=/)[0-9].*', ad_and_metric[0])
                    route_details["metric"] = route_metric[0]
                    if route_details in self.routes[self.prefix]:
                        pass
                    else:
                        self.routes[self.prefix].append(route_details)
                else:
                    pass
            except IndexError:
                pass

        def find_next_hop():

            find_hops = re.findall(r'(?<=via\s)[0-9].*\..*[0-9]\..*[0-9]\..*', split_route_entry[0])
            route_details["next-hop"] = find_hops[0]

        def write_to_dictionary():

            if route_details in self.routes[self.prefix]:
                pass
            else:
                self.routes[self.prefix].append(route_details)

        # Use inner functions to start collecting routes and route particulars
        if re.findall(r'(?<=via\s)[0-9].*\..*[0-9]\..*[0-9]\..*', split_route_entry[0]):
            find_next_hop()
            outgoing_interfaces()
            find_metric()
        if re.findall(r'(?<=,\s)direct', routing_entry):
            route_details["next-hop"] = "direct"
            outgoing_interfaces()
            find_metric()
        if re.findall(r'(?<=,\s)local', routing_entry):
            route_details["next-hop"] = "local"
            find_metric()

        write_to_dictionary()

    def protocols_and_metrics(self, routing_entry: str) -> None:

        """Gets route type, Parent protocol/Child type. Ex. OSPF, or OSPF E2. """

        route_details = {"protocol": None, "admin-distance": None, "tag": None}
        split_route_entry = routing_entry.split(",")

        # Check for route tag as all routes don't have a tag
        def check_for_tagging():

            try:
                tag = re.findall(r'(?<=\s)[0-9].*', split_route_entry[6])
                route_details["tag"] = tag[0]
            except IndexError:
                pass
            
            try:
                tag = re.findall(r'(?<=\s)[0-9].*', split_route_entry[5])
                route_details["tag"] = tag[0]
            except IndexError:
                pass

        # Find administrative distance
        def find_admin_distance():

            ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
            admin_distance = re.findall(r'[0-9].*(?=/)', ad_and_metric[0])
            route_details["admin-distance"] = admin_distance[0]

        def write_to_dictionary():

            if route_details in self.routes[self.prefix]:
                pass
            else:
                self.routes[self.prefix].append(route_details)

        # Set metrics and admin-distance for local and direct route

        if re.findall(r'(?<=,\s)direct', routing_entry):
            route_details["protocol"] = "direct"
            route_details["admin-distance"] = "0"
            route_details["tag"] = "direct"

        if re.findall(r'(?<=,\s)local', routing_entry):
            route_details["protocol"] = "local"
            route_details["admin-distance"] = "0"
            route_details["tag"] = "local"

        # Find routing protocol, call inner functions for checks

        try:
            if not re.findall(r'(?<=\s)[A-Z].*', split_route_entry[1]):
                if re.findall(r'(?<=\s)[0-9].*', split_route_entry[3]):
                    pass
                else:
                    route_details["protocol"] = split_route_entry[3].replace(" ", "") + split_route_entry[4]
                    check_for_tagging()
                    find_admin_distance()
            else:
                route_details["protocol"] = split_route_entry[4].replace(" ", "") + split_route_entry[5]
                check_for_tagging()
                find_admin_distance()
        except IndexError:
            pass

        write_to_dictionary()

    def neighbors(self) -> dict:
        """Get full interface name from the routing database, convert to cdp interface types, write to dictionary
        full interface type as key, cdp interface type as value"""

        formatted_interfaces = {}
        cdp_lldp_neighbors = {}
        db_connect = db_queries.Routing_Datbases()
        interfaces = db_connect.get_routing_interfaces(table="Routing_Nexus")

        def db_outgoing_ints():

            if len(interfaces) == 0:
                pass
            else:
                for k in interfaces.keys():
                    if len(k[0]) < 2 or "None" in k[0]:
                        pass
                    else:
                        interface_type = k[0][0:3]
                        if re.findall(r'(?<=[a-zA-Z])[0-9]', k[0]):

                            interface_number = re.findall(r'(?<=[a-zA-Z])[0-9]', k[0])

                            try:
                                formatted_interfaces[k[0]] = interface_type + interface_number[0]
                            except (IndexError, TypeError):
                                pass

                        if re.findall(r'(?<=[a-zA-Z])[0-9].*[0-9]', k[0]):

                            interface_number = re.findall(r'(?<=[a-zA-Z])[0-9].*[0-9]', k[0])

                            try:
                                formatted_interfaces[k[0]] = interface_type + interface_number[0]
                            except (IndexError, TypeError):
                                pass

        def parse_cdp():

            interface = None
            device_id = None
            cdp_neigh = Neighbors.lldp_neighbors(self.netmiko_connection)

            line = re.findall(r'.*(?=\n)', cdp_neigh)
            for _ in line:
                if re.findall(r'(?<=\s)[a-zA-Z].*/[0-9]\s\s', _):
                    find_interface = re.findall(r'(?<=\s)[a-zA-Z].*/[0-9]\s\s', _)
                    interface = re.split(r'\s', find_interface[0])
                    split_string = re.split(r'\s', _)
                    if re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0]):
                        device_id = re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0])
                    else:
                        device_id = re.split(r'\s', _)

                elif re.findall(r'(?<=\s)[a-zA-Z].*/[0-9][0-9]\s\s', _):
                    find_interface = re.findall(r'(?<=\s)[a-zA-Z].*/[0-9][0-9]\s\s', _)
                    interface = re.split(r'\s', find_interface[0])
                    split_string = re.split(r'\s', _)
                    if re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0]):
                        device_id = re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0])
                    else:
                        device_id = re.split(r'\s', _)

                try:
                    for k, v in formatted_interfaces.items():
                        if v == interface[0]:
                            self.cdp_lldp_neighbors[k] = device_id[0]
                        else:
                            pass
                except (TypeError, IndexError):
                    pass

        def parse_lldp():

            interface = None
            device_id = None
            lldp_neigh = Neighbors.lldp_neighbors_detail(self.netmiko_connection)

            line = re.findall(r'.*(?=\n)', lldp_neigh)
            for _ in line:
                if re.findall(r'(?<=\s)[a-zA-Z].*/[0-9]\s\s', _):
                    find_interface = re.findall(r'(?<=\s)[a-zA-Z].*/[0-9]\s\s', _)
                    interface = re.split(r'\s', find_interface[0])
                    split_string = re.split(r'\s', _)
                    if re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0]):
                        device_id = re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0])
                    else:
                        device_id = re.split(r'\s', _)

                elif re.findall(r'(?<=\s)[a-zA-Z].*/[0-9][0-9]\s\s', _):
                    find_interface = re.findall(r'(?<=\s)[a-zA-Z].*/[0-9][0-9]\s\s', _)
                    interface = re.split(r'\s', find_interface[0])
                    split_string = re.split(r'\s', _)
                    if re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0]):
                        device_id = re.findall(r'^.*(?=\.[a-zA-Z].*\.)', split_string[0])
                    else:
                        device_id = re.split(r'\s', _)

                try:
                    for k, v in formatted_interfaces.items():
                        if v == interface[0]:
                            self.cdp_lldp_neighbors[k] = device_id[0]
                        else:
                            pass
                except (TypeError, IndexError):
                    pass

        db_outgoing_ints()
        parse_cdp()
        parse_lldp()

        return self.cdp_lldp_neighbors
    
    def routes_unpacked(self):
        """Print route formated"""

        for vdc, values_vdc in self._vdcroutes.items():
            entry = 0
            print("\n")
            print("#############################################")
            print("VDC: " + vdc)
            print("#############################################")
            print("\n")
            for i in values_vdc:
                for vrf, route_contents in i.items():
                    print("#############################################")
                    print("VRF: " + vrf)
                    print("#############################################")
                    print("\n")
                    for prefix, val_prefix in route_contents.items():
                        print("\n")
                        try:
                            print("Prefix: " + prefix)
                        except TypeError:
                            continue
                        entry = entry + 1
                        for attributes in val_prefix:
                            for attribute, value in attributes.items():
                                try:
                                    print(attribute + ": " + value)
                                except TypeError:
                                    pass
                    print("\n")
                    print(entry)

    def database(self):

        # Create DB object
        db_write = databaseops.RoutingDatabase()

        # Unpack routing dictionary
        for vdc, values_vdc in self._vdcroutes.items():
            for i in values_vdc:
                for vrf, route_contents in i.items():
                    for prefix, val_prefix in route_contents.items():
                        routes_attributes = []
                        for attributes in val_prefix:
                            for attribute, value in attributes.items():
                                # Save routing attributes to list in preperation for DB write
                                routes_attributes.append(value)

                        # Get the length of the list. Each will be a fixed length. Combine next hops, interfaces, metrics
                        # and tags. This is so we dont have to modify DB rows/columns.
                        if len(routes_attributes) == 6:

                            ldp_neigh = [v for k, v in self.cdp_lldp_neighbors.items() if k == routes_attributes[4]]
                            
                            try:
                                db_write.db_update_nexus(vdc, vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                  routes_attributes[3], routes_attributes[4], routes_attributes[5], routes_attributes[2], ldp_neigh=ldp_neigh[0])
                            except (IndexError, TypeError):
                                db_write.db_update_nexus(vdc, vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                         routes_attributes[3], routes_attributes[4],
                                                         routes_attributes[5], routes_attributes[2], ldp_neigh="Unknown")

                        if len(routes_attributes) == 9:

                            ldp_neigh = [v for k, v in self.cdp_lldp_neighbors.items() if k == routes_attributes[4] or k == routes_attributes[7]]
        
                            try:

                                next_hops = routes_attributes[3] + ", " + routes_attributes[6]
                                route_metrics = routes_attributes[5] + ", " + routes_attributes[8]
                                interfaces = routes_attributes[4] + ", " + routes_attributes[7]
                                db_write.db_update_nexus(vdc, vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                  next_hops, interfaces, route_metrics, routes_attributes[2], ", ".join(ldp_neigh))

                            except (IndexError, TypeError, NameError):

                                next_hops = routes_attributes[3] + ", " + routes_attributes[6]
                                route_metrics = routes_attributes[5] + ", " + routes_attributes[8]
                                interfaces = routes_attributes[4] + ", " + routes_attributes[7]
                                db_write.db_update_nexus(vdc, vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                         next_hops, interfaces, route_metrics, routes_attributes[2],
                                                         ldp_neigh="Unknown")

                        if len(routes_attributes) == 12:

                            try:
                                next_hops = routes_attributes[3] + ", " + routes_attributes[6] + routes_attributes[9]
                                route_metrics = routes_attributes[5] + ", " + routes_attributes[8] + routes_attributes[11]
                                interfaces = routes_attributes[4] + ", " + routes_attributes[7] + routes_attributes[10]
                                db_write.db_update_nexus(vdc, vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                  next_hops, interfaces, route_metrics, routes_attributes[2])
                            except (IndexError, TypeError, NameError) as error:
                                pass

                        if len(routes_attributes) == 15:

                            try:
                                next_hops = routes_attributes[3] + ", " + routes_attributes[6] + routes_attributes[9] + routes_attributes[12]
                                route_metrics = routes_attributes[5] + ", " + routes_attributes[8] + routes_attributes[11] + routes_attributes[14]
                                interfaces = routes_attributes[4] + ", " + routes_attributes[7] + routes_attributes[10] + routes_attributes[13]
                                db_write.db_update_nexus(vdc, vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                  next_hops, interfaces, route_metrics, routes_attributes[2])
                            except (IndexError, TypeError, NameError) as error:
                                pass

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host: str) -> None:
        self._host = host

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password: str) -> None:
        self._password = password

    @property
    def routing(self) -> dict:
        return self._vdcroutes






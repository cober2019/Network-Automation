from netmiko import ConnectHandler, ssh_exception
import re
import collections
import time


def netmiko_login(host=None, username=None, password=None):
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


def get_routing_table(netmiko_connection, *vrf):
    """Using the connection object created from the netmiko_login() and vdc gtp, get_vdcs(), get routes from device"""

    routes = None

    if not vrf:
        routes = netmiko_connection.send_command(command_string="show ip route")
    else:
        routes = netmiko_connection.send_command(command_string="show ip route vrf %s" % vrf[0])

    return routes


def get_vdcs(netmiko_connection):
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


def get_vrfs(netmiko_connection, vdc):
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


class Routing:

    """Collect Routing table details using netmiko and re. Methods will return a dictionary with routes, protocol,
    next-hop, interfaces. for code readlabilty, Each method contains inner fuctions to perfrom actions for that
    particular method """

    def __init__(self, host=None, username=None, password=None):

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
        self.prefix = None
        self.initialize_class_methods()  # Initiate class methods

    def initialize_class_methods(self):

        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        def find_prefix(prefix):

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
                                self.route_types(i)
                                self.slash_ten_and_up(i)
                            elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', i):
                                self.route_types(i)
                                self.slash_nine_and_below(i)
                            else:
                                self.route_types(i)
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
                            self.route_types(i)
                            self.slash_ten_and_up(i)
                        elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', i):
                            self.route_types(i)
                            self.slash_nine_and_below(i)
                        else:
                            self.route_types(i)
                            self.no_mask(i)
                    else:
                        pass

                # Save routes to dictionary, reset dictionary k,v's
                vrf_routes["default"] = self.routes
                self._vdcroutes[vdc].append(vrf_routes)
                self.routes = collections.defaultdict(list)

        # Create connection object and store to instance attribute
        create_netmiko_connection = netmiko_login(self.host, self.username, self.password)
        self.netmiko_connection = create_netmiko_connection

        # Get VDCs
        vdcs = get_vdcs(self.netmiko_connection)

        # Use inner functions to start collecting routes and route particulars
        parse_global_routing_entries()
        parse_routing_entries_with_vrfs()

    def slash_ten_and_up(self, routing_entry):

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

    def slash_nine_and_below(self, routing_entry):

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

    def no_mask(self, routing_entry):

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

    def route_types(self, routing_entry):

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

        # Find routing protocol, call inner functions for checks
        try:
            if not re.findall(r'(?<=\s)[A-Z].*', split_route_entry[1]):
                route_details["protocol"] = split_route_entry[3] + split_route_entry[4]
                check_for_tagging()
                find_admin_distance()
            else:
                route_details["protocol"] = split_route_entry[4] + split_route_entry[5]
                check_for_tagging()
                find_admin_distance()
        except IndexError:
            pass

        write_to_dictionary()

    def vdc_routes_unpacked(self):
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

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def vdcroutes(self):
        return self._vdcroutes




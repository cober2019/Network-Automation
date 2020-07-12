from netmiko import ConnectHandler, ssh_exception
import re
import collections


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


def get_vrfs(netmiko_connection):
    """Using the connection object created from the netmiko_login(), get routes from device"""

    netmiko_connection.send_command(command_string="terminal length 0")
    send_vrfs = netmiko_connection.send_command(command_string="show vrf")
    vrfs = []

    line = re.findall(r'.*$', send_vrfs)
    if not line:
        pass
    else:
        for _ in line:
            try:
                vrf = re.search(r'^.*[a-zA-Z](?=\s\s)', _)
                vrfs.append(vrf.group(0))
            except AttributeError:
                pass

        return vrfs


def get_routing_table(netmiko_connection, *vrfs):
    """Using the connection object created from the netmiko_login(), get routes from device"""
    
    routes = None

    if not vrfs:
        netmiko_connection.send_command(command_string="terminal length 0")
        routes = netmiko_connection.send_command(command_string="show ip route")
    elif vrfs:
        netmiko_connection.send_command(command_string="terminal length 0")
        routes = netmiko_connection.send_command(command_string="show ip route vrf %s" % vrfs[0])

    return routes


class Routing:
    """Collect Routing table details using netmiko and re. Methods will return a dictionary with routes, protocol,
    next-hop, interfaces. for code readlabilty, Each method contains inner fuctions to perfrom actions for that
    particular method """

    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    def __init__(self, host=None, username=None, password=None):

        """Initialize instance attributes. Credentials
        _host
        _username
        _password
        routes = maintains nested parse route data,VRF, route particulars
        _routing_instance = Parent to routes dictionary, maintans VDC Key
        prefix = maintains current prefix in the loop
        protocol = maintains routing protocol until the next line provides the next protocol
        initialize_class_methods() = initializes class methods
        """

        self._host = host
        self._username = username
        self._password = password
        self.netmiko_connection = None
        self.routes = collections.defaultdict(list)
        self._routing_instance = {}
        self.prefix = None
        self.protocol = None
        self.initialize_class_methods()  # Initiate class methods

    def initialize_class_methods(self):

        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        def find_prefix(prefix):

            """Finds the prefix on the current line. Maintains the current prefix in the loop until the next prefix
            The next prefix may not come for severial lines, this is to allow for multiple hops to be entered in
            self.prefix """

            if re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9](?=\s)', prefix):
                prefix = re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9](?=\s)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[0-9](?=\s)', prefix):
                prefix = re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9]/[0-9](?=\s)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\.[0-9](?=\s\[)', prefix):
                prefix = re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9](?=\s\[)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\.[0-9][0-9](?=\s\[)', prefix):
                prefix = re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9](?=\s\[)', prefix)
                self.prefix = prefix[0]
            elif re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\.[0-9][0-9][0-9](?=\s\[)', prefix):
                prefix = re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\..*[0-9](?=\s\[)', prefix)
                self.prefix = prefix[0]

        def parse_global_routing_entries():

            route_entries = get_routing_table(self.netmiko_connection)
            line = re.findall(r'.*(?=\n)', route_entries)
            get_last_line = re.findall(r'.*$', route_entries)
            line.append(get_last_line[0])

            for routing_entry in line:

                # Find the prefix in the current line/routing entry
                find_prefix(routing_entry)

                # Matches prefix mask, use other methods to find route type, next-hop, outgoing interfaces
                if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', routing_entry):
                    self.protocols_and_metrics(routing_entry)
                    self.slash_ten_and_up(routing_entry)
                elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', routing_entry):
                    self.protocols_and_metrics(routing_entry)
                    self.slash_nine_and_below(routing_entry)
                else:
                    self.protocols_and_metrics(routing_entry)
                    self.no_mask(routing_entry)
                
            self._routing_instance["global"] = self.routes
            self.routes = collections.defaultdict(list)

        def parse_routing_entries_with_vrfs(vrfs):

            if not vrfs:
                pass
            else:
                
                for vrf in vrfs:
                    route_entries = get_routing_table(self.netmiko_connection, vrf)
                    line = re.findall(r'.*(?=\n)', route_entries)
                    for routing_entry in line:
        
                        # Find the prefix in the current line/routing entry
                        find_prefix(routing_entry)
        
                        # Matches prefix mask, use other methods to find route type, next-hop, outgoing interfaces
                        if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', routing_entry):
                            self.protocols_and_metrics(routing_entry)
                            self.slash_ten_and_up(routing_entry)
                        elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', routing_entry):
                            self.protocols_and_metrics(routing_entry)
                            self.slash_nine_and_below(routing_entry)
                        else:
                            self.protocols_and_metrics(routing_entry)
                            self.no_mask(routing_entry)

                    self._routing_instance[vrf] = self.routes
                    self.routes = collections.defaultdict(list)

        # Create connection object, save object to instance attribute, get vrfs, find global routes, and find vrf
        # routes
            
        create_netmiko_connection = netmiko_login(self.host, self.username, self.password)
        self.netmiko_connection = create_netmiko_connection
        get_routing_instances = get_vrfs(self.netmiko_connection)

        parse_global_routing_entries()
        parse_routing_entries_with_vrfs(get_routing_instances)

    def slash_ten_and_up(self, routing_entry):

        """Gets routes with a mask /10 +, writes next hope to instance attribute self.routes"""

        route_details = {"next-hop": None, "interface": None, "metric": None}

        def outgoing_interfaces():

            if re.findall(r'(?<=,\s)[A-Z].*', routing_entry):
                outgoing_interface = re.findall(r'(?<=,\s)[A-Z].*', routing_entry)
                route_details["interface"] = outgoing_interface[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)
            else:
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)

        def find_metric():

            if re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry):
                ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
                route_metric = re.findall(r'(?<=/)[0-9].*', ad_and_metric[0])
                route_details["metric"] = route_metric[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)

        # Use inner functions to start collecting route particulars

        if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*[0-9](?=,)', routing_entry):
            next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', routing_entry)
            route_details["next-hop"] = next_hop[0]
            outgoing_interfaces()
            find_metric()

        if re.findall(r'(?<=directly\s)connected(?=,)', routing_entry):
            route_details["next-hop"] = "connected"
            outgoing_interfaces()
            find_metric()

    def slash_nine_and_below(self, routing_entry):

        """Gets routes with a mask - /10 , writes next hope to instance attribute self.routes"""

        route_details = {"next-hop": None, "interface": None, "metric": None}

        def outgoing_interfaces():

            if re.findall(r'(?<=,\s)[A-Z].*', routing_entry):
                outgoing_interface = re.findall(r'(?<=,\s)[A-Z].*', routing_entry)
                route_details["interface"] = outgoing_interface[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)
            else:
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)

        def find_metric():

            if re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry):
                ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
                route_metric = re.findall(r'(?<=/)[0-9].*', ad_and_metric[0])
                route_details["metric"] = route_metric[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)

        # Use inner functions to start collecting route particulars

        if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*[0-9](?=,)', routing_entry):
            next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', routing_entry)
            route_details["next-hop"] = next_hop[0]
            outgoing_interfaces()
            find_metric()

        if re.findall(r'(?<=directly\s)connected(?=,)', routing_entry):
            route_details["next-hop"] = "connected"
            outgoing_interfaces()
            find_metric()

    def no_mask(self, routing_entry):

        """Gets routes with no mask/show in the routing table as \"subnetted\""""

        route_details = {"next-hop": None, "interface": None, "metric": None}

        def outgoing_interfaces():

            if re.findall(r'(?<=,\s)[A-Z].*', routing_entry):
                outgoing_interface = re.findall(r'(?<=,\s)[A-Z].*', routing_entry)
                route_details["interface"] = outgoing_interface[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)
            else:
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)

        def find_metric():

            if re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry):
                ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
                route_metric = re.findall(r'(?<=/)[0-9].*', ad_and_metric[0])
                route_details["metric"] = route_metric[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)

        # Use inner functions to start collecting route particulars

        if re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\.[0-9](?=\s\[)', routing_entry):
            find_hops = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', routing_entry)
            route_details["next-hop"] = find_hops[0]
            outgoing_interfaces()
            find_metric()

        if re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\.[0-9][0-9](?=\s\[)', routing_entry):
            find_hops = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', routing_entry)
            route_details["next-hop"] = find_hops[0]
            outgoing_interfaces()
            find_metric()

        if re.findall(r'\b[0-9].*\..*[0-9]\..*[0-9]\.[0-9][0-9][0-9](?=\s\[)', routing_entry):
            find_hops = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', routing_entry)
            route_details["next-hop"] = find_hops[0]
            outgoing_interfaces()
            find_metric()

        if re.findall(r'(?<=directly\s)connected(?=,)', routing_entry):
            route_details["next-hop"] = "connected"
            outgoing_interfaces()
            find_metric()

    def protocols_and_metrics(self, routing_entry):

        """Gets route type, Parent protocol/Child type. Ex. OSPF, or OSPF E2. """

        route_details = {"protocol": None, "admin-distance": None}
        find_protocol = [protocol for protocol in Routing.route_protocols if protocol in routing_entry[0:5]]

        def write_to_dictionary():

            if route_details in self.routes[self.prefix]:  # Check to see if method dict in list
                pass
            else:
                self.routes[self.prefix].append(route_details)

        try:
            if len(find_protocol) == 2:
                self.protocol = find_protocol[1]
            else:
                self.protocol = find_protocol[0]
        except IndexError:
            pass

        try:
            ad_and_metric = re.findall(r'(?<=\[)[0-9].*(?=])', routing_entry)
            admin_distance = re.findall(r'[0-9].*(?=/)', ad_and_metric[0])
            route_details["admin-distance"] = admin_distance[0]
            route_details["protocol"] = self.protocol
            write_to_dictionary()
        except IndexError:
            pass

    def routes_unpacked(self):
        """Print routes formatted"""

        for vrf, values_vrf in self._routing_instance.items():
            entry = 0
            print("\n")
            print("#############################################")
            print("VRF: " + vrf)
            print("#############################################")
            print("\n")
            for prefix, val_prefix in values_vrf.items():
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
            print("Total Routes: %s" % entry)
            
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
    def routing_instance(self):
        return self._routing_instance

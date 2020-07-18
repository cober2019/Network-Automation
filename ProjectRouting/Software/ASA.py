from netmiko import ConnectHandler, ssh_exception
import re
import collections
import Database.DatabaseOps as databaseops
import Abstract
import Software.DeviceLogin as connect_with


def get_routing_table(netmiko_connection: object) -> str:
    """Using the connection object created from the netmiko_login(), get routes from device"""

    routes = None

    netmiko_connection.send_command(command_string="terminal pager 0")
    routes = netmiko_connection.send_command(command_string="show route")

    return routes


class Routing_Asa(Abstract.Routing):
    """Collect Routing table details using netmiko and re. Methods will return a dictionary with routes, protocol,
    next-hop, interfaces. for code readlabilty, Each method contains inner fuctions to perfrom actions for that
    particular method """

    route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                       "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

    prefix_to_mask = {"/30": "255.255.255.252", "/29": "255.255.255.248", "/28": "255.255.255.240",
                       "/27": "255.255.255.224", "/26": "255.255.255.192", "/25": "255.255.255.128",
                       "/24": "255.255.255.0", "/23": "255.255.254.0", "/22": "255.255.252.0", "/21": "255.255.248.0",
                       "/20": "255.255.240.0", "/19": "255.255.224.0", "/18": "255.255.192.0", "/17": "255.255.128.0",
                       "/16": "255.255.0.0", "/15": "255.254.0.0", "/14": "255.252.0.0","/13": "255.248.0.0",
                       "/12": "255.240.0.0", "/11": "255.224.0.0", "/10": "255.192.0.0", "/9": "255.128.0.0",
                       "/8": "255.0.0.0" , "/0": "0.0.0.0", "/31": "255.255.255.254", "/32": "255.255.255.255"}

    def __init__(self, host=None, username=None, password=None, enable=None, **enale):

        """Initialize instance attributes. Credentials
        _host
        _username
        _password
        routes = maintains nested parse route data,VRF, route particulars
        _routing = Parent to routes dictionary, maintans VDC Key
        prefix = maintains current prefix in the loop
        protocol = maintains routing protocol until the next line provides the next protocol
        initialize_class_methods() = initializes class methods
        """

        self._host = host
        self._username = username
        self._password = password
        self.netmiko_connection = None
        self.routes = collections.defaultdict(list)
        self._routing = {}
        self.prefix = None
        self.protocol = None

        try:
            self.enable = enable["enable"]
        except TypeError:
            self.enable = None

        self.initialize_class_methods()  # Initiate class methods
        self.database()

    def initialize_class_methods(self):

        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        def find_prefix(prefix: str) -> None:

            """Find the netmask in the route entry and convert to to CIDR. This allows the program to read the massk
            as designed. Uses class variable to match the whole mask to CIDR"""

            # Find Routes
            try:
                if re.findall(r'(?<=\s)255.*(?=\s)', prefix):
                    mask = re.findall(r'(?<=\s)255.*(?=\s)', prefix)
                    prefix_length = [k for k, v in Routing_Asa.prefix_to_mask.items() if mask[0] == v]
                    network_id = re.findall(r'(?<=\s)[0-9].*(?=\s[0-9])', prefix)
                    self.prefix = network_id[0] + prefix_length[0]
            except IndexError as error:
                pass

            # Default Route
            try:
                if re.findall(r'(?<=\s)0.0.0.0(?=\s)', prefix):
                    mask = re.findall(r'(?<=\s)0.0.0.0(?=\s)', prefix)
                    prefix_length = [k for k, v in Routing_Asa.prefix_to_mask.items() if mask[0] == v]
                    if "0.0.0.0" in prefix:
                        self.prefix = "0.0.0.0/0"
                    else:
                        pass
            except IndexError:
                pass

            # Connected Routes
            try:
                if re.findall(r'(?<=\s)255.*(?=\sis)', prefix):
                    mask = re.findall(r'(?<=\s)255.*(?=\sis)', prefix)
                    prefix_length = [k for k, v in Routing_Asa.prefix_to_mask.items() if mask[0] == v]
                    network_id = re.findall(r'(?<=\s)[0-9].*(?=\s[0-9])', prefix)
                    self.prefix = network_id[0] + prefix_length[0]
            except IndexError as error:
                pass

        # Check to see if self.enable has been assigned. Create connection object, save object to instance attribute

        if self.enable is None:
            create_netmiko_connection = connect_with.netmiko_w_enable(self.host, self.username, self.password)
        else:
            create_netmiko_connection = connect_with.netmiko_w_enable(self.host, self.username, self.password,
                                                                        enable["enable"])
        self.netmiko_connection = create_netmiko_connection

        # Get route table using netmiko instance attribute.
        route_entries = get_routing_table(self.netmiko_connection)
        line = re.findall(r'.*(?=\n)', route_entries)
        get_last_line = re.findall(r'.*$', route_entries)
        line.append(get_last_line[0])

        for routing_entry in line:

            # Find the prefix in the current line/routing entry
            find_prefix(routing_entry)

            if self.prefix is None:
                continue
            elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', self.prefix):
                self.protocols_and_metrics(routing_entry)
                self.slash_ten_and_up(routing_entry)
            elif re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', self.prefix):
                self.protocols_and_metrics(routing_entry)
                self.slash_nine_and_below(routing_entry)
            else:
                self.protocols_and_metrics(routing_entry)
                self.no_mask(routing_entry)

        self._routing["None"] = self.routes
        self.routes = collections.defaultdict(list)


    def slash_ten_and_up(self, routing_entry: str) -> None:

        """Gets routes with a mask /10 +, writes next hope to instance attribute self.routes"""

        route_details = {"next-hop": None, "zone": None, "metric": None}

        def outgoing_interfaces():

            if re.findall(r'(?<=,\s)[a-zA-Z].*', routing_entry):
                outgoing_interface = re.findall(r'(?<=,\s)[a-zA-Z].*$', routing_entry)
                route_details["zone"] = outgoing_interface[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)
            else:
                pass

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

    def slash_nine_and_below(self, routing_entry: str) -> None:

        """Gets routes with a mask - /10 , writes next hope to instance attribute self.routes"""

        route_details = {"next-hop": None, "zone": None, "metric": None}

        def outgoing_interfaces():

            if re.findall(r'(?<=,\s)[a-zA-Z].*', routing_entry):
                outgoing_interface = re.findall(r'(?<=,\s)[a-zA-Z].*', routing_entry)
                route_details["zone"] = outgoing_interface[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)
            else:
                pass

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

    def no_mask(self, routing_entry: str) -> None:

        """Gets routes with no mask/show in the routing table as \"subnetted\""""

        route_details = {"next-hop": None, "zone": None, "metric": None}

        def outgoing_interfaces():

            if re.findall(r'(?<=,\s)[a-zA-Z].*', routing_entry):
                outgoing_interface = re.findall(r'(?<=,\s)[a-zA-Z].*', routing_entry)
                route_details["zone"] = outgoing_interface[0]
                if route_details in self.routes[self.prefix]:
                    pass
                else:
                    self.routes[self.prefix].append(route_details)
            else:
                pass

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

    def protocols_and_metrics(self, routing_entry: str) -> None:

        """Gets route type, Parent protocol/Child type. Ex. OSPF, or OSPF E2. """

        route_details = {"protocol": None, "admin-distance": None}
        find_protocol = [protocol for protocol in Routing_Asa.route_protocols if protocol in routing_entry[0:5]]

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

        if re.findall(r'(?<=directly\s)connected(?=,)', routing_entry):
            route_details["admin-distance"] = 0
            route_details["protocol"] = "C"
            write_to_dictionary()

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

        for vrf, values_vrf in self._routing.items():
            entry = 0
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

    def database(self):

        # Initiate databse object
        db_write = databaseops.RoutingDatabase()

        for vrf, values_vrf in self._routing.items():
            for prefix, val_prefix in values_vrf.items():
                routes_attributes = []
                for attributes in val_prefix:
                    for attribute, value in attributes.items():
                        routes_attributes.append(value)

                # Get the length of the route_attributes list. Each will be a fixed length. Combine next hops, interface, metrics
                # and tags. This is so we dont have to modify DB rows/columns.

                if len(routes_attributes) == 5:

                    # Check for tag in route entry, no tag assign None to variable
                    try:
                        tag = attributes[8]
                    except KeyError:
                        tag = None

                    try:
                        db_write.db_update_asa(vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                  routes_attributes[2], routes_attributes[3], routes_attributes[4],
                                                  tag)
                    except (IndexError, TypeError) as error:
                        print(error)
                        pass

                if len(routes_attributes) == 8:

                    # Check for tag in route entry, no tag assign None to variable
                    try:
                        tag = attributes[8]
                    except KeyError:
                        tag = None

                    try:
                        next_hops = routes_attributes[2] + ", " + routes_attributes[5]
                        route_metrics = routes_attributes[4] + ", " + routes_attributes[7]
                        interfaces = routes_attributes[3] + ", " + routes_attributes[6]
                        db_write.db_update_asa(vrf, prefix, routes_attributes[0], routes_attributes[1],
                                                  next_hops, interfaces, route_metrics, tag)
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
    def routing(self) -> None:
        return self._routing




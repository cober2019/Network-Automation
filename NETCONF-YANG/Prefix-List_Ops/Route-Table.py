from netmiko import ConnectHandler, ssh_exception
import re

class Routing:
    
    """Collect Routing table details using netmiko and re. Method will return a dictionary with route, protocol, next-hop"""
    
    def __init__(self, host=None, username=None, password=None):

        self.host= host
        self.username = username
        self.password = password
        self.routing_prefixes = {}

    def get_routing_table(self):

        """Gets all subnets and protocol/route types in the device routing table. This is used as check when
        a new prefix wants to be inserted into a list"""

        credentials = {
            'device_type': 'cisco_ios',
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'session_log': 'my_file.out'}

        try:
            device_connect = ConnectHandler(**credentials)
        except ssh_exception.AuthenticationException as error:
            raise ConnectionError("Could not connect to device {}".format(self.host))
            pass

        terminal_length = device_connect.send_command(command_string="terminal length 0")
        get_routes = device_connect.send_command(command_string="show ip route")
        exit = device_connect.send_command(command_string="exit", expect_string="")

        line = re.findall(r'.*(?=\n)', get_routes)
        for i in line:
            route_details = {}

            # Find entries eith mask /10-32

            try:
                if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', i):

                    if re.findall(r'.*[0-9]\.*[0-9]\..*[0-9]\..*[0-9]/[1-9][0-9]', i):
                        generic = re.findall(r'.*[0-9]\.*[0-9]\.*[0-9]\.*[0-9]/[1-9][0-9]', i)
                    if re.findall(r'\b[0-9].*\.[0-9].*\.[0-9].*\.[0-9].*/[1-9][0-9]\b', generic[0]):
                        prefix = re.findall(r'\b[0-9].*\.[0-9].*\.[0-9].*\.[0-9].*/[1-9][0-9]\b', generic[0])
                    if re.findall(r'\b[a-zA-Z]\b', generic[0]):
                        route_type = re.findall(r'[a-zA-Z]', generic[0])
                        route_details["protocol"] = route_type[0]
                    if re.findall(r'\b[a-zA-Z]\s[A-Z][0-9]\b', generic[0]):
                        route_type = re.findall(r'\b[a-zA-Z]\s[A-Z][0-9]\b', generic[0])
                        route_details["protocol"] = route_type[0]
                    if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*[0-9](?=,)', i):
                        next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', i)
                        route_details["next-hop"] = next_hop[0]
                    if re.findall(r'(?<=directly\s)connected(?=,)', i):
                        route_details["next-hop"] = "connected"
                    if re.findall(r'(?<=variably\s)subnetted(?=,)', i):
                        route_details["next-hop"] = "variably subnetted"
                    if re.findall(r'(?<=is\s)subnetted(?=,)', i):
                        route_details["next-hop"] = "subnetted"

                    try:
                        self.routing_prefixes[prefix[0].replace(" ", "")] = route_details
                    except UnboundLocalError:
                        pass

            except IndexError:
                pass

            # Find entries with mask /0-9

            try:
                if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]/[1-9]\b', i):

                    if re.findall(r'.*[0-9]\.*[0-9]\..*[0-9]\..*[0-9]/[1-9]', i):
                        generic = re.findall(r'.*[0-9]\.*[0-9]\.*[0-9]\.*[0-9]/[1-9]', i)
                    if re.findall(r'\b[0-9].*\.[0-9].*\.[0-9].*\.[0-9].*/[1-9]\b', generic[0]):
                        prefix = re.findall(r'\b[0-9].*\.[0-9].*\.[0-9].*\.[0-9].*/[1-9]\b', generic[0])
                    if re.findall(r'\b[a-zA-Z]\b', generic[0]):
                        route_type = re.findall(r'[a-zA-Z]', generic[0])
                        route_details["protocol"] = route_type[0]
                    if re.findall(r'\b[a-zA-Z]\s[A-Z][0-9]\b', generic[0]):
                        route_type = re.findall(r'\b[a-zA-Z]\s[A-Z][0-9]\b', generic[0])
                        route_details["protocol"] = route_type[0]
                    if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*[0-9](?=,)', i):
                        next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', i)
                        route_details["next-hop"] = next_hop[0]
                    if re.findall(r'(?<=directly\s)connected(?=,)', i):
                        route_details["next-hop"] = "connected"
                    if re.findall(r'(?<=variably\s)subnetted(?=,)', i):
                        route_details["next-hop"] = "variably subnetted"
                    if re.findall(r'(?<=is\s)subnetted(?=,)', i):
                        route_details["next-hop"] = "subnetted"

                    try:
                        self.routing_prefixes[prefix[0].replace(" ", "")] = route_details
                    except UnboundLocalError:
                        pass

            except IndexError:
                pass

            # Find entries no subnet mask

            try:
                if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9](?=\s)', i):
                    if re.findall(r'.*[0-9]\.*[0-9]\..*[0-9]\..*[0-9](?=\s)', i):
                        generic = re.findall(r'.*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=\s)', i)
                        prefix = re.findall(r'\b[0-9].*\.[0-9].*\.[0-9].*\..*[0-9](?=\s)', i)
                    if re.findall(r'\b[a-zA-Z]\b', generic[0]):
                        route_type = re.findall(r'[a-zA-Z]', generic[0])
                        route_details["protocol"] = route_type[0]
                    if re.findall(r'\b[a-zA-Z]\s[A-Z][0-9]\b', generic[0]):
                        route_type = re.findall(r'\b[a-zA-Z]\s[A-Z][0-9]\b', generic[0])
                        route_details["protocol"] = route_type[0]
                    if re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\..*[0-9]\..*[0-9](?=,)', i):
                        next_hop = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', i)
                        route_details["next-hop"] = next_hop[0]
                    if re.findall(r'(?<=directly\s)connected(?=,)', i):
                        route_details["next-hop"] = "connected"
                    if re.findall(r'(?<=variably\s)subnetted(?=,)', i):
                        route_details["next-hop"] = "variably subnetted"
                    if re.findall(r'(?<=is\s)subnetted(?=,)', i):
                        route_details["next-hop"] = "subnetted"

                    try:
                        self.routing_prefixes[prefix[0]] = route_details
                    except UnboundLocalError:
                        pass

            except IndexError:
                pass

            # Find lines that are equal routes, no protocol on line just next hop

            try:
                if re.findall(r"^\s.*(?=\[)", i):
                    find_hops = re.findall(r'(?<=via\s).*[0-9]\.*[0-9]\.*[0-9]\.*[0-9](?=,)', i)
                    self.routing_prefixes[prefix[0]]["next-hop"] = find_hops[0]
            except (IndexError, TypeError):
                pass

            # Save last prefix just in case the next hopd are on the next line(s). We can still use the prefix as the
            # key in the dictionary. Usage - self.routing_prefixes[prefix[0]]["next-hop"] = find_hops[0]

            try:
                prefix = prefix
            except (UnboundLocalError):
                pass

        return self.routing_prefixes


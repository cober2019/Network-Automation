import ipaddress
from netmiko import ConnectHandler, ssh_exception
from socket import gaierror
from ncclient import manager
import xmltodict
import collections
import re

class IpOps:

    """IpOps class is ised for ip prefix-list operations:

    1. View prefix-list
    2. Search via length
    3. Search for overlapping
    4  Search by prefix
    """

    def __init__(self, host=None, username=None, password=None):

        self.prefix_list = collections.defaultdict(list)
        self.overlapp_prefixes = collections.defaultdict(list)
        self.prefix_length = collections.defaultdict(list)
        self.routing_prefixes = collections.defaultdict(list)
        self.username = username
        self.password = password
        self.host = host
        self.prefixes = []
        self._device_connect()
        self._ip_prefix_list()

    def _device_connect(self):

        """Device login using NCC Client. One login is complete the program will _collect_data(self)"""

        try:

            self.session = manager.connect(host=self.host, port=830, timeout=3, username=self.username, password=self.password,
                                           device_params={'name': 'csr'})

        except manager.NCClientError:
            raise ConnectionError("Connection to {} failed".format(self.host))
        except AttributeError:
            raise ConnectionError("Connection to {} failed".format(self.host))
        except gaierror:
            raise ConnectionError("Connection to {} failed".format(self.host))
        else:
            return self.session

    def _ip_prefix_list(self):

        """Get all prefix-list entries for a device.

        Here's how to access the data:

        for k, v in get.items():
            print("\n")
            print(k)
            for v in v:
                print(v["seq"], v["action"], v["prefix"])"""

        init_dict_breakdown = {}
        filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <ip>
                        <prefix-list/>
                        </ip>
                        </native>
                        </filter>"""

        intf_info = self.session.get(filter)
        intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
        prefix_list = intf_dict["native"]["ip"]["prefix-list"]["prefixes"]

        for i in prefix_list:
            init_dict_breakdown[i["name"]] = i["seq"]
        for k, v in init_dict_breakdown.items():
            if not isinstance(v, list):
                if v["action"] == "deny":
                    self._prefix_parse(k=k, v=v, action="deny")
                elif v["action"] == "permit":
                    self._prefix_parse(k=k, v=v, action="permit")
            else:
                for v in v:
                    if v["action"] == "deny":
                        self._prefix_parse(k=k, v=v, action="deny")
                    elif v["action"] == "permit":
                        self._prefix_parse(k=k, v=v, action="permit")

    def _prefix_parse(self, k=None, v=None, action=None):

        """Parse prefix-list entry and store to dictionary"""

        entry_details = {}
        entry_details["action"] = action

        try:
            entry_details["prefix"] = v["ip"]
            entry_details["seq"] = v["no"]
        except KeyError:
            pass
        try:
            entry_details["prefix"] = v[action]["ip"]
            entry_details["seq"] = v["no"]
        except KeyError:
            pass
        try:
            entry_details["length_ge"] = v[action]["ge"]
        except (KeyError, TypeError):
            pass
        try:
            entry_details["length_le"] = v[action]["le"]
        except (KeyError, TypeError):
            pass
        try:
            entry_details["length_ge"] = v[action]["ge"]
            entry_details["length_le"] = v[action]["le"]
        except (KeyError, TypeError):
            pass

        self.prefix_list[k].append(entry_details)

    def view_prefix_list(self):

        """View current prefix-list"""

        for k, v in self.prefix_list.items():
            print("\n")
            print(k)
            for v in v:
                try:
                    if "length_ge" in v and not "length_le" in v:
                        print(v["seq"], v["action"], v["prefix"], v["length_ge"])
                except KeyError:
                    pass

                try:
                    if "length_le" in v and "length_ge" not in v:
                        print(v["seq"], v["action"], v["prefix"], v["length_le"])
                except KeyError:
                    pass

                try:
                    if "length_ge" in v and "length_le" in v:
                        print(v["seq"], v["action"], v["prefix"], v["length_ge"], v["length_le"])
                except KeyError:
                    pass
                try:
                    if "length_ge" not in v and "length_le" not in v:
                        print(v["seq"], v["action"], v["prefix"])
                except KeyError:
                    pass

    def find_prefix_length(self, length=None):

        """ Finds prefix with a certain length. Takes one argument, length ex. \"25\". Return dictionationary
        Use view_prefix_length() method to get formatted output"""

        tempt_dict = {}
        for k, v in self.prefix_list.items():
            if isinstance(v, list):
                for v in v:
                    prefix_find = re.findall(r'(?<=/).*$', v["prefix"])
                    if length in prefix_find:
                        tempt_dict["seq"] = v["seq"]
                        tempt_dict["prefix"] = v["prefix"]
                        self.prefix_length[k].append(tempt_dict)
                        tempt_dict = {}
                    else:
                        pass
            else:
                prefix_find = re.findall(r'(?<=/).*$', v["prefix"])
                if length in prefix_find:
                    tempt_dict["seq"] = v["seq"]
                    tempt_dict["prefix"] = v["prefix"]
                    self.prefix_length[k].append(tempt_dict)
                    tempt_dict = {}
                else:
                    pass

        return self.prefix_length

    def duplicate_prefix(self):

        prefixes = []
        dup_prefixes = collections.defaultdict(list)

        for k, v in self.prefix_list.items():
            if isinstance(v, list):
                for v in v:
                    prefixes.append(v["prefix"])
            else:
                prefixes.append(v["prefix"])

        dups = [k for k, v in collections.Counter(prefixes).items() if v > 1]

        for i in dups:
            find_prefixes = self.find_prefix(prefix=i)
            dup_prefixes["prefixes"].append(find_prefixes)

        return  dup_prefixes

    def find_prefix(self, prefix=None):

        prefixes = collections.defaultdict(list)
        tempt_dict = {}

        for k, v in self.prefix_list.items():
            if isinstance(v, list):
                for v in v:
                    if prefix == v["prefix"]:
                        tempt_dict["seq"] = v["seq"]
                        tempt_dict["prefix"] = v["prefix"]
                        prefixes[k].append(tempt_dict)
                        tempt_dict = {}
                    else:
                        pass
            else:
                if prefix == v["prefix"]:
                    tempt_dict["seq"] = v["seq"]
                    tempt_dict["prefix"] = v["prefix"]
                    prefixes[k].append(tempt_dict)
                    tempt_dict = {}
                else:
                    pass

        return prefixes

    def find_overlapping_prefixes(self):

        """This method finds overlapping prefixes. The loop logic is as follows:

                1. Unpack k, v. K = prefix-list name. V = prefix-list configuration
                2. Unpack v in v. Each v is a part of the prefix entries configuration
                3. Check if GE or LE or both are present in v (prefix-list configuration)
                4. Get network address
                5. If length (ge or le) and create range
                6. Add 1 to ge or subtract 1 from le for each CIDR in range. Concatenate network address with GE/LE and
                   everyone one in between, below, or above
                7. For each prefix in list, loops through all prefixes in list.
                8. Check to see if they overlap
                9. Store to list/dictionary

                Returns Ordered dictionary. For formatted output use view_overlapping_prefixes()"""

        remove_dups = list(dict.fromkeys(self.prefixes))
        prefix_list = []

        for k, v in self.prefix_list.items():
            for v in v:
                list_networks = []
                try:
                    if "length_ge" in v and not "length_le" in v:
                        network_address = str(ipaddress.IPv4Network(v["prefix"]).network_address)

                        int_prefix = int(v["length_ge"])
                        prefix_range = range(int_prefix, 32 + 1)

                        for i in prefix_range:
                           list_networks.append(network_address + "/" + str(int_prefix))
                           int_prefix = int_prefix + 1

                        for network in remove_dups:
                            prefix_dict = collections.OrderedDict()
                            for i in list_networks:
                                try:
                                    if ipaddress.IPv4Network(network).overlaps(ipaddress.IPv4Network(i)):
                                        prefix_list.append(i)
                                    else:
                                        pass
                                except ValueError:
                                    pass

                            if not prefix_list:
                                pass
                            else:
                                prefix_dict["prefix"] = network
                                prefix_dict["overlapping-seq"] = v["seq"]
                                prefix_dict["ge"] = v["length_ge"]
                                prefix_dict["le"] = "32"
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self.overlapp_prefixes[k].append(prefix_dict)
                                prefix_list = []

                except KeyError:
                    pass

                try:
                    if "length_le" in v and "length_ge" not in v:
                        network_address = str(ipaddress.IPv4Network(v["prefix"]).network_address)

                        int_prefix = int(v["length_le"])
                        prefix_range = range(0, int_prefix)

                        for i in prefix_range:
                           list_networks.append(network_address + "/" + str(int_prefix))
                           int_prefix = int_prefix - 1

                        for network in remove_dups:
                            prefix_dict = collections.OrderedDict()
                            for i in list_networks:
                                try:
                                    if network == i:
                                        pass
                                    elif ipaddress.IPv4Network(network).overlaps(ipaddress.IPv4Network(i)):
                                        prefix_list.append(i)
                                    else:
                                        pass
                                except ValueError:
                                    pass

                            if not prefix_list:
                                pass
                            else:
                                prefix_dict["prefix"] = network
                                prefix_dict["overlapping-seq"] = v["seq"]
                                prefix_dict["le"] = v["length_le"]
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self.overlapp_prefixes[k].append(prefix_dict)
                                prefix_list = []
                except KeyError:
                    pass

                try:
                    if "length_ge" in v and "length_le" in v:
                        network_address = str(ipaddress.IPv4Network(v["prefix"]).network_address)

                        start_prefix = int(v["length_ge"])
                        end_prefix = int(v["length_le"])
                        prefix_range = range(start_prefix, end_prefix + 1)

                        for i in prefix_range:
                           list_networks.append(network_address + "/" + str(start_prefix))
                           start_prefix = start_prefix + 1

                        for network in remove_dups:
                            prefix_dict = collections.OrderedDict()
                            for i in list_networks:
                                try:
                                    if network == i:
                                        pass
                                    elif ipaddress.IPv4Network(network).overlaps(ipaddress.IPv4Network(i)):
                                        prefix_list.append(i)
                                    else:
                                        pass
                                except ValueError:
                                    pass

                            if not prefix_list:
                                pass
                            else:
                                prefix_dict["prefix"] = network
                                prefix_dict["overlapping-seq"] = v["seq"]
                                prefix_dict["ge"] = v["length_ge"]
                                prefix_dict["le"] = v["length_le"]
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self.overlapp_prefixes[k].append(prefix_dict)
                                prefix_list = []
                except KeyError:
                    pass

                try:
                    if "length_ge" not in v and "length_le" not in v:
                        list_networks.append(v["prefix"])

                        for network in remove_dups:
                            prefix_dict = collections.OrderedDict()
                            for i in list_networks:
                                try:
                                    if network == i:
                                        pass
                                    elif ipaddress.IPv4Network(network).overlaps(ipaddress.IPv4Network(i)):
                                        prefix_list.append(i)
                                    else:
                                        pass
                                except ValueError:
                                    pass

                            if not prefix_list:
                                pass
                            else:
                                prefix_dict["prefix"] = network
                                prefix_dict["overlapping-seq"] = v["seq"]
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self.overlapp_prefixes[k].append(prefix_dict)
                                prefix_list = []
                except KeyError:
                    pass

    def view_overlapping_prefixes(self):

        """Print overlapping prefixes. For dictionary output use find_overlapping_prefixes()"""

        for k, v in self.overlapp_prefixes.items():
            print(k)
            for v in v:
                print("Prefix: {}".format(v["prefix"]))
                print("Overlapping Sequence: {}".format(v["overlapping-seq"]))
                try:
                    print("Range: GE: {}".format(v["ge"]))
                except KeyError:
                    pass
                try:
                    print("Range: LE {}".format(v["le"]))
                except KeyError:
                    pass
                print("Overlapping Prefixes: {}".format(", ".join(v["overlapping-prefixes"])))
                print("\n")

    def view_prefix_length(self):

        """Prints output from find_prefix_length() method"""

        for k, v in self.prefix_length.items():
            print("List: {}".format(k))
            for v in v:
                print("Sequence: {} Prefix: {}".format(v["seq"], v["prefix"]))
            print("\n")

    def send_prefix_list(self, **kwargs):

        """Send prefix statement to device. Based on kwargs passed to method a specific template will be selected. The following
        conditions need to be met for the configuration to send:

        1. Check to see if self.routing_prefixes is empty. Ask to pass check. If not empty, see if the prefix is in routing,
           and check to see if external, warn user.
        1. Sequence must be unique. Raise exception if the check fails
        2. Prefix must be unique. Rise exception if the check fails
        3. The new prefix can't overlap with a current prefix (exact prefix and ge/le check)"""

        external_routes = ("O E1", "O E2", "D EX", "B", "O N1", "O N2", "i L2")

        if not self.routing_prefixes:
            warning = input("NETMIKO routing table empty! Do you want to bypass routing check?\n").lower()
            if warning == "yes":
                pass
            elif warning == "no":
                raise ValueError("Prefix configuration aborted")
            else:
                raise ValueError("Invalid Input!")
        else:
            for k, v in self.routing_prefixes.items():
                if kwargs["prefix"] == k:
                    if v["protocol"] in external_routes:
                        warning = input("Prefix is external/not local, Are you sure you want to add (yes/no)?\n").lower()
                        if warning == "yes":
                            continue
                        elif warning == "no":
                            raise ValueError("Prefix configuration aborted")
                        else:
                            raise ValueError("Invalid Input!")
                    else:
                        pass
                else:
                    continue

        for k, v in self.prefix_list.items():
            for v in v:
                if kwargs["name"] == k and kwargs["seq"] == v["seq"]:
                    raise ValueError("Sequence Exist")
                if kwargs["name"] == k and kwargs["prefix"] == v["prefix"]:
                    raise ValueError("Prefix Exist")

        try:
            if "ge" in kwargs and "le" not in kwargs:
                self._find_dups_internal(prefix=kwargs["prefix"], ge=kwargs["ge"])
                filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip><prefix-list><prefixes>
                            <name>""" + kwargs["name"] + """</name>
                            <seq>
                            <no>""" + kwargs["seq"] + """</no> 
                            <""" + kwargs["action"] + """>
                            <ip>""" + kwargs["prefix"] + """</ip> 
                            <ge>""" + kwargs["ge"] + """</ge> 
                            </""" + kwargs["action"] + """>
                            </seq>
                            </prefixes></prefix-list></ip></native></config>"""
        except KeyError:
            pass

        try:
            if "le" in kwargs and "ge" not in kwargs:
                self._find_dups_internal(prefix=kwargs["prefix"], ge=kwargs["le"])
                filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip><prefix-list><prefixes>
                            <name>""" + kwargs["name"] + """</name>
                            <seq>
                            <no>""" + kwargs["seq"] + """</no> 
                            <""" + kwargs["action"] + """> 
                            <ip>""" + kwargs["prefix"] + """</ip>
                            <le>""" + kwargs["le"] + """</le>
                            </""" + kwargs["action"] + """>
                            </seq>
                            </prefixes></prefix-list></ip></native></config>"""
        except KeyError:
            pass

        try:
            if "le" in kwargs and "ge" in kwargs:
                self._find_dups_internal(prefix=kwargs["prefix"], ge=kwargs["ge"], le=kwargs["le"])
                filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip><prefix-list><prefixes>
                            <name>""" + kwargs["name"] + """</name>
                            <seq>
                            <no>""" + kwargs["seq"] + """</no>
                            <""" + kwargs["action"] + """>
                            <ip>""" + kwargs["prefix"] + """</ip>
                            <ge>""" + kwargs["ge"] + """</ge>
                            <le>""" + kwargs["le"] + """</le>
                            </""" + kwargs["action"] + """>
                            </seq>
                            </prefixes></prefix-list></ip></native></config>"""
        except KeyError as error:
            print(error)
            pass

        try:
            if "le" not in kwargs and "ge" not in kwargs:
                self._find_dups_internal(prefix=kwargs["prefix"])
                filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip><prefix-list><prefixes>
                            <name>""" + kwargs["name"] + """</name>
                            <seq>
                            <no>""" + kwargs["seq"] + """</no> 
                            <""" + kwargs["action"] + """>
                            <ip>""" + kwargs["prefix"] + """</ip>
                            </""" + kwargs["action"] + """>
                            </seq>
                            </prefixes></prefix-list></ip></native></config>"""
        except KeyError:
            pass


        self.session.edit_config(config=filter, target="running")
        self.prefix_list.clear()
        self._ip_prefix_list()

        return self.view_prefix_list()

    def _find_dups_internal(self, **kwargs):

        """Finds overlapping prefixes when creating a new prefix statement. An error will be raised if new
        prefix overlaps with a current sequence in the same list

        The logic is to unpack all prefix ranges between the le, ge, or both. Then compare all prefixes
        to the newly created list, list_networks"""

        remove_dups = list(dict.fromkeys(self.prefixes))
        list_networks = []

        list_networks.append(kwargs["prefix"])

        if "length_ge" in kwargs and "length_le" not in kwargs:
            network_address = str(ipaddress.IPv4Network(kwargs["prefix"]).network_address)

            int_prefix = int(kwargs["ge"])
            prefix_range = range(int_prefix, 32 + 1)

            for i in prefix_range:
                list_networks.append(network_address + "/" + str(int_prefix))
                int_prefix = int_prefix + 1

        if "length_le" in kwargs and "length_ge" not in kwargs:

            network_address = str(ipaddress.IPv4Network(kwargs["prefix"]).network_address)

            start_prefix = int(kwargs["ge"])
            end_prefix = int(kwargs["le"])
            prefix_range = range(start_prefix, end_prefix + 1)

            for i in prefix_range:
                list_networks.append(network_address + "/" + str(start_prefix))
                start_prefix = start_prefix + 1

        if "length_ge" not in kwargs and "length_le" not in kwargs:
            list_networks.append(kwargs["prefix"])

        for network in remove_dups:
            for i in list_networks:
                if ipaddress.IPv4Network(network).overlaps(ipaddress.IPv4Network(i)):
                    raise ValueError("{} overlapps with {}".format(kwargs["prefix"], network))

    def get_routing_table(self):

        """Gets all subnets and protocol/route types in the device routing table. This is used as check when
        a new prefix wants to be inserted into a list"""

        self._clear_attr_routes()
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
                        route_details["next-hop"] ="connected"
                    if re.findall(r'(?<=variably\s)subnetted(?=,)', i):
                        route_details["next-hop"] ="variably subnetted"
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
                        route_details["next-hop"] ="connected"
                    if re.findall(r'(?<=variably\s)subnetted(?=,)', i):
                        route_details["next-hop"] ="variably subnetted"
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
                        route_details["next-hop"] ="connected"
                    if re.findall(r'(?<=variably\s)subnetted(?=,)', i):
                        route_details["next-hop"] ="variably subnetted"
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

    def compile_new_prefixes(self):

        """ Clear prefix list dictionary attributes. No need to create another object instance"""

        self.prefix_list.clear()
        self.prefix_length.clear()
        self.overlapp_prefixes.clear()
        self._ip_prefix_list()

    def _clear_attr_routes(self):

        """Clears routing table dictionary attributes"""

        self.routing_prefixes.clear()












import ipaddress
from typing import Any, Dict, DefaultDict
from socket import gaierror
from ncclient import manager
from Software import IOSXE
import xmltodict
import collections
import re


class IpOpsIsr:
    """IpOps class is ised for ip prefix-list operations:

    1. View prefix-list
    2. Search via length
    3. Search for overlapping
    4  Search by prefix
    """

    def __init__(self, host=None, username=None, password=None):

        self.username = username
        self.password = password
        self.host = host

        self._prefix_list = collections.defaultdict(list)
        self._overlapping_prefixes = collections.defaultdict(list)
        self.prefix_check = collections.defaultdict(list)
        self.prefixes = []
        self.routing_table = None
        self.session = None
        self.device_connect()
        self.ip_prefix_list()

    def device_connect(self) -> object:

        """Device login using NCC Client. One login is complete the program will _collect_data(self)"""

        try:

            self.session = manager.connect(host=self.host, port=830, timeout=3, username=self.username,
                                           password=self.password,
                                           device_params={'name': 'csr'})

        except manager.NCClientError:
            raise ConnectionError("Connection to {} failed".format(self.host))
        except AttributeError:
            raise ConnectionError("Connection to {} failed".format(self.host))
        except gaierror:
            raise ConnectionError("Connection to {} failed".format(self.host))
        else:
            return self.session

    def ip_prefix_list(self) -> None:

        init_dict_breakdown = {}
        xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <ip>
                        <prefix-list/>
                        </ip>
                        </native>
                        </filter>"""

        intf_info = self.session.get(xml_filter)
        intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]
        prefix_list = intf_dict["native"]["ip"]["prefix-list"]["prefixes"]

        if isinstance(prefix_list, list):
            for i in prefix_list:
                init_dict_breakdown[i["name"]] = i["seq"]
        else:
            for k, v in prefix_list.items():
                init_dict_breakdown[prefix_list["name"]] = prefix_list["seq"]

        for k, data in init_dict_breakdown.items():
            if not isinstance(data, list):
                if "deny" in data:
                    self.prefix_parse(k=k, v=data, action="deny")
                elif "permit" in data:
                    self.prefix_parse(k=k, v=data, action="permit")
            else:
                for statment in data:
                    if "deny" in statment:
                        self.prefix_parse(k=k, v=statment, action="deny")
                    elif "permit" in statment:
                        self.prefix_parse(k=k, v=statment, action="permit")

    def prefix_parse(self, k: Dict[str, str] = None, v: Dict[str, str] = None, action: Dict[str, str] = None) -> None:

        """Parse prefix-list entry and store to dictionary"""

        entry_details = {"action": action}

        try:
            entry_details["prefix"] = v["ip"]
            self.prefixes.append(v["ip"])
            entry_details["seq"] = v["no"]
        except KeyError:
            pass
        try:
            entry_details["prefix"] = v[action]["ip"]
            self.prefixes.append(v[action]["ip"])
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

        self._prefix_list[k].append(entry_details)

    def find_duplicate_prefix(self):

        prefixes = []

        for k, structure in self.prefix_list.items():
            if isinstance(structure, list):
                for entry in structure:
                    prefixes.append(entry["prefix"])
            elif isinstance(structure, dict):
                prefixes.append(structure["prefix"])

        dups = [k for k, v in collections.Counter(prefixes).items() if v > 1]

        for i in dups:
            for k, structure in self.prefix_list.items():
                for v in structure:
                    if i == v["prefix"]:
                        print("________________________")
                        print("\nPrefix: " + i)
                        print("\nList: " + k)
                        try:
                            if "length_ge" in v and "length_le" not in v:
                                print(v["seq"], v["action"], v["prefix"],
                                      v["length_ge"])
                        except KeyError:
                            pass

                        try:
                            if "length_le" in v and "length_ge" not in v:
                                print(v["seq"], v["action"], v["prefix"],
                                      v["length_le"])
                        except KeyError:
                            pass

                        try:
                            if "length_ge" in v and "length_le" in v:
                                print(v["seq"], v["action"], v["prefix"],
                                      v["length_ge"],
                                      v["length_le"])
                        except KeyError:
                            pass
                        try:
                            if "length_ge" not in v and "length_le" not in v:
                                print(v["seq"], v["action"], v["prefix"])
                        except KeyError:
                            pass

    def find_prefix(self, prefix=None):
        """Find specific prefix in prefix-list"""

        for k, structure in self.prefix_list.items():
            for v in structure:
                if prefix == v["prefix"]:
                    print("\nList: " + k)
                    print("Seq: " + v["seq"])
                    print("Prefix: " + v["prefix"])

    def find_overlapping_prefixes(self) -> None:

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

                Returns funtion. For formatted output use view_overlapping_prefixes()"""

        remove_dups = list(dict.fromkeys(self.prefixes))
        prefix_list = []

        for k, v in self._prefix_list.items():
            for statement in v:
                list_networks = []
                try:
                    if "length_ge" in v and "length_le" not in v:
                        network_address = str(ipaddress.IPv4Network(statement["prefix"]).network_address)

                        int_prefix = int(statement["length_ge"])
                        prefix_range = range(int_prefix, 32 + 1)

                        for _ in prefix_range:
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
                                prefix_dict["overlapping-seq"] = statement["seq"]
                                prefix_dict["ge"] = statement["length_ge"]
                                prefix_dict["le"] = "32"
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self._overlapping_prefixes[k].append(prefix_dict)
                                prefix_list = []

                except KeyError:
                    pass

                try:
                    if "length_le" in v and "length_ge" not in v:
                        network_address = str(ipaddress.IPv4Network(statement["prefix"]).network_address)

                        int_prefix = int(statement["length_le"])
                        prefix_range = range(0, int_prefix)

                        for _ in prefix_range:
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
                                prefix_dict["overlapping-seq"] = statement["seq"]
                                prefix_dict["le"] = statement["length_le"]
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self._overlapping_prefixes[k].append(prefix_dict)
                                prefix_list = []
                except KeyError:
                    pass

                try:
                    if "length_ge" in v and "length_le" in v:
                        network_address = str(ipaddress.IPv4Network(statement["prefix"]).network_address)

                        start_prefix = int(statement["length_ge"])
                        end_prefix = int(statement["length_le"])
                        prefix_range = range(start_prefix, end_prefix + 1)

                        for _ in prefix_range:
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
                                prefix_dict["overlapping-seq"] = statement["seq"]
                                prefix_dict["ge"] = statement["length_ge"]
                                prefix_dict["le"] = statement["length_le"]
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self._overlapping_prefixes[k].append(prefix_dict)
                                prefix_list = []
                except KeyError:
                    pass

                try:
                    if "length_ge" not in v and "length_le" not in v:
                        list_networks.append(statement["prefix"])

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
                                prefix_dict["overlapping-seq"] = statement["seq"]
                                prefix_dict["overlapping-prefixes"] = prefix_list
                                self._overlapping_prefixes[k].append(prefix_dict)
                                prefix_list = []
                except KeyError:
                    pass

        return self.view_overlapping_prefixes()

    def view_overlapping_prefixes(self) -> None:

        """Print overlapping prefixes. For dictionary output use find_overlapping_prefixes()"""

        for k, v in self._overlapping_prefixes.items():
            print(k)
            for prefix in v:
                print("Prefix: {}".format(prefix["prefix"]))
                print("Overlapping Sequence: {}".format(prefix["overlapping-seq"]))
                try:
                    print("Range: GE: {}".format(prefix["ge"]))
                except KeyError:
                    pass
                try:
                    print("Range: LE {}".format(prefix["le"]))
                except KeyError:
                    pass
                print("Overlapping Prefixes: {}".format(", ".join(prefix["overlapping-prefixes"])))
                print("\n")

    def send_prefix_list(self, **kwargs: str) -> Any:

        """Send prefix statement to device. Based on kwargs passed to method a specific template will be selected.
        The following conditions need to be met for the configuration to send:

        1. Check to see if self.routing_table is empty. Ask to pass check. If not empty, see if the prefix is in
        routing, and check to see if external, warn user. 1. Sequence must be unique. Raise exception if the check
        fails 2. Prefix must be unique. Rise exception if the check fails 3. The new prefix can't overlap with a
        current prefix (exact prefix and ge/le check) """

        route_protocols = ("L", "C", "S", "R", "M", "B", "D", "D EX", "O", "O IA", "O N1", "O N2", "O E1", "O E2", "i",
                           "i su", "i L1", "i l2", "*", "U", "o", "P", "H", "l", "a", "+", "%", "p", "S*")

        config_filter = None

        # Get local routing table.

        get_routing_table = IOSXE.RoutingIos(host=self.host, username=self.username, password=self.password)
        self.routing_table = get_routing_table.routing

        if not self.routing_table:

            warning = input("NETMIKO routing table empty! Do you want to bypass routing check?\n").lower()
            if warning == "yes":
                pass
            elif warning == "no":
                raise ValueError("Prefix configuration aborted")
            else:
                raise ValueError("Invalid Input!")

        else:

            # Check the local routing table to see if the prefix has been originated elsewhere

            for vrf, values_vrf in self.routing_table.items():
                for prefix, val_prefix in values_vrf.items():
                    if kwargs["prefix"] == prefix or kwargs["prefix"] in prefix:
                        for attributes in val_prefix:
                            for attribute, protocol in attributes.items():
                                if protocol in route_protocols:
                                    print(
                                        "\nDetails\nPrefix: {}\nProtocol: {}\n".format(prefix, attributes["protocol"]))
                                    warning = input(
                                        "Prefix is external/not local, Are you sure you want to add (yes/no): ").lower()
                                    if warning == "yes":
                                        break
                                    elif warning == "no":
                                        raise ValueError("Prefix configuration aborted")
                                    else:
                                        raise ValueError("Invalid Input!")
                                else:
                                    break
                        else:
                            continue
                    else:
                        continue

        # Check for duplicate sequences

        for k, v in self.prefix_check.items():
            for v in v:
                if kwargs["name"] == k and kwargs["seq"] == v["seq"]:
                    raise ValueError("Sequence Exist")
                if kwargs["name"] == k and kwargs["prefix"] == v["prefix"]:
                    raise ValueError("Prefix Exist")

        # Create configuration based off method arguments

        try:
            if "ge" in kwargs and "le" not in kwargs:
                self.find_dups_internal(prefix=kwargs["prefix"], ge=kwargs["ge"])
                config_filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                            <prefix-list><prefixes><name>""" + kwargs["name"] + """</name> 
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
                self.find_dups_internal(prefix=kwargs["prefix"], ge=kwargs["le"])
                config_filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                            <prefix-list><prefixes><name>""" + kwargs["name"] + """</name> 
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
                self.find_dups_internal(prefix=kwargs["prefix"], ge=kwargs["ge"], le=kwargs["le"])
                config_filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                            <prefix-list><prefixes><name>""" + kwargs["name"] + """</name> 
                            <seq>
                            <no>""" + kwargs["seq"] + """</no>
                            <""" + kwargs["action"] + """>
                            <ip>""" + kwargs["prefix"] + """</ip>
                            <ge>""" + kwargs["ge"] + """</ge>
                            <le>""" + kwargs["le"] + """</le>
                            </""" + kwargs["action"] + """>
                            </seq>
                            </prefixes></prefix-list></ip></native></config>"""
        except KeyError:
            pass

        try:
            if "le" not in kwargs and "ge" not in kwargs:
                self.find_dups_internal(prefix=kwargs["prefix"])
                config_filter = """<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                            <prefix-list><prefixes><name>""" + kwargs["name"] + """</name> 
                            <seq>
                            <no>""" + kwargs["seq"] + """</no> 
                            <""" + kwargs["action"] + """>
                            <ip>""" + kwargs["prefix"] + """</ip>
                            </""" + kwargs["action"] + """>
                            </seq>
                            </prefixes></prefix-list></ip></native></config>"""
        except KeyError:
            pass

        # Send configuration via NETCONF

        self.session.edit_config(config=config_filter, target="running")
        self._prefix_list.clear()
        self.ip_prefix_list()

        return self.view_prefix_list()

    def find_dups_internal(self, **kwargs: str) -> None:

        remove_dups = list(dict.fromkeys(self.prefixes))
        list_networks = []

        if "length_ge" in kwargs and "length_le" not in kwargs:
            network_address = str(ipaddress.IPv4Network(kwargs["prefix"]).network_address)

            int_prefix = int(kwargs["ge"])
            prefix_range = range(int_prefix, 32 + 1)

            for _ in prefix_range:
                list_networks.append(network_address + "/" + str(int_prefix))
                int_prefix = int_prefix + 1

        if "length_le" in kwargs and "length_ge" not in kwargs:

            network_address = str(ipaddress.IPv4Network(kwargs["prefix"]).network_address)

            start_prefix = int(kwargs["ge"])
            end_prefix = int(kwargs["le"])
            prefix_range = range(start_prefix, end_prefix + 1)

            for _ in prefix_range:
                list_networks.append(network_address + "/" + str(start_prefix))
                start_prefix = start_prefix + 1

        if "length_ge" not in kwargs and "length_le" not in kwargs:
            list_networks.append(kwargs["prefix"])

        for network in remove_dups:
            for i in list_networks:
                if ipaddress.IPv4Network(network).overlaps(ipaddress.IPv4Network(i)):
                    raise ValueError("{} overlapps with {}".format(kwargs["prefix"], network))

    def view_prefix_list(self) -> None:

        """View current prefix-list, match statemnt combinations"""

        for k, v in self._prefix_list.items():
            print("\n" + k + "\n")
            print("________________________")
            for statement in v:
                try:
                    if "length_ge" in v and "length_le" not in v:
                        print(statement["seq"], statement["action"], statement["prefix"], statement["length_ge"])
                except KeyError:
                    pass

                try:
                    if "length_le" in v and "length_ge" not in v:
                        print(statement["seq"], statement["action"], statement["prefix"], statement["length_le"])
                except KeyError:
                    pass

                try:
                    if "length_ge" in v and "length_le" in v:
                        print(statement["seq"], statement["action"], statement["prefix"], statement["length_ge"],
                              statement["length_le"])
                except KeyError:
                    pass
                try:
                    if "length_ge" not in v and "length_le" not in v:
                        print(statement["seq"], statement["action"], statement["prefix"])
                except KeyError:
                    pass

    @property
    def prefix_list(self) -> DefaultDict[Any, list]:
        return self._prefix_list


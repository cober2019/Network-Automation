from ncclient import manager
from socket import gaierror
import collections
import datetime
import xmltodict
import time


class Netconf:


    """A collection of methods that allows a Network Engineer to collect interface data"""

    def __init__(self):

        self.session = None
        self.interfaces = {}
        self.interface_stats = {}
        self.interface_qos = collections.defaultdict(list)
        self.interface_trunks = collections.defaultdict(list)
        self.port_channels = {}
        self.access_ports = {}
        self.interface_uptime = {}
        self.bandwidth_dict = {}
        self.status_dict = {}

    def device_connect(self, host=None, username=None, password=None):

        """Device login using NCC Client. One login is complete the program will _collect_data(self)"""

        try:

            self.session = manager.connect(host=host, port=830, timeout=3, username=username, password=password,
                                           device_params={'name': 'csr'})

        except manager.NCClientError:
            raise ConnectionError("Connection to {} failed".format(host))
        except AttributeError:
            raise ConnectionError("Connection to {} failed".format(host))
        except gaierror:
            raise ConnectionError("Connection to {} failed".format(host))
        else:
            self._collect_data()
            return self.session

    def _collect_data(self):

        """BIG Method begins by querying the device for interface configuration. It parses each dict for a particular
        interface type. It then determines if the data return is in list or dictionary format, accesses them a such, gets
        IP information, and lastly uses the get_interface_state method to return all state information. In all, 2 different
        YANG models are used

        Here's how to access data from this method. The new line char seperates each interface output

        for k, v in view.items():
            print("\n")
            print(k)
            for k, v in v.items():
                print(k,v)"""

        int_details = {}
        filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <interface/>
                        </native>
                        </filter>"""

        intf_info = self.session.get(filter)
        intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]

        # Find out data structure (dictionary or list)

        try:
            intf_gigabitethernet = intf_dict["native"]["interface"]["GigabitEthernet"]
        except KeyError:
            intf_gigabitethernet = []

        if isinstance(intf_gigabitethernet, dict):
            if "name" in intf_gigabitethernet:
                self.get_interface_info(interface="GigabitEthernet" + intf_gigabitethernet["name"],
                                        dict=intf_gigabitethernet)
                self._compile_port_channels(dict=intf_gigabitethernet, interface="GigabitEthernet")
                self._compile_trunks(intf_gigabitethernet, interface="GigabitEthernet")
                self._compile_access_ports(interface="GigabitEthernet" + intf_gigabitethernet["name"],
                                           dict=intf_gigabitethernet)

        else:
            try:
                for interface in intf_gigabitethernet:
                    self.get_interface_info(interface="GigabitEthernet" + interface["name"], dict=interface)
                    self._compile_port_channels(dict=interface, interface="GigabitEthernet")
                    self._compile_trunks(interface, interface="GigabitEthernet")
                    self._compile_access_ports(interface="GigabitEthernet" + interface["name"], dict=interface)
            except UnboundLocalError:
                pass

        try:
            intf_loopback = intf_dict["native"]["interface"]["Loopback"]
        except KeyError:
            intf_loopback = []

        if isinstance(intf_loopback, dict):
            if "name" in intf_loopback:
                self.get_interface_info(interface="Loopback" + intf_loopback["name"], dict=intf_loopback)
        else:
            try:
                for interface in intf_loopback:
                    get_interface_state = self.get_interface_info(interface="Loopback" + interface["name"],
                                                                  dict=interface)
            except UnboundLocalError:
                pass

        try:
            intf_tunnel = intf_dict["native"]["interface"]["Tunnel"]
        except KeyError:
            intf_tunnel = []

        if isinstance(intf_tunnel, dict):
            if "name" in intf_tunnel:
                self.get_interface_info(interface="Tunnel" + intf_tunnel["name"], dict=intf_tunnel)
        else:
            try:
                for interface in intf_tunnel:
                    self.get_interface_info(interface="Tunnel" + interface["name"], dict=interface)
            except UnboundLocalError:
                pass

        try:
            intf_vlan = intf_dict["native"]["interface"]["Vlan"]
        except KeyError:
            intf_vlan = []

        if isinstance(intf_vlan, dict):
            if "name" in intf_vlan:
                self.get_interface_info(interface="Vlan" + intf_vlan["name"], dict=intf_vlan)
        else:
            try:
                for interface in intf_vlan:
                    self.get_interface_info(interface="Vlan" + interface["name"], dict=interface)
            except UnboundLocalError:
                pass

        try:
            intf_portchannel = intf_dict["native"]["interface"]["Port-channel"]
        except KeyError:
            intf_portchannel = []

        if isinstance(intf_portchannel, dict):
            if "name" in intf_portchannel:
                self.get_interface_info(interface="Port-channel" + intf_portchannel["name"], dict=intf_portchannel)
        else:
            try:
                for interface in intf_portchannel:
                    self.get_interface_info(interface="Port-channel" + interface["name"], dict=interface)
            except UnboundLocalError:
                pass

        try:
            intf_tengigabit = intf_dict["native"]["interface"]["TenGigabitEthernet"]
        except KeyError:
            intf_tengigabit = []

        if isinstance(intf_tengigabit, dict):
            if "name" in intf_tengigabit:
                self.get_interface_info(interface="TenGigabitEthernet" + intf_tengigabit["name"], dict=intf_tengigabit)
                self._compile_port_channels(dict=intf_tengigabit, interface="TenGigabitEthernet")
                self._compile_trunks(dict=intf_tengigabit, interface="TenGigabitEthernet")
                self._compile_access_ports(interface="TenGigabitEthernet" + intf_tengigabit["name"])

        else:
            try:
                for interface in intf_tengigabit:
                    self.get_interface_info(interface="TenGigabitEthernet" + interface["name"], dict=interface)
                    self._compile_port_channels(dict=interface, interface="TenGigabitEthernet")
                    self._compile_trunks(dict=interface, interface="TenGigabitEthernet")
                    self._compile_access_ports(interface="TenGigabitEthernet" + interface["name"])
            except UnboundLocalError:
                pass

        try:
            intf_portch_sub = intf_dict["native"]["interface"]["Port-channel-subinterface"]
        except KeyError:
            intf_portch_sub = []

        if isinstance(intf_portch_sub, dict):
            if "Port-channel" in intf_portch_sub:
                self.get_interface_info(interface="Port-channel" + intf_portch_sub["Port-channel"]["name"],
                                        dict=intf_portch_sub)
        else:

            try:
                for interface in intf_portch_sub:
                    self.get_interface_info(interface="Port-channel" + interface["Port-channel"]["name"],
                                            dict=interface)
            except UnboundLocalError:
                pass

    def get_interface_info(self, **kwargs):

        """Called from get_interfaces method and returns interface state information. (up/down, speed, change, mac, etc).
        Returns information to the caller"""

        int_details = {}
        nested_dictionary = {}
        int_stats = """<filter>
                   <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                   <interface>
                   <name>%s</name>
                   </interface>
                   </interfaces-state>
                   </filter>""" % kwargs["interface"]

        get_state = self.session.get(int_stats)
        int_status = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]

        try:
            int_info = int_status["interfaces-state"]["interface"]
        except (TypeError, KeyError):
            raise ValueError("Please Check Argument or Session | interface={}".format(kwargs["interface"]))

        try:
            admin_status = int_info["admin-status"]
            oper_status = int_info["oper-status"]
            last_change = int_info["last-change"]
            phy_address = int_info["phys-address"]
            speed = int_info["speed"]
            int_details["admin-status"] = admin_status
            int_details["oper-status"] = oper_status
            int_details["speed"] = speed
            int_details["last-change"] = last_change
            int_details["phys-address"] = phy_address
        except (TypeError, KeyError):
            pass

        try:
            ip = kwargs["dict"]["ip"]["address"]["primary"]["address"]
            mask = kwargs["dict"]["ip"]["address"]["primary"]["mask"]
            int_details["ip"] = ip + " " + mask
        except (TypeError, KeyError):
            pass

        try:
            int_details["standby_prio"] = kwargs["dict"]["standby"]["standby-list"]["priority"]
            int_details["standby_group"] = kwargs["dict"]["standby"]["standby-list"]["group-number"]
            int_details["standby_addr"] = kwargs["dict"]["standby"]["standby-list"]["ip"]["address"]
        except (TypeError, KeyError):
            pass

        try:
            int_details["encap"] = kwargs["interface"]["Port-channel"]["encapsulation"]["dot1Q"]["vlan-id"]
        except (KeyError, TypeError):
            pass

        self.interfaces[kwargs["interface"]] = int_details

        # Get interface statistics and store seperate dictionary

        self.interface_stats[kwargs["interface"]] = nested_dictionary

        try:
            nested_dictionary["In-octets"] = int_info["statistics"]["in-octets"]
            nested_dictionary["In-unicast"] = int_info["statistics"]["in-unicast-pkts"]
            nested_dictionary["In-multicast"] = int_info["statistics"]["in-multicast-pkts"]
            nested_dictionary["In-discards"] = int_info["statistics"]["in-discards"]
            nested_dictionary["In-errors"] = int_info["statistics"]["in-errors"]
            nested_dictionary["In-unknown-protocol"] = int_info["statistics"]["in-unknown-protos"]
            nested_dictionary["Out-octets"] = int_info["statistics"]["out-octets"]
            nested_dictionary["Out-unicast"] = int_info["statistics"]["out-unicast-pkts"]
            nested_dictionary["Out-multicast"] = int_info["statistics"]["out-multicast-pkts"]
            nested_dictionary["Out-discards"] = int_info["statistics"]["out-discards"]
            nested_dictionary["Out-errors"] = int_info["statistics"]["out-errors"]
            nested_dictionary["Out-broad-errors"] = int_info["statistics"]["out-broadcast-pkts"]
            nested_dictionary["Out-multi-errors"] = int_info["statistics"]["out-multicast-pkts"]
            stat_set_in = int_info["statistics"]["in-octets"]
            stat_set_out = int_info["statistics"]["out-octets"]
        except (TypeError, KeyError):
            pass

        self.interface_stats[kwargs["interface"]] = nested_dictionary

        return self.interfaces, speed, stat_set_in, stat_set_out

    def view_interface_qos(self, interface=None):

        """Gather QoS statistics for a given interface. You can access the key, v in the dictionary created with the
        following code:

        for k, v in call_class.interface_qos.items():
            for v in v:
                for k,v in v.items():
                    print(k, v)"""

        nested_dictionary = {}
        int_stats = """<filter>
                    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                    <name>%s</name>
                    </interface>
                    </interfaces-state>
                    </filter>""" % interface

        intf_state_reply = self.session.get(int_stats)
        intf_status = xmltodict.parse(intf_state_reply.xml)["rpc-reply"]["data"]

        try:
            intf_info_tree = intf_status["interfaces-state"]["interface"]
        except (TypeError, KeyError):
            raise ValueError("Please Check Argument or Session | interface={}".format(interface))

        # Access the rpc reponse from device. First check for the policy name then write to the new dictionary. This
        # ensures we don't write a interface name before checking if a policy exist.
        # Two different try/excepts. One to check for policy map, the other to check if the policy map has class-maps/queues

        try:
            self.interface_qos[intf_info_tree["diffserv-target-entry"]["policy-name"]].append(nested_dictionary)
            nested_dictionary["policy_direction"] = intf_info_tree["diffserv-target-entry"]["direction"]
            index = 0
            for queue in range(0, 50):
                try:
                    nested_dictionary["class_name"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "classifier-entry-name"]
                    nested_dictionary["parent_policy"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "parent-path"]
                    nested_dictionary["class_bytes"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "classifier-entry-statistics"]["classified-bytes"]
                    nested_dictionary["class_pkts"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "classifier-entry-statistics"]["classified-pkts"]
                    nested_dictionary["class_rate"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "classifier-entry-statistics"]["classified-rate"]
                    nested_dictionary["queue_size_pkts"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "queuing-statistics"]["queue-size-pkts"]
                    nested_dictionary["queue_size_bytes"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "queuing-statistics"]["queue-size-bytes"]
                    nested_dictionary["drop_pkts"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "queuing-statistics"]["drop-pkts"]
                    nested_dictionary["drop_bytes"] = \
                    intf_info_tree["diffserv-target-entry"]["diffserv-target-classifier-statistics"][index][
                        "queuing-statistics"]["drop-bytes"]
                    self.interface_qos[intf_info_tree["diffserv-target-entry"]["policy-name"]].append(nested_dictionary)
                    index = index + 1
                    nested_dictionary = {}
                except (TypeError, IndexError):
                    pass
        except (KeyError, TypeError):
            pass
        else:
            return self.interface_qos

    def _compile_port_channels(self, dict=None, interface=None):

        try:
            int_details = {}
            int_details["Group_number"] = dict["channel-group"]["number"]
            self.port_channels[interface + dict["name"]] = int_details
            int_details["Channel-mode"] = dict["channel-group"]["mode"]
            self.port_channels[interface + dict["name"]] = int_details
        except KeyError:
            pass

    def _compile_access_ports(self, dict=None, interface=None):

        """Compile access ports"""

        try:
            access_ports = dict["switchport"]["access"]["vlan"]["vlan"]
            self.access_ports[interface] = access_ports
        except (KeyError, TypeError):
            pass

    def _compile_trunks(self, dict=None, interface=None):

        """Compile different trunk configurations, vlans, add, all, or None (all)"""

        try:
            trunks = dict["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]
            self.interface_trunks[interface + dict["name"]].append(trunks)
        except KeyError:
            pass

        try:
            trunks = dict["switchport"]["trunk"]["allowed"]["vlan"]["add"]
            self.interface_trunks[interface + dict["name"]].append(trunks)
        except KeyError:
            pass

        try:
            if dict["switchport"]["trunk"]["allowed"]["vlan"]["vlans"] == "all":
                self.interface_trunks[interface + dict["name"]].append("all")
        except KeyError:
            pass

        try:
            if dict["switchport"]["mode"]["trunk"] is None:
                self.interface_trunks[interface + dict["name"]].append("all")
        except KeyError:
            pass

    def get_trunks(self):

        """Returns trunking interfaces in dictionary format"""

        return self.interface_trunks

    def get_interfaces(self):

        """Returns interface information in dictionary format"""

        return self.interfaces

    def get_interface_stats(self):

        """Returns interface stats in dictionary format"""

        return self.interface_stats

    def view_int_up_down(self):

        """Get interface up/down"""

        status_dict = {}
        for interface, value in self.interfaces.items():
            for key, status in value.items():
                if key == "oper-status":
                    self.status_dict[interface] = status

        return self.status_dict

    def get_interface_qos(self, interface=None):

        """Returns interface queue stats in dictionary format"""

        self.view_interface_qos(interface=interface)

        return self.interface_qos

    def view_single_interface(self, interface=None):

        """Get single interface statistics"""

        try:
            access_dict = self.interfaces[interface]
        except KeyError:
            access_dict = {interface: "Doesn't Exist"}

        return access_dict

    def view_portchannel(self):

        """Get single interface statistics

        Dictionary Access:

        for k,v in self.port_channels.items():
            print(k)
            for k,v in v.items():
                print(k, v)"""

        return self.port_channels

    def view_access_ports(self):

        """Get single interface statistics

        Dictionary Access:

        for k,v in self.port_channels.items():
            print(k)
            for k,v in v.items():
                print(k, v)"""

        return self.access_ports

    def get_interface_uptime(self):

        """Get interface uptime. Calculated my last change k value and current date/time"""

        for interface, stat_set in self.interfaces.items():
            self.interface_uptime[interface] = None
            for k, v in stat_set.items():
                if k == "last-change":
                    last_change = datetime.datetime.now() - datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f+00:00')
                    self.interface_uptime[interface] = last_change
                else:
                    pass

        return self.interface_uptime

    def interfaces_usage(self):

        """Get interface bandwidth usage. Polling time is 10 seconds, Return dictionary to caller"""

        self.bandwidth_dict = {}
        for k, v in self.interfaces.items():
            self._compile_int_usage(interface=k)

        return self.bandwidth_dict

    def interface_usage(self, interface=None):

        """Get interface bandwidth usage. Polling time is 10 seconds, Return dictionary to caller"""

        self.bandwidth_dict = {}
        self._compile_int_usage(interface=interface)

        return self.bandwidth_dict

    def _compile_int_usage(self, interface=None):

        """Internal method to collect and calculate interface bandwdith usage, 10 second polling"""

        nested_dictionary = {}
        stat_set_one = self.get_interface_info(interface=interface)
        time.sleep(10)
        stat_set_two = self.get_interface_info(interface=interface)

        try:
            bytes_in_diff = int(stat_set_two[2]) - int(stat_set_one[2])
            bits_in = int(bytes_in_diff * 8 // 10)
            calc_1 = round(bytes_in_diff * 8 * 100, 4)
            calc_2 = round(10 * int(stat_set_one[1]), 2)
            mbps_in_perc = round(calc_1 / calc_2, 2)
        except (ValueError, IndexError):
            pass

        try:
            bytes_out_diff = int(stat_set_two[3]) - int(stat_set_one[3])
            bits_out = int(bytes_out_diff * 8 // 10)
            calc_1 = round(bytes_out_diff * 8 * 100, 4)
            calc_2 = round(10 * int(stat_set_one[1]), 2)
            mbps_out_perc = round(calc_1 / calc_2, 2)
        except (ValueError, IndexError):
            pass

        self.bandwidth_dict[interface] = nested_dictionary
        nested_dictionary["Percent In"] = mbps_in_perc
        nested_dictionary["Percent Out"] = mbps_out_perc
        self.bandwidth_dict[interface] = nested_dictionary



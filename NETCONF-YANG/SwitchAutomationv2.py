import sys
import os
try:
    from ncclient import manager
except ImportError:
    print("Module NCC Client not available.")
try:
    import ncclient
except ImportError:
    print("Module NCC Client not available.")
try:
    from ncclient.operations import RPCError
except ImportError:
    print("Module NCC Client not available.")
try:
    import lxml.etree as ET
except ImportError:
    print("Module lxml.etree as ET not available.")
try:
    import xml.etree.cElementTree as xml
except ImportError:
    print("Module xml.etree.ElementTree not available.")
try:
    import xmltodict
except ImportError:
    print("Module xmltodict not available.")
try:
    import numpy
except ImportError:
    print("Module numpy not available.")
try:
    from socket import gaierror
except ImportError:
    print("Module socket not available.")
try:
    import ipaddress
except ImportError:
    print("Module readline not available.")
try:
    import time
except ImportError:
    print("Module time not available.")
try:
    import readline
except ImportError:
    print("Module readline not available.")
try:
    from multiprocessing import Process
    import multiprocessing
except ImportError:
    print("Module multiprocessing not available.")

int32 = numpy.dtype(numpy.int32)
status_dict = dict()
core_dict = dict()
access_dict = dict()
hsrp_subnets = dict()
vlan_dict = dict()
device_dict = dict()

int_config = "C:\Python\XML_Filters\Send_Config\Interface_Config.xml"
int_descrp_1 = ["core_to_core", "access_sw_1", "access_sw_2", "access_sw_3", "access_sw_4"]
channel_mode = ["active", "auto", "desirable", "on", "passive"]
int_descrp_2 = ["access_to_core_1", "access_to_core_2"]
span_mode_types = ["rapid-pvst"]

save_payload = """
               <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
               """
config = """  <filter>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
</native>
</filter>
"""
global_bpdu = """  
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<spanning-tree>
<portfast xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree">
<bdpu>bpduguard</bdpu>
<default/>
</portfast>
</spanning-tree>
</native>
</config>"""

interface_config = """  
    <filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface/>
      </native>
    </filter>
"""

###########################################################################

def empty_core_banner():
    print("\n")
    print("|########################################|")
    print("|    Core Topology Empty, Add Devices    |")
    print("|########################################|")
    print("\n")

def empty_access_banner():
    print("\n")
    print("|###########################################|")
    print("|    Access Topology Empty, Add Devices     |")
    print("|###########################################|")
    print("\n")

def int_descrptions(text, state):
    int_descrp_commands = [cmd for cmd in int_descrp_1 if cmd.startswith(text)]

    if state < len(int_descrp_commands):
        return int_descrp_commands[state]
    else:
        return None

def int_descrptions_access(text, state):
    int_descrp_commands = [cmd for cmd in int_descrp_2 if cmd.startswith(text)]

    if state < len(int_descrp_commands):
        return int_descrp_commands[state]
    else:
        return None

def span_mode_selections(text, state):
    span_mode_types_commands = [cmd for cmd in span_mode_types if cmd.startswith(text)]

    if state < len(span_mode_types_commands):
        return span_mode_types_commands[state]
    else:
        return None

def channel_mode_selections(text, state):

    channel_mode_commands = [cmd for cmd in channel_mode if cmd.startswith(text)]

    if state < len(channel_mode_commands):
        return channel_mode_commands[state]
    else:
        return None

###########################################################################
def check_empty_topology():

    if not core_dict:
        empty_core_banner()
        if not access_dict:
            empty_access_banner()
        else:
            return topology()
    else:
        return topology()

def multiproccesing_1(function, arg1):

    loop_count = 0
    while loop_count != 3:
        try:
            global proccess
            proccess = Process(target=function, args=(arg1, ))
            proccess.start()
            break
        except (KeyError, NameError):
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue
        except multiprocessing.ProcessError:
            loop_count = loop_count + 1
            pass
            continue

def send_variable_config(var, key, k):

    loop_count = 0
    while loop_count != 3:
        try:
            m.edit_config(var, target="running")
            response = m.dispatch(ET.fromstring(save_payload))
            status_dict[key] = "Configuration Successful"
            break
        except ET.XMLSyntaxError:
            status_dict["Syntax Error "] = "Empty File, or XML  Syntax Error"
            loop_count = loop_count + 1
            pass
            continue
        except ncclient.operations.RPCError:
            status_dict["RPC "] = "Verify Configuration Application"
            loop_count = loop_count + 1
            pass
            continue
        except ncclient.operations.errors.TimeoutExpiredError:
            status_dict["Connectivity "] = "Connectivity Issue"
            loop_count = loop_count + 1
            pass
            continue
        except (KeyError, NameError):
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue

###########################################################################

def send_config_file(file, key, k):

    loop_count = 0
    while loop_count != 3:
        try:
            config_file = open(file).read()
            m.edit_config(config_file, target="running")
            status_dict[key] = "Configuration Successful"
            response = m.dispatch(ET.fromstring(save_payload))
            break
        except ET.XMLSyntaxError:
            status_dict["Syntax Error "] = "Empty File, or XML  Syntax Error"
            loop_count = loop_count + 1
            pass
            continue
        except FileNotFoundError:
            loop_count = loop_count + 1
            pass
            continue
        except ncclient.operations.RPCError:
            status_dict[key] = "RPC Error, Verify Configuration Application"
            loop_count = loop_count + 1
            pass
            continue
        except SyntaxError:
            status_dict[key] = "Invalid XMLTree. Configuration Failed"
            loop_count = loop_count + 1
            pass
            continue
        except ncclient.operations.errors.TimeoutExpiredError:
            status_dict["Connectivity "] = "Connectivity Issue"
            loop_count = loop_count + 1
            pass
            continue
        except (KeyError, NameError):
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue

###########################################################################

def device_connect(k):

    loop_count = 0
    while loop_count != 3:
        try:

            global m
            m = manager.connect(host=k, port=830, username="cisco", password="cisco",
                                             device_params={'name': 'csr'})
            break

        except AttributeError:
            status_dict[k] = "Connection Failed"
            loop_count = loop_count + 1
            pass
            continue
        except ncclient.NCClientError:
            status_dict[k] = "Connection Failed"
            loop_count = loop_count + 1
            pass
            continue
        except gaierror:
            status_dict[k] = "Connection Failed"
            loop_count = loop_count + 1
            pass
            continue

###########################################################################

def cleanup_empty_elements(root_var, file):

    tree = xml.ElementTree(element=root_var)
    tree.write(file_or_filename=file)

    root = ET.fromstring(open(file=file).read())
    for element in root.xpath("//*[not(node())]"):
        element.getparent().remove(element)

    tree = xml.ElementTree(element=root)
    tree.write(file_or_filename=file)

###########################################################################

def search_vlan():

    for device in core_dict.keys():

        int_dict = dict()
        print("\n")
        print(device + " #####################################")
        print("\n")

        device_connect(device)
        config_data = m.get(config)

        try:
            config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
        except KeyError:
            pass
        try:
            vlan_details = config_details["native"]["spanning-tree"]["vlan"]
        except KeyError:
            pass
        try:
            hsrp_details = config_details["native"]["interface"]["Vlan"]
        except KeyError:
            pass
        try:
            int_details = config_details["native"]["interface"]["GigabitEthernet"]
        except KeyError:
            pass

        print("{:10} {:10}  {:11} {:6}  {:10} {:6} ".format("Inter", "IP", "Mask", "Prio", "Group", "VIP"))
        print("\n")
        for items in hsrp_details:
            if "standby" in items:
                int_dict["Vlan"] = items
                try:
                    for k, v in int_dict.items():
                        int_row = "{:6} {:10}  {:15} {:7}  {:6} {:6} ".format(v["name"],
                                                                        v["ip"]["address"]["primary"]["address"],
                                                                        v["ip"]["address"]["primary"]["mask"],
                                                                        v["standby"]["standby-list"]["priority"],
                                                                        v["standby"]["standby-list"]["group-number"],
                                                                    v["standby"]["standby-list"]["ip"][ "address"])


                    print(int_row)
                except TypeError:
                    pass

        print("\n")
        print("{:9} {:11} {:11} ".format("PoCh", "Inter", "Mode"))
        print("\n")
        for items in int_details:
            if "channel-group" in items:
                int_dict["GigabitEthernet"] = items
                for k, v in int_dict.items():
                    if k == "GigabitEthernet":

                        try:
                            int_row = "{:9} {:10} {:15}".format(v["channel-group"]["number"],
                                                                            v["name"],
                                                                            v["channel-group"]["mode"])
                        except TypeError:
                            pass
                        except UnboundLocalError:
                            pass

                print(int_row)

        try:
            print("\n")
            print("{:7} {:6}".format("Vlan", "Priority"))
            print("\n")
            for items in vlan_details:
                vlan_row = "{:8} {:7}".format(items["id"],
                                                                    items["priority"])
                print(vlan_row)

        except TypeError:
            pass
        except UnboundLocalError:
            pass

    for device in access_dict.keys():

            int_dict = dict()
            vlan_dict = dict()

            print("\n")
            print(device + " #####################################")
            print("\n")

            device_connect(device)
            config_data = m.get(config)

            try:
                config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
            except KeyError:
                pass
            try:
                vlan_details = config_details["native"]["spanning-tree"]["vlan"]
                vlan_dict["Vlan"] = vlan_details
            except KeyError:
                pass
            try:
                hsrp_details = config_details["native"]["interface"]["Vlan"]
            except KeyError:
                pass
            try:
                int_details = config_details["native"]["interface"]["GigabitEthernet"]
            except KeyError:
                pass

            print("\n")
            print("{:9} {:11} {:11} ".format("PoCh", "Inter", "Mode"))
            print("\n")
            for items in int_details:
                if "channel-group" in items:
                    int_dict["GigabitEthernet"] = items
                    for k, v in int_dict.items():
                        try:
                            if k == "GigabitEthernet":
                                    int_row = "{:9} {:10} {:15}".format(v["channel-group"]["number"],
                                                                                v["name"],
                                                                                v["channel-group"]["mode"])
                                    print(int_row)

                        except TypeError:
                            pass
                        except UnboundLocalError:
                            pass


            try:
                print("\n")
                print("{:7} {:6}".format("Vlan", "Priority"))
                print("\n")
                for k, v in vlan_dict.items():
                    vlan_row = "{:8} {:7}".format(v["id"],
                                                                        v["priority"])
                    print(vlan_row)

            except TypeError:
                pass
            except UnboundLocalError:
                pass



###########################################################################

def core_interfaces(k):

    int_dict = dict()

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    int_element = xml.SubElement(native_element, "interface")

    loop_count = 0
    while loop_count != 3:
        try:
            config_data = m.get(interface_config)
            config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
            global int_details
            int_details = config_details["native"]["interface"]["GigabitEthernet"]
            break
        except ncclient.operations.errors.TimeoutExpiredError:
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue
        except (KeyError, NameError):
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue

    for items in int_details:
        if "channel-group" not in items:
            int_dict["GigabitEthernet"] = items
            for interface, v in int_dict.items():
                if "name" in v and v["name"] != "0/0":
                    int_type = xml.SubElement(int_element, "GigabitEthernet")
                    int_phy = xml.SubElement(int_type, "name")
                    int_phy.text = v["name"]
                    span_element = xml.SubElement(int_type, "spanning-tree")
                    span_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree" )
                    port_fast_element = xml.SubElement(span_element, "portfast")
                    shutdown = xml.SubElement(int_type, "shutdown")

                    try:
                        tree = xml.ElementTree(root)
                        with open("C:\Python\XML_Filters\Send_Config\Interface_Core_%s.xml" % k, "wb") as fh:
                            tree.write(fh)
                    except FileNotFoundError:
                        print("\n")
                        print("File Not Found")
                        pass

    proccess = Process(target=send_config_file, args=("C:\Python\XML_Filters\Send_Config\Interface_Core_%s.xml" % k, "Port", k, ))
    proccess.start()
    proccess = Process(target=send_variable_config, args=(global_bpdu,  "BPDU", k, ))
    proccess.start()

###########################################################################

def access_interfaces(k):

    int_dict = dict()

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    int_element = xml.SubElement(native_element, "interface")

    loop_count = 0
    while loop_count != 3:
        try:
            config_data = m.get(interface_config)
            config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
            global int_details
            int_details = config_details["native"]["interface"]["GigabitEthernet"]
            break
        except ncclient.operations.errors.TimeoutExpiredError:
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue
        except (KeyError, NameError):
            status_dict["Connectivity "] = "Connectivity Issue"
            device_connect(k)
            loop_count = loop_count + 1
            pass
            continue

    for items in int_details:
        if "channel-group" not in items:
            int_dict["GigabitEthernet"] = items
            for interface, v in int_dict.items():
                if "name" in v and v["name"] != "0/0":

                    int_type = xml.SubElement(int_element, "GigabitEthernet")
                    int_phy = xml.SubElement(int_type, "name")
                    int_phy.text = v["name"]
                    span_element = xml.SubElement(int_type, "spanning-tree")
                    span_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
                    port_fast_element = xml.SubElement(span_element, "portfast")
                    shutdown = xml.SubElement(int_type, "shutdown")

                    try:
                        tree = xml.ElementTree(root)
                        with open("C:\Python\XML_Filters\Send_Config\Interface_Access_%s.xml" % k, "wb") as fh:
                            tree.write(fh)
                    except FileNotFoundError:
                        print("\n")
                        print("File Not Found")
                        pass


    proccess = Process(target=send_config_file, args=("C:\Python\XML_Filters\Send_Config\Interface_Access_%s.xml" % k, "Port", k, ))
    proccess.start()
    proccess = Process(target=send_variable_config, args=(global_bpdu, "BPDU", k, ))
    proccess.start()

###########################################################################

def topology_deploy():

    hsrp_file = "C:\Python\XML_Filters\Send_Config\HSRP_Send_Config.xml"
    hsrp2_file = "C:\Python\XML_Filters\Send_Config\HSRP2_Send_Config.xml"
    vlan_file = "C:\Python\XML_Filters\Send_Config\VLAN_Send_Config.xml"
    vlan2_file = "C:\Python\XML_Filters\Send_Config\VLAN_2_Send_Config.xml"
    vlan_acc_file = "C:\Python\XML_Filters\Send_Config\VLAN_Access_Send_Config.xml"
    trunk_file = "C:\Python\XML_Filters\Send_Config\Trunk_Send_Config.xml"

    ################################################################################ Send Configuration to Core Switches

    global  status_dict
    loop_count = 0

    while loop_count != 1:
        if not core_dict:
            empty_core_banner()
            break
        else:
            loop_count = loop_count + 1
            for k, file in core_dict.items():
                status_dict = dict()

                if "Core_1" in file:

                    device_connect(k)

                    print("\n")
                    print("%s: Sending configuration... " % k )

                    send_config_file(hsrp_file, "HSRP", k)
                    time.sleep(1)
                    send_config_file(vlan_file, "VLAN", k)
                    time.sleep(1)
                    send_config_file(file, "Interface", k)

                    print("\n")
                    print("{:15} {:30} ".format("Config", "Status"))
                    print("\n")
                    for k, v in status_dict.items():
                        print("{:<15} {:<30}".format(k, v))

                elif"Core_2" in file:
                    status_dict = dict()

                    device_connect(k)

                    print("\n")
                    print("%s: Sending configuration... " % k )

                    send_config_file(hsrp2_file, "HSRP", k)
                    time.sleep(1)
                    send_config_file(vlan2_file, "VLAN", k)
                    time.sleep(1)
                    send_config_file(file, "Interface", k)

                    print("\n")
                    print("{:15} {:30} ".format("Config", "Status"))
                    print("\n")

                    for k, v in status_dict.items():
                        print("{:<15} {:<30}".format(k, v))

    ################################################################################ Send Configuration to Access Switches
    loop_count = 0
    while loop_count != 1:
        if not access_dict:
            empty_access_banner()
            break
        else:
            loop_count = loop_count + 1
            for k, v in access_dict.items():

                status_dict = dict()
                device_connect(k)

                print("\n")
                print("%s: Sending configuration... " % k)

                send_config_file(vlan_acc_file, "VLAN", k)
                send_config_file(v, "Interface", k)

                print("\n")
                print("{:15} {:30} ".format("Config", "Status"))
                print("\n")
                for k, v in status_dict.items():
                    print("{:<15} {:<30}".format(k, v))

    status_dict = dict()
    if not core_dict and not access_dict:
        main()
    else:
        print("\n")
        print("Program will sleep until local device sync... ")
        print("\n")
        time.sleep(20)
        print("Almost there...")
        print("\n")
        time.sleep(20)
        print("\n")
        print("Scanning devices fore non-trunking and unsuded ports..")
        print("\n")
        print("Applying Configurations via background procceses. Routing you to the main menu")
        time.sleep(5)

        for k in core_dict.keys():
            if "Core_1" in file:
                multiproccesing_1(core_interfaces, k)
            elif "Core_2" in file:
                multiproccesing_1(core_interfaces, k)

        for k in access_dict.keys():
            multiproccesing_1(access_interfaces, k)


###########################################################################

def L2_Core_edgePorts():

    while True:
        if not core_dict:
            empty_core_banner()
            break
        else:
            print("\n")
            print("|###############################################|")
            print("|   Applying Core  Edge Port Configurations...  |")
            print("|###############################################|")
            print("|     Configuration will run in background      |")
            print("|###############################################|")
            print("\n")
            for k, file in core_dict.items():
                multiproccesing_1(core_interfaces, k)
            break

def L2_Access_edgePorts():

    while True:
        if not access_dict:
            empty_access_banner()
            break
        else:
            print("\n")
            print("|###############################################|")
            print("|   Applying Access Edge Port Configurations... |")
            print("|###############################################|")
            print("|     Configuration will run in background      |")
            print("|###############################################|")
            print("\n")
            for k, v in access_dict.items():
                multiproccesing_1(access_interfaces, k)
            break

###########################################################################

def save_configuration():

    print("\n")
    print("Saving configuration")
    print("\n")

    for k in core_dict.keys():
        loop_count = 0
        while loop_count !=3:
            try:
                response = m.dispatch(ET.fromstring(save_payload))
                print("{:<15} {:<30}".format(k, "Configuration Saved"))
                break
            except ncclient.NCClientError:
                print("{:<15} {:<30}".format(k, "Configuration Save Failed"))
                loop_count = loop_count + 1
                pass
                continue
            except (TypeError, NameError):
                device_connect(k)
                loop_count = loop_count + 1
                print("\n")
                pass
                continue

    for k in access_dict.keys():
        loop_count = 0
        while loop_count !=3:
            try:

                response = m.dispatch(ET.fromstring(save_payload))
                print("{:<15} {:<30}".format(k, "Configuration Saved"))
                break
            except ncclient.NCClientError:
                print("{:<15} {:<30}".format(k, "Configuration Save Failed"))
                loop_count = loop_count + 1
                pass
                continue
            except (TypeError, NameError):
                device_connect(k)
                loop_count = loop_count + 1
                print("\n")
                pass
                continue

    print("\n")
    main()
###########################################################################

def topology():

    if not core_dict:
        empty_core_banner()
    else:
        print("\n")
        print("Core Switches:")
        print("##############")
        print("\n")
        for k in core_dict.keys():
            cores = k
            print("{:<0}".format(cores))

    if not access_dict:
        empty_access_banner()
    else:
        print("\n")
        print("Access Switches:")
        print("##############")
        print("\n")
        for k in access_dict.keys():
            access = k
            print( "{:<0}".format(access))
        print("\n")

###########################################################################

def build_topology():

    loop_count = 0
    print("\n")
    print("Topology Build")
    print("\n")
    print("Enter CTRL+ C to move on to the main menu, or enter channel mode to continue")
    print("\n")

    try:

        readline.parse_and_bind("tab: complete")
        readline.set_completer(channel_mode_selections)

        while True:

            chan_mode_input = input("Please enter etherchannel mode: ")
            print("\n")

            if chan_mode_input not in channel_mode:
                print("\n")
                print("Invalid channel mode")
                print("\n")
                continue
            else:
                break

        while True:
            try:

                loop_count = loop_count + 1
                root = xml.Element("config")
                root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
                root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
                native_element = xml.Element("native")
                native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
                root.append(native_element)
                int_element = xml.SubElement(native_element, "interface")

                print("\n")
                print("Topology Build")
                print("\n")
                print("Enter Core Switches, Enter CTRL+ C to move on to Access Switches")
                print("\n")

                device_input = input("Core Switch: ")
                print("#######################")
                print("\n")
                ipaddress.IPv4Address(device_input)
                core_dict[device_input] = "C:\Python\XML_Filters\Send_Config\Core_%s" % loop_count +"_%s.xml" % device_input

                while True:
                    try:
                        po_int_input = input("Port-Channel Number:  ")

                        int_type_po = xml.SubElement(int_element, "Port-channel")

                        po_int_element = xml.SubElement(int_type_po, "name")
                        po_int_element.text = po_int_input

                        while True:

                            readline.parse_and_bind("tab: complete")
                            readline.set_completer(int_descrptions)

                            print("*Press TAB for interfaces description options.  ")
                            print("\n")
                            int_descr = input("Interface description: ").lower()

                            if int_descr == "":
                                print("\n")
                                print("Please enter a descrption")
                                print("\n")
                                continue
                            else:
                                int_descrp = xml.SubElement(int_type_po, "description")
                                int_descrp.text = int_descr
                                break

                        if "core"  in int_descr:
                            while True:
                                try:
                                    device_int_input = input("Interface Name: ")

                                    int_type = xml.SubElement(int_element, "GigabitEthernet")

                                    int_phy = xml.SubElement(int_type, "name")
                                    int_phy.text = device_int_input

                                    switchport = xml.SubElement(int_type, "switchport")
                                    port_mode = xml.SubElement(switchport, "mode")
                                    port_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-switch")
                                    mode_trunk = xml.SubElement(port_mode, "trunk")

                                    port_mode = xml.SubElement(int_type, "channel-group")
                                    port_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet")

                                    pch_num = xml.SubElement(port_mode, "number")
                                    pch_num.text = po_int_input

                                    chan_mode = xml.SubElement(port_mode, "mode")
                                    chan_mode.text = chan_mode_input

                                    try:
                                        tree = xml.ElementTree(root)
                                        with open("C:\Python\XML_Filters\Send_Config\Core_%s" % loop_count + "_%s.xml" % device_input,"wb") as fh:
                                            tree.write(fh)

                                    except FileNotFoundError:
                                        print("\n")
                                        print("File Not Found")
                                        pass
                                except KeyboardInterrupt:
                                    print("\n")
                                    pass
                                    break
                        else:

                            span_element = xml.SubElement(int_type_po, "spanning-tree")
                            span_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
                            root_guard = xml.SubElement(span_element, "guard")
                            root_guard.text = "root"

                            while True:
                                try:
                                    device_int_input = input("Interface Name: ")

                                    int_type = xml.SubElement(int_element, "GigabitEthernet")

                                    int_phy = xml.SubElement(int_type, "name")
                                    int_phy.text = device_int_input

                                    switchport = xml.SubElement(int_type, "switchport")
                                    port_mode = xml.SubElement(switchport, "mode")
                                    port_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-switch")
                                    mode_trunk = xml.SubElement(port_mode, "trunk")

                                    port_mode = xml.SubElement(int_type, "channel-group")
                                    port_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet")

                                    pch_num = xml.SubElement(port_mode, "number")
                                    pch_num.text = po_int_input

                                    chan_mode = xml.SubElement(port_mode, "mode")
                                    chan_mode.text = chan_mode_input

                                    try:

                                        tree = xml.ElementTree(root)
                                        with open("C:\Python\XML_Filters\Send_Config\Core_%s" % loop_count +"_%s.xml" % device_input, "wb") as fh:
                                            tree.write(fh)

                                    except FileNotFoundError:
                                        print("\n")
                                        print("File Not Found")
                                        pass
                                except KeyboardInterrupt:
                                    print("\n")
                                    pass
                                    break
                    except KeyboardInterrupt:
                        print("\n")
                        pass
                        break
            except ipaddress.AddressValueError:
                print("Invalid IP Address")
                print("\n")
            except KeyboardInterrupt:
                print("\n")
                break
    except KeyboardInterrupt:
        print("\n")
        check_empty_topology()
        main()
        pass

##################################################### Access switch configuration

    while True:
        try:

            root = xml.Element("config")
            root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
            root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
            native_element = xml.Element("native")
            native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
            root.append(native_element)
            int_element = xml.SubElement(native_element, "interface")

            print("Press CTRL+C to exit to the main menu")
            print("\n")

            device_input = input("Access Switch: ")
            print("#########################")
            print("\n")
            ipaddress.IPv4Address(device_input)
            access_dict[device_input] = "C:\Python\XML_Filters\Send_Config\Access_%s.xml" % device_input

            while True:
                try:
                    po_int_input = input("Port-Channel Number:  ")

                    int_type_po = xml.SubElement(int_element, "Port-channel")

                    po_int_element = xml.SubElement(int_type_po, "name")
                    po_int_element.text = po_int_input

                    while True:

                        readline.parse_and_bind("tab: complete")
                        readline.set_completer(int_descrptions_access)

                        print("*Press TAB for interfaces description options.  ")
                        print("\n")
                        int_descr = input("Interface description: " ).lower()

                        int_descrp = xml.SubElement(int_type_po, "description")
                        int_descrp.text = int_descr

                        if int_descr =="":
                            print("\n")
                            print("Please enter a descrption")
                            print("\n")
                        else:
                            break

                    while True:
                        try:
                            device_int_input = input("Interface Name: ")

                            int_type = xml.SubElement(int_element, "GigabitEthernet")

                            int_phy = xml.SubElement(int_type, "name")
                            int_phy.text = device_int_input

                            switchport = xml.SubElement(int_type, "switchport")
                            port_mode = xml.SubElement(switchport, "mode")
                            port_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-switch")
                            mode_trunk = xml.SubElement(port_mode, "trunk")

                            port_mode = xml.SubElement(int_type, "channel-group")
                            port_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet")

                            pch_num = xml.SubElement(port_mode, "number")
                            pch_num.text = po_int_input

                            chan_mode = xml.SubElement(port_mode, "mode")
                            chan_mode.text = chan_mode_input

                            try:
                                tree = xml.ElementTree(root)
                                with open("C:\Python\XML_Filters\Send_Config\Access_%s.xml" % device_input,"wb") as fh:
                                    tree.write(fh)
                            except FileNotFoundError:
                                print("\n")
                                print("File Not Found")
                                pass
                        except KeyboardInterrupt:
                            print("\n")
                            pass
                            break
                except KeyboardInterrupt:
                    print("\n")
                    break
                    pass
        except ipaddress.AddressValueError:
            print("Invalid IP Address")
            print("\n")
        except KeyboardInterrupt:
            print("\n")
            print("\n")
            break

###########################################################################

def main():

    config_selection = ' '
    while config_selection != 'q':

        print("\n")
        print("Basic Network Programabiltiy and Automation Program")
        print("\n")
        print(" 1: L2/L3 Setup")
        print(" 2: Send Topology")
        print(" 3: Send L2 Edge")
        print(" 4. Build Topology")
        print(" 5. View Configuration")
        print(" 6. Save Configuration")
        print("[q] (quit)")
        print("\n")

        config_selection = input("Please select an option:  ")

        if config_selection == "1":
            vlans()
        elif config_selection == "2":
            topology_deploy()
        elif config_selection == "3":
            L2_Core_edgePorts()
            L2_Access_edgePorts()
        elif config_selection == "4":
            build_topology()
        elif config_selection == "5":
            search_vlan()
        elif config_selection == "6":
            save_configuration()

##############################################################################

def vlans():

    global vlan_dict
    vlan_dict= dict()
    vlan_array = [ ]
    int32 = numpy.dtype(numpy.int32)
    vlan_prio_array = [4096, 8192, 12288, 16384, 20480, 24576, 28672, 32768, 36864, 40960, 45056, 49152, 53248, 57344, 61440]
    vlan_array_int32 = numpy.array(vlan_prio_array, dtype=int32)
    vlan_range = range(1, 4097)

    Core_1_file = "C:\Python\XML_Filters\Send_Config\VLAN_Send_Config.xml"
    Core_2_file = "C:\Python\XML_Filters\Send_Config\VLAN_2_Send_Config.xml"
    acc_switch_file = "C:\Python\XML_Filters\Send_Config\VLAN_Access_Send_Config.xml"

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    tree = xml.ElementTree(root)

    vlan_element = xml.SubElement(native_element, "vlan")

    print("\n")
    print("VLAN Configuration Mode")
    print("\n")

    readline.parse_and_bind("tab: complete")
    readline.set_completer(span_mode_selections)

    print("\n")
    span_tree_element = xml.SubElement(native_element, "spanning-tree")

    span_mode_input = input("Enter spanning tree mode: ")

    span_mode = xml.SubElement(span_tree_element, "mode")
    span_mode.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
    span_mode.text = span_mode_input

    while True:
        try:

            print("\n")
            print("Press CTRL+C to escape and send configuration")
            print("\n")

            while True:

                vl_id_input = int(input("VLAN: "))

                vlan_list = xml.SubElement(vlan_element, "vlan-list")
                vlan_list.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-vlan")

                if vl_id_input in vlan_range:

                    vl_id = xml.SubElement(vlan_list, "id")
                    vl_id.text = str(vl_id_input)

                    with open(Core_1_file, "wb") as fh:
                        tree.write(fh)
                    break

                else:
                    print("\n")
                    print("Invalid Vlan ID (1 - 4096)")
                    print("\n")
                    continue

            vl_name_input = input("VLAN name: ")
            vl_name = xml.SubElement(vlan_list, "name")
            vl_name.text = vl_name_input

            span_vlan_element = xml.SubElement(span_tree_element, "vlan")
            span_vlan_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")

            span_vl_id = xml.SubElement(span_vlan_element, "id")
            span_vl_id.text =str(vl_id_input)

            while True:

                vl_bd_prio_input = int(input("Bridge priority: "))
                int_vlan_prio = int(vl_bd_prio_input)

                if vl_bd_prio_input in vlan_array_int32:

                    vl_bd_prio = xml.SubElement(span_vlan_element, "priority")
                    vl_bd_prio.text = str(vl_bd_prio_input)

                    vlan_dict[vl_id_input] = vl_bd_prio_input
                    vlan_array.append(vl_bd_prio_input)

                    cleanup_empty_elements(root, Core_1_file)
                    break

                else:
                    print("\n")
                    print("Invalid Bridge ID (0-61440,) increments of 4096.")
                    print("\n")
                    continue

        except KeyboardInterrupt:

            uplink_fast = xml.SubElement(span_tree_element, "uplinkfast")
            uplink_fast.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
            loop_guard = xml.SubElement(span_tree_element, "loopguard")
            loop_guard.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
            default_element = xml.SubElement(loop_guard, "default")

            try:
                tree = xml.ElementTree(root)
                with open(Core_1_file, "wb") as fh:
                    tree.write(fh)
            except FileNotFoundError:
                print("\n")
                print("File Not Found")
                pass

            vlan_array = numpy.array(vlan_array, dtype=int32)
            min_val = int(numpy.min(vlan_array))
            max_val = int(numpy.max(vlan_array))

            for priority in root.iter('priority'):
                vlan_pro = int(priority.text)
                if vlan_pro == min_val:
                    diff = max_val - vlan_pro
                    vlan_pro = int(priority.text) + diff
                    priority.text = str(vlan_pro)
                elif vlan_pro == max_val:
                    diff = max_val - min_val
                    vlan_pro = int(priority.text) - diff
                    priority.text = str(vlan_pro)

            try:
                tree = xml.ElementTree(root)
                with open(Core_2_file, "wb") as fh:
                    tree.write(fh)
            except FileNotFoundError:
                print("\n")
                print("File Not Found")
                pass

            for priority in root.iter('priority'):
                priority.text = "61440"

            try:
                tree = xml.ElementTree(root)
                with open(acc_switch_file, "wb") as fh:
                    tree.write(fh)
            except FileNotFoundError:
                print("\n")
                print("File Not Found")
                pass

            print("\n")
            print("###########################################|")
            print("#Routing you to HSRP Configuration...######|")
            print("###########################################|")
            print("\n")
            time.sleep(5)
            print("\n")

            redundancy()

###########################################################################

def redundancy():

    hsrp_file = "C:\Python\XML_Filters\Send_Config\HSRP_Send_Config.xml"
    hsrp2_file = "C:\Python\XML_Filters\Send_Config\HSRP2_Send_Config.xml"
    Core_1_file = "C:\Python\XML_Filters\Send_Config\VLAN_Send_Config.xml"

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    int_element = xml.SubElement(native_element, "interface")

    vlan_element = xml.SubElement(native_element, "vlan")
    vlan_list = xml.SubElement(vlan_element, "vlan-list")
    vlan_list.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-vlan")
    print("\n")

    hsrp_subnets = dict()
    vl_ids = [ ]
    vl_priority = [ ]

    for k, v in vlan_dict.items():
        vl_ids.append(k)
        vl_priority.append(v)
        print("VLAN: {0:5} Priority: {1:<5}".format(k, v))

    while True:
        try:

            print("\n")
            print("Press CTRL+C to escape and send configuration")
            print("\n")

            int_type_leaf = xml.SubElement(int_element, "Vlan")

            while True:
                interface_number = int(input("Please enter a Vlan (SVI:)  "))

                if interface_number in vl_ids:
                    int_name = xml.SubElement(int_type_leaf, "name")
                    int_name.text = str(interface_number)

                    int_choice_1 = input("Please enter a description: ")
                    int_descrp = xml.SubElement(int_type_leaf, "description")
                    int_descrp.text = int_choice_1
                    break
                else:
                    print("\n")
                    print("VLAN not created")
                    print("\n")
                    continue

            while True:
                try:
                    ip_input, mask_input = input("Please Enter A IP address and mask:  ").split()
                    ipaddress.IPv4Address(ip_input)
                    ipaddress.IPv4Network(mask_input)
                    break

                except ValueError:
                    print("\n")
                    print("Invalid IP address or mask")
                    print("\n")
                    pass
                    continue
                except ipaddress.AddressValueError:
                    print("\n")
                    print("Invalid IP address or mask")
                    print("\n")
                    pass
                    continue

            ip_leaf = xml.SubElement(int_type_leaf, "ip")
            address_leaf = xml.SubElement(ip_leaf, "address")
            primary_leaf = xml.SubElement(address_leaf, "primary")

            address = xml.SubElement(primary_leaf, "address")
            address.text = ip_input

            mask = xml.SubElement(primary_leaf, "mask")
            mask.text = mask_input

            standby = xml.SubElement(int_type_leaf, "standby")

            standby_ver = xml.SubElement(standby, "version")
            standby_ver.text = "2"

            mac_refresh_input= input("Please enter MAC refresh timer:  ")
            mac_refresh = xml.SubElement(standby, "mac-refresh")
            mac_refresh.text = mac_refresh_input

            standby_list = xml.SubElement(standby, "standby-list")

            standby_group_input= input("Please enter standby group:  ")
            standby_group = xml.SubElement(standby_list, "group-number")
            standby_group.text = standby_group_input

            authentication = xml.SubElement(standby_list, "authentication")

            auth_input= input("Please enter authentication string: ")
            auth = xml.SubElement(authentication, "text")
            auth.text = auth_input

            ip = xml.SubElement(standby_list, "ip")

            while True:
                try:
                    standby_ip_input= input("Please enter a standby IP: ")
                    ipaddress.IPv4Interface(standby_ip_input)
                    break
                except ValueError:
                    print("\n")
                    print("Invalid IP address ")
                    print("\n")
                    pass
                    continue
                except ipaddress.AddressValueError:
                    print("\n")
                    print("Invalid IP address")
                    print("\n")
                    pass
                    continue

            standby_address = xml.SubElement(ip, "address")
            standby_address.text = standby_ip_input

            prio = xml.SubElement(standby_list, "priority")

            preempt = xml.SubElement(standby_list, "preempt")
            preempt_delay = xml.SubElement(preempt, "delay")

            pre_min_input= input("Please enter preempt delay: ")
            pre_min = xml.SubElement(preempt_delay, "minimum")
            pre_min.text = pre_min_input

            try:
                vlan_array = numpy.array(vl_priority, dtype=int32)
                min_val = int(numpy.min(vl_priority))
                max_val = int(numpy.max(vl_priority))

                for k, v in vlan_dict.items():
                    if k == interface_number:
                        value_1 = v
                        if value_1 in vlan_array and value_1 == min_val:
                                prio.text = "110"
                        elif value_1 in vlan_array and value_1 == max_val:
                                prio.text = "210"

                hsrp_subnets[prio.text] = ip_input
                cleanup_empty_elements(root, hsrp_file)

            except ValueError:
                print("\n")
                print("Please create VLANs First")
                pass
                vlans()
                print("\n")

        except KeyboardInterrupt:

            for priority in root.iter('priority'):
                new_pri = int(priority.text)
                if new_pri == 110:
                    new_pri = int(priority.text) + 100
                    priority.text = str(new_pri)
                elif new_pri > 110:
                    new_pri = int(priority.text) - 100
                    priority.text = str(new_pri)

            for k, v in hsrp_subnets.items():
                for address in root.iter('address'):
                    if address.text == v and k == "110":
                        new_address = ipaddress.ip_address(address.text) + 1
                        address.text = str(new_address)
                    elif address.text == v and k == "210":
                        new_address = ipaddress.ip_address(address.text) + 1
                        address.text = str(new_address)

            cleanup_empty_elements(root, hsrp2_file)

            print("\n")
            print("###########################################|")
            print("#Routing you to the main menu...###########|")
            print("###########################################|")
            print("\n")
            time.sleep(5)
            print("\n")

            main()

if __name__ == '__main__':

    build_topology()
    topology()
    main()


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

int_config = "C:\Python\XML_Filters\Send_Config\Interface_Config.xml"
hsrp_file = "C:\Python\XML_Filters\Send_Config\HSRP_Send_Config.xml"
hsrp2_file = "C:\Python\XML_Filters\Send_Config\HSRP2_Send_Config.xml"
Core_1_file = "C:\Python\XML_Filters\Send_Config\VLAN_Send_Config.xml"
hsrp_file = "C:\Python\XML_Filters\Send_Config\HSRP_Send_Config.xml"
hsrp2_file = "C:\Python\XML_Filters\Send_Config\HSRP2_Send_Config.xml"
vlan_file = "C:\Python\XML_Filters\Send_Config\VLAN_Send_Config.xml"
vlan2_file = "C:\Python\XML_Filters\Send_Config\VLAN_2_Send_Config.xml"
vlan_acc_file = "C:\Python\XML_Filters\Send_Config\VLAN_Access_Send_Config.xml"
trunk_file = "C:\Python\XML_Filters\Send_Config\Trunk_Send_Config.xml"
Core_1_file = "C:\Python\XML_Filters\Send_Config\VLAN_Send_Config.xml"
Core_2_file = "C:\Python\XML_Filters\Send_Config\VLAN_2_Send_Config.xml"
acc_switch_file = "C:\Python\XML_Filters\Send_Config\VLAN_Access_Send_Config.xml"

root = xml.Element("config")
root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
native_element = xml.Element("native")
native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
root.append(native_element)
int_element = xml.SubElement(native_element, "interface")

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


int32 = numpy.dtype(numpy.int32)
status_dict = dict()
core_dict = dict()
access_dict = dict()
hsrp_subnets = dict()
vlan_dict = dict()
device_dict = dict()

def int_descrptions(text, state):
    int_descrp = ["core_to_core", "access_sw_1", "access_sw_2", "access_sw_3", "access_sw_4"]
    int_descrp_commands = [cmd for cmd in int_descrp if cmd.startswith(text)]

    if state < len(int_descrp_commands):
        return int_descrp_commands[state]
    else:
        return None

def int_descrptions_access(text, state):
    int_descrp = ["access_to_core_1", "access_to_core_2"]
    int_descrp_commands = [cmd for cmd in int_descrp if cmd.startswith(text)]

    if state < len(int_descrp_commands):
        return int_descrp_commands[state]
    else:
        return None

def span_mode_selections(text, state):
    span_mode_types = ["rapid-pvst"]
    span_mode_types_commands = [cmd for cmd in span_mode_types if cmd.startswith(text)]

    if state < len(span_mode_types_commands):
        return span_mode_types_commands[state]
    else:
        return None

def channel_mode_selections(text, state):
    channel_mode = ["active", "auto", "desirable", "on", "passive"]
    channel_mode_commands = [cmd for cmd in channel_mode if cmd.startswith(text)]

    if state < len(channel_mode_commands):
        return channel_mode_commands[state]
    else:
        return None

def cleanup_empty_elements(root_var, file):

    tree = xml.ElementTree(element=root_var)
    tree.write(file_or_filename=file)

    root = ET.fromstring(open(file=file).read())
    for element in root.xpath("//*[not(node())]"):
        element.getparent().remove(element)

    tree = xml.ElementTree(element=root)
    tree.write(file_or_filename=file)

def search_vlan():

    for device in core_dict.keys():

        int_dict = dict()
        print("\n")
        print(device + " #####################################")
        print("\n")
        try:
            m = manager.connect(host=device, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})

            config_data = m.get(config)

            config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
            vlan_details = config_details["native"]["spanning-tree"]["vlan"]
            hsrp_details = config_details["native"]["interface"]["Vlan"]
            int_details = config_details["native"]["interface"]["GigabitEthernet"]

            print("{:10} {:10}  {:11} {:6}  {:10} {:6} ".format("Inter", "IP", "Mask", "Prio", "Group", "VIP"))
            print("\n")
            for items in hsrp_details:
                if "standby" in items:
                    int_dict["Vlan"] = items
                    for k, v in int_dict.items():
                        int_row = "{:6} {:10}  {:15} {:7}  {:6} {:6} ".format(v["name"],
                                                                        v["ip"]["address"]["primary"]["address"],
                                                                        v["ip"]["address"]["primary"]["mask"],
                                                                        v["standby"]["standby-list"]["priority"],
                                                                        v["standby"]["standby-list"]["group-number"],
                                                                        v["standby"]["standby-list"]["ip"][ "address"])

                    print(int_row)

            print("\n")
            print("{:9} {:11} {:11} ".format("PoCh",  "Inter", "Mode"))
            print("\n")
            for items in int_details:
                if "channel-group" in items:
                    int_dict["GigabitEthernet"] = items
                    for k, v in int_dict.items():
                        if k == "GigabitEthernet":
                            int_row = "{:9} {:10} {:15}".format(v["channel-group"]["number"],
                                                                            v["name"],
                                                                            v["channel-group"]["mode"])

                    print(int_row)

            print("\n")
            print("{:7} {:6}".format("Vlan", "Priority"))
            print("\n")
            for items in vlan_details:
                vlan_row = "{:8} {:7}".format(items["id"],
                                                                    items["priority"])
                print(vlan_row)

        except (KeyError, TypeError):
            print("\n")
            pass
        except UnicodeError:
            print("\n")
            print("Invalid IP address. Please try again")
            pass
        except ncclient.NCClientError:
            print("\n")
            print("Connection unsuccessful to " + device)
            pass

    for device in access_dict.keys():

        int_dict = dict()
        vlan_dict = dict()
        print("\n")
        print(device + " #####################################")
        print("\n")
        try:
            m = manager.connect(host=device, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})

            config_data = m.get(config)

            config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
            vlan_details = config_details["native"]["spanning-tree"]["vlan"]
            int_details = config_details["native"]["interface"]["GigabitEthernet"]
            vlan_dict["Vlan"] = vlan_details


            print("\n")
            print("{:9} {:11} {:11} ".format("PoCh",  "Inter", "Mode"))
            print("\n")
            for items in int_details:
                if "channel-group" in items:
                    int_dict["GigabitEthernet"] = items
                    for k, v in int_dict.items():
                        if k == "GigabitEthernet":
                            int_row = "{:9} {:10} {:15}".format(v["channel-group"]["number"],
                                                                            v["name"],
                                                                            v["channel-group"]["mode"])

                    print(int_row)

            print("\n")
            print("{:7} {:6}".format("Vlan", "Priority"))
            print("\n")
            for k, v in vlan_dict.items():
                vlan_row = "{:8} {:7}".format(v["id"],
                                                                    v["priority"])
                print(vlan_row)

        except (KeyError, TypeError):
            print("\n")
            pass
        except UnicodeError:
            print("\n")
            print("Invalid IP address. Please try again")
            pass
        except ncclient.NCClientError:
            print("\n")
            print("Connection unsuccessful to " + device)
            pass

def core_interfaces():


    int_dict = dict()
    config_data = m.get(config)

    config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
    int_details = config_details["native"]["interface"]["GigabitEthernet"]

    for items in int_details:
        if "channel-group" not in items:
            int_dict["GigabitEthernet"] = items
            for k, v in int_dict.items():
                if "name" in v and v["name"] != "0/0":

                    int_type = xml.SubElement(int_element, "GigabitEthernet")
                    int_phy = xml.SubElement(int_type, "name")
                    int_phy.text = v["name"]
                    span_element = xml.SubElement(int_type, "spanning-tree")
                    span_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree" )
                    port_fast_element = xml.SubElement(span_element, "portfast")
                    shutdown = xml.SubElement(int_type, "shutdown")

                    tree = xml.ElementTree(root)
                    with open("C:\Python\XML_Filters\Send_Config\Interface_Config.xml" ,"wb") as fh:
                        tree.write(fh)
            try:
                config_file = open(int_config).read()
                m.edit_config(config_file, target="running")
                m.edit_config(global_bpdu, target="running")
            except ncclient.operations.RPCError:
                pass
            except (KeyError, TypeError):
                pass

def access_interfaces():

    int_dict = dict()
    config_data = m.get(config)

    config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
    int_details = config_details["native"]["interface"]["GigabitEthernet"]

    for items in int_details:
        if "channel-group" not in items:
            int_dict["GigabitEthernet"] = items
            for k, v in int_dict.items():
                if "name" in v and v["name"] != "0/0":
                    interface = v["name"]

                    int_type = xml.SubElement(int_element, "GigabitEthernet")
                    int_phy = xml.SubElement(int_type, "name")
                    int_phy.text = v["name"]
                    span_element = xml.SubElement(int_type, "spanning-tree")
                    span_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
                    port_fast_element = xml.SubElement(span_element, "portfast")
                    shutdown = xml.SubElement(int_type, "shutdown")

                    tree = xml.ElementTree(root)
                    with open("C:\Python\XML_Filters\Send_Config\Interface_Config.xml", "wb") as fh:
                        tree.write(fh)

            try:
                config_file = open(int_config).read()
                m.edit_config(config_file, target="running")
                m.edit_config(global_bpdu, target="running")
            except ncclient.operations.RPCError:
                pass
            except (KeyError, TypeError):
                pass

def topology_deploy():

    ################################################################################ Send Configuration to Core Switches

    global  status_dict
    int_dict = dict()
    status_dict = dict()

    for k, file in core_dict.items():
        if "Core_1" in file:
            try:
                global m
                m = manager.connect(host=k, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})
                print("\n")
                print("%s: Sending configuration... " % k )

                print("\n")
                print("{:15} {:30} ".format("Config", "Status"))
                print("\n")

                try:

                    config_file = open(hsrp_file).read()
                    m.edit_config(config_file, target="running")
                    status_dict["HSRP "] = "Configuration Successful"
                except FileNotFoundError:
                    print("\n")
                    status_dict["File "] = "File not found"
                except ncclient.NCClientError:
                    status_dict["HSRP "] = "Configuration Failed"
                    pass
                except SyntaxError:
                    status_dict["HSRP "] = "Invalid XMLTree. Configuration Failed"
                    pass

                try:
                    config_file = open(vlan_file).read()
                    m.edit_config(config_file, target="running")
                    status_dict["VLAN"] = "Configuration Successful"
                except FileNotFoundError:
                    print("\n")
                    status_dict["File "] = "File not found"
                except ncclient.NCClientError:
                    status_dict["VLAN"] = "Configuration Failed"
                    pass
                except SyntaxError:
                    status_dict["VLAN"] = "Invalid XMLTree. Configuration Failed"
                    pass

                try:
                    config_file = open(v).read()
                    m.edit_config(config_file, target="running")
                    status_dict["Interface"] = "Configuration Successful"
                except FileNotFoundError:
                    print("\n")
                    status_dict["File "] = "File not found"
                except ncclient.NCClientError:
                    status_dict["Interface"] = "Configuration Failed"
                    pass
                except SyntaxError:
                    status_dict["Interface"] = "Invalid XMLTree. Configuration Failed"
                    pass
            except AttributeError:
                status_dict[k] = "Connection Unsucessful"
                pass
                break

            for k, v in status_dict.items():
                print("{:<15} {:<30}".format(k, v))


        elif"Core_2" in file:
            status_dict = dict()
            try:

                m = manager.connect(host=k, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})

                print("\n")
                print("%s: Sending configuration... " % k )
                print("\n")

                print("\n")
                print("{:15} {:30} ".format("Config", "Status"))
                print("\n")

                try:

                    config_file = open(hsrp2_file).read()
                    m.edit_config(config_file, target="running")
                    status_dict["HSRP"] = "Configuration Successful"
                except FileNotFoundError:
                    print("\n")
                    status_dict["File "] = "File not found"
                except ncclient.NCClientError:
                    status_dict["HSRP"] = "Configuration Failed"
                    pass
                except SyntaxError:
                    status_dict["HSRP"] = "Invalid XMLTree. Configuration Failed"
                    pass

                try:
                    config_file = open(vlan2_file).read()
                    m.edit_config(config_file, target="running")
                    status_dict["VLAN"] = "Configuration Successful"
                except FileNotFoundError:
                    print("\n")
                    status_dict["File "] = "File not found"
                except ncclient.NCClientError:
                    status_dict["VLAN"] = "Configuration Failed"
                    pass
                except SyntaxError:
                    status_dict["VLAN"] = "Invalid XMLTree. Configuration Failed"
                    pass

                try:
                    config_file = open(v).read()
                    m.edit_config(config_file, target="running")
                    status_dict["Interface"] = "Configuration Successful"
                except FileNotFoundError:
                    print("\n")
                    status_dict["File "] = "File not found"
                except ncclient.NCClientError:
                    status_dict["Interface"] = "Configuration Failed"
                    pass
                except SyntaxError:
                    status_dict["xml"] = "Invalid XMLTree. Configuration Failed"
                    pass
            except AttributeError:
                status_dict[k] = "Connection Unsucessful"
                pass
                break

            for k, v in status_dict.items():
                print("{:<15} {:<30}".format(k, v))


    ################################################################################ Send Configuration to Access Switches

    for k, v in access_dict.items():
        status_dict = dict ()
        try:

            m = manager.connect(host=k, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})

        except AttributeError:
            status_dict[k] = "Connection Failed"
            pass

        print("\n")
        print("%s: Sending configuration... " % k)
        print("\n")

        print("\n")
        print("{:15} {:30} ".format("Config", "Status"))
        print("\n")

        try:
            config_file = open(vlan_acc_file).read()
            m.edit_config(config_file, target="running")
            status_dict["VLAN"] = "Configuration Successful"
        except FileNotFoundError:
            print("\n")
            status_dict["File "] = "File not found"
        except ncclient.NCClientError:
            status_dict["VLAN"] = "Configuration Failed"
            pass
        except SyntaxError:
            status_dict["VLAN"] = "Invalid XMLTree. Configuration Failed"
            pass

        try:
            config_file = open(v).read()
            m.edit_config(config_file, target="running")
            status_dict["Interface"] = "Configuration Successful"
        except FileNotFoundError:
            print("\n")
            status_dict["File "] = "File not found"
        except ncclient.NCClientError:
            status_dict["Interface"] = "Configuration Failed"
            pass
        except SyntaxError:
            status_dict["Interface"] = "Invalid XMLTree. Configuration Failed"
            pass

        for k, v in status_dict.items():
            print("{:<15} {:<30}".format(k, v))

    save_configuration()
    print("\n")
    print("#####################################################################|")
    print("#Applying portfast, BPDU-guard, and shutting down unused ports ...###|")
    print("#####################################################################|")
    core_interfaces()
    access_interfaces()
    save_configuration()
    main()
    print("\n")

def save_configuration():

    print("\n")
    print("Saving configuration takes 40 seconds due to local database sync. Please stand by...")
    time.sleep(50)
    print("\n")

    for k in core_dict.keys():
        while True:
            try:
                save_payload = """
                               <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
                               """
                response = m.dispatch(ET.fromstring(save_payload))
                print("{:<15} {:<30}".format(k, "Configuration Saved"))
                break

            except ncclient.NCClientError:
                print("{:<15} {:<30}".format(k, "Configuration Save Failed"))
                pass
                break
            except NameError:
                m = manager.connect(host=k, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})
                print("\n")
            except KeyboardInterrupt:
                pass
                main()
                break

    for k in access_dict.keys():
        while True:
            try:
                save_payload = """
                               <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
                               """
                response = m.dispatch(ET.fromstring(save_payload))
                print("{:<15} {:<30}".format(k, "Configuration Saved"))
                break

            except ncclient.NCClientError:
                print("{:<15} {:<30}".format(k, "Configuration Save Failed"))
                pass
                break
            except NameError:
                m = manager.connect(host=k, port=830, username="cisco", password="cisco", device_params={'name': 'csr'})
                continue
                print("\n")
            except KeyboardInterrupt:
                pass
                main()
                break

def topology():

    int = 0
    print("Core Switches:")
    print("##############")
    print("\n")
    for k in core_dict.keys():
        cores = k
        int = int + 1
        print("{:<0}".format(cores))

    print("\n")
    print("Access Switches:")
    print("################")
    print("\n")
    for k in access_dict.keys():
        access = k
        int = int + 1
        print( "{:<0}".format(access))
    print("\n")

def build_topology():

    int = 0
    global  core_dict
    core_dict = dict()
    global  access_dict
    access_dict = dict()
    core_config_dict =dict()

    print("\n")
    print("Topology Build")
    print("\n")
    print("Enter Core Switches, Enter CTRL+ C to move on to Access Switches:")
    print("\n")

    readline.parse_and_bind("tab: complete")
    readline.set_completer(channel_mode_selections)
    chan_mode_input = input("Please enter etherchannel mode: ")
    print("\n")

    while True:
        try:
            int = int + 1
            device_input = input("Core Switch: ")
            print("#######################")
            print("\n")
            ipaddress.IPv4Address(device_input)
            core_dict[device_input] = "C:\Python\XML_Filters\Send_Config\Core_%s" % int +"_%s.xml" % device_input

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
                                core_config_dict[po_int_input] = device_int_input

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

                                tree = xml.ElementTree(root)
                                with open("C:\Python\XML_Filters\Send_Config\Core_%s" % int + "_%s.xml" % device_input,"wb") as fh:
                                    tree.write(fh)

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

                                tree = xml.ElementTree(root)
                                with open("C:\Python\XML_Filters\Send_Config\Core_%s" % int +"_%s.xml" % device_input, "wb") as fh:
                                    tree.write(fh)

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

##################################################### Access switch configuration

    int = 0
    print("Press CTRL+C to exit to the main menu")
    print("\n")

    while True:
        int = int + 1
        try:
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

                            tree = xml.ElementTree(root)
                            with open("C:\Python\XML_Filters\Send_Config\Access_%s.xml" % device_input,"wb") as fh:
                                tree.write(fh)

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
            print("\n")
            print("\n")
            print("\n")
            break

def main():

    print(core_dict)
    print()
    topology()

    config_selection = ' '
    while config_selection != 'q':

        print("\n")
        print("Basic Network Programabiltiy and Automation Program")
        print("\n")

        print("\n")
        print(" 1: L2/L3 Setup")
        print(" 2: L2 Edge Ports")
        print(" 3: Build Topology")
        print(" 4. Send Topology")
        print(" 5. Save Configuration")
        print(" 6. View Config")

        print("[q] (quit)")

        print("\n")

        config_selection = input("Please select an option:  ")

        if config_selection == "1":
            vlans()
        elif config_selection == "2":
            core_interfaces()
            access_interfaces()
            save_configuration()
        elif config_selection == "3":
            build_topology()
        elif config_selection == "4":
            topology_deploy()
        elif config_selection == "5":
            save_configuration()
        elif config_selection == "6":
            search_vlan()

##############################################################################

def vlans():

    global vlan_dict
    vlan_dict= dict()
    vlan_array = [ ]
    int32 = numpy.dtype(numpy.int32)
    vlan_prio_array = [4096, 8192, 12288, 16384, 20480, 24576, 28672, 32768, 36864, 40960, 45056, 49152, 53248, 57344, 61440]
    vlan_array_int32 = numpy.array(vlan_prio_array, dtype=int32)
    vlan_range = range(1, 4097)

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

            tree = xml.ElementTree(root)
            with open(Core_1_file, "wb") as fh:
                tree.write(fh)

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

            tree = xml.ElementTree(root)
            with open(Core_2_file, "wb") as fh:
                tree.write(fh)

            for priority in root.iter('priority'):
                priority.text = "61440"


                tree = xml.ElementTree(root)
                with open(acc_switch_file, "wb") as fh:
                    tree.write(fh)


            print("\n")
            print("###########################################|")
            print("#Routing you to HSRP Configuration...######|")
            print("###########################################|")
            print("\n")
            time.sleep(5)
            print("\n")

            redundancy()

def redundancy():


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
    main()
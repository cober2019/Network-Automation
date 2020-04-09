import sys
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
from os import system, name

status_dict = dict()
core_dict = dict()
access_dict = dict()
hsrp_subnets = dict()
vlan_dict = dict()
device_dict = dict()
vlan_to_port = dict()
core_switch_array = [ ]
access_switch_array = [ ]
phys_trunk_array = [ ]
po_array = [ ]
interfaces = [ ]
int32 = numpy.dtype(numpy.int32)
get_username = " "
get_password = " "

def menu():

    while True:

        print("\n")
        print("|-HSRP Configuration Program---------------------|")
        print("|------------------------------------------------|\n")
        print("Guideline (1) Press enter for if you dont want to configure an option. You will be re-asked of the option is needed")
        print("Guideline (2) Use CTRL-C to exit config mode for the following config (device input, vlan creation, HSRP interface creation)\n")

        print("1. Get Configuration")
        print("2. Send Configuration\n")

        selection = input("Select an option: ")
        print("\n")

        if selection == "1":
            view_single_device()
            view_config()
        elif selection == "2":
            log_devices()
            vlans()
        else:
            print("Invalid Slection\n")

def view_single_device():

    while True:
        try:
            core_switch = input("Device: ")
            ipaddress.IPv4Address(core_switch)    # Check for vaild IP address
            break
        except (ValueError, ipaddress.AddressValueError) as error:
            print("\n")
            print(error)
            print("\n")
            time.sleep(3)
            clear()
            continue

    global get_username
    global get_password
    get_username = input("Username: ")
    get_password = input("Password: ")
    print("\n")
    core_switch_array.append(core_switch)
    clear()

def log_devices():

    print("\n")
    print("Press CTRL+C to return to the main menu\n")
    print("Enter desired active gateway first")

    print("\n")
    print("|-Core Switches-------------------|")
    print("|---------------------------------|")
    print("\n")

    # Collect core switches and store to an array. If the IP address isn't valid and exception will be thrown. You will
    # be prompted untial a valid address has been entered. Use CTRL+C to exit the primary loop.

    while True:
        try:
            while True:
                try:
                    core_switch = input("Core Switch: ")
                    ipaddress.IPv4Address(core_switch)    # Check for vaild IP address
                    core_switch_array.append(core_switch)
                except (ValueError, ipaddress.AddressValueError) as error:
                    print("\n")
                    print(error)
                    print("\n")
                    continue
        except KeyboardInterrupt:                          # Only when you done entering switch, use CTRL+C to break the loop
            print("\n")
            break

    print("\n")
    print("|-Access Switches-----------------|")
    print("|---------------------------------|")
    print("\n")

    # Collect access switches and store to an array. If the IP address isn't valid and exception will be thrown. You will
    # be prompted untial a valid address has been entered. Use CTRL+C to exit the primary loop.

    while True:
        try:
            while True:
                try:
                    access_switch = input("Access Switch: ")
                    ipaddress.IPv4Address(access_switch)      # Check for vaild IP address
                    access_switch_array.append(access_switch)
                except (ValueError, ipaddress.AddressValueError) as error:
                    print("\n")
                    print(error)
                    print("\n")
                    continue
        except KeyboardInterrupt:                              # Only when you done entering switch, use CTRL+C to break the loop
            print("\n")
            break

    time.sleep(1)
    clear()
    credential_check()


def credential_check():

    # This fucntion validates credentials for the devices being changed. If 1 devices fails, you will be returned
    # to the credential menu

    fails = 0  # Fail counter

    try:
        while True:

            print("\n")
            print("Press CTRL+C to return to the main menu\n")

            print("\n")
            print("|-Credentials---------------------|")
            print("|---------------------------------|")
            print("\n")
            print("* Please ensure these credential are used for all device in the topology")
            print("\n")

            global get_username
            global get_password
            get_username = input("Username: ")
            get_password = input("Password: ")
            print("\n")

            if not core_switch_array:
                break
            else:
                for ip in core_switch_array: # Loop through core switches and test provided credentials
                    try:
                        m = manager.connect(host=ip, port=830, timeout=3, username=get_username, password=get_password, device_params={'name': 'csr'})
                    except (AttributeError, ncclient.NCClientError) as error:
                        print("Connection Unsuccessful: " + ip)
                        print("Reason: %s" % error)
                        fails = fails + 1                       # If login fails, increase counter
                        continue

            if not access_switch_array:
                break
            else:
                for ip in access_switch_array: # Loop through access switches and test provided credentials
                    try:
                        m = manager.connect(host=ip, port=830, timeout=3, username=get_username, password=get_password, device_params={'name': 'csr'})
                    except (AttributeError, ncclient.NCClientError) as error:
                        print("Connection Unsuccessful: " + ip)
                        print("Reason: %s" % error)
                        fails = fails + 1                       # If login fails, increase counter

        if fails == 1:
            time.sleep(2)                                       # Check if fail count is == 1
            clear()
            credential_check()                                  # Return to credential input if condition is true
        else:
            print("Authentication Successful...")               # If all device pass,break the loop, go to vlan() funtion
            time.sleep(2)
            clear()

            print("Routing you to VLAN configuration...")
            time.sleep(2)
            clear()
            vlans()

    except KeyboardInterrupt:                                   # CTRL-C to escape to main menu
        core_switch_array.clear()                               # Clear core array
        access_switch_array.clear()                             # Clear switch array
        clear()
        menu()                                                  # Return to main menu

def vlans():
    try:
        global vlan_dict
        vlan_dict= dict()
        vlan_array = [ ]
        int32 = numpy.dtype(numpy.int32)
        vlan_prio_array = [4096, 8192, 12288, 16384, 20480, 24576, 28672, 32768, 36864, 40960, 45056, 49152, 53248, 57344, 61440]
        vlan_array_int32 = numpy.array(vlan_prio_array, dtype=int32)
        vlan_range = range(1, 4097)


        Core_1_file = "C:\Python\VLAN_Send_Config.xml"
        Core_2_file = "C:\Python\VLAN_2_Send_Config.xml"
        acc_switch_file = "C:\Python\VLAN_Access_Send_Config.xml"

        root = xml.Element("config")
        root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
        native_element = xml.Element("native")
        native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
        root.append(native_element)
        tree = xml.ElementTree(root)
        vlan_element = xml.SubElement(native_element, "vlan")
        span_tree_element = xml.SubElement(native_element, "spanning-tree")

        while True:
            try:

                # Thi loop takes input for vlans, bridge prioritie, and vlan name. Whilw taking put it create an XML tree to be saved
                # later. A value erro exception will be thrown if the vlan isn't an integer

                while True:
                    try:

                        print("\n")
                        print("Press CTRL+C to escape and send configuration")
                        print("\n")

                        vl_id_input = int(input("VLAN: "))
                        vlan_list = xml.SubElement(vlan_element, "vlan-list")
                        vlan_list.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-vlan")

                        if vl_id_input in vlan_range:               # Checks to see if the vlan is a valid vlan number. If not you will be warned and ask to input again

                            vl_id = xml.SubElement(vlan_list, "id")
                            vl_id.text = str(vl_id_input)

                            while True:

                                vl_name_input = input("VLAN name: ")

                                if vl_name_input !=  "":

                                    vl_name = xml.SubElement(vlan_list, "name")
                                    vl_name.text = vl_name_input
                                    span_vlan_element = xml.SubElement(span_tree_element, "vlan")
                                    span_vlan_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree")
                                    span_vl_id = xml.SubElement(span_vlan_element, "id")
                                    span_vl_id.text = str(vl_id_input)

                                    #Write the XML tree to file. This file is your configuration

                                    try:
                                        with open(Core_1_file, "wb") as fh:
                                            tree.write(fh)
                                        break
                                    except TypeError:
                                        print("Error while saving. Returning you to vlan setup")
                                        vlans()
                                else:
                                    print("\n")
                                    print("Invalid Vlan Name")
                                    print("\n")
                                    continue
                        else:
                            print("\n")
                            print("Invalid Vlan ID (1 - 4096)")
                            print("\n")
                            continue

                        while True:
                            try:
                                vl_bd_prio_input = int(input("Bridge priority: "))
                                int_vlan_prio = int(vl_bd_prio_input)

                                # Check to see if the priority is a valid value. Using int32 numpy array for larger numbers.
                                # During developement i could not enter a priority larger than 9999.

                                if vl_bd_prio_input in vlan_array_int32:

                                    vl_bd_prio = xml.SubElement(span_vlan_element, "priority")
                                    vl_bd_prio.text = str(vl_bd_prio_input)
                                    vlan_dict[vl_id_input] = vl_bd_prio_input
                                    vlan_array.append(vl_bd_prio_input)

                                    # Save XML tree to file. This file is your configuration

                                    cleanup_empty_elements(root, Core_1_file)
                                    break
                                else:
                                    print("\n")
                                    print("Invalid Bridge ID (0-61440,) increments of 4096.")
                                    print("\n")
                                    continue
                            except ValueError:
                                print("\n")
                                print("Invalid Bridge ID (0-61440,) increments of 4096.")
                                print("\n")
                                continue
                    except ValueError:
                        print("\n")
                        print("Invalid Vlan ID (1 - 4096)")
                        print("\n")
                        continue


            except KeyboardInterrupt:
                print("\n")
                # This is where the magic happens.

                try:
                    tree = xml.ElementTree(root)
                    with open(Core_1_file, "wb") as fh:
                        tree.write(fh)
                except TypeError:
                    print("Error while saving. Returning you to vlan setup")
                    vlans()

                # adds bridge priority array to and allows it to be larger than 9999 mention earlier. Grab the minimum int in

                vlan_array = numpy.array(vlan_array, dtype=int32)
                min_val = int(numpy.min(vlan_array))                  # Grab the smallest int in the array
                max_val = int(numpy.max(vlan_array))                  # Grab the largest number in the array
                for priority in root.iter('priority'):                # Grab "priority" as we iterate through the XML tree from string
                    vlan_pro = int(priority.text)                     # Once found store the value
                    if vlan_pro == min_val:                           # If the priority == min value in the array, 4096
                        diff = min_val + vlan_pro
                        vlan_pro = int(priority.text) + diff
                        priority.text = str(vlan_pro)                 # Your new value is is created, writen to the second core switch.
                    else:
                        diff = vlan_pro + min_val                     # Subtract min value from max, or 61440 - 4096
                        vlan_pro = int(priority.text) - diff          # Subtract configured value minus min-max diff
                        priority.text = str(vlan_pro)                 # Write new value to tree

                try:
                    tree = xml.ElementTree(root)
                    with open(Core_2_file, "wb") as fh:
                        tree.write(fh)                                    # After all that , save the file.
                except TypeError:
                    print("Error while saving. Returning you to vlan setup")
                    vlans()

                for priority in root.iter('priority'):                # Find all "priority" set value to 61440 and save to file
                    priority.text = "61440"                           # This will be used for access switches only.

                    try:
                        tree = xml.ElementTree(root)
                        with open(acc_switch_file, "wb") as fh:
                            tree.write(fh)
                    except TypeError:
                        print("Error while saving. Returning you to vlan setup")
                        vlans()

            print("Routing you tp HSRP configuration...")
            time.sleep(2)
            clear()
            redundancy()
            # Continue to HSRP funtion.
    except KeyboardInterrupt:
        pass
        vlans()

def redundancy():

    try:
        hsrp_subnets = dict()
        vl_ids = [ ]
        vl_priority = [ ]

        hsrp_file = "C:\Python\HSRP_Send_Config.xml"
        hsrp2_file = "C:\Python\HSRP2_Send_Config.xml"
        Core_1_file = "C:\Python\VLAN_Send_Config.xml"

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

        for k, v in vlan_dict.items():                          # Display vlans with priorities create in the VLAN section
            vl_ids.append(k)                                    # Add the key, or vlan id to array for later use
            vl_priority.append(v)
            print("VLAN: {:2} Priority: {:5}".format(k, v))

        while True:
            try:

                print("\n")
                print("Press CTRL+C to escape and send configuration")
                print("\n")

                int_type_leaf = xml.SubElement(int_element, "Vlan")

                while True:
                    interface_number = int(input("Please enter a Vlan (SVI:)  "))

                    if interface_number in vl_ids:                                     # Check to see if SVI is in vl_ids_array, line 298
                        int_name = xml.SubElement(int_type_leaf, "name")               # Continue to buidl XML tree
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
                        ip_input, mask_input = input("Please Enter A IP address and mask:  ").split() # Enter IP address and mask. Uses split(" ")
                        ipaddress.IPv4Address(ip_input)                                               # Validate ip
                        ipaddress.IPv4Address(mask_input)                                             # Validate mask
                        break
                    except (ipaddress.AddressValueError, ValueError):
                        # Through Value error is the latter is invalid
                        print("\n")
                        print("Invalid IP address or mask")
                        print("\n")
                        pass
                        continue

                ip_leaf = xml.SubElement(int_type_leaf, "ip")                                           # Continue to build XML tree, answer inputs to line 409
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

                while True:
                    standby_group_input= input("Please enter standby group:  ")

                    if standby_group_input != "":

                        standby_group = xml.SubElement(standby_list, "group-number")
                        standby_group.text = standby_group_input
                        break
                    else:
                        print("\n")
                        print("Invalid IP address")
                        print("\n")
                        continue

                authentication = xml.SubElement(standby_list, "authentication")
                md5 = xml.SubElement(authentication, "md5")
                md5_key_string = xml.SubElement(md5, "key-string")

                auth_input= input("Please enter authentication string: ")
                auth = xml.SubElement(md5_key_string, "string")
                auth.text = auth_input

                ip = xml.SubElement(standby_list, "ip")

                while True:
                    try:
                        standby_ip_input= input("Please enter a standby IP: ")
                        ipaddress.IPv4Interface(standby_ip_input)
                        break
                    except (ipaddress.AddressValueError, ValueError):
                        print("\n")
                        print("Invalid IP address")
                        print("\n")

                standby_address = xml.SubElement(ip, "address")
                standby_address.text = standby_ip_input
                prio = xml.SubElement(standby_list, "priority")
                preempt = xml.SubElement(standby_list, "preempt")
                preempt_delay = xml.SubElement(preempt, "delay")
                pre_min_input= input("Please enter preempt delay: ")
                pre_min = xml.SubElement(preempt_delay, "minimum")
                pre_min.text = pre_min_input

                try:

                    # This section helps us align or bridge priorities and HSRP priority. Int turn, make it so we dont have to configure the second device

                    vlan_array = numpy.array(vl_priority, dtype=int32)
                    min_val = int(numpy.min(vl_priority))
                    max_val = int(numpy.max(vl_priority))

                    for k, v in vlan_dict.items():                              # Search vlan dict which is vlan and vlan prioriies
                        if k == interface_number:                               # If the vlan == key configured SVI
                            value_1 = v                                         # Set value_1 to the bridge priority
                            if value_1 in vlan_array and value_1 == min_val:    # Check to see if value_1 is in the vlan array and if its == to minvalue 4096
                                    prio.text = "110"                           # If so, set the hSRP priority to 110
                            elif value_1 in vlan_array and value_1 == max_val:  # If not, set the priority to 210
                                    prio.text = "210"

                    hsrp_subnets[prio.text] = ip_input                          # Stores the newly created hsrp priorities to a diction for later use
                    cleanup_empty_elements(root, hsrp_file)                     # Saves to file and cleans up any empty setting during configuration

                except ValueError:
                    print("\n")
                    print("Please create VLANs First")
                    pass
                    vlans()
                    print("\n")

            except KeyboardInterrupt:                                           # Break the primary loop so we can finsh our HSRP config. Or should say, let the program do it
                print("\n")
                # This is where we create our second core file.

                for priority in root.iter('priority'):                          # We iterate from string again
                    new_pri = int(priority.text)                                # Grab prioty that we creatd during configuration
                    if new_pri == 110:                                          # If it equals 110 we will just add 100
                        new_pri = int(priority.text) + 100                      # Make string an int, Add 100
                        priority.text = str(new_pri)                            # assign new priority as wtring
                    elif new_pri > 110:                                         # If the value is greate than 110, we will just subtract 110
                        new_pri = int(priority.text) - 100                      # Make string an int, Subtract 110
                        priority.text = str(new_pri)                            # assign new priority as string

                for k, v in hsrp_subnets.items():
                    for address in root.iter('address'):                          # Iterate through the string again
                        if address.text == v and k == "110":                      # If ip address == v, saved earlier, and k == 110, assign above
                            new_address = ipaddress.ip_address(address.text) + 1  # Add one to the last octet
                            address.text = str(new_address)                       # Assign new address to variable
                        elif address.text == v and k == "210":                    # If ip address == v, saved earlier, and k == 210, assign above
                            new_address = ipaddress.ip_address(address.text) + 1  # Add one to the last octet
                            address.text = str(new_address)                       # Assign the new address to variable

                cleanup_empty_elements(root, hsrp2_file)                          # Cleanup any empty element, second core switch file
                search_vlan()

    except KeyboardInterrupt:
        redundancy()
        pass

def search_vlan():

    print("Checking for existing trunks and associated vlans")
    time.sleep(2)
    clear()

    for ip in core_switch_array:        # Loop through device entered at the begingin of the program
        get_configuration_loop(ip)      # Carry the IP variable to the get_configuration() function
    for ip in access_switch_array:
        get_configuration_loop(ip)

    topology_deploy()

def get_configuration_loop(ip):

    config = """  <filter><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"></native></filter>"""

    # Access and iterate array and creates during log_device funtion. The point of the search_vlan function is to access the devices
    # and get the current configuration. We need to gather all ports that are trunking, both physical and logical. This is needed so
    # we can place the same vlans back on the port. If not place back, NETCONF will only add the new vlans delting these rest.. I've
    # tried a few differnt was but no luck.

    try:
        m = manager.connect(host=ip, port=830, timeout=3, username=get_username, password=get_password, device_params={'name': 'csr'})
    except (AttributeError, ncclient.NCClientError) as error:
        print("Connection Unsuccessful: " + ip)
        print("Reason: %s" % error)
        pass

    config_data = m.get(config)
    config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]

    int_details_2 = config_details["native"]["interface"]["Port-channel"]
    int_details = config_details["native"]["interface"]["GigabitEthernet"]

    for items in int_details_2:
        try:
            if items["switchport"]["trunk"]["allowed"]["vlan"]["add"]:
                vlan_to_port[items["name"]] = items["switchport"]["trunk"]["allowed"]["vlan"]["add"]
        except KeyError:
            pass
        try:
            if items["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]:
                vlan_to_port[items["name"]] = items["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]
        except KeyError:
            pass
        try:
            if items["switchport"]["trunk"]["allowed"]["vlan"]["vlans"] == "all":
                vlan_to_port[items["name"]] = "all"
        except KeyError:
            pass

    for items in int_details:

        try:
            if items["switchport"]["trunk"]["allowed"]["vlan"]["add"]:
                vlan_to_port[items["name"]] = items["switchport"]["trunk"]["allowed"]["vlan"]["add"]
        except KeyError:
            pass
        try:
            if items["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]:
                vlan_to_port[items["name"]] = items["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]
        except KeyError:
            pass
        try:
            if items["switchport"]["trunk"]["allowed"]["vlan"]["vlans"] == "all":
                vlan_to_port[items["name"]] = "all"
        except KeyError:
            pass


    build_topology(ip)

def build_topology(ip):

    # In this fuction we will build orl XML tree and save it to file. We can later open the file and send it to the device
    # via NETCONF

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    int_element = xml.SubElement(native_element, "interface")

    # Start iterating over the k and values create in the search_vlan function. All ports and vlans assigned were mapped
    # to this global dictionary. Here we can assign the keys and value to the proper XML element

    for k, v in vlan_to_port.items():
        for new_vlan in vlan_dict.keys():

            if "/" in k:
                int_type = xml.SubElement(int_element, "GigabitEthernet")
            else:
                int_type = xml.SubElement(int_element, "Port-channel")

            po_int_element = xml.SubElement(int_type, "name")
            po_int_element.text = k                                  # The key from each iteration will be assign to the interface element
            switchport = xml.SubElement(int_type, "switchport")
            mode_trunk = xml.SubElement(switchport, "trunk")
            mode_trunk.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-switch")
            allowed = xml.SubElement(mode_trunk, "allowed")
            vlan = xml.SubElement(allowed, "vlan")
            vlans = xml.SubElement(vlan, "vlans")

            if v == "all":
                vlans.text == "all"
            elif v == "add":
                vlans.text == v  + "," + str(new_vlan)
            else:
                vlans.text = v  + "," + str(new_vlan)                    # The value from each iteration which is the current vlans assigned to the port
                                                                     # We will also add a comma plus new vlan we want to add. This vlan was created in
                                                                     # vlan() funtion. We saved it do a vlan_dict(),  line 231. This allows to add all
                                                                     # vlans back.

            # Write the XML tree to file. This will be accessed later and sent to the device. The file will be written with unique device IP
            # to it. Second, write the file path to a dictionary so they can be used to send the configs

            if ip in core_switch_array:
                core_dict[ip] = "C:\Python\Trunk_Vlans_%s.xml" % ip
                tree = xml.ElementTree(root)

                try:
                    with open("C:\Python\Trunk_Vlans_%s.xml" % ip, "wb") as fh:
                        tree.write(fh)
                except TypeError:
                    print("Error while saving. Returning you to gateway setup")
                    redundancy()

            elif ip in access_switch_array:
                access_dict[ip] = "C:\Python\Trunk_Vlans_%s.xml" % ip
                tree = xml.ElementTree(root)

                try:
                    with open("C:\Python\Trunk_Vlans_%s.xml" % ip, "wb") as fh:
                        tree.write(fh)
                except TypeError:
                    print("Error while saving. Returning you to gateway setup")
                    redundancy()

    # Now that our first iteration of the array build in logging_device is complete we will reset our dictionary and continue to the next device.
    # This proccess will happen untill all device have been accessed.

    dict.clear(vlan_to_port)

def topology_deploy():

    hsrp_file = "C:\Python\HSRP_Send_Config.xml"
    hsrp2_file = "C:\Python\HSRP2_Send_Config.xml"
    vlan_file = "C:\Python\VLAN_Send_Config.xml"
    vlan2_file = "C:\Python\VLAN_2_Send_Config.xml"
    vlan_acc_file = "C:\Python\VLAN_Access_Send_Config.xml"
    headers = "\n {:15} {:30} ".format("Config", "Status\n")

    loop_count = 1
    for k, file in core_dict.items():                       # Iterate through core_dict. The K == the IP, while the V(file) == a file path created earlier

        try:
            m = manager.connect(host=k, port=830, timeout=3, username=get_username, password=get_password, device_params={'name': 'csr'})
        except (AttributeError, ncclient.NCClientError) as error:
            status_dict[k] = error
            continue

        print("\n")
        print("%s: Sending configuration... \n" % k )
        print(headers)

        if loop_count == 1:
            send_config(m, " HSRP", hsrp_file)                   # Send HSRP file using send config function. We send m which is the netconf connection, and filepaths
            send_config(m, " VLAN", vlan_file)                   # By using this function we've elemenated about 20-30 lines of code
            send_config(m, " Interface", file)
            save_configuration(m)
        elif loop_count > 1:
            send_config(m, " HSRP", hsrp2_file)
            send_config(m, " VLAN", vlan2_file)
            send_config(m, " Interface", file)
            save_configuration(m)
        for k, v in status_dict.items():                    # Print the status of each type of config. This are logged in the send_config funtion
            print("{:<15} {:<30}".format(k, v))

        loop_count = loop_count + 1

    status_dict.clear()                                     # Clear the dictionary so it can be used in the access switch configurations

    for k, file in access_dict.items():                     # Here is where we loop the through the access dictionary. Its the same as the latter but one less file(HSRP)

        try:
            m = manager.connect(host=k, port=830, username=get_username, password=get_password, device_params={'name': 'csr'}) # NETCONF Login
        except AttributeError as error:
            status_dict[k] = str(error)
            pass

        print("\n")
        print("%s: Sending configuration... \n" % k)
        print(headers)

        send_config(m, " VLAN", vlan_acc_file)
        send_config(m, " Interface", file)
        save_configuration(m)
        for k, v in status_dict.items():
            print("{:<15} {:<30}".format(k, v))

    print("\n")
    core_switch_array.clear()
    access_switch_array.clear()
    menu()

def view_config():

    print("Atempting to connect...")
    time.sleep(2)
    clear()

    for ip in core_switch_array:
        view_config_loops(ip)
    for ip in access_switch_array:
        view_config_loops(ip)

    access_switch_array.clear()
    core_switch_array.clear()

def view_config_loops(ip):

    config = """<filter><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"></native></filter>"""
    int_stats = """<filter><interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/></filter>"""
    heading_1 = "Trunk Interfaces-----------------|\n"
    heading_2 = "Port-Channels--------------------|"
    heading_3 = "Vlan Information-----------------|\n"
    hsrp_headers =  "    L3 Interface(s)----------------------|  {:6} {} {} {:21} {:17} {:14} {:11}  {:16} {:16}  ".format(" ", "\n", "\n", "    Interface", "IP", "Mask", "Prio", "Group", "VIP\n")

    try:
        m = manager.connect(host=ip, port=830, timeout=3, username=get_username, password=get_password, device_params={'name': 'csr'})
    except (AttributeError, ncclient.NCClientError) as error:
        print("Connection Unsuccessful: " + ip)
        print("Reason: %s" % error)
        time.sleep(3)
        clear()
        pass

    print("! Connection Established !")
    time.sleep(1)
    clear()

    try:
        config_data = m.get(config)
        config_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]  # Convert XML reponse to dictionary

        print("Collecting Data...")
        time.sleep(2)
        clear()

        print("Device:" + ip + "-------------------------------------\n\n")

        # isinstance() is used in each block of code. This checks to see if xmltodict has converted out XML data
        # into a list, or dictionary. This is important because the two data structures are accessed differently.
        # When there is one of something, like vlan, port-channel, data is converted to an dict(), when there is
        # more than one of something, data is converted to an array. Depending on the latter, a function will be
        # access to display the data

        # The dictionaries are access dircectly, while list items need to be looped throug. The caveat is that as we looped
        # the items will still need to be access like dicionary. This is called a list of dictionaries i.e. a mess. This ones are simple.

        #  The function is repetitive so it will be explained in line 755-765

        # Check for HSRP or vlan interfaces Lines 752-762

        try:
            hsrp_details = config_details["native"]["interface"]["Vlan"]
            if isinstance(hsrp_details, list):                                      # Check if list
                print(hsrp_headers)                                                 # Print headers variable
                for hsrp in hsrp_details:                                           # for i, or hsrp in this case, iterate throught the list of dictionaries
                    access_hsrp_dict(hsrp)                                          # Send to config and output
            elif isinstance(hsrp_details, dict):                                    # Check if dictionary
                print(hsrp_headers)                                                 # Print headers variable
                access_hsrp_dict(hsrp_details)                                      # Send to config and output. Access dictionary directly since there is only one of
        except (KeyError):                                                          # what your look for. Example, there could be one svi.
            pass

        # Check for HSRP or vlan interfaces Lines 768-777

        try:
            gig_details = config_details["native"]["interface"]["GigabitEthernet"]
            if isinstance(gig_details, list):
                for int in gig_details:
                    access_interface_dicts(int)
            elif isinstance(gig_details, dict):
                access_interface_dicts(gig_details)
            print("\n")
        except (KeyError):
            pass

        # Check for trunks on physical interfaces and port-channel interfaces Lines 776 -798

        try:
            gig_details = config_details["native"]["interface"]["GigabitEthernet"]
            for items in gig_details:
                try:
                    access_trunk_dicts_2(items)
                except KeyError:
                    continue
        except (KeyError):
            pass

        try:
            port_channel = config_details["native"]["interface"]["Port-channel"]
            if isinstance(port_channel, list):
                for items in port_channel:
                    try:
                        if items["switchport"]["mode"]["trunk"] == None:
                            access_trunk_dicts(items)
                    except KeyError:
                        continue
            elif isinstance(port_channel, dict):
                access_trunk_dicts(port_channel)
        except (KeyError):
            pass

        # Check for what port-channel the physical interfaces are associated with Lines 802-807

        try:
            gig_details = config_details["native"]["interface"]["GigabitEthernet"]
            for items in gig_details:
                access_po_dictionaries(items)
        except (KeyError):
            pass

        interface_sideXside(heading_1, heading_2)                                    # Side by side print for interfaces and port-channels

        try:
            vlan_details = config_details["native"]["spanning-tree"]["vlan"]
            if isinstance(vlan_details, list):
                print(heading_3)
                for items in vlan_details:
                    access_vlan_dict(items)
            elif isinstance(vlan_details, dict):
                print(heading_3)
                access_vlan_dict(vlan_details)
        except (KeyError):
            pass

    except UnboundLocalError:
        pass
    print("\n")

# The following funtions are used to access the dictionaries and print the contents. Each funtion output something different
# Most output formatting can be done here. Hears wre edited in view_config_loops() function

def access_hsrp_dict(hsrp_details):

    try:
        hsrp_info = "{:6} {:12} {:15}  {:19} {:11}  {:12} {:19}".format(" ", hsrp_details["name"],
                                                                             hsrp_details["ip"]["address"]["primary"]["address"],
                                                                             hsrp_details["ip"]["address"]["primary"]["mask"],
                                                                             hsrp_details["standby"]["standby-list"]["priority"],
                                                                             hsrp_details["standby"]["standby-list"]["group-number"],
                                                                             hsrp_details["standby"]["standby-list"]["ip"]["address"])
        print(hsrp_info)
        interfaces.append(hsrp_details["name"])

    except (KeyError, TypeError):
        access_interface_dicts(hsrp_details)
        pass

def access_interface_dicts(interface_details):

    try:
        int_info = "{:6} {:12} {:15}  {:19} {:12} {:12} {:19}  ".format(" ", interface_details["name"],
                                                                             interface_details["ip"]["address"]["primary"]["address"],
                                                                             interface_details["ip"]["address"]["primary"]["mask"],
                                                                             "---", "---", "   ---")
        if interface_details["name"] in interfaces:
            pass
        else:
            print(int_info)
    except (KeyError, TypeError):
        pass

def access_trunk_dicts(item):

        # This applies to the next two funtions, Lines 871 - 929

        # This section takes care of a few things. One, grabs trunks with no vlans assigned. Two, grabs trunk with vlans assigned through conditional statement
        # Three, since the devices like to save the same vlan multiple time like 10,10,12,13,13 we will need to clean that up and reformat. All in the sake of
        # getting a clean output.

    if item["switchport"]["mode"]["trunk"] == None:                                             # Check to see if the interfaces is trunk

        int_trunks = "{:5} {:8} {:19}".format(" ", item["name"], "all")                         # Map interfaces configured with mode trunk
        phys_trunk_array.append(int_trunks)                                                     # store them in an array with trunk "all" This is really a placeholder
                                                                                                # as a interface wil non specified trunks will not be in the ouput without some work

        if item["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]:                                  # If vlans are store in this key "vlans"
            vlan_to_port[item["name"]] = item["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]     # Store the name and vlans to vlan_to_port dict.
            vlans_to_list = item["switchport"]["trunk"]["allowed"]["vlan"]["vlans"].split(",")       # Turn list to an array.
            remove_duplicates = list(dict.fromkeys(vlans_to_list))                                   # Convert to dict to remove duplicates
            join_vlans = ",".join(remove_duplicates)                                                 # Join the list back together
            remove_old = phys_trunk_array.remove("{:5} {:8} {:19}".format(" ", item["name"], "all")) # Remove the old list entry create on line 875
            pc_trunks = "{:5} {:8} {:19}".format(" ", item["name"], join_vlans)                      # Format our string
            phys_trunk_array.append(pc_trunks)                                                       # Save the new string to the same as arrayfrom line 876
            pass
        elif item["switchport"]["trunk"]["allowed"]["vlan"]["add"]:
            vlan_to_port[item["name"]] = item["switchport"]["trunk"]["allowed"]["vlan"]["add"]
            vlans_to_list = item["switchport"]["trunk"]["allowed"]["vlan"]["add"].split(",")
            remove_duplicates = list(dict.fromkeys(vlans_to_list))
            join_vlans = ",".join(remove_duplicates)
            remove_old = phys_trunk_array.remove("{:5} {:8} {:19}".format(" ", item["name"], "all"))
            pc_trunks = "{:5} {:8} {:19}".format(" ", item["name"], join_vlans)
            phys_trunk_array.append(int_trunks)
            pass

def access_trunk_dicts_2(item):

    if item["switchport"]["mode"]["trunk"] == None:

        int_trunks = "{:5} {:8} {:19}".format(" ", item["name"], "all")
        phys_trunk_array.append(int_trunks)

        if item["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]:
            vlan_to_port[item["name"]] = item["switchport"]["trunk"]["allowed"]["vlan"]["vlans"]
            vlans_to_list = item["switchport"]["trunk"]["allowed"]["vlan"]["vlans"].split(",")
            remove_duplicates = list(dict.fromkeys(vlans_to_list))
            join_vlans = ",".join(remove_duplicates)
            remove_old = phys_trunk_array.remove("{:5} {:8} {:19}".format(" ", item["name"], "all"))
            pc_trunks = "{:5} {:8} {:19}".format(" " , item["name"], join_vlans)
            phys_trunk_array.append(pc_trunks)

        elif item["switchport"]["trunk"]["allowed"]["vlan"]["add"]:
            vlan_to_port[item["name"]] = item["switchport"]["trunk"]["allowed"]["vlan"]["add"]
            vlans_to_list = item["switchport"]["trunk"]["allowed"]["vlan"]["add"].split(",")
            remove_duplicates = list(dict.fromkeys(vlans_to_list))
            join_vlans = ",".join(remove_duplicates)
            remove_old = phys_trunk_array.remove("{:5} {:8} {:19}".format(" ", item["name"], "all"))
            pc_trunks = "{:5} {:8} {:19}".format(" ", item["name"], join_vlans)
            phys_trunk_array.append(int_trunks)
        else:
            pass


    # OrderedDict([('name', '1/0/2'), ('switchport', OrderedDict([('mode', OrderedDict([('@xmlns', 'http://cisco.com/ns/yang/Cisco-IOS-XE-switch'), ('trunk', None)]))])), ('channel-group',
# OrderedDict([('@xmlns', 'http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet'), ('number', '30'), ('mode', 'active')]))])
def access_po_dictionaries(items):

    try:
        if "channel-group" in items:
            po_channels = "{:3} {:10} {:5} {}".format(" ", items["name"],items["channel-group"]["number"],items["channel-group"]["mode"])
            po_array.append(po_channels)
    except KeyError:
        pass

def access_vlan_dict(item):

    try:
        vlan_row = " {:3} Priority: {:<6}       Vlans: {} ".format(" ", item["priority"],  item["id"])
        print(vlan_row)
    except KeyError:
        pass

def interface_sideXside(heading_1, heading_2):

    get_length = len(phys_trunk_array)                                       # Get length of phys_trunk_array. Since its longer than po_array
    for i in range(1, get_length):                                           # Use the range method and using the get_length variable
        po_array.append("")                                                  # Add extra items to the shorter array.

    print("{:3} {:37} {}".format(" ", heading_2, heading_1))
    print("{:5} {:9} {:7} {:17} {:8} {} ".format(" ", "Int", "PoCh", "Mode", "Int", "Trunked VLANs--------\n"))

    for phy_port, po_channel in zip(phys_trunk_array, po_array):             # Loop through the two arrays using zip, Print the items side by side
        print("{} {:33} {}" .format(" ", po_channel, phy_port))              # Print the items side by side
    print("\n")

    po_array.clear()                                                         # Clear the po_array for the next devices interfaces to be stored
    phys_trunk_array.clear()                                                 # Clear the phys_trunk_array for the next devices interfaces to be stored

def send_config(m, config_type, file):

    try:

        config_file = open(file).read()                                     # Open file send from the topology_deploy() function
        m.edit_config(config_file, target="running")                        # Send file, target running config
        status_dict[config_type] = "Configuration Successful"               # If successful, log config type and status to status_dict

    except ncclient.NCClientError as error:
        status_dict[config_type] = str(error)                               # If unsuccessful, log config type and status to status_dict
        pass
    except SyntaxError as error:
        status_dict[config_type] = str(error)                               # If successful, log config type and status to status_dict
        pass
    except UnboundLocalError as error:
        status_dict[config_type] = str(error)                               # If successful, log config type and status to status_dict
        pass

def cleanup_empty_elements(root_var, file):

    # Writes configuration to file, re-opens the file to finds any nodes/elements that are empty, ex. <OSPF>EMPTY<OSPF> and deletes them. This will cause NETCONF
    # to throw a syntax error due to the XML tree being incomplete incomplete. This is create every time you hit enter when asked for an input.

    tree = xml.ElementTree(element=root_var)
    tree.write(file_or_filename=file)

    root = ET.fromstring(open(file=file).read())
    for element in root.xpath("//*[not(node())]"):
        element.getparent().remove(element)

    tree = xml.ElementTree(element=root)
    tree.write(file_or_filename=file)

def save_configuration(m):

    try:
        save_payload = """
                       <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
                       """
        response = m.dispatch(ET.fromstring(save_payload))
        status_dict[" CopyRunStart"] = "Success"
    except ncclient.NCClientError as error:
        status_dict[" CopyRunStart"] = error
        pass

def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

if __name__ == '__main__':

    menu()
    log_devices()


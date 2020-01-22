try:
    import sys
except ImportError:
    print("Module sys not available.")
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
    import paramiko
except ImportError:
    print("Module paramiko not available.")
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
    import collections
except ImportError:
    print("Module multiprocessing not available.")
try:
    import xml.dom.minidom as dom
except ImportError:
    print("Module xml.dom.minidom not available.")
try:
    from multiprocessing import Process
    import multiprocessing
except ImportError:
    print("Module multiprocessing not available.")

nested_dict = dict()
nested_dict_2 = dict()
queue_dict = dict()
interface_dict = dict()
policy_map_dict  = dict()
parent_map_dict = dict()
temp_dict = dict()
status_dict = dict()
child_dict = { }
parent_dict = { }
class_maps = " "
policy_maps = " "

bandwidth_range = range(1, 1000)
percent_range = range(1,100)

int_options = ["Tunnel", "GigabitEthernet", "FastEthernet", "Loopback"]
int_types = ["0/0/0", "0/0/1", "0/0/2", "0/0/3"]
match_types = ["match-any", "match-all"]
wred_types = ["dscp-based", "precedence-based"]
shape_pol_actions = ["shape", "police"]
qos_actions = ["bandwidth", "priority"]
nested_dict_array = ["class-default" ]

tag_array = ["af11" , "af12", "af13", "af21", "af22", "af23", "af31", "af32", "af33", "af41", "af42", "af43", "cs1", "cs2", "cs3", "cs4", "cs5", "cs6", "cs7",  "dscp0", "dscp8", "dscp10", "dscp12", "dscp14", "dscp16",
            "dscp18", "dscp20", "dscp22", "dscp24", "dscp26", "dscp28", "dscp30", "dscp32", "dscp38", "dscp34", "dscp40", "dscp46", "dscp56"]

classmap_file = "C:\Python\XML_Filters\Send_Config\QoS\QoS_Send_Config.xml"
classmap_2_file = "C:\Python\XML_Filters\Send_Config\QoS\QoS_Send_Config_2.xml"

save_payload = """
               <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
               """

config = """  <filter>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
</native>
</filter>
"""

def cleanup_empty_elements(root_var, file):

    tree = xml.ElementTree(element=root_var)
    tree.write(file_or_filename=file)

    root = ET.fromstring(open(file=file).read())
    for element in root.xpath("//*[not(node())]"):
        element.getparent().remove(element)

    tree = xml.ElementTree(element=root)
    tree.write(file_or_filename=file)

                                                                                                                          # Below are various arrays function for the use of TAB and auto complete

def tag_selection(text, state):
    tag_commands = [cmd for cmd in tag_array if cmd.startswith(text)]

    if state < len(tag_commands):
        return tag_commands[state]
    else:
        return None

def int_type_selection(text, state):
    int_type_commands = [cmd for cmd in int_types if cmd.startswith(text)]

    if state < len(int_type_commands):
        return int_type_commands[state]
    else:
        return None

def int_selection(text, state):
    int_opt_commands = [cmd for cmd in int_options if cmd.startswith(text)]

    if state < len(int_opt_commands):
        return int_opt_commands[state]
    else:
        return None

def qos_shape_pol_selection(text, state):
    shape_pol_commands = [cmd for cmd in shape_pol_actions if cmd.startswith(text)]

    if state < len(shape_pol_commands):
        return shape_pol_commands[state]
    else:
        return None

def qos_action_selection(text, state):
    qos_action_commands = [cmd for cmd in qos_actions if cmd.startswith(text)]

    if state < len(qos_action_commands):
        return qos_action_commands[state]
    else:
        return None

def qos_match_selection(text, state):
    match_types_commands = [cmd for cmd in match_types if cmd.startswith(text)]

    if state < len(match_types_commands):
        return match_types_commands[state]
    else:
        return None

def match_class_selection(text, state):
    class_selection = [cmd for cmd in nested_dict_array if cmd.startswith(text)]

    if state < len(class_selection):
        return class_selection[state]
    else:
        return None

def wred_type_selection(text, state):
    wred_selection = [cmd for cmd in wred_types if cmd.startswith(text)]

    if state < len(wred_selection):
        return wred_selection[state]
    else:
        return None

def disable_paging(remote_conn):
    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    output = remote_conn.recv(1000)
    return output

def paramiko_login():                                                                                   # Paramiko login with output.
                                                                                                                          # User_Option

    global device_ip
    device_ip = input("Please enter device IP: ")

    try:
        command1 = "show run class-map \n"
        command2 = "show run policy-map \n"
        username = 'cisco'
        password = 'cisco'

        remote_conn_pre = paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_conn_pre.connect(device_ip, username=username, password=password, look_for_keys=False, allow_agent=False)
        remote_conn = remote_conn_pre.invoke_shell()
        disable_paging(remote_conn)

        remote_conn.send("\n")

        remote_conn.send(command1)
        time.sleep(2)

        output = remote_conn.recv(5000)
        output_str = output.decode('utf-8')
        class_maps = output_str

        remote_conn.send(command2)
        time.sleep(2)

        output = remote_conn.recv(5000)
        output_str_2 = output.decode('utf-8')
        policy_maps = output_str_2

        print(class_maps)
        print(policy_maps)

    except paramiko.ssh_exception:
        print("\n")
        print("Connection Unsuccessful")
        print("\n")

def nested_dict_breakdown():

    int_1 = 0
    for v in nested_dict.values():
        int_1  = int_1 + 1
        temp_dict["Queue_%s" % int_1 ] = v["Name"]
        nested_dict_array.append(v["Name"])

def send_config_file(file):

    device_connect()

    loop_count = 0
    while loop_count != 3:
        try:

            config_file = open(file).read()
            m.edit_config(config_file, target="running")
            status_dict["Great"] = "Configuration Successful"
            save_configuration()
            break
        except ncclient.operations.RPCError:
            status_dict["Syntax Error"] = "Syntax Error"
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
            loop_count = loop_count + 1
            pass
            continue

    loop_count = 0
    while loop_count != 3:
        try:

            config_file = open(classmap_2_file).read()
            m.edit_config(config_file, target="running")
            status_dict["Great"] = "Configuration Successful"
            save_configuration()
            break
        except ncclient.operations.RPCError:
            status_dict["Syntax Error"] = "Syntax Error"
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
            loop_count = loop_count + 1
            pass
            continue

    for k, v in status_dict.items():
        print(v)


###########################################################################

def save_configuration():

    try:
        response = m.dispatch(ET.fromstring(save_payload))
    except ncclient.NCClientError:
        pass
    except (TypeError, NameError):
        print("\n")
        pass

###########################################################################

def device_connect():                                                                                      # Netconf Login # User_Option

    device_input = input("Please enter device IP: ")
    loop_count = 0
    while loop_count != 3:
        try:

            global m
            m = manager.connect(host=device_input, port=830, username="cisco", password="cisco",
                                             device_params={'name': 'csr'})
            break

        except AttributeError:
            loop_count = loop_count + 1
            pass
            continue
        except ncclient.NCClientError:
            loop_count = loop_count + 1
            pass
            continue
        except gaierror:
            loop_count = loop_count + 1
            pass
            continue

def view_class_maps():                                                                                  # View current Class-map dictionary with configured options

    if not nested_dict:
        print("\n")
        print("No Class-maps Configured")
    else:
        for v in nested_dict.values():
            print("\n")
            print("{:15} {:<35}".format("Class: ", v["Name"]))
            print("_____")
            print("\n")
            print("{:15} {:<35}".format("Prematch: ", v["Prematch"]))
            int_dict = 0
            while int_dict <= 20:
                int_dict = int_dict + 1
                try:
                    if "Tag_%s" % int_dict in v:
                        print("{:15} {:<35}".format("Tag_%s: "% int_dict, v["Tag_%s" % int_dict]))
                except KeyError:
                    print("\n")
                    break
                    pass

def view_child_policy():                                                                                # View current Child dictionary with configured options

    int_dict = 0

    if not child_dict:
        print("No Child PoliciesConfigured")
    else:
        for k, v in child_dict.items():
            print("\n")
            print("{:15} {:<35}".format("Policy: ", v))
            print("_______")

        for k, v in queue_dict.items():
            int_dict = int_dict + 1
            print("\n")
            try:
                print("{:15} {:<35}".format("Queue", v["Name"]))
                print("{:15} {:<35}".format("Action", v["Action"]))
                print("{:15} {:<35}".format("Allocation", v["Allocation"]))
            except KeyError:
                continue
                pass
            try:
                print("{:15} {:<35}".format("Queue Limit", v["Queue_Limit"]))
            except KeyError:
                continue
                pass
            try:
                print("{:15} {:<35}".format("Congestion", v["Wred_Mode"]))
            except KeyError:
                continue
                pass

def view_parent_policy():                                                                              # View current Parent dictionary with configured options

    try:
        print("{:15} {:<35}".format("Parent: ", parent_dict["Policy-map"]))
        print("_____________")
        print("\n")
        print("{:15} {:<35}".format("Match_Class: ", parent_dict["Match_Class"]))
        print("{:15} {:<35}".format("Child_Policy: ", parent_dict["Child_Policy"]))
        print("{:15} {:<35}".format("Action: ", parent_dict["Action"]))
        print("{:15} {:<35}".format("Bits: ", str(parent_dict["Bits"])))
    except KeyError:
        print("No Parent Policies Configured")

def search_dicts():                                                                                         # This function is used to modify dictionary built within a sing;r program insance. If you close the program, dictionaries are wiped.

    int_1 = 0
    view_class_maps()
    view_child_policy()
    view_parent_policy()
    dict_1_len = (len(nested_dict))

    while True:
        print("\n")
        print(" 1: Modify Class-maps")
        print(" 2: Modify Child Policies")
        print(" 3: Modify Parent Policies")
        print(" 4: Main Menu")

        print("\n")
        question_1 = input("Please select an option: ")
        print("\n")

        if question_1 == "1":                                                                               # Modify class-map tagging

            print("\n")
            key = input("Configuration Selection: ")
            change = input("New Configuration: ")                                         # Select the tag to modify

            if dict_1_len  > 1:
                class_input = input("Which Class: ")                                            # If multiple class-map are configured, please select the desired class-map to modify
                for k, v in nested_dict.items():
                    if v["Name"] == class_input:
                        try:
                            nested_dict[k][key] = change                                           # Apply the new v based off the change variable
                            break
                        except KeyError:
                            pass
                    else:
                        print("\n")

            else:
                for k, v in nested_dict.items():                                                     # If one one class-map exist, use this loop
                    while int_1 < 1:
                        int_1 = int_1 + 1
                        try:
                            nested_dict[key] = change
                            break
                        except KeyError:
                            pass

            view_class_maps()

        if question_1 == "2":                                                                              # Modify child_policy

            view_child_policy()

            print("\n")
            key = input("Configuration Selection: ")                                       # Select which option to modify based on the far left column
            change = input("New Configuration: ")                                         # Enter the desired change
            print("\n")

            for k, v in queue_dict.items():
                try:
                    queue_dict[k][key] = change                                                   # Apply the new v based off the change variable
                except KeyError:
                    pass

            view_child_policy()

        if question_1 == "3":                                                                              #Modify Parent policy

            view_parent_policy()

            print("\n")
            key = input("Configuration Selection: ")                                        #Select which part of the configuration to modify
            print("\n")

            if key == "Bits":                                                                                    # If bits is selected, apply the MBits to bit equations
                print("\n")
                try:
                    bandwidth_input = int(input("Bandwidth (Mbits:)   "))
                    print("\n")
                    if bandwidth_input in bandwidth_range:

                        bandwidth = 1000000 * bandwidth_input
                        bandwidth = int(bandwidth)

                        parent_dict[key] = str(bandwidth)
                        break

                    else:
                        print("\n")
                        print("Invalid input")
                        print("\n")
                        continue

                except ValueError:
                    print("\n")
                    print("Invalid input")
                    print("\n")
                    pass
                                                                                                                            # Other options to change as well, Actions, Match_class, and Child_Policy
            elif key == "Action":
                change = input("New Configuration: ")
                parent_dict[key] = change

            elif key == "Match_Class":
                change = input("New Configuration: ")
                parent_dict[key] = change

            elif key == "Child_Policy":
                change = input("New Configuration: ")
                parent_dict[key] = change

            else:
                search_dicts()

            view_parent_policy()
            search_dicts()

        if question_1 == "4":
            main()

def view_config_send(file):

    print("\n")
    print("Configuration: ")
    print("\n")

    Interface_config = open(file=file).read()
    print(dom.parseString(str(Interface_config)).toprettyxml())

    while True:

        print("\n")
        print(" 1: Send Single Device Configuration")
        print(" 2: Cancel Configuration Send")

        print("\n")
        question_1 = input("Please select an option: ")
        print("\n")

        if question_1 == "1":
            send_config_file(file=file)
            break
        if question_1 == "2":
            print("\n")
            print("Configuration Canceled")
            print("\n")
            break
        else:
            print("\n")
            print("Invalid Selection")
            print("\n")

def qos_configuration():                                                                                                # Class-map configuration build. All class-map slection options are mapped to a doctionary for later consumption

    root = xml.Element("config")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    policy_element = xml.Element("policy")
    native_element.append(policy_element)
    class_element = xml.Element("class-map")
    class_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
    policy_element.append(class_element)

    int_1 = 0
    while True:

        int_1 = int_1 + 1
        class_map_dict = dict()

        try:

            print("\n")
            print("Create class-map")
            print("\n")

            class_input = input("Cass-map name: ")
            class_id = xml.SubElement(class_element, "name")
            class_id.text = class_input

            class_map_dict["Name"] = class_input

            while True:

                readline.parse_and_bind("tab: complete")
                readline.set_completer(qos_match_selection)
                print("\n")
                match_type_input = input("Match Type (match-any/all): ")
                print("\n")

                if match_type_input in match_types:

                    prematch_element = xml.SubElement(class_element, "prematch")
                    prematch_element.text = match_type_input
                    match_element = xml.SubElement(class_element, "match")
                    class_map_dict["Prematch"] = match_type_input
                    break

                else:
                    print("\n")
                    print("Invalid input")
                    print("\n")
                    continue

            try:

                print("\n")
                print("Please add match statements")
                print("\n")
                print("Press CTRL+C to escape at any time")
                print("\n")

                int_2 = 0
                tag_match_dict = dict()

                while True:                                                                                                         # Class-map Tag loop use CTRL+C  to exit loop
                    int_2 = int_2 + 1
                    try:

                        readline.parse_and_bind("tab: complete")                                        # Use tab function to check avaiable QoS tags
                        readline.set_completer(tag_selection)

                        tag_value = input("Tag:  ")                                                                    # Configured tags

                        if tag_value in tag_array:                                                                        # Ceck tag_array to vailidate tags

                            match_1_element = xml.SubElement(match_element, "tag")
                            match_1_element.text = tag_value

                            tag_match_dict["Tag_%s" % int_2] = tag_value                            # Mapp tag values to dictonary for later consumption

                        else:
                            print("\n")
                            print("Invalid Input")
                            print("\n")
                            continue
                    except ValueError:
                        print("\n")
                        print("Invalid Input")
                        print("\n")
                        continue
                    except KeyboardInterrupt:
                        pass
                        class_map_dict.update(tag_match_dict)
                        nested_dict["Class_%s" % int_1] = class_map_dict
                        break
            except KeyboardInterrupt:
                pass
                break
        except KeyboardInterrupt:
            pass
            main()
            break

def policy_map_configuration():                                                                 #  Child Policy Configration

    int_1 = 0
    bandwidth_used = 0
    nested_dict_breakdown()

    pol_map_input = input("Please create policy map name: ")
    child_dict["Name"] = pol_map_input
    parent_dict["Name"] = pol_map_input

    print("\n")
    print("Policy-map Configuration")
    print("\n")

    if bandwidth_used <= 100:
        for v in temp_dict.values():                                                                    # Loops through class-map file and automaticlly maps the queue names, you with be prompted here for queue actions. Once loops is complete (based of class-maps configured earlier
                                                                                                                            # you will be send to the main menu
           int_1 = int_1 + 1
           queue_dict["Queue_%s" % int_1] = {}
           print("Bandwidth Allocation: %s" % bandwidth_used)
           print("\n")
           print("Queue: %s " % v)
           print("\n")

           queue_dict["Queue_%s" % int_1]["Name"] = v                               # Name key by queue and apply V which is the class-map name configred in temp doctionary


           readline.parse_and_bind("tab: complete")
           readline.set_completer(qos_action_selection)
           band_prio = input("Please Enter class-map type (bandwidth/priority): ")

           while True:
                if band_prio not in qos_actions:

                   print("\n")
                   print("Invalid Selection")
                   print("\n")
                   band_prio = input("Please Enter class-map type (bandwidth/priority): ")

                else:
                    break

           while band_prio == "priority":
               queue_dict["Queue_%s" % int_1]["Action"] = "priority"

               try:
                   print("\n")
                   bandwidth_input = int(input("Bandwidth Percent: "))
                   bandwidth_used = bandwidth_used + int(bandwidth_input)
                   print("\n")

                   if bandwidth_input in bandwidth_range:

                       bandwidth_used = bandwidth_used + int(bandwidth_input)
                       queue_dict["Queue_%s" % int_1]["Allocation"] = bandwidth_input
                       break

                   else:

                       print("\n")
                       print("Invalid Input")
                       print("\n")
               except:
                   print("\n")
                   print("Invalid Input")
                   print("\n")

           while band_prio == "bandwidth":

                   queue_dict["Queue_%s" % int_1]["Action"] = "bandwidth"

                   try:
                       print("\n")
                       bandwidth_input = int(input("Bandwidth Percent: "))
                       bandwidth_used = bandwidth_used + int(bandwidth_input)
                       print("\n")

                       if bandwidth_input in bandwidth_range:

                           bandwidth_used = bandwidth_used + int(bandwidth_input)
                           queue_dict["Queue_%s" % int_1]["Allocation"] = bandwidth_input
                           break

                       else:

                           print("\n")
                           print("Invalid Input")
                           print("\n")
                   except:
                       print("\n")
                       print("Invalid Input")
                       print("\n")

           wred = input("Enabled WRED (yes/no): ").lower()

           while True:
                if wred == "yes":
                    queue_dict["Queue_%s" % int_1]["Congest_avoid"] = "random-detect"
                    print("\n")

                    readline.parse_and_bind("tab: complete")
                    readline.set_completer(wred_type_selection)

                    wred_mode = input("Precedence-based or DSCP-based: ").lower()

                    if wred_mode == "precedence-based":
                        queue_dict["Queue_%s" % int_1]["Wred_Mode"] = "precedence-based"
                        break
                    elif wred_mode == "dscp-based":
                        queue_dict["Queue_%s" % int_1]["Wred_Mode"] = "dscp-based"
                        break
                    else:
                        print("\n")
                        print("Invalid Selection")
                        print("\n")
                        continue

                elif wred == "no":
                    break

           while True:
                queue_limit = input("Enabled Queue Limit (yes/no):  ").lower()

                if queue_limit == "yes":
                    queue_dict["Queue_%s" % int_1]["Queue_Limit"] = "queue-limit"

                    try:
                        queue_limit_val = int(input("Queue Limit Value: "))
                        queue_dict["Queue_%s" % int_1]["Queue_Limit"] = queue_limit_val
                        break
                    except ValueError:
                        print("\n")
                        print("Invalid Input")
                        print("\n")
                elif queue_limit == "no":
                    break
                else:
                    print("\n")
                    print("Invalid input")
                    print("\n")
                    continue

        print("\n")
        print("All queues assigned")                                                                    # Loops ends when all queus are assigned, or all class have been looped though via temp_dict
        print("\n")
    else:
       print("All bandwidth has been allocated")
       print("\n")

    view_child_policy()
    main()

def shaping():                                                                                                      # Build Parent policy dictionary for later consumptions

    pol_map_input = input("Parent policy map: ")
    parent_dict["Policy-map"] = pol_map_input

    readline.parse_and_bind("tab: complete")                                               # Use tab for options, "Class-default" is the only option currently in the array, arbitrary value.
    readline.set_completer(match_class_selection)

    print("\n")
    nest_input = input("Nested Class: ")
    print("\n")

    parent_dict["Match_Class"] = nest_input

    for child_policy in child_dict.values():                                                        # Place Child policy   in Parent dictionary for later consumption

        parent_dict["Child_Policy"] = child_policy

        readline.parse_and_bind("tab: complete")
        readline.set_completer(qos_shape_pol_selection)

        shape_or_police = input("Shape or Police: ")

        while shape_or_police in shape_pol_actions:
            parent_dict["Action"] =shape_or_police
            break
        else:
            print("\n")
            print("Invalid input")
            print("\n")
            continue

        while True:
            try:

                print("\n")
                bandwidth_input = int(input("Bandwidth (Mbits:)   "))               # Inputs MBits to be converted to bitd
                print("\n")

                if bandwidth_input in bandwidth_range:                                      # Converts bandwith (MBITs) to bits

                    bandwidth = 1000000 * bandwidth_input
                    bandwidth = int(bandwidth)

                    parent_dict["Bits"] = bandwidth
                    break
                else:
                    print("\n")
                    print("Invalid input")
                    print("\n")
                    continue
            except ValueError:
                print("\n")
                print("Invalid input")
                print("\n")
                continue

    main()

def  Qos_Interface():                                                                                             # Interface function which allows the QoS policy to be mapped to an interface

    root = xml.Element("config")
    root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
    root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)

    int_element = xml.SubElement(native_element, "interface")

    while True:

        readline.parse_and_bind("tab: complete")                                               # Use tab function to see avaiable interfaces, interfaces are written in array (int_options)
        readline.set_completer(int_selection)

        print("\n")
        int_type = input("Interface Type: ")

        if int_type in int_options:                                                                             # Check to see if the intergace is in int_option array

            int_type_element = xml.SubElement(int_element, int_type)
            temp_dict["Interface"] = int_type
            break
        else:
            print("\n")
            print("Invalid input")
            print("\n")
            continue

    while True:

        readline.parse_and_bind("tab: complete")                                             # Use tab function to see avaiable interfaces, interfaces are written in array (int_types)
        readline.set_completer(int_type_selection)
        print("\n")
        int_num = input("interface number:")
        print("\n")

        if int_num in int_types:                                                                                # Check to see if the intergace is in int_type array

            int_num_element = xml.SubElement(int_type_element, "name")
            int_num_element.text = int_num
            temp_dict["Number"] = int_num
            break
        else:
            print("\n")
            print("Invalid input")
            print("\n")
            continue

    service_1_element = xml.SubElement(int_type_element, "service-policy")
    service_1_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")

    interface_dict["Interfaces"] = temp_dict

def policy_build():                                                                                                  # Build complete Qos policy based off build 1, 2 funtions

    root = xml.Element("config")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    policy_element = xml.Element("policy")
    native_element.append(policy_element)

    view_class_maps()
    view_child_policy()
    view_parent_policy()

    build_1()
    build_2()

def build_1():

                                                                                                                                    # (Loops) Builds class-map configuration from dictionaries built in the "Configure class-map" section.
    root = xml.Element("config")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    policy_element = xml.Element("policy")
    native_element.append(policy_element)

    for v in nested_dict.values():                                                                             # Class-map build, apply class names, match polucy (match-any/all)

        class_element = xml.Element("class-map")
        class_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
        policy_element.append(class_element)

        class_id = xml.SubElement(class_element, "name")
        class_id.text = v["Name"]

        prematch_element = xml.SubElement(class_element, "prematch")
        prematch_element.text = v["Prematch"]
        match_element = xml.SubElement(class_element, "match")

        int_dict =0
        while int_dict <= 20:                                                                                        # Apply configured tags withing the class-maps
            int_dict = int_dict + 1
            try:
                if  "Tag_%s" % int_dict in v:
                    match_1_element = xml.SubElement(match_element, "dscp")
                    match_1_element.text = v["Tag_%s" % int_dict]

                    try:
                        tree = xml.ElementTree(root)
                        with open("C:\Python\XML_Filters\Send_Config\QoS\QoS_Send_Config.xml", "wb") as fh:
                            tree.write(fh)
                    except FileNotFoundError:
                        pass

            except KeyError:
                break
                pass

    for v in child_dict.values():                                                                                                         # Policy-map build with basic configuration. No queuing options are applied during this build.

        policy_map_element = xml.Element("policy-map")
        policy_map_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
        policy_element.append(policy_map_element)

        pol_map_name = xml.SubElement(policy_map_element, "name")
        pol_map_name.text = v

        for v in queue_dict.values():

            pol_class_element = xml.SubElement(policy_map_element, "class")
            pol_name = xml.SubElement(pol_class_element, "name")
            pol_name.text = v["Name"]

            action_list_element = xml.SubElement(pol_class_element, "action-list")
            action_type_element = xml.SubElement(action_list_element, "action-type")
            action_type_element.text = v["Action"]

            priority_container = xml.SubElement(action_list_element, v["Action"])
            percent_element = xml.SubElement(priority_container, "percent")
            percent_element.text = str(v["Allocation"])

            try:
                tree = xml.ElementTree(root)
                with open("C:\Python\XML_Filters\Send_Config\QoS\QoS_Send_Config.xml", "wb+") as fh: # Saving build #1 to file. Class-maps and Child policies (without queuing options)  are saved to the same file.
                    tree.write(fh)
            except FileNotFoundError:
                pass

def build_2():                                                                                                                                          # Build the Child-policies again, but this time we will apply the queuing policies such as WRED (types, ) Queue Limits etc.

    root = xml.Element("config")
    native_element = xml.Element("native")
    native_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-native")
    root.append(native_element)
    policy_element = xml.Element("policy")
    native_element.append(policy_element)

    for v in child_dict.values():                                                                                                              # Loop through Child-Policy dictionary, apply configuration options

        policy_map_element = xml.Element("policy-map")
        policy_map_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
        policy_element.append(policy_map_element)

        pol_map_name = xml.SubElement(policy_map_element, "name")
        pol_map_name.text = v

        for v in queue_dict.values():

            pol_class_element = xml.SubElement(policy_map_element, "class")
            pol_name = xml.SubElement(pol_class_element, "name")
            pol_name.text = v["Name"]

            while True:                                                                                                                                 # While WRED option in dictionary value, apply the following configrations.
                if "Wred_Mode" in v:
                    action_list_element = xml.SubElement(pol_class_element, "action-list")
                    action_type_element = xml.SubElement(action_list_element, "action-type")
                    action_type_element.text = v["Congest_avoid"]
                    random_detect = xml.SubElement(action_list_element, v["Congest_avoid"])
                    wred_mode = xml.SubElement(random_detect, v["Wred_Mode"])

                    try:
                        tree = xml.ElementTree(root)
                        with open("C:\Python\XML_Filters\Send_Config\QoS\Qos_Send_Config_2.xml", "wb") as fh:  # Saving build #2 to file. Parent policiesand Child policies (with queuing options)  are saved to the same file.
                            tree.write(fh)
                    except FileNotFoundError:
                        pass

                    break
                else:
                    break

            while True:                                                                                                                              # While queue limit option in dictionary value, apply the following configrations.
                if "Queue_Limit" in v:
                    action_list_element = xml.SubElement(pol_class_element, "action-list")
                    action_type_element = xml.SubElement(action_list_element, "action-type")
                    action_type_element.text = "queue-limit"
                    queue_limit = xml.SubElement(action_list_element, "queue-limit")
                    queue_limit_val = xml.SubElement(queue_limit, "queue-limit-value")
                    queue_limit_val.text = v["Queue_Limit"]                                                                  # Queue limit int

                    try:
                        tree = xml.ElementTree(root)
                        with open("C:\Python\XML_Filters\Send_Config\QoS\Qos_Send_Config_2.xml", "wb") as fh: # Saving build #2 to file. Parent policiesand Child policies (with queuing options)  are saved to the same file.
                            tree.write(fh)
                    except FileNotFoundError:
                        pass

                    break
                else:
                    break

        # Parent policy is read directly from dictionary, no key/value looping needed

        policy_map_element = xml.Element("policy-map")
        policy_map_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")
        policy_element.append(policy_map_element)

        pol_map_name = xml.SubElement(policy_map_element, "name")
        pol_map_name.text = parent_dict["Policy-map"]

        pol_class_element = xml.SubElement(policy_map_element, "class")
        pol_name = xml.SubElement(pol_class_element, "name")
        pol_name.text = parent_dict["Match_Class"]

        action_list_element = xml.SubElement(pol_class_element, "action-list")
        action_type_element = xml.SubElement(action_list_element, "action-type")
        action_type_element.text = parent_dict["Action"]

        if action_type_element.text == "police":
            police = xml.SubElement(action_list_element, "police-target-bitrate")
            police_rate= xml.SubElement(police, "police")
            bit_rate = xml.SubElement(police_rate, "bit-rate")
            bit_rate.text = str(parent_dict["Bits"])

            try:
                tree = xml.ElementTree(root)
                with open("C:\Python\XML_Filters\Send_Config\QoS\Qos_Send_Config_2.xml", "wb+") as fh: # Saving build #2 to file. Parent policiesand Child policies (with queuing options)  are saved to the same file.
                    tree.write(fh)
            except FileNotFoundError:
                pass

        elif action_type_element.text == "shape":
            shape = xml.SubElement(action_list_element, "shape")
            average = xml.SubElement(shape, "average")
            bit_rate = xml.SubElement(average, "bit-rate")
            bit_rate.text = str(parent_dict["Bits"])

        for v in child_dict.values():                                                                                                     # Nest child policy configured in option #2 (Configure Policy-maps) withing the Parent dictionary
            action_list_element = xml.SubElement(pol_class_element, "action-list")
            action_type_element = xml.SubElement(action_list_element, "action-type")
            action_type_element.text = "service-policy"
            service_policy_element = xml.SubElement(action_list_element, "service-policy")
            service_policy_element.text = v                                                                                      # Nested Child policy

        try:
            tree = xml.ElementTree(root)
            with open("C:\Python\XML_Filters\Send_Config\QoS\Qos_Send_Config_2.xml", "wb+") as fh: # Saving build #2 to file. Parent policiesand Child policies (with queuing options)  are saved to the same file.
                tree.write(fh)
        except FileNotFoundError:
            pass

        if not interface_dict:
            main()
        else:
            for k, v in interface_dict.items():

                int_element = xml.SubElement(native_element, "interface")
                int_type_element = xml.SubElement(int_element, v["Interface"])
                int_num_element = xml.SubElement(int_type_element, "name")
                int_num_element.text = v["Number"]

                service_1_element = xml.SubElement(int_type_element, "service-policy")
                service_1_element.set("xmlns", "http://cisco.com/ns/yang/Cisco-IOS-XE-policy")

                try:
                    tree = xml.ElementTree(root)
                    with open("C:\Python\XML_Filters\Send_Config\QoS\Qos_Send_Config_2.xml", "wb+") as fh:
                        tree.write(fh)
                except FileNotFoundError:
                    pass

                for k in parent_map_dict.keys():

                    service_1_output = xml.SubElement(service_1_element, "output")
                    service_1_output.text = k

                    try:
                        tree = xml.ElementTree(root)
                        with open("C:\Python\XML_Filters\Send_Config\QoS\Qos_Send_Config_2.xml", "wb+") as fh:
                            tree.write(fh)
                    except FileNotFoundError:
                        pass

def main():

    config_selection = ' '
    while config_selection != 'q':

        print("\n")
        print("Basic Network QoS  Programabiltiy and Automation Program")
        print("\n")
        print("1. Configure Class-map")
        print("2. Configure Policy-map")
        print("3. Confgure Policy-map (shaping)")
        print("4. Interface Selection")
        print("5. Build Policy File")
        print("6. Modify Dicts")
        print("7. Send Configuration")
        print("8. Get Configuration")
        print("[q] (quit)")
        print("\n")

        config_selection = input("Please select an option:  ")
        print("\n")

        if config_selection == "1":
            qos_configuration()
        elif config_selection == "2":
            policy_map_configuration()
        elif config_selection == "3":
            shaping()
        elif config_selection == "4":
            Qos_Interface()
        elif config_selection == "5":
            policy_build()
        elif config_selection == "6":
            search_dicts()
        elif config_selection == "7":
            view_config_send(classmap_file)
        elif config_selection == "8":
            paramiko_login()


if __name__ == '__main__':

    main()

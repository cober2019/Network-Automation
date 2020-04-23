from os import system, name

try:
    from netmiko import  ConnectHandler
    from netmiko import ssh_exception
except ImportError:
    print("Netmiko no installed")
try:
    import  time
except ImportError:
    print("time no installed")
try:
    import  re
except ImportError:
    print("time no installed")
try:
    import requests
except ImportError:
    module_array.append("request")
    pass
try:
    import warnings
except ImportError:
    module_array.append("warnings")
    pass
try:
    import json
except ImportError:
    module_array.append("json")
try:
    import  EndpointTracker2 as EPCollect
except ImportError:
    pass
try:
    import  validators
except ImportError:
    pass
try:
    import  ipaddress
except ImportError:
    pass

ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request') # Filtering annoying security errors. Not an exception but warning.
headers = {'content-type': 'text/xml'}

###################################################################
#### File Used to read/write during runtime

get_file_1 = "C:\Python\ACI\Get_ACI.txt"
get_file_2 = "C:\Python\ACI\Get_ACI_2.txt"
get_file_3 = "C:\Python\ACI\Get_ACI_3.txt"

###################################################################
#### Commands used by netmiko during program runtime

get_port_channel = "show port-channel summary"
module_mode = "vsh_lc"
show_infra_mappings = "show system internal eltmc info vlan brief"
debug_mode = "debug platform internal tah elam asic 0"
trigger_reset = "trigger reset"
initializer ="trigger init in-select 6 out-select 0"
start = "start"
status = "stat"
end = "end"
exit ="exit"
get_ovec = "report | grep  ovec"

###################################################################
#### Carious array, variables, and dictionaries used during runtime

ep_forward_array_1 = ['Forwarding Information: ', '\n' ]
ep_forward_array_2 = [' ', '\n']
device_dict_nested = {}
device_dict_nested_2 = {}
credentials_array = [ ]
leaf_array = [ ]

def device_login(username, password):

    clear()
    print("|-Target Layer--------------------|")
    print("|---------------------------------|")
    print("\n")

    # Commands sent to the CLI depend on the layer you want to capture at. As seen under the if staement, CLI code is different

    layer_selection = " "
    while layer_selection ==  "1" or "2":

        layer_selection = input(" 1. L3 capture\n 2. L2 Capture\n\n Selection: ")

        if layer_selection == "1":
            src_dst_iter =   [ip for ip in EPCollect.endpoint_array]
            set_layer = "set outer ipv4 src_ip {} dst_ip {}".format(src_dst_iter[0], src_dst_iter[1])
            get_report_1 = "show platform internal hal ep l3 all | grep %s" % src_dst_iter[1]
            get_report_2 = "show platform internal hal ep l3 all | grep %s" % src_dst_iter[0]
            dst_ep = " show endpoint ip %s" % src_dst_iter[1]
            src_ep = " show endpoint ip %s" % src_dst_iter[0]
            break
        elif layer_selection == "2":
            src_dst_iter = [mac for mac in EPCollect.ep_mac_array]
            set_layer = "set outer l2 src_mac {} dst_mac {}".format(src_dst_iter[0], src_dst_iter[1])
            dst_ep = " show endpoint mac %s" % src_dst_iter[1]
            src_ep = " show endpoint mac %s" % src_dst_iter[0]
            break
        else:
            print("\n")
            print("Invalid Input\n")

    clear()

    if layer_selection == "1":

        print("|-Target Port--------------------|")
        print("|--------------------------------|")
        print("\n")

        # If layer 1 is selected above, you will be asked to put in either a source or destination port

        port_selection = " "
        while port_selection == "1" or "2":

            port_selection = input(" 1. Source port\n 2. Destionation port:\n\n Selection: ")

            if port_selection == "1":
                target_port = input(" Port: ")
                set_inner_l4_1 = "set outer l4 src-port %s" % target_port
                break
            elif port_selection == "2":
                target_port = input(" Port: ")
                set_inner_l4_1 = "set outer l4 dst-port %s" % target_port
                break
            else:
                print("\n")
                print("Invalid Input\n")
    else:
        pass

    clear()
    print("Capture Configuration:\n")
    print(set_layer)

    try:
        print(set_inner_l4_1)
    except UnboundLocalError:
        pass

    print("\n")
    print("|-Target Leafs--------------------|")
    print("|-CTRL + C When Complete----------|")
    print("\n")

    while True:
       try:
            leaf = input("Leaf: ")
            leaf_array.append(leaf)
       except KeyboardInterrupt:
           break

    time.sleep(1)
    clear()

    # Start the ELAM capture setup using the leaf array created on line 153

    print("\n")
    print("|-Configuring Triggers------------|")
    print("|---------------------------------|\n")

    loop_count = 0
    for i in leaf_array:

        device_dict = {}
        source_dict = {}

        # Netmiko login credentials dictionary. Uses variables carried over from the EPCollect module

        credentials = {
            'device_type': 'cisco_ios',
            'host': i,
            'username': username,
            'password': password,
            'session_log': 'my_file.out'}


        # If login fails continue the loop at the next variable, or leaf

        try:
            credentials_array.append(credentials)
            try:
                device_connect = ConnectHandler(**credentials)
            except (ValueError, ssh_exception.AuthenticationException, ssh_exception.NetmikoTimeoutException) as error:
                print(error)
                continue
            ###################################################################################################
            # Gather the destination fabric VLAN, Endpoint VRF, and where the Endpoint was learned from

            # Send command to CLI which gets all endpoint information for with EP IP or MAC

            ep_fabric_vl_1 = device_connect.send_command(dst_ep)

            #Save string to file

            with open(get_file_1, "w") as report:
                report.write(ep_fabric_vl_1)

            # Open file and search lines for infrastructure vlans. Not all leafs will have a vlan
            # In this case store v to key as N/A.
            # If there is a vlan in a line, the regex will seach for the vlan at the begining of the line
            # to the next white space.

            with open(get_file_1, "r") as report:
                for line in report:
                    if re.findall(r'^[0-9].*?\s', line):
                        if EPCollect.ep_encap_array[1] in line:
                            vlan = re.findall(r'^[0-9].*?\s', line)
                            device_dict["Infra_vl"] = vlan[0]
                            break
                        elif re.findall(r'^[0-9].*?\s', line):
                            vlan = re.findall(r'^[0-9].*?\s', line)
                            device_dict["Infra_vl"] = vlan[0]
                            break
                    else:
                        device_dict["Infra_vl"] = "N/A"

            #Open file and search of the vrf in line. Leafs may have vlans but no vrf. In this case it will use a tunnel
            # to forward to the reporting leaf. Search begingin of line for lower case chars until the chars end with
            # either upper or lowercase chars. Write vrf to dictionary

            with open(get_file_1, "r") as report:
                for line in report:
                    if re.findall(r'^[a-z].*?[a-zA-Z].*?', line):
                        vrf = re.findall(r'^[a-z].*?:[a-zA-Z].*?\s', line)
                        device_dict["vrf"] = vrf[0]
                        break
                    else:
                        device_dict["vrf"] = "N/A"

            # Find where the endpoint was learned from. Could be ethernet, port-channel, or tunnel
            # search regex \b = border, starting with the interface type, ending in a number 0-9, or \b
            # Write to dictionary

            with open(get_file_1, "r") as report:
                for line in report:
                    if re.findall(r'\bpo.*?', line):
                        learnedFrom = re.findall(r'\bpo.*?[0-9]\b', line)
                        device_dict["LearnedFrom"] = learnedFrom[0]
                    elif re.findall(r'\beth.*?[0-9]', line):
                        learnedFrom = re.findall(r'\beth.*?[0-9]\b', line)
                        device_dict["LearnedFrom"] = learnedFrom[0]
                    elif re.findall(r'\btun.*?[0-9]', line):
                        learnedFrom = re.findall(r'\btun.*?[0-9]\b', line)
                        device_dict["LearnedFrom"] = learnedFrom[0]
            report.close()

            ##############################################################################################
            # Gather the source fabric VLAN, Endpoint VRF, and where the Endpoint was learned from
            # We are going to repeat the above lines, but write to a source dictionary

            ep_fabric_vl_2 = device_connect.send_command(src_ep)

            with open(get_file_1, "w") as report:
                report.write(ep_fabric_vl_2)

            with open(get_file_1, "r") as report:
                for line in report:
                    if re.findall(r'^[0-9].*?\s', line):
                        if EPCollect.ep_encap_array[0] in line:
                            vlan = re.findall(r'^[0-9].*?\s', line)
                            source_dict["Infra_vl"] = vlan[0]
                            break
                        elif re.findall(r'^[0-9].*?\s', line):
                            vlan = re.findall(r'^[0-9].*?\s', line)
                            source_dict["Infra_vl"] = vlan[0]
                            break
                    else:
                        source_dict["Infra_vl"] = "N/A"

            with open(get_file_1, "r") as report:
                for line in report:
                    if re.findall(r'^[a-z].*?[a-zA-Z].*?', line):
                        vrf = re.findall(r'^[a-z].*?:[a-zA-Z].*?\s', line)
                        source_dict["vrf"] = vrf[0]
                        break
                    else:
                        source_dict["vrf"] = "N/A"

            with open(get_file_1, "r") as report:
                for line in report:
                    if re.findall(r'\bpo.*?', line):
                        learnedFrom = re.findall(r'\bpo.*?[0-9]\b', line)
                        source_dict["LearnedFrom"] = learnedFrom[0]
                    elif re.findall(r'\beth.*?[0-9]', line):
                        learnedFrom = re.findall(r'\beth[0-9].*?[0-9]\b', line)
                        source_dict["LearnedFrom"] = learnedFrom[0]
                    elif re.findall(r'\btun.*?[0-9]', line):
                        learnedFrom = re.findall(r'\btun.*?[0-9]\b', line)
                        source_dict["LearnedFrom"] = learnedFrom[0]

            report.close()
            commands = device_connect.send_command(module_mode, expect_string="module-1#")
            device_connect.disable_paging(command='terminal length 0')

            ##################################################################################################
            # Gather Destination Endpoint Information Endpoint DB port, Hardware BD. This information is all
            # about hardware, or how the fabric see the path.

            # First we need to decide which commands we need to send to CLI. If an IP is the endpooint we will
            # will validate with the ipaddress module. If not a valid ip, we will use the excpetion as the
            # condition

            try:
                ipaddress.IPv4Address(src_dst_iter[0])
                get_report_1 = "show platform internal hal ep l3 all | grep %s" % src_dst_iter[1]
                get_report_2 = "show platform internal hal ep l3 all | grep %s" % src_dst_iter[0]
                network_report_1 = device_connect.send_command(get_report_1)
                network_report_2 = device_connect.send_command(get_report_2)
                ep_dest = src_dst_iter[0]
                ep_src = src_dst_iter[0]
            except ipaddress.AddressValueError:
                get_l2_src = "show platform internal hal ep l2 mac %s" % src_dst_iter[0]
                get_l2_dst = "show platform internal hal ep l2 mac %s" % src_dst_iter[1]
                network_report_1 = device_connect.send_command(get_l2_dst)
                network_report_2 = device_connect.send_command(get_l2_src)
                ep_dest = src_dst_iter[0].swapcase()
                ep_src = src_dst_iter[0].swapcase()
                pass

            with open(get_file_1, "w") as report:
                report.write(network_report_1)

            with open(get_file_1, "r") as report:
                for line in report:
                    bd = re.findall(r'\bBD-.*?\s', line)
                    if re.findall(r'\bEth.*?[0-9]\s', line):
                        learned_ep_1 = re.findall(r'\bEth[0-9].*?[0-9]\b', line)
                        device_dict["EP DB Port"] = learned_ep_1[0]
                        device_dict["EP Hw BD"] = bd[0]
                    elif re.findall(r'\bPo.*?[0-9]\s', line):
                        learned_ep_1 = re.findall(r'\bPo.*?[0-9]\b', line)
                        dst_interface = learned_ep_1[0]
                        device_dict["EP DB Port"] = learned_ep_1[0]
                        device_dict["EP Hw BD"] = bd[0]
                    elif re.findall(r'\bTun.*?[0-9]', line):
                        learned_ep_1 = re.findall(r'\bTun.*?[0-9]\b', line)
                        bd = re.findall(r'\bBD-.*?\s', line)
                        device_dict["EP DB Port"] = learned_ep_1[0]
                        device_dict["EP Hw BD"] = bd[0]
                        device_dict["Sw Port"] = "N/A"

            report.close()

            ###############################################################################################
            # Gather Source Endpoint Information  Endpoint DB port, Hardware BD

            with open(get_file_1, "w") as report:
                report.write(network_report_2)

            with open(get_file_1, "r") as report:
                for line in report:
                    bd = re.findall(r'\bBD-.*?\s', line)
                    if re.findall(r'\bEth.*?[0-9]\b', line):
                        learned_ep_1 = re.findall(r'\bEth[0-9].*?[0-9]\b', line)
                        src_interface = learned_ep_1[0]
                        source_dict["EP DB Port"] = learned_ep_1[0]
                        source_dict["EP Hw BD"] = bd[0]
                    elif re.findall(r'\bPo.*?[0-9]\s', line):
                        learned_ep_1 = re.findall(r'\bPo.*?[0-9]\b', line)
                        src_interface = learned_ep_1[0]
                        source_dict["EP DB Port"] = learned_ep_1[0]
                        source_dict["EP Hw BD"] = bd[0]
                    elif re.findall(r'\bTun.*?[0-9]\s', line):
                        learned_ep_1 = re.findall(r'\bTun.*?[0-9]\b', line)
                        source_dict["EP DB Port"] = learned_ep_1[0]
                        source_dict["EP Hw BD"] = bd[0]
                        source_dict["Sw Port"] = "N/A"

            exit_module = device_connect.send_command(exit, expect_string="")

            ###############################################################################################
            # Gather Source Endpoint Information  Endpoint Software port.

            port_channel = device_connect.send_command(get_port_channel)

            with open(get_file_1, "w") as report:
                report.write(port_channel)

            try:
                if "Tunnel" not in learned_ep_1[0]:

                    with open(get_file_1, "r") as report:
                        for line in report:
                            try:
                                if dst_interface in line:
                                    learned_phy_ports = re.findall(r'\bEth[0-9].*?[0-9]\b', line)
                                    if len(learned_phy_ports) > 1:
                                        join_ints = ", ".join(learned_phy_ports)
                                        device_dict["Sw Port"] = join_ints
                                        break
                                    else:
                                        device_dict["Sw Port"] = learned_phy_ports[0]
                                        break
                                else:
                                    device_dict["Sw Port"] = dst_interface
                            except UnboundLocalError:
                                pass

                    with open(get_file_1, "r") as report:
                        for line in report:
                            try:
                                if src_interface in line:
                                    learned_phy_ports = re.findall(r'\bEth[0-9].*?[0-9]\b', line)
                                    if len(learned_phy_ports) > 1:
                                        join_ints = ", ".join(learned_phy_ports)
                                        source_dict["Sw Port"] = join_ints
                                        break
                                    else:
                                        source_dict["Sw Port"] = learned_phy_ports[0]
                                        break
                                else:
                                    source_dict["Sw Port"] = src_interface
                            except UnboundLocalError:
                                pass
                else:
                    device_dict["Sw Port"] = "N/A"
                    source_dict["Sw Port"] = "N/A"

            except UnboundLocalError:
                pass

            ###############################################################################################
                    # Setup ELAM capture perameters and intialize the capture

            commands = device_connect.send_command(module_mode, expect_string="")
            device_connect.disable_paging(command='terminal length 0')
            debug = device_connect.send_command(debug_mode, expect_string="")
            reset_trigger = device_connect.send_command(trigger_reset, expect_string="")
            init_trigger = device_connect.send_command(initializer, expect_string="")
            layer_three = device_connect.send_command(set_layer, expect_string="")

            try:
                layer_four = device_connect.send_command(set_inner_l4_1, expect_string="")
            except UnboundLocalError:
                pass

            init = device_connect.send_command(start, expect_string="")
            stat = device_connect.send_command(status, expect_string="ed")

            print(" IP (Leaf): {} Status: {}".format(i, "Armed"))

            device_dict_nested_2.update({i: source_dict})
            device_dict_nested.update({i: device_dict})
            loop_count = loop_count + 1

        except (OSError, UnboundLocalError, TypeError) as error:
            print("Failed to initialize ELAM capture for leaf: %s") % i
            print("Error: " + error)
            continue

    print("\n")
    holder = input("Hit enter to check status: ")

    print("\n")
    print("Checking Trigger...")
    clear()

    ###############################################################################################
        # Present Endpoint ACI confiurations with external vlan tags

    print("Endpoints:\n")
    for endpoint_1, endpoint_2 in zip(EPCollect.query_array_1, EPCollect.query_array_2):
        print("{:54}{}".format(endpoint_1, endpoint_2))
    print("\n")

    ###############################################################################################
        # Present Endpoint hardware configuration create by the internal fabric

    try:
        print(" Source Endpoint Fabric Information:\n")
        for k,v in device_dict_nested_2.items():
            print(" {:1} {:<25} {:<20} {:<30} {:<20} {:<20} {:<27} {}".format(" ",
                                                                    "Leaf : " + k,
                                                                    "Infra_vl : " + v["Infra_vl"],
                                                                    "vrf: " + v["vrf"],
                                                                    "EP DB Port: " + v["EP DB Port"],
                                                                    "EP hw BD: " + v["EP Hw BD"],
                                                                    "LearningPort: " + v["LearnedFrom"],
                                                                    "Phys Port: " + v["Sw Port"]))

        print("\n")
    except KeyError as error:
        print(error)
        pass

    ###############################################################################################
        # Check to see if any of our ELAM traps have been triggered. If so crab the ovec hex, gther the report,
        # and find which port is associated the the hex.


    for leaf in leaf_array:
        try:
            credentials = {
                'device_type': 'cisco_ios',
                'host': leaf,
                'username': username,
                'password': password,
                'session_log': 'my_file.out'}

            try:
                device_connect = ConnectHandler(**credentials)
            except (ValueError, ssh_exception.AuthenticationException, ssh_exception.NetmikoTimeoutException) as error:
                continue

            commands = device_connect.send_command(module_mode, expect_string="")
            device_connect.disable_paging(command='terminal length 0')
            debug = device_connect.send_command(debug_mode, expect_string="")
            init_trigger = device_connect.send_command(initializer, expect_string="")
            stat = device_connect.send_command(status, expect_string="ed")

            if "Triggered" in stat:

                print(" IP (Leaf): {} Status: {}\n".format(leaf, "Triggered ####"))

                ###############################################################################################
                    # Request the ovec report from CLI and use regex to get the hex. Since the right of the x
                    # is the the important char, we will create a variable with only those chars. Here we
                    # are searching directly from string.

                ovec_report = device_connect.send_command(get_ovec)
                if  re.compile(r'\b0x.\b').findall(ovec_report):
                    hex = re.compile(r'\b0x.').findall(ovec_report)
                    hex_strip = str(hex[0].replace("0x", "")).swapcase()
                elif  re.compile(r'\b0x..\b').findall(ovec_report):
                    hex = re.compile(r'\b0x..').findall(ovec_report)
                    hex_strip = str(hex[0].replace("0x", "")).swapcase()
                ###############################################################################################
                        # Get full report, open it and scan for the port associated with the hex string.

                get_port = "show platform internal hal l2 port gpd"
                report_filtered = device_connect.send_command(get_port)
                with open("C:\\Python\ELAM_Report.txt", "w") as report:
                    report.write(report_filtered)

                try:
                    with open("C:\\Python\ELAM_Report.txt", "r") as report:
                        print("\n")
                        for line in report:
                            if re.findall(r'\b' + hex_strip + '.' + hex_strip   + '\s', line):
                                ovec_port = re.findall(r'\bEth[0-9].*?[0-9]\b', line)
                                device_dict_nested[leaf]["ovec"] = ovec_port[0]

                            elif re.findall(r'\b' + hex_strip + '..' + hex_strip + '\s', line):
                                ovec_port = re.findall(r'\bEth[0-9].*?[0-9]\b', line)
                                device_dict_nested[leaf]["ovec"] = ovec_port[0]

                                ###############################################################################################
                                # Present the destination Endpoints fabric forwarding information with ovec. If the final 3
                                # values show association then the forwarding path is correct.

                        print(" Infra_vl: {}    vrf: {}    EP hw BD: {}    EP DB Fw: {}    [LearningPort: {}    Phys Port: {}    Ovec Port: {}]". format(
                                                                                                                                    device_dict_nested[leaf]["Infra_vl"],
                                                                                                                                    device_dict_nested[leaf]["vrf"],
                                                                                                                                    device_dict_nested[leaf]["EP Hw BD"],
                                                                                                                                    device_dict_nested[leaf]["EP DB Port"],
                                                                                                                                    device_dict_nested[leaf]["LearnedFrom"],
                                                                                                                                    device_dict_nested[leaf]["Sw Port"],
                                                                                                                                    device_dict_nested[leaf]["ovec"]))

                        print("\n")
                except (NameError) as error:
                    continue
            else:
                continue
        except (UnboundLocalError, OSError) as error:
            print("Failed to initialize ELAM capture for leaf: %s") % leaf
            print("Error: " + error)
            continue

    complete = input("Capture Complete")

def get_infra_location(session, apic):

    uri_1 = "https://192.168.128.11/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAccPortP&target-" \
            "subtree-class=infraFexP,infraHPortS,infraPortBlk&query-target=subtree"
    uri_2 = "https://192.168.128.11/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraNodeP&target-" \
            "subtree-class=infraLeafS,infraNodeBlk,infraRsAccNodePGrp&query-target=subtree" \

    r_1 = session.get(uri_1, verify=False, headers=headers)
    pretty_data_1 = json.dumps(r_1.json(), indent=4)
    r_2 = session.get(uri_2, verify=False, headers=headers)
    pretty_data_2 = json.dumps(r_2.json(), indent=4)

    try:
        file = open(get_file_3, 'w')
        file.write(pretty_data_1)
        file.close()
    except:
        print("File Error")

def file_write_2(data):

    try:
        file = open(get_file_2, 'w')
        file.write(data)
        file.close()
    except:
        print("File Error")


def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

if __name__ == '__main__':

    EPCollect.apic_login()

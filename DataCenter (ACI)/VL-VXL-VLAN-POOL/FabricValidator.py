module_array = [ ]
from os import system, name
try:
    from netmiko import  ConnectHandler
    from netmiko import ssh_exception
except ImportError:
    module_array.append("netmiko")
try:
    import  re
except ImportError:
    module_array.append("re")
try:
    import  time
except ImportError:
    module_array.append("time")
try:
    import  ipaddress
except ImportError:
    module_array.append("ipaddress")
try:
    import VLAN_Pools as vlanPool
except ImportError:
    module_array.append("Vlan_Pools")
try:
    import requests
except ImportError:
    module_array.append("request")
    pass
try:
    import lxml.etree as ET
except ImportError:
    module_array.append("lxml")
    pass
try:
    import warnings
except ImportError:
    module_array.append("warnings")
    pass
try:
    import collections
except ImportError:
    pass

###################################################################
#### File Used to read/write during runtime

get_file_1 = "C:\Python\ACI\Get_ACI.txt"

def module_check():

    # Check to see if there is any python modules not install. If so you will be notified.
    if not module_array:
        print("Module validation passed!")
        time.sleep(2)
        clear()
    else:
        print("{:>75}".format("!!Program will close if all modules below aren't installed!!"))
        print("\n")
        for module in module_array:
            print("{:^84}".format(module))
        print("\n")
        ack = input("Press enter to acknowledge")
        clear()

def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

def apic_login():

    print("Fabric Credentials:\n")
    apic = input("APIC: ")
    username = input("Username: ")                              # Enter fabric username
    password = input("Password: ")

    uri = "https://%s/api/mo/aaaLogin.xml" % apic
    ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    headers = {'content-type': 'text/xml'}

    # POST username and password to the APIC

    raw_data = """<!-- AAA LOGIN -->
        <aaaUser name="{}" pwd="{}"/> 
        """.format(username, password)

    try:
        session = requests.Session()
        r = session.post(uri, data=raw_data, verify=False, headers=headers)  # Sends the request to the APIC
        response = r.text                                                    # save the response to variable

        if re.findall("\\bFAILED local authentication\\b", response):        # Check the response the string \\b is for border
            print("Login Failed, please verify credentials")                 # or exact string the regex
            print("\n")
            apic_login()
        elif re.findall("\\bFailed to parse login request\\b", response):    # Check the response the string \\b is for border
            print("Login Failed, please verify credentials")                 # or exact string the regex
            print("\n")
            apic_login()
        else:
            vlanPool.aci_gets.vlan_pools(session, apic)
            vlanPool.aci_gets.phys_domains(session, apic)
            body(session, apic,username, password)
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL): # If APIC IP is incorrect which makes the URI
        print("Login Failed, please verify APIC IP")                              # Invalid, this exception will be thrown.
        print("\n")
        apic_login()

def body(session, apic, username, password):


    leaf_array = [ ]
    leaf_dict = { }
    vlans = [ ]
    vlan_vxlan_array = [ ]
    vxlan_array = [ ]
    wrong_dict = { }
    correct_dict = { }
    vlan_pool = collections.defaultdict(list)
    phys_doms = collections.defaultdict(list)
    aaeps = collections.defaultdict(list)
    location = collections.defaultdict(list)
    path = collections.defaultdict(list)

    time.sleep(1)
    clear()                                                         # Clear terminal

    print("\n")
    print("|-Target Leafs--------------------|")
    print("|-CTRL + C When Complete----------|")
    print("\n")

    while True:
           try:
            leaf = input("Leaf: ")                                     # Input target leafs
            ipaddress.IPv4Address(leaf)                                # Check for valid IP
            leaf_array.append(leaf)                                    # If valid IP, store to array
           except (ipaddress.AddressValueError, ValueError):           # Exception for invalid IP
               print("Invalid IP Address\n")
               continue                                                # Continue loop, prompt again
           except KeyboardInterrupt:                                   # Break the loop using CTRL-C
               print("\n")
               break

    clear()
    print("Gathering VLAN to VXLAN Mappings...")
    time.sleep(2)
    clear()

    module_mode = "vsh_lc"                                               # Command used by netmiko ti access module smode
    show_infra_mappings = "show system internal eltmc info vlan brief"   # Command used to get vlan to vxlan mappings

    try:
        for leaf in leaf_array:                                          # Iterate through leaf array/fabric leafs

            vlan_vxlan_array = [ ]
            vxlan_array = [ ]
            vlans_array = [ ]
            wrong_vlans = [ ]

            credentials = {                                             # Netmiko credential dictionary
                'device_type': 'cisco_ios',
                'host': leaf,
                'username': username,
                'password': password,
                'session_log': 'my_file.out'}

            try:
                device_connect = ConnectHandler(**credentials)          # Connect to device/leaf using crdential dictionary
            except (ValueError, ssh_exception.AuthenticationException, ssh_exception.NetmikoTimeoutException) as error:
                print(error)                                            # Print error
                pass

            switch_to_hardware = device_connect.send_command(module_mode, expect_string="module-1#") # Send command store in variable to device
            device_connect.disable_paging(command='terminal length 0')                               # Disable paging on device CLI
            get_infra_mappings = device_connect.send_command(show_infra_mappings)                    # Send command store in variable to device

            with open(get_file_1, "w") as report:                                       # Write ouput to file
                report.write(get_infra_mappings)                                        # Variable create during netmiko session

            with open(get_file_1, "r") as report:
                for line in report:                                                     # Read file as report
                    if "802.1q" in line:                                                # Check if 802.1q in line
                       L2_info = (re.findall(r"q\b.*\s\b", line))                       # Grab text borded by q and whitespace
                       cleanup = L2_info[0].replace("q", "")                            # Remove q from string
                       cleanup = cleanup.replace("VXLAN", "")                           # Remove VXLAN from string
                       final_L2 = (re.findall(r"\b[0-9].*?[0-9]\b", cleanup))           # Grab vlan - bordered by anything [0-9] ending in [0-9]
                       if len(final_L2) == 1:                                           # Since final_2 cariable creates a list, see if the list length == 1
                           vlan = (re.findall(r"\b[0-9]\b", final_L2[0]))               # Find the vlan in final_2 index 0
                           vxlan = (re.findall(r"\b[0-9][0-9].*?[0-9]\b", final_L2[0])) # Find the vxlan in final_2 index 0
                           vlan_vxlan = str(vlan[0] + " " + vxlan[0])                   # Concatinate the two
                           vlan_split = vlan_vxlan.split(" ")                           # Create list of two using split.
                           vlans_array.append(vlan_split[0])                            # Index vlan, store to array
                           vxlan_array.append(vlan_split[1])                            # Index vxlan, store to array
                           vlan_vxlan_array.append(vlan_split)                          # Grab whole list, store to array
                       else:
                           vlans_array.append(final_L2[0])                              # If final_2 len != 1 index vlan, store to array
                           vxlan_array.append(final_L2[1])                              # If final_2 len != 1 index vxlan, store to array
                           vlan_vxlan_array.append(final_L2)                            # Grab whole list, store to array
                    else:
                        pass

                leaf_dict[leaf] = vlan_vxlan_array                                      # Store list in dictionaries. Keys being leaf IPs

                remove_duplicates_vlans = list(dict.fromkeys(vlans_array))              # Clear of duplicates in list. This allows us to have all assigned vlans across the fabric
                remove_duplicates_vxlans = list(dict.fromkeys(vxlan_array))             # Clear of duplicates in list. This allows us to have all assigned vxlans across the fabric

                clear()

                print("\n")
                for k, v in leaf_dict.items():                                          # Iterate through key/value pairs
                    wrong_array = []                                                    # List will be reset every k interation
                    correct_array = []                                                  # List will be reset every k interation
                    for v in v:
                        for vlan, vxlan in zip(remove_duplicates_vlans, remove_duplicates_vxlans):

                            if vlan == v[0] and vxlan == v[1]:
                                correct_array.append(" Leaf IP: " + k + "    |    VLAN: {:7} |   VXLAN ID: {:15}   ".format(vlan, vxlan))
                            if vlan == v[0] and vxlan != v[1]:
                                wrong_vlans.append(vlan)
                                wrong_array.append(" Leaf IP: " + k + "    |    VLAN: {:7} |   VXLAN ID: {:15}   ".format(v[0], v[1]))
                            else:
                                pass
                    if len(wrong_array) == 0:
                        correct_dict[k] = correct_array
                    else:
                        wrong_dict[k] = wrong_array


        remove_dups = list(dict.fromkeys(wrong_vlans))
        for vlan in remove_dups:
            pools = vlanPool.aci_gets.find_duplicatee_vlan(session, apic,vlan)
            vlan_pool[vlan].append(pools[0])
            phys_doms[vlan].append(pools[1])
            aaeps[vlan].append(pools[2])
            location[vlan].append(pools[3])
            path[vlan].append(pools[4])

        for key_1, v in wrong_dict.items():  # unpack k, v pairs
            if not v:  # If the key has no value, continue at the top of the loop
                continue
            else:
                for string in v:
                    vlan_1 = re.search(r'(?<=VLAN:\s).*?[0-9]\b', string)
                    print("   Fabric VLAN to VXLAN Mapping                               *Leaf Perspective")
                    print("--------------------------------------------------------------------------------\n")
                    print("   *" + string)
                    for key_2, v in correct_dict.items():
                        for string_2 in v:
                            vlan_2 = re.search(r'(?<=VLAN:\s).*?[0-9]\b', string_2)
                            try:
                                if vlan_1.group(0) == vlan_2.group(0):
                                    if string == string_2:
                                        pass
                                    else:
                                        print("    " + string_2)
                                else:
                                    pass
                            except AttributeError:
                                pass

                    unpacked_vlan_pools = [v for k, v in vlan_pool.items() if vlan_1.group(0) == k for v in v for v in v]
                    unpacked_phys_doms = [v for k, v in phys_doms.items() if vlan_1.group(0) == k for v in v for v in v ]
                    unpacked_aaep = [v for k, v in aaeps.items() if vlan_1.group(0) == k for v in v for v in v ]
                    unpacked_location = [v for k, v in location.items() if vlan_1.group(0) == k for v in v for v in v ]
                    unpacked_path = [v for k, v in path.items() if vlan_1.group(0) == k for v in v for v in v]

                    print("\n")
                    print("   Access Policy Details:\n")
                    print("     VLAN Pool(s): " + "\n                   ".join(unpacked_vlan_pools))
                    print("\n")
                    print("     Phys Dom(s):  " + "\n                   ".join(unpacked_phys_doms))
                    print("\n")
                    print("     AAEP(s):      " + "\n                   ".join(unpacked_aaep))
                    print("\n")
                    print("     Encap Loc.:   " + "\n                   ".join(unpacked_location))
                    print("\n")
                    print("     Path Attach:  " + "\n                   ".join(unpacked_path))
                    print("\n")


    except (UnboundLocalError,OSError):
        print("Something Went Wrong. Please Verify Connectivity and Credentials\n")
        pass

    stop = input("Program Ended")

if __name__ == '__main__':

    module_check()
    apic_login()
from os import system, name
try:
    from netmiko import  ConnectHandler
    from netmiko import ssh_exception
except ImportError:
    print("Netmiko not installed")
try:
    import  re
except ImportError:
    print("RE not installed")
try:
    import  time
except ImportError:
    print("time not installed")
try:
    import  ipaddress
except ImportError:
    print("ipaddress not installed")
###################################################################
#### File Used to read/write during runtime

get_file_1 = "C:\Python\ACI\Get_ACI.txt"

file = open("C:\Python\\vxlan.txt")
read = file.read()
print(read)
def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

def body():


    leaf_array = [ ]
    leaf_dict = { }
    vlans = [ ]
    vlan_vxlan_array = [ ]
    vxlan_array = [ ]
    wrong_dict = { }
    correct_dict = { }
    wrong_array = [ ]
    correct_array = [ ]

    print("Fabric Credentials:\n.")
    username = input("Username: ")                                  # Enter fabric username
    password = input("Password: ")                                  # Enter fabric password

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

            credentials = {                                             # Netmiko credential dictionary
                'device_type': 'cisco_ios',
                'host': leaf,
                'username': username,
                'password': password,
                'session_log': 'my_file.out'}

            try:
                device_connect = ConnectHandler(**credentials)          # Connect to device/leaf using crdential dictionary
            except (ValueError, ssh_exception.AuthenticationException,  # Catch netmiko exceptions
                    ssh_exception.NetmikoTimeoutException) as error:
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

                # The following variables will be used for conditional statements by gathering vlans/vxlans in the fabric, not where there are assigned currently. That wil be checked later

                remove_duplicates_vlans = list(dict.fromkeys(vlans_array))              # Clear of duplicates in list. This allows us to have all assigned vlans across the fabric
                remove_duplicates_vxlans = list(dict.fromkeys(vxlan_array))             # Clear of duplicates in list. This allows us to have all assigned vxlans across the fabric

                clear()

                print("\n")
                for k, v in leaf_dict.items():                                          # Iterate through key/value pairs
                    wrong_array = []                                                    # List will be reset every k interation
                    correct_array = []                                                  # List will be reset every k interation
                    for v in v:
                        for vlan, vxlan in zip(remove_duplicates_vlans, remove_duplicates_vxlans): # Iterate through both list we create on line 133, 134
                            if vlan == v[0] and vxlan == v[1]:                                     # Check see if the variables vlan/vxlan are == to values in the dictionary
                                correct_array.append(" Leaf IP: " + k + "    |    VLAN: {:7} |   VXLAN ID: {:15}   |".format(vlan, vxlan)) # Store value if true
                            if vlan == v[0] and vxlan != v[1]:                                     # Check see if the variables vlan is == to value but vxlan is not
                                wrong_array.append(" Leaf IP: " + k + "    |    VLAN: {:7} |   VXLAN ID: {:15}   |".format(v[0], v[1]))    # Store value if false
                            else:
                                pass
                    if len(wrong_array) == 0:               # If list length == to 0, or if mapping are correct store to dictionary
                        correct_dict[k] = correct_array
                    else:                                   # if list > 1 then a mapping wasnt correct, store to dictionary
                        wrong_dict[k] = wrong_array

        for k, v in wrong_dict.items():                     # unpack k, v pairs
            if not v:                                       # If the key has no value, continue at the top of the loop
                continue
            else:
                for string in v:                            # Else, unpack v (string) from v. This is needed because the v is a list of v(vlan, to vxlan mappings
                    vlan_1 = re.search(r'\bVL.*?[0-9]\b', string)               # Grab the first occurnece of and int, whihc would be the vlan
                    print("Fabric VLAN to VXLAN Mapping                                    *Leaf Perspective")
                    print("---------------------------------------------------------------------------------")
                    print(" *" + string)                                        # Print the value stored in wrong array, or incorrect mapping
                    for k, v in correct_dict.items():                           # Next unpack the correct mappings
                        for string_2 in v:                                      # Get the value in the value, or list in the list
                            vlan_2 = re.search(r'\bVL.*?[0-9]\b', string_2)     # Store the value
                            try:
                                if vlan_1.group(0) == vlan_2.group(0):          # Compare the to variables for correct and incorrect
                                    if string == string_2:                      # If they're equal each other, check if the string in each dict == each other.
                                        pass                                    # If they are, dont print since it was printed in the first unpacking
                                    else:
                                        print("  " + string_2)                  # ELSE, print the string
                                else:
                                    pass
                            except AttributeError:
                                pass
                    print("---------------------------------------------------------------------------------")
                    print("\n")

    except UnboundLocalError:
        print("Something Went Wrong. Please Verify Connectivity and Credentials\n")
        pass

    stop = input("Program Ended")

if __name__ == '__main__':

    body()
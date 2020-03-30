module_array = [ ]

from os import system, name
try:
    import re
except ImportError:
    module_array.append("request")
    pass
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
    import readline
except ImportError:
    module_array.append("readline")
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
    import time
except ImportError:
    module_array.append("time")

ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {'content-type': 'text/xml'}

get_file = "C:\Python\ACI\Get_ACI.xml"
get_file_2 = "C:\Python\ACI\Get_ACI_json.txt"

subnet_array = [ ]
total_gateways = len(subnet_array)
tenant_array = [ ]
query_dict = dict()

def module_check():

    # Check to see if there is any python modules not install. If so you will be notified.

    if not module_array:
        pass
    else:
        print("\n")
        print("{:>75}".format("!!Program will close if all modules below aren't installed!!"))
        print("\n")
        for module in module_array:
            print("{:^84}". format(module))
        print("\n")


def clear():

    # Clear screen for windows or MAC

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')

def tab_subnet_completion(text, state):

    # Used for subnet table completion

    subnet = [cmd for cmd in subnet_array if cmd.startswith(text)]

    if state < len(subnet):
        return subnet[state]
    else:
        return None

def view_tenants():

    # Find all Tenants that are configured in ACI

    headers = {'content-type': 'text/xml'}
    uri = "https://%s/api/class/fvTenant.json" % apic

    r = session.get(uri,verify=False, headers=headers)
    pretty_data = json.dumps(r.json(), indent=4)

    try:
        file = open(get_file_2, 'w')
        file.write(pretty_data)
        file.close()

        with open(get_file_2) as json_file:
            tenant_data = json.load(json_file)

        # Get the total number of Tenants so we can use this for loop (range). This is so the loop can iterate the
        # exact amount of times, no more, no less. Line 103

        total_count = int(tenant_data["totalCount"])

    except:
        print("File Error")

    try:
        index = 0
        for i in range(0, total_count):
            tenant_array.append(tenant_data["imdata"][index]["fvTenant"]["attributes"]["name"])
            index = index + 1
    except IndexError:
        pass

def find_subnet():

    global  subnet_array
    subnet_array = []

    view_tenants()

    uri_1 = "https://%s/api/class/fvBD.xml?query-target=subtree" % apic
    r = session.get(uri_1,verify=False, headers=headers)

    file_operation(r)

    tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
    root = tree.getroot()

    # Iterate through the xml tree and store all the subnet attributes to an array. This array will be used for
    # TAB completion and a total subnet count. Line 138

    for fvSubnet in root.iter("fvSubnet"):
        subnets = fvSubnet.get("ip")
        subnet_array.append(subnets)

    print("\n")
    print("--------------------------------------|")
    print("ACI Subnet Finder---------------------|")
    print("--------------------------------------|")
    print("\n")

    # Display as integer the total number of subnets in ACI

    total_gateways = len(subnet_array)
    print("Total Fabric Subnets: {}".format(total_gateways))
    print("\n")

    # Display previous queries during the program runtime. Line 148

    print("Previous Lookups:\n")

    for v in query_dict.values():
        print(v)
    print("\n")
    print("\n")

    # TAB completion for easy subnet find. Call tab_subnet_completion() function

    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_subnet_completion)

    print("Enter gateway IP plus prefix length (ex. 1.1.1.1/24)")
    print("\n")
    subnet_id = input("Please enter a gateway IP: ")
    print("\n")

    uri_2 = "https://%s/api/class/fvBD.xml?query-target=subtree" % apic
    r = session.get(uri_2,headers=headers)

    # Writes the contents of the GET to file, carries the response to the function

    file_operation(r)

    tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
    root = tree.getroot()

    # Opens the file and finds root. Iterates the the xml doc and finds the subnet location, ip. If the ip
    # contains the subnet_id variable, create location and store the IP. Grab the subnet scope as well.

    for fvSubnet in root.iter("fvSubnet"):
        location = fvSubnet.get("dn")
        ip = fvSubnet.get("ip")
        if subnet_id in ip:
            gps = location
            gps_ip = ip
            scope = fvSubnet.get("scope")

    # Iterates through the xml document and finds the bridge domain atrributes. Checks to see if the variable gps,
    # line 180, contains the bridge domain string. Use regex with boarder to find the exact string. Grabse unicast
    # route as well to check if routing is enabled.

    try:
        for fvBD in root.iter("fvBD"):
            bridge_domain = fvBD.get("name")
            if re.findall('\\b' + bridge_domain + '\\b', gps):
                gps_bd = bridge_domain
                uni_route = fvBD.get("unicastRoute")

        #Iterates through the xml document to find vrf attributes. Checks to see which vrf matches the location
        # create on line 177. Uses regex to find and exact string match.

        for fvRsCtx in root.iter("fvRsCtx"):
            vrf = fvRsCtx.get("tnFvCtxName")
            location = fvRsCtx.get("dn")
            if re.findall('\\b' + gps_bd + '\\b', location):
                gps_vrf = vrf

        for tenant in tenant_array:
            if tenant in gps:
                gps_tenant = tenant
            else:
                continue
    except UnboundLocalError:
        pass

    # All variables create above are used in the text variable and stored into a dictionary used in line 148.
    # variable also printed below.

    try:
        text = (" Subnet {} is located in {} Tenant, Bridge Domain {}\n\n Vrf: {}\n Routing Enabled: "
                                                                    "{}\n Scope: {}\n".format(gps_ip,
                                                                                              gps_tenant,
                                                                                              gps_bd,
                                                                                              gps_vrf,
                                                                                              uni_route,scope))
        print(text)
        query_dict[gps_ip] = text
        time.sleep(5)

        # Uses the clear function to clear the screen output for next query. Return to find_subnet() functions

        clear()
        find_subnet()

    except UnboundLocalError:
        print("Subnet doesn't exist \n")
        time.sleep(5)
        clear()
        find_subnet()

def file_operation(r):

    try:
        file = open(get_file, 'w')
        file.write(r.text)
        file.close()
    except:
        print("File Error")

def apic_login():

    #########################################################
    # APIC login credential code - Please fill in USERNAME and PASSWORD
    #########################################################

    global apic
    apic = input("Please enter an APIC IP: ")
    username = input("Username: ")
    password = input("Password: ")
    uri = "https://%s/api/mo/aaaLogin.xml" % apic

    raw_data = """<!-- AAA LOGIN -->
        <aaaUser name="{}" pwd="{}"/> 
        """.format(username, password)
    try:
        global session
        session = requests.Session()
        r = session.post(uri, data=raw_data, verify=False, headers=headers)
        print("Status Code:", r.status_code)
        find_subnet()
    except:
        print("\n")
        print("Unable to login. Very credentials and URI are correct")
        print("\n")
        apic_login()

if __name__ == '__main__':

    module_check()
    apic_login()
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
try:
    from socket import  gaierror
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

def view_tenants(session, apic):

    # Find all Tenants that are configured in ACI

    headers = {'content-type': 'text/xml'}
    uri = "https://%s/api/class/fvTenant.json" % apic

    r = session.get(uri,verify=False, headers=headers)
    response_dict = r.json()
    total_count = int(response_dict["totalCount"])

    try:
        index = 0
        for i in range(0, total_count):
            tenant_array.append(response_dict["imdata"][index]["fvTenant"]["attributes"]["name"])
            index = index + 1
    except IndexError:
        pass

def apic_login():

    print("Fabric Credentials:\n")
    apic = input("APIC: ")
    username = input("Username: ")
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
            pass
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL): # If APIC IP is incorrect which makes the URI
        print("Login Failed, please verify APIC IP")                              # Invalid, this exception will be thrown.
        print("\n")
        apic_login()


    return session, apic

if __name__ == '__main__':

    module_check()
    apic_detials = apic_login()

    while True:
        try:

            subnet_array = []

            view_tenants(apic_detials[0], apic_detials[1])

            uri_1 = "https://%s/api/class/fvBD.xml?query-target=subtree" % apic_detials[1]
            r = apic_detials[0].get(uri_1,verify=False, headers=headers)

            try:
                file = open(get_file, 'w')
                file.write(r.text)
                file.close()
            except:
                print("File Error")

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

            tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
            root = tree.getroot()

            # Opens the XML file and finds root. Iterates the the xml doc and finds the subnet location, ip. If the ip
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
                    if re.findall('[?<=/BD-]' + bridge_domain + '(?=/)', gps):
                        gps_bd = bridge_domain
                        uni_route = fvBD.get("unicastRoute")
                        unkwn_uni = fvBD.get("unkMacUcastAct")

                #Iterates through the xml document to find vrf attributes. Checks to see which vrf matches the location
                # create on line 177. Uses regex to find and exact string match.

                for fvRsCtx in root.iter("fvRsCtx"):
                    vrf = fvRsCtx.get("tnFvCtxName")
                    location = fvRsCtx.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', location):
                        gps_vrf = vrf

                # Iterate through class fvRtBD which will give you a DN showing the tenant, app profile, and endpoint groups.
                # We will use regex to search the dn with out BD
                # We will store these to list since a BD can live in more that one location

                aps = [ ]
                epgs = [ ]
                for fvRtBd in root.iter("fvRtBd"):
                    dn = fvRtBd.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                        ap = re.findall(r'(?<=ap-).*(?=/ep)', dn)
                        aps.append(ap[0])
                        epg = re.findall(r'(?<=epg-).*(?=\])', dn)
                        epgs.append(epg[0])

                    else:
                        pass

                # Iterate through the fvRsBDToOut class to find the L3Out the BD is associated with
                # We will use regex to search the dn with out BD
                # Sometime a BD isnt advertised externall so we ad a condition to the logic. Now leout variable will always have something
                # avoid issues down the road

                for fvRsBDToOut in root.iter("fvRsBDToOut"):
                    dn = fvRsBDToOut.get("dn")
                    if re.findall('[?<=/BD-]' + gps_bd + '(?=/)', dn):
                        if not fvRsBDToOut.get("tnL3extOutName"):
                            l3out = "N/A"
                        else:
                            l3out = fvRsBDToOut.get("tnL3extOutName")

                for tenant in tenant_array:
                    if tenant in gps:
                        gps_tenant = tenant
                    else:
                        continue
            except UnboundLocalError:
                pass

            # All variables create above are used in the text variable and stored into a dictionary used in line 148.
            # Unpack all the list we xreated earlier using list comprehension. We can then convert to string using the join method

            unpack_ap = [i for i in aps]
            unpack_epg = [i for i in epgs]
            text = (" Subnet {} is located in {} Tenant, Bridge Domain {}\n\n Vrf: {}\n L3out: {}\n Routing: "
                                                                        "{}\n Scope: {}\n Unkwn Uni: {}\n"
                                                                        " App Profile: {}\n EPG: {}\n".format(gps_ip,
                                                                                                              gps_tenant,
                                                                                                              gps_bd,
                                                                                                              gps_vrf,
                                                                                                              l3out,
                                                                                                              uni_route,scope,
                                                                                                              unkwn_uni,
                                                                                                              ", ".join(unpack_ap),
                                                                                                              ", ".join(unpack_epg)))
            query_dict[gps_ip] = text
            print(text)
            another_lookup = input("Please hit enter for another lookup")

            # Uses the clear function to clear the screen output for next query. Return to find_subnet() functions

            clear()

        except (UnboundLocalError, NameError):
            print("Subnet doesn't exist \n")
            time.sleep(2)
            clear()
            pass

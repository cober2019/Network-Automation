module_array = [ ]

from os import system, name, chdir
try:
    import ipaddress
except ImportError:
    module_array.append("ipaddress")
    pass
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
    import ELAM2
except ImportError:
    module_array.append("time")

ignore_warning = warnings.filterwarnings('ignore', message='Unverified HTTPS request') # Filtering annoying security errors. Not an exception but warning.

headers = {'content-type': 'text/xml'}
get_file = "C:\Python\ACI\Get_ACI.xml"
get_file_2 = "C:\Python\ACI\Get_ACI_json.txt"
get_file_3 = "C:\Python\ACI\Get_ACI_json_sub_ints.txt"
query_dict = dict()
info_dict = dict()
leaf_array = [ ]
endpoint_array = [ ]
ep_mac_array = [ ]
ep_encap_array = [ ]
query_array_1 = [ ]
query_array_2 = [ ]
sub_int_array = [ ]
failed_eps = [ ]
apic = " "

def apic_login():

    #########################################################
    # APIC login credential code - Please fill in USERNAME and PASSWORD
    #########################################################

    apic = input("APIC: ")
    username = input("Username: ")
    password = input("Password: ")
    print("\n")

    # APIC Login URI

    uri = "https://%s/api/mo/aaaLogin.xml" % apic

    # POST username and password to the APIC

    raw_data = """<!-- AAA LOGIN -->
        <aaaUser name="{}" pwd="{}"/> 
        """.format(username, password)

    try:
        session = requests.Session()
        r = session.post(uri, data=raw_data, verify=False, headers=headers)  # Sends the request to the APIC
        response = r.text  # save the response to variable

        if re.findall("\\bFAILED local authentication\\b",response):  # Check the response the string \\b is for border
            print("Login Failed, please verify credentials")  # or exact string the regex
            print("\n")
            apic_login()
        elif re.findall("\\bFailed to parse login request\\b",response):  # Check the response the string \\b is for border
            print("Login Failed, please verify credentials")  # or exact string the regex
            print("\n")
            apic_login()
        else:
            ELAM2.get_infra_location(session, apic)
            enpoint_tracker(session, apic)
            ELAM2.device_login(username, password)

    except (requests.exceptions.ConnectionError,requests.exceptions.InvalidURL) as error:  # If APIC IP is incorrect which makes the URI
        print(error)
        print("Login Failed, please verify APIC IP")  # Invalid, this exception will be thrown.
        print("\n")
        apic_login()

def enpoint_tracker(session, apic):

    # Main body of code that allows you to check for endpoints

    leaf_array = [ ]
    print("\n")
    print("----------------------------------------|")
    print("ACI Endpoint Tracker--------------------|")
    print("----------------------------------------|")
    print("\n")

    endpoint_1 = input("Endpoint: ")
    endpoint_2 = input("Endpoint: ")
    endpoint_array.append(endpoint_1)
    endpoint_array.append(endpoint_2)
    print("\n")

    failures = 0
    loop = 0
    for endpoint in endpoint_array:

        leaf_array.clear()

        try:
            # Check to see if the endpoint variables is an IP address. If so execute a GET to the variables URI. Both GET WILL run, one for XML, the other for JASON
            # The reason for both is that its easier to access data converted from JSON to dictionary.

            ipaddress.IPv4Address(endpoint) # Check if IP
            uri = "https://%s" % apic + "/api/node/class/fvCEp.xml?rsp-subtree=full&rsp-subtree-include=required&rsp-subtree-filter=eq(fvIp.addr," + "\"%s\"" % endpoint
            uri_2 = "https://%s" % apic + "/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&rsp-subtree-filter=eq(fvIp.addr," + "\"%s\"" % endpoint
            r_1 = session.get(uri, verify=False, headers=headers)
            r_2 = session.get(uri_2, verify=False, headers=headers)

            pretty_data = json.dumps(r_2.json(), indent=4)

            file_operation_1(r_1)                           # Write xml repsonse to file, carry r_1 to funtion - Line 238
            file_operation_2(r_2, pretty_data)              # Write JSON response to file, carry r_2 and pretty_data to functionLine 248

            tree = ET.parse('C:\Python\ACI\Get_ACI.xml')    # get XML tree root and iterate through XML elements. Find attributes, store to variables Line 133-138
            root = tree.getroot()

            for fvCEp in root.iter("fvCEp"):
                ep_mac = fvCEp.get("mac")
                encap = fvCEp.get("encap")
                ep_loc = fvCEp.get("dn")
                ep_ip = fvCEp.get("mac")
                ep_domain = fvCEp.get("lcC")

            try:
                with open(get_file_2) as json_file:  # Open JSON file create in file_operation_2 funtion Line 248.
                    endpoint_data = json.load(json_file)

                    total_count = int(endpoint_data["totalCount"])

                    if total_count == 0:
                        failure_notice = "{} not found".format(endpoint)
                        failures = failures + 1
                        failed_eps.append(failure_notice)
                        continue
                    else:
                        index = 0
                        try:
                            for i in range(0, 20):
                                report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvIp"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                                index = index + 1
                                leaf_array.append(report_node)
                        except IndexError:
                            pass
            except (TypeError):  # A type error will occure the endpoint is not found or the JSON files is empty
                pass

            # Here we will strip the string of all uneeded chars. Since the GET response doesnt supply use with all information we will create it ourselves
            # In our case we are break down dn="uni/tn-Production/ap-ANP-VL109/epg-EPG-VL109/ to get the Tenant, App Profile, EPG.
            location_rework = ep_loc.replace("tn-", "")
            location_rework = location_rework.replace("ap-", "")
            location_rework = location_rework.replace("epg-", "")
            location_rework = location_rework.replace("cep-", "")
            location_rework = location_rework.replace("uni", "")
            location_rework_2 = location_rework.replace("/", ",")
            location_to_array = location_rework_2.split(",")     # After dealing with th strings, we will place the data into an array,

            index = 0
            for i in location_to_array: # Now that we the array we can create dictionary. Increment variable index to make the keys unique and save i as the values
                info_dict["item_%s" % index] = i
                index = index + 1

            join_array = ' , '.join(leaf_array) # Convert leaf array to string. leaf_array was create on lines 207, 201, or 154. Doiong this will allow use to present
                                                # the data as a string not array

            # Prints all data collected from the above lines

            if loop == 0:
                ep_mac_array.append(ep_mac)
                ep_encap_array.append(encap)
                query_array_1.append(" Query:                {}".format(endpoint))
                query_array_1.append(" Reverse Lookup:       {}".format(ep_ip))
                query_array_1.append(" Tenant:               {}".format(info_dict["item_1"]))
                query_array_1.append(" App Prof:             {}".format(info_dict["item_2"]))
                query_array_1.append(" EPG:                  {}".format(info_dict["item_3"]))
                query_array_1.append(" Learned From:         {}".format(ep_domain))
                query_array_1.append(" Encap:                {}".format(encap))
                query_array_1.append(" Reporting Leafs:      {}".format(join_array))

            elif loop == 1:
                ep_mac_array.append(ep_mac)
                ep_encap_array.append(encap)
                query_array_2.append(" Query:                {}".format(endpoint))
                query_array_2.append(" Reverse Lookup:       {}".format(ep_ip))
                query_array_2.append(" Tenant:               {}".format(info_dict["item_1"]))
                query_array_2.append(" App Prof:             {}".format(info_dict["item_2"]))
                query_array_2.append(" EPG:                  {}".format(info_dict["item_3"]))
                query_array_2.append(" Learned From:         {}".format(ep_domain))
                query_array_2.append(" Encap:                {}".format(encap))
                query_array_2.append(" Reporting Leafs:      {}".format(join_array))

            loop = loop + 1

        except ipaddress.AddressValueError: # IF the endpoint is not an IP, the IP Address check will throw a value error. In turn we will use a different URI to
                                            # find the enpoint. At the end of the URI, fvCEP.mac
            uri = "https://%s" % apic + "/api/node/class/fvCEp.xml?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,fvRsToVm&query-target-filter=eq(fvCEp.mac," + "\"%s\"" % endpoint
            uri_2 = "https://%s" % apic + "/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,fvRsToVm&query-target-filter=eq(fvCEp.mac," + "\"%s\"" % endpoint

            r_1 = session.get(uri,verify=False, headers=headers)
            r_2 = session.get(uri_2,verify=False, headers=headers)
            pretty_data = json.dumps(r_2.json(), indent=4)

            file_operation_1(r_1)                   # Write xml repsonse to file, carry r_1 to funtion - Line 238
            file_operation_2(r_2, pretty_data)      # Write JSON response to file, carry r_2 and pretty_data to functionLine 248

            tree = ET.parse('C:\Python\ACI\Get_ACI.xml') # get XML tree root and iterate through XML elements. Find attributes, store to variables Line 133-138
            root = tree.getroot()

            key_error = 0
            for fvCEp in root.iter("fvCEp"):
                ep_name = fvCEp.get("name")
                ep_mac = fvCEp.get("mac")
                encap = fvCEp.get("encap")
                ep_loc = fvCEp.get("dn")
                ep_ip = fvCEp.get("ip")
                ep_domain = fvCEp.get("lcC")

            with open(get_file_2) as json_file:         # Open JSON file create in file_operation_2 funtion Line 238.
                endpoint_data = json.load(json_file)

                index = 0
                total_count = int(endpoint_data["totalCount"])

                if total_count == 0:
                    failure_notice = "{} not found".format(endpoint)
                    failures = failures + 1
                    failed_eps.append(failure_notice)
                    continue
                elif total_count > 1:

                    print("EP has more than one location. Likely cause: Sub-Interfaces\n")
                    print("Enpoint Information\n")

                    for fvCEp in root.iter("fvCEp"):
                        ep_loc = fvCEp.get("dn")
                        encap = fvCEp.get("encap")
                        string_modification(encap, ep_loc)
                    for endpoint_1 in sub_int_array:
                        print("{}".format(endpoint_1))

                    selection = "vlan-" + (input("Select encapsulation for EP location: "))

                    sub_int_array.clear()
                    for fvCEp in root.iter("fvCEp"):
                        encap = fvCEp.get("encap")
                        if selection == encap:
                            ep_name = fvCEp.get("name")
                            ep_mac = fvCEp.get("mac")
                            encap = fvCEp.get("encap")
                            ep_loc = fvCEp.get("dn")
                            ep_ip = fvCEp.get("ip")
                            ep_domain = fvCEp.get("lcC")
                            break
                        else:
                            pass

                for i in range(0, total_count):

                    # Iterate through INT range 0,20 and find all Leaf Nodes associated with the endpoint. Store to leaf_array for later use. An Index
                    # error will occur due to the index variable being out of range for the dictionary lookup. 20 may come first if you have more
                    # thank 20 Leaf nodes.

                    try:
                        report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsHyper"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                        leaf_array.append(report_node)
                        index = index + 1
                    except (KeyError, IndexError):
                        pass

                    try:
                        report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsToVm"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                        leaf_array.append(report_node)
                        index = index + 1
                    except (KeyError, IndexError):
                        pass

                    try:
                        report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsCEpToPathEp"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                        leaf_array.append(report_node)
                        index = index + 1
                    except (KeyError, IndexError):
                        pass


                    try:
                        report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsCEpToPathEp"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                        leaf_array.append(report_node)
                        index = index + 1
                    except (KeyError, IndexError):
                        pass

            try:

                # Here we will strip the string of all uneeded chars. Since the GET response doesnt supply use with all information we will create it ourselves
                # In our case we are break down dn="uni/tn-Production/ap-ANP-VL109/epg-EPG-VL109/ to get the Tenant, App Profile, EPG.

                location_rework = ep_loc.replace("tn-", "")
                location_rework = location_rework.replace("ap-", "")
                location_rework = location_rework.replace("epg-", "")
                location_rework = location_rework.replace("cep-", "")
                location_rework = location_rework.replace("uni", "")
                location_rework_2 = location_rework.replace("/", ",")
                location_to_array = location_rework_2.split(",")     # After dealing with th strings, we will place the data into an array,

                index = 0
                for i in location_to_array: # Now that we the array we can create dictionary. Increment variable index to make the keys unique and save i as the values
                    info_dict["item_%s" % index] = i
                    index = index + 1

                join_array = ' , '.join(leaf_array) # Convert leaf array to string. leaf_array was create on lines 207, 201, or 154. Doiong this will allow use to present
                                                    # the data as a string not array

                # Prints all data collected from the above lines
                if loop == 0:
                    ep_mac_array.append(ep_mac)
                    ep_encap_array.append(encap)
                    query_array_1.append(" Query:                {}".format(endpoint))
                    query_array_1.append(" Reverse Lookup:       {}".format(ep_ip))
                    query_array_1.append(" Tenant:               {}".format(info_dict["item_1"]))
                    query_array_1.append(" App Prof:             {}".format(info_dict["item_2"]))
                    query_array_1.append(" EPG:                  {}".format(info_dict["item_3"]))
                    query_array_1.append(" Learned From:         {}".format(ep_domain))
                    query_array_1.append(" Encap:                {}".format(encap))
                    query_array_1.append(" Reporting Leafs:      {}".format(join_array))

                elif loop == 1:
                    ep_mac_array.append(ep_mac)
                    ep_encap_array.append(encap)
                    query_array_2.append(" Query:                {}".format(endpoint))
                    query_array_2.append(" Reverse Lookup:       {}".format(ep_ip))
                    query_array_2.append(" Tenant:               {}".format(info_dict["item_1"]))
                    query_array_2.append(" App Prof:             {}".format(info_dict["item_2"]))
                    query_array_2.append(" EPG:                  {}".format(info_dict["item_3"]))
                    query_array_2.append(" Learned From:         {}".format(ep_domain))
                    query_array_2.append(" Encap:                {}".format(encap))
                    query_array_2.append(" Reporting Leafs:      {}".format(join_array))

                loop = loop + 1
            except UnboundLocalError as error:
                print("Endpoint not Found")     # throws excpetion if device is found or in this care variable hasn't been created
                enpoint_tracker(session, apic)

    if failures > 0:
        failed_endpoint = [print(endpoint) for endpoint in failed_eps]
        print("Destination EP not found, returning EP entry")
        endpoint_array.clear()
        enpoint_tracker(session, apic)
    else:
        pass

def string_modification(encap, ep_loc):

    location_rework = ep_loc.replace("tn-", "")
    location_rework = location_rework.replace("ap-", "")
    location_rework = location_rework.replace("epg-", "")
    location_rework = location_rework.replace("cep-", "")
    location_rework = location_rework.replace("uni", "")
    location_rework_2 = location_rework.replace("/", ",")
    location_to_array = location_rework_2.split(",")  # After dealing with th strings, we will place the data into an array,

    index = 0
    for i in location_to_array:  # Now that we the array we can create dictionary. Increment variable index to make the keys unique and save i as the values
        info_dict["item_%s" % index] = i
        index = index + 1

    sub_int_array.append(" Tenant:               {}".format(info_dict["item_1"]))
    sub_int_array.append(" App Prof:             {}".format(info_dict["item_2"]))
    sub_int_array.append(" EPG:                  {}".format(info_dict["item_3"]))
    sub_int_array.append(" Encap:                {}".format(encap + "\n"))

def ep_dictionary_access(selection, endpoint_data, total_count, loop):

    # Iterate through INT range 0,20 and find all Leaf Nodes associated with the endpoint. Store to leaf_array for later use. An Index
    # error will occur due to the index variable being out of range for the dictionary lookup. 20 may come first if you have more
    # thank 20 Leaf nodes.
    index = 0
    for i in range(0, total_count):
        try:
            try:
                report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsHyper"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                leaf_array.append(report_node)
                index = index + 1
            except (KeyError, IndexError):
                pass

            try:
                report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsToVm"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                leaf_array.append(report_node)
                index = index + 1
            except (KeyError, IndexError):
                pass

            try:
                report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsCEpToPathEp"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                leaf_array.append(report_node)
                index = index + 1
            except (KeyError, IndexError):
                pass

            try:
                report_node = endpoint_data["imdata"][0]["fvCEp"]["children"][0]["fvRsCEpToPathEp"]["children"][index]["fvReportingNode"]["attributes"]["id"]
                leaf_array.append(report_node)
                index = index + 1
            except (KeyError, IndexError):
                pass
            loop = loop + 1
            index = index + 1
        except UnboundLocalError as error:
            print("Endpoint not Found")  # throws excpetion if device is found or in this care variable hasn't been created
            enpoint_tracker(session, apic)

def file_operation_1(r):

    try:
        file = open(get_file, 'w')     # Open/creates a file to write XML data to
        file.write(r.text)
        file.close()

    except:
        print("File Error")

def file_operation_2(r, pretty_data):

    try:
        file = open(get_file_2, 'w')  # Open/creates a file to write JSON data to
        file.write(pretty_data)
        file.close()

    except:
        print("File Error")

if __name__ == '__main__':

    enpoint_tracker()
    ELAM.find_phys_path()
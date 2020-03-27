module_array = [ ]

try:
    import requests
except ImportError:
    module_array.append("request")
    print("request not avaialable")
try:
    import json
except ImportError:
    module_array.append("json")
    print("JSON not available")
try:
    import readline
except ImportError:
    module_array.append("readline")
    print("readline not available")

api_key = input("API Key: ")
org_id_2 = input("Org ID: ")

meraki_file = "C:\Python\MerakiFileOne.txt"
network_file = "C:\Python\MerakiFileTwo.txt"
content_type = 'application/json'

site_conversion = " "

site_dict = dict()
port_dict = dict()
subnet_dict = dict()
vpn_dict = dict()
firewall_dict = dict()
content_dict = dict()
allowed_url_array = []
blocked_url_array = []
blocked_cat_array = []
sites = [ ]

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


def tab_site_completion(text, state):

    # Used for site table completion

    with open(meraki_file) as json_file:
        network_data = json.load(json_file)

    site_array = [ ]
    for site in network_data:
        site_array.append(site["name"])

    sites = [cmd for cmd in site_array if cmd.startswith(text)]

    if state < len(sites):
        return sites[state]
    else:
        return None


def get_meraki_networks():

  # Part 1 of GET site info. Collect Site Name, site ID, Timezone and store them for later use.

  url = "https://api.meraki.com/api/v0/organizations/" + org_id_2 + "/networks/"
  headers = {'X-Cisco-Meraki-API-Key': api_key, "Content-Type": content_type, 'Accept': '*/*'}

  response = requests.request("GET", url, headers=headers)
  pretty_data = json.dumps(response.json(), indent=4)

  try:
    file = open(meraki_file, 'w')
    file.write(pretty_data)
    file.close()
  except (FileExistsError, FileNotFoundError) as error:
      print(error)

  with open(meraki_file) as json_file:
      network_data = json.load(json_file)

  dict_increment = 1
  SiteName = "SiteName_%s" % dict_increment
  SiteId = "SiteId_%s" % dict_increment
  TimeZone = "TimeZone_%s" % dict_increment

  for site in network_data:

      site_dict[site["id"]] = site["name"]
      site_dict[TimeZone] = site["timeZone"]

      dict_increment = dict_increment + 1
      SiteName = "SiteName_%s" % dict_increment
      SiteId = "SiteId_%s" % dict_increment
      TimeZone = "TimeZone_%s" % dict_increment

  main()

def get_network_subnets():

   # Part 1 of GET subnet configuration. Use the select_site module to get the site id, the global site_conversion
   # variable will be used in the URI. The fetch_subnets() will create the dictionary needed to display results.
   # Increment through the dictionary k,v using the unique key created in th fetch_subnets() module.

  select_site()

  url = "https://api.meraki.com/api/v0/networks/" + site_conversion + "/vlans"
  headers = {'X-Cisco-Meraki-API-Key': api_key, "Content-Type": content_type, 'Accept': '*/*'}
  response = requests.request("GET", url, headers=headers)

  pretty_response(response)
  fetch_subnets()

  sql_increment = 1
  vlan_id = "vlanID_%s" % sql_increment
  name = "vlanName_%s" % sql_increment
  applianceIp = "ip_%s" % sql_increment
  subnet = "subnet_%s" % sql_increment

  print("\n")
  print("Site Subnets ________________________")
  print("_____________________________________")
  print("\n")

  print("{:>1} {:>5} {:>13} {:>20} {:>20}".format
        (" ", "Vlan ID", "Vlan Name", "Gateway", "Subnet"))
  print("____________________________________________________"
        "________________________")
  print("\n")

  try:
      for i in range(0, 11):

          print("{:<3} {:<10} {:<20} {:<20} {:<20}".format(" ", str(subnet_dict[vlan_id]), subnet_dict[name], subnet_dict[applianceIp], subnet_dict[subnet] ))

          sql_increment = sql_increment + 1
          vlan_id = "vlanID_%s" % sql_increment
          name = "vlanName_%s" % sql_increment
          applianceIp = "ip_%s" % sql_increment
          subnet = "subnet_%s" % sql_increment
  except KeyError:
    pass

  main()

def get_appliance_ports():

    # Part 1 of GET port configuration. Use the select_site module to get the site id, the global site_conversion
    # variable will be used in the URI. The fetch_ports() will create the dictionary needed to display results.
    # Increment through the dictionary k,v using the unique key created in th fetch_ports() module.



    select_site()

    with open(network_file) as json_file:
        network_data = json.load(json_file)

    url = "https://api.meraki.com/api/v0/networks/" + site_conversion + "/appliancePorts"
    headers = {'X-Cisco-Meraki-API-Key': api_key, "Content-Type": content_type, 'Accept': '*/*'}
    response = requests.request("GET", url, headers=headers)

    pretty_response(response)
    fetch_ports()

    sql_increment = 1
    port_num = "number_%s" % sql_increment
    port_en = "enabled_%s" % sql_increment
    port_type = "type_%s" % sql_increment
    port_allow_vlans = "allowedVlans_%s" % sql_increment
    port_vlans = "vlans_%s" % sql_increment
    port_access_pol = "accessPol_%s" % sql_increment
    drop_untagged = "dropUntag_%s" % sql_increment

    print("\n")
    print("Appliance Ports _____________________")
    print("_____________________________________")
    print("\n")

    print("{:>1} {:>5} {:>15} {:>13} {:>20} {:>15} {:>20} {:>20}".format
          (" ", "Port", "Enabled", "Type", "Allowed Vlans", "Port Vlan", "Access Policy", "Drop Untagged"))
    print("___________________________________________________________"
          "___________________________________________________________")
    print("\n")

    try:
        for i in range(0, 11):

            print("{:3} {:<12} {:<14} {:<15} {:<18} {:<18} {:<20} {:<20}".format(" ", port_dict[port_num], port_dict[port_en],
                                                            port_dict[port_type], port_dict[port_allow_vlans], port_dict[port_vlans],
                                                            port_dict[port_access_pol], port_dict[drop_untagged]))

            sql_increment = sql_increment + 1
            port_num = "number_%s" % sql_increment
            port_en = "enabled_%s" % sql_increment
            port_type = "type_%s" % sql_increment
            port_allow_vlans = "allowedVlans_%s" % sql_increment
            port_vlans = "vlans_%s" % sql_increment
            port_access_pol = "accessPol_%s" % sql_increment
            drop_untagged = "dropUntag_%s" % sql_increment

    except KeyError as error:
        pass

    main()

def get_vpn():

    # Part 1 of GET vpn configuration. Use the select_site module to get the site id, the global site_conversion
    # variable will be used in the URI. The fetch_vpn() will create the dictionary needed to display results.
    # Increment through the dictionary k,v using the unique key created in th fetch_vpn() module.
    # Line 223 uses the global dictionary site_dict[vpn_dict[hub_id]] in combination with the hub_id variable
    # to return the hub ids human readable name.


    select_site()

    with open(network_file) as json_file:
        network_data = json.load(json_file)

    url = "https://api.meraki.com/api/v0/networks/" + site_conversion + "/siteToSiteVpn"
    headers = {'X-Cisco-Meraki-API-Key': api_key, "Content-Type": content_type, 'Accept': '*/*'}
    response = requests.request("GET", url, headers=headers)

    pretty_response(response)
    fetch_vpn()

    print("\n")
    print("VPN Information _____________________")
    print("_____________________________________")
    print("\n")

    sql_increment = 1
    hub_id = "HubId_%s" % sql_increment
    use_default = "UseDefault_%s" % sql_increment

    try:
        for i in range(0, 30):

            if vpn_dict[hub_id] == "---":
                continue
            else:
                print("{:<1} HubID: {:<20} |   Hub Name: {:<20} | Default Route: {:<20} ".format(" ", vpn_dict[hub_id],
                                                                                                      site_dict[vpn_dict[hub_id]],
                                                                                                      vpn_dict[use_default]))

            sql_increment = sql_increment + 1
            hub_id = "HubId_%s" % sql_increment
            use_default = "UseDefault_%s" % sql_increment

    except KeyError:
        pass

    print("\n")
    sql_increment = 1
    vpn_subnet = "VPNSubnet_%s" % sql_increment
    use_vpn = "UseVPN_%s" % sql_increment

    try:
        for i in range(0, 30):

                if vpn_dict[vpn_subnet] == "---":
                    continue
                else:
                    print("{:<1} Subnet: {:<20}|   VPN Advertised: {:<20} ".format(" ", vpn_dict[vpn_subnet], vpn_dict[use_vpn]))

                sql_increment = sql_increment + 1
                vpn_subnet = "VPNSubnet_%s" % sql_increment
                use_vpn = "UseVPN_%s" % sql_increment

    except KeyError:
        pass

    main()

def get_firewall():

    # Part 1 of GET Firewall rules Use the select_site module to get the site id, the global site_conversion
    # variable will be used in the URI. The fetch_firewall_rules() will create the dictionary needed to display results.
    # Increment through the dictionary k,v using the unique key created in th fetch_firewall_rules() modules.

    select_site()

    with open(network_file) as json_file:
        network_data = json.load(json_file)

    sql_increment = 1
    fw_comment = "comment_%s" % sql_increment
    fw_policy = "policy_%s" % sql_increment
    fw_protocol = "protocol_%s" % sql_increment
    fw_src_port = "srcPort_%s" % sql_increment
    fw_src_subnet = "srcSubnet_%s" % sql_increment
    fw_dst_port = "dstPort_%s" % sql_increment
    fw_dst_subnet = "dstSubnet_%s" % sql_increment
    fw_syslog = "syslog_%s" % sql_increment

    url = "https://api.meraki.com/api/v0/organizations/" + org_id_2 + "/networks/" + site_conversion + "/l3FirewallRules"
    headers = {'X-Cisco-Meraki-API-Key': api_key, "Content-Type": content_type, 'Accept': '*/*'}
    response = requests.request("GET", url, headers=headers)

    pretty_response(response)
    fetch_firewall_rules()

    print("\n")
    print("Firewall Rules ______________________")
    print("_____________________________________")
    print("\n")

    try:
        for i in range(0, 50):

            print("{:<1} Comment:         {:<20}".format(" ", firewall_dict[fw_comment]))
            print("{:>1} Policy:          {:<16}".format(" ", firewall_dict[fw_policy]))
            print("{:>1} Protocol:        {:<12}".format(" ", firewall_dict[fw_protocol]))
            print("{:>1} Src Port:        {:<12}".format(" ", firewall_dict[fw_src_port]))
            print("{:>1} Src Subnet:      {:<10}".format(" ", firewall_dict[fw_src_subnet]))
            print("{:>1} Dst Port:        {:<12}".format(" ", firewall_dict[fw_dst_port]))
            print("{:>1} Dst Subnet:      {:<10}".format(" ", firewall_dict[fw_dst_subnet]))
            print("{:>1} Syslog:          {:<13}".format(" ", firewall_dict[fw_syslog]))
            print("\n")

            sql_increment = sql_increment + 1
            fw_comment = "comment_%s" % sql_increment
            fw_policy = "policy_%s" % sql_increment
            fw_protocol = "protocol_%s" % sql_increment
            fw_src_port = "srcPort_%s" % sql_increment
            fw_src_subnet = "srcSubnet_%s" % sql_increment
            fw_dst_port = "dstPort_%s" % sql_increment
            fw_dst_subnet = "dstSubnet_%s" % sql_increment
            fw_syslog = "syslog_%s" % sql_increment

    except(KeyError) as error:
        pass

    main()

def get_content_filtering():

    # Part 1 of thr fetch_content_filter modules. Use the select_site module to get the site id, the global site_conversion
    # variable will be used in the URI. The fetch_content_filter will create the dictionary need to display results.

    select_site()

    url = "https://api.meraki.com/api/v0/organizations/" + org_id_2 + "/networks/" + site_conversion + "/contentFiltering"
    headers = {'X-Cisco-Meraki-API-Key': api_key, "Content-Type": content_type, 'Accept': '*/*'}
    response = requests.request("GET", url, headers=headers)

    pretty_response(response)
    fetch_content_filtering()

    print("Allowed URLS:")
    print("\n")
    print(*content_dict["AllowedPattern"], sep="\n")
    print("\n")

    print("Blocked URLS:")
    print("\n")
    print(*content_dict["BlockedPattern"], sep="\n")
    print("\n")

    print("Blocked Categories:")
    print("\n")
    print(*content_dict["BlockedCat"], sep="\n")
    print("\n")

    main()


def select_site():

    # Collect all networks from file "network_dat" and print it via for loop. Using readline, use TAB to autocomplete site name.
    # When a site is entered, line 354 finds the k and creates a global variable for URL use. The global variable is the SiteID.
    # starting witn N_. If readline doesnt work than it should pass the expception

    try:

        with open(meraki_file) as json_file:
            network_data = json.load(json_file)

        for site in network_data:
            print("Site: " + site["name"])
        print("\n")

        # Use readline for TAB functionality

        readline.parse_and_bind("tab: complete")
        readline.set_completer(tab_site_completion)
        print("\n")

        user_input = input("Enter Site: ")

        # Convert site ["name"] to site["id] for URL request

        for k, v in site_dict.items():
            if user_input == v:
                global site_conversion
                site_conversion = k

    except (json.JSONDecodeError, UnboundLocalError) as error:
        print("\n")
        print("JSON data didnt convert, please  check if the content was fetched correctly | Check File %s" % network_file + " for contents")
        main()
    except:
        pass

def pretty_response(response):

    try:
        pretty_data = json.dumps(response.json(), indent=4)
    except json.JSONDecodeError as error:
        print("\n")
        print("JSON Date didnt convert, please  check if the content was fetched correctly | GET Response: %s" % response)
        main()

    file = open(network_file, 'w')
    file.write(pretty_data)
    file.close()

def fetch_subnets():

    # Collect all subnets and create a key/value pair in subnetdict. Increment key integer to create unique keys.

    with open(network_file) as json_file:
        site_data = json.load(json_file)

    sql_increment = 1
    vlan_id = "vlanID_%s" % sql_increment
    name = "vlanName_%s" % sql_increment
    applianceIp = "ip_%s" % sql_increment
    subnet = "subnet_%s" % sql_increment

    for data in site_data:

        try:
            network_id = data['id']
            subnet_dict[vlan_id] = network_id
        except (KeyError, TypeError):
            pass

            ##########################

        try:
            network_name = data['name']
            subnet_dict[name] = network_name
        except (KeyError, TypeError):
            pass

            ##########################

        try:
            gateway = data['applianceIp']
            subnet_dict[applianceIp] = gateway
        except (KeyError, TypeError):
            pass

            ##########################

        try:
            subnet_id = data['subnet']
            subnet_dict[subnet] = subnet_id
        except (KeyError, TypeError):
            pass

        sql_increment = sql_increment + 1
        vlan_id = "vlanID_%s" % sql_increment
        name = "vlanName_%s" % sql_increment
        applianceIp = "ip_%s" % sql_increment
        subnet = "subnet_%s" % sql_increment

def fetch_ports():

    # Collect all site ports and create a key/value pair in port_dict. Increment key integer to create unique keys. If a exception is raised, insert a null chars.
    # Doing this makes it easier to access without exceptions and can give a complete table instead of blank rows/columns.

    sql_increment = 1
    index = 0
    port_num = "number_%s" % sql_increment
    port_en = "enabled_%s" % sql_increment
    port_type = "type_%s" % sql_increment
    port_allow_vlans = "allowedVlans_%s" % sql_increment
    port_vlans = "vlans_%s" % sql_increment
    port_access_pol = "accessPol_%s" % sql_increment
    drop_untagged = "dropUntag_%s" % sql_increment

    with open(network_file) as json_file:
        content_data = json.load(json_file)

        try:
            for i in range(0, 11):

                try:
                    port_id = content_data[index]["number"]
                    port_dict[port_num] = port_id
                except (TypeError, KeyError):
                    port_dict[port_num] = "---"
                    pass

                try:
                    port_active = str(content_data[index]["enabled"])
                    port_dict[port_en] = port_active
                except (TypeError, KeyError):
                    port_dict[port_en] = "---"
                    pass

                try:
                    access_trunk = content_data[index]["type"]
                    port_dict[port_type] = access_trunk
                except (TypeError, KeyError):
                    port_dict[port_type] = "---"
                    pass

                try:
                    vlan_allowed = content_data[index]["allowedVlans"]
                    port_dict[port_allow_vlans] = vlan_allowed
                except (KeyError, TypeError):
                    port_dict[port_allow_vlans] = '---'
                    pass

                try:
                    vlan_access = content_data[index]["vlan"]
                    port_dict[port_vlans] = vlan_access
                except (KeyError, TypeError):
                    port_dict[port_vlans] = "---"
                    pass

                try:
                    access_policy = content_data[index]["accessPolicy"]
                    port_dict[port_access_pol] = access_policy
                except (KeyError, TypeError):
                    port_dict[port_access_pol] = "---"
                    pass

                try:
                    drop_id = str(content_data[index]["dropUntaggedTraffic"])
                    port_dict[drop_untagged] = drop_id
                except (KeyError, TypeError):
                    port_dict[drop_untagged] = "---"
                    pass

                sql_increment = sql_increment + 1
                index = index + 1
                port_num = "number_%s" % sql_increment
                port_en = "enabled_%s" % sql_increment
                port_tag = "tagging_%s" % sql_increment
                port_type = "type_%s" % sql_increment
                port_allow_vlans = "allowedVlans_%s" % sql_increment
                port_vlans = "vlans_%s" % sql_increment
                port_access_pol = "accessPol_%s" % sql_increment
                drop_untagged = "dropUntag_%s" % sql_increment

        except IndexError:
            pass

def fetch_vpn():

    # Collect all site vpn settings and create a key/value pair in vpn_dict. Increment key integer to create unique keys. If a exception is raised, insert a null chars.
    # Doing this makes it easier to access without exceptions and can give a complete table instead of blank rows/columns.

    sql_increment = 1
    index = 0
    hub_id = "HubId_%s" % sql_increment
    use_default = "UseDefault_%s" % sql_increment

    with open(network_file) as json_file:
        site_data = json.load(json_file)

    for i in range(0, 30):

        try:
            hub = site_data["hubs"][index]["hubId"]
            vpn_dict[hub_id] = hub
        except (TypeError, KeyError, IndexError):
            vpn_dict[hub_id] = "---"
            pass

        try:
            default_hub = str(site_data["hubs"][index]["useDefaultRoute"])
            vpn_dict[use_default] = default_hub
        except (TypeError, KeyError, IndexError):
            vpn_dict[use_default] = "---"
            pass

        sql_increment = sql_increment + 1
        index = index + 1
        hub_id = "HubId_%s" % sql_increment
        use_default = "UseDefault_%s" % sql_increment


    sql_increment = 1
    index = 0
    vpn_subnet = "VPNSubnet_%s" % sql_increment
    use_vpn = "UseVPN_%s" % sql_increment

    for i in range(0,30):

        try:
            subnet = site_data["subnets"][index]["localSubnet"]
            vpn_dict[vpn_subnet] = subnet
        except (TypeError, KeyError, IndexError):
            vpn_dict[vpn_subnet] = "---"
            pass

        try:
            in_vpn = str(site_data["subnets"][index]["useVpn"])
            vpn_dict[use_vpn] = in_vpn
        except (TypeError, KeyError, IndexError):
            vpn_dict[use_vpn] = "---"
            pass

        sql_increment = sql_increment + 1
        index = index + 1
        vpn_subnet = "VPNSubnet_%s" % sql_increment
        use_vpn = "UseVPN_%s" % sql_increment

def fetch_firewall_rules():

    # Collect all site firewall rules and create a key/value pair in firewall_dict. Increment key integer to create unique keys. If a exception is raised, insert a null chars.
    # Doing this makes it easier to access without exceptions and can give a complete table instead of blank rows/columns.


    with open(network_file) as json_file:
        firewall_data = json.load(json_file)

    sql_increment = 1
    fw_comment = "comment_%s" % sql_increment
    fw_policy = "policy_%s" % sql_increment
    fw_protocol = "protocol_%s" % sql_increment
    fw_src_port = "srcPort_%s" % sql_increment
    fw_src_subnet = "srcSubnet_%s" % sql_increment
    fw_dst_port = "dstPort_%s" % sql_increment
    fw_dst_subnet = "dstSubnet_%s" % sql_increment
    fw_syslog = "syslog_%s" % sql_increment

    for fw_rules in firewall_data:

        try:
            comment = fw_rules["comment"]
            firewall_dict[fw_comment] = comment
        except (KeyError, TypeError):
            firewall_dict[fw_comment] = "---"

        ##########################

        try:
            policy = fw_rules["policy"]
            firewall_dict[fw_policy] = policy
        except (KeyError, TypeError):
            firewall_dict[fw_policy] = "---"
            pass

        ##########################

        try:
            protocol = fw_rules["protocol"]
            firewall_dict[fw_protocol] = protocol
        except (KeyError, TypeError):
            firewall_dict[fw_protocol] = "---"
            pass

        ##########################

        try:
            src_port = fw_rules["srcPort"]
            firewall_dict[fw_src_port] = src_port
        except (KeyError, TypeError):
            firewall_dict[fw_src_port] = "---"
            pass

        ##########################

        try:
            src_Cidr = fw_rules["srcCidr"]
            firewall_dict[fw_src_subnet] = src_Cidr
        except (KeyError, TypeError):
            firewall_dict[fw_src_subnet] = "---"
            pass

        ##########################

        try:
            destPort = fw_rules["destPort"]
            firewall_dict[fw_dst_port] = destPort
        except (KeyError, TypeError):
            firewall_dict[fw_dst_port] = "---"
            pass

        ##########################

        try:
            dstCidr = fw_rules["destCidr"]
            firewall_dict[fw_dst_subnet] = dstCidr
        except (KeyError, TypeError):
            firewall_dict[fw_dst_subnet] = "---"
            pass

        ##########################

        try:
            sys_log = str(fw_rules["syslogEnabled"])
            firewall_dict[fw_syslog] = sys_log
        except (KeyError, TypeError):
            firewall_dict[fw_syslog] = "---"

        sql_increment = sql_increment + 1
        fw_comment = "comment_%s" % sql_increment
        fw_policy = "policy_%s" % sql_increment
        fw_protocol = "protocol_%s" % sql_increment
        fw_src_port = "srcPort_%s" % sql_increment
        fw_src_subnet = "srcSubnet_%s" % sql_increment
        fw_dst_port = "dstPort_%s" % sql_increment
        fw_dst_subnet = "dstSubnet_%s" % sql_increment
        fw_syslog = "syslog_%s" % sql_increment

def fetch_content_filtering():

    # Collect all site content filtering, store each URL in an array and create a key/value pair in content_dict with nested array. Increment key
    # integer to create unique keys. If a exception is raised, insert a null chars.Doing this makes it easier to access without
    # exceptions and can give a complete table instead of blank rows/columns. 200 URLS can be stored, change range to store more

    with open(network_file) as json_file:
        content_data = json.load(json_file)

    allowed_patterns = content_data["allowedUrlPatterns"]

    try:
        for url in range(0, 200):
            if "*" == allowed_patterns:
                allowed_url_array.append("*")
                pass
            else:
                allowed_url_array.append(allowed_patterns[url])
    except IndexError:
        pass

    blocked_patterns = content_data["blockedUrlPatterns"]

    try:
        for url in range(0, 200):
            if "*" == blocked_patterns:
                blocked_url_array.append("*")
                pass
            else:
                blocked_url_array.append(blocked_patterns[url])
    except IndexError:
        pass

    blocked_categories = content_data["blockedUrlPatterns"]

    try:
        for url in range(0, 200):
            if "*" == blocked_categories:
                blocked_cat_array.append("*")
                pass
            else:
                blocked_cat_array.append(blocked_categories[url])
    except IndexError:
        pass

    content_dict["AllowedPattern"] = allowed_url_array
    content_dict["BlockedPattern"] = blocked_url_array
    content_dict["BlockedCat"] = blocked_cat_array

def main():

    print("\n")
    while True:

        print("Interface Viewer")
        print("\n")
        print("1. View Content Filtering")
        print("2. View Network Port ")
        print("3. View Firewall Rules")
        print("4. View Subnets ")
        print("5. View VPN Settings ")
        print("6. Find Site ID ")
        print("7. Fetch the Cloud ")


        print("\n")
        selection = input("Selection: ")
        print("\n")

        if selection == "1":
            get_content_filtering()
            break

        elif selection == "2":
            get_appliance_ports()
            break

        elif selection == "3":
            get_firewall()
            break

        elif selection == "4":
            get_network_subnets()
            break

        elif selection == "5":

            get_vpn()
            break

        elif selection == "6":

            select_site()

            print("\n")
            print("Site Name to Site ID ________________")
            print("_____________________________________")
            print("\n")

            print("Site ID: %s" % site_conversion)
            main()
            break

        elif selection == "7":

            get_meraki_networks()
            main()
            break

        else:
            print("\n")
            print("Invalid Selection")
            print("\n")

if __name__ == '__main__':

    module_check()
    get_meraki_networks()
    main()

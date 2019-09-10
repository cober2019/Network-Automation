try:
    import sys
except ImportError:
    print("Module sysT not available.")
try:
    import xmltodict
except ImportError:
    print("Module xmltodict not available.")
try:
    import xml.dom.minidom as dom
except ImportError:
    print("Module XML.DOM.MINDOM not available.")
    pass
try:
    import xml.etree.ElementTree as xml
except ImportError:
    print("Module XM.ETREE.ELEMENTTREE not available.")
    pass
try:
    import requests
except ImportError:
    print("Module REQUESTS not available.")
    pass
try:
    import lxml.etree as ET
except ImportError:
    print("Module LXML.ETREE as ET not available.")
    pass
try:
    import ipaddress
except ImportError:
    print("Module IPADDRESS is  not available.")
    pass
try:
    import paramiko
except ImportError:
    print("Module IPADDRESS is  not available.")
    pass
try:
    import readline
except ImportError:
    print("Module READLINE not available.")
    pass
try:
    import urllib3
except ImportError:
    print("Module URLLIB3 not available.")
    pass
try:
    import warnings
except ImportError:
    print("Module WARNING not available.")
    pass
try:
    import pathlib
except ImportError:
    print("Module PATHLIB not available.")
    pass
try:
    import time
except ImportError:
    print("Module TIME not available.")
    pass




##################################################################



def disable_paging(remote_conn):

    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    output = remote_conn.recv(1000)
    return output


def paramiko_login(command):

    try:
        ip = input("Please enter a IP address: ")
        username = 'USERNAME'
        password = 'PASSWORD'

        remote_conn_pre = paramiko.SSHClient()

        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
        print("SSH connection established to %s" % ip)

        remote_conn = remote_conn_pre.invoke_shell()
        print("Interactive SSH session established")

        output = remote_conn.recv(1000)
        print(output)

        disable_paging(remote_conn)

        remote_conn.send(command)
        time.sleep(2)

        output = remote_conn.recv(5000)
        output_str = output.decode('utf-8')
        print(output_str)

        while True:
            try:

                repeat_selection = input("Do you want to repeat command? ")

                if repeat_selection == "yes":
                    remote_conn.send(command)
                    time.sleep(2)

                    output = remote_conn.recv(5000)
                    output_str = output.decode('utf-8')
                    print(output_str)
                    continue

                elif repeat_selection == "no":
                    main()
                    break
                else:
                    print("\n")
                    print("Invalid Selection")
                    print("\n")
                    continue
            except paramiko.ssh_exception:
                print("\n")
                print("Connection Unsuccessful")
                print("\n")
                main()
    except paramiko.ssh_exception:
        print("\n")
        print("Connection Unsuccessful")
        print("\n")
        device_admin()

#################################################################

def select_configuration_file():

    # CONFIGURATION FILES CAN BE VIEWED FROM THIS DIRECTORY AND SENT. THIS CAN BE USED TO SEND FILES THAT INTIALLY FAILED

    while True:

        print("\n")
        print(" 1: File Select")
        print(" 2: Main Menu")

        print("\n")
        question_1 = input("Please select an option: ")
        print("\n")

        if question_1 == "1":

            dir_files = []
            for p in pathlib.Path("C:\Python\ACI").iterdir():
                if p.is_file():
                    print(p)
                    dir_files.append(p)

            print("\n")
            config_file = input("Please enter a filename: ")
            file = "C:\Python\ACI" + "\\" + config_file
            send_configuration(file)
            break
        elif question_1 == "2":
            main()
            break
        else:
            print("\n")
            print("Invalid Selection")
            print("\n")

################################
#Gets configured Tenant on currentAPIC
################################
def view_tenant():

    headers = {'content-type': 'text/xml'}
    uri = "https://%s/api/class/fvTenant.xml" % apic

    try:
        r = session.get(uri,verify=False, headers=headers)
        print("\n")

        file= open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Tenants on APIC %s: " % apic)
        print("\n")
        for fvTenant in root.iter("fvTenant"):
            tenant = fvTenant.get("name")
            global  tenants
            tenants = [tenant]
            print(tenant)

    except UnboundLocalError:
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()

def tenant_vrf(tenant_input):
    #########################
    # Gets VRF from selected Tenant
    #########################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/node/mo/uni/tn-" + tenant_input + ".xml?query-target=children&target-subtree-class=fvCtx"

    try:
        r = session.get(uri, verify=False, headers=headers)
        print("\n")

        file = open(get_vrf_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("VRFs in Tenant %s " % apic)
        print("\n")
        for fvCtx in root.iter("fvCtx"):
            vrf = fvCtx.get("name")
            print(vrf)

    ##########################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ################

    except UnboundLocalError:
        print("403 Forbidden - Please log into APIC to vew/push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("403 Forbidden - Please log into APIC to vew/push configurations")
        print("\n")
        apic_login()

def infr():

    headers = {'content-type': 'text/xml'}
    uri = "https://%s/api/node/mo/topology/pod-1.xml?query-target=children" % apic

    try:
        r = session.get(uri,verify=False, headers=headers)
        print("\n")

        file= open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Fabric Nodes %s: " % apic)
        print("\n")
        for fabricNode in root.iter("fabricNode"):
            fabric_node = fabricNode.get("name")
            model_node = fabricNode.get("model")
            serial_node = fabricNode.get("serial")
            device_info = [fabric_node, model_node,serial_node ]

            print ("{0:12} {1:<16} {2:>16}".format(fabric_node, model_node, serial_node))

    except UnboundLocalError:
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        print("Unknown Error. Relogging into APIC")
        apic_login()

def view_bd(tenant_input):

    #########################
    # Gets Bridge Domains  from selected Tenant
    #########################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/node/mo/uni/tn-" + tenant_input + ".xml?query-target=children&target-subtree-class=fvBD"

    try:
        r = session.get(uri,verify=False, headers=headers)
        print("\n")

        file = open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Bridge Domains in %s: " % tenant_input)
        print("\n")
        for fvBD in root.iter("fvBD"):
            bridge_domain = fvBD.get("name")
            UnicastRoute = fvBD.get("unicastRoute")
            pc_tag = fvBD.get("pcTag")

            print ("{0:35} {1:<15} {2:<15}".format(bridge_domain, UnicastRoute, "pcTag: %s" % pc_tag))

    ##########################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ################

    except UnboundLocalError:
        print("\n")
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("\n")
        print("Unknown Error. Relogging into APIC")
        print("\n")
        apic_login()

def view_app_profiles(tenant_input):

    #######################################
    # Gets Application Profiles from selected Tenant
    #######################################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/node/mo/uni/tn-" + tenant_input + ".xml?query-target=children&target-subtree-class=fvAp"

    try:
        r = session.get(uri, verify=False, headers=headers)
        print("\n")

        file = open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Tenant %s Application Profiles: " % tenant_input)
        print("\n")
        for fvAp in root.iter("fvAp"):
            app_p = fvAp.get("name")
            print(app_p)

    ############################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ##################

    except UnboundLocalError:
        print("\n")
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("\n")
        print("Unknown Error. Relogging into APIC")
        apic_login()

###################################################################

def view_vlan_pools():

    ####################################
    # Gets EndPoint Groups from selected Tenant
    ####################################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/class/fvnsVlanInstP.xml?query-target=subtree"

    try:

        r= session.get(uri, verify=False, headers=headers)
        print("\n")

        file = open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Configured VLAN pools: ")
        print("\n")
        for fvnsVlanInstP in root.iter("fvnsVlanInstP"):
            vlan_pool = fvnsVlanInstP.get("name")
            for fvnsEncapBlk in root.iter("fvnsEncapBlk"):
                vlan_start = fvnsEncapBlk.get("from")
                vlan_end = fvnsEncapBlk.get("to")
                alloc_mode= fvnsEncapBlk.get("allocMode")

                print ("{0:25} {1:<15} {2:<15} {3:<15}".format(vlan_pool, vlan_start, vlan_end, alloc_mode))

    ############################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ##################

    except UnboundLocalError:
        print("\n")
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("\n")
        print("Unknown Error. Relogging into APIC")
        print("\n")
        apic_login()

##########################################################################

def view_epgs(tenant_input, app_input):

    ####################################
    # Gets EndPoint Groups from selected Tenant
    ####################################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/node/mo/uni/tn-" + tenant_input + "/ap-" + app_input + ".xml?query-target=children&target-subtree-class=fvAEPg"

    try:

        r = session.get(uri, verify=False, headers=headers)
        print("\n")

        file = open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Tenant %s Endpoint Groups: " % tenant_input)
        print("\n")
        for fvAEPg in root.iter("fvAEPg"):
            EPG = fvAEPg.get("name")
            pcTag = fvAEPg.get("pcTag")

            print ("{0:35} {1:>15}".format(EPG, "pcTag: %s" % pcTag))

    ############################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ##################

    except UnboundLocalError:
        print("\n")
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("\n")
        print("Unknown Error. Relogging into APIC")
        apic_login()

#####################################################################

def view_int_profiles():

    ####################################
    # Gets EndPoint Groups from selected Tenant
    ####################################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/node/mo/uni/infra.xml?query-target=subtree"

    try:

        r = session.get(uri, verify=False, headers=headers)
        print("\n")

        file = open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Interface Profiles" )
        print("\n")
        for infraAccBndlGrp in root.iter("infraAccBndlGrp"):
            int_path = infraAccBndlGrp.get("name")
            print(int_path)

    ############################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ##################

    except UnboundLocalError:
        print("\n")
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("\n")
        print("Unknown Error. Relogging into APIC")
        apic_login()

###################################################################

def apic_login():

    #########################################################
    # APIC login credential code - Please fill in USERNAME and PASSWORD
    #########################################################

    raw_data = """<!-- AAA LOGIN -->
        <aaaUser name="USERNAME" pwd="PASSWORD"/>
        """
    global apic

    apic = input("Please enter an APIC IP: ")
    headers = {'content-type': 'text/xml'}
    uri = "https://%s/api/mo/aaaLogin.xml" % apic

    global session

    while True:
        try:
            session = requests.Session()
            r = session.post(uri, data=raw_data, verify=False, headers=headers)
            print("\n")
            print("Status Code:", r.status_code)
            main()
            break
        except requests.exceptions.InvalidURL:
            print("\n")
            print("Invalid APIC IP")
            apic_login()


####################################################################
def view_contracts(tenant_input):

    ####################################
    # Gets EndPoint Groups from selected Tenant
    ####################################

    headers = {'content-type': 'text/xml'}
    uri = "https://" + apic + "/api/class/vzBrCP.xml"

    try:

        r = session.get(uri, verify=False, headers=headers)
        print("\n")

        file = open(get_file, 'w')
        file.write(r.text)
        file.close()

        tree = ET.parse('C:\Python\ACI\Get_ACI.xml')
        root = tree.getroot()

        print("Tenant %s Contracts: " % tenant_input)
        print("\n")
        for vzBrCP in root.iter("vzBrCP"):
            contract = vzBrCP.get("name")
            scope = vzBrCP.get("scope")
            dn = vzBrCP.get("dn")

            print("{0:35} {1:<20} {2:<20}".format(contract, "Scope: %s" % scope, "Tenant: %s" % dn))

    ############################################################
    # The follwing two exceptions will be thrown in you dont log in to the APIC
    ######################################### ##################

    except UnboundLocalError:
        print("\n")
        print("403 Forbidden - Please log into APIC to vew or push configurations")
        print("\n")
        apic_login()
    except NameError:
        print("\n")
        print("Unknown Error. Relogging into APIC")
        apic_login()

def send_configuration(file):

    config_file = open(file=file).read()
    print("\n")
    print(dom.parseString(str(config_file)).toprettyxml())

    url = "https://%s/api/mo/uni.xml" % apic
    headers = {'content-type': 'application/xml'}

    try:
        r = session.post(url=url, data=config_file, verify=False, headers=headers)
        warnings.filterwarnings("ignore")
        print("Status Code:", r.status_code)
    except:
        print("Please log into APIC")
        print("\n")
        apic_login()

        try:
            r = session.post(url=url, data=config_file, verify=False, headers=headers)
            print("Status Code:", r.status_code) # 200 mean successfule
        except:
            print("Error:", r.reason)
            print("Please log into APIC")
            print("\n")
            main()


######################################################################
def yes_no_answer(text, state):

    answer_yes_no = ["yes", "no"]
    answer_yes_no_commands = [cmd for cmd in answer_yes_no if cmd.startswith(text)]

    if state < len(answer_yes_no_commands):
        return answer_yes_no_commands[state]
    else:
        return None

#######################################################################


def ip_scope(text, state):

    bd_ip_scope = ["public", "private", "shared"]
    bd_ip_scope_commands = [cmd for cmd in bd_ip_scope if cmd.startswith(text)]

    if state < len(bd_ip_scope_commands):
        return bd_ip_scope_commands[state]
    else:
        return None

########################################################################

def contract_filter_entry(text, state):

    filter_entry = ["unspecified"]
    filter_entry_commands = [cmd for cmd in filter_entry if cmd.startswith(text)]

    if state < len(filter_entry_commands):
        return filter_entry_commands[state]
    else:
        return None

def flood_scope(text, state):

    unk_flood_scope = ["proxy", "flood"]
    unk_flood_scope_commands = [cmd for cmd in unk_flood_scope if cmd.startswith(text)]

    if state < len(unk_flood_scope_commands):
        return unk_flood_scope_commands[state]
    else:
        return None

def contract_scopes(text, state):

    contract_scope = ["tenant", "vrf", "global", "application profile"]
    contract_scope_commands = [cmd for cmd in contract_scope if cmd.startswith(text)]

    if state < len(contract_scope_commands):
        return contract_scope_commands[state]
    else:
        return None

def tenant_array(text, state):

    tenant_list = view_tenant()
    tenant_list_selection = [cmd for cmd in tenant_list if cmd.startswith(text)]

    if state < len(tenant_list_selection):
        return tenant_list_selection[state]
    else:
        return None


###########################################################################3

########################################################################

def main():

    config_selection = ' '
    while config_selection != 'q':

        print("\n")
        print("Datacenter Network Programabiltiy and Automation Program")
        print("\n")

        print("\n")
        print(" 1: Tenant")
        print(" 2: Application Profile")
        print(" 3: Bridge Domain")
        print(" 4: Contracts")
        print(" 5: View Config")
        print(" 6: Send Config")
        print(" 7: APIC Login")
        print(" 8: Troubleshooting")
        print(" 9: Infrastructure")
        print("[q] (quit)")

        print("\n")

        config_selection = input("Please select an option:  ")

        if config_selection == "1":
            tenant_configuration()
        elif config_selection == "2":
            app_profile_configuration()
        elif config_selection == "3":
            bridge_domain_configuration()
        elif config_selection == "4":
            contract_configuration()
        elif config_selection == "5":
            view_config()
        elif config_selection == "6":
            select_configuration_file()
        elif config_selection == "7":
            apic_login()
        elif config_selection == "8":
            troubleshooting()
        elif config_selection == "9":
            infr()
        elif config_selection == "q":
            print("Exiting Program")
            print("\n")
        else:
            print("\n")
            print("Invalid Selection")

            print("\n")

    print("Thank you for using the Datacenter Network Programabiltiy and Automation Program")
    quit()

###########################################################################
def troubleshooting():

    config_selection = ' '
    while config_selection != '2':

        print("\n")
        print("Troubleshooting: ")
        print("\n")

        print("\n")
        print(" 1: Zoning (Contracts:)")
        print(" 2: Main")

        print("\n")

        config_selection = input("Please select an option:  ")

        if config_selection == "1":
            view_tenant()
            print("\n")
            tenant_input = input("Please select a Tenant: ")
            view_app_profiles(tenant_input)
            print("\n")
            app_input = input("Please select a App profile: ")
            view_epgs(tenant_input, app_input)
            print("\n")
            pcTag = input("Please select a pcTag: ")
            paramiko_login("show zoning-rule src-epg %s\n" % pcTag)
            troubleshooting()

        elif config_selection == "2":
            main()

        else:

            print("\n")
            print("Invalid Selection")
            print("\n")

def view_config():

    print("View Configurations")

    print("\n")
    print(" 1: Tenant")
    print(" 2: Application Profile/EPG")
    print(" 3: Bridge Domain")
    print(" 4: VLAN Pools")
    print(" 5: Interface Profiles")
    print(" 6: Contracts")
    print(" 7: APIC Login")

    config_selection = input("Please select an option: ")

    if config_selection == "1":
        view_tenant()
    elif config_selection == "2":
        view_tenant()
        print("\n")
        tenant_input = input("Please select a Tenant: ")
        view_app_profiles(tenant_input)
        print("\n")
        app_input = input("Please create a Application Profile: ")
        view_epgs(tenant_input, app_input)
    elif config_selection == "3":
        view_tenant()
        print("\n")
        tenant_input = input("Please select a Tenant: ")
        view_bd(tenant_input)
    elif config_selection == "4":
        view_vlan_pools()
    elif config_selection == "5":
        view_int_profiles()
    elif config_selection == "6":
        view_tenant()
        tenant_input = input("Please select a Tenant: ")
        view_contracts(tenant_input)


def tenant_configuration():

    print("\n")
    print("TAB option can be use on some options, this will avoid configuration failures")

    view_tenant(get_tenant_file)

    root = xml.Element("fvTenant")

    print("\n")
    tenant_input = input("Please create a Tenant: ")
    root.set("name", tenant_input)

    vrf = xml.Element("fvCtx")
    vrf_input = input("Please create a vrf: ")
    vrf.set("name", vrf_input)
    root.append(vrf)

    tree = xml.ElementTree(root)
    with open(tenant_file, "wb") as fh:
        tree.write(fh)

    send_configuration(tenant_file)

########################################## Displays current app profiles. Reads APIC via URI, saves ouput to file and then iterates file to find Application Profiles

def app_profile_configuration():

    print("\n")
    print("TAB option can be use on some options, this will avoid configuration failures")
    print("\n")

    view_tenant()
    print("\n")

    tenant_input = input("Please enter a Tenant: ")

    view_app_profiles(tenant_input)
    print("\n")

    root = xml.Element("fvTenant")
    root.set("name", tenant_input)

############################################## Application Profile Configuration - This input is also used to display available App Profile and EPGS

    print("\n")
    app = xml.Element("fvAp")
    app_input = input("Please enter a Application Profile: ")
    root.append(app)
    app.set("name", app_input)

    app_descr = input("Please enter a description: ")
    app.set("descr", app_descr)

############################################## Displays current EPGs. Reads APIC via URI, saves ouput to file and then iterates file to find EPGss

    print("Endpoint Group Configuration")

    view_epgs(tenant_input, app_input)

    print("\n")
    epg = xml.Element("fvAEPg")
    app.append(epg)

    epg_input = input("Please enter a Endpoint Group(EPG): ")
    epg.set("name", epg_input)

    epg_descr = input("Please enter a description: ")
    epg.set("descr", epg_descr)

    ########################################## Assign Bridge Domain to EPG

    view_bd(tenant_input)

    epg_bd = xml.Element("fvRsBd")
    epg.append(epg_bd)
    epg_bd_input = input("Please assign a Bridge Domain: ")
    epg_bd.set("tnFvBDName", epg_bd_input)

    ########################################## Add contracts to EPG

    view_contracts(tenant_input
                   )
    epg_con_prov = xml.Element("fvRsCons")
    epg.append(epg_con_prov)

    con_contract = input("Please enter a consumed contract: ")
    epg_con_prov.set("tnVzBrCPName", con_contract)

    epg_con_prov = xml.Element("fvRsProv ")
    epg.append(epg_con_prov)

    prov_contract = input("Please enter a provided contract: ")
    epg_con_prov.set("tnVzBrCPName", prov_contract)

    ########################################## Attach physical and VMM domains, tags static paths with vlans

    print("Static PathConfiguration")

    print("View Configurations")

    print("\n")
    print(" 1: VMM Domain")
    print(" 2: Physical Domain")
    print(" 2: Other Static Path")
    print(" 3: Main")

    config_selection = input("Please select an option: ")

    if config_selection == "1":

        domain_attach = xml.Element("fvRsDomAtt")
        epg.append(domain_attach)

        vmm_dom = input("Please attach VMM Domian: ")
        domain_attach.set("tDn", "uni/vmmp-VMware/dom-%s" % vmm_dom )

        vla_encap = input("Please assign vlan encapsulation: ")
        domain_attach.set("encap", "vlan-" + vla_encap)

        tree = xml.ElementTree(root)
        with open(app_file, "wb") as fh:
            tree.write(fh)

        send_configuration(epg_file)

    if config_selection == "2":

        domain_attach = xml.Element("fvRsDomAtt")
        epg.append(domain_attach)

        phys_domain = input("Please assign physical domain: ")
        domain_attach.set("tDn", "uni/phys-%s" % phys_domain)

        tree = xml.ElementTree(root)
        with open(epg_file, "wb") as fh:
            tree.write(fh)

        send_configuration(epg_file)

def bridge_domain_configuration(): ##########################Create Bridge Domain, enable routing, flood unknown unicast

    print("\n")
    print("TAB option can be use on some options, this will avoid configuration failures")

    view_tenant()
    print("\n")

    tenant_input = input("Please enter a Tenant: ")

    root = xml.Element("fvTenant")
    root.set("name", tenant_input)

    view_bd(tenant_input)

    bd = xml.Element("fvBD")
    root.append(bd)
    print("\n")
    bd_input = input("Please enter a bridge domain: ")
    bd_options.append(bd_input)
    bd.set("name", bd_input)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(yes_no_answer)

    unicast_route_input = input("Enable unicast route (yes/no): ")
    bd.set("unicastRoute", unicast_route_input)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(flood_scope)

    flood_type_input = input("Hardware Proxy or Flood: ")
    bd.set("unkMacUcastAct", flood_type_input)

##########################Associate to L3Out

    l3out= xml.Element("fvRsBDToOut")

    l3out_asso = input("Associate with L3Out: ")
    l3out.set("tnL3extOutName", l3out_asso)

##########################Subnet Configuration
    subnet= xml.Element("fvSubnet")

    readline.parse_and_bind("tab: complete")
    readline.set_completer(ip_scope)

    scope_adv = input("Please enter a scope: ")
    subnet.set("scope", scope_adv)

    bd.append(subnet)

    while True:
        try:
            ip = input("Please enter a ip address and mask as CIDR: ")
            ipaddress.IPv4Interface(ip)

            subnet.set("ip", ip)

            bd_vrf = xml.Element("fvRsCtx")
            bd.append(bd_vrf)

            bd_vrf_input = input("Please assign a VRF: ")
            bd_vrf.set("tnFvCtxName", bd_vrf_input)

            tree = xml.ElementTree(root)
            with open(bd_file, "wb") as fh:
                tree.write(fh)

            send_configuration(bd_file)
            print("\n")
            break

        except ipaddress.AddressValueError:
            print("\n")
            print("Invalid IP Address")
            print("\n")

def  contract_configuration():

    print("\n")
    print("TAB option can be use on some options, this will avoid configuration failures")

    contract_file = "C:\Python\ACI\Create_Contract_ACI.xml"

    root = xml.Element("fvTenant")

    view_tenant(get_tenant_file)
    print("\n")

    tenant_input = input("Please select a Tenant: ")
    root.set("name", tenant_input)

    vz_filter = xml.Element("vzFilter")

    filter_input = input("Please create a contract filter: ")
    root.append(vz_filter)
    vz_filter.set("name", filter_input)


##################################################Create Filter

    print ("Set filter parameters: ")

    vz_entry = xml.Element("vzEntry")

    filter_entry_input = input("Please assign filter entry a name: ")
    vz_filter.append(vz_entry)
    vz_entry.set("name", filter_entry_input)

    filter_entry_desc_input = input("Entry description: ")
    vz_entry.set("descr", filter_entry_desc_input)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(yes_no_answer)

    stateful_input = input("Stateful (yes/no): ")
    vz_entry.set("stateful", stateful_input)

    ether_type = ("unspecified")
    vz_entry.set("etherT", ether_type)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(contract_filter_entry)

    source_port_input = input("Source port: ")
    vz_entry.set("sToPort", source_port_input)

    dest_input = input("Destination port: ")
    vz_entry.set("sFromPort", dest_input)

    dest_source_input = input("Destination source port: ")
    vz_entry.set("dToPort", dest_source_input)

    dest_dest_input = input("Destination port: ")
    vz_entry.set("dFromPort", dest_dest_input)

################################################## Create contract
    contract = xml.Element("vzBrCP")

    contract_input = input("Please create a contract: ")
    root.append(contract)
    contract.set("name", contract_input)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(contract_scopes)

    contr_scope =input("Please intput a contract scope: ")
    contract.set("scope", contr_scope)

##################################################Create Contract Subject

    subject = xml.Element("vzSubj")

    contract.append(subject)

    subject_name =input("Please enter a subject name: : ")
    subject.set("name", subject_name)

    contr_desc =input("Please input a subject description: ")
    subject.set("descr", contr_desc)

    rev_ports =input("Reverse ports (yes/no:) ")
    subject.set("revFltPorts", rev_ports)

    filter = xml.Element("vzRsSubjFiltAtt")

    subject.append(filter)
    assign_filter = input("Please assign a filter to the contract: ")
    filter.set(" tnVzFilterName", assign_filter)

    tree = xml.ElementTree(root)
    with open(contract_file, "wb") as fh:
        tree.write(fh)

    send_configuration(contract_file)

if __name__ == '__main__':

    ###########################################################
    #Configuration and view files that can be access anywhere in the program
    ###########################################################

    tenant_file = "C:\Python\ACI\Create_Tenant_ACI.xml"
    contract_file = "C:\Python\ACI\Create_Contract_ACI.xml"
    bd_file = "C:\Python\ACI\Create_BD_ACI.xml"
    epg_file = "C:\Python\ACI\Create_EPG_ACI.xml"
    app_file = "C:\Python\ACI\Create_App_ACI.xml"
    get_vlan_pool= "C:\Python\ACI\Get_VLAN_Pool_ACI.xml"
    get_file= "C:\Python\ACI\Get_ACI.xml"

    warnings.filterwarnings("ignore")
    apic = " "
    apic_login()

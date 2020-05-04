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
            body(session, apic)
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL): # If APIC IP is incorrect which makes the URI
        print("Login Failed, please verify APIC IP")                              # Invalid, this exception will be thrown.
        print("\n")
        apic_login()

def body(session, apic):

    vlan_pool = collections.defaultdict(list)
    phys_doms = collections.defaultdict(list)
    aaeps = collections.defaultdict(list)
    location = collections.defaultdict(list)
    path = collections.defaultdict(list)

    time.sleep(1)
    clear()                                                         # Clear terminal

    print("\n")
    print("|-Target Encap--------------------|")
    print("|---------------------------------|")
    print("\n")

    vlan = input("Encap: ")

    pools = vlanPool.aci_gets.find_duplicatee_vlan(session, apic, vlan)
    vlan_pool[vlan].append(pools[0])
    phys_doms[vlan].append(pools[1])
    aaeps[vlan].append(pools[2])
    location[vlan].append(pools[3])
    path[vlan].append(pools[4])

    unpacked_vlan_pools = [v for k, v in vlan_pool.items() for v in v for v in v]
    unpacked_phys_doms = [v for k, v in phys_doms.items() for v in v for v in v ]
    unpacked_aaep = [v for k, v in aaeps.items() for v in v for v in v ]
    unpacked_location = [v for k, v in location.items() for v in v for v in v ]
    unpacked_path = [v for k, v in path.items() for v in v for v in v]

    print("\n")
    print("   Access Policy Details:\n")
    print("     VLAN Pool(s): " + "\n                   ".join(unpacked_vlan_pools))
    print("\n")
    print("     Domain(s):    " + "\n                   ".join(unpacked_phys_doms))
    print("\n")
    print("     AAEP(s):      " + "\n                   ".join(unpacked_aaep))
    print("\n")
    print("     Encap Loc.:   " + "\n                   ".join(unpacked_location))
    print("\n")
    print("     Path Attach:  " + "\n                   ".join(unpacked_path))
    print("\n")

    press_enter = input("Hit End to Continue")
    body(session, apic)

if __name__ == '__main__':

    module_check()
    apic_login()
"""Helper program enabling a user to create and view class maps via NETCONF/YANG"""

import xml.etree.cElementTree as xml
import lxml.etree as ET
from ncclient import manager
import collections
from ncclient.operations import RPCError
import xmltodict
import QoSChecks.Checks as MatchType
import QoSChecks.Build as CreateConfig

class_file = None
get_policies = """<filter><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
					<policy>
					<class-map xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-policy"/>
					</policy>
					</native>
					</filter>"""


# -------------------------------- Begin Supporting Functions ----------------------------

def is_instance(list_or_dict):
    """Converts dictionary to list"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def create_netconf_connection(host, username, password) -> manager:
    """Creates devince connection, get and converts configuration"""

    try:

        netconf_session = manager.connect(host=host, port=830, username=username,
                                          password=password,
                                          device_params={'name': 'csr'})

    except manager.operations.errors.TimeoutExpiredError:
        raise ConnectionError(f"Connection to {host} failed")
    except manager.transport.AuthenticationError:
        raise ConnectionError(f"Invalid Credentials")

    return netconf_session


def check_rpc_reply(response):
    """Checks RPC Reply for string. Notifies user config was saved"""

    if response.rfind("Save running-config successful") != -1:
        print("\nConfiguration Saved!")
    else:
        print("\nConfiguration Not Saved!")

def save_running_config(session):
    """Save new configuration to running config"""

    save_payload = """
                       <cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
                       """
    try:
        response = session.dispatch(ET.fromstring(save_payload)).xml
        check_rpc_reply(response)
    except RPCError as error:
        print("\nAn error has ocuured, pleqase try again!")


def send_configuration(host, user, password, config):
    """Send configuration via NETCONF"""

    session = create_netconf_connection(host, user, password)
    config_file = open(config).read()

    try:
        session.edit_config(config_file, target="running")
        save_running_config(session)
    except manager.operations.errors.TimeoutExpiredError:
        raise ConnectionError(f"Connection to {host} failed")
    except manager.transport.AuthenticationError:
        raise ConnectionError(f"Invalid Credentials")


def save_to_file(config):
    """Finds current directory, creates file, saves file"""

    global class_file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    class_file = dir_path + '\\ClassMaps.xml'

    try:
        config.write(file_or_filename=class_file)
    except OSError:
        raise OSError("Unable to save configuration to file, permission error")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ End Supporting Functions ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# -------------------------------- Begin User Functions ----------------------------------

def credenitals():

    host = input("Host: ")
    user = input("Username: ")
    password = input("Password: ")

    return host, user, password

def config_in_dir() -> str:

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("\nConfiguration Files:\n")
    files = os.listdir()
    for file in files:
        if file.rfind(".xml") != -1:
            print(f"{file}")

    config = input("\nSelection: ")
    full_path = f"{dir_path}\\{config}"

    return full_path


def search_strings(i):
    """Search configuration for config k, v's Calls Checks module"""

    print("\n")
    print(f"{'Class:':>15} {i.get('name')}")
    print(f"{'Prematch:':>15} {i.get('prematch')}")
    print("---------------------------")
    MatchType.is_any(i.get('any'))
    for key in i.get('match', {}):
        if isinstance(i.get('match', {}).get(key, {}), list):
            print(f"{key.capitalize() + ':':>15} {', '.join(i.get('match', {}).get(key, {}))}")
        elif isinstance(i.get('match', {}).get(key, {}), dict):
            MatchType.is_mpls(key, i.get('match', {}).get(key, {}))
            MatchType.is_vlan(key, i.get('match', {}).get(key, {}))
            MatchType.is_protocol(key, i.get('match', {}).get(key, {}))
            MatchType.is_access_group(key, i.get('match', {}).get(key, {}))
            MatchType.is_security_group(key, i.get('match', {}).get(key, {}))
            MatchType.is_atm(key, i.get('match', {}).get(key, {}))
            MatchType.is_discard_class(key, i.get('match', {}).get(key, {}))
            MatchType.is_ip(key, i.get('match', {}).get(key, {}))


def get_class_maps(host, username, password):
    """Gets device class-map configuration"""

    session = create_netconf_connection(host, username, password)
    config_data = session.get(get_policies)
    qos_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
    class_map_details = qos_details["native"].get("policy", {}).get("class-map", {})
    config_list = is_instance(class_map_details)
    list(map(search_strings, config_list))


def class_map():
    """Begin class-map build with root elements and namespaces"""

    parent_opts =   ('access-group', 'any', 'cos', 'discard_class','dscp', 'group_object ','input_interface', 'ip',
                     'mpls', 'not', 'packet','precedence', 'protocol','qos_group', 'security_group', 'vlan')
    match_any_all = ("match-any", "match-all")

    class_input = input("\nCass-map name: ")
    while True:
        match_type = input("Match Type (match-any/all): ").lower()
        if match_type in match_any_all:
            break
        else:
            print("Invalid Input")

    # Print options
    print("\n" + "\n".join(parent_opts) + "\n")
    match = input("Match: ").lower()
    print("\n")

    # Creates object in Templates class, sends class name and match type to _init_
    call_templates = CreateConfig.Templates(class_input, match_type)
    # Gets and checks class method and calls method to begin configuration
    call_method = getattr(call_templates, match)
    config = call_method()
    root = xml.ElementTree(element=config)
    save_to_file(root)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ End User Funtions ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

if __name__ == '__main__':

    while True:
        print("\nNETCONF QoS using ios-xe-native YANG model\n")
        print("1. Create Classmaps\n2. View Classmaps\n3. Send Config\n")

        selection = input("Selection: ")

        if selection == "1":
            class_map()
        elif selection == "2":
            creds = credenitals()
            get_class_maps(host=creds[0], username=creds[1], password=creds[2])
        elif selection == "3":
            creds = credenitals()
            config_file = config_in_dir()
            send_configuration(creds[0], creds[1], creds[2], config_file)
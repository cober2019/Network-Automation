"""Helper program enabling a user to create and view class maps via NETCONF/YANG"""

import lxml.etree as ET
from ncclient import manager
import Checks.Prints as MatchType
from ncclient.operations import RPCError
import xmltodict
import os


class_file = None
get_policies = """<filter><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<router/>
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

def search_strings(config):
    """Parse and prints router BGP configuration"""

    # Get legacy routing configuration
    print(f"\n-----------------------\nLocal AS: {config.get('id')} -------\n")

    if config.get('bgp').get('log-neighbor-changes') is not None:
        print(f"Logging Neighbor: {config.get('bgp').get('log-neighbor-changes')}")

    if config.get('neighbor') is not None:
        print(f"\n-----------------------\nNeighbors -------------\n")
        list(map(MatchType.neighbor, config.get('neighbor', {})))

    if config.get('network') is not None:
        print(f"\nNetwork Statements-----------------------\n")
        list(map(MatchType.networks, config.get('network', {})))

    # Legacy routing configuration
    if config.get("redistribute") is not None:
        print(f"\nRedistribution -----------------------\n")
        try:
            [MatchType.legacy_redistribution(k, v) for k, v in config.get("redistribute").items()]
        except AttributeError:
            pass

    # Cisco ASR
    if config.get('address-family').get('no-vrf').get('ipv4').get('ipv4-unicast'):
        key_1 = [k for k, v in dict.fromkeys(config.get('address-family')).items()]
        key_2 = [k for k, v in dict.fromkeys(config.get('address-family').get(key_1[0])).items()]

        af = config.get('address-family').get(key_1[0]).get(key_2[0])
        print(f"\nAF Name: {af.get('af-name')} -------\n")
        list(map(MatchType.address_family, af.get('ipv4-unicast').get('neighbor')))

        protocols = [k for k, v in dict.fromkeys(af.get('ipv4-unicast').get('redistribute')).items()]
        print(f"\nAF Redistribution: {af.get('af-name')}-----------------------\n")
        [[MatchType.af_redistribution(i, k, v) for k, v in af.get('ipv4-unicast').get('redistribute').get(i).items()] for i in protocols]
    # Cisco ISR
    else:
        key_1 = [k for k, v in dict.fromkeys(config.get('address-family')).items()]
        key_2 = [k for k, v in dict.fromkeys(config.get('address-family').get(key_1[0])).items()]

        af = config.get('address-family').get(key_1[0]).get(key_2[0])
        print(f"\nAF Name: {af.get('af-name')} -------\n")
        list(map(MatchType.address_family, af.get('neighbor')))

        print(f"\nAF Redistribution: {af.get('af-name')}-----------------------\n")
        [MatchType.legacy_redistribution(k, v) for k, v in af.get("redistribute").items()]

    input("")


def get_bgp(host, username, password):
    """Gets device class-map configuration"""

    session = create_netconf_connection(host, username, password)
    config_data = session.get(get_policies)
    qos_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
    bgp_details = qos_details["native"].get("router", {}).get("bgp", {})
    search_strings(bgp_details)


if __name__ == '__main__':

    device = input("Device: ")
    user = input("Username: ")
    password = input("Paasword: ")

    get_bgp(host=device, username=user, password=password)

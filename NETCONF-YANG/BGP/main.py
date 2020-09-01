"""Helper program enabling a user to create and view class maps via NETCONF/YANG"""

from ncclient import manager
import Checks.Prints as MatchType
import xmltodict


get_policies = """<filter><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<router/>
</native>
</filter>"""


# -------------------------------- Begin Supporting Functions ----------------------------

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
    if config.get("redistribute"):
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
        
        if af.get('ipv4-unicast').get('neighbor'):
            print(f"\nNeighbors -------\n")
            list(map(MatchType.address_family, af.get('ipv4-unicast').get('neighbor')))
        if af.get('ipv4-unicast').get('redistribute'):
            protocols = [k for k, v in dict.fromkeys(af.get('ipv4-unicast').get('redistribute')).items()]
            print(f"\nAF Redistribution: {af.get('af-name')}-----------------------\n")
            [[MatchType.af_redistribution(i, v) for k, v in af.get('ipv4-unicast').get('redistribute').get(i).items()] for i in protocols]
        if af.get('ipv4-unicast').get('networks'):
            print(f"\nNetworks -------\n")
            list(map(MatchType.networks, af.get('ipv4-unicast').get('networks')))

    # Cisco ISR
    else:
        key_1 = [k for k, v in dict.fromkeys(config.get('address-family')).items()]
        key_2 = [k for k, v in dict.fromkeys(config.get('address-family').get(key_1[0])).items()]

        af = config.get('address-family').get(key_1[0]).get(key_2[0])
        print(f"\nAF Name: {af.get('af-name')} -------\n")
        list(map(MatchType.address_family, af.get('neighbor')))
        if af.get("redistribute"):
            print(f"\nAF Redistribution: {af.get('af-name')}-----------------------\n")
            [MatchType.af_redistribution(k, v) for k, v in af.get("redistribute").items()]
        if af.get('neighbor'):
            print(f"\nNeighbor Statements-----------------------\n")
            list(map(MatchType.neighbor, af.get('neighbor', {})))
        if af.get('network') is not None:
            print(f"\nNetwork Statements-----------------------\n")
            list(map(MatchType.networks, af.get('network', {})))

    input("")


def get_bgp(host, username, password):
    """Gets device class-map configuration"""

    session = create_netconf_connection(host, username, password)
    config_data = session.get(get_policies)
    qos_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
    bgp_details = qos_details["native"].get("router", {}).get("bgp", {})
    print(bgp_details)
    search_strings(bgp_details)


if __name__ == '__main__':

    device = input("Device: ")
    user = input("Username: ")
    pwrd = input("Paasword: ")

    get_bgp(host=device, username=user, password=pwrd)

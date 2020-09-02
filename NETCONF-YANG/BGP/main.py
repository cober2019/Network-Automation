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

def af_family_asr(config) -> None:
    """Get and parse address-family for ASR YANG"""

    if config.get('address-family', {}).get('no-vrf', {}).get('ipv4', {}).get('ipv4-unicast', {}):
        # Find vrfs, if any
        key_1 = [k for k, v in dict.fromkeys(config.get('address-family')).items()]
        for i in key_1:
            # If vrf print address-family vrf
            if i == "with-vrf":
                print(f"\nAddress Family: {config.get('af-name')} -------")
                print(f"{'VRF: ' + config.get('address-family').get('with-vrf', {}).get('ipv4').get('ipv4-unicast', {}).get('vrf').get('name')} -------")

            # Find ip type, v4 or v6. v4 only supported for now
            key_2 = [k for k, v in dict.fromkeys(config.get('address-family').get(i)).items()]
            af = config.get('address-family').get(i).get(key_2[0])

            if af.get('ipv4-unicast').get('neighbor'):
                print(f"\nAddress Family: {af.get('af-name')} -------")
                print(f"\n   AF Neighbors:\n")
                list(map(MatchType.address_family, af.get('ipv4-unicast').get('neighbor')))
            if af.get('ipv4-unicast').get('redistribute'):
                print(f"\n   AF Redistribution:\n")
                [MatchType.redistribution(k, v) for k, v in af.get('ipv4-unicast').get("redistribute").items()]
            if af.get('ipv4-unicast').get('networks'):
                print(f"   AF Network Statements:\n")
                list(map(MatchType.networks, af.get('ipv4-unicast').get('networks')))
            if af.get('ipv4-unicast').get('prefix-list'):
                list(map(MatchType.networks, af.get('ipv4-unicast').get('prefix-list', {})))


def af_family_isr(config) -> None:
    """Get and parse address-family for ISR YANG"""

    # Cisco ISR,
    if config.get('address-family'):
        # Find vrfs, if any
        if_vrf = [k for k, v in dict.fromkeys(config.get('address-family')).items()]
        for i in if_vrf:
            # If vrf print address-family vrf
            if i == "with-vrf":
                print(f"\nAddress Family: {config.get('af-name')} "
                      f"{'VRF: ' + config.get('address-family').get('with-vrf', {}).get('ipv4').get('vrf').get('name')} -------")

            # Find ip type, v4 or v6. v4 only supported for now
            ip_type = [k for k, v in dict.fromkeys(config.get('address-family').get(i)).items()]
            af = config.get('address-family').get(i).get(ip_type[0])

            # Begin configuration for BGP perameters
            if af.get('neighbor'):
                print(f"\nAddress Family: {af.get('af-name')} -------")
                print(f"\n   AF Neighbor Information:\n")
                list(map(MatchType.address_family, af.get('neighbor')))
            if af.get("redistribute"):
                print(f"\n   AF Redistribution:\n")
                [MatchType.redistribution(k, v) for k, v in af.get("redistribute").items()]
            if af.get('network'):
                print(f"\n   AF Network Statements:\n")
                list(map(MatchType.networks, af.get('network', {})))
            if af.get('prefix-list'):
                list(map(MatchType.networks, af.get('prefix-list', {})))


def legacy(config) -> None:
    """Legacy routing config, non address-family"""

    if config.get('neighbor'):
        print(f"   Neighbors -------------\n")
        list(map(MatchType.neighbor, config.get('neighbor', {})))
    if config.get('network'):
        print(f"\n   Network Statements-----------------------\n")
        list(map(MatchType.networks, config.get('network', {})))
    if config.get("redistribute"):
        print(f"\n   Redistribution -----------------------\n")
        [MatchType.redistribution(k, v) for k, v in config.get("redistribute", {}).items()]
    if config.get('prefix-list'):
        list(map(MatchType.networks, config.get('prefix-list', {})))


def search_config(config) -> None:
    """Parse and prints router BGP configuration"""

    # Get legacy routing configuration
    print(f"\n-----------------------\nLocal AS: {config.get('id')} -------\n")

    if config.get('bgp', {}).get('log-neighbor-changes', {}):
        print(f"Logging Neighbor: {config.get('bgp').get('log-neighbor-changes')}\n")

    legacy(config)
    af_family_asr(config)
    af_family_isr(config)

    input("\nEnd Program, Press Enter to Close")


def get_bgp(host, username, password) -> None:
    """Gets device BGP configuration"""

    session = create_netconf_connection(host, username, password)
    config_data = session.get(get_policies)
    qos_details = xmltodict.parse(config_data.xml)["rpc-reply"]["data"]
    bgp_details = qos_details["native"].get("router", {}).get("bgp", {})
    search_config(bgp_details)


if __name__ == '__main__':

    device = input("Device: ")
    user = input("Username: ")
    pwd = input("Password: ")

    get_bgp(host=device, username=user, password=pwd)

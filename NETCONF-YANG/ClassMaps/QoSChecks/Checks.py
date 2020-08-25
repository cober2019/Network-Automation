"""Helper functions to search class-map configurations"""


def is_instance(list_or_dict) -> list:
    """Converts dictionary to list"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_mpls(outter_key, inner_key) -> None:
    """Prints MPLS Experimental tags"""

    if outter_key == "mpls":
        make_list = is_instance(inner_key.get('experimental', {}).get('topmost', {}))
        print(f"{'MPLS:':>15} {', '.join(make_list)}")


def is_vlan(outter_key, inner_key) -> None:
    """Prints vlan tags"""

    if outter_key == "vlan":
        if inner_key.get('inner') is not None:
            make_list = is_instance(inner_key.get('inner', {}))
            print(f"{'InnerVlan(s):':>15} {', '.join(make_list)}")
        if inner_key.get('value') is not None:
            make_list = is_instance(inner_key.get('value', {}))
            print(f"{'Vlan(s):':>15} {', '.join(make_list)}")


def is_protocol(outter_key, inner_key) -> None:
    """Prints protocol Experimental tags"""

    if outter_key == "protocol":
        if len(inner_key.get('protocols-list')) == 1:
            print(f"{'Protocol(s):':>15} {inner_key.get('protocols-list').get('protocols')}")
        else:
            protocols = [i.get('protocols') for i in inner_key.get('protocols-list')]
            print(f"{'Protocols:':>15} {', '.join(protocols)}")


def is_access_group(outter_key, inner_key) -> None:
    """Prints access-group """

    if outter_key == "access-group":
        if inner_key.get('index') is not None:
            make_list = is_instance(inner_key.get('index', {}))
            print(f"{'AccGrp(int):':>15} {', '.join(make_list)}")
        if inner_key.get('name') is not None:
            make_list = is_instance(inner_key.get('name', {}))
            print(f"{'AccGrp(name):':>15} {', '.join(make_list)}")


def is_security_group(outter_key, inner_key) -> None:
    """Prints security group """

    if outter_key == "security-group":
        if inner_key.get('source') is not None:
            print(f"{'SecGrp(source):':>15} {inner_key.get('source', {}).get('tag', {})}")
        if inner_key.get('destination') is not None:
            print(f"{'SecGrp(dest):':>15} {inner_key.get('destination', {}).get('tag', {})}")


def is_atm(outter_key, inner_key) -> None:
    """Not supported"""

    if outter_key == "atm":
        if inner_key.get('clp') is not None:
            make_list = is_instance(inner_key.get('clp', {}))
            print(f"{'Access - Grp(int):':>15} {', '.join(make_list):<30}")
        if inner_key.get('atm-vci ') is not None:
            make_list = is_instance(inner_key.get('atm-vci ', {}))
            print(f"{'Access - Grp(name):':>15} {', '.join(make_list):<30}")


def is_discard_class(outter_key, inner_key) -> None:
    """Prints discard class"""

    if outter_key == "discard-class":
        make_list = is_instance(inner_key.get('discard-class', {}))
        print(f"{'DiscardClass(s):':>15} {', '.join(make_list)}")


def is_packet_length(outter_key, inner_key) -> None:
    """Prints packet length"""

    if outter_key == "packet":
        if inner_key.get('length').get('min') is not None:
            make_list = is_instance(inner_key.get('length').get('min'))
            print(f"{'Pkt Length(min):':>15} {', '.join(make_list)}")
        if inner_key.get('length').get('max') is not None:
            make_list = is_instance(inner_key.get('length').get('max'))
            print(f"{'Pkt Length(max):':>15} {', '.join(make_list)}")


def is_ip(outter_key, inner_key) -> None:
    """Prints ip, rtp, precdedence"""

    if outter_key == "ip":
        if inner_key.get('dscp') is not None:
            make_list = is_instance(inner_key.get('dscp'))
            print(f"{'IP Dscp:':>15} {', '.join(make_list)}")
        if inner_key.get('precedence') is not None:
            make_list = is_instance(inner_key.get('precedence'))
            print(f"{'IP Precedence:':>15} {', '.join(make_list)}")
        if inner_key.get('rtp') is not None:
            make_list = is_instance(inner_key.get('rtp', {}).get('port1', {}))
            print(f"{'RTP High:':>15} {', '.join(make_list)}")
            make_list = is_instance(inner_key.get('rtp', {}).get('port2', {}))
            print(f"{'RTP Low:':>15} {', '.join(make_list)}")


def is_any(inner_key) -> None:
    """Prints any"""

    if inner_key is None:
        print(f"{'Match: Any':>19}")

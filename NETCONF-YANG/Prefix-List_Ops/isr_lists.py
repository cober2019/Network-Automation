"""Helper funtions for prefix list operations"""
from typing import Any, Tuple
from ncclient import manager
from Software import Get_Routing
import ipaddress
import xmltodict


def is_instance(list_or_dict):

    """Checks to if miltiple prefix-list are in the config. If one list is in the configuration, structure is dictionary
    If multiple list are in the config, structure will be a list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_seq_list(list_or_dict):
    """Checks to "seq" key is list or dictionary. If one seq is in the prefix-list, seq is a dictionary, if multiple seq,
    seq will be list of dictionaries. Convert to list if dictionary"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def is_ge_or_le(list_attributes):
    # Check ge or le for configuration template variable
    try:
        mask = list_attributes["ge"]
        ge_le = "ge"
    except KeyError:
        mask = list_attributes["le"]
        ge_le = "le"

    return mask, ge_le


def is_permit_or_deny(sequence) -> str:
    """Gets key, permit or deny from prefix statement"""

    action = None
    if "permit" in sequence:
        action = "permit"
    elif "deny" in sequence:
        action = "deny"
    return action


# Warning functions used for pre-deployment checks-----------------

def check_duplicate_ge_le(prefix_lists, list_name, seq, prefix, ge=None, le=None, ge_le=None) -> None:
    """Check to see if the proposed sequence is duplicate. This a pre-deploymnet check. Configuration
    may be list or dictionary"""

    for prefix_list in prefix_lists:
        lists = is_seq_list(prefix_list["seq"])
        for sequence in lists:
            action = is_permit_or_deny(sequence)
            if list_name == prefix_list["name"] and seq == sequence["no"]:
                raise ValueError("Sequence Exist")
            if sequence[action]["ip"][-2:] == ge or sequence[action]["ip"][-2:] == ge_le and prefix == sequence[action]["ip"]:
                raise ValueError(f"ge_le value overlaps with prefix-length: seq {sequence['no']} prefix: {sequence[action]['ip']}")
            if sequence[action]["ip"][-2:] == le or sequence[action]["ip"][-2:] == ge_le and prefix == sequence[action]["ip"]:
                raise ValueError(f"ge_le value overlaps with prefix-length: seq {sequence['no']} prefix: {sequence[action]['ip']}")


def check_duplicate(prefix_lists, list_name, seq, proposed_prefix) -> None:
    """Check to see if the proposed sequence is duplicate. This a pre-deploymnet check. Configuration
    may be list or dictionary"""

    for prefix_list in prefix_lists:
        lists = is_seq_list(prefix_list["seq"])
        for sequence in lists:
            action = is_permit_or_deny(sequence)
            if list_name == prefix_list["name"] and seq == sequence["no"]:
                raise ValueError(f"Sequence Exist Seq: {sequence['no']}")
            if list_name == prefix_list["name"] and ipaddress.IPv4Network(proposed_prefix).\
                    overlaps(ipaddress.IPv4Network(sequence[action]["ip"])):
                raise ValueError(f"Prefix Exist/Overlaps List: {list_name} Seq:{sequence['no']}")


def is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, current_prefix) -> None:

    try:
        if list(set(proposed_cidrs) & set(current_cidrs)):
            raise ValueError(f"{proposed_prefix}: overlap detected in list {list_name}: seq {sequence['no']}")
    except TypeError:
        pass


def check_overlapping(prefix_lists, proposed_prefix, list_name, ge=None, le=None, ge_le=None, mask=None) -> None:
    """Checks to see if the proposed prefix overlaps with a current prefix statement"""

    proposed_cidrs = None
    current_cidrs = None

    if le is not None and le is not None:
        proposed_cidrs = list(range(int(ge), int(le)))
    if ge_le == "ge":
        proposed_cidrs = list(range(int(mask), 33))
    if ge_le == "le":
        proposed_cidrs = list(range(6, int(mask)))

    for prefix_list in prefix_lists:
        lists = is_seq_list(prefix_list["seq"])
        for sequence in lists:
            action = is_permit_or_deny(sequence)

            if prefix_list["name"] == list_name and ipaddress.IPv4Network(proposed_prefix).overlaps(ipaddress.IPv4Network(sequence[action]["ip"])):
                # Get existing ge/le and compare to proposed ge/le
                try:
                    current_cidrs = list(range(int(sequence[action]["ge"]), int(sequence[action]["le"])))
                    is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, sequence[action]["ip"])
                except (KeyError, TypeError, UnboundLocalError):
                    pass
                try:
                    current_cidrs = list(range(int(sequence[action]["ge"]), 33))
                    is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, sequence[action]["ip"])
                except (KeyError, TypeError, UnboundLocalError):
                    pass
                try:
                    current_cidrs = list(range(int(sequence[action]["ip"][-2:]), int(sequence[action]["le"])))
                    is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, sequence[action]["ip"])
                except (KeyError, TypeError, UnboundLocalError):
                    pass


def external_prefix_warning(vrf) -> None:
    """Check to see if the proposed prefix is in routing. This a pre-deploymnet check"""

    while True:
        which_vrf = [k for k in vrf.keys()]
        print(f"\nExternal prefix located in vrf {which_vrf[0]}\n")
        warning = input("      - Prefix is external/not local, Are you sure you want to add (yes/no)?: ").lower()
        if warning == "yes":
            break
        elif warning == "no":
            raise ValueError("Prefix configuration aborted")
        else:
            print("Invalid Input!")


# ^^^^^^^^^^^^^^^^^^^^ End pre-deployements funtions ^^^^^^^^^^^^^^^^^^^^

# ----------------------Begin user funtions------------------------------


def get_prefix_list(username, password, host) -> Tuple[list, Any]:
    """Gets current prefix-lists from device and converts from xml to dictionary"""

    xml_filter = """<filter xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                    <ip>
                    <prefix-list/>
                    </ip>
                    </native>
                    </filter>"""

    try:

        netconf_session = manager.connect(host=host, port=830, timeout=3, username=username,
                                          password=password,
                                          device_params={'name': 'csr'})

    except (manager.NCClientError, AttributeError, ConnectionError):
        raise ConnectionError(f"Connection to {host} failed")

    intf_info = netconf_session.get(xml_filter)
    intf_dict = xmltodict.parse(intf_info.xml)["rpc-reply"]["data"]

    # Check to see if the configuration is empty
    if intf_dict is None:
        prefixt_lists = None
    else:
        prefixes = intf_dict["native"]["ip"]["prefix-list"]["prefixes"]
        prefixt_lists = is_instance(prefixes)

    return prefixt_lists, netconf_session


def find_prefix(username, password, host, prefix) -> None:
    """Find specific prefix in prefix-list. Confgiuration may be list or dictionary"""

    # Get prefix-list configuration
    prefix_lists = get_prefix_list(username, password, host)

    for prefix_list in prefix_lists[0]:
        lists = is_instance(prefix_list["seq"])
        # Config is list if only one prefix statement in list
        for sequence in lists:
            action = is_permit_or_deny(sequence)
            try:
                if prefix == sequence[action]["ip"]:
                    print(f"\nList: {prefix_list['name']}")
                    print(f"Seq: {sequence['no']}")
                    print(f"Prefix: {sequence[action]['ip']}")
            except KeyError:
                pass


def view_prefix_list(username, password, host) -> None:
    """View current prefix-list, match statemnt combinations."""

    # Get prefix-list configuration
    prefix_lists = get_prefix_list(username, password, host)

    for prefix_list in prefix_lists[0]:
        print(prefix_list["name"])
        lists = is_instance(prefix_list["seq"])
        # Config is list if only one prefix statement in list
        for sequence in lists:
            action = is_permit_or_deny(sequence)
            if "ge" in sequence[action] and "le" in sequence[action]:
                print(sequence["no"], action, sequence[action]["ip"], sequence[action]["ge"], sequence[action]["le"])
            if "ge" in sequence[action] and "le" not in sequence[action]:
                print(sequence["no"], action, sequence[action]["ip"], sequence[action]["ge"])
            if "le" in sequence[action] and "ge" not in sequence[action]:
                print(sequence["no"], action, sequence[action]["ip"], sequence[action]["le"])
            if "le" not in sequence[action] and "ge" not in sequence[action]:
                print(sequence["no"], action, sequence[action]["ip"])
        print("\n")


def send_prefix_list(username, password, host, **list_attributes) -> None:
    """Selects and sends configuration based user arguments. Performs pre-deployemnet check prior to deploying the
    configuration"""

    config_template = None
    # Get prefix-list configuration
    prefix_lists = get_prefix_list(username, password, host)
    search_for_route = Get_Routing.find_prefix(host=host, username=username, password=password,
                                               proposed_prefix=list_attributes["prefix"])

    # Check to see if the proposed prefix in the current routing table
    if True in search_for_route.values():
        external_prefix_warning(search_for_route)
    else:
        pass

    # Depending on user inputs/arguments, one of 4 config templates will be choosen. If the device doesnt have prefix-list, bypass the checks.

    if "le" in list_attributes and "ge" in list_attributes:
        if prefix_lists[0] is not None:
            check_overlapping(prefix_lists[0], list_attributes["prefix"], list_attributes["name"], ge=list_attributes["ge"], le=list_attributes["le"])
            check_duplicate_ge_le(prefix_lists[0], list_attributes["name"], list_attributes["seq"], list_attributes["prefix"], ge=list_attributes["ge"], le=list_attributes["le"])

        config_template = f"""<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                    <prefix-list><prefixes><name>{list_attributes["name"]}</name> 
                    <seq>
                    <no>{list_attributes["seq"]}</no>
                    <{list_attributes["action"]}>
                    <ip>{list_attributes["prefix"]}</ip> 
                    <ge>{list_attributes["ge"]}</ge>
                    <le>{list_attributes["le"]}</le>
                    </{list_attributes["action"]}>
                    </seq>
                    </prefixes></prefix-list></ip></native></config>"""

    elif "ge" in list_attributes or "le" in list_attributes:

        ge_le = is_ge_or_le(list_attributes)
        if prefix_lists[0] is not None:
            check_overlapping(prefix_lists[0], list_attributes["prefix"], list_attributes["name"],  ge_le=ge_le[1], mask=ge_le[0])
            check_duplicate_ge_le(prefix_lists[0], list_attributes["name"], list_attributes["seq"], list_attributes["prefix"], ge=ge_le)

        # Check ge or le for configuration template variable
        config_template = f"""<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                    <prefix-list><prefixes><name>{list_attributes["name"]}</name> 
                    <seq>
                    <no>{list_attributes['seq']}</no> 
                    <{list_attributes["action"]}>
                    <ip>{list_attributes["prefix"]}</ip> 
                    <{ge_le[1]}>{ge_le[0]}</{ge_le[1]}> 
                    </{list_attributes["action"]}>
                    </seq>
                    </prefixes></prefix-list></ip></native></config>"""

    elif "le" not in list_attributes and "ge" not in list_attributes:
        if prefix_lists[0] is not None:
            check_overlapping(prefix_lists[0], list_attributes["prefix"], list_attributes["name"])
            check_duplicate(prefix_lists[0], list_attributes["name"], list_attributes["seq"], list_attributes["prefix"])

        config_template = f"""<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                    <prefix-list><prefixes><name>{list_attributes["name"]}</name> 
                    <seq>
                    <no>{list_attributes["seq"]}</no> 
                    <{list_attributes["action"]}>
                    <ip>{list_attributes["prefix"]}</ip>
                    </{list_attributes["action"]}>
                    </seq>
                    </prefixes></prefix-list></ip></native></config>"""

    # Send the configuration via netconf
    prefix_lists[1].edit_config(config=config_template, target="running")


# ^^^^^^^^^^^^^^^^^^^^ End user funtions ^^^^^^^^^^^^^^^^^^^^

view_prefix_list(username="cisco", password="cisco", host="10.48.1.51")
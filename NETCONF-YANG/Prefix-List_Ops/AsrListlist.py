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

# Warning functions used for pre-deployment checks-----------------


def check_duplicate_ge_le(prefix_lists, list_name, seq, prefix, ge=None, le=None) -> None:
    """Check to see if the proposed sequence is duplicate. This a pre-deploymnet check. Configuration
    may be list or dictionary"""

    for prefix_list in prefix_lists:
        lists = is_seq_list(prefix_list["seq"])
        for sequence in lists:
            if list_name == prefix_list.get("name") and seq == sequence.get("no"):
                raise ValueError("Sequence Exist")
            if sequence.get("ip")[-2:] == ge and prefix == sequence.get("ip"):
                raise ValueError(f"ge_le value overlaps with prefix-length: seq {sequence.get('no')} prefix: {sequence.get('ip')}")
            if sequence.get("ip")[-2:] == le and prefix == sequence.get("ip"):
                raise ValueError(f"ge_le value overlaps with prefix-length: seq {sequence.get('no')} prefix: {sequence.get('ip')}")


def check_duplicate(prefix_lists, list_name, seq, proposed_prefix) -> None:
    """Check to see if the proposed sequence is duplicate. This a pre-deploymnet check. Configuration
    may be list or dictionary"""

    for prefix_list in prefix_lists:
        lists = is_seq_list(prefix_list["seq"])
        for sequence in lists:
            if list_name == prefix_list.get("name") and seq == sequence.get("no"):
                raise ValueError(f"Sequence Exist Seq: {sequence.get('no')}")
            if list_name == prefix_list.get("name") and ipaddress.IPv4Network(proposed_prefix).\
                    overlaps(ipaddress.IPv4Network(sequence.get("ip"))):
                raise ValueError(f"Prefix Exist/Overlaps List: {list_name} Seq:{sequence.get('no')}")


def is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, current_prefix) -> None:

    try:
        if list(set(proposed_cidrs) & set(current_cidrs)):
            raise ValueError(f"{proposed_prefix}: overlap detected in list {list_name}: seq {sequence.get('no')}")
    except TypeError:
        pass


def check_overlapping(prefix_lists, proposed_prefix, list_name, ge=None, le=None) -> None:
    """Checks to see if the proposed prefix overlaps with a current prefix statement"""

    for prefix_list in prefix_lists:
        lists = is_seq_list(prefix_list["seq"])
        for sequence in lists:

            if prefix_list.get("name") == list_name and ipaddress.IPv4Network(proposed_prefix).overlaps(ipaddress.IPv4Network(sequence.get("ip"))):
                # Get existing ge/le and compare to proposed ge/le
                try:
                    proposed_cidrs = list(range(int(ge), int(le)))
                    current_cidrs = list(range(int(sequence.get("ge")), int(sequence.get("le"))))
                    is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, sequence.get("ip"))
                except TypeError:
                    pass
                try:
                    proposed_cidrs = list(range(int(ge), 33))
                    current_cidrs = list(range(int(sequence.get("ge")), 33))
                    is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, sequence.get("ip"))
                except TypeError:
                    pass
                try:
                    proposed_cidrs = list(range(6, int(le)))
                    current_cidrs = list(range(int(sequence.get("ip")[-2:]), int(sequence.get("le"))))
                    is_overlapping(proposed_cidrs, current_cidrs, sequence, proposed_prefix, list_name, sequence.get("ip"))
                except TypeError:
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
        for sequence in lists:
            if prefix == sequence.get("ip"):
                print(f"\nList: {prefix_list.get('name')}")
                print(f"Seq: {sequence.get('no')}")
                print(f"Prefix: {sequence.get('action')} {sequence.get('ip')}")


def view_prefix_list(username, password, host) -> None:
    """View current prefix-list, match statemnt combinations."""

    # Get prefix-list configuration
    prefix_lists = get_prefix_list(username, password, host)

    for prefix_list in prefix_lists[0]:
        print(prefix_list.get("name"))
        lists = is_instance(prefix_list["seq"])
        for sequence in lists:
            print(sequence.get("no"), sequence.get("action"), sequence.get("ip"), sequence.get("ge", ""), sequence.get("le", ""))
        print("\n")


def send_prefix_list(username, password, host, **list_attributes) -> None:
    """Selects and sends configuration based user arguments. Performs pre-deployemnet check prior to deploying the
    configuration"""

    # Get prefix-list configuration
    prefix_lists = get_prefix_list(username, password, host)
    search_for_route = Get_Routing.find_prefix(host=host, username=username, password=password,
                                               proposed_prefix=list_attributes.get("prefix"))

    # Check to see if the proposed prefix in the current routing table
    if True in search_for_route.values():
        external_prefix_warning(search_for_route)
    else:
        pass

    # Depending on user inputs/arguments, one of 4 config templates will be choosen. If the device doesnt have prefix-list, bypass the checks.

    config_template = f"""<config><native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"><ip>
                   <prefix-list><prefixes><name>{list_attributes["name"]}</name> 
                   <seq>
                   <no>{list_attributes.get("seq")}</no> 
                   <action>{list_attributes.get("action")}</action>
                   <ip>{list_attributes.get("prefix")}</ip>"""

    if list_attributes.get("le") and list_attributes.get("ge"):
        if prefix_lists[0] is not None:
            check_overlapping(prefix_lists[0], list_attributes.get("prefix"), list_attributes.get("name"), ge=list_attributes.get("ge"), le=list_attributes.get("le"))
            check_duplicate_ge_le(prefix_lists[0], list_attributes.get("name"), list_attributes.get("seq"), list_attributes.get("prefix"), ge=list_attributes.get("ge"), le=list_attributes.get("le"))

        config_template = config_template + f"""<ge>{list_attributes["ge"]}</ge><le>{list_attributes["le"]}</le>"""

    elif list_attributes.get("ge") or list_attributes.get("le"):

        if prefix_lists[0] is not None:
            check_overlapping(prefix_lists[0], list_attributes.get("prefix"), list_attributes.get("name"), le=list_attributes.get("le"), ge=list_attributes.get("ge"))
            check_duplicate_ge_le(prefix_lists[0], list_attributes.get("name"), list_attributes.get("seq"), list_attributes.get("prefix"), le=list_attributes.get("le"), ge=list_attributes.get("ge"))
        if list_attributes.get("ge"):
            config_template = config_template + f"""<ge>{list_attributes.get("ge")}</ge>"""
        if list_attributes.get("le"):
            config_template = config_template + f"""<le>{list_attributes.get("le")}</le>"""

    else:
        check_duplicate(prefix_lists[0], list_attributes.get("name"), list_attributes.get("seq"), list_attributes.get("prefix"))

    # Close XML elements out at the end of the configuration template
    config_template = config_template + f"""</seq></prefixes></prefix-list></ip></native></config>"""
    # Send the configuration via netconf
    prefix_lists[1].edit_config(config=config_template, target="running")


# ^^^^^^^^^^^^^^^^^^^^ End user funtions ^^^^^^^^^^^^^^^^^^^^

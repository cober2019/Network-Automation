"""Helper funtions to view IETF interface qos and statistics"""

from ncclient import manager
import xmltodict
import collections

all_ints = f"""<filter>
           <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
           <interface>
           </interface>
           </interfaces-state>
           </filter>"""

# ------------------------ pre-deployements funtions -----------------------


def is_instance(list_or_dict):
    """convert anything not a list to list"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def create_netconf_connection(username, password, host) -> manager:
    """Creates devince connection, get and converts configuration"""

    try:

        netconf_session = manager.connect(host=host, port=830, username=username,
                                          password=password,
                                          device_params={'name': 'csr'})

    except manager.operations.errors.TimeoutExpiredError:
        raise ConnectionError(f"Connection to {host} failed")

    return netconf_session


def print_queues(policies):
    """Join list which are the queues. Add worw titles to row using zip(tuple)"""

    cat = ("Queue      ->", "Bytes In   ->", "Bytes Out  ->", "Drop Bytes ->", "Drop Pkts  ->")
    for v in policies.values():
        queue = (list(zip(*v)))
        for b, i in zip(cat, queue):
            print(f"{b}  {' '.join(i)}")


def is_key(interface):
    """Check for interface key, two possibilities"""

    try:
        int_type = interface.get('name', {}).get('#text', {})
    except AttributeError:
        int_type = interface['name']

    return int_type


def parse_stats(interface):
    """Search key value pairs, print policy, queues, stats"""

    key = is_key(interface)
    policies = collections.defaultdict(list)
    # Check interface for policy application, skip if not applied
    if interface.get("diffserv-target-entry", {}).get("direction", {}):
        print(f"\n-------------------------\n{key}\nPolicy Direction: {interface.get('diffserv-target-entry', {}).get('direction', {})}")
        print(f"Policy Name: {interface.get('diffserv-target-entry', {}).get('policy-name', {})}\n-------------------------\n")
        for stat in interface.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {}):
            # Creates list and resets at each iteration
            queue = []
            # Write dictionary values to list, add string formatting
            queue.append(f"{stat.get('classifier-entry-name', {}):<20}")
            queue.append(f"{stat.get('classifier-entry-statistics', {}).get('classified-bytes', {}):<20}")
            queue.append(f"{stat.get('classifier-entry-statistics', {}).get('classified-pkts', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('drop-pkts', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('drop-bytes', {}):20}")
            # Write list as value to key which is our policy name
            policies[interface.get('diffserv-target-entry', {}).get('policy-name', {})].append(queue)
        print_queues(policies)


def get_interfaces(username, password, host, interface=None):
    """Gets one interface with policies, queues, and stats"""

    if interface is not None:

        int_stats = f"""<filter>
                    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                    <name>{interface}</name>
                    </interface>
                    </interfaces-state>
                    </filter>"""

        # Create NETCONF Session, get config
        netconf_session = create_netconf_connection(username, password, host)
        get_state = netconf_session.get(int_stats)
        int_info = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]["interfaces-state"]["interface"]

    else:

        netconf_session = create_netconf_connection(username, password, host)
        get_state = netconf_session.get(all_ints)
        int_info = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]["interfaces-state"]["interface"]

    # Check to see if value us a list or dict, makes list if not. Helps cut down on code
    make_ints_lists = is_instance(int_info)
    # Iterate through make_ints_lists using map funtion, call parses stats, send list
    list(map(parse_stats, make_ints_lists))


def has_qos(username, password, host):
    """Check to see if the interface is assigned a policy"""

    # Create NETCONF Session, get config
    netconf_session = create_netconf_connection(username, password, host)
    get_state = netconf_session.get(all_ints)

    # Create variable to access the values of the interfaces key
    int_info = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]["interfaces-state"]["interface"]

    # Check to see if value us a list or dict, makes list if not. Helps cut down on code
    make_ints_lists = is_instance(int_info)
    for interface in make_ints_lists:
        print(f"{interface['name']}\n-------------------------")
        # Check interface for policy application, mark policy as "Not Assigned" if no policy
        if interface.get("diffserv-target-entry", {}).get("direction", {}):
            print(f"Qos Policy Assigned: Assign->Policy Name: {interface.get('diffserv-target-entry', {}).get('policy-name', {})}\n")
        else:
            print(f"Qos Policy Assigned: Not Assigned\n")







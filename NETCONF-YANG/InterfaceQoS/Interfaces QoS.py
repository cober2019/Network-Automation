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


def is_instance(list_or_dict) -> list:
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
    except manager.transport.AuthenticationError:
        raise ConnectionError(f"Invalid Credentials")

    return netconf_session


def print_queues(policies) -> None:
    """Join list which are the queues. Add worw titles to row using zip(tuple)"""

    cat = ("Queue       ->", "Class Rate  ->",
           "Class Pkts  ->", "Class Bytes ->",
           "Out Bytes   ->", "Out Pkts    ->",
           "Drop Bytes  ->", "Drop Pkts   ->",
           "WRED Pkts   ->", "WRED Bytes  ->")

    for v in policies.values():
        queue = (list(zip(*v)))
        for b, i in zip(cat, queue):
            print(f"{b}  {' '.join(i)}")


def is_key(config) -> list:
    """Check for interface key, two possibilities"""

    try:
        int_type = config.get('name', {}).get('#text', {})
    except AttributeError:
        int_type = config['name']

    return int_type


def parse_stats(config) -> None:
    """Search key value pairs, print policy, queues, stats"""

    key = is_key(config)
    policies = collections.defaultdict(list)
    # Check interface for policy application, skip if not applied
    if config.get("diffserv-target-entry", {}).get("direction", {}):
        print(
            f"\n-------------------------\n{key}\nPolicy Direction: {config.get('diffserv-target-entry', {}).get('direction', {})}")
        print(
            f"Policy Name: {config.get('diffserv-target-entry', {}).get('policy-name', {})}\n-------------------------\n")
        for stat in config.get("diffserv-target-entry", {}).get("diffserv-target-classifier-statistics", {}):
            # Creates list and resets at each iteration
            queue = []
            # Write dictionary values to list, add string formatting
            queue.append(f"{stat.get('classifier-entry-name', {}):<20}")
            queue.append(f'{stat.get("classifier-entry-statistics", {}).get("classified-rate", {}):<20}')
            queue.append(f"{stat.get('classifier-entry-statistics', {}).get('classified-bytes', {}):20}")
            queue.append(f"{stat.get('classifier-entry-statistics', {}).get('classified-pkts', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('output-bytes', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('output-pkts', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('drop-pkts', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('drop-bytes', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('wred-stats', {}).get('early-drop-pkts', {}):20}")
            queue.append(f"{stat.get('queuing-statistics', {}).get('wred-stats', {}).get('early-drop-bytes', {}):20}")
            # Write list as value to key which is our policy name
            policies[config.get('diffserv-target-entry', {}).get('policy-name', {})].append(queue)
        print_queues(policies)


def get_interfaces(username, password, host, interface_name=None) -> None:
    """Gets one interface with policies, queues, and stats"""

    if interface_name is not None:

        int_stats = f"""<filter>
                    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                    <name>{interface_name}</name>
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
    main()



def has_qos(username, password, host) -> None:
    """Check to see if the interface is assigned a policy"""

    # Create NETCONF Session, get config
    netconf_session = create_netconf_connection(username, password, host)
    get_state = netconf_session.get(all_ints)

    # Create variable to access the values of the interfaces key
    int_info = xmltodict.parse(get_state.xml)["rpc-reply"]["data"]["interfaces-state"]["interface"]

    # Check to see if value us a list or dict, makes list if not. Helps cut down on code
    make_ints_lists = is_instance(int_info)
    for config in make_ints_lists:
        print(f"{config['name']}\n-------------------------")
        # Check interface for policy application, mark policy as "Not Assigned" if no policy
        if config.get("diffserv-target-entry", {}).get("direction", {}):
            print(
                f"Qos Policy Assigned: Assign->Policy Name: {config.get('diffserv-target-entry', {}).get('policy-name', {})}\n")
        else:
            print(f"Qos Policy Assigned: Not Assigned\n")

    main()


def main():

    print("Netconf Qos\n")
    print("1. View All Qos Interfaces")
    print("2. View Single Interface")
    print("3. Check if Interface has QoS\n")

    selection = input("Selecection: ")

    if selection == "1":
        device = input("Host: ")
        user = input("Username: ")
        pwd = input("Password: ")
        get_interfaces(username=user, password=pwd, host=device)
    elif selection == "2":
        device = input("Host: ")
        user = input("Username: ")
        pwd = input("Password: ")
        interface = input("Interface: ")
        get_interfaces(username=user, password=pwd, host=device, interface_name=interface)
    elif selection == "3":
        device = input("Host: ")
        user = input("Username: ")
        pwd = input("Password: ")
        has_qos(username=user, password=pwd, host=device)


if __name__ == '__main__':
    main()
"""Helper functions to search class-map configurations"""


def is_instance(list_or_dict) -> list:
    """Converts dictionary to list"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


def neighbor(config):

    print(f"Neighbor: {config.get('id'):<15}  Remote AS: {config.get('remote-as')}")

def address_family(config):

    print(f"Neighbor: {config.get('id', {}):<15} Direction: {config.get('route-map', {}).get('inout', 'None'):<7} "
          f"Route-Map: {config.get('route-map', {}).get('route-map-name', 'None'):<15} "
          f"Networks: {config.get('network', 'None')} "
          f"Soft-Reconfig: {config.get('soft-reconfiguration', 'None')}")

def networks(config):

    print(f"Networks: {config.get('number', 'None'):<15}  Mask:{config.get('mask', 'None')}")

def legacy_redistribution(protocol, details):

    if protocol == "connected":
        print(f"Protocol: {protocol:<15} "
              f"{'Route-map: ' + details.get('route-map') + ' -----> '}"
              f"{'Metric: ' + details.get('metric')}")

    if protocol == "ospf":
        print(f"Protocol: {protocol:<15} Routing ID: {details.get('id', {}) + ' ----->'}  "
              f"{' Route-map: ' + details.get('non-vrf', {}).get('route-map', {}) + ' ----->'} "
              f"{'Metric: ' + details.get('non-vrf', {}).get('metric', {})}")


def af_redistribution(protocol, value=None):

    if protocol == "connected":
        print(f"Protocol: {protocol:<15} Route-map: {value}")
        print(f"-------------------------------------------------")
    if protocol == "ospf" and isinstance(value, str):
        print(f"Protocol: {protocol:<15} Proccess-ID: {value}")
    elif protocol == "ospf" and isinstance(value, dict):
        print(f"Protocol: {protocol:<15} Route-map: {value.get('route-map', 'None')}")








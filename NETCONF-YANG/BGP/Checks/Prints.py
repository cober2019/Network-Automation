"""Helper functions to search class-map configurations"""


def neigh_options(config):
    """Gets various neighbor configuration options"""

    next_hop = ["Yes" for k in dict.fromkeys(config) if k == "next-hop-self"]
    if not next_hop:
        next_hop = ["No"]

    reflector = ["Yes" for k in dict.fromkeys(config) if k == "route-reflector-client"]
    if not reflector:
        reflector = ["No"]

    soft_reconfig = [v for k, v in config.items() if k == "soft-reconfiguration"]
    if not soft_reconfig:
        soft_reconfig = ["No"]

    activate = ["Yes" for k in dict.fromkeys(config) if k == "activate"]
    if not reflector:
        activate = ["No"]

    return next_hop, reflector, soft_reconfig, activate

def neighbor(config):
    """Gets legacy neighbor config"""

    check_options = neigh_options(config)
    if config.get('remote-as'):
        print(f"{'Remote AS: ':>20}{config.get('remote-as')}")
    print(f"{'Neighbor: ':>20}{config.get('id')}")
    print(f"{'Next-Hop-Self: ':>20}{check_options[0][0]}")
    print(f"{'Route-Reflector: ':>20}{check_options[1][0]}")
    print(f"{'Soft-Reconfig: ':>20}{check_options[2][0]}")
    print("\n")

def address_family(config):
    """Gets AF neighbor config"""

    check_options = neigh_options(config)
    print(f"{'Neighbor: ':>20}{config.get('id', {}):<10}")
    print(f"{'Next-Hop-Self: ':>20}{check_options[0][0]}")
    print(f"{'Route-Reflector: ':>20}{check_options[1][0]}")
    print(f"{'Route-Map: ':>20}{config.get('route-map', {}).get('route-map-name', 'None'):<15}Direction: {config.get('route-map', {}).get('inout', 'None')}")
    print(f"{'Prefix-list: ':>20}{config.get('prefix-list', {}).get('prefix-list-name', 'None'):<15}Direction: {config.get('prefix-list', {}).get('inout', 'None')}")
    print(f"{'Activate: ':>20}{check_options[3][0]}\n")

def networks(config):
    """Gets Anetwork statementsg"""

    print(f"{'Network:':>20} {config.get('number', 'None'):>10}  Mask: {config.get('mask', 'None')}")

def redistribution(protocol, details):
    """Gets legacy redistribution config"""

    if protocol == "connected":
        print(f"{'Protocol:':>20} {protocol}")
        try:
            print(f"{'Route-map:':>20} {details.get('route-map', 'None')}"
                  f"{'Metric:':>20} {details.get('metric', 'None')}")
            print(f"{'----------':>20}")
        except AttributeError:
            pass
        print(f"{'----------':>20}")

    if protocol == "static":
        print(f"{'Protocol:':>20} {protocol} ")
        try:
            print(f"{'Route-map:':>20} {details.get('route-map', 'None')}"
                  f"{'Metric:':>20} {details.get('metric', 'None')}")
        except AttributeError:
            pass
        print(f"{'----------':>20}")

    if protocol == "ospf":
        print(f"{'Protocol:':>20} {protocol}  {details.get('id')}")
        try:
            print(f"{'Route-map:':>20} {details.get('non-vrf', {}).get('route-map', 'None')}"
                  f"{'Metric:':>20} {details.get('non-vrf', {}).get('metric', 'None')}")
        except AttributeError:
            pass
        print(f"{'----------':>20}")


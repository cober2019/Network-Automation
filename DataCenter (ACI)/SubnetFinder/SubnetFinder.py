"""Help program for locating subnets in ACI"""

import requests
import xml.etree.ElementTree as ET
import warnings

# Check and ignore unverfied http reequest
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def request_subnets(session, apic):
    """Request ACI subnets, checks response for vailidity"""

    root = None
    uri = f"https://{apic}/api/class/fvBD.xml?query-target=subtree"
    response = session.get(uri, verify=False)

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        print("Something went wrong. Please try again")

    return root


def get_subnets(session, apic):
    """Gets current gateways in ACI"""

    root = request_subnets(session, apic)
    unicast = []
    for gateway in root.iter("fvSubnet"):
        subnets = gateway.get("ip")
        unicast.append(subnets)

    total_unicast = len(unicast)

    return unicast, total_unicast, root


def apic_login() -> tuple:
    """Login into apic and request access policy configurations"""

    session = None
    print("Fabric Credentials:\n")
    apic = input("APIC: ")
    username = input("Username: ")
    password = input("Password: ")

    uri = f"https://{apic}/api/mo/aaaLogin.xml"
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    raw_data = f"""<!-- AAA LOGIN --> <aaaUser name="{username}" pwd="{password}"/>"""

    # APIC login, failed login or ivalid APIC will result in reprompting credentials.
    try:
        session = requests.Session()
        request = session.post(uri, data=raw_data, verify=False)
        response = request.text
        if response.rfind("FAILED local authentication") != -1 or response.rfind("Failed to parse login request") != -1:
            print("Login Failed, please verify credentials\n")
            apic_login()
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        print("Login Failed, please verify APIC IP\n")
        apic_login()

    return session, apic


def user_input(session, apic):
    """User inputs gatewy to search for"""

    gateways = get_subnets(session, apic)
    print("\n--------------------------------------|")
    print("ACI Subnet Finder---------------------|")
    print("--------------------------------------|\n")
    print(f"Total Fabric Subnets: {gateways[1]}")

    print("Enter gateway IP plus prefix length (ex. 1.1.1.1)\n")
    unicast_gateway = input("Please enter a gateway IP: ")
    find_gateways(unicast_gateway, gateways[2], session, apic)


def gateway_is_none(location, session, apic):
    """Check location of gateway, if None return to user input"""

    if location is None:
        print("Gateway not Found!")
        user_input(session, apic)


def find_gateways(unicast_gateway, root, session, apic):
    """Search for ACI Gateways and get configurations"""

    aps = []
    epgs = []
    l3Outs = []
    location, bridge_domain, uni_route, scope, unkwn_uni, tenant, bd_vrf = None, None, None, None, None, None, None

    # Locate subnet in ACI, get scope, map location
    for fvSubnet in root.iter("fvSubnet"):
        ip = fvSubnet.get("ip")
        if unicast_gateway in ip:
            location = fvSubnet.get("dn")
            scope = fvSubnet.get("scope")
            break

    # Check to see if gate in ACI, return to user input if location is None
    gateway_is_none(location, session, apic)

    # Find BD, check to see if unicast routing is enable and unkown unicast setting is
    for fvBD in root.iter("fvBD"):
        bds = fvBD.get("name")
        if location.rfind(bds) != -1:
            bridge_domain = bds
            uni_route = fvBD.get("unicastRoute")
            unkwn_uni = fvBD.get("unkMacUcastAct")

    # Find vrf associated with BD
    for fvRsCtx in root.iter("fvRsCtx"):
        vrf = fvRsCtx.get("tnFvCtxName")
        location = fvRsCtx.get("dn")
        if location.rfind(bridge_domain) != -1:
            bd_vrf = vrf

    # Find tenant, ap, and epgs, save to list
    for fvRtBd in root.iter("fvRtBd"):
        dn = fvRtBd.get("dn")
        if dn.rfind(bridge_domain) != -1:
            tenant = dn.split("/")[1].strip("tn-")
            aps.append(dn.split("/")[5].strip("ap-"))
            epgs.append(dn.split("/")[6].strip("epg-").strip("]"))

    # Find L3outs, save to list
    for fvRsBDToOut in root.iter("fvRsBDToOut"):
        dn = fvRsBDToOut.get("dn")
        if dn.rfind(bridge_domain) != -1:
            l3Outs.append(dn.split("/")[3].strip("rsBDToOut-"))

    # Join list created
    join_aps = ', '.join(aps)
    join_epgs = ', '.join(epgs)
    join_l3outs = ', '.join(l3Outs)

    # Print output using f-strings
    print(f"BD:\n + {bridge_domain}\nEnable:\n + {uni_route}\nScope:\n + {scope}\nUnkwn Uni:\n + {unkwn_uni}\n"
          f"Tenant:\n + {tenant}\nAPs:\n + {join_aps}\nEpgs:\n + {join_epgs}\nL3Outs:\n + {join_l3outs}\nVRF:\n + {bd_vrf}")

    # Return to user input
    user_input(session, apic)


if __name__ == '__main__':

    session_info = apic_login()
    user_input(session_info[0], session_info[1])


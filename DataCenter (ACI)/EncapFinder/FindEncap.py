"""Helper funtions to get information about ACI encapsulations"""

from os import system, name
import time
import ACI_Policies as GetPolicies
import requests
import warnings


def clear() -> None:
    """Clears terminal"""

    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')


def apic_login() -> None:
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
        r = session.post(uri, data=raw_data, verify=False)
        response = r.text
        if response.rfind("FAILED local authentication") != -1 or response.rfind("Failed to parse login request") != -1:
            print("Login Failed, please verify credentials\n")
            apic_login()
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
        print("Login Failed, please verify APIC IP\n")
        apic_login()

    # if authentication passes, collet access policy config, request encapsulation from user
    GetPolicies.vlan_pools(session, apic)
    GetPolicies.domains(session, apic)
    encap_selection(session, apic)


def encap_selection(session, apic) -> None:
    """Gets and prints mapped policies"""

    time.sleep(1)
    clear()

    print("\n")
    print("|-Target Encap--------------------|")
    print("|---------------------------------|")
    print("\n")

    vlan = input("Encap: ")

    # Configuration will be return in a tuple, index and joing tuples with newline
    pools = GetPolicies.map_policy_configurations(session, apic, vlan)

    print("\n")
    print("   Access Policy Details:\n")
    if pools[0]:
        print("     VLAN Pool(s): " + "\n                   ".join(pools[0]))
        print("\n")
    if pools[1]:
        print("     Domain(s):    " + "\n                   ".join(pools[1]))
        print("\n")
    if pools[2]:
        print("     AAEP(s):      " + "\n                   ".join(pools[2]))
        print("\n")
    if pools[3]:
        print("     Encap Loc:   " + "\n                   ".join(pools[3]))
        print("\n")
    if pools[4]:
        print("     Path Attach:  " + "\n                   ".join(pools[4]))
        print("\n")

    input("Hit Enter to Continue")
    clear()
    encap_selection(session, apic)


if __name__ == '__main__':

    apic_login()


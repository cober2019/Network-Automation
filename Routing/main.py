import xe_routing, asa_routing, nxos_routing
import connections
import traceback

def device_login() -> object:

    ip = input('IP: ')
    username = input('Username: ')
    password = input('Password: ')
    enable = input('Enable: ')
    
    if enable == '':
        enable = None

    if enable is None:
        netmiko_connection = connections.netmiko(host=ip,username=username,password=password)
    else:
        netmiko_connection = connections.netmiko_w_enable(host=ip,username=username,password=password,enable_pass=enable)
    
    if netmiko_connection[1] != False or netmiko_connection[0] is not None:
        pass
    else:
        print('\nLogin Failed\n')
        menu()

    return netmiko_connection[0]

def menu() -> None:

    print('\nXE-Routing Table\n')
    selection = input('1. XE-Routing\n2. ASA Routing\n3. NXOS Routing\n\nSelection: ')
    netmiko_connection = device_login()

    if selection == '1':
        route_obj = xe_routing.RoutingIos(netmiko_connection)
        [print(", ".join(i)) for i in route_obj.route_table]
        menu()
    elif selection == '2':
        route_obj = asa_routing.RoutingAsa(netmiko_connection)
        [print(", ".join(i)) for i in route_obj.route_table if None not in i]
        menu()
    elif selection == '3':
        route_obj = nxos_routing.RoutingNexus(netmiko_connection)
        [print(", ".join(i)) for i in route_obj.route_table]
        menu()
    else:
        print('Invalid Selection')
        menu()


if __name__ == '__main__':

    try:
        menu()
    except BaseException:
        print(f'\n\n\nSomething Is Really Wrong. Please submit an issue with the following log:\n')
        print(traceback.print_exc())
        menu()
    
    

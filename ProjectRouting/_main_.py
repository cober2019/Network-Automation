"""Helper tool for quering route table databases"""

from Database import DB_queries as DbQueries
from Software import NXOS, IOSXE, ASA

get_tables = DbQueries.get_db_tables_with_data()


def query_menu_options():

    while True:

        print("\nDB_Query Tool-------------\n")
        print("\nTable: %s\n" % get_tables[0])
        print("1. Search by protocol")
        print("2. Search by prefix")
        print("3. Search by metric")
        print("4. Search by AD")
        print("5. Search by Interface")
        print("6. Search by Tag")
        print("7. Full Table")
        print("8. Export to Excel\n")

        selection = input("Selection: ")
        print("\n")

        if selection == "1":

            if get_tables[0] == "Routing_ASA":

                DbQueries.print_protocols(get_tables[0])
                protocol = input("Protocol: ")
                print("\n")
                DbQueries.search_db_asa(protocol=protocol)

            elif get_tables[0] == "Routing_IOS_XE":
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.print_protocols(get_tables[0])
                protocol = input("Protocol: ")
                print("\n")
                DbQueries.search_db_ios(vrf=vrf, protocol=protocol)

            elif get_tables[0] == "Routing_Nexus":

                DbQueries.get_vdcs()
                vdc = input("VDC: ")
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.print_protocols(get_tables[0])
                protocol = input("Protocol: ")
                print("\n")
                DbQueries.search_db_nexus(vdc=vdc, vrf=vrf, protocol=protocol)

        elif selection == "2":
            if get_tables[0] == "Routing_ASA":

                prefix = input("Prefix: ")
                print("\n")
                DbQueries.search_db_asa(prefix=prefix)

            elif get_tables[0] == "Routing_IOS_XE":

                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                prefix = input("Prefix: ")
                print("\n")
                DbQueries.search_db_ios(vrf=vrf, prefix=prefix)

            elif get_tables[0] == "Routing_Nexus":

                DbQueries.get_vdcs()
                vdc = input("VDC: ")
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                prefix = input("Prefix: ")
                print("\n")
                DbQueries.search_db_nexus(vdc=vdc, vrf=vrf, prefix=prefix)

        elif selection == "3":

            if get_tables[0] == "Routing_ASA":

                metric = input("Metric: ")
                print("\n")
                DbQueries.search_db_asa(metric=metric)

            elif get_tables[0] == "Routing_IOS_XE":

                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                metric = input("Metric: ")
                print("\n")
                DbQueries.search_db_ios(vrf=vrf, metric=metric)

            elif get_tables[0] == "Routing_Nexus":

                DbQueries.get_vdcs()
                vdc = input("VDC: ")
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                metric = input("Metric: ")
                print("\n")
                DbQueries.search_db_nexus(vdc=vdc, vrf=vrf, metric=metric)

        elif selection == "4":

            if get_tables[0] == "Routing_ASA":
                DbQueries.get_admin_disatnces(get_tables[0])
                ad = input("AD: ")
                print("\n")
                DbQueries.search_db_asa(ad=ad)

            elif get_tables[0] == "Routing_IOS_XE":

                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.get_admin_disatnces(get_tables[0])
                ad = input("AD: ")
                print("\n")
                DbQueries.search_db_ios(vrf=vrf, ad=ad)

            elif get_tables[0] == "Routing_Nexus":

                DbQueries.get_vdcs()
                vdc = input("VDC: ")
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.get_admin_disatnces(get_tables[0])
                ad = input("AD: ")
                print("\n")
                DbQueries.search_db_nexus(vdc=vdc, vrf=vrf, ad=ad)

        elif selection == "5":

            if get_tables[0] == "Routing_ASA":

                DbQueries.print_routing_interfaces(table=get_tables[0])
                interface = input("Interface: ")
                print("\n")
                DbQueries.search_db_asa(interface=interface)

            elif get_tables[0] == "Routing_IOS_XE":

                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.print_routing_interfaces(table=get_tables[0])
                interface = input("Interface: ")
                print("\n")
                DbQueries.search_db_ios(vrf=vrf, interface=interface)

            elif get_tables[0] == "Routing_Nexus":

                DbQueries.get_vdcs()
                vdc = input("VDC: ")
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.print_routing_interfaces(table=get_tables[0])
                interface = input("Interface: ")
                print("\n")
                DbQueries.search_db_nexus(vdc=vdc, vrf=vrf, interface=interface)

        elif selection == "6":

            if get_tables[0] == "Routing_ASA":

                DbQueries.get_tags(table=get_tables[0])
                tag = input("Tag: ")
                print("\n")
                DbQueries.search_db_asa(tag=tag)

            elif get_tables[0] == "Routing_IOS_XE":

                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.get_tags(table=get_tables[0])
                tag = input("Tag: ")
                print("\n")
                DbQueries.search_db_ios(vrf=vrf, tag=tag)

            elif get_tables[0] == "Routing_Nexus":

                DbQueries.get_vdcs()
                vdc = input("VDC: ")
                DbQueries.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                DbQueries.get_tags(table=get_tables[0])
                tag = input("Tag: ")
                print("\n")
                DbQueries.search_db_nexus(vdc=vdc, vrf=vrf, tag=tag)

        elif selection == "7":
            if get_tables[0] == "Routing_ASA":
                DbQueries.view_routes_asa("Routing_ASA")
            elif get_tables[0] == "Routing_IOS_XE":
                DbQueries.view_routes_ios("Routing_IOS_XE")
            elif get_tables[0] == "Routing_Nexus":
                DbQueries.view_routes_nexus("Routing_Nexus")

        elif selection == "8":
            DbQueries.export_excel(get_tables[0])
        else:
            print("Invalid Selection")

        query_menu_options()


def main():

    print("Routing Tables Lookup Tool")
    print("\n1. Fetch new routing table\n2. Search existing table (Previous fetch)\n")
    selection = input("Selection: ")

    if selection == "1":

        print("\nOS Options\n")

        print("1. IOS XE")
        print("2. Nexus OS")
        print("3. ASA\n")

        selection = input("Selection: ")
        print("\n")

        device_ip = input("Device IP: ")
        username = input("Username: ")
        password = input("Password: ")

        enable_question = input("Enable Password(yes/no)? ").lower()

        if enable_question == "yes":
            same_as_username_password = input("Enable Password same as user password(yes/no)? ").lower()
            if same_as_username_password == "yes":
                if selection == "1":
                    IOSXE.RoutingIos(host=device_ip, username=username, password=password, enable=password)
                elif selection == "2":
                    NXOS.RoutingNexus(host=device_ip, username=username, password=password, enable=password)
                elif selection == "3":
                    ASA.RoutingAsa(host=device_ip, username=username, password=password, enable=password)

            elif same_as_username_password == "no":

                enable = input("Enable Password(yes/no)? ")

                if selection == "1":
                    IOSXE.RoutingIos(host=device_ip, username=username, password=password, enable=enable)
                elif selection == "2":
                    NXOS.RoutingNexus(host=device_ip, username=username, password=password, enable=enable)
                elif selection == "3":
                    ASA.RoutingAsa(host=device_ip, username=username, password=password, enable=enable)

        elif enable_question == "no":

            if selection == "1":
                IOSXE.RoutingIos(host=device_ip, username=username, password=password)
            elif selection == "2":
                NXOS.RoutingNexus(host=device_ip, username=username, password=password)
            elif selection == "3":
                ASA.RoutingAsa(host=device_ip, username=username, password=password)

        query_menu_options()

    elif selection == "2":

        if not get_tables:
            print("No routing table")
        else:
            query_menu_options()


if __name__ == '__main__':
    main()

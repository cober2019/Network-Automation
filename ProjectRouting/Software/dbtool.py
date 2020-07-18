import Database.DB_queries as db_queries
from Software import NXOS, IOSXE, ASA

if __name__ == '__main__':

    skip_login = input("Database populated? Press enter to skip.")
    print("\n")

    if skip_login != "":

        print("OS Options\n")

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
                    IOSXE.Routing_Ios(host=device_ip, username=username, password=password, enable=password)
                elif selection == "2":
                    NXOS.Routing_Nexus(host=device_ip, username=username, password=password, enable=password)
                elif selection == "3":
                    ASA.Routing_Asa(host=device_ip, username=username, password=password, enable=password)

            elif same_as_username_password == "no":

                enable = input("Enable Password(yes/no)? ")

                if selection == "1":
                    IOSXE.Routing_Ios(host=device_ip, username=username, password=password, enable=enable)
                elif selection == "2":
                    NXOS.Routing_Nexus(host=device_ip, username=username, password=password, enable=enable)
                elif selection == "3":
                    ASA.Routing_Asa(host=device_ip, username=username, password=password, enable=enable)

        elif enable_question == "no":

            if selection == "1":
                IOSXE.Routing_Ios(host=device_ip, username=username, password=password)
            elif selection == "2":
                NXOS.Routing_Nexus(host=device_ip, username=username, password=password)
            elif selection == "3":
                ASA.Routing_Asa(host=device_ip, username=username, password=password)

        db_class = db_queries.Routing_Datbases()

        while True:
            get_tables = db_queries.get_db_tables_with_data()
            if not get_tables:
                continue
            else:
                break
    else:
        db_class = db_queries.Routing_Datbases()
        get_tables = db_queries.get_db_tables_with_data()
        if not get_tables:
            print("No routing table")
        else:
            pass

    while True:

        print("\nDB_Query Tool-------------\n")
        print("\nTable: %s\n" % get_tables[0])
        print("1. Search by protocol")
        print("2. Search by prefix")
        print("3. Search by metric")
        print("4. Search by AD")
        print("5. Search by Interface")
        print("6. Search by Tag")
        print("7. Full Table\n")

        selection = input("Selection: ")
        print("\n")

        if selection == "1":

            if get_tables[0] == "Routing_ASA":

                db_class.get_protocols(get_tables[0])
                protocol = input("Protocol: ")
                print("\n")
                db_class.search_db_asa(context=None, protocol=protocol)

            elif get_tables[0] == "Routing_IOS_XE":
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_protocols(get_tables[0])
                protocol = input("Protocol: ")
                print("\n")
                db_class.search_db_ios(vrf=None, protocol=protocol)

            elif get_tables[0] == "Routing_Nexus":

                db_class.get_vdcs()
                vdc = input("VDC: ")
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_protocols(get_tables[0])
                protocol = input("Protocol: ")
                print("\n")
                db_class.search_db_nexus(vdc=vdc, vrf=vrf, protocol=protocol)

        elif selection == "2":
            if get_tables[0] == "Routing_ASA":

                prefix = input("Prefix: ")
                print("\n")
                db_class.search_db_asa(context=None, prefix=prefix)

            elif get_tables[0] == "Routing_IOS_XE":
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                prefix = input("Prefix: ")
                print("\n")
                db_class.search_db_ios(vrf=vrf, prefix=prefix)

            elif get_tables[0] == "Routing_Nexus":

                db_class.get_vdcs()
                vdc = input("VDC: ")
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                prefix = input("Prefix: ")
                print("\n")
                db_class.search_db_nexus(vdc=vdc, vrf=vrf, prefix=prefix)

        elif selection == "3":

            if get_tables[0] == "Routing_ASA":

                metric = input("Metric: ")
                print("\n")
                db_class.search_db_asa(context=None, metric=metric)

            elif get_tables[0] == "Routing_IOS_XE":

                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                metric = input("Metric: ")
                print("\n")
                db_class.search_db_ios(vrf=vrf, metric=metric)

            elif get_tables[0] == "Routing_Nexus":

                db_class.get_vdcs()
                vdc = input("VDC: ")
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                metric = input("Metric: ")
                print("\n")
                db_class.search_db_nexus(vdc=vdc, vrf=vrf, metric=metric)

        elif selection == "4":

            if get_tables[0] == "Routing_ASA":
                db_class.get_admin_disatnces(get_tables[0])
                ad = input("AD: ")
                print("\n")
                db_class.search_db_asa(context=None, ad=ad)

            elif get_tables[0] == "Routing_IOS_XE":

                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_admin_disatnces(get_tables[0])
                ad = input("AD: ")
                print("\n")
                db_class.search_db_ios(vrf=vrf, ad=ad)

            elif get_tables[0] == "Routing_Nexus":

                db_class.get_vdcs()
                vdc = input("VDC: ")
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_admin_disatnces(get_tables[0])
                ad = input("AD: ")
                print("\n")
                db_class.search_db_nexus(vdc=vdc, vrf=vrf, ad=ad)

        elif selection == "5":

            if get_tables[0] == "Routing_ASA":

                db_class.get_routing_interfaces(table=get_tables[0])
                interface = input("Interface: ")
                print("\n")
                db_class.search_db_asa(context=None, interface=interface)

            elif get_tables[0] == "Routing_IOS_XE":

                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_routing_interfaces(table=get_tables[0])
                interface = input("Interface: ")
                print("\n")
                db_class.search_db_ios(vrf=vrf, interface=interface)

            elif get_tables[0] == "Routing_Nexus":

                db_class.get_vdcs()
                vdc = input("VDC: ")
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_routing_interfaces(table=get_tables[0])
                interface = input("Interface: ")
                print("\n")
                db_class.search_db_nexus(vdc=vdc, vrf=vrf, interface=interface)

        elif selection == "6":

            if get_tables[0] == "Routing_ASA":

                db_class.get_tags(table=get_tables[0])
                tag = input("Tag: ")
                print("\n")
                db_class.search_db_asa(context=None, tag=tag)

            elif get_tables[0] == "Routing_IOS_XE":

                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_tags(table=get_tables[0])
                tag = input("Tag: ")
                print("\n")
                db_class.search_db_ios(vrf=vrf, tag=tag)

            elif get_tables[0] == "Routing_Nexus":

                db_class.get_vdcs()
                vdc = input("VDC: ")
                db_class.get_vrfs(get_tables[0])
                vrf = input("VRF: ")
                db_class.get_tags(table=get_tables[0])
                tag = input("Tag: ")
                print("\n")
                db_class.search_db_nexus(vdc=vdc, vrf=vrf, tag=tag)

        elif selection == "7":
            if get_tables[0] == "Routing_ASA":
                db_class.view_routes_asa()
            elif get_tables[0] == "Routing_IOS_XE":
                db_class.view_routes_ios()
            elif get_tables[0] == "Routing_Nexus":
                db_class.view_routes_nexus()

        else:
            print("Invalid Selection")









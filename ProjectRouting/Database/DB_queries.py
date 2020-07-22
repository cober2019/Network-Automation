import sqlite3
from typing import Union, Any, List
import re

mydb = sqlite3.connect("Routing")
cursor = mydb.cursor()
cursor_2 = mydb.cursor()
route_tables = []


def get_db_tables_with_data() -> list:

    """Gets database tables. If table is empty pass"""
    full_dbs = []
    database_class = Routing_Datbases()
    get_tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    for table in get_tables:
        check_table_rows = cursor_2.execute('SELECT count(*) FROM {}'.format(table[0]))
        for row in check_table_rows:
            if row[0] == 0:
                pass
            else:
                full_dbs.append(table[0])

    return full_dbs

def query_db_asa(**attributes: Union[str, List[int]]) -> None:
    """Find databse entries with arbitrary routing attributes. Checks for single hope metric or multi path
    using \',\' between metrics"""

    get_table_rows = [row for row in cursor.execute('SELECT count(*) FROM Routing_ASA')]
    if get_table_rows[0][0] == 0:
        print("No Routes In Table")
    else:
        context_query = cursor.execute('SELECT * FROM Routing_ASA WHERE context=?', ("None", ))

        matched_query = 0
        for row in context_query:

            # Find single metric route

            if attributes["query"] == row[attributes["index"]]:
                print("Context: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                      "Metric(s): {}\nTag: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                        row[7]))

                matched_query = matched_query + 1

            else:
                pass

            # Find routes with multihop. Sperator is ","

            if attributes["query"] in row[attributes["index"]]:
                if "," in row[attributes["index"]]:

                    if attributes["query"] in re.findall(r'^' + attributes["query"] + '(?=,)', row[attributes["index"]]) \
                            or \
                       attributes["query"] in re.findall(r'(?<=,)' + attributes["query"] + '', row[attributes["index"]]):

                       print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7]))
                       matched_query = matched_query + 1

                    if attributes["query"] in re.findall(r'^' + attributes["query"] + '(?=,)', row[attributes["index"]]) \
                            or \
                       attributes["query"] in re.findall(r'(?<=,)' + attributes["query"] + '', row[attributes["index"]]):

                       print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7]))
                       matched_query = matched_query + 1
                else:
                    pass

        print("Total Routes: %s" % matched_query)


def query_db_ios(**attributes: Union[str, List[int]]) -> None:
    """Find databse entries with arbitrary routing attributes"""

    get_table_rows = [row for row in cursor.execute('SELECT count(*) FROM Routing_IOS_XE')]
    if get_table_rows[0][0] == 0:
        print("No Routes In Table")
    else:
        vrf_query = cursor.execute('SELECT * FROM Routing_IOS_XE WHERE vrf=?', (attributes["vrf"],))

        matched_query = 0
        for row in vrf_query:

            # Find single metric route

            if attributes["query"] == row[attributes["index"]]:
                print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                      "Metric(s): {}\nTag: {}\nCDP neighbor(s): {}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                        row[7], row[8]))

                matched_query = matched_query + 1

            else:
                pass

            # Find routes with multihop. Sperator is ","

            if attributes["query"] in row[attributes["index"]]:
                if "," in row[attributes["index"]]:

                    if attributes["query"] in re.findall(r'^' + attributes["query"] + '(?=,)', row[attributes["index"]]) \
                            or \
                       attributes["query"] in re.findall(r'(?<=,)' + attributes["query"] + '', row[attributes["index"]]):

                       print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\nCDP neighbor(s): {}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7], row[8]))
                       matched_query = matched_query + 1

                    if attributes["query"] in re.findall(r'^' + attributes["query"] + '(?=,)', row[attributes["index"]]) \
                            or \
                       attributes["query"] in re.findall(r'(?<=,)' + attributes["query"] + '', row[attributes["index"]]):

                       print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\nCDP neighbor(s): {}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7], row[8]))
                       matched_query = matched_query + 1
                else:
                    pass

        print("Total Routes: %s" % matched_query)


def query_db_nexus(**attributes: Union[str, List[int]]) -> None:
    """Find databse entries with arbitrary routing attributes"""

    get_table_rows = [row for row in cursor.execute('SELECT count(*) FROM Routing_Nexus')]
    if get_table_rows[0][0] == 0:
        print("No Routes In Table")
    else:
        vdc_query = cursor.execute('SELECT * FROM Routing_Nexus WHERE vdc=?', (attributes["vdc"],))

        matched_query = 0
        for row in vdc_query:

            # Find single metric route

            if attributes["vrf"] == row[1] and attributes["query"] == row[attributes["index"]]:
                print("VDC: {}\nVRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                    "Metric(s): {}\nTag: {}\nCDP neighbor(s): {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                      row[7], row[8], row[9]))

                matched_query = matched_query + 1

            else:
                pass

            # Find routes with multihop. Sperator is ","

            if attributes["query"] in row[attributes["index"]]:
                if "," in row[attributes["index"]]:

                    if attributes["query"] in re.findall(r'^' + attributes["query"] + '(?=,)', row[attributes["index"]]) \
                            or \
                       attributes["query"] in re.findall(r'(?<=,)' + attributes["query"] + '', row[attributes["index"]]):

                       print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\nCDP neighbor(s): {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7], row[8]))

                       matched_query = matched_query + 1

                    if attributes["query"] in re.findall(r'^' + attributes["query"] + '(?=,)', row[attributes["index"]]) \
                            or \
                       attributes["query"] in re.findall(r'(?<=,)' + attributes["query"] + '', row[attributes["index"]]):

                       print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\nCDP neighbor(s): {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7], row[8]))

                       matched_query = matched_query + 1
                else:
                    pass

        print("Total Routes: %s" % matched_query)


class Routing_Datbases():

    mydb = sqlite3.connect("Routing")

    def __init__(self):

        # Initialize class methods to get database tables, store as a module attribute
        self.get_tables_names_ios()
        self.get_tables_names_nexus()

    def get_tables_names_ios(self):
        """Get database table which are the routing tables"""

        try:
            for row in cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\''):
                route_tables.append(row[0])
        except sqlite3.OperationalError:
            pass

    def get_tables_names_nexus(self):
        """Get database table which are the routing tables"""

        try:
            for row in cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\''):
                route_tables.append(row[0])
        except sqlite3.OperationalError:
            pass

    @staticmethod
    def view_routes_asa():
        """View all database entries"""

        for table in route_tables:
            get_table_rows = [row for row in cursor.execute('SELECT count(*) FROM {}'.format(table))]
            if get_table_rows[0][0] == 0:
                continue
            else:
                print("\nRouting Table: " + table + "\n")
                print("__________________" + "\n")
                query = cursor.execute('SELECT * FROM {}'.format(table))
                for row in query:
                        print("Context: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

                print("Total Routes: %s" % get_table_rows[0][0])

    @staticmethod
    def view_routes_ios():
        """View all database entries"""

        for table in route_tables:
            get_table_rows = [row for row in cursor.execute('SELECT count(*) FROM {}'.format(table))]
            if get_table_rows[0][0] == 0:
                continue
            else:
                print("\nRouting Table: " + table + "\n")
                print("__________________" + "\n")
                query = cursor.execute('SELECT * FROM {}'.format(table))
                for row in query:
                        print("VRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

                print("Total Routes: %s" % get_table_rows[0][0])

    @staticmethod
    def view_routes_nexus():
        """View all database entries"""

        for table in route_tables:
            get_table_rows = [row for row in cursor.execute('SELECT count(*) FROM {}'.format(table))]
            if get_table_rows[0][0] == 0:
                continue
            else:
                print("\nRouting Table: " + table + "\n")
                print("__________________" + "\n")
                query = cursor.execute('SELECT * FROM {}'.format(table))
                for row in query:
                        print("VDC: {}\nVRF: {}\nPrefix: {}\nProtocol: {}\nAdmin-Distance: {}\nHop(s): {}\nOut-Interface(s): {}\n"
                            "Metric(s): {}\nTag: {}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                                              row[7], row[8]))

                print("Total Routes: %s" % get_table_rows[0][0])


    def search_db_asa(self, context: str = None, **attributes: str) -> None:
        """Find databse entries by artbitrary attribute using **attributes (kwargs)
                                vrf, admin-distance, metric, prefix, next-hop, tag"""

        # Create variables from **attributes (**kwargs). Pass on KeyErrors which is when the keyword argument
        # wasn't passed

        if context is None or "":
            context = "None"
        else:
            pass

        try:
            prefix = attributes["prefix"]
        except  KeyError:
            pass

        try:
            protocol = attributes["protocol"]
        except  KeyError:
            pass

        try:
            metric = attributes["metric"]
        except  KeyError:
            pass

        try:
            ad = attributes["ad"]
        except  KeyError:
            pass

        try:
            tag = attributes["tag"]
        except  KeyError:
            pass

        try:
            interface = attributes["interface"]
        except  KeyError:
            pass

        # Check to see if the argument has been passed, call db_query with args and db index of the query argument

        try:
            if attributes["protocol"]:
                query_db_asa(context=context, query=protocol, index=2)
        except KeyError:
            pass

        try:
            if attributes["prefix"]:
                query_db_asa(context=context, query=prefix, index=1)
        except KeyError:
            pass

        try:
            if attributes["metric"]:
                query_db_asa(context=context, query=metric, index=6)
        except KeyError:
            pass

        try:
            if attributes["ad"]:
                query_db_asa(context=context, query=ad, index=3)
        except KeyError:
            pass

        try:
            if attributes["tag"]:
                query_db_asa(context=context, query=tag, index=7)
        except KeyError:
            pass

        try:
            if attributes["interface"]:
                query_db_asa(context=context, query=interface, index=5)
        except KeyError:
            pass

    def search_db_ios(self, vrf: str = None, **attributes: str) -> None:
        """Find databse entries by artbitrary attribute using **attributes (kwargs)
                                vrf, admin-distance, metric, prefix, next-hop, tag"""

        # Create variables from **attributes (**kwargs). Pass on KeyErrors which is when the keyword argument
        # wasn't passed

        if vrf is None or vrf  == "":
            vrf = "global"
        else:
            pass

        try:
            prefix = attributes["prefix"]
        except  KeyError:
            pass

        try:
            protocol = attributes["protocol"]
        except  KeyError:
            pass

        try:
            metric = attributes["metric"]
        except  KeyError:
            pass

        try:
            ad = attributes["ad"]
        except  KeyError:
            pass

        try:
            tag = attributes["tag"]
        except  KeyError:
            pass

        try:
            interface = attributes["interface"]
        except  KeyError:
            pass

        # Check to see if the argument has been passed, call db_query with args and db index of the query argument

        try:
            if attributes["protocol"]:
                query_db_ios(vrf=vrf, query=protocol, index=2)
        except KeyError:
            pass

        try:
            if attributes["prefix"]:
                query_db_ios(vrf=vrf, query=prefix, index=1)
        except KeyError:
            pass

        try:
            if attributes["metric"]:
                query_db_ios(vrf=vrf, query=metric, index=6)
        except KeyError:
            pass

        try:
            if attributes["ad"]:
                query_db_ios(vrf=vrf, query=ad, index=3)
        except KeyError:
            pass

        try:
            if attributes["tag"]:
                query_db_ios(vrf=vrf, query=tag, index=7)
        except KeyError:
            pass

        try:
            if attributes["interface"]:
                query_db_ios(vrf=vrf, query=interface, index=5)
        except KeyError:
            pass

    def search_db_nexus(self, vdc: str = None, vrf: str = None, **attributes: str) -> None:
        """Find databse entries by artbitrary attribute using **attributes (kwargs)
                                vrf, admin-distance, metric, prefix, next-hop, tag"""

        if vrf is None or vrf == "":
            vrf = "default"
        else:
            pass

        # Create variables from **attributes (**kwargs)

        try:
            prefix = attributes["prefix"]
        except  KeyError:
            pass

        try:
            protocol = attributes["protocol"]
        except  KeyError:
            pass

        try:
            metric = attributes["metric"]
        except  KeyError:
            pass

        try:
            ad = attributes["ad"]
        except  KeyError:
            pass

        try:
            tag = attributes["tag"]
        except  KeyError:
            pass

        try:
            interface = attributes["interface"]
        except  KeyError:
            pass


        # Check to see if the argument has been passed, call db_query with args and db index of the query argument

        try:
            if attributes["protocol"]:
                query_db_nexus(vdc=vdc, vrf=vrf, query=protocol, index=3)
        except KeyError:
            pass

        try:
            if attributes["prefix"]:
                query_db_nexus(vdc=vdc, vrf=vrf, query=prefix, index=2)
        except KeyError:
            pass

        try:
            if attributes["metric"]:
                query_db_nexus(vdc=vdc, vrf=vrf, query=metric, index=7)
        except KeyError:
            pass

        try:
            if attributes["ad"]:
                query_db_nexus(vdc=vdc, vrf=vrf, query=ad, index=4)
        except KeyError:
            pass

        try:
            if attributes["tag"]:
                query_db_nexus(vdc=vdc, vrf=vrf, query=tag, index=8)
        except KeyError:
            pass

        try:
            if attributes["interface"]:
                query_db_nexus(vdc=vdc, vrf=vrf, query=interface, index=6)
        except KeyError:
            pass

    def get_vrfs(self, table: str) -> None:
        """Gets VRFs from the device. Databse default is "global"""

        vrf = {}
        get_vrfs = cursor.execute('SELECT vrf FROM {}'.format(table))

        for i in get_vrfs:
            vrf[i] = None

        print("\nVRFs ---------\n")
        if len(vrf) == 0:
            print("\nPress enter to use global")
        else:
            for k in vrf.keys():
                print("+ " + k[0])
            print("\n")

    def get_vdcs(self):
        """Gets VDCs from the device table"""

        vdc = {}
        get_vdcs = cursor.execute('SELECT vdc FROM Routing_Nexus')
        for i in get_vdcs:
            vdc[i] = None

        print("\nVDCs ---------\n")
        if len(vdc) == 0:
            pass
        else:
            for k in vdc.keys():
                print("+ " + k[0])
            print("\n")

    def get_routing_interfaces(self, table: str = None) -> dict:
        """Gets routing interfaces from table"""

        interfaces = {}
        get_interfaces = cursor.execute('SELECT interfaces FROM {}'.format(table))
        for row in get_interfaces:
            if ", " in row[0]:
                split_interfaces = row[0].split(", ")
                for i in split_interfaces:
                    interfaces[i[0]] = None
            else:
                interfaces[row] = None

        return interfaces

    def print_routing_interfaces(self, table: str = None) -> None:
        """Gets routing interfaces from table, prints"""

        interfaces = self.get_routing_interfaces(table=table)

        print("\nRouting Interfaces ---------\n")
        if len(interfaces) == 0:
            pass
        else:
            for k in interfaces.keys():
                if len(k[0]) < 2 or "None" in k[0]:
                    pass
                else:
                    print("+ " + k[0])
            print("\n")

    def get_tags(self, table: str = None) -> None:
        """Gets tags from the the routing table"""

        tag = {}
        get_tags = cursor.execute('SELECT tag FROM {}'.format(table))
        for i in get_tags:
            tag[i] = None

        print("\nRoute Tags ---------\n")
        if len(tag) == 0:
            pass
        else:
            for k in tag.keys():
                print("+ " + k[0])
            print("\n")

    def get_admin_disatnces(self, table: str = None) -> None:
        """Gets administrative distance from the routing table"""

        ad = {}
        get_ads = cursor.execute('SELECT admin_distance FROM {}'.format(table))
        for i in get_ads:
            ad[i] = None

        print("\nAdmin Distances ---------\n")
        if len(ad) == 0:
            pass
        else:
            for k in ad.keys():
                print("+ " + k[0])
            print("\n")

    def get_protocols(self, table: str = None) -> None:
        """Gets route protocol with types from the the routing table"""

        protocol = {}
        get_protocol = cursor.execute('SELECT protocol FROM {}'.format(table))
        for i in get_protocol:
            protocol[i] = None

        print("\nProtocols ---------\n")
        if len(protocol) == 0:
            pass
        else:
            for k in protocol.keys():
                if "None" in k[0]:
                    pass
                else:
                    print("+ " + k[0])
            print("\n")


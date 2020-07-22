import sqlite3
import Abstract
from typing import Union, Any, List, Optional, cast

mydb = sqlite3.connect("Routing")
cursor = mydb.cursor()

def delete_table_nexus():
    """Deletes existing database table Routing_Nexus"""

    try:
        cursor.execute('''DROP TABLE Routing_Nexus''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def delete_table_ios_xe():
    """Deletes existing database table Routing_IOS_XE"""

    try:
        cursor.execute('''DROP TABLE Routing_IOS_XE''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def delete_table_asa():
    """Deletes existing database table Routing_ASA"""

    try:
        cursor.execute('''DROP TABLE Routing_ASA''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass

def db_table_cleanup(f):
    """Decorator for database table cleanup"""

    def db_check(self):

        funtion = None

        if f.__name__ == "create_database_table_nexus":
            delete_table_nexus()
            funtion = f(self)
        elif f.__name__ == "create_database_table_ios_xe":
            delete_table_ios_xe()
            funtion = f(self)
        elif f.__name__ == "create_database_table_asa":
            delete_table_asa()
            funtion = f(self)

        return funtion
    return db_check

class RoutingDatabase(Abstract.Database):
    """Class of methods performs database funtions:
                                Creates tables in database
                                Inserts rows into database tables"""

    def __init__(self):

        self.create_database_table_nexus()
        self.create_database_table_ios_xe()
        self.create_database_table_asa()

    @db_table_cleanup
    def create_database_table_nexus(self):

        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_Nexus (vdc, vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag, ldp)''')
        mydb.commit()

    @db_table_cleanup
    def create_database_table_ios_xe(self):

        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_IOS_XE (vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag, ldp)''')
        mydb.commit()

    @db_table_cleanup
    def create_database_table_asa(self):

        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_ASA (context, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag)''')
        mydb.commit()

    def db_update_nexus(self, vdc: str, vrf: str,  prefix: str, protocol: str, admin_distance: str, nexthops: str, interfaces: str, metric: str, tag: str, ldp_neigh: str) -> None:

        cursor.execute("INSERT INTO Routing_Nexus VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                  (vdc, vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag, ldp_neigh))
        mydb.commit()

    def db_update_ios_xe(self, vrf: str, prefix: str, protocol: str, admin_distance: str, nexthops: str, interfaces: str, metric: str, tag: str, ldp_neigh: str) -> None:

        tag =None

        cursor.execute("INSERT INTO Routing_IOS_XE VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                  (vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag, ldp_neigh))
        mydb.commit()

    def db_update_asa(self, vrf: str,  prefix: str, protocol: str, admin_distance: str, nexthops: str, interfaces: str, metric: str, tag: str) -> None:

        cursor.execute("INSERT INTO Routing_ASA VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                  (vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag))
        mydb.commit()
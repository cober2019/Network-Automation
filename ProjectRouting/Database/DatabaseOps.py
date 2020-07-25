import sqlite3

mydb = sqlite3.connect("Routing")
cursor = mydb.cursor()


def delete_table_nexus() -> None:
    """Deletes existing database table Routing_Nexus"""

    try:
        cursor.execute('''DROP TABLE Routing_Nexus''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass


def delete_table_ios_xe() -> None:
    """Deletes existing database table Routing_IOS_XE"""

    try:
        cursor.execute('''DROP TABLE Routing_IOS_XE''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass


def delete_table_asa() -> None:
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


def update_ldp_neighbors(table: str = None, value: str = None, ip_address: str = None) -> None:
    """Deletes existing database table Routing_Nexus"""

    try:
        cursor.execute("UPDATE {} SET ldp=? ipaddress=?".format(table), (value, ip_address, ))
        mydb.commit()
    except sqlite3.OperationalError:
        pass


def db_update_nexus(vdc: str, vrf: str, prefix: str, protocol: str, admin_distance: str, nexthops: str,
                    interfaces: str, metric: str, tag: str = None) -> None:

    cursor.execute("INSERT INTO Routing_Nexus VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                   (vdc, vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag))
    mydb.commit()


def db_update_ios_xe(vrf: str, prefix: str, protocol: str, admin_distance: str, nexthops: str, interfaces: str,
                     metric: str, tag: str) -> None:

    tag = "None"

    cursor.execute("INSERT INTO Routing_IOS_XE VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                   (vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag))
    mydb.commit()


def db_update_asa(vrf: str, prefix: str, protocol: str, admin_distance: str, nexthops: str,
                  interfaces: str, metric: str, tag: str) -> None:
    cursor.execute("INSERT INTO Routing_ASA VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                   (vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag))
    mydb.commit()


class RoutingDatabase:
    """Class of methods performs database funtions:
                                Creates tables in database
                                Inserts rows into database tables"""

    def __init__(self):
        self.create_database_table_nexus()
        self.create_database_table_ios_xe()
        self.create_database_table_asa()

    @db_table_cleanup
    def create_database_table_nexus(self) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_Nexus (vdc, vrf, prefix, protocol, admin_distance, nexthops, 
        interfaces, metric, tag)''')
        mydb.commit()

    @db_table_cleanup
    def create_database_table_ios_xe(self) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_IOS_XE (vrf, prefix, protocol, admin_distance, nexthops, interfaces, 
        metric, tag)''')
        mydb.commit()

    @db_table_cleanup
    def create_database_table_asa(self) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_ASA (context, prefix, protocol, admin_distance, nexthops, interfaces, 
        metric, tag)''')
        mydb.commit()

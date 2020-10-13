import sqlite3


def delete_table_nexus(mydb, cursor) -> None:
    """Deletes existing database table Routing_Nexus"""

    try:
        cursor.execute('''DROP TABLE Routing_Nexus''')
        mydb.commit()
    except sqlite3.OperationalError:
        pass


def delete_table_ios_xe(mydb, cursor) -> None:
    """Deletes existing database table Routing_IOS_XE"""

    try:
        cursor.execute('''DROP TABLE Routing_IOS_XE''')
        mydb.commit()
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass


def delete_table_asa(mydb, cursor) -> None:
    """Deletes existing database table Routing_ASA"""

    try:
        cursor.execute('''DROP TABLE Routing_ASA''')
        mydb.commit()
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass


def db_table_cleanup(f):
    """Decorator for database table cleanup"""

    def db_check(self, mydb, cursor):

        funtion = None

        if f.__name__ == "create_database_table_nexus":
            delete_table_nexus(mydb, cursor)
            funtion = f(self, mydb, cursor)
        elif f.__name__ == "create_database_table_ios_xe":
            delete_table_ios_xe(mydb, cursor)
            funtion = f(self, mydb, cursor)
        elif f.__name__ == "create_database_table_asa":
            delete_table_asa(mydb, cursor)
            funtion = f(self, mydb, cursor)

        return funtion

    return db_check


class RoutingDatabase:
    """Class of methods performs database funtions:
                                Creates tables in database
                                Inserts rows into database tables"""

    def __init__(self, mydb, conn):
        self.create_database_table_nexus(mydb, conn)
        self.create_database_table_ios_xe(mydb, conn)
        self.create_database_table_asa(mydb, conn)

    @db_table_cleanup
    def create_database_table_nexus(self, mydb, cursor) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_Nexus (vdc, vrf, prefix, protocol, admin_distance, nexthops, 
        interfaces, metric, tag, age)''')
        mydb.commit()

    @db_table_cleanup
    def create_database_table_ios_xe(self, mydb, cursor) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_IOS_XE (vrf, prefix, protocol, admin_distance, metric, nexthops, 
        interfaces, tag, age)''')
        mydb.commit()

    @db_table_cleanup
    def create_database_table_asa(self, mydb, cursor) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_ASA (context, prefix, protocol, admin_distance, nexthops, interfaces, 
        metric, tag, age)''')
        mydb.commit()

    def db_update_nexus(self, mydb, cursor, vdc=None, vrf=None, prefix=None, protocol=None, admin_distance=None,
                        nexthops=None, interfaces=None, metric=None, age=None, tag=None) -> None:

        cursor.execute("INSERT INTO Routing_Nexus VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                       (vdc, vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag, age))
        mydb.commit()

    def db_update_ios_xe(self, mydb, cursor, vrf=None, prefix=None, protocol=None, admin_distance=None, nexthops=None,
                         interfaces=None, metric=None, age=None, tag=None) -> None:

        cursor.execute("INSERT INTO Routing_IOS_XE VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                       (vrf, prefix, protocol, admin_distance, metric, nexthops, interfaces, tag, age))
        mydb.commit()

    def db_update_asa(self, mydb, cursor, vrf=None, prefix=None, protocol=None, admin_distance=None, nexthops=None,
                      interfaces=None, metric=None, age=None, tag=None) -> None:

        cursor.execute("INSERT INTO Routing_ASA VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                       (vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag, age))
        mydb.commit()


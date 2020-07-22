from abc import ABC, abstractmethod


class Routing(ABC):
    """Routing table blueprint"""

    @abstractmethod
    def initialize_class_methods(self):
        def find_prefix():
            pass
        def parse_global_routing_entries():
            pass
        def parse_routing_entries_with_vrfs(vrfs):
            pass
        pass

    @abstractmethod
    def slash_ten_and_up(self):
        def outgoing_interfaces():
            pass
        def find_metric():
            pass
        pass

    @abstractmethod
    def slash_nine_and_below(self):
        def outgoing_interfaces():
            pass
        def find_metric():
            pass
        pass

    @abstractmethod
    def no_mask(self):
        def outgoing_interfaces():
            pass
        def find_metric():
            pass
        pass

    @abstractmethod
    def protocols_and_metrics(self):
        pass
    
    @abstractmethod
    def neighbors(self):
        def db_outgoing_ints():
            pass
        def parse_cdp():
            pass
        def parse_lldp():
            pass
        pass
    
    @abstractmethod
    def routes_unpacked(self):
        pass

    @abstractmethod
    def database(self):
        pass

    @property
    @abstractmethod
    def host(self):
        pass

    @property
    @abstractmethod
    def host(self, host: str):
        pass

    @property
    @abstractmethod
    def username(self):
        pass

    @property
    @abstractmethod
    def username(self, username: str):
        pass

    @property
    @abstractmethod
    def password(self):
        pass

    @property
    @abstractmethod
    def password(self, password: str):
        pass

    @property
    @abstractmethod
    def routing(self):
        pass


class Database(ABC):
    """This class's purpose is informational

    Database Columns

    vrf, prefix, protocol, admin_distance, nexthops, interfaces, metric, tag"""

    @abstractmethod
    def create_database_table_nexus(self):
        pass

    @abstractmethod
    def create_database_table_ios_xe(self):
        pass

    @abstractmethod
    def create_database_table_asa(self):
        pass

    @abstractmethod
    def db_update_nexus(self):
        pass

    @abstractmethod
    def db_update_ios_xe(self):
        pass

    @abstractmethod
    def db_update_asa(self):
        pass

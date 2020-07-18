from abc import ABC, abstractmethod


class Routing(ABC):
    """Routing table blueprint"""

    @abstractmethod
    def initialize_class_methods(self):
        pass

    @abstractmethod
    def slash_ten_and_up(self):
        pass

    @abstractmethod
    def slash_nine_and_below(self):
        pass

    @abstractmethod
    def no_mask(self):
        pass

    @abstractmethod
    def protocols_and_metrics(self):
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
    """This class's purpose is informational"""

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

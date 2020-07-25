from abc import ABC, abstractmethod


class Routing(ABC):
    """Routing table blueprint"""

    @abstractmethod
    def initialize_class_methods(self):
        pass

    @abstractmethod
    def slash_ten_and_up(self, routing_entry):
        pass

    @abstractmethod
    def slash_nine_and_below(self, routing_entry):
        pass

    @abstractmethod
    def no_mask(self, routing_entry):
        pass

    @abstractmethod
    def protocols_and_metrics(self, routing_entry):
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

    @abstractmethod
    def host(self):
        pass

    @property
    @abstractmethod
    def username(self):
        pass

    @property
    @abstractmethod
    def username(self):
        pass

    @property
    @abstractmethod
    def password(self):
        pass

    @property
    @abstractmethod
    def password(self):
        pass

    @property
    @abstractmethod
    def routing(self):
        pass

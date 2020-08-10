from abc import ABC, abstractmethod


class Routing(ABC):

    @abstractmethod
    def device_login(self):
        pass

    @abstractmethod
    def _find_prefix(self, routing_entry):
        pass

    @abstractmethod
    def _get_protocol(self, routing_entry):
        pass

    @abstractmethod
    def _route_breakdown(self, routing_entry):
        pass

    @abstractmethod
    def _write_to_dict(self, route_details):
        pass

    @abstractmethod
    def database(self):
        pass




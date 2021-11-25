"""A class that gets and parse RIB data using ietf-routing yang model"""


import collections
import time
import requests
import json
import warnings
from json.decoder import JSONDecodeError

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers = {"Content-Type": 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

def is_instance(list_or_dict):
    """Converts dictionary object to list"""

    if isinstance(list_or_dict, list):
        make_list = list_or_dict
    else:
        make_list = [list_or_dict]

    return make_list


class Routing:

    def __init__(self):

        self.routes = collections.defaultdict(list)
        self.previous_routes = []
        self._protocols = []
        self._flapping_routes = collections.defaultdict(list)

    def get_routing_info(self, ip, port, username, password):
        """Creates NETCONF Session and initiate getting the current RIB and protocols"""

        self.routes = collections.defaultdict(list)

        try:
            response = requests.get(f"https://{ip}:{port}/restconf/data/ietf-routing:routing-state", headers=headers, verify=False, auth=(username, password))
            interface_data = json.loads(response.text).get('ietf-routing:routing-state', {}).get('routing-instance', {})
            for i in interface_data:
                for k, v in i.items():
                    if k == 'routing-protocols' and not self._protocols:
                        # Get routing protocols, vrfs, interfaces
                        [self._routing_protocols(protocol, i.get('name'), i.get('type'), i.get('interfaces', {})) for protocol in is_instance(v.get('routing-protocol'))]

                    elif k == 'ribs':

                        #Get routes for each rib instance
                        [list((self._store_routes(rib.get('name'), rib.get('address-family'), route) for route in
                                is_instance(rib.get('routes', {}).get('route', {})))) for rib in v.get('rib')]
                                
        except (JSONDecodeError, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,UnboundLocalError, AttributeError):
            pass

        #Get difference between last rib polled and new rib polled
        self._get_rib_diff()

        #Assign variable for next poll rib comparisons
        self.previous_routes = self.routes

        return self._protocols, self.routes, self._flapping_routes

    def _get_rib_diff(self):
        """Get route diffrence between current and previous rib tables"""

        if self.previous_routes:
            new_dest = [list((i for i in v)) for v in self.routes.values()][0]
            old_dest = [list((i for i in v)) for v in self.previous_routes.values()][0]

            # If routes have been added to the rib, this code will be used
            if len(old_dest) < len(new_dest):
                self._new_entries(new_dest, old_dest)
            elif len(old_dest) > len(new_dest):
                self._removed_entries(new_dest, old_dest)

    def _new_entries(self, new_dest, old_dest):
        """Used if the current rib table is larger then the previous table"""

        for new_routes in new_dest:
            for old_routes in old_dest:
                # Create status variable. Only change if the i or top level variable match the second level loop variable, h
                status = 0
                if new_routes.get('dest_prefix') == old_routes.get('dest_prefix'):
                    status = 1
                    break
                else:
                    continue

            # If status is still zero at the end of the loop than the is new , and we will modify the dictionary
            # to reflect the status
            if status == 0:
                new_routes.update({'status': 'green'})
                new_routes.update({'time': f'{time.strftime("%H")}:{time.strftime("%M")}:{time.strftime("%S")}'})
                self._flapping_routes['routes'].append(new_routes)

    def _removed_entries(self, new_dest, old_dest):
        """Used if the current rib table is smaller then the previous table"""

        for old_routes in old_dest:
            for new_routes in new_dest:
                # Create status variable. Only change if the i or top level variable match the second level loop variable, h
                status = 0
                if old_routes.get('dest_prefix') == new_routes.get('dest_prefix'):
                    status = 1
                    break
                else:
                    continue
            # If status is still zero at the end of the loop than the route doesnt exist , and we will modify the dictionary
            # to reflect the status
            if status == 0:
                old_routes.update({'status': 'orange'})
                old_routes.update({'time': f'{time.strftime("%H")}:{time.strftime("%M")}:{time.strftime("%S")}'})
                self._flapping_routes['routes'].append(old_routes)


    def _store_routes(self, rib_name, address_family, route):
        """Get all the details for the rin entry"""

        route_details = {}
        route_details['name'] = rib_name
        route_details['address_family'] = address_family

        if isinstance(route, str):
            pass
        else:
            try:
                route_details['dest_prefix'] = route.get('destination-prefix')
                route_details['route_preference'] = route.get('route-preference')
                route_details['metric'] = route.get('metric')

                if route.get('next-hop').get('outgoing-interface') is None:
                    route_details['outgoing_interface'] = '---'
                else:
                    route_details['outgoing_interface'] = route.get('next-hop').get('outgoing-interface')

                route_details['next_hop'] = route.get('next-hop').get('next-hop-address')

                if str(route.get('active')) == '[None]':
                    route_details['active'] = 'Active Route'
                else:
                    route_details['active'] = 'Inactive'

                if isinstance(route.get('source-protocol'), dict):
                    route_details['source_protocol'] = route.get('source-protocol').get('#text')
                else:
                    route_details['source_protocol'] = route.get('source-protocol')

                # Append value of create key creating a list of dictionaries
                self.routes[address_family].append(route_details)

            except AttributeError:
                pass

    def _routing_protocols(self, protocol, name, type, interfaces):
        """Collect and store configured routing protocols"""

        details = {}
        if isinstance(protocol.get('type'), dict):

            details['protocol'] = protocol.get('type').get('#text', {})
            details['id'] = protocol.get('name', {})
            details['name'] = name
            details['type'] = type

            if isinstance(interfaces.get('interface'), list):
                details['interfaces'] = ', '.join(interfaces.get('interface', 'Not Assigned'))
            else:
                details['interfaces'] = interfaces.get('interface', 'Not Assigned')

        else:
            details['protocol'] = protocol.get('type')
            details['id'] = protocol.get('name', {})
            details['name'] = name
            details['type'] = type

            if isinstance(interfaces.get('interface'), list):
                details['interfaces'] = ', '.join(interfaces.get('interface', 'Not Assigned'))
            else:
                details['interfaces'] = interfaces.get('interface', 'Not Assigned')

        self._protocols.append(details)


"""Helper class that gets and returns data via netmiko"""

import logging
import collections


def send_command(netmiko_session, command):
    response = None

    try:
        netmiko_session.send_command(command_string="terminal length 0")
        command = netmiko_session.send_command(command_string=command)
        response = command.split("\n")
    except OSError as error:
        logging.exception(f"{error}", exc_info=True)
        print(f"\n{error}")

    return response


class NetmikoOperations:

    def __init__(self):

        self.span_table = []
        self.mac_table = []
        self.arp_table = []
        self.vlan_table = []
        self.cdp_neighbors = []
        self._trunks = None

    def reset(self):

        self.span_table = []
        self.mac_table = []
        self.arp_table = []
        self.vlan_table = []
        self.cdp_neighbors = []

    def get_cpu(self, netmiko_session):
        """Gets mac and arp tables. Concatinates into one"""

        tables = collections.defaultdict(list)
        tables_2 = collections.defaultdict(list)
        final_table = collections.defaultdict(list)
        get_cpu = 'show processes cpu history'
        current_time = None

        # Gets and parse mac table response
        cpu_table = send_command(netmiko_session, get_cpu)
        for line in reversed(cpu_table):
            try:
                if not line:
                    continue
                if line.rfind('last 72 hours') != -1:
                    current_time = '72hr'
                if line.rfind('last 60 minutes') != -1:
                    current_time = '60min'
                if line.rfind('last 60 seconds') != -1:
                    current_time = '60sec'

                if line.split()[1][0] == '#' or line.split()[1][0] == '*':
                    percent = {'percent': line.split()[0], 'time': list(line[6:])}
                    tables[current_time].append(percent)

            except IndexError:
                pass

        # 72 hours CPU
        for i in tables['72hr']:
            for index, marker in enumerate(i['time']):
                if marker == '#' or marker == '*':
                    tables_2[index].append(int(i['percent']))

        seven_two_hour_table = {'72hrs': tables_2}
        for k, v in seven_two_hour_table.items():
            for a, b in v.items():
                final_table['72hr'].append({str(a): list(reversed(b))[0]})

        # 60 minutes CPU
        tables_2 = collections.defaultdict(list)
        for i in tables['60min']:
            for index, marker in enumerate(i['time']):
                if marker == '#' or marker == '*':
                    tables_2[index].append(int(i['percent']))

        sixty_min_table = {'60min': tables_2}
        for k, v in sixty_min_table.items():
            for a, b in v.items():
                final_table['60min'].append({str(a): list(reversed(b))[0]})

        # 60 seconds CPU
        tables_2 = collections.defaultdict(list)
        for i in tables['60sec']:
            for index, marker in enumerate(i['time']):
                if marker == '#' or marker == '*':
                    tables_2[index].append(int(i['percent']))

        sixty_sec_table = {'60sec': tables_2}
        for k, v in sixty_sec_table.items():
            for a, b in v.items():
                final_table['60sec'].append({str(a): list(reversed(b))[0]})

        return final_table

    def get_cdp_neighbors(self, netmiko_session):
        """Gets mac and arp tables. Concatinates into one"""

        get_cdp_neigh = 'show cdp neighbors'
        name = None
        local_port = None
        remote_port = None

        # Gets and parse mac table response
        cdp_neighbors = send_command(netmiko_session, get_cdp_neigh)
        for neighbor in cdp_neighbors:
            try:
                if not neighbor:
                    continue
                elif neighbor.split()[0] == "":
                    continue
                elif neighbor.split()[0] == 'Capability':
                    continue
                elif neighbor.split()[0] == 'Device':
                    continue
                if len(neighbor.split()) == 1:
                    name = neighbor.split()[0]
                elif len(neighbor.split()) == 7:
                    remote_port = neighbor.split()[5] + neighbor.split()[6]
                    local_port = neighbor.split()[0] + neighbor.split()[1]
                elif len(neighbor.split()) == 8:
                    remote_port = neighbor.split()[6] + neighbor.split()[7]
                    local_port = neighbor.split()[0] + neighbor.split()[1]
                elif len(neighbor.split()) == 9:
                    remote_port = neighbor.split()[7] + neighbor.split()[8]
                    local_port = neighbor.split()[0] + neighbor.split()[1]

            except IndexError:
                continue

            if remote_port is not None:
                self.cdp_neighbors.append({'name': name, 'local-port': local_port, 'remote-port': remote_port})
                name = None
                local_port = None
                remote_port = None

        return self.cdp_neighbors

    def get_span_root(self, netmiko_session) -> list:
        """Gets mac and arp tables. Concatinates into one"""

        get_macs = 'show spanning-tree root'

        # Gets and parse mac table response
        span_table = send_command(netmiko_session, get_macs)

        for vlan in span_table:
            try:
                if vlan.split()[0].rfind("-") != -1:
                    continue
                elif vlan.split()[0] == 'Vlan':
                    continue
                else:
                    if vlan.split()[0][-2] == "0":

                        if len(vlan.split()) == 8:
                            self.span_table.append(
                                {'vlan': vlan.split()[0][-1:], 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': vlan.split()[7]})
                        elif len(vlan.split()) == 7:
                            self.span_table.append(
                                {'vlan': vlan.split()[0][-1:], 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': "Root Bridge"})
                    else:

                        if len(vlan.split()) == 8:
                            self.span_table.append(
                                {'vlan': vlan.split()[0][-2:], 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': vlan.split()[7]})
                        elif len(vlan.split()) == 7:
                            self.span_table.append(
                                {'vlan': vlan.split()[0][-1:], 'root-prio': vlan.split()[1], 'root-id': vlan.split()[2],
                                 'root-cost': vlan.split()[3], 'root-port': "Root Bridge"})
            except IndexError:
                continue

        return self.span_table

    def get_mac_arp_table(self, netmiko_session) -> list:
        """Gets mac and arp tables. Concatinates into one"""

        get_macs = 'show mac address-table'
        gets_arps = 'show ip arp'

        # Gets and parse mac table response
        mac_table = send_command(netmiko_session, get_macs)
        for mac in mac_table:
            try:
                if mac.split()[0].rfind("-") != -1:
                    continue
                elif mac.split()[0] == 'Vlan':
                    continue
                elif mac.split()[0] == 'All':
                    continue
                elif mac.split()[0] == 'Total':
                    continue
                else:
                    self.mac_table.append({'vlan': mac.split()[0], 'address': mac.split()[1], 'type': mac.split()[2],
                                           'interface': mac.split()[3]})
            except IndexError:
                continue

        # Gets and parse arp table response
        arp_table = send_command(netmiko_session, gets_arps)
        for arp in arp_table:
            try:
                if arp.split()[0] == 'Protocol':
                    continue
                elif arp.split()[0] == 'Total':
                    continue
                else:
                    self.arp_table.append(
                        {'protocol': arp.split()[0], 'ip': arp.split()[1], 'age': arp.split()[2], 'mac': arp.split()[3],
                         'interface': arp.split()[5]})
            except IndexError:
                continue

        # Check to see if mac has an arp entry. If so, add k/v to existing dictionary
        for mac in self.mac_table:
            for entry in self.arp_table:
                if mac.get('address') == entry.get('mac'):
                    mac['ip'] = entry.get('ip')
                    mac['ip_int'] = entry.get('interface')
                    break

        return self.mac_table

    def get_netmiko_vlans(self, netmiko_session) -> list:
        """Using Netmiko, this methis logs onto the device and gets the routing table. It then loops through each prefix
        to find the routes and route types."""

        iter_vlan = "1"
        get_vlans = 'show vlan brief'
        get_vlan_pro = 'show spanning-tree bridge priority'
        vlan_ports = None

        vlans = send_command(netmiko_session, get_vlans)
        get_prio = send_command(netmiko_session, get_vlan_pro)

        # Parse netmiko vlan reponse
        for vlan in vlans:
            if not vlan:
                continue
            if not (enumerate(vlan.split(), 0)):
                continue
            elif vlan.split()[0] == "":
                continue
            elif vlan.split()[0].rfind("VLAN") != -1:
                continue
            elif vlan.split()[0].rfind("-") != -1:
                continue

            if iter_vlan != vlan.split()[0] or iter_vlan == "1":
                if vlan.split()[0].rfind("/") != -1:
                    vlan_ports = ' '.join(vlan.split())
                else:
                    vlan_ports = ' '.join(vlan.split()[3:])

            for prio in get_prio:
                try:
                    if list(enumerate(prio.split(), 0))[0][1][-2:] == list(enumerate(vlan.split(), 0))[0][1]:
                        self.vlan_table.append(
                            {'id': prio.split()[0][-2:], 'prio': prio.split()[1], 'name': vlan.split()[1],
                             'status': vlan.split()[2], 'ports': vlan_ports})
                except IndexError:
                    pass

            iter_vlan = vlan.split()[0]

        return self.vlan_table

    @property
    def trunks(self):
        return self._trunks

    @trunks.setter
    def trunks(self, value):
        self._trunks = value

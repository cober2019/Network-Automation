"""Helper functions that get output via netmiko"""

from netmiko import ConnectHandler, ssh_exception
from paramiko.ssh_exception import PasswordRequiredException
import ipapi 

def send_command(command, username, password, host) -> list:
    """Logs into device and returns a connection object to the caller. """

    response = []
    credentials = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'port': 22,
        "fast_cli": False,
        'session_log': 'my_file.out'}

    try:
        with ConnectHandler(**credentials) as connection:
            response = connection.send_command(command)
    except (ssh_exception.AuthenticationException, EOFError, ssh_exception.NetmikoTimeoutException, PasswordRequiredException):
        pass
    
    return response


def get_hsrp_status(username, password, host) -> list:
    """Gets HSRP operation data"""

    hsrp = []
    hsrp_data = send_command('show standby brief | ex Interface', username, password, host)

    if hsrp_data:
        for interface in hsrp_data.splitlines():
            if len(interface.split()) == 0:
                continue
            else:
                try:
                    hsrp.append({'vlanInt': interface.split()[0], 'group': interface.split()[1], 'priority': interface.split()[2], 'state':  interface.split()[4],
                    'active': interface.split()[5], 'standby': interface.split()[6], 'vip':  interface.split()[7]}) 
                except IndexError:
                    pass

    return hsrp

def get_dmvpn(username, password, host) -> tuple:
    """Gets dmvpn peers, attributes, and statuses"""

    dmvpn_data = []
    nbma_location = []
    dmvpn = send_command('show dmvpn | b Interface', username, password, host)
    
    if dmvpn:
        for line in dmvpn.splitlines():
            data = line.split()
            if data == 0 or '-' in line or '#' in line:
                continue
            elif len(line.split()) == 6:

                try:
                    nbma_location.append(ipapi.location(data[1], key=None))
                except ipapi.exceptions.RateLimited as e:
                    pass

                dmvpn_data.append({'peerNbma': data[1], 'peerTunnel': data[2], 'state': data[3], 'upTime': data[4], 'attrb': data[5]})

    return dmvpn_data, nbma_location


def get_arp(username, password, host):
    """Get ARP table"""

    entries = []
    vrfs = _get_vrfs(username, password, host)
    
    try:
        if vrfs:
            for vrf in vrfs:
                arps_entries = send_command(f'show ip arp vrf {vrf}', username, password, host)
                for i in arps_entries.splitlines():
                    try:
                        if i.split()[0] != 'Protocol':
                            entries.append(
                                {'address': i.split()[1], 'time': i.split()[2], 'vrf': vrf,
                                'hardware': i.split()[3], 'type':'n/a', 'enctype':  i.split()[4], 'mode': 'n/a',
                                'interface': i.split()[5]})
                    except IndexError:
                        pass

        arps_entries = send_command(f'show ip arp', username, password, host)
        for i in arps_entries.splitlines():
            try:
                if i.split()[0] != 'Protocol':
                    entries.append(
                        {'address': i.split()[1], 'time': i.split()[2], 'vrf': 'global',
                        'hardware': i.split()[3], 'type':'n/a', 'enctype':  i.split()[4], 'mode': 'n/a',
                        'interface': i.split()[5]})
            except IndexError:
                pass
    except AttributeError:
        pass

    return entries


def _get_vrfs(username, password, host):
    """Get vrfs"""

    vrfs = []
    get_vrf = send_command('show vrf', username, password, host)

    if get_vrf:
        for line in get_vrf.splitlines():
            try:
                if 'Name'not in line:
                    vrfs.append(line.split()[0])
            except IndexError:
                pass
    return vrfs

def get_mac_table(username, password, host):
        """Gets mac table"""

        mac_data = []
        mac_table = send_command('show mac address-table | ex Vlan|All|Total|%|-', username, password, host)

        if mac_table:
            for mac in mac_table.splitlines():
                try:
                    if mac.split()[0] == '%':
                        break
                    else:
                        mac_data.append({'vlan-id-number': mac.split()[0], 'mac': mac.split()[1], 'mat-addr-type': mac.split()[2],
                                            'port': mac.split()[3]})
                except IndexError:
                    continue
   
        return mac_data

def get_model(username, password, host):
        """Get self.device model"""

        model = None
        serial = None
        uptime = None
        software = None
        get_model = send_command('show inventory', username, password, host)
        show_version = send_command('show version', username, password, host)


        try:

            for i in get_model.splitlines():
                if i.rfind('Chassis') != -1:
                    model = i.split("\"")[3].split()[1][0:3]
                elif i.rfind('NAME') != -1:
                    model = i.split("\"")[1]

                if i.rfind('SN') != -1:
                    serial = i.split('SN: ')[1]
                    break

            for i in show_version.splitlines():
                if i.rfind('Uptime') != -1:
                    uptime = i.split("is")[2]
                    break
                elif i.rfind('RELEASE SOFTWARE') != -1:
                    software = i
        except AttributeError:
            pass

        return model, serial, uptime, software

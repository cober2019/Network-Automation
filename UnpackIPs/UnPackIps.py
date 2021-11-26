"""Helper functions to deal with IP ranges. Also can be used a ping tool with logging"""

import ipaddress
import subprocess as sp
import logging
import time

subnet = None
logging.basicConfig(filename='ping.log', level=logging.INFO)


def _diagnose(ip, status) -> logging:
    """Parse ping results. Print and save to ping.log"""

    for i in status[1].split("\n"):

        try:
            if i.split()[0] == "Reply":
                print(f"{ip} up | Latency: {i.split()[4].split('=')[1]} Time: {time.strftime('%a, %d %b %Y %H:%M:%S +0000')}")
                logging.info(f"\n          {ip} up | Latency: {i.split()[4].split('=')[1]} Time: {time.strftime('%a, %d %b %Y %H:%M:%S +0000')}")
            elif i.split()[0] == "Ping" or "Packets" or "Approximate" or "Minimum":
                pass

            if i.split()[0] == "Request":
                print(
                    f"!!! {ip} Resquest timed out. | Status: Down | Time: {time.strftime('%a, %d %b %Y %H:%M:%S +0000')} !!!")
                logging.info(
                    f"\n          !!! {ip} Resquest timed out. | Status: Down | Time: {time.strftime('%a, %d %b %Y %H:%M:%S +0000')} !!!")
        except IndexError:
            pass


def _is_ip(ip):
    """Check for IP address."""

    valid_ip = False

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print(f"Not a valid IP address {ip}")
        return valid_ip


def _get_subnets(user_input):
    # Remove space to avoind ip address errors
    global subnet

    ips = user_input.replace(" ", "")

    """Private method for getting subnet and fourth octet info."""
    ip_details = []
    for subnet in ips.split('|'):
        if '/' in subnet:
            [ip_details.append({"subnet": str(subnet), "ranges": str(i)}) for i in ipaddress.ip_network(subnet)]
        else:
            octets = subnet.split('.')
            subnet = '.'.join(octets[0:-1])

            try:
                ranges = octets[3]
            except IndexError:
                pass

            if len(octets) != 4:
                ValueError("There was more than 4 octets found: " + ips)
            ip_details.append({"subnet": subnet, "ranges": ranges})

    return ip_details


def _mixrange(short_hand):
    """Working with splitting on on command and dashes."""

    ranges = []
    # Taken from https://stackoverflow.com/a/18759797
    for item in short_hand.split(','):
        if '-' not in item:
            ranges.append(int(item))
        else:
            l, h = map(int, item.split('-'))
            ranges += range(l, h + 1)
    return ranges


def get_ips(user_input: str = None) -> list:
    """Take in the user input and split twice using parsing methods for '|', ', and ','."""

    ip_details = _get_subnets(user_input)
    expanded_ip = []
    check_overlap = {}

    for item in ip_details:
        # Check for CIDR
        if '/' in item['subnet']:
            # exclode .0
            if item['ranges'][-1] != '0':
                expanded_ip.append(item['ranges'])
        else:
            fourth_octets = _mixrange(item['ranges'])
            for fourth_octet in fourth_octets:
                ip = item['subnet'] + '.' + str(fourth_octet)
    
                # Verify if there is an IP address, skip ip is function return False
                valid_ip = _is_ip(ip)
                if valid_ip is False:
                    continue
    
                # Check if this IP converted to an integer has been found already, using the dictionary
                # to determine if this IP was seen already.
                if check_overlap.get(int(ipaddress.IPv4Address(ip))):
                    raise ValueError("Overlapping IP: " + ip)
                check_overlap[int(ipaddress.IPv4Address(ip))] = True
                expanded_ip.append(ip)

    return expanded_ip


def ping(user_input: str = None):
    ips = get_ips(user_input)

    for i in ips:
        ping_ips = sp.getstatusoutput("ping " + i)
        _diagnose(i, ping_ips)
        print("\n")

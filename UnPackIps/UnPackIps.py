"""Helper class to deal with IP ranges."""

import ipaddress


class IpRanges:
    """Class for dealing with human readable ip ranges."""

    def get_ips(self, user_input: str) -> None:
        """Take in the user input and split twice using parsing methods for '|', ', and ','."""
        ip_details = self._get_subnets(user_input)
        expanded_ip = []
        check_overlap = {}
        for item in ip_details:
            fourth_octets = self._mixrange(item['ranges'])
            for fourth_octet in fourth_octets:
                ip = item['subnet'] + '.' + str(fourth_octet)
                # Verify if there is an IP address
                self.is_ip(ip)
                # Check if this IP converted to an integer has been found already, using the dictionary
                # to determine if this IP was seen already.
                if check_overlap.get(int(ipaddress.IPv4Address(ip))):
                    raise ValueError("Overlapping IP: " + ip)
                check_overlap[int(ipaddress.IPv4Address(ip))] = True
                expanded_ip.append(ip)
        return expanded_ip

    def is_ip(self, ip):
        """Check for IP address."""
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError("NOT a valid IP: " + ip)

    def _get_subnets(self, user_input):
        """Private method for getting subnet and fourth octet info."""
        ip_details = []
        for subnet in user_input.split('|'):
            octets = subnet.split('.')
            subnet = '.'.join(octets[0:-1])
            ranges = octets[3]
            if len(octets) != 4:
                ValueError("There was more than 4 octets found: " + user_input)
            ip_details.append({"subnet": subnet, "ranges": ranges})
        return ip_details

    def _mixrange(self, short_hand):
        """Working with splitting on on command and dashes."""
        ranges = []
        # Taken from https://stackoverflow.com/a/18759797
        for item in short_hand.split(','):
            if '-' not in item:
                ranges.append(int(item))
            else:
                l,h = map(int, item.split('-'))
                ranges+= range(l,h+1)
        return ranges

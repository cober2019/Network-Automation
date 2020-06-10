import ipaddress
import re

class IpRanges:

    """This is the intial class which is called from main
    Methods =  _init_, _syntac_check, _check_sub_overlapp, get_ips"""

    def __init__(self):

        """Initialize constructors"""
        ...

        self._parsed_ips = []               # List returned from IpParse class/object
        self._final_list = []               # Final list return the the program caller
        self._subnets = []                  # List used to find duplcates between pipes in string

    def _syntax_check(self, *args):

        """Checks to see if the is an [a-zA-Z] char in the string"""
        ...

        if re.findall(r'[a-zA-Z]', args[0]):
            raise ValueError("Invalid Syntax")
        else:
            pass

    def _check_sub_overlapp(self):

        """Checks for overlapping subnets between the pipe \"|\" 10.1.1 | 10.1.1"""
        ...

        overlap = " & ".join(self._subnets)

        if len(self._subnets) != len(set(self._subnets)) == True:
            raise ValueError("Overlapping Subnets between \"|\" %s" % overlap)
        else:
            pass

    def get_ips(self, *args):

        """Initiates the IpParse class/object for each index between the pipe \"|\"
        This is allows for seperate iteration been IP groups.
        Checks for overlapping subnets, duplicate ips, and writes final list to _final_list"""
        ...

        IpRanges._syntax_check(self, args[0])
        split_string = args[0].split("|")
        index = 0
        for ip_address in split_string:

            split_comma = split_string[index].split(",")
            initiate_class = IpParse(_ip_address=ip_address, _split_string=split_string,_split_comma=split_comma)

            for i in initiate_class._ip_list:
                self._parsed_ips.append(i)

            index = index + 1
            self._subnets.append(initiate_class.strip_last_octet[0])

        self._final_list = list(dict.fromkeys(self._parsed_ips))
        IpRanges._check_sub_overlapp(self)

        return self._final_list

class IpParse:


    """All operation for parsing IP string/User Input
    Methods - _init_, _find_range, _indivisual_ips, _whole_ips, _assemble_ips"""
    ...

    def __init__(self, _ip_address=None,_split_string=None, _split_comma=None):

        """Initiate contructors for class use"""
        ...

        self._ip_address = _ip_address
        self._split_string = _split_string
        self._split_comma = _split_comma
        self._ip_list = []
        self._octet_list = []
        self.strip_last_octet = re.findall(r'^.*?[0-9]\..*?[0-9]\..*?[0-9]\.', self._ip_address)
        self._indivisual_ips()
        self._whole_ips()
        self._assemble_ips()

    def _find_range(self, i):

        """Check for start and end range using regex ex. 10-20, 50-60
            This method is called in the _assemble_ips method. Return for range() interation"""
        ...

        if re.findall(r'(?<=\.)[1-9](?=-)', i):
            begin_range = re.findall(r'(?<=\.)[1-9](?=-)', i)
        if re.findall(r'(?<=\.)[1-9][0-9](?=-)', i):
            begin_range = re.findall(r'(?<=\.)[1-9][0-9](?=-)', i)
        if re.findall(r'(?<=\.)[1-9][0-9][0-9](?=-)', i):
            begin_range = re.findall(r'(?<=\.)[1-9][0-9][0-9](?=-)', i)

        if re.findall(r'^[1-9](?=-)', i):
            begin_range = re.findall(r'^[1-9](?=-)', i)
        if re.findall(r'^[1-9][0-9](?=-)', i):
            begin_range = re.findall(r'^[1-9][0-9](?=-)', i)
        if re.findall(r'^[1-9][0-9][0-9](?=-)', i):
            begin_range = re.findall(r'^[1-9][0-9][0-9](?=-)', i)

        if re.findall(r'(?<=-)[0-9]$', i):
            end_range = re.findall(r'(?<=-)[0-9]$', i)
        if re.findall(r'(?<=-)[0-9][0-9]$', i):
            end_range = re.findall(r'(?<=-)[0-9][0-9]$', i)
        if re.findall(r'(?<=-)[0-9][0-9][0-9]$', i):
            end_range = re.findall(r'(?<=-)[0-9][0-9][0-9]$', i)

        return int(begin_range[0]), (end_range[0])

    def _indivisual_ips(self):

        """Search for indivisual ips. Ex. 1,50,60,100
        Adds to _octet_list and assembled at the bottom of the method"""
        ...

        for i in self._split_comma:
            try:
                if re.findall(r'^[1-9]$', i):
                    octet_1 = re.findall(r'^[1-9]$', i)
                    unpack_ips = [self._octet_list.append(octet) for octet in octet_1]
            except IndexError:
                pass

            try:
                if re.findall(r'^[1-9][0-9]$', i):
                    octet_2 = re.findall(r'^[1-9][0-9]$', i)
                    unpack_ips = [self._octet_list.append(octet) for octet in octet_2]
            except IndexError:
                pass

            try:
                if re.findall(r'^[1-9][0-9][0-9]$', i):
                    octet_3 = re.findall(r'^[1-9][0-9][0-9]$', i)
                    unpack_ips = [self._octet_list.append(octet) for octet in octet_3]
            except IndexError:
                pass

            for ip in self._octet_list:
                try:
                    new_ip = self.strip_last_octet[0] + ip
                    next_address = ipaddress.ip_address(new_ip)
                    self._ip_list.append(str(next_address))
                except (IndexError, ValueError):
                    pass

    def _whole_ips(self):

        """Finds whole IPs with in the list, Checks to see if they are valid addresses, stores to list"""
        ...

        for i in self._split_comma:

            whole_ip_1 = re.findall(r'^.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9](?=-)', i)
            for ip in whole_ip_1:
                try:
                    ipaddress.ip_address(ip)
                except ValueError:
                    pass
                else:
                    ipaddress.ip_address(ip)
                    self._ip_list.append(ip)

            whole_ip_2 = re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\..*[0-9]', i)
            for ip in whole_ip_2:
                try:
                    ipaddress.ip_address(ip)
                except ValueError:
                    pass
                else:
                    ipaddress.ip_address(ip)
                    self._ip_list.append(ip)

    def _assemble_ips(self):

        """ Assembles whole ips with ranges. Ex. 10.1.1.1-10, 192.168.128.50-60
        Checks for valid IPs during iteration. Adds 1 for each IP within the range"""
        ...

        for i in self._split_comma:

            if re.findall(r'^.*[0-9]\..*?[0-9]\..*?[0-9]\..*?[0-9](?=-)', i):

                begin_range = re.findall(r'^.*[0-9]\..*?[0-9]\..*?[0-9]\..*?[0-9](?=-)', i)
                ip_address = begin_range[0]
                self._ip_list.append(begin_range[0])
                ip_range = self._find_range(i)

                for ip in range(int(ip_range[0]), int(ip_range[1])):
                    next_address = ipaddress.ip_address(ip_address) + 1
                    self._ip_list.append(str(next_address))
                    ip_address = next_address

            if re.findall(r'^[1-9]-[1-9]$', i):

                ip_range = self._find_range(i)
                ip_address = self.strip_last_octet[0] + str(ip_range[0])
                self._ip_list.append(ip_address)

                for ip in range(int(ip_range[0]), int(ip_range[1])):
                    next_address = ipaddress.ip_address(ip_address) + 1
                    self._ip_list.append(str(next_address))
                    ip_address = next_address

            if re.findall(r'^[1-9][0-9]-[1-9][0-9]$', i):

                ip_range = self._find_range(i)
                ip_address = self.strip_last_octet[0] + str(ip_range[0])
                self._ip_list.append(ip_address)

                for ip in range(int(ip_range[0]), int(ip_range[1])):
                    next_address = ipaddress.ip_address(ip_address) + 1
                    self._ip_list.append(str(next_address))
                    ip_address = next_address

            if re.findall(r'^[1-9][0-9][0-9]-[1-9][0-9][0-9]$', i):

                ip_range = self._find_range(i)
                ip_address = self.strip_last_octet[0] + str(ip_range[0])
                self._ip_list.append(ip_address)

                for ip in range(int(ip_range[0]), int(ip_range[1])):
                    next_address = ipaddress.ip_address(ip_address) + 1
                    self._ip_list.append(str(next_address))
                    ip_address = next_address


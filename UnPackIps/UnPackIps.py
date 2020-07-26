import ipaddress
import re


class IpRanges:

    """Intial class which is called from main
    Methods =  _init_, syntax_check, check_sub_overlapp, get_ips"""

    def __init__(self):

        """Initialize constructors
        _final_list = final ip list return to use"""

        self._final_list = []

    def get_ips(self, user_input: str) -> None:

        """Take in the user input and split twice using \"|\" and \",\""as seperators. Create object from IpParse
        class to unpack IPs. Use inner funtions to check for overlapping subnets and syntax validation"""

        ip_set = user_input.split("|")
        subnets = []
        parsed_ips = []
        
        def check_subnet_overlapp() -> None:

            """Checks for overlapping subnets between the pipe \"|\" 10.1.1 | 10.1.1"""
            ...

            overlap = " & ".join(subnets)

            if len(subnets) != len(set(subnets)) is True:
                raise ValueError("Overlapping Subnets between \"|\" %s" % overlap)
            else:
                pass

        def syntax_check(subnet_string: str) -> None:

            """Checks to see if the is an [a-zA-Z] char in the string"""
            ...

            if re.findall(r'[a-zA-Z]', subnet_string):
                raise ValueError("Invalid Syntax")
            else:
                pass

        # Check vaild string input using inner function
        syntax_check(user_input)

        index = 0
        for ip_address in ip_set:

            # Find commas in user input to split ip ranges
            subnet_ranges = ip_set[index].split(",")
            Class_IpParse = IpParse(ip_address=ip_address, ip_set=ip_set, subnet_ranges=subnet_ranges)

            # Call the class_ipparse ip_list property and add each assembled ip to the instance attribute
            for i in Class_IpParse.ip_list:
                parsed_ips.append(i)

            index = index + 1
            # Store our subnet id to check for overlapping
            subnets.append(Class_IpParse.network_id[0])

        # Perform housekeeping on our list
        self._final_list = list(dict.fromkeys(parsed_ips))

        # Check for no overlapping subnets once ip set had been assembled
        check_subnet_overlapp()

    @property
    def final_list(self) -> list:
        return self._final_list


def find_range(i: str) -> tuple:

    """Check for start and end range using regex ex. 10-20, 50-60
        This method is called in the _assemble_ips method. Return for range() interation"""
    
    begin_range = None
    end_range = None
    
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


class IpParse:

    """All operation for parsing IP string/User Input
    Methods - _init_, find_range, indivisual_ips, whole_ips, assemble_ips"""

    def __init__(self, ip_address: str = None, ip_set: list = None, subnet_ranges: list = None):

        """Initiate instance attributes"""

        self.ip_address = ip_address
        self.ip_set = ip_set
        self.subnet_ranges = subnet_ranges
        self._ip_list = []
        self.network_id = re.findall(r'^.*?[0-9]\..*?[0-9]\..*?[0-9]\.', self.ip_address)

        # Initialize class methods used to analyze user input
        self.indivisual_ips()
        self.whole_ips()
        self.whole_subnets()
        self.assemble_ips()

    def indivisual_ips(self) -> None:

        """Search for indivisual ips. Ex. 1,50,60,100
        Adds to octet_list and assembled at the bottom of the method"""

        octet_list = []

        for i in self.subnet_ranges:

            if re.findall(r'^[1-9]$', i):
                octet_1 = re.findall(r'^[1-9]$', i)
                [octet_list.append(octet) for octet in octet_1]

            elif re.findall(r'^[1-9][0-9]$', i):
                octet_2 = re.findall(r'^[1-9][0-9]$', i)
                [octet_list.append(octet) for octet in octet_2]

            elif re.findall(r'^[1-9][0-9][0-9]$', i):
                octet_3 = re.findall(r'^[1-9][0-9][0-9]$', i)
                [octet_list.append(octet) for octet in octet_3]

        for ip in octet_list:
            try:
                new_ip = self.network_id[0] + ip
                next_address = ipaddress.ip_address(new_ip)
                self._ip_list.append(str(next_address))
            except (IndexError, ValueError):
                pass

    def whole_subnets(self) -> None:

        """Unpack whole subnets"""
        
        ips = None
        
        for i in self.subnet_ranges:

            try:
                if ipaddress.ip_network(i):
                    ips = list(ipaddress.ip_network(i))
            except ValueError:
                continue

            for _ in ips:
                if re.findall(r'.*[0-9]\..*[0-9]\..*[0-9]\.[0]', str(_)):
                    continue
                else:
                    self._ip_list.append(str(_))

    def whole_ips(self) -> None:

        """Finds whole IPs with in the list, Checks to see if they are valid addresses, stores to list"""

        for i in self.subnet_ranges:

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

    def assemble_ips(self) -> None:

        """ Assembles whole ips with ranges. Ex. 10.1.1.1-10, 192.168.128.50-60. Checks for valid IPs during iteration.
        User inner function to build IPs"""

        def build_ips(address, start_range, end_range):

            for ip in range(start_range, end_range):
                next_address = ipaddress.ip_address(address) + 1
                self._ip_list.append(str(next_address))
                address = next_address

        for i in self.subnet_ranges:

            if re.findall(r'^.*[0-9]\..*?[0-9]\..*?[0-9]\..*?[0-9](?=-)', i):

                begin_range = re.findall(r'^.*[0-9]\..*?[0-9]\..*?[0-9]\..*?[0-9](?=-)', i)
                ip_address = begin_range[0]
                self._ip_list.append(begin_range[0])
                ip_range = find_range(i)
                build_ips(ip_address, int(ip_range[0]), int(ip_range[1]))

            elif re.findall(r'^[1-9]-[1-9]$', i):

                ip_range = find_range(i)
                ip_address = self.network_id[0] + str(ip_range[0])
                self._ip_list.append(ip_address)
                build_ips(ip_address, int(ip_range[0]), int(ip_range[1]))

            elif re.findall(r'^[1-9][0-9]-[1-9][0-9]$', i):

                ip_range = find_range(i)
                ip_address = self.network_id[0] + str(ip_range[0])
                self._ip_list.append(ip_address)
                build_ips(ip_address, int(ip_range[0]), int(ip_range[1]))

            elif re.findall(r'^[1-9][0-9][0-9]-[1-9][0-9][0-9]$', i):

                ip_range = find_range(i)
                ip_address = self.network_id[0] + str(ip_range[0])
                self._ip_list.append(ip_address)
                build_ips(ip_address, int(ip_range[0]), int(ip_range[1]))

    @property
    def ip_list(self) -> list:
        return self._ip_list


try:
    import  ipaddress
except ImportError:
    print("ipaddress not installed")
try:
    import  re
except ImportError:
    print("RE not installed")

ip_list = [ ]
octet_list = [ ]

def ip_ranges():

    # Enter ip ranges and/or seperate IPs followed by commas (last ip doesn't need a comma)
    # If entering individual IP only, end as ex. 192.168.128.15-15,20,30,40. Still using the
    # heiphen, butn no range.

    try:
        try:
            ip_address, ip_range = input("IP address:  ").split("-")
        except ValueError as error:
            pass

        # Append ip_list the intial ip, without ranges or seperate IPs
        addr4 = ipaddress.IPv4Address(ip_address)
        ip_list.append(str(addr4))

        # Strip the IP address of the last octet. Used later

        strip_last_octet = re.findall(r'^.*?[0-9]\..*?[0-9]\..*?[0-9]\.', ip_address)

        # Find the last octet whether its 1/2/3 integers. Store the integer to variable

        if re.search(r'[.]\b[1-9]$', ip_address):
            before = re.search(r'[1-9]$', ip_address)
        elif re.search(r'[.]\b[1-9][0-9]$', ip_address):
            before = re.search(r'[1-9][0-9]$', ip_address)
        elif re.search(r'[.]\b[1-9][1-9][0-9]$', ip_address):
            before = re.search(r'[1-9][1-9][0-9]$', ip_address)

        # Find any integer between two commas whether its 1/2/3 integers.
        # Use list comprehension just in case there is more than one 1/2/3 length intergers
        # Unpack all and store individualy to octet_list. Lines 46-65

        try:
            if re.findall(r'(?<=,)([1-9])(?=,)', ip_range):
                octet_1 = re.findall(r'(?<=,)([1-9])(?=,)', ip_range)
                unpack_ips = [octet_list.append(ip) for ip in octet_1]
        except IndexError:
            pass

        try:
            if re.findall(r'(?<=,)([1-9][0-9])(?=,)', ip_range):
                octet_2 = re.findall(r'(?<=,)([1-9][0-9])(?=,)', ip_range)
                unpack_ips = [octet_list.append(ip) for ip in octet_2]
        except IndexError:
            pass

        try:
            if re.findall(r'(?<=,)([1-9][0-9][0-9])(?=,)', ip_range):
                octet_3 = re.findall(r'(?<=,)([1-9][0-9][0-9])(?=,)', ip_range)
                unpack_ips = [octet_list.append(ip) for ip in octet_3]
        except IndexError:
            pass

        # Find the last ip in user input. Search anything after a comma,  [1-9] at the end of the string
        # This works for 1/2/3 integers. Lines 70-89

        try:
            if re.findall(r'(?<=,)([1-9])$', ip_range):
                octet_1 = re.findall(r'(?=,)([1-9])$', ip_range)
                octet_list.append(octet_1[0])
        except IndexError:
            pass

        try:
            if re.findall(r'(?<=,)([1-9][0-9])$', ip_range):
                octet_2 = re.findall(r'(?<=,)([1-9][0-9])$', ip_range)
                octet_list.append(octet_2[0])
        except IndexError:
            pass

        try:
            if re.findall(r'(?<=,)([1-9][0-9][0-9])$', ip_range):
                octet_3 = re.findall(r'(?<=,)([1-9][0-9][0-9])$', ip_range)
                octet_list.append(octet_3[0])
        except IndexError:
            pass

        # If the range is followed by individual IPs, strip everythin after the comma to the end of the string
        # Replace with nothing.

        if re.findall(r'\b,.*$', ip_range):
            strip = re.findall(r'\b,.*$', ip_range)
            replace = ip_range.replace(strip[0], "")
        else:
            replace = ip_range

        # ranges are create from replace variable and before regex variable(indexed)

        end_range = int(replace)
        start_range = int(before.group(0))

        # If a range was entered, use the start end variables.
        # Add 1 to each ip until the range is exhuasted

        for ip in range(start_range, end_range):
            next_address = ipaddress.ip_address(ip_address) + 1
            ip_list.append(str(next_address))
            ip_address = next_address

        # Using the steip_last_octed created earlier, concatinate the individual IP to the variable
        # variable was ex. 192.168.128. + ip. Append ip_list list

        try:
            for ip in octet_list:
                new_ip = strip_last_octet[0] + ip
                next_address = ipaddress.ip_address(new_ip)
                ip_list.append(str(next_address))
        except IndexError:
            pass

        return ip_list

    except (ipaddress.AddressValueError) as error:
        print(error)
        pass


if __name__ == '__main__':

    ip_ranges()
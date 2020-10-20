UnPackIps
==============
Description
--------------

IpRanges was designed for Network Engineer to quickly unpack IP ranges. The intention is to avoid spreadsheets, and other
methods of IP importing.

Dependency
__________

+ Python3

Usage
--------------
+ A pipe "|" separator is used to separate subnets within the string, and commas and dashes to expand IP addresses.

Example 1: Unpacking IPs

          >>> ips = get_ips(user_input="10.1.1.130, 131, 133| 192.168.1.22-50, 1|8.8.8.8")
          ['10.1.1.130', '10.1.1.131', '10.1.1.133', '192.168.1.22', '192.168.1.23', '192.168.1.24', '192.168.1.25', '192.168.1.26', '192.168.1.27', '192.168.1.28',
          '192.168.1.29', '192.168.1.30', '192.168.1.31', '192.168.1.32', '192.168.1.33', '192.168.1.34', '192.168.1.35', '192.168.1.36', '192.168.1.37'
          , '192.168.1.38', '192.168.1.39', '192.168.1.40', '192.168.1.41', '192.168.1.42', '192.168.1.43', '192.168.1.44', '192.168.1.45', '192.168.1.46', '192.168.1.47',
          '192.168.1.48', '192.168.1.49', '192.168.1.50', '192.168.1.1', '8.8.8.8']



Example 2: Check for Overlap

```
>>> from UnPackIps import IpRanges
>>> class_setup = IpRanges()
>>> class_setup.get_ips(user_input = "10.1.1.20-25,21")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/tmp/Network-Automation/UnPackIps/UnPackIps.py", line 28, in get_ips
    ipaddress.ip_address(ip)
ValueError: Overlapping IP: 10.1.1.21
>>> 
```

Example 3: Invalid IP found

```
>>> from UnPackIps import IpRanges
>>> class_setup = IpRanges()
>>> class_setup.get_ips(user_input = "10.1.1.20,500")
Traceback (most recent call last):
  File "/tmp/Network-Automation/UnPackIps/UnPackIps.py", line 37, in is_ip
    subnet = '.'.join(octets[0:-1])
  File "/usr/local/Cellar/python@3.8/3.8.5/Frameworks/Python.framework/Versions/3.8/lib/python3.8/ipaddress.py", line 53, in ip_address
    raise ValueError('%r does not appear to be an IPv4 or IPv6 address' %
ValueError: '10.1.1.500' does not appear to be an IPv4 or IPv6 address

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/tmp/Network-Automation/UnPackIps/UnPackIps.py", line 26, in get_ips
    """Check for IP address."""
  File "/tmp/Network-Automation/UnPackIps/UnPackIps.py", line 39, in is_ip
    if len(octets) != 4:
ValueError: NOT a valid IP: 10.1.1.500
>>> 
```

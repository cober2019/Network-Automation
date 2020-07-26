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

Example 1: Split functionality

```Python
>>> from UnPackIps import IpRanges
>>> class_setup = IpRanges()
>>> class_setup.get_ips(user_input = "10.1.1.20,25,60-65|192.168.1.1-10")
['10.1.1.20', '10.1.1.25', '10.1.1.60', '10.1.1.61', '10.1.1.62', '10.1.1.63', '10.1.1.64', '10.1.1.65', '192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5', '192.168.1.6', '192.168.1.7', '192.168.1.8', '192.168.1.9', '192.168.1.10']
>>> 
```

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

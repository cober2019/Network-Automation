
**IpRanges**
==============

**Description**
--------------

IpRanges was designed for Network Engineer to quickly unpack IP ranges. The intention is to avoid spreadsheets, and other
methods of IP importing.

**Depedency Modules**
__________

+ ipaddress
+ re

Usage
--------------
+ A pipe "|" seperator is used to seperate subnets within the string.

Example 1::

      >>> string = "10.1.1.1-5,10,15,50-60|192.168.128.1-5,10,15,100-110"
      >>> send_ips = class_setup.get_ips(string)
      >>> print(send_ips)
      ['10.1.1.1', '10.1.1.2', '10.1.1.3', '10.1.1.4', '10.1.1.5', '192.168.128.1', '192.168.128.2', '192.168.128.3', '192.168.128.4', '192.168.128.5', '10.1.1.10', '10.1.1.15', '192.168.128.10', '192.168.128.15', '10.1.1.50', '10.1.1.51', '10.1.1.52', '10.1.1.53', '10.1.1.54', '10.1.1.55', '10.1.1.56', '10.1.1.57', '10.1.1.58', '10.1.1.59', '10.1.1.60', '192.168.128.100', '192.168.128.101', '192.168.128.102', '192.168.128.103', '192.168.128.104', '192.168.128.105', '192.168.128.106', '192.168.128.107', '192.168.128.108', '192.168.128.109', '192.168.128.110']

Example 2:

		  >>> string = "10.1.1.20.25,60-65|192.168.1.100-105,192.168.1.1"
		  >>> call_class = range.IpRanges()
		  >>> send_string = call_class.get_ips(string)
	    >>> print(send_string)
		  ['10.1.1.60', '10.1.1.61', '10.1.1.62', '10.1.1.63', '10.1.1.64', '10.1.1.65', '192.168.1.100', '192.168.1.1', '192.168.1.101', '192.168.1.102', '192.168.1.103', '192.168.1.104', '192.168.1.105']
		  
Example 3:

		  >>> string = "10.1.1.20,10.1.50.1"
		  >>> call_class = range.IpRanges()
		  >>> send_string = call_class.get_ips(string)
		  >>> print(send_string)
		  ['10.1.1.20', '10.1.50.1']

Example 4:

      >>> string = "10.1.1.20,50-60"
      >>> call_class = range.IpRanges()
      >>> send_string = call_class.get_ips(string)
      >>> print(send_string)
      ['10.1.1.20', '10.1.1.50', '10.1.1.51', '10.1.1.52', '10.1.1.53', '10.1.1.54', '10.1.1.55', '10.1.1.56', '10.1.1.57', '10.1.1.58', '10.1.1.59', '10.1.1.60']

Exceptions
____________

As the IPs are being assembled they are validated by the ipaddresses module. These exceptions will be passed and the IP(s) wont be added to the list. 
A ValueError will be thrown if the subnets on both sides of the pipe "|" are the same. The traceback will display the overlapping subnets

Exception 1:

		  >>> string = "10.1.1.1|10.1.1.2"
		  >>> call_class = range.IpRanges()
		  >>> send_string = call_class.get_ips(string)
		  Traceback (most recent call last):
		    File "<pyshell#26>", line 1, in <module>
			  send_string = call_class.get_ips(string)
		    File "C:\Users\JohnDoe\AppData\Local\Programs\Python\Python37-32\lib\site-packages\IpRanges\AddressRange.py", line 62, in get_ips
			  IpRanges._check_sub_overlapp(self)
		    File "C:\Users\JohnDoe\AppData\Local\Programs\Python\Python37-32\lib\site-packages\IpRanges\AddressRange.py", line 36, in _check_sub_overlapp
			  raise ValueError("Overlapping Subnets between \"|\" %s" % overlap)
		  ValueError: Overlapping Subnets between "|" 10.1.1. & 10.1.1.
		  >>> 
		  
Exception 2:

		  >>> string = "10.1.1.20,10.1.5a.1"
		  >>> call_class = range.IpRanges()
		  >>> send_string = call_class.get_ips(string)
		 Traceback (most recent call last):
		    File "<pyshell#35>", line 1, in <module>
			  send_string = call_class.get_ips(string)
		    File "C:\Users\JohnDoe\AppData\Local\Programs\Python\Python37-32\lib\site-packages\IpRanges\AddressRange.py", line 47, in get_ips
			  IpRanges._syntax_check(self, args[0])
		    File "C:\Users\JohnDoe\AppData\Local\Programs\Python\Python37-32\lib\site-packages\IpRanges\AddressRange.py", line 24, in _syntax_check
			  raise ValueError("Invalid Syntax")
		  ValueError: Invalid Syntax
		  >>> 
